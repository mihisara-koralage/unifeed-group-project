/* Progressive enhancements; all submission and filtering works without JS. */
(() => {
  const form = document.querySelector('[data-resource-form]');
  if (!form) return;
  ['title', 'url', 'category', 'description'].forEach(name => {
    const input = form.elements.namedItem(name);
    if (!input) return;
    const ids = [input.getAttribute('aria-describedby')];
    const help = document.getElementById(`resource-${name}-help`);
    const error = document.getElementById(`resource-${name}-error`);
    if (help) ids.push(help.id);
    if (error) { ids.push(error.id); input.setAttribute('aria-invalid', 'true'); }
    const describedBy = ids.filter(Boolean).join(' ');
    if (describedBy) input.setAttribute('aria-describedby', describedBy);
  });
  const url = form.elements.namedItem('url');
  const validateURL = () => {
    const value = url.value.trim();
    let message = '';
    if (value) {
      try {
        const parsed = new URL(value);
        if (!/^https?:\/\/\S+$/i.test(value) || !['http:', 'https:'].includes(parsed.protocol)) {
          message = 'Please enter a full link starting with http:// or https://';
        } else if (parsed.username || parsed.password) {
          message = 'Resource links must not contain a username or password.';
        }
      } catch (_) { message = 'Please enter a full link starting with http:// or https://'; }
    }
    url.setCustomValidity(message);
  };
  url.addEventListener('input', validateURL);
  validateURL();
  const description = form.elements.namedItem('description');
  const count = form.querySelector('[data-description-count]');
  const updateCount = () => { count.textContent = `${description.value.length} / 500`; };
  description.addEventListener('input', updateCount);
  updateCount();
  const invalid = form.querySelector('[aria-invalid="true"]');
  if (invalid) invalid.focus();
})();
