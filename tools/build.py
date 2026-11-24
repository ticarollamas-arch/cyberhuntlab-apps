import json,datetime
d=json.load(open('data.json'));d['generated']=datetime.date.today().strftime('%d/%m/%Y')
s=json.dumps(d,ensure_ascii=False).replace('</','<\\/')
t=open('template.html').read().replace('__DATA__',s)
import os;os.makedirs('/home/claude/cyberhuntlab-apps',exist_ok=True)
open('/home/claude/cyberhuntlab-apps/index.html','w').write(t)
vj={
 "trailingSlash": True,
 "redirects":[
  {"source":"/achadinhos","destination":"https://osachadinhosdashopee.com.br","permanent":False}
 ],
 "rewrites":[
  {"source":"/cortador-916/:path*","destination":"https://cortador-916.vercel.app/:path*"},
  {"source":"/api/transcrever","destination":"https://cortador-916.vercel.app/api/transcrever"},
  {"source":"/sobre/:slug*","destination":"/index.html"}
 ],
 "headers":[
  {"source":"/(.*)","headers":[
   {"key":"X-Content-Type-Options","value":"nosniff"},
   {"key":"Referrer-Policy","value":"strict-origin-when-cross-origin"},
   {"key":"Permissions-Policy","value":"camera=(), microphone=(), geolocation=()"}]},
  {"source":"/((?!cortador-916).*)","headers":[{"key":"X-Frame-Options","value":"DENY"}]}
 ]
}
open('/home/claude/cyberhuntlab-apps/vercel.json','w').write(json.dumps(vj,indent=2,ensure_ascii=False))
