document.getElementById("role").addEventListener("change", (e) => {
  document.getElementById("companyNameField").style.display =
    e.target.value === "company" ? "block" : "none";
});

document.getElementById("registerForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errorBox = document.getElementById("error");
  const successBox = document.getElementById("success");
  errorBox.classList.add("d-none");
  successBox.classList.add("d-none");

  const payload = {
    role: document.getElementById("role").value,
    name: document.getElementById("name").value,
    email: document.getElementById("email").value,
    password: document.getElementById("password").value,
  };
  if (payload.role === "company") {
    payload.company_name = document.getElementById("companyName").value;
  }

  try {
    await apiPost("/auth/register", payload);
    successBox.textContent = "Registered! Redirecting to login...";
    successBox.classList.remove("d-none");
    setTimeout(() => (window.location.href = "index.html"), 1200);
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.classList.remove("d-none");
  }
});