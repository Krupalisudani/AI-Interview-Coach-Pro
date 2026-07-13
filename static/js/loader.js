/* ==========================================================================
   GLOBAL LOADER OVERLAY INTERACTION MANAGEMENT INTERFACES
   ========================================================================== */
function showLoader() {
    const loader = document.getElementById("global-loader");
    if (loader) loader.classList.remove("hidden");
}

function hideLoader() {
    const loader = document.getElementById("global-loader");
    if (loader) loader.classList.add("hidden");
}

// Ensure interface layer transitions exit cleanly on document load completion
window.addEventListener("load", () => {
    setTimeout(hideLoader, 200);
});