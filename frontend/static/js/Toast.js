/**
 * Toast Notification System
 * 
 * A modern, non-blocking replacement for native alert() dialogs.
 * Toasts appear in the top-right corner, auto-dismiss after a configurable
 * duration, and can be manually closed.
 *
 * Usage:
 *   showToast("Operation successful!", "success");
 *   showToast("Something went wrong", "error");
 *   showToast("Be careful", "warning");
 *   showToast("FYI", "info");
 *
 * Types: "success" | "error" | "warning" | "info" (default: "info")
 * Duration: milliseconds (default: 4000 for success/info, 6000 for error/warning)
 */

// Ensure the toast container exists in the DOM
(function initToastContainer() {
    if (!document.getElementById("toast-container")) {
        const container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }
})();

const TOAST_ICONS = {
    success: "✅",
    error: "❌",
    warning: "⚠️",
    info: "ℹ️",
};

const TOAST_DEFAULT_DURATIONS = {
    success: 4000,
    error: 6000,
    warning: 6000,
    info: 4000,
};

/**
 * Display a toast notification.
 * @param {string} message - The message to display.
 * @param {string} [type="info"] - Toast type: "success", "error", "warning", or "info".
 * @param {number} [duration] - Auto-dismiss duration in ms (0 = no auto-dismiss).
 */
function showToast(message, type = "info", duration) {
    const container = document.getElementById("toast-container");
    if (!container) return;

    // Resolve duration
    const ms = duration !== undefined ? duration : (TOAST_DEFAULT_DURATIONS[type] || 4000);
    const icon = TOAST_ICONS[type] || TOAST_ICONS.info;

    // Create toast element
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.style.position = "relative";
    toast.style.overflow = "hidden";

    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
        <button class="toast-close" aria-label="Close notification">&times;</button>
        ${ms > 0 ? `<div class="toast-progress" style="animation-duration: ${ms}ms;"></div>` : ""}
    `;

    // Close button handler
    toast.querySelector(".toast-close").addEventListener("click", () => dismissToast(toast));

    // Add to container
    container.appendChild(toast);

    // Auto-dismiss
    if (ms > 0) {
        setTimeout(() => dismissToast(toast), ms);
    }

    // Limit max visible toasts to 5 (remove oldest)
    const toasts = container.querySelectorAll(".toast:not(.toast-exit)");
    if (toasts.length > 5) {
        dismissToast(toasts[0]);
    }
}

/**
 * Dismiss a toast with exit animation.
 */
function dismissToast(toastElement) {
    if (!toastElement || toastElement.classList.contains("toast-exit")) return;
    toastElement.classList.add("toast-exit");
    setTimeout(() => {
        if (toastElement.parentNode) {
            toastElement.parentNode.removeChild(toastElement);
        }
    }, 300);
}

/**
 * Escape HTML to prevent XSS in toast messages.
 */
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Recursively escape strings received from the API before interpolating them
 * into legacy innerHTML templates. 
 * SECURITY FIX: This prevents XSS (Cross-Site Scripting) attacks where a malicious 
 * user could input `<script>alert('hack')</script>` as their name or observation.
 * By escaping it to HTML entities, the browser renders it as safe text instead of executing it.
 */
function sanitizeApiData(value) {
    if (typeof value === "string") return escapeHtml(value);
    if (Array.isArray(value)) return value.map(sanitizeApiData);
    if (value && typeof value === "object") {
        return Object.fromEntries(
            Object.entries(value).map(([key, nestedValue]) => [key, sanitizeApiData(nestedValue)])
        );
    }
    return value;
}

// Make showToast globally available
window.showToast = showToast;
window.escapeHtml = escapeHtml;
window.sanitizeApiData = sanitizeApiData;
