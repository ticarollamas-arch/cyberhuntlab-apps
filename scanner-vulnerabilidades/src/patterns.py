#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Padrões de detecção: segredos hardcoded e indícios de CWE em código-fonte."""

import re

# ----------------------------------------------------------------------
# SEGREDOS — funcionam sobre qualquer texto (código, smali, config).
# Cada entrada: (id, rótulo, regex compilada, dica de correção)
# ----------------------------------------------------------------------
SECRET_PATTERNS = [
    (
        "AWS-ARN",
        "AWS IAM Role/Resource ARN",
        re.compile(r"arn:aws:[a-z0-9\-]+:[a-z0-9\-]*:\d{12}:[^\s\"']+"),
        "ARNs de produção não devem existir no cliente. Emita credenciais temporárias por um backend.",
    ),
    (
        "AWS-AKID",
        "AWS Access Key ID",
        re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
        "Revogue a chave imediatamente e use IAM Roles ou Secrets Manager.",
    ),
    (
        "GOOGLE-API",
        "Google API Key",
        re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"),
        "Restrinja a chave por aplicativo/API no console e não a versione.",
    ),
    (
        "GITHUB-PAT",
        "GitHub Token",
        re.compile(r"\bgh[pousr]_[0-9A-Za-z]{36,}\b"),
        "Revogue em github.com/settings/tokens e rotacione.",
    ),
    (
        "SLACK-TOKEN",
        "Slack Token",
        re.compile(r"\bxox[baprs]-[0-9A-Za-z\-]{10,}\b"),
        "Revogue o token no painel do Slack.",
    ),
    (
        "PRIVATE-KEY",
        "Chave privada (PEM)",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"),
        "Chave privada nunca deve ser distribuída. Rotacione o par de chaves.",
    ),
    (
        "JWT",
        "JSON Web Token",
        re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b"),
        "Tokens JWT embutidos costumam ser credenciais de longa duração. Verifique.",
    ),
    (
        "GENERIC-SECRET",
        "Segredo genérico atribuído no código",
        re.compile(
            r"""(?ix)\b(?:api[_-]?key|secret|password|passwd|token|auth)\b\s*[:=]\s*["']([^"'\s]{8,})["']"""
        ),
        "Mova o valor para variável de ambiente ou cofre de segredos.",
    ),
]

# Termos que indicam exemplo/placeholder — reduzem a confiança do achado.
_PLACEHOLDER = re.compile(
    r"(?i)(example|sample|dummy|test|placeholder|your[_-]?key|xxxx|changeme|<[^>]+>)"
)


# ----------------------------------------------------------------------
# CWEs — sink (função perigosa) casado com fonte (entrada não confiável).
# Aplicam-se a código-fonte, não a smali.
# ----------------------------------------------------------------------
_SOURCES = r"(req|request|params|query|body|input|args|argv|filename|user|data|getenv|os\.environ)"

CWE_PATTERNS = [
    (
        "CWE-22",
        "Path Traversal",
        re.compile(
            r"(?ix)\b(fs\.readfile(?:sync)?|res\.sendfile|open|path\.join|sendfile)\s*\([^)]*\b"
            + _SOURCES + r"\b"
        ),
        "Normalize com realpath e verifique se o caminho continua dentro da raiz permitida.",
    ),
    (
        "CWE-78",
        "OS Command Injection",
        re.compile(
            r"(?ix)\b(exec|execsync|spawn|popen|system|child_process|subprocess\.(?:run|call|popen))\s*\([^)]*\b"
            + _SOURCES + r"\b"
        ),
        "Nunca passe entrada do usuário ao shell. Use argumentos parametrizados sem shell=True.",
    ),
    (
        "CWE-89",
        "SQL Injection",
        re.compile(
            r"""(?ix)\b(query|execute|db\.raw|cursor\.execute)\s*\(\s*(?:f["']|["'][^"']*["']\s*[\+%]|["'][^"']*\{)"""
        ),
        "Use consultas parametrizadas (placeholders), nunca concatenação de string.",
    ),
    (
        "CWE-94",
        "Code Injection / RCE",
        re.compile(
            r"(?ix)\b(eval|exec|new\s+function|settimeout|setinterval)\s*\([^)]*\b"
            + _SOURCES + r"\b"
        ),
        "Não avalie entrada dinâmica. Refatore para uma lógica sem eval/exec.",
    ),
    (
        "CWE-79",
        "Cross-Site Scripting",
        re.compile(
            r"(?ix)\b(innerhtml|document\.write|dangerouslysetinnerhtml|res\.send|res\.render)\b[^;\n]*\b"
            + _SOURCES + r"\b"
        ),
        "Escape a saída ou use APIs seguras (textContent) e um template com auto-escaping.",
    ),
    (
        "CWE-502",
        "Desserialização insegura",
        re.compile(r"(?ix)\b(pickle\.loads|yaml\.load|marshal\.loads)\s*\("),
        "Use yaml.safe_load e evite desserializar dados não confiáveis.",
    ),
    (
        "CWE-327",
        "Criptografia fraca",
        re.compile(r"(?ix)\b(md5|sha1|des|rc4)\b\s*\("),
        "Troque por SHA-256+ para hash e AES-GCM para cifragem.",
    ),
]

# Indícios de sanitização perto do achado de CWE — rebaixam para "revisar".
DEFENSES = re.compile(
    r"(?i)(basename|realpath|sanitize|escape|shlex\.quote|parameteriz|safe_load|"
    r"normalize|allowlist|whitelist|validate|\.\.'|indexof\('\.\.'\)|includes\('\.\.'\))"
)


def looks_like_placeholder(text: str) -> bool:
    return bool(_PLACEHOLDER.search(text))
