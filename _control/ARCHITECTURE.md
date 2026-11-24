# ARCHITECTURE

## Visão geral
Um único projeto na Vercel serve o domínio principal:

```
/                          vitrine (index.html, gerado a partir dos 86 repositórios)
/sobre/<familia>/          página de detalhes de cada projeto (rota da vitrine)
/<repositorio>/            aplicação real
/_runtime/                 executor comum dos apps Python (runner.js, runner.py, app.css)
```

## Tipos de integração
1. **Python no navegador (Pyodide):** o script ORIGINAL do repositório é copiado sem alterações
   para `/<repo>/src/` e executado em WebAssembly na aba do visitante. Sem servidor, sem custo,
   sem envio de dados. Usado em: go-traversal-detector, varredor-vulnerabilidades, scanner-vulnerabilidades.
2. **Proxy para deploy existente:** `vercel.json` reescreve `/<repo>/*` para o deploy próprio do app.
   Usado em: cortador-916 (cortador-916.vercel.app).
3. **Redirect para site em produção:** `/achadinhos` → https://osachadinhosdashopee.com.br.
4. **(próximos) Deploy próprio + proxy:** apps Vite/Next ganham um projeto Vercel cada um, com
   `base: '/<repo>/'` (Vite) ou `basePath: '/<repo>'` (Next), num branch `integracao` do repositório
   original, e uma regra de rewrite aqui. Cada app fica isolado, com suas variáveis de ambiente.

## Segurança
- Nenhum `.git`, `.env` ou credencial é publicado; só os arquivos que o app precisa.
- `_control/` fica fora do deploy (`.vercelignore`).
- Upload limitado a 25 MB; ZIPs extraídos com proteção contra zip slip e zip bomb (`runner.py`).
- Apps com IA só vão ao ar com modo demo e limite de uso: chave de API nunca no front-end.
