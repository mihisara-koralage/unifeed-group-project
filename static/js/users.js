/* Module 1 only. The committed Django forms remain the source of validation. */
(() => {
  'use strict';
  document.querySelectorAll('.field-group').forEach(group => {
    const input = group.querySelector('input:not([type=checkbox]), textarea');
    if (!input) return;
    const errors = group.querySelector('.field-errors');
    const help = group.querySelector('.field-help');
    const descriptions = [help?.id, errors?.id].filter(Boolean);
    if (descriptions.length) input.setAttribute('aria-describedby', descriptions.join(' '));
    if (errors) input.setAttribute('aria-invalid', 'true');
  });

  document.querySelectorAll('input[type="password"]').forEach(input => {
    const wrapper = document.createElement('div');
    wrapper.className = 'password-input';
    input.before(wrapper);
    wrapper.append(input);
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'password-toggle';
    toggle.textContent = 'Show';
    const label = input.labels[0]?.textContent.replace('*', '').trim().toLowerCase() || 'password';
    toggle.setAttribute('aria-label', `Show ${label}`);
    toggle.setAttribute('aria-pressed', 'false');
    toggle.setAttribute('aria-controls', input.id);
    toggle.addEventListener('click', () => {
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      toggle.textContent = show ? 'Hide' : 'Show';
      toggle.setAttribute('aria-label', `${show ? 'Hide' : 'Show'} ${label}`);
      toggle.setAttribute('aria-pressed', String(show));
    });
    wrapper.append(toggle);
  });

  const form = document.querySelector('[data-profile-form]');
  if (form) {
    const input = form.querySelector('input[type=file]');
    const preview = form.querySelector('[data-avatar-preview]');
    const status = form.querySelector('[data-avatar-status]');
    let url;
    input?.addEventListener('change', () => {
      if (url) URL.revokeObjectURL(url);
      preview.hidden = true;
      const file = input.files[0];
      if (!file) return;
      if (!file.type.startsWith('image/')) {
        input.value = '';
        status.textContent = 'Please choose an image file for your profile photo.';
        return;
      }
      url = URL.createObjectURL(file);
      preview.src = url;
      preview.hidden = false;
      status.textContent = `${file.name} selected. Save your profile to upload it.`;
    });
  }
})();
