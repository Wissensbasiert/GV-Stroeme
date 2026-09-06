  // One controller per dialog, even when several buttons open it.
  const dialogControllers = new WeakMap();
  function bindDialog(buttonId, dialogId, onOpen) {
    const button = document.getElementById(buttonId);
    const dialog = document.getElementById(dialogId);
    if (!button || !dialog) return;
    if (!button.matches('button, a[href], input')) {
      button.setAttribute('role', 'button');
      button.tabIndex = 0;
      button.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); button.click(); }
      });
    }
    let controller = dialogControllers.get(dialog);
    if (!controller) {
      let opener = null;
      const focusable = () => [...dialog.querySelectorAll('a[href], button, input, select, textarea, [tabindex]')]
        .filter(node => !node.disabled && node.tabIndex >= 0 && node.getClientRects().length && !node.closest('[hidden], [inert]'));
      dialog.setAttribute('role', 'dialog');
      dialog.setAttribute('aria-modal', 'true');
      dialog.tabIndex = -1;
      dialog.querySelectorAll('.modal-close').forEach(node => {
        if (!node.getAttribute('aria-label')) node.setAttribute('aria-label', 'Dialog schließen');
      });
      const close = () => {
        dialog.classList.remove('active');
        if (opener?.isConnected) opener.focus();
      };
      dialog.querySelectorAll('.modal-close, [data-close]').forEach(node => node.addEventListener('click', close));
      dialog.addEventListener('click', event => { if (event.target === dialog) close(); });
      document.addEventListener('keydown', event => {
        if (!dialog.classList.contains('active')) return;
        if (event.key === 'Escape') { event.preventDefault(); close(); return; }
        if (event.key !== 'Tab') return;
        const items = focusable();
        const first = items[0] || dialog, last = items.at(-1) || dialog;
        if (!items.length || !dialog.contains(document.activeElement) ||
            (event.shiftKey && document.activeElement === first) ||
            (!event.shiftKey && document.activeElement === last)) {
          event.preventDefault();
          (event.shiftKey ? last : first).focus();
        }
      });
      document.addEventListener('focusin', event => {
        if (dialog.classList.contains('active') && !dialog.contains(event.target)) (focusable()[0] || dialog).focus();
      });
      controller = { open(origin) {
        opener = origin;
        dialog.classList.add('active');
        (dialog.querySelector('.modal-close') || focusable()[0] || dialog).focus();
      }};
      dialogControllers.set(dialog, controller);
    }
    button.addEventListener('click', async () => {
      controller.open(button);
      await onOpen?.(dialogId);
    });
  }

