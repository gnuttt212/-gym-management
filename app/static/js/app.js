/**
 * GYM Manager – Utility JavaScript
 */

'use strict';

/**
 * Format a number as Vietnamese currency (VND).
 * @param {number} amount
 * @returns {string} e.g. "1.200.000đ"
 */
function formatVND(amount) {
    return new Intl.NumberFormat('vi-VN').format(amount) + 'đ';
}

/**
 * Show a Bootstrap toast notification.
 * @param {string} message
 * @param {string} type - 'success' | 'danger' | 'warning' | 'info'
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') ||
        (() => {
            const div = document.createElement('div');
            div.id = 'toast-container';
            div.className = 'toast-container position-fixed top-0 end-0 p-3';
            div.style.zIndex = '1080';
            document.body.appendChild(div);
            return div;
        })();

    const toastHTML = `
        <div class="toast align-items-center text-bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto"
                        data-bs-dismiss="toast"></button>
            </div>
        </div>`;

    container.insertAdjacentHTML('beforeend', toastHTML);
    const toastEl = container.lastElementChild;
    const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
    toast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

/**
 * Confirm action with a Bootstrap modal.
 * @param {string} message
 * @returns {Promise<boolean>}
 */
function confirmAction(message) {
    return new Promise((resolve) => {
        if (confirm(message)) {
            resolve(true);
        } else {
            resolve(false);
        }
    });
}
