document.addEventListener('DOMContentLoaded', () => {
  const usernameEl = document.getElementById('username');
  const btnLogin = document.getElementById('btnLogin');
  const btnDemo = document.getElementById('btnDemo');
  const messagesEl = document.getElementById('messages');
  const textEl = document.getElementById('text');
  const sendBtn = document.getElementById('send');
  const statusDot = document.getElementById('statusDot');
  const statusText = document.getElementById('statusText');
  const meName = document.getElementById('meName');
  const connCount = document.getElementById('connCount');
  const loginContainer = document.getElementById('login');

  let ws = null;
  let username = null;
  let explicitClose = false;

  function setStatus(ok){
    if(ok){
      statusDot.classList.add('ok');
      statusText.textContent = 'conectado';
    } else {
      statusDot.classList.remove('ok');
      statusText.textContent = 'desconectado';
    }
  }

  function addMessage(text, cls='msg others'){
    const el = document.createElement('div');
    el.className = cls;
    el.innerHTML = text;
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function wsUrl(){
    const scheme = location.protocol === 'https:' ? 'wss' : 'ws';
    return `${scheme}://${location.host}/ws`;
  }

  function connect(){
    if(ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;
    explicitClose = false;
    ws = new WebSocket(wsUrl());
    setStatus(false);

    ws.addEventListener('open', () => {
      setStatus(true);
      addMessage(`<strong>[system]</strong> conectado al servidor`, 'msg system');
    });

    ws.addEventListener('message', (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if(data.type === 'chat'){
          const isMe = (data.from === username);
          if(isMe) addMessage(`<div>${data.text}<div class="meta">${data.from}</div></div>`, 'msg me');
          else addMessage(`<div>${data.text}<div class="meta">${data.from}</div></div>`, 'msg others');
        } else if (data.type === 'system'){
          addMessage(`<em>${data.text}</em>`, 'msg system');
        }
      } catch(e){
        addMessage(`[raw] ${ev.data}`, 'msg others');
      }
    });

    ws.addEventListener('close', (ev) => {
      setStatus(false);
      addMessage(`<em>desconectado (code=${ev.code})</em>`, 'msg system');
      if(!explicitClose) setTimeout(connect, 1500);
    });

    ws.addEventListener('error', (e) => {
      console.error('WS error', e);
    });
  }

  async function doLogin(name){
    try {
      const res = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        credentials: 'same-origin',
        body: JSON.stringify({username: name})
      });
      const j = await res.json();
      if(!res.ok || !j.ok) { alert('Login falló'); return false; }
      username = j.username;
      meName.textContent = username;
      loginContainer.style.display = 'none';
      connect();
      return true;
    } catch(err){
      console.error('login error', err);
      alert('Error en login (ver consola)');
      return false;
    }
  }

  btnLogin.addEventListener('click', async () => {
    const v = usernameEl.value.trim();
    if(!v) return alert('Escribe tu nombre');
    btnLogin.disabled = true;
    const ok = await doLogin(v);
    btnLogin.disabled = false;
    if(!ok) setStatus(false);
  });

  btnDemo.addEventListener('click', async () => {
    const rnd = 'user' + Math.floor(Math.random()*9000 + 100);
    usernameEl.value = rnd;
    await doLogin(rnd);
  });

  sendBtn.addEventListener('click', () => {
    const txt = textEl.value.trim();
    if(!txt) return;
    if(!ws || ws.readyState !== WebSocket.OPEN){ alert('No conectado'); return; }
    ws.send(JSON.stringify({type:'chat', text: txt}));
    textEl.value = '';
  });

  textEl.addEventListener('keydown', (e) => { if(e.key === 'Enter') sendBtn.click(); });

  setStatus(false);
  // export for quick debugging in console
  window._rt = { connect, doLogin };
});
