const API_BASE = "http://127.0.0.1:5000/api";

async function apiPost(path, data) {
  const res = await fetch(API_BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  const body = await res.json();
  if (!res.ok) {
    throw new Error(body.error || "Something went wrong");
  }
  return body;
}

async function apiAuthGet(path) {
  const token = localStorage.getItem("token");
  const res = await fetch(API_BASE + path, {
    headers: { Authorization: "Bearer " + token },
  });
  const body = await res.json();
  if (!res.ok) {
    throw new Error(body.error || "Something went wrong");
  }
  return body;
}

async function apiAuthPost(path) {
  const token = localStorage.getItem("token");
  const res = await fetch(API_BASE + path, {
    method: "POST",
    headers: { Authorization: "Bearer " + token },
  });
  const body = await res.json();
  if (!res.ok) {
    throw new Error(body.error || "Something went wrong");
  }
  return body;
}

async function apiAuthPut(path, data) {
  const token = localStorage.getItem("token");
  const res = await fetch(API_BASE + path, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Authorization: "Bearer " + token },
    body: JSON.stringify(data),
  });
  const body = await res.json();
  if (!res.ok) {
    throw new Error(body.error || "Something went wrong");
  }
  return body;
}

async function apiAuthPostBody(path, data) {
  const token = localStorage.getItem("token");
  const res = await fetch(API_BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: "Bearer " + token },
    body: JSON.stringify(data),
  });
  const body = await res.json();
  if (!res.ok) {
    throw new Error(body.error || "Something went wrong");
  }
  return body;
}