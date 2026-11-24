#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Motor do scanner: prepara a entrada e varre por segredos e CWEs."""

import os
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from patterns import (
    SECRET_PATTERNS,
    CWE_PATTERNS,
    DEFENSES,
    looks_like_placeholder,
)

CODE_EXT = {".js", ".ts", ".jsx", ".tsx", ".py", ".java", ".rb", ".php", ".go"}
TEXT_EXT = CODE_EXT | {".smali", ".xml", ".json", ".yml", ".yaml", ".env", ".properties", ".txt", ".gradle"}
SKIP_DIRS = {"node_modules", ".git", ".github", "dist", "build", "vendor", "__pycache__", "test", "tests", "example", "examples", "fixtures"}
MAX_BYTES = 3_000_000  # ignora arquivos gigantes (binários, mapas)


@dataclass
class Finding:
    kind: str          # "secret" ou "cwe"
    ident: str         # ex. "AWS-ARN" ou "CWE-22"
    label: str
    file: str
    line: int
    evidence: str
    confidence: str    # "alta" | "media" | "revisar"
    fix: str


@dataclass
class ScanResult:
    findings: list = field(default_factory=list)
    files_scanned: int = 0
    input_kind: str = ""
    apktool_ok: bool = True


def _redact(secret: str) -> str:
    s = secret.strip()
    if len(s) <= 12:
        return s[:4] + "…"
    return s[:8] + "…" + s[-4:]


def _decompile_apk(apk: Path, workdir: Path) -> tuple[Path, bool]:
    """Tenta descompilar com apktool. Se não houver apktool, cai para unzip cru."""
    out = workdir / "apk_src"
    if shutil.which("apktool"):
        try:
            subprocess.run(
                ["apktool", "d", "-f", "-o", str(out), str(apk)],
                check=True, capture_output=True, timeout=300,
            )
            return out, True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
    # fallback: descompacta o APK como ZIP (não há smali, mas pega strings/assets)
    out.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(apk) as z:
            z.extractall(out)
    except zipfile.BadZipFile:
        pass
    return out, False


def prepare_input(target: str, workdir: Path) -> tuple[Path, str, bool]:
    """Devolve (pasta_para_varrer, tipo_da_entrada, apktool_ok)."""
    p = Path(target)
    if p.is_dir():
        return p, "pasta", True
    if p.suffix.lower() == ".apk":
        src, ok = _decompile_apk(p, workdir)
        return src, "apk", ok
    if p.suffix.lower() in {".zip", ".jar", ".ipa"}:
        out = workdir / "zip_src"
        out.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(p) as z:
            z.extractall(out)
        return out, "zip", True
    # arquivo único
    return p.parent, "arquivo", True


def _iter_files(root: Path):
    if root.is_file():
        yield root
        return
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            fp = Path(base) / name
            if fp.suffix.lower() not in TEXT_EXT:
                continue
            try:
                if fp.stat().st_size > MAX_BYTES:
                    continue
            except OSError:
                continue
            yield fp


def _scan_secrets(rel: str, lines: list[str], out: list):
    for i, line in enumerate(lines, 1):
        if len(line) > 800:  # linha minificada gigante: pula
            continue
        for ident, label, rx, fix in SECRET_PATTERNS:
            m = rx.search(line)
            if not m:
                continue
            hit = m.group(1) if (m.groups() and m.group(1)) else m.group(0)
            conf = "media" if looks_like_placeholder(line) else "alta"
            out.append(Finding(
                kind="secret", ident=ident, label=label, file=rel, line=i,
                evidence=_redact(hit), confidence=conf, fix=fix,
            ))


# fonte de entrada não confiável (usada tanto direto quanto via variável)
import re as _re
_SRC = _re.compile(
    r"(?ix)\b(req|request|params|query|body|input\s*\(|argv|getenv|os\.environ|"
    r"process\.env|\$_GET|\$_POST|\$_REQUEST)\b"
)
# atribuição: <var> = ...fonte...   (JS: const/let/var; Python: nome = )
_ASSIGN = _re.compile(
    r"(?ix)(?:const|let|var\s+)?\s*([a-z_$][\w$]*)\s*=\s*(.+)$"
)
# sinks perigosos com o CWE que representam
_SINKS = [
    ("CWE-22", "Path Traversal",
     _re.compile(r"(?ix)\b(fs\.readfile(?:sync)?|res\.sendfile|sendfile|open|readfile)\s*\("),
     "Normalize com realpath e verifique se o caminho continua dentro da raiz permitida."),
    ("CWE-78", "OS Command Injection",
     _re.compile(r"(?ix)\b(exec|execsync|spawn|popen|os\.system|system|subprocess\.(?:run|call|popen))\s*\("),
     "Nunca passe entrada do usuário ao shell. Use argumentos parametrizados sem shell=True."),
    ("CWE-94", "Code Injection / RCE",
     _re.compile(r"(?ix)\b(eval|exec)\s*\("),
     "Não avalie entrada dinâmica. Refatore para uma lógica sem eval/exec."),
    ("CWE-79", "Cross-Site Scripting",
     _re.compile(r"(?ix)\b(innerhtml|document\.write|dangerouslysetinnerhtml)\b"),
     "Escape a saída ou use APIs seguras (textContent) com auto-escaping."),
]


def _scan_cwe(rel: str, lines: list[str], out: list):
    if Path(rel).suffix.lower() not in CODE_EXT:
        return
    tainted: set[str] = set()   # variáveis que carregam entrada não confiável

    for i, line in enumerate(lines, 1):
        if len(line) > 800:
            continue

        # 1) atualiza o conjunto de variáveis marcadas
        m = _ASSIGN.match(line.strip())
        if m:
            var, rhs = m.group(1), m.group(2)
            if _SRC.search(rhs) or any(t in rhs for t in tainted):
                tainted.add(var)

        # 2) sinks: casa se a fonte está na linha OU uma variável marcada chega ali
        for ident, label, rx, fix in _SINKS:
            if not rx.search(line):
                continue
            direct = bool(_SRC.search(line))
            via_var = any(_re.search(r"\b" + _re.escape(t) + r"\b", line) for t in tainted)
            if not (direct or via_var):
                continue
            lo, hi = max(0, i - 6), min(len(lines), i + 5)
            block = "".join(lines[lo:hi])
            conf = "revisar" if DEFENSES.search(block) else "media"
            out.append(Finding(
                kind="cwe", ident=ident, label=label, file=rel, line=i,
                evidence=line.strip()[:120], confidence=conf, fix=fix,
            ))
            break  # um sink por linha

        # 3) padrões que não dependem de fonte (sql, deser, cripto)
        for ident, label, rx, fix in CWE_PATTERNS:
            if ident not in ("CWE-89", "CWE-502", "CWE-327"):
                continue
            if rx.search(line):
                lo, hi = max(0, i - 6), min(len(lines), i + 5)
                conf = "revisar" if DEFENSES.search("".join(lines[lo:hi])) else "media"
                out.append(Finding(
                    kind="cwe", ident=ident, label=label, file=rel, line=i,
                    evidence=line.strip()[:120], confidence=conf, fix=fix,
                ))


def scan(target: str) -> ScanResult:
    res = ScanResult()
    with tempfile.TemporaryDirectory() as tmp:
        root, kind, apktool_ok = prepare_input(target, Path(tmp))
        res.input_kind, res.apktool_ok = kind, apktool_ok
        base = root if root.is_dir() else root.parent
        for fp in _iter_files(root):
            try:
                lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
            except OSError:
                continue
            try:
                rel = str(fp.relative_to(base))
            except ValueError:
                rel = fp.name
            res.files_scanned += 1
            _scan_secrets(rel, lines, res.findings)
            _scan_cwe(rel, lines, res.findings)
    # ordena: segredos alta primeiro, depois por id
    order = {"alta": 0, "media": 1, "revisar": 2}
    res.findings.sort(key=lambda f: (f.kind != "secret", order[f.confidence], f.ident))
    return res
