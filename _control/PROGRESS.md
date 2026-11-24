# PROGRESS

Última atualização: 24/11/2026 · ciclo 1

## Integrados e funcionando no domínio (3)
- varredor-vulnerabilidades
- go-traversal-detector
- scanner-vulnerabilidades

## Integrados via proxy/redirect (site já no ar) (2)
- cortador-916
- achadinhos-atualizado

## Próximo lote: CLIs Python (candidatos a rodar no navegador) (13)
- aegis-scout
- aegis-audit
- aegis-vrp
- aegis-agent
- aegis-agent-l
- 30agents-crewai
- netaudit-cli
- cyberhuntlab-2026-termux-pipeline
- cyberhunterlab-correcao-vercel
- minimax-h3-termux-python
- lucrar_afiliados_termux
- lucrar_afiliados_vercel
- arquivo.md

## Precisam de deploy próprio (build na Vercel) (4)
- cyber-hunt-lab
- cyberhuntlab_vercel
- Loja-Da-Shopee
- hackmind-geosentinel

## Precisam de servidor/backend (4)
- CWE-Cover-2.0
- Ziptodevgit
- ats-web
- agentes-shopee

## Precisam de chaves de API (bloqueados até haver modo demo) (40)
- sentinel_auditoria_vercel
- sentinel_auditoria_vercel_v2
- sentinel_ai_chat_vercel
- Engenheiro-Reverso
- carol_reverse_engineering_engine_corrigido
- Engenharia-Reversa
- projeto_carol-gemini-only
- Descontrutor-Reverso
- projeto_carol_corrigido
- projeto_carol-corrigido-ollama
- cyber-hunter-lab-integrated-v2
- cyberhuntlab-v1-1-0--1-
- cyberhuntlab-v1-1-0--2-
- openui-codecode
- openui-code-code-cyberhuntlab-atualizado
- opencode-chat
- opencode-workspace-vercel
- cyberhuntlab-gsoc-research--1-
- Deepseek-cyberhuntlab
- cyberhuntrlab_vercel_independente
- prompts-orquestrados
- cyber-scaffolder
- forgelab-studio
- forgelab-cyberhuntlab
- Cyberhuntlab-Dev
- github-intelligence-career-ai
- github-intelligence-career-suite-ai
- Github-automatic
- Cyberhunterlab
- ziptogithub
- cyberhunterlab-funil-curriculo-github
- cyberhunterlab-completo-vercel--1-
- Gerador-Ideias-Hackathons-
- Tts-Audio
- AI-Voice-Generation-Professional-Text-to-Speech
- Shorts-Achadinhos-Shopee
- Money-imprime-turbo
- gerador-ebook-pdf
- loja-da-shopee-deploy
- Blogg-template-achadinhos-da-shopee

## Estáticos ou só documentação (5)
- security-writeups
- Prompt.md
- cv-intelligence-ai-zip--1-
- Projeto
- files

## Open source de terceiros (não publicar como app próprio) (8)
- Gitzip-to-dev
- GeradorShorts-Youtube
- video
- Opusclips-clone
- Gerador-Short-Youtube
- Gerador-Shorts-Virais
- skills-main
- Blog-Automatico-Seo

## Sem código publicado (7)
- lab-path-traversal
- pipeline-devsecops
- forgelab-cyberhunt
- diana-shopee
- ticarollamas-arch
- youcinemobile
- VideoMoneyTurbo

## Ponto de retomada
Ciclo 2 começa pelo lote `cli-python`: verificar se cada script usa só a biblioteca padrão
(aegis-scout, netaudit-cli, cyberhuntlab-2026-termux-pipeline…). Os que fazem requisições de rede
reais não rodam no navegador por CORS e precisam de outra estratégia (ver ERRORS.md).
