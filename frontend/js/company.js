let currentJobs = [];

function showTab(tabId) {
  document.querySelectorAll(".tab-pane").forEach(el => el.classList.add("d-none"));
  document.getElementById(tabId).classList.remove("d-none");

  document.querySelectorAll(".nav-link").forEach(el => el.classList.remove("active"));
  event.target.classList.add("active");

  if (tabId === "overview") loadStats();
  if (tabId === "profile") loadProfile();
  if (tabId === "myJobs") loadMyJobs();
}

async function loadStats() {
  const stats = await apiAuthGet("/company/dashboard");
  checkApproval(stats.approval_status);

  const row = document.getElementById("statsRow");
  row.innerHTML = `
    <div class="col-md-4">
      <div class="card p-3 text-center">
        <div class="fs-3 fw-bold">${stats.total_job_postings}</div>
        <div class="text-muted">Job Postings</div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card p-3 text-center">
        <div class="fs-3 fw-bold">${stats.total_applicants}</div>
        <div class="text-muted">Total Applicants</div>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card p-3 text-center">
        <div class="fs-5 fw-bold text-capitalize">${stats.approval_status}</div>
        <div class="text-muted">Approval Status</div>
      </div>
    </div>`;
}

function checkApproval(status) {
  const banner = document.getElementById("approvalBanner");
  if (status !== "approved") {
    banner.innerHTML = `<div class="alert alert-warning">Your company is <strong>${status}</strong>. You can post jobs only after admin approval.</div>`;
  } else {
    banner.innerHTML = "";
  }
}

async function loadProfile() {
  const p = await apiAuthGet("/company/profile");
  document.getElementById("pf_name").value = p.company_name || "";
  document.getElementById("pf_industry").value = p.industry || "";
  document.getElementById("pf_location").value = p.location || "";
  document.getElementById("pf_contact").value = p.hr_contact || "";
  document.getElementById("pf_website").value = p.website || "";
}

async function saveProfile() {
  const msg = document.getElementById("profileMsg");
  try {
    await apiAuthPut("/company/profile", {
      company_name: document.getElementById("pf_name").value,
      industry: document.getElementById("pf_industry").value,
      location: document.getElementById("pf_location").value,
      hr_contact: document.getElementById("pf_contact").value,
      website: document.getElementById("pf_website").value,
    });
    msg.innerHTML = `<div class="alert alert-success">Profile updated.</div>`;
  } catch (err) {
    msg.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

async function postJob() {
  const msg = document.getElementById("jobMsg");
  const deadlineInput = document.getElementById("job_deadline").value;
  try {
    await apiAuthPostBody("/company/job-positions", {
      title: document.getElementById("job_title").value,
      description: document.getElementById("job_desc").value,
      skills_required: document.getElementById("job_skills").value,
      salary: document.getElementById("job_salary").value,
      application_deadline: deadlineInput,
    });
    msg.innerHTML = `<div class="alert alert-success">Job submitted for admin approval.</div>`;
  } catch (err) {
    msg.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

async function loadMyJobs() {
  currentJobs = await apiAuthGet("/company/job-positions");
  const tbody = document.getElementById("jobsTable");
  tbody.innerHTML = "";
  currentJobs.forEach(j => {
    tbody.innerHTML += `
      <tr>
        <td>${j.title}</td>
        <td>${j.status}</td>
        <td>${j.applicant_count}</td>
        <td><button class="btn btn-sm btn-outline-primary" onclick="viewApplicants(${j.id})">View Applicants</button></td>
      </tr>`;
  });
}

async function viewApplicants(jobId) {
  const applicants = await apiAuthGet(`/company/job-positions/${jobId}/applicants`);
  const panel = document.getElementById("applicantsPanel");

  if (applicants.length === 0) {
    panel.innerHTML = `<div class="alert alert-info mt-3">No applicants yet for this job.</div>`;
    return;
  }

  let rows = applicants.map(a => `
    <tr>
      <td>${a.student_name}</td>
      <td>${a.student_email}</td>
      <td>${a.branch || "-"}</td>
      <td>${a.cgpa || "-"}</td>
      <td>${a.status}</td>
      <td>
        <select class="form-select form-select-sm" onchange="updateStatus(${a.application_id}, this.value, ${jobId})">
          <option value="">Change status...</option>
          <option value="shortlisted">Shortlisted</option>
          <option value="interview">Interview</option>
          <option value="offer">Offer</option>
          <option value="rejected">Rejected</option>
          <option value="placed">Placed</option>
        </select>
      </td>
    </tr>`).join("");

  panel.innerHTML = `
    <h5 class="mt-4">Applicants</h5>
    <table class="table bg-white">
      <thead><tr><th>Name</th><th>Email</th><th>Branch</th><th>CGPA</th><th>Status</th><th>Update</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

async function updateStatus(applicationId, newStatus, jobId) {
  if (!newStatus) return;
  await apiAuthPostBody(`/company/applications/${applicationId}/status`, { status: newStatus });
  viewApplicants(jobId);
}

loadStats();