import json,os,re,subprocess
R='/home/claude/repos'; D=json.load(open('/home/claude/tools/data.json'))
INTEG={'go-traversal-detector':'/go-traversal-detector/','varredor-vulnerabilidades':'/varredor-vulnerabilidades/','scanner-vulnerabilidades':'/scanner-vulnerabilidades/'}
EXT={'cortador-916':'/cortador-916/ (proxy para cortador-916.vercel.app)','achadinhos-atualizado':'/achadinhos → https://osachadinhosdashopee.com.br'}
def files(d): return subprocess.run(['git','-C',f'{R}/{d}','ls-files'],capture_output=True,text=True).stdout.split()
out=[]
for f in D['fams']:
  for r in f['repos']:
    d=r['repo'];fs=files(d);blob='\n'.join(fs)
    pj=sorted([x for x in fs if x.endswith('package.json') and 'node_modules' not in x],key=len)
    pk=open(f'{R}/{d}/{pj[0]}',errors='ignore').read() if pj else ''
    envf=[x for x in fs if re.search(r'\.env(\.example|\.sample)?$',x)]
    keys=sorted(set(re.findall(r'^([A-Z0-9_]*(?:KEY|TOKEN|SECRET)[A-Z0-9_]*)=',open(f'{R}/{d}/{envf[0]}',errors='ignore').read(),re.M))) if envf else []
    fw='next' if '"next"' in pk else 'vite' if '"vite"' in pk else ('node' if pj else '')
    backend=bool(re.search(r'(^|/)(server\.(ts|js|py)|app\.py|index\.php|backend/)',blob,re.M)) or '"express"' in pk
    py=[x for x in fs if x.endswith('.py')]
    if d in INTEG: st,nxt,rota='integrado','validar no navegador após o deploy',INTEG[d]
    elif d in EXT: st,nxt,rota='integrado-externo','validar proxy/redirect após o deploy',EXT[d]
    elif r['reserved']: st,nxt,rota='sem-codigo','publicar o código no repositório',None
    elif r['upstream']: st,nxt,rota='terceiros','manter como estudo; não publicar como aplicação própria',None
    elif keys: st,nxt,rota='requer-chaves',f'definir modo demo e configurar variáveis na Vercel: {", ".join(keys[:6])}',None
    elif fw in('next','vite') and not backend: st,nxt,rota='requer-build','deploy próprio na Vercel com base path /'+d,None
    elif backend: st,nxt,rota='requer-backend','avaliar funções serverless ou VPS',None
    elif py: st,nxt,rota='cli-python','avaliar execução no navegador (Pyodide) se usar só biblioteca padrão',None
    else: st,nxt,rota='estatico-ou-docs','avaliar publicação estática',None
    out.append(dict(repo=d,familia=f['slug'],categoria=f['cat'],status=st,rota=rota,framework=fw or None,backend=backend,variaveis=keys,proximo_passo=nxt,commit=subprocess.run(['git','-C',f'{R}/{d}','log','-1','--format=%h'],capture_output=True,text=True).stdout.strip()))
json.dump({'atualizado':'2026-11-24','repositorios':out},open('/home/claude/cyberhuntlab-apps/_control/PROJECTS.json','w'),ensure_ascii=False,indent=1)
from collections import Counter;print(Counter(x['status'] for x in out))
