/* api.js — Centralized API client for CareerCraft AI */

const API_BASE = 'http://localhost:8000/api';

const Api = {
  /* ── Resume Analysis ─────────────────── */
  async analyzeResume(file) {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${API_BASE}/analyze`, { method: 'POST', body: form });
    if (!res.ok) throw await _parseError(res);
    return res.json();
  },

  /* ── Job Match ───────────────────────── */
  async matchJob(resumeText, jobDescription) {
    const res = await fetch(`${API_BASE}/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription }),
    });
    if (!res.ok) throw await _parseError(res);
    return res.json();
  },

  /* ── Builder: Summary ────────────────── */
  async generateSummary(payload) {
    const res = await fetch(`${API_BASE}/builder/summary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw await _parseError(res);
    return res.json();
  },

  /* ── Builder: Rewrite Bullet ─────────── */
  async rewriteBullet(bullet, context = '') {
    const res = await fetch(`${API_BASE}/builder/rewrite-bullet`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bullet, context }),
    });
    if (!res.ok) throw await _parseError(res);
    return res.json();
  },

  /* ── Builder: Suggest Skills ─────────── */
  async suggestSkills(targetRole, currentSkills = '', experienceLevel = 'fresher') {
    const res = await fetch(`${API_BASE}/builder/suggest-skills`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_role: targetRole, current_skills: currentSkills, experience_level: experienceLevel }),
    });
    if (!res.ok) throw await _parseError(res);
    return res.json();
  },

  /* ── Builder: Improve Section ────────── */
  async improveSection(sectionName, originalContent, targetRole = '') {
    const res = await fetch(`${API_BASE}/builder/improve-section`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ section_name: sectionName, original_content: originalContent, target_role: targetRole }),
    });
    if (!res.ok) throw await _parseError(res);
    return res.json();
  },

  /* ── Builder: Tailor from Resume + Job Description ── */
  async tailorResume(file, jobDescription) {
    const form = new FormData();
    form.append('file', file);
    form.append('job_description', jobDescription);
    const res = await fetch(`${API_BASE}/builder/tailor`, { method: 'POST', body: form });
    if (!res.ok) throw await _parseError(res);
    return res.json();
  },

  /* ── Interview Prep ──────────────────── */
  async interviewPrep(resumeText, jobDescription = '') {
    const res = await fetch(`${API_BASE}/interview-prep`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume_text: resumeText, job_description: jobDescription }),
    });
    if (!res.ok) throw await _parseError(res);
    return res.json();
  },

  /* ── Export ──────────────────────────── */
  async exportResume(data, format) {
    const res = await fetch(`${API_BASE}/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...data, format }),
    });
    if (!res.ok) throw await _parseError(res);
    const blob = await res.blob();
    const cd = res.headers.get('Content-Disposition') || '';
    const match = cd.match(/filename="(.+)"/);
    const filename = match ? match[1] : `resume.${format}`;
    _downloadBlob(blob, filename);
  },
};

/* ── Helpers ─────────────────────────────── */
async function _parseError(res) {
  try {
    const data = await res.json();
    return new Error(data.detail || 'Unknown error');
  } catch {
    return new Error(`HTTP ${res.status}: ${res.statusText}`);
  }
}

function _downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

/* ── Session store — persist resume text across pages ── */
const Session = {
  set(key, val) { sessionStorage.setItem(`cc_${key}`, JSON.stringify(val)); },
  get(key)      { try { return JSON.parse(sessionStorage.getItem(`cc_${key}`)); } catch { return null; } },
  clear(key)    { sessionStorage.removeItem(`cc_${key}`); },
};

/* ── UI Utilities ────────────────────────── */
function showLoader(msg = 'Analyzing with AI...') {
  const ol = document.getElementById('loadingOverlay');
  if (ol) {
    ol.querySelector('.loading-text').textContent = msg;
    ol.classList.add('active');
  }
}
function hideLoader() {
  const ol = document.getElementById('loadingOverlay');
  if (ol) ol.classList.remove('active');
}
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  const colors = { success:'#10b981', error:'#ef4444', warning:'#f59e0b', info:'#3b82f6' };
  toast.style.cssText = `
    position:fixed; bottom:24px; right:24px; z-index:9999;
    background:#0d1530; border:1px solid ${colors[type] || colors.info};
    color:#f0f4ff; padding:14px 20px; border-radius:12px;
    font-family:Inter,sans-serif; font-size:0.9rem; max-width:360px;
    box-shadow:0 8px 32px rgba(0,0,0,0.4);
    animation:fadeInUp 0.3s ease;
  `;
  toast.innerHTML = `<span style="color:${colors[type]};margin-right:8px;">${{success:'✓',error:'✗',warning:'⚠',info:'ℹ'}[type]}</span>${message}`;
  document.body.appendChild(toast);
  setTimeout(() => { toast.style.opacity='0'; toast.style.transition='opacity 0.4s'; setTimeout(()=>toast.remove(), 400); }, 3500);
}

function scoreColor(score) {
  if (score >= 80) return '#10b981';
  if (score >= 60) return '#f59e0b';
  if (score >= 40) return '#3b82f6';
  return '#ef4444';
}
function matchLevelBadge(level) {
  const map = { 'Excellent':'badge-green','Strong':'badge-cyan','Good':'badge-blue','Fair':'badge-orange','Poor':'badge-red' };
  return map[level] || 'badge-blue';
}
