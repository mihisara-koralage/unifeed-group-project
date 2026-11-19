(() => {
  'use strict';
  const search = document.querySelector('[data-conversation-search]');
  if (!search) return;
  const rows = [...document.querySelectorAll('[data-conversation]')];
  search.addEventListener('input', () => {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    rows.forEach(row => { row.hidden = !row.textContent.toLocaleLowerCase().includes(query); if (!row.hidden) visible++; });
    document.querySelector('[data-inbox-empty]').hidden = rows.length === 0 || visible > 0;
    document.querySelector('[data-inbox-status]').textContent = `${visible} conversations shown.`;
  });
})();
