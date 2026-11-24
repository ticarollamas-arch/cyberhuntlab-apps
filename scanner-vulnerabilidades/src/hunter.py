#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cyber Hunt Scanner — encontra segredos hardcoded e indícios de CWE
em APK, ZIP ou código-fonte.

Uso:
    python3 hunter.py <alvo> [--format terminal|markdown|json] [--output arquivo]

Exemplos:
    python3 hunter.py app.apk
    python3 hunter.py ./meu-projeto --format markdown --output relatorio.md
    python3 hunter.py codigo.zip --format json --output achados.json
"""

import argparse
import json
import sys
from collections import Counter

from engine import scan

# cores só quando a saída é um terminal de verdade
_TTY = sys.stdout.isatty()
def _c(code): return code if _TTY else ""
RED, YEL, GRN, CYA, DIM, BLD, RST = (
    _c("\033[91m"), _c("\033[93m"), _c("\033[92m"),
    _c("\033[96m"), _c("\033[2m"), _c("\033[1m"), _c("\033[0m"),
)

CONF_COLOR = {"alta": RED, "media": YEL, "revisar": DIM}
DISCLAIMER = (
    "Estes achados indicam EXPOSIÇÃO e PADRÕES DE RISCO por análise estática. "
    "Não constituem prova de exploração — confirme cada caso manualmente antes de reportar."
)


def _banner(res):
    kinds = f"{res.files_scanned} arquivo(s) · entrada: {res.input_kind}"
    print(f"\n{BLD}{CYA}Cyber Hunt Scanner{RST}  {DIM}{kinds}{RST}")
    if res.input_kind == "apk" and not res.apktool_ok:
        print(f"{YEL}aviso: apktool não encontrado — o APK foi lido como ZIP, "
              f"sem classes smali. Instale o apktool para varredura completa.{RST}")
    print()


def render_terminal(res):
    _banner(res)
    if not res.findings:
        print(f"{GRN}Nenhum achado.{RST}\n")
        return
    for f in res.findings:
        col = CONF_COLOR[f.confidence]
        tag = "SEGREDO" if f.kind == "secret" else "PADRÃO"
        print(f"{col}[{tag}] {f.ident}{RST}  {BLD}{f.label}{RST}")
        print(f"  {DIM}confiança:{RST} {col}{f.confidence}{RST}   "
              f"{DIM}local:{RST} {f.file}:{f.line}")
        print(f"  {DIM}evidência:{RST} {f.evidence}")
        print(f"  {DIM}correção:{RST} {f.fix}\n")

    counts = Counter(f.ident for f in res.findings)
    print(f"{CYA}{'─'*46}{RST}")
    print(f"{BLD}Resumo{RST}")
    for ident, n in counts.most_common():
        print(f"  {ident} → {n}")
    high = sum(1 for f in res.findings if f.confidence == "alta")
    print(f"\n  total: {len(res.findings)}   alta confiança: {high}")
    print(f"{DIM}\n{DISCLAIMER}{RST}\n")


def render_markdown(res):
    out = ["# Relatório — Cyber Hunt Scanner", ""]
    out.append(f"- Arquivos analisados: **{res.files_scanned}**")
    out.append(f"- Tipo de entrada: **{res.input_kind}**")
    out.append(f"- Total de achados: **{len(res.findings)}**")
    out.append("")
    out.append(f"> {DISCLAIMER}")
    out.append("")
    if not res.findings:
        out.append("Nenhum achado.")
        return "\n".join(out)

    out.append("| Tipo | ID | Achado | Confiança | Local | Evidência |")
    out.append("|---|---|---|---|---|---|")
    for f in res.findings:
        tipo = "Segredo" if f.kind == "secret" else "Padrão"
        ev = f.evidence.replace("|", "\\|")
        out.append(f"| {tipo} | {f.ident} | {f.label} | {f.confidence} | "
                   f"`{f.file}:{f.line}` | `{ev}` |")

    out.append("\n## Correções sugeridas\n")
    seen = {}
    for f in res.findings:
        seen.setdefault(f.ident, (f.label, f.fix))
    for ident, (label, fix) in seen.items():
        out.append(f"- **{ident} — {label}:** {fix}")
    out.append("")
    return "\n".join(out)


def render_json(res):
    return json.dumps({
        "files_scanned": res.files_scanned,
        "input_kind": res.input_kind,
        "apktool_ok": res.apktool_ok,
        "disclaimer": DISCLAIMER,
        "findings": [vars(f) for f in res.findings],
    }, ensure_ascii=False, indent=2)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Scanner de segredos e CWEs (APK/ZIP/código).")
    ap.add_argument("alvo", help="caminho do APK, ZIP ou pasta de código")
    ap.add_argument("--format", choices=["terminal", "markdown", "json"], default="terminal")
    ap.add_argument("--output", help="salva o relatório num arquivo em vez do terminal")
    args = ap.parse_args(argv)

    try:
        res = scan(args.alvo)
    except FileNotFoundError:
        print(f"erro: alvo não encontrado: {args.alvo}", file=sys.stderr)
        return 2

    if args.format == "terminal" and not args.output:
        render_terminal(res)
        return 1 if any(f.confidence == "alta" for f in res.findings) else 0

    text = render_markdown(res) if args.format == "markdown" else render_json(res)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"relatório salvo em {args.output} ({len(res.findings)} achados)")
    else:
        print(text)
    return 1 if any(f.confidence == "alta" for f in res.findings) else 0


if __name__ == "__main__":
    sys.exit(main())
