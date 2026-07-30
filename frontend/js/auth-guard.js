const token = localStorage.getItem("token");
const role = localStorage.getItem("role");
const name = localStorage.getItem("name");

function checkAuth() {
  const currentToken = localStorage.getItem("token");
  if (!currentToken) {
    window.location.href = "index.html";
  }
}

checkAuth();

document.getElementById("userName").textContent = name ? `${name} (${role})` : "";

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  localStorage.removeItem("name");
  window.location.href = "index.html";
}

// Re-check auth whenever the page is restored from bfcache (e.g. browser back button)
window.addEventListener("pageshow", (event) => {
  if (event.persisted) {
    checkAuth();
  }
});