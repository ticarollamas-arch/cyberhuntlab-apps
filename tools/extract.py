import os,re,json,subprocess,sys
R=sys.argv[1]
EXT={'py':'Python','ts':'TypeScript','tsx':'TypeScript','js':'JavaScript','jsx':'JavaScript','cjs':'JavaScript','mjs':'JavaScript','go':'Go','rs':'Rust','php':'PHP','sh':'Shell','html':'HTML','css':'CSS','sql':'SQL','java':'Java','kt':'Kotlin','yml':'YAML','yaml':'YAML'}
def md2txt(s):
    s=re.sub(r'!\[[^\]]*\]\([^)]*\)','',s); s=re.sub(r'\[([^\]]*)\]\([^)]*\)',r'\1',s)
    s=re.sub(r'<[^>]+>','',s); s=re.sub(r'[*_`]','',s); return re.sub(r'\s+',' ',s).strip()
out=[]
for d in sorted(os.listdir(R)):
    p=os.path.join(R,d)
    if not os.path.isdir(p): continue
    files=subprocess.run(['git','-C',p,'ls-files'],capture_output=True,text=True).stdout.split()
    date=subprocess.run(['git','-C',p,'log','-1','--format=%cs'],capture_output=True,text=True).stdout.strip()
    langs={}
    for f in files:
        e=f.rsplit('.',1)[-1].lower() if '.' in f else ''
        if e in EXT and 'node_modules' not in f: langs[EXT[e]]=langs.get(EXT[e],0)+1
    rd=next((f for f in os.listdir(p) if f.lower()=='readme.md'),None)
    txt=open(os.path.join(p,rd),encoding='utf-8',errors='ignore').read() if rd else ''
    m=re.search(r'^#\s+(.+)$',txt,re.M); title=md2txt(m.group(1)) if m else d
    title=re.sub(r'^[^\wÀ-ú]+','',title).strip()
    summ=''
    if m:
        rest=txt[m.end():]
        for para in re.split(r'\n\s*\n',rest):
            t=para.strip()
            if not t or t.startswith(('#','<','!','|','```','---','╔','║','╚')): 
                if t.startswith('#') and summ: break
                continue
            if t.startswith('>'): t=t.lstrip('> ')
            if t.startswith('- ') or t.startswith('1.'): 
                if summ: break
                continue
            summ=md2txt(t); break
    up=re.search(r'(?:Cópia|Versão adaptada|cópia)[^\n]*?\[([^\]]+)\]\((https://github\.com/[^)]+)\)',txt)
    links=sorted(set(re.findall(r'https://[a-z0-9.-]+\.(?:vercel\.app|railway\.app|netlify\.app|up\.railway\.app|onrender\.com)[^\s)"\'>]*',txt)))
    blob=' '.join(files).lower()
    pk=''
    for f in files:
        if f.endswith('package.json') and 'node_modules' not in f:
            try: pk+=open(os.path.join(p,f),errors='ignore').read().lower()
            except: pass
    pyreq=''
    for f in files:
        if f.endswith(('requirements.txt','pyproject.toml')):
            try: pyreq+=open(os.path.join(p,f),errors='ignore').read().lower()
            except: pass
    stack=[]
    def has(k,src): return k in src
    for k,n in [('"next"','Next.js'),('"react"','React'),('"vite"','Vite'),('"express"','Express'),('supabase','Supabase'),('@google/genai','Gemini API'),('@google/generative-ai','Gemini API'),('tailwind','Tailwind'),('prisma','Prisma'),('"pg"','PostgreSQL'),('@libsql','Turso'),('openai','OpenAI API'),('anthropic','Claude API')]:
        if has(k,pk) and n not in stack: stack.append(n)
    for k,n in [('fastapi','FastAPI'),('flask','Flask'),('crewai','CrewAI'),('streamlit','Streamlit'),('moviepy','MoviePy'),('whisper','Whisper'),('requests','requests'),('google-generativeai','Gemini API'),('openai','OpenAI API'),('ollama','Ollama')]:
        if has(k,pyreq) and n not in stack: stack.append(n)
    if 'dockerfile' in blob: stack.append('Docker')
    if '.github/workflows' in blob: stack.append('GitHub Actions')
    if 'vercel.json' in blob: stack.append('Vercel')
    if 'termux' in (txt.lower()+d.lower()): stack.append('Termux')
    reserved=('reservado' in txt[:1500].lower() and 'não contém código' in txt[:1500].lower()) or len(files)<=3
    out.append(dict(repo=d,title=title,summary=summ[:420],langs=langs,files=len(files),date=date,upstream=(up.group(1),up.group(2)) if up else None,demo=links[:3],stack=stack,reserved=reserved))
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
print(len(out))
