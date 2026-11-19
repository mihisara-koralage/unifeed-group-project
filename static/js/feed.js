(() => {
  'use strict';
  let toastTimer;
  window.communityToast = message => {
    const toast = document.querySelector('#community-toast');
    toast.textContent = message;
    toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { toast.hidden = true; }, 5000);
  };

  const composer = document.querySelector('[data-composer]');
  if (composer) {
    const content = composer.querySelector('textarea');
    const file = composer.querySelector('input[type=file]');
    const preview = composer.querySelector('[data-photo-preview]');
    const image = composer.querySelector('[data-photo-image]');
    const status = composer.querySelector('[data-photo-status]');
    let objectUrl;
    const count = () => { composer.querySelector('[data-content-count]').textContent = `${content.value.length} / 1000`; };
    content.addEventListener('input', count);
    count();
    file.addEventListener('change', () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      preview.hidden = true;
      const selected = file.files[0];
      if (!selected) return;
      if (!selected.type.startsWith('image/')) { file.value = ''; window.communityToast('Please choose an image file.'); return; }
      objectUrl = URL.createObjectURL(selected);
      image.src = objectUrl;
      preview.hidden = false;
      status.textContent = `${selected.name} selected.`;
    });
    composer.querySelector('[data-remove-photo]').addEventListener('click', () => {
      file.value = '';
      preview.hidden = true;
      image.removeAttribute('src');
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      objectUrl = null;
      status.textContent = 'Selected photo removed.';
    });
    composer.addEventListener('submit', () => {
      if (!composer.checkValidity()) return;
      const button = composer.querySelector('[type=submit]');
      button.disabled = true;
      button.textContent = 'Posting…';
    });
    window.addEventListener('pageshow', () => {
      const button = composer.querySelector('[type=submit]');
      button.disabled = false;
      if (button.textContent === 'Posting…') button.textContent = 'Post →';
    });
  }

  const feed = document.querySelector('[data-feed]');
  if (feed) {
    const posts = [...feed.querySelectorAll('[data-post]')];
    const search = feed.querySelector('[data-feed-search]');
    const buttons = [...feed.querySelectorAll('[data-filter]')];
    let selected = 'all';
    const filter = () => {
      const query = search.value.trim().toLocaleLowerCase();
      let visible = 0;
      posts.forEach(post => {
        const matches = selected === 'all' || (selected === 'mine' && post.dataset.author === feed.dataset.currentUser) || (selected === 'photos' && post.dataset.photo === 'true');
        post.hidden = !matches || !post.textContent.toLocaleLowerCase().includes(query);
        if (!post.hidden) visible++;
      });
      feed.querySelector('[data-filter-empty]').hidden = !posts.length || visible > 0;
      feed.querySelector('[data-filter-status]').textContent = `Showing ${visible} of ${posts.length} posts.`;
      const end = feed.querySelector('.feed-end');
      if (end) end.hidden = visible === 0;
    };
    buttons.forEach(button => button.addEventListener('click', () => {
      selected = button.dataset.filter;
      buttons.forEach(item => { const active = item === button; item.classList.toggle('active', active); item.setAttribute('aria-pressed', String(active)); });
      filter();
    }));
    search.addEventListener('input', filter);
    feed.querySelector('[data-clear-filters]').addEventListener('click', () => { search.value = ''; buttons[0].click(); search.focus(); });
    const tags = new Map();
    feed.querySelectorAll('[data-post-tag]').forEach(link => {
      const name = link.dataset.postTag;
      const tag = tags.get(name) || {count:0, href:link.getAttribute('href')};
      tag.count++;
      tags.set(name,tag);
    });
    if (tags.size) {
      const target = feed.querySelector('[data-discovery-tags]');
      target.replaceChildren();
      [...tags.entries()].sort((a,b) => b[1].count-a[1].count || a[0].localeCompare(b[0])).slice(0,6).forEach(([name,tag]) => {
        const link = document.createElement('a');
        link.href = tag.href;
        const title = document.createElement('strong');
        title.textContent = `#${name}`;
        const count = document.createElement('span');
        count.textContent = `${tag.count} ${tag.count === 1 ? 'post' : 'posts'}`;
        link.append(title,count);
        target.append(link);
      });
    }
  }

  document.addEventListener('click', async event => {
    const more = event.target.closest('[data-read-more]');
    if (more) {
      const expanded = more.getAttribute('aria-expanded') !== 'true';
      more.setAttribute('aria-expanded', String(expanded));
      document.getElementById(more.getAttribute('aria-controls')).classList.toggle('post-truncated', !expanded);
      more.textContent = expanded ? 'Show less' : 'Read more';
    }
    const copy = event.target.closest('[data-copy-post]');
    if (copy) {
      try { await navigator.clipboard.writeText(new URL(copy.dataset.copyPost, location.origin).href); window.communityToast('Post link copied. Share a little campus connection.'); }
      catch { window.communityToast('Your browser blocked copying. Open the post and copy its link from the address bar.'); }
    }
  });
})();
