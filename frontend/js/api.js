/**
 * API client module.
 * Wraps fetch with auth headers and JSON handling.
 */

const API = {
  getToken() {
    return localStorage.getItem("token");
  },

  setToken(token) {
    localStorage.setItem("token", token);
  },

  setUser(user) {
    localStorage.setItem("user", JSON.stringify(user));
  },

  getUser() {
    try {
      return JSON.parse(localStorage.getItem("user"));
    } catch {
      return null;
    }
  },

  clearAuth() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  },

  async request(method, path, body, isFormData = false) {
    const headers = {};
    const token = this.getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
    if (!isFormData) headers["Content-Type"] = "application/json";

    const options = { method, headers };
    if (body) {
      options.body = isFormData ? body : JSON.stringify(body);
    }

    const resp = await fetch(path, options);

    if (resp.status === 401 && !["/api/auth/login", "/api/auth/signup"].includes(path)) {
      this.clearAuth();
      window.location.href = "/login";
      return;
    }

    if (!resp.ok) {
      const text = await resp.text();
      let message;
      try {
        message = JSON.parse(text).detail || text;
      } catch {
        message = text;
      }
      throw new Error(message);
    }

    return resp.json();
  },

  // Auth
  signup(data) { return this.request("POST", "/api/auth/signup", data); },
  login(data) { return this.request("POST", "/api/auth/login", data); },
  me() { return this.request("GET", "/api/auth/me"); },

  // Scribe
  transcribe(formData) { return this.request("POST", "/api/scribe/transcribe", formData, true); },
  analyze(data) { return this.request("POST", "/api/scribe/analyze", data); },
  finalize(data) { return this.request("POST", "/api/scribe/finalize", data); },
  sessions() { return this.request("GET", "/api/scribe/sessions"); },
  getSession(id) { return this.request("GET", `/api/scribe/sessions/${id}`); },
};
