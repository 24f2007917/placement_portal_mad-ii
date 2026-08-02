function showTab(tabId) {
  document.querySelectorAll(".tab-pane").forEach(el => el.classList.add("d-none"));
  document.getElementById(tabId).classList.remove("d-none");

  document.querySelectorAll(".nav-link").forEach(el => el.classList.remove("active"));
  event.target.classList.add("active");

  if (tabId === "overview") loadStats();
  if (tabId === "browse") browseJobs();
  if (tabId === "applications") loadApplications();
  if (tabId === "profile") loadProfile();
}

async function loadStats() {
  const stats = await apiAuthGet("/student/dashboard");
  document.getElementById("statsRow").innerHTML = `
    <div class="col-md-4">
      <div class="card p-3 text-center">
        <div class="fs-3 fw-bold">${stats.total_applications}</div>
        <div class="text-muted">Total Applications</div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card p-3 text-center">
        <div class="fs-3 fw-bold">${stats.shortlisted_count}</div>
        <div class="text-muted">Shortlisted or Further</div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card p-3 text-center">
        <div class="fs-5 fw-bold">${stats.branch || "-"} ${stats.cgpa ? "| CGPA " + stats.cgpa : ""}</div>
        <div class="text-muted">Profile</div>
      </div>
    </div>`;
}

async function browseJobs() {
  const q = document.getElementById("searchBox").value;
  const jobs = await apiAuthGet("/student/job-positions" + (q ? `?q=${encodeURIComponent(q)}` : ""));
  const grid = document.getElementById("jobsGrid");
  grid.innerHTML = "";

  if (jobs.length === 0) {
    grid.innerHTML = `<div class="text-muted">No approved job postings found.</div>`;
    return;
  }

  jobs.forEach(j => {
    grid.innerHTML += `
      <div class="col-md-6">
        <div class="card p-3">
          <h5>${j.title}</h5>
          <div class="text-muted small mb-2">${j.company_name}</div>
          <p class="small">${j.description || ""}</p>
          <div class="small text-muted mb-2">
            Deadline: ${new Date(j.application_deadline).toLocaleDateString()} |
            Salary: ${j.salary || "-"} |
            Min CGPA: ${j.min_cgpa}
          </div>
          <button class="btn btn-sm btn-primary" ${j.already_applied ? "disabled" : ""} onclick="applyToJob(${j.id})">
            ${j.already_applied ? "Already Applied" : "Apply"}
          </button>
        </div>
      </div>`;
  });
}

async function applyToJob(jobId) {
  try {
    await apiAuthPost(`/student/job-positions/${jobId}/apply`);
    browseJobs();
  } catch (err) {
    alert(err.message);
  }
}

async function loadApplications() {
  const apps = await apiAuthGet("/student/applications");
  const tbody = document.getElementById("applicationsTable");
  tbody.innerHTML = "";
  apps.forEach(a => {
    tbody.innerHTML += `
      <tr>
        <td>${a.company_name}</td>
        <td>${a.job_title}</td>
        <td>${new Date(a.application_date).toLocaleDateString()}</td>
        <td><span class="badge bg-secondary text-capitalize">${a.status}</span></td>
      </tr>`;
  });
}

async function loadProfile() {
  const p = await apiAuthGet("/student/profile");
  document.getElementById("pf_branch").value = p.branch || "";
  document.getElementById("pf_cgpa").value = p.cgpa || "";
  document.getElementById("pf_year").value = p.year || "";
  document.getElementById("pf_skills").value = p.skills || "";
}

async function saveProfile() {
  const msg = document.getElementById("profileMsg");
  try {
    await apiAuthPut("/student/profile", {
      branch: document.getElementById("pf_branch").value,
      cgpa: parseFloat(document.getElementById("pf_cgpa").value) || null,
      year: parseInt(document.getElementById("pf_year").value) || null,
      skills: document.getElementById("pf_skills").value,
    });
    msg.innerHTML = `<div class="alert alert-success">Profile updated.</div>`;
  } catch (err) {
    msg.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

loadStats();