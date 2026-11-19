/* The message and typing payloads match messaging/consumers.py. */
(() => {
  'use strict';
  const root = document.querySelector('[data-chat]');
  if (!root) return;
  const form = root.querySelector('[data-chat-form]');
  const input = root.querySelector('[data-chat-input]');
  const send = root.querySelector('[data-send-message]');
  const status = root.querySelector('[data-connection-state]');
  const reconnect = root.querySelector('[data-reconnect]');
  const feedback = root.querySelector('[data-chat-feedback]');
  const history = root.querySelector('[data-chat-history]');
  const scroll = root.querySelector('[data-chat-scroll]');
  const empty = root.querySelector('[data-chat-empty]');
  const typing = root.querySelector('[data-typing]');
  const jump = root.querySelector('[data-new-messages]');
  const token = form.querySelector('[name=csrfmiddlewaretoken]').value;
  let socket, pending = null, typingTimer, incomingTypingTimer, isTyping = false;

  const say = message => { feedback.textContent = message; feedback.hidden = !message; };
  const connected = () => socket && socket.readyState === WebSocket.OPEN;
  const updateSend = () => { send.disabled = !connected() || pending !== null || !input.value.trim(); };
  const nearBottom = () => scroll.scrollHeight - scroll.scrollTop - scroll.clientHeight < 90;
  const scrollDown = () => { scroll.scrollTop = scroll.scrollHeight; jump.hidden = true; };
  const sendTyping = value => {
    if (value === isTyping) return;
    isTyping = value;
    if (connected()) socket.send(JSON.stringify({type:'typing', is_typing:value}));
  };

  function appendMessage(data) {
    const id = Number(data.message_id);
    if (!Number.isSafeInteger(id) || id <= 0 || history.querySelector(`[data-message-id="${id}"]`)) return;
    const mine = String(data.sender_id) === root.dataset.userId;
    const follow = nearBottom() || mine;
    const fragment = document.querySelector('#live-message-template').content.cloneNode(true);
    const article = fragment.querySelector('article');
    article.id = `message-${id}`;
    article.dataset.messageId = id;
    article.classList.toggle('mine', mine);
    const avatar = article.querySelector('.avatar');
    if (mine) avatar.remove(); else avatar.textContent = String(data.sender_email || '?').slice(0,1).toUpperCase();
    // Message text is always text, never executable HTML.
    article.querySelector('.message-bubble').textContent = String(data.content || '');
    article.querySelector('time').textContent = String(data.timestamp || '');
    article.querySelector('[data-delivery]').textContent = mine ? 'Sent' : '';
    article.querySelector('form').action = root.dataset.deletePattern.replace(/\/0\/$/, `/${id}/`);
    article.querySelector('[name=csrfmiddlewaretoken]').value = token;
    history.append(fragment);
    empty.hidden = true;
    if (mine && pending === data.content) {
      input.value = '';
      input.style.height = '';
      pending = null;
      input.readOnly = false;
      root.querySelector('[data-message-count]').textContent = '0 / 2000';
      say('');
    }
    if (!mine) typing.hidden = true;
    updateSend();
    if (follow) scrollDown(); else jump.hidden = false;
  }

  function connect() {
    if (socket && [WebSocket.OPEN, WebSocket.CONNECTING].includes(socket.readyState)) return;
    if (pending !== null) {
      say('A message may have been sent before disconnecting. Refresh to check the conversation before sending again.');
      return;
    }
    if (!('WebSocket' in window)) { status.textContent = 'Chat unavailable'; say('This browser does not support live chat.'); return; }
    status.dataset.state = 'connecting';
    status.textContent = 'Connecting…';
    reconnect.hidden = true;
    try { socket = new WebSocket(`${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}${root.dataset.wsPath}`); }
    catch { status.dataset.state = 'offline'; status.textContent = 'Disconnected'; reconnect.hidden = false; return; }
    socket.addEventListener('open', () => { status.dataset.state = 'connected'; status.textContent = 'Chat connected'; reconnect.hidden = true; isTyping = false; say(''); updateSend(); });
    socket.addEventListener('message', event => {
      let data;
      try { data = JSON.parse(event.data); } catch { return; }
      if (data.type === 'chat_message') appendMessage(data);
      if (data.type === 'typing') {
        typing.hidden = !data.is_typing;
        clearTimeout(incomingTypingTimer);
        if (data.is_typing) incomingTypingTimer = setTimeout(() => { typing.hidden = true; }, 4000);
      }
    });
    socket.addEventListener('close', () => {
      status.dataset.state = 'offline';
      status.textContent = 'Disconnected';
      reconnect.hidden = false;
      typing.hidden = true;
      isTyping = false;
      if (pending !== null) say('Connection interrupted. Your draft is safe; refresh to check whether it was delivered before resending.');
      else say('Chat is disconnected. Reconnect to continue. Your draft is safe.');
      updateSend();
    });
    socket.addEventListener('error', () => { say('Unable to connect to chat. Try reconnecting in a moment.'); });
  }

  form.addEventListener('submit', event => {
    event.preventDefault();
    const content = input.value.trim();
    if (!connected() || pending !== null || !content || content.length > 2000) return;
    pending = content;
    input.readOnly = true;
    sendTyping(false);
    try { socket.send(JSON.stringify({type:'chat_message', content})); say('Sending…'); }
    catch { pending = null; input.readOnly = false; say('Message could not be sent. Your draft is safe.'); }
    updateSend();
  });
  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = `${Math.min(input.scrollHeight,120)}px`;
    root.querySelector('[data-message-count]').textContent = `${input.value.length} / 2000`;
    updateSend();
    if (connected()) sendTyping(Boolean(input.value.trim()));
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => sendTyping(false), 1000);
  });
  input.addEventListener('blur', () => sendTyping(false));
  input.addEventListener('keydown', event => { if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) { event.preventDefault(); form.requestSubmit(); } });
  reconnect.addEventListener('click', connect);
  jump.addEventListener('click', scrollDown);
  scroll.addEventListener('scroll', () => { if (nearBottom()) jump.hidden = true; });
  empty.hidden = Boolean(history.querySelector('[data-message-id]'));
  scrollDown();
  connect();
  window.addEventListener('pagehide', () => { sendTyping(false); socket?.close(); });
  window.addEventListener('pageshow', event => { if (event.persisted) connect(); });
})();
