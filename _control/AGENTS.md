# AGENTS — como continuar este trabalho

Loop por repositório: DESCOBRIR → ANALISAR → PLANEJAR → CLONAR → CORRIGIR → INTEGRAR → TESTAR → PUBLICAR → VALIDAR.

Regras:
1. Leia `PROJECTS.json` e `PROGRESS.md` antes de começar; não refaça o que está "integrado".
2. Nunca apague repositórios nem código; mudanças nos originais só em branch `integracao`.
3. Não invente funcionalidade: se o app não funciona, a vitrine diz o estado real.
4. Projetos de terceiros ficam como estudo, com crédito e licença originais.
5. Máximo de 3 tentativas por erro; depois registre em `ERRORS.md` e siga para o próximo.
6. Atualize `PROJECTS.json`, `PROGRESS.md` e `ERRORS.md` ao fim de cada repositório.
7. Regenerar a vitrine: `python3 tools/families.py repos.json data.json && python3 tools/build.py`.
