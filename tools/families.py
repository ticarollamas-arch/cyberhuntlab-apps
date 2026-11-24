import json, sys

# categoria -> (rótulo, ícone)
CATS = {
  "seg":   ("Segurança & AppSec", "🛡️"),
  "rev":   ("Engenharia reversa", "🧬"),
  "ia":    ("Plataforma & agentes de IA", "🤖"),
  "car":   ("Carreira & GitHub", "🧭"),
  "vid":   ("Vídeo & áudio", "🎬"),
  "com":   ("E-commerce & afiliados", "🛒"),
  "oss":   ("Estudos de open source", "📚"),
  "res":   ("Reservados", "🗂️"),
}

# slug, cat, título, frase curta, o que demonstra (competências), repos (o 1º é o principal), status opcional
F = [
 ("cwe-cover","seg","CWE-Cover 2.0","Triagem de segurança com mapeamento para a taxonomia MITRE CWE e pacote de relatório.",
  ["Análise estática e taint analysis","Mapeamento OWASP / MITRE CWE","CLI em Python + painel React","Geração de relatórios"],["CWE-Cover-2.0"]),
 ("varredor-vulnerabilidades","seg","Varredor Inteligente de Vulnerabilidades","Rastreia entrada não confiável (req, query, argv) até funções perigosas.",
  ["Source → sink (taint analysis)","Triagem estática multilinguagem","Python CLI","Docker"],["varredor-vulnerabilidades"]),
 ("go-traversal-detector","seg","go-traversal-detector","Encontra path traversal (CWE-22) em código Go por análise estática.",
  ["CWE-22 / path traversal","Análise estática de Go","Python"],["go-traversal-detector"]),
 ("cyber-hunt-scanner","seg","Cyber Hunt Scanner","Analisa APK, ZIP ou pasta de código atrás de segredos hardcoded e padrões inseguros.",
  ["Detecção de segredos (AWS, tokens)","Análise de APK","GitHub Actions"],["scanner-vulnerabilidades"]),
 ("aegis","seg","AEGIS — toolkit DevSecOps","Família de CLIs de auditoria defensiva: web passiva, Google Cloud, APIs e agentes CrewAI.",
  ["Auditoria passiva web (headers, CORS, TLS, cookies)","Google Cloud (GKE / Cloud Run)","Agentes CrewAI + Ollama","Docker / docker-compose","Arquitetura de plugins"],
  ["aegis-scout","aegis-audit","aegis-vrp","aegis-agent","aegis-agent-l","30agents-crewai","netaudit-cli"]),
 ("sentinel","seg","Sentinel","Auditoria externa não invasiva de exposição de arquivos sensíveis e assistente de segurança defensiva.",
  ["Funções serverless (Vercel)","Auditoria externa não invasiva","Gateway seguro para LLM"],
  ["sentinel_auditoria_vercel","sentinel_auditoria_vercel_v2","sentinel_ai_chat_vercel"]),
 ("termux-headers","seg","Auditor HTTP/TLS para Termux","Scanner não invasivo de cabeçalhos de segurança e TLS que roda no Android.",
  ["Cabeçalhos de segurança HTTP","TLS","Python no Android (Termux)"],["cyberhuntlab-2026-termux-pipeline"]),
 ("pesquisa","seg","Pesquisa, writeups e laboratórios","Writeups de bug bounty com divulgação responsável, laboratório de CWE-22 e pipeline DevSecOps de referência.",
  ["Divulgação responsável","Documentação técnica","DevSecOps (CI)"],["security-writeups","lab-path-traversal","pipeline-devsecops"]),

 ("engenheiro-reverso","rev","Engenheiro Reverso","Engenharia reversa clean-room de APK e ZIP com IA, em várias versões (Gemini, Ollama, multi-modelo).",
  ["Engenharia reversa de APK","Full-stack React + Express","Integração com LLMs (Gemini / Ollama)","Roda no Termux"],
  ["Engenheiro-Reverso","carol_reverse_engineering_engine_corrigido","Engenharia-Reversa","projeto_carol-gemini-only","Descontrutor-Reverso","projeto_carol_corrigido","projeto_carol-corrigido-ollama"]),

 ("cyberhuntlab-plataforma","ia","Plataforma CyberHuntLab","Bancada de desenvolvimento com agentes (OpenCode + 9Router) e auditoria estática de ZIP.",
  ["Next.js / TypeScript","Orquestração de agentes de código","Auditoria estática de ZIP","Gateway multi-modelo"],
  ["cyber-hunter-lab-integrated-v2","cyberhuntlab-v1-1-0--1-","cyberhuntlab-v1-1-0--2-","openui-codecode","openui-code-code-cyberhuntlab-atualizado","opencode-chat","opencode-workspace-vercel","cyberhunterlab-correcao-vercel"]),
 ("research-center","ia","CyberHuntLab Research","Central para organizar pesquisa de segurança autorizada: escopo, achados e relatórios.",
  ["Next.js","Fluxo de bug bounty","Gestão de escopo"],["cyberhuntlab-gsoc-research--1-"]),
 ("agente-react","ia","Agente ReAct de pesquisa","Chat com LLMs e agente ReAct para pesquisa de segurança, com back-end FastAPI.",
  ["Agente ReAct","FastAPI","Integração com LLMs"],["Deepseek-cyberhuntlab"]),
 ("blog-prompts","ia","Blog e biblioteca de prompts","Site Next.js com Prisma e PostgreSQL para publicar prompts técnicos com busca.",
  ["Next.js + Prisma","PostgreSQL","CMS próprio"],["cyber-hunt-lab"]),
 ("site-institucional","ia","Site institucional CyberHuntLab","Site e front-end do scanner, com funções serverless no Vercel.",
  ["Vite","Serverless (Vercel)","Front-end responsivo"],["cyberhuntlab_vercel","cyberhuntrlab_vercel_independente"]),
 ("prompts","ia","Engenharia de prompts","Orquestrador de prompts com blindagem de instruções, scaffolder de ferramentas e prompt de análise de scanner.",
  ["Engenharia de prompts","Prompt hardening","React + Gemini"],["prompts-orquestrados","cyber-scaffolder","Prompt.md"]),

 ("forgelab","car","ForgeLab Studio","Portal SaaS que reúne GitHub Intelligence, ZipToGit e HACKMIND, com login, planos e painel.",
  ["Monorepo TypeScript (pnpm)","PostgreSQL / Supabase","Autenticação e planos","Deploy Vercel e Railway"],
  ["forgelab-studio","Gitzip-to-dev","forgelab-cyberhuntlab","Cyberhuntlab-Dev","Ziptodevgit","forgelab-cyberhunt"]),
 ("github-intelligence","car","GitHub Intelligence Career Suite","Usa IA para alinhar currículo e portfólio no GitHub e curar repositórios.",
  ["React + Express","Gemini API","API do GitHub"],["github-intelligence-career-ai","github-intelligence-career-suite-ai","Github-automatic","Cyberhunterlab"]),
 ("ziptogit","car","ZipToGit","Publica o conteúdo de um ZIP direto no GitHub e analisa a arquitetura.",
  ["API do GitHub","Full-stack TypeScript","Análise de arquitetura com IA"],["ziptogithub","Loja-Da-Shopee"]),
 ("funil-ats","car","Funil Currículo ATS → GitHub","Monorepo com otimizador de currículo ATS e o Engenheiro Reverso, publicáveis juntos.",
  ["Monorepo","Docker","Vercel"],["cyberhunterlab-funil-curriculo-github","cyberhunterlab-completo-vercel--1-"]),
 ("ats","car","ATS Currículo","Otimizador web de currículos compatíveis com sistemas ATS.",
  ["Flask","Processamento de texto"],["ats-web","cv-intelligence-ai-zip--1-"]),
 ("hackmind","car","HACKMIND","Gera e planeja ideias de projeto para hackathons.",
  ["React + Express","Planejamento com IA"],["Gerador-Ideias-Hackathons-"]),
 ("geosentinel","car","HACKMIND GeoSentinel","Protótipo do NASA Space Apps: imagens de satélite NASA GIBS e séries temporais ambientais.",
  ["Dados abertos da NASA","Visualização geoespacial","React + Vite"],["hackmind-geosentinel"]),

 ("cortador-916","vid","Cortador 9:16","Transforma vídeos longos em cortes verticais com legenda por IA, no navegador.",
  ["Processamento de vídeo no navegador","Transcrição com Whisper","Site estático (Vercel)"],["cortador-916"]),
 ("audio-tts","vid","Voice Library & suíte de áudio","Biblioteca de vozes TTS, casting com IA e geração de áudio a partir de roteiros.",
  ["Text-to-speech","React + TypeScript","Gemini API"],["Tts-Audio","AI-Voice-Generation-Professional-Text-to-Speech"]),
 ("shorts-achadinhos","vid","Editor de Shorts — Achadinhos","Editor Flask de cortes 9:16 para vídeos de produtos, junto a um gerador de vídeos com IA.",
  ["Flask","MoviePy / FFmpeg","Pipeline de vídeo"],["Shorts-Achadinhos-Shopee","Money-imprime-turbo"]),
 ("minimax","vid","MiniMax-H3 no Termux","Cliente Python sem dependências para gerar vídeo a partir de texto.",
  ["Python puro","Consumo de API","Termux"],["minimax-h3-termux-python"]),
 ("ebook","vid","AI eBook Forge","Gera e-books em HTML/PDF a partir de conteúdo, com IA.",
  ["React + Express","Geração de documentos","Gemini API"],["gerador-ebook-pdf"]),

 ("achadinhos","com","Os Achadinhos da Shopee","Site de ofertas afiliadas: front-end, API PHP/SQL, versão Node + Turso, painel de agentes e template Blogger.",
  ["PHP 8 + MySQL","Node.js + Turso","SEO","Painel com fila de tarefas"],
  ["achadinhos-atualizado","Projeto","loja-da-shopee-deploy","files","agentes-shopee","Blogg-template-achadinhos-da-shopee","diana-shopee"]),
 ("lucrar","com","LUCRAR.PY","Gerenciador de links de afiliado com redirecionamento e estatísticas.",
  ["Flask","Termux e Vercel"],["lucrar_afiliados_termux","lucrar_afiliados_vercel"]),
 ("basecamp","com","Basecamp","Site afiliado de equipamentos de camping.",
  ["HTML/CSS","Conteúdo e SEO"],["arquivo.md"]),

 ("oss","oss","Estudos de projetos open source","Cópias e adaptações de projetos de terceiros, com crédito e licença originais preservados.",
  ["Leitura de bases grandes","Adaptação e deploy","Respeito a licenças (MIT / AGPL)"],
  ["GeradorShorts-Youtube","video","Opusclips-clone","Gerador-Short-Youtube","Gerador-Shorts-Virais","skills-main","Blog-Automatico-Seo"]),

 ("reservados","res","Repositórios reservados","Nomes reservados para projetos futuros e o README do perfil.",
  ["Organização do portfólio"],["ticarollamas-arch","youcinemobile","VideoMoneyTurbo"]),
]

SUMMARY_FIX = {
 "aegis-scout":"Auditoria passiva de segurança web para bug bounty e DevSecOps: cabeçalhos, CORS, cookies, SSL e relatório.",
 "aegis-audit":"CLI modular e containerizada para auditorias não invasivas em Google Cloud (GKE / Cloud Run).",
 "aegis-vrp":"Auditoria de segurança para endpoints web e APIs, com geração de relatório.",
 "aegis-agent":"Plataforma de auditoria de segurança com vários agentes especializados baseados em LLM.",
 "aegis-agent-l":"Versão enxuta: orquestração de auditorias simuladas com CrewAI + Ollama.",
 "30agents-crewai":"Auditoria defensiva web com agentes CrewAI, cada um responsável por um aspecto de hardening.",
 "netaudit-cli":"CLI Python de auditoria defensiva de cabeçalhos HTTP de serviços públicos, com política em JSON e histórico em SQLite.",
 "AI-Voice-Generation-Professional-Text-to-Speech":"Suíte multimídia com Gemini: transforma textos em narração e publica o áudio.",
 "gerador-ebook-pdf":"Transforma conteúdo em e-books HTML/PDF formatados com ajuda da IA.",
 "Cyberhunterlab":"GitHub Project Forge AI: gera estrutura e documentação de projetos para o GitHub com IA.",
 "cyber-scaffolder":"LLM ToolForge: gera scaffolds de ferramentas e código com checagens de segurança desde o início.",
 "prompts-orquestrados":"Orquestrador de prompts com técnicas de blindagem contra injeção de instruções.",
 "arquivo.md":"Site afiliado de equipamentos de camping e conjunto de skills de design.",
 "ticarollamas-arch":"README do perfil do GitHub.",
}

APPS = {
 "go-traversal-detector": ("/go-traversal-detector/", "funcionando"),
 "varredor-vulnerabilidades": ("/varredor-vulnerabilidades/", "funcionando"),
 "cyber-hunt-scanner": ("/scanner-vulnerabilidades/", "funcionando"),
 "cortador-916": ("/cortador-916/", "funcionando"),
 "achadinhos": ("https://osachadinhosdashopee.com.br", "no ar"),
}

def main(src, dst):
    repos = {r["repo"]: r for r in json.load(open(src))}
    used = set(); fams = []
    for slug, cat, title, short, comp, members, *rest in F:
        items = []
        for m in members:
            assert m in repos, m
            assert m not in used, m
            used.add(m); r = dict(repos[m])
            if m in SUMMARY_FIX: r["summary"] = SUMMARY_FIX[m]
            items.append(r)
        langs = {}
        for r in items:
            for k, v in r["langs"].items(): langs[k] = langs.get(k, 0) + v
        stack = []
        for r in items:
            for s in r["stack"]:
                if s not in stack: stack.append(s)
        live = [d for r in items for d in r["demo"]]
        fams.append(dict(slug=slug, cat=cat, title=title, short=short, comp=comp, repos=items,
                         langs=langs, stack=stack, live=live[:1],
                         date=max(r["date"] for r in items), app=APPS.get(slug)))
    missing = set(repos) - used
    assert not missing, missing
    json.dump(dict(cats=CATS, fams=fams), open(dst, "w"), ensure_ascii=False)
    print(len(fams), "famílias,", len(used), "repositórios")

main(sys.argv[1], sys.argv[2])
