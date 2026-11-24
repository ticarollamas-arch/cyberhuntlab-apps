// Interface comum dos apps Python da bancada CyberHuntLab.
// Carrega o Pyodide, copia os arquivos ORIGINAIS do repositório para a memória
// e executa o script como na linha de comando. Tudo acontece no navegador.
(() => {
  const C = window.APP;
  const $ = s => document.querySelector(s);
  const PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
  const MAX_BYTES = 25 * 1024 * 1024;
  let py = null, files = [], mode = 'exemplo';

  // ---------- montagem da página ----------
  document.title = `${C.title} · CyberHuntLab`;
  document.body.innerHTML = `
  <header class="top"><a class="home" href="/"><i></i>cyberhuntlab</a>
    <div class="sp"><a class="btn" href="/sobre/${C.family}">Sobre o projeto</a><a class="btn pri" href="https://github.com/ticarollamas-arch/${C.repo}" target="_blank" rel="noopener">Código ↗</a></div></header>
  <main>
    <div class="head"><span class="pill">● aplicação real · roda no seu navegador</span><h1>${C.title}</h1><p>${C.lead}</p></div>
    <div class="app">
      <section class="pane">
        <div class="tabs" role="tablist">
          <button class="tab on" data-v="exemplo">Código</button>
          <button class="tab" data-v="arquivos">Enviar arquivos / ZIP</button>
          ${C.selftest ? '<button class="tab" data-v="autoteste">Autoteste</button>' : ''}
        </div>
        <div class="view on" id="v-exemplo">
          <div class="fname">arquivo: <select id="sample"></select> <input id="fn" aria-label="nome do arquivo"></div>
          <textarea id="src" spellcheck="false" aria-label="código a analisar"></textarea>
        </div>
        <div class="view" id="v-arquivos">
          <label class="drop" id="drop"><input type="file" id="file" multiple hidden accept="${C.accept}">
            <span><b>Arraste arquivos ou um ZIP aqui</b><br>ou clique para escolher · até 25 MB<br><small>${C.acceptLabel}</small></span></label>
          <div class="flist" id="flist"></div>
        </div>
        ${C.selftest ? `<div class="view" id="v-autoteste"><div class="selftest">Roda o autoteste embutido no próprio script (<code>${C.selftest.join(' ')}</code>), que confere se ele detecta código vulnerável e ignora código seguro.</div></div>` : ''}
        <div class="run"><button class="btn pri" id="go">▶ Analisar</button><small id="hint">Ctrl+Enter também executa</small></div>
      </section>
      <section class="pane out">
        <div class="bar"><span class="led" id="led"></span><span id="st">pronto · o Python (~10 MB) é baixado na primeira análise</span>
          <button class="btn" id="dl" style="margin-left:auto;display:none">⬇ relatório</button></div>
        <pre id="out" aria-live="polite">Escolha um exemplo, cole seu código ou envie arquivos e clique em ▶ Analisar.</pre>
      </section>
    </div>
    <p class="note">${C.note}</p>
    <div class="meta">
      <div><b>Projeto</b>${C.title}</div>
      <div><b>Autoria</b>Ana Caroline Lamas</div>
      <div><b>Tecnologias</b>${C.tech}</div>
      <div><b>Versão</b><span id="ver">—</span></div>
      <div><b>Licença</b><a href="src/LICENSE.txt" target="_blank">${C.license}</a></div>
      <div><b>Repositório</b><a href="https://github.com/ticarollamas-arch/${C.repo}" target="_blank" rel="noopener">${C.repo}</a></div>
      <div><b>Referências</b>${C.refs}</div>
    </div>
  </main>`;

  fetch('src/VERSION.txt').then(r => r.ok ? r.text() : '').then(t => { if (t) $('#ver').textContent = 'commit ' + t.trim(); }).catch(() => {});

  // ---------- exemplos ----------
  const sel = $('#sample'), src = $('#src'), fn = $('#fn');
  C.samples.forEach((s, i) => sel.append(new Option(s.label, i)));
  async function loadSample(i) {
    const s = C.samples[i]; fn.value = s.name;
    src.value = s.code != null ? s.code : await (await fetch(s.url)).text();
  }
  sel.onchange = () => loadSample(sel.value); loadSample(0);
  src.addEventListener('keydown', e => {
    if (e.key === 'Tab') { e.preventDefault(); src.setRangeText('    ', src.selectionStart, src.selectionEnd, 'end'); }
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); analisar(); }
  });

  // ---------- abas ----------
  document.querySelectorAll('.tab').forEach(t => t.onclick = () => {
    mode = t.dataset.v;
    document.querySelectorAll('.tab').forEach(x => x.classList.toggle('on', x === t));
    document.querySelectorAll('.view').forEach(v => v.classList.toggle('on', v.id === 'v-' + mode));
  });

  // ---------- upload ----------
  const drop = $('#drop'), input = $('#file');
  function setFiles(list) {
    files = [...list]; const tot = files.reduce((a, f) => a + f.size, 0);
    if (tot > MAX_BYTES) { files = []; $('#flist').textContent = 'Passou de 25 MB. Para projetos grandes, rode a CLI localmente (veja o README).'; return; }
    $('#flist').innerHTML = files.map(f => `• ${f.name.replace(/[<>&]/g, '')} (${(f.size / 1024).toFixed(1)} KB)`).join('<br>');
  }
  input.onchange = () => setFiles(input.files);
  ['dragenter', 'dragover'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add('over'); }));
  ['dragleave', 'drop'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove('over'); }));
  drop.addEventListener('drop', e => setFiles(e.dataTransfer.files));

  // ---------- execução ----------
  const out = $('#out'), led = $('#led'), st = $('#st'), go = $('#go'), dl = $('#dl');
  let lastReport = '';
  function loadScript(u) { return new Promise((ok, no) => { const s = document.createElement('script'); s.src = u; s.onload = ok; s.onerror = () => no(new Error('Não foi possível baixar o interpretador Python. Verifique a conexão e tente de novo.')); document.head.append(s); }); }
  async function boot() {
    st.textContent = 'baixando o interpretador Python…';
    await loadScript(PYODIDE + 'pyodide.js');
    py = await loadPyodide({ indexURL: PYODIDE });
    py.FS.mkdirTree('/app/src'); py.FS.mkdirTree('/app/runtime');
    const names = [...C.files];
    for (const n of names) py.FS.writeFile('/app/src/' + n, await (await fetch('src/' + n)).text());
    py.FS.writeFile('/app/runtime/runner.py', await (await fetch('/_runtime/runner.py')).text());
    await py.runPythonAsync('import sys; sys.path.insert(0, "/app/runtime"); import runner');
  }
  function paint(t) {
    const e = s => s.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
    return t.split('\n').map(l => {
      const x = e(l);
      if (/FALHOU|ERRO|Traceback/i.test(l)) return `<span class="er">${x}</span>`;
      if (/\[!!\]|REVISAR|CWE-\d+|ALTA|HIGH|segredo|secret/i.test(l)) return `<span class="hi">${x}</span>`;
      if (/\bOK\b|Nenhum candidato|nenhum achado/i.test(l)) return `<span class="ok">${x}</span>`;
      return x;
    }).join('\n');
  }
  async function analisar() {
    go.disabled = true; led.className = 'led run'; dl.style.display = 'none'; out.textContent = '';
    try {
      if (!py) await boot();
      st.textContent = 'analisando…';
      let args, buf = '';
      py.setStdout({ batched: s => { buf += s + '\n'; } }); py.setStderr({ batched: s => { buf += s + '\n'; } });
      await py.runPythonAsync('alvo = runner.preparar("/work")');
      if (mode === 'autoteste') args = C.selftest;
      else if (mode === 'exemplo') {
        const name = (fn.value || C.samples[0].name).replace(/[^\w.\-]/g, '_');
        py.FS.writeFile('/work/alvo/' + name, src.value);
        args = C.args('/work/alvo', '/work/alvo/' + name, 1);
      } else {
        if (!files.length) throw new Error('Escolha ao menos um arquivo.');
        for (const f of files) py.FS.writeFile('/work/alvo/' + f.name.replace(/[^\w.\-]/g, '_'), new Uint8Array(await f.arrayBuffer()));
        const single = files.length === 1 ? '/work/alvo/' + files[0].name.replace(/[^\w.\-]/g, '_') : null;
        if (C.extractZip) {
          const avisos = py.runPython('runner.extrair_zips(alvo)').toJs();
          if (avisos.length) buf += avisos.map(a => '[aviso] ' + a).join('\n') + '\n\n';
        }
        args = C.args('/work/alvo', C.extractZip ? null : single, files.length);
      }
      py.globals.set('ARGS', py.toPy(args));
      const t0 = performance.now();
      const rc = await py.runPythonAsync(`runner.executar("/app/src", ${JSON.stringify(C.entry)}, ARGS)`);
      lastReport = buf || '(o script não imprimiu nada)';
      out.innerHTML = paint(lastReport);
      led.className = 'led ' + (rc === 0 ? 'ok' : 'warn');
      st.textContent = `concluído em ${Math.round(performance.now() - t0)} ms · código de saída ${rc}${rc ? ' (achados para revisar)' : ''}`;
      dl.style.display = '';
    } catch (err) {
      led.className = 'led err'; st.textContent = 'erro';
      out.innerHTML = `<span class="er">${String(err.message || err).split('\n').slice(-8).join('\n').replace(/[&<>]/g, '')}</span>`;
    } finally { go.disabled = false; }
  }
  go.onclick = analisar;
  dl.onclick = () => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([lastReport], { type: 'text/plain' })); a.download = `${C.repo}-relatorio.txt`; a.click(); };
})();
