/**
 * Login and signup page logic.
 * Reads data-page attribute on <body> to decide which form to bind.
 */

document.addEventListener("DOMContentLoaded", () => {
  // If already logged in, redirect to dashboard.
  if (API.getToken() && API.getUser()) {
    window.location.href = "/dashboard";
    return;
  }

  const page = document.body.dataset.page;

  if (page === "login") initLogin();
  if (page === "signup") initSignup();
});


function initLogin() {
  const form = document.getElementById("loginForm");
  const errEl = document.getElementById("loginError");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errEl.textContent = "";

    const email = form.email.value.trim();
    const password = form.password.value;

    if (!email || !password) {
      errEl.textContent = "Please fill in all fields.";
      return;
    }

    try {
      const data = await API.login({ email, password });
      API.setToken(data.token);
      API.setUser(data.user);
      window.location.href = "/dashboard";
    } catch (err) {
      errEl.textContent = err.message;
    }
  });
}


function initSignup() {
  const form = document.getElementById("signupForm");
  const errEl = document.getElementById("signupError");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errEl.textContent = "";

    const name = form.fullName.value.trim();
    const email = form.email.value.trim();
    const password = form.password.value;
    const clinicName = form.clinicName.value.trim();
    const role = form.role.value;

    if (!name || !email || !password || !clinicName || !role) {
      errEl.textContent = "Please fill in all fields.";
      return;
    }

    try {
      const data = await API.signup({
        name,
        email,
        password,
        clinic_name: clinicName,
        role,
      });
      API.setToken(data.token);
      API.setUser(data.user);
      window.location.href = "/dashboard";
    } catch (err) {
      errEl.textContent = err.message;
    }
  });
}
