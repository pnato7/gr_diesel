/**
 * Modal Personalizado - Sistema de confirmação
 * Substitui o confirm() padrão por um modal elegante
 */

class ConfirmModal {
  constructor() {
    this.backdrop = null;
    this.container = null;
    this.resolveCallback = null;
    this.init();
  }

  init() {
    // Criar backdrop
    this.backdrop = document.createElement('div');
    this.backdrop.className = 'modal-backdrop';
    this.backdrop.addEventListener('click', (e) => {
      if (e.target === this.backdrop) {
        this.close();
      }
    });

    // Criar container do modal
    this.container = document.createElement('div');
    this.container.className = 'modal-container';

    this.backdrop.appendChild(this.container);
    document.body.appendChild(this.backdrop);

    // Fechar ao pressionar Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.backdrop.classList.contains('active')) {
        this.close();
      }
    });
  }

  show(options = {}) {
    const {
      title = 'Confirmar ação',
      message = 'Tem certeza que deseja continuar?',
      cancelText = 'Cancelar',
      confirmText = 'Confirmar',
      isDanger = false
    } = options;

    // Montar HTML do modal
    this.container.innerHTML = `
      <div class="modal-header">
        <div class="modal-icon ${isDanger ? 'danger' : ''}">
          ${isDanger ? '⚠️' : 'ℹ️'}
        </div>
        <div class="modal-header-content">
          <h2 class="modal-title">${this.escapeHtml(title)}</h2>
          <p class="modal-subtitle">${this.escapeHtml(message)}</p>
        </div>
      </div>
      <div class="modal-footer">
        <button class="modal-btn modal-btn-cancel" data-action="cancel">
          ${this.escapeHtml(cancelText)}
        </button>
        <button class="modal-btn modal-btn-confirm" data-action="confirm">
          ${this.escapeHtml(confirmText)}
        </button>
      </div>
    `;

    // Adicionar listeners
    const cancelBtn = this.container.querySelector('[data-action="cancel"]');
    const confirmBtn = this.container.querySelector('[data-action="confirm"]');

    cancelBtn.addEventListener('click', () => this.close(false));
    confirmBtn.addEventListener('click', () => this.close(true));

    // Focus no botão confirmar
    setTimeout(() => confirmBtn.focus(), 100);

    // Mostrar modal
    this.backdrop.classList.add('active');

    // Retornar Promise
    return new Promise((resolve) => {
      this.resolveCallback = resolve;
    });
  }

  close(result = false) {
    this.backdrop.classList.remove('active');
    if (this.resolveCallback) {
      this.resolveCallback(result);
      this.resolveCallback = null;
    }
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Instância global
const confirmModal = new ConfirmModal();

/**
 * Função global para confirmar ações
 * Uso: showConfirm({ title: 'Deletar?', message: 'Tem certeza?' }).then(result => {...})
 */
window.showConfirm = function(options) {
  return confirmModal.show(options);
};

/**
 * Interceptar formulários com data-confirm
 * Uso: <form data-confirm="Deletar este cliente?">
 */
document.addEventListener('submit', async (e) => {
  const form = e.target;
  const confirmMsg = form.getAttribute('data-confirm');

  if (confirmMsg) {
    e.preventDefault();

    const result = await showConfirm({
      title: 'Confirmar ação',
      message: confirmMsg,
      confirmText: 'Sim, deletar',
      cancelText: 'Cancelar',
      isDanger: true
    });

    if (result) {
      form.submit();
    }
  }
});
