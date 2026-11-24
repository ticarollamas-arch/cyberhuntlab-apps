# ERRORS / BLOQUEIOS

| Data | Repositório | Problema | Causa | Ação |
|---|---|---|---|---|
| 24/11 | go-traversal-detector | Exemplo seguro com variável `raiz` era marcado "revisar" | A regex GUARDS só reconhece `HasPrefix` com variáveis chamadas base/root/realBase/realRoot/dir | Exemplo ajustado para `base`. Melhoria proposta: aceitar qualquer variável após `filepath.Clean`/`Abs` (fazer em branch `integracao`, com teste) |
| 24/11 | (todos) | Não foi possível compilar apps Vite/Next neste ambiente | Ambiente de trabalho sem acesso ao registro npm | Build fica a cargo da Vercel no deploy de cada app |
| 24/11 | 40 repositórios | Dependem de chaves (Gemini, OpenAI, Groq, NVIDIA, GitHub) | Uso público queimaria a cota/custo da dona | Bloqueados até definir modo demo + limite por visitante |
| 24/11 | (infra) | Sem permissão para criar repositório novo no GitHub | Sessão só envia para repositórios existentes | A dona cria o repositório vazio; depois o envio é automático |
| 24/11 | CLIs com rede (aegis-scout, termux-pipeline…) | Navegador bloqueia requisições a outros domínios (CORS) | Scanners de cabeçalhos precisam falar com o alvo | Opção: função serverless com lista de alvos permitidos e rate limit |
