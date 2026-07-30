document.getElementById("loginForm").reset();

document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const errorBox = document.getElementById("error");
  errorBox.classList.add("d-none");

  try {
    const data = await apiPost("/auth/login", { email, password });
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("role", data.role);
    localStorage.setItem("name", data.name);

    if (data.role === "admin") window.location.href = "admin.html";
    else if (data.role === "company") window.location.href = "company.html";
    else window.location.href = "student.html";
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.classList.remove("d-none");
  }
});