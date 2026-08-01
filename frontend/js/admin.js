function showTab(tabId) {
  document.querySelectorAll(".tab-pane").forEach(el => el.classList.add("d-none"));
  document.getElementById(tabId).classList.remove("d-none");

  document.querySelectorAll(".nav-link").forEach(el => el.classList.remove("active"));
  event.target.classList.add("active");

  if (tabId === "overview") loadStats();
  if (tabId === "companies") loadCompanies();
  if (tabId === "students") loadStudents();
  if (tabId === "jobs") loadJobs();
}

async function loadStats() {
  const stats = await apiAuthGet("/admin/dashboard");
  const row = document.getElementById("statsRow");
  row.innerHTML = "";
  const labels = {
    total_students: "Total Students",
    total_companies: "Total Companies",
    total_job_positions: "Job Postings",
    total_applications: "Applications",
    pending_company_approvals: "Pending Company Approvals",
    pending_job_approvals: "Pending Job Approvals",
  };
  for (const key in labels) {
    row.innerHTML += `
      <div class="col-md-4">
        <div class="card p-3 text-center">
          <div class="fs-3 fw-bold">${stats[key]}</div>
          <div class="text-muted">${labels[key]}</div>
        </div>
      </div>`;
  }
}

async function loadCompanies() {
  const companies = await apiAuthGet("/admin/companies");
  const tbody = document.getElementById("companiesTable");
  tbody.innerHTML = "";
  companies.forEach(c => {
    tbody.innerHTML += `
      <tr>
        <td>${c.company_name}</td>
        <td>${c.email}</td>
        <td>${c.approval_status}</td>
        <td>
          <button class="btn btn-sm btn-success" onclick="approveCompany(${c.id})">Approve</button>
          <button class="btn btn-sm btn-danger" onclick="rejectCompany(${c.id})">Reject</button>
        </td>
      </tr>`;
  });
}

async function approveCompany(id) {
  await apiAuthPost(`/admin/companies/${id}/approve`);
  loadCompanies();
}

async function rejectCompany(id) {
  await apiAuthPost(`/admin/companies/${id}/reject`);
  loadCompanies();
}

async function loadStudents() {
  const students = await apiAuthGet("/admin/students");
  const tbody = document.getElementById("studentsTable");
  tbody.innerHTML = "";
  students.forEach(s => {
    tbody.innerHTML += `
      <tr>
        <td>${s.name}</td>
        <td>${s.email}</td>
        <td>${s.branch || "-"}</td>
        <td>${s.cgpa || "-"}</td>
      </tr>`;
  });
}

async function loadJobs() {
  const jobs = await apiAuthGet("/admin/job-positions");
  const tbody = document.getElementById("jobsTable");
  tbody.innerHTML = "";
  jobs.forEach(j => {
    tbody.innerHTML += `
      <tr>
        <td>${j.title}</td>
        <td>${j.company_name}</td>
        <td>${j.status}</td>
        <td>
          <button class="btn btn-sm btn-success" onclick="approveJob(${j.id})">Approve</button>
          <button class="btn btn-sm btn-danger" onclick="rejectJob(${j.id})">Reject</button>
        </td>
      </tr>`;
  });
}

async function approveJob(id) {
  await apiAuthPost(`/admin/job-positions/${id}/approve`);
  loadJobs();
}

async function rejectJob(id) {
  await apiAuthPost(`/admin/job-positions/${id}/reject`);
  loadJobs();
}

loadStats();