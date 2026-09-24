import { createStory, getMyDashboard, getProfile, submitContact } from './api.js';
import { logout, requireRole } from './auth.js';
const state = { data: null };
function el(t, c, x) { const n = document.createElement(t); if (c) n.className = c; if (x !== undefined) n.textContent = x; return n; }
function toast(m) { const t = document.querySelector('[data-toast]'); if (!t) return; t.hidden = false; t.textContent = m; clearTimeout(t._h); t._h = setTimeout(() => { t.hidden = true; }, 3000); }
function switchView(n) { document.querySelectorAll('[data-dash-nav] [data-view]').forEach((b) => b.classList.toggle('active', b.dataset.view === n)); document.querySelectorAll('[data-view-panel]').forEach((p) => p.classList.toggle('active', p.dataset.viewPanel === n)); document.getElementById('dash-title').textContent = n[0].toUpperCase() + n.slice(1); }
function card(title, sub, body) { const c = el('div', 'card'); c.style.padding = '1rem'; c.append(el('strong', '', title)); if (sub) c.append(el('p', '', sub)); if (body) c.append(el('p', '', body)); return c; }
function render(d) {
  const g = document.getElementById('user-stats'); g.innerHTML = '';
  [['Projects live', d.total_projects, 'community led'], ['Stories shared', d.total_stories, 'from the field'], ['My messages', d.my_messages.length, 'sent by you']].forEach(([h, n, s], i) => { const k = el('div', i === 0 ? 'stat accent' : 'stat'); k.append(el('h3', '', h), el('div', 'num', String(n)), el('div', 'sub', s)); g.appendChild(k); });
  const lp = document.getElementById('latest-projects'); lp.innerHTML = '';
  if (!d.latest_projects.length) lp.appendChild(el('p', 'empty', 'No projects yet.'));
  d.latest_projects.slice(0, 3).forEach((p) => lp.appendChild(card(p.name, p.category + ' - ' + p.summary, '')));
  const pl = document.getElementById('projects-list'); pl.innerHTML = '';
  if (!d.latest_projects.length) pl.appendChild(el('p', 'empty', 'No projects yet.'));
  d.latest_projects.forEach((p) => pl.appendChild(card(p.name, p.category, p.summary)));
  document.getElementById('projects-count').textContent = d.latest_projects.length + ' projects';
  const sl = document.getElementById('stories-list'); sl.innerHTML = '';
  if (!d.latest_stories.length) sl.appendChild(el('p', 'empty', 'No stories yet. Be the first to share one.'));
  d.latest_stories.forEach((s) => sl.appendChild(card(s.title, s.category + ' - ' + s.year, s.excerpt)));
  document.getElementById('stories-count').textContent = d.latest_stories.length + ' stories';
  const ml = document.getElementById('messages-list'); ml.innerHTML = '';
  if (!d.my_messages.length) ml.appendChild(el('p', 'empty', 'You have not sent any messages yet.'));
  d.my_messages.forEach((m) => ml.appendChild(card(m.name, m.created_at ? new Date(m.created_at).toLocaleString() : '', m.message)));
}
async function init() {
  let user = null;
  try { const p = await getProfile(); user = p?.user ?? null; } catch { user = null; }
  if (!user) { window.location.href = '/login.html'; return; }
  if (user.role === 'admin') { window.location.href = '/admin.html'; return; }
  requireRole([], '/login.html');
  document.getElementById('user-name').textContent = user.username;
  document.getElementById('user-email').textContent = user.email || '';
  document.getElementById('user-role').textContent = (user.role || 'viewer').toUpperCase();
  document.getElementById('user-hello').textContent = 'Hi, ' + user.username;
  document.getElementById('user-avatar').textContent = (user.username || 'M')[0].toUpperCase();
  document.querySelectorAll('[data-dash-nav] [data-view]').forEach((b) => b.addEventListener('click', () => switchView(b.dataset.view)));
  document.querySelectorAll('[data-goto]').forEach((b) => b.addEventListener('click', () => switchView(b.dataset.goto)));
  document.querySelector('[data-logout]').addEventListener('click', () => logout());
  const q = document.querySelector('[data-dash-search]');
  if (q) q.addEventListener('input', (e) => { const v = e.target.value.toLowerCase(); document.querySelectorAll('#projects-list .card, #stories-list .card').forEach((c) => { c.style.display = c.textContent.toLowerCase().includes(v) ? '' : 'none'; }); });
  document.querySelector('[data-new-story]').addEventListener('click', () => document.querySelector('[data-modal]').classList.add('open'));
  document.querySelector('[data-modal-close]').addEventListener('click', () => document.querySelector('[data-modal]').classList.remove('open'));
  document.querySelector('[data-story-form]').addEventListener('submit', async (e) => { e.preventDefault(); const fd = new FormData(e.currentTarget); const st = document.querySelector('[data-story-status]'); try { st.textContent = 'Publishing...'; await createStory(fd.get('title'), fd.get('category'), fd.get('excerpt'), Number(fd.get('year'))); st.textContent = 'Published.'; e.currentTarget.reset(); document.querySelector('[data-modal]').classList.remove('open'); toast('Story published'); await load(); } catch (err) { st.textContent = err.message || 'Could not publish.'; } });
  document.querySelector('[data-quick-contact]').addEventListener('submit', async (e) => { e.preventDefault(); const fd = new FormData(e.currentTarget); const st = document.querySelector('[data-quick-status]'); try { st.textContent = 'Sending...'; await submitContact(fd.get('name'), fd.get('email'), fd.get('message')); st.textContent = 'Sent. Thank you.'; e.currentTarget.reset(); toast('Message sent'); await load(); } catch (err) { st.textContent = err.message || 'Could not send.'; } });
  async function load() { const d = await getMyDashboard(); state.data = d; render(d); }
  try { await load(); } catch (err) { toast(err.message || 'Dashboard failed to load'); }
}
init();
