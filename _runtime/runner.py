# Executor genérico dos apps da bancada CyberHuntLab.
# Roda o script ORIGINAL do repositório, sem alterações, dentro do Pyodide
# (Python compilado para WebAssembly, no navegador do visitante).
# Nada é enviado para servidor: os arquivos analisados ficam na memória da aba.
import os
import runpy
import shutil
import sys
import zipfile

MAX_ARQUIVOS_ZIP = 5000
MAX_BYTES_ZIP = 200 * 1024 * 1024


def preparar(work):
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(os.path.join(work, "alvo"))
    return os.path.join(work, "alvo")


def extrair_zips(alvo):
    """Extrai ZIPs enviados, com proteção contra zip slip e zip bomb."""
    avisos = []
    for raiz, _, nomes in os.walk(alvo):
        for nome in nomes:
            if not nome.lower().endswith(".zip"):
                continue
            caminho = os.path.join(raiz, nome)
            destino = os.path.realpath(caminho[:-4])
            try:
                with zipfile.ZipFile(caminho) as z:
                    membros = z.infolist()
                    if len(membros) > MAX_ARQUIVOS_ZIP or sum(m.file_size for m in membros) > MAX_BYTES_ZIP:
                        avisos.append(f"{nome}: grande demais para analisar no navegador, ignorado")
                        continue
                    for m in membros:
                        alvo_m = os.path.realpath(os.path.join(destino, m.filename))
                        if not alvo_m.startswith(destino + os.sep):
                            avisos.append(f"{nome}: entrada fora da pasta ignorada ({m.filename})")
                            continue
                        if m.is_dir():
                            os.makedirs(alvo_m, exist_ok=True)
                            continue
                        os.makedirs(os.path.dirname(alvo_m), exist_ok=True)
                        with z.open(m) as src, open(alvo_m, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                os.remove(caminho)
            except zipfile.BadZipFile:
                avisos.append(f"{nome}: ZIP inválido")
    return avisos


def executar(src_dir, script, argv):
    """Executa src_dir/script como se fosse `python3 script argv...`."""
    src_dir = os.path.realpath(src_dir)
    for nome, mod in list(sys.modules.items()):
        arq = getattr(mod, "__file__", None) or ""
        if arq and os.path.realpath(arq).startswith(src_dir + os.sep):
            del sys.modules[nome]
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    antigo = sys.argv
    sys.argv = [script] + list(argv)
    codigo = 0
    try:
        runpy.run_path(os.path.join(src_dir, script), run_name="__main__")
    except SystemExit as e:
        codigo = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    finally:
        sys.argv = antigo
    return codigo
