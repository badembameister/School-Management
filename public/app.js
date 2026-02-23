/* ── School Management System — Frontend ── */

const $ = s => document.querySelector(s);
const page = () => $('#page');
const API = '/api';
let modal, currentPage = 'dashboard';

// Cache for dropdowns
let teachersCache = [], classesCache = [], coursesCache = [], studentsCache = [], parentsCache = [];

async function api(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}

function toast(msg, type = 'success') {
  const t = $('#toast');
  t.className = `toast align-items-center text-bg-${type} border-0`;
  $('#toastMsg').textContent = msg;
  bootstrap.Toast.getOrCreateInstance(t).show();
}

function showModal(title, bodyHtml, onSave) {
  $('#modalTitle').textContent = title;
  $('#modalBody').innerHTML = bodyHtml;
  const saveBtn = $('#modalSave');
  const newBtn = saveBtn.cloneNode(true);
  saveBtn.replaceWith(newBtn);
  newBtn.id = 'modalSave';
  newBtn.addEventListener('click', async () => {
    try { await onSave(); modal.hide(); } catch (e) { toast(e.message, 'danger'); }
  });
  modal.show();
}

function field(id, label, type = 'text', value = '', extra = '') {
  return `<div class="mb-3"><label class="form-label fw-semibold">${label}</label><input class="form-control" id="${id}" type="${type}" value="${value}" ${extra}></div>`;
}

function selectField(id, label, options, selected = '') {
  const opts = options.map(o => `<option value="${o.value}" ${o.value == selected ? 'selected' : ''}>${o.label}</option>`).join('');
  return `<div class="mb-3"><label class="form-label fw-semibold">${label}</label><select class="form-select" id="${id}"><option value="">— Select —</option>${opts}</select></div>`;
}

function val(id) { return document.getElementById(id)?.value?.trim() || ''; }
function valInt(id) { const v = val(id); return v ? parseInt(v) : null; }

async function loadCaches() {
  [teachersCache, classesCache, coursesCache, studentsCache, parentsCache] = await Promise.all([
    api('/teachers'), api('/classes'), api('/courses'), api('/students'), api('/parents')
  ]);
}

function teacherOpts() { return teachersCache.map(t => ({ value: t.id, label: `${t.first_name} ${t.last_name}` })); }
function classOpts() { return classesCache.map(c => ({ value: c.id, label: c.name })); }
function courseOpts() { return coursesCache.map(c => ({ value: c.id, label: `${c.code} — ${c.name}` })); }
function studentOpts() { return studentsCache.map(s => ({ value: s.id, label: `${s.first_name} ${s.last_name}` })); }
function parentOpts() { return parentsCache.map(p => ({ value: p.id, label: `${p.first_name} ${p.last_name}` })); }

// ── Navigation ───────────────────────────────────────

document.querySelectorAll('[data-page]').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    document.querySelectorAll('[data-page]').forEach(l => l.classList.remove('active'));
    link.classList.add('active');
    currentPage = link.dataset.page;
    navigate(currentPage);
    if (window.innerWidth < 768) $('#sidebar').classList.remove('show');
  });
});

async function navigate(pg) {
  await loadCaches();
  const pages = { dashboard: renderDashboard, students: renderStudents, teachers: renderTeachers, courses: renderCourses, classes: renderClasses, parents: renderParents, enrollments: renderEnrollments, attendance: renderAttendance, schedules: renderSchedules };
  if (pages[pg]) pages[pg]();
}

// ── Dashboard ────────────────────────────────────────

async function renderDashboard() {
  const s = await api('/dashboard');
  const cards = [
    { label: 'Students', val: s.students, icon: 'bi-people-fill', bg: '#4361ee' },
    { label: 'Teachers', val: s.teachers, icon: 'bi-person-badge-fill', bg: '#7209b7' },
    { label: 'Courses', val: s.courses, icon: 'bi-book-fill', bg: '#f72585' },
    { label: 'Classes', val: s.classes, icon: 'bi-building-fill', bg: '#4cc9f0' },
    { label: 'Parents', val: s.parents, icon: 'bi-person-hearts', bg: '#4895ef' },
    { label: 'Enrollments', val: s.enrollments, icon: 'bi-journal-check', bg: '#560bad' },
  ];
  page().innerHTML = `<h4 class="section-title">Dashboard</h4><div class="row g-3">${cards.map(c => `
    <div class="col-sm-6 col-lg-4 col-xl-3"><div class="card stat-card p-3"><div class="d-flex align-items-center gap-3">
      <div class="icon text-white" style="background:${c.bg}"><i class="bi ${c.icon}"></i></div>
      <div><div class="text-muted small">${c.label}</div><div class="fw-bold fs-4">${c.val}</div></div>
    </div></div></div>`).join('')}</div>`;
}

// ── Generic CRUD table ────────────────────────────────

function crudTable(title, columns, rows, { onAdd, onEdit, onDelete, extra = '' } = {}) {
  const ths = columns.map(c => `<th>${c.label}</th>`).join('') + '<th>Actions</th>';
  const trs = rows.map(r => {
    const tds = columns.map(c => `<td>${c.render ? c.render(r) : (r[c.key] ?? '')}</td>`).join('');
    return `<tr>${tds}<td class="text-nowrap">
      ${onEdit ? `<button class="btn btn-sm btn-outline-primary me-1" onclick="window._edit(${r.id})"><i class="bi bi-pencil"></i></button>` : ''}
      ${onDelete ? `<button class="btn btn-sm btn-outline-danger" onclick="window._del(${r.id})"><i class="bi bi-trash"></i></button>` : ''}
    </td></tr>`;
  }).join('') || `<tr><td colspan="${columns.length + 1}" class="text-center text-muted py-4">No records found</td></tr>`;
  return `<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="section-title mb-0">${title}</h4>
    <div>${extra}${onAdd ? `<button class="btn btn-primary" onclick="window._add()"><i class="bi bi-plus-lg me-1"></i>Add</button>` : ''}</div>
  </div>
  <div class="card border-0 shadow-sm"><div class="table-responsive"><table class="table table-hover mb-0"><thead><tr>${ths}</tr></thead><tbody>${trs}</tbody></table></div></div>`;
}

// ── Students ─────────────────────────────────────────

async function renderStudents() {
  const data = studentsCache;
  const cols = [
    { key: 'id', label: 'ID' },
    { label: 'Name', render: r => `${r.first_name} ${r.last_name}` },
    { key: 'date_of_birth', label: 'DOB' },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Phone' },
    { key: 'class_name', label: 'Class' },
  ];
  page().innerHTML = crudTable('Students', cols, data, { onAdd: true, onEdit: true, onDelete: true });
  window._add = () => showModal('Add Student',
    field('fn','First Name') + field('ln','Last Name') + field('dob','Date of Birth','date') + field('em','Email','email') + field('ph','Phone') + selectField('cls','Class',classOpts()),
    async () => { await api('/students', { method: 'POST', body: { first_name: val('fn'), last_name: val('ln'), date_of_birth: val('dob'), email: val('em'), phone: val('ph'), class_id: valInt('cls') } }); toast('Student added'); navigate('students'); }
  );
  window._edit = id => { const r = data.find(x => x.id === id); showModal('Edit Student',
    field('fn','First Name','text',r.first_name) + field('ln','Last Name','text',r.last_name) + field('dob','Date of Birth','date',r.date_of_birth||'') + field('em','Email','email',r.email||'') + field('ph','Phone','text',r.phone||'') + selectField('cls','Class',classOpts(),r.class_id||''),
    async () => { await api(`/students/${id}`, { method: 'PUT', body: { first_name: val('fn'), last_name: val('ln'), date_of_birth: val('dob'), email: val('em'), phone: val('ph'), class_id: valInt('cls') } }); toast('Student updated'); navigate('students'); }
  ); };
  window._del = async id => { if (confirm('Delete this student?')) { await api(`/students/${id}`, { method: 'DELETE' }); toast('Student deleted'); navigate('students'); } };
}

// ── Teachers ─────────────────────────────────────────

async function renderTeachers() {
  const data = teachersCache;
  const cols = [
    { key: 'id', label: 'ID' },
    { label: 'Name', render: r => `${r.first_name} ${r.last_name}` },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Phone' },
    { key: 'subject_specialty', label: 'Specialty' },
  ];
  page().innerHTML = crudTable('Teachers', cols, data, { onAdd: true, onEdit: true, onDelete: true });
  window._add = () => showModal('Add Teacher',
    field('fn','First Name') + field('ln','Last Name') + field('em','Email','email') + field('ph','Phone') + field('sp','Specialty'),
    async () => { await api('/teachers', { method: 'POST', body: { first_name: val('fn'), last_name: val('ln'), email: val('em'), phone: val('ph'), subject_specialty: val('sp') } }); toast('Teacher added'); navigate('teachers'); }
  );
  window._edit = id => { const r = data.find(x => x.id === id); showModal('Edit Teacher',
    field('fn','First Name','text',r.first_name) + field('ln','Last Name','text',r.last_name) + field('em','Email','email',r.email||'') + field('ph','Phone','text',r.phone||'') + field('sp','Specialty','text',r.subject_specialty||''),
    async () => { await api(`/teachers/${id}`, { method: 'PUT', body: { first_name: val('fn'), last_name: val('ln'), email: val('em'), phone: val('ph'), subject_specialty: val('sp') } }); toast('Teacher updated'); navigate('teachers'); }
  ); };
  window._del = async id => { if (confirm('Delete this teacher?')) { await api(`/teachers/${id}`, { method: 'DELETE' }); toast('Teacher deleted'); navigate('teachers'); } };
}

// ── Courses ──────────────────────────────────────────

async function renderCourses() {
  const data = coursesCache;
  const cols = [
    { key: 'id', label: 'ID' },
    { key: 'code', label: 'Code' },
    { key: 'name', label: 'Name' },
    { key: 'teacher_name', label: 'Teacher', render: r => r.teacher_name || '<span class="text-muted">Unassigned</span>' },
    { key: 'max_capacity', label: 'Capacity' },
    { key: 'description', label: 'Description' },
  ];
  page().innerHTML = crudTable('Courses', cols, data, { onAdd: true, onEdit: true, onDelete: true });
  window._add = () => showModal('Add Course',
    field('nm','Course Name') + field('cd','Code') + field('ds','Description') + selectField('ti','Teacher',teacherOpts()) + field('cap','Max Capacity','number','30'),
    async () => { await api('/courses', { method: 'POST', body: { name: val('nm'), code: val('cd'), description: val('ds'), teacher_id: valInt('ti'), max_capacity: valInt('cap') || 30 } }); toast('Course added'); navigate('courses'); }
  );
  window._edit = id => { const r = data.find(x => x.id === id); showModal('Edit Course',
    field('nm','Course Name','text',r.name) + field('cd','Code','text',r.code) + field('ds','Description','text',r.description||'') + selectField('ti','Teacher',teacherOpts(),r.teacher_id||'') + field('cap','Max Capacity','number',r.max_capacity||30),
    async () => { await api(`/courses/${id}`, { method: 'PUT', body: { name: val('nm'), code: val('cd'), description: val('ds'), teacher_id: valInt('ti'), max_capacity: valInt('cap') || 30 } }); toast('Course updated'); navigate('courses'); }
  ); };
  window._del = async id => { if (confirm('Delete this course?')) { await api(`/courses/${id}`, { method: 'DELETE' }); toast('Course deleted'); navigate('courses'); } };
}

// ── Classes ──────────────────────────────────────────

async function renderClasses() {
  const data = classesCache;
  const cols = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'grade_level', label: 'Level' },
    { key: 'section', label: 'Section' },
    { key: 'academic_year', label: 'Year' },
    { key: 'teacher_name', label: 'Homeroom Teacher', render: r => r.teacher_name || '<span class="text-muted">Unassigned</span>' },
  ];
  page().innerHTML = crudTable('Classes', cols, data, { onAdd: true, onEdit: true, onDelete: true });
  window._add = () => showModal('Add Class',
    field('nm','Class Name') + field('gl','Grade Level') + field('sc','Section') + field('yr','Academic Year') + selectField('ti','Homeroom Teacher',teacherOpts()),
    async () => { await api('/classes', { method: 'POST', body: { name: val('nm'), grade_level: val('gl'), section: val('sc'), academic_year: val('yr'), homeroom_teacher_id: valInt('ti') } }); toast('Class added'); navigate('classes'); }
  );
  window._edit = id => { const r = data.find(x => x.id === id); showModal('Edit Class',
    field('nm','Class Name','text',r.name) + field('gl','Grade Level','text',r.grade_level) + field('sc','Section','text',r.section||'') + field('yr','Academic Year','text',r.academic_year||'') + selectField('ti','Homeroom Teacher',teacherOpts(),r.homeroom_teacher_id||''),
    async () => { await api(`/classes/${id}`, { method: 'PUT', body: { name: val('nm'), grade_level: val('gl'), section: val('sc'), academic_year: val('yr'), homeroom_teacher_id: valInt('ti') } }); toast('Class updated'); navigate('classes'); }
  ); };
  window._del = async id => { if (confirm('Delete this class?')) { await api(`/classes/${id}`, { method: 'DELETE' }); toast('Class deleted'); navigate('classes'); } };
}

// ── Parents ──────────────────────────────────────────

async function renderParents() {
  const data = parentsCache;
  const cols = [
    { key: 'id', label: 'ID' },
    { label: 'Name', render: r => `${r.first_name} ${r.last_name}` },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Phone' },
    { key: 'address', label: 'Address' },
  ];
  const extra = `<button class="btn btn-outline-primary me-2" onclick="window._linkForm()"><i class="bi bi-link-45deg me-1"></i>Link to Student</button>`;
  page().innerHTML = crudTable('Parents', cols, data, { onAdd: true, onEdit: true, onDelete: true, extra });
  window._add = () => showModal('Add Parent',
    field('fn','First Name') + field('ln','Last Name') + field('em','Email','email') + field('ph','Phone') + field('ad','Address'),
    async () => { await api('/parents', { method: 'POST', body: { first_name: val('fn'), last_name: val('ln'), email: val('em'), phone: val('ph'), address: val('ad') } }); toast('Parent added'); navigate('parents'); }
  );
  window._edit = id => { const r = data.find(x => x.id === id); showModal('Edit Parent',
    field('fn','First Name','text',r.first_name) + field('ln','Last Name','text',r.last_name) + field('em','Email','email',r.email||'') + field('ph','Phone','text',r.phone||'') + field('ad','Address','text',r.address||''),
    async () => { await api(`/parents/${id}`, { method: 'PUT', body: { first_name: val('fn'), last_name: val('ln'), email: val('em'), phone: val('ph'), address: val('ad') } }); toast('Parent updated'); navigate('parents'); }
  ); };
  window._del = async id => { if (confirm('Delete this parent?')) { await api(`/parents/${id}`, { method: 'DELETE' }); toast('Parent deleted'); navigate('parents'); } };
  window._linkForm = () => showModal('Link Parent to Student',
    selectField('pid','Parent',parentOpts()) + selectField('sid','Student',studentOpts()) +
    `<div class="mb-3"><label class="form-label fw-semibold">Relationship</label><select class="form-select" id="rel"><option>Parent</option><option>Guardian</option><option>Other</option></select></div>`,
    async () => { await api('/parents/link', { method: 'POST', body: { parent_id: valInt('pid'), student_id: valInt('sid'), relationship: val('rel') } }); toast('Linked'); }
  );
}

// ── Enrollments & Grades ─────────────────────────────

async function renderEnrollments() {
  const data = await api('/enrollments');
  const cols = [
    { key: 'enrollment_id', label: 'ID' },
    { key: 'student_name', label: 'Student' },
    { key: 'course_code', label: 'Course Code' },
    { key: 'course_name', label: 'Course' },
    { label: 'Score', render: r => r.score != null ? r.score.toFixed(1) : '<span class="text-muted">—</span>' },
    { key: 'letter_grade', label: 'Grade', render: r => r.letter_grade || '<span class="text-muted">—</span>' },
  ];
  const extra = `<button class="btn btn-outline-success me-2" onclick="window._gradeForm()"><i class="bi bi-award me-1"></i>Grade</button>`;
  page().innerHTML = crudTable('Enrollments & Grades', cols, data.map(r => ({ ...r, id: r.enrollment_id })), { onAdd: true, onDelete: true, extra });
  window._add = () => showModal('Enroll Student',
    selectField('sid','Student',studentOpts()) + selectField('cid','Course',courseOpts()),
    async () => { await api('/enrollments', { method: 'POST', body: { student_id: valInt('sid'), course_id: valInt('cid') } }); toast('Enrolled'); navigate('enrollments'); }
  );
  window._del = async id => { if (confirm('Remove this enrollment?')) { await api(`/enrollments/${id}`, { method: 'DELETE' }); toast('Unenrolled'); navigate('enrollments'); } };
  window._gradeForm = () => {
    const enrollOpts = data.map(e => ({ value: e.enrollment_id, label: `#${e.enrollment_id} — ${e.student_name} / ${e.course_code}` }));
    showModal('Assign Grade',
      selectField('eid','Enrollment',enrollOpts) + field('score','Score (0-100)','number') + field('rem','Remarks'),
      async () => { await api('/grades', { method: 'POST', body: { enrollment_id: valInt('eid'), score: val('score'), remarks: val('rem') } }); toast('Grade assigned'); navigate('enrollments'); }
    );
  };
}

// ── Attendance ───────────────────────────────────────

async function renderAttendance() {
  page().innerHTML = `
    <h4 class="section-title">Attendance</h4>
    <div class="row g-3 mb-4">
      <div class="col-md-6"><div class="card border-0 shadow-sm p-3">
        <h6 class="fw-bold mb-3"><i class="bi bi-people me-2"></i>Mark Class Attendance</h6>
        <div class="mb-2">${selectField('att_cls','Class',classOpts())}</div>
        ${field('att_date','Date','date',new Date().toISOString().split('T')[0])}
        <button class="btn btn-primary" onclick="window._loadClassAtt()">Load Students</button>
        <div id="attList" class="mt-3"></div>
      </div></div>
      <div class="col-md-6"><div class="card border-0 shadow-sm p-3">
        <h6 class="fw-bold mb-3"><i class="bi bi-person me-2"></i>View Student Attendance</h6>
        <div class="mb-2">${selectField('att_stu','Student',studentOpts())}</div>
        <button class="btn btn-primary" onclick="window._viewStuAtt()">View</button>
        <div id="stuAttResult" class="mt-3"></div>
      </div></div>
    </div>`;

  window._loadClassAtt = async () => {
    const classId = val('att_cls'), date = val('att_date');
    if (!classId || !date) { toast('Select class and date', 'warning'); return; }
    const data = await api(`/attendance?class_id=${classId}&date=${date}`);
    if (!data.length) { $('#attList').innerHTML = '<p class="text-muted">No students in this class.</p>'; return; }
    const rows = data.map(r => `<tr>
      <td>${r.name}</td>
      <td><select class="form-select form-select-sm att-status" data-sid="${r.student_id}">
        <option value="Present" ${r.status==='Present'?'selected':''}>Present</option>
        <option value="Absent" ${r.status==='Absent'?'selected':''}>Absent</option>
        <option value="Late" ${r.status==='Late'?'selected':''}>Late</option>
        <option value="Excused" ${r.status==='Excused'?'selected':''}>Excused</option>
      </select></td></tr>`).join('');
    $('#attList').innerHTML = `<table class="table table-sm"><thead><tr><th>Student</th><th>Status</th></tr></thead><tbody>${rows}</tbody></table>
      <button class="btn btn-success" onclick="window._saveClassAtt()"><i class="bi bi-check-lg me-1"></i>Save All</button>`;
  };

  window._saveClassAtt = async () => {
    const date = val('att_date');
    const records = [...document.querySelectorAll('.att-status')].map(el => ({
      student_id: parseInt(el.dataset.sid), status: el.value
    }));
    await api('/attendance/bulk', { method: 'POST', body: { date, records } });
    toast(`Attendance saved for ${records.length} students`);
  };

  window._viewStuAtt = async () => {
    const sid = val('att_stu');
    if (!sid) { toast('Select a student', 'warning'); return; }
    const data = await api(`/attendance?student_id=${sid}`);
    if (!data.records?.length) { $('#stuAttResult').innerHTML = '<p class="text-muted">No records.</p>'; return; }
    const s = data.stats;
    const rows = data.records.map(r => `<tr><td>${r.date}</td><td><span class="badge badge-${r.status.toLowerCase()}">${r.status}</span></td><td>${r.remarks||''}</td></tr>`).join('');
    $('#stuAttResult').innerHTML = `
      <div class="d-flex gap-3 mb-2 flex-wrap">
        <span class="badge bg-secondary">Total: ${s.total}</span><span class="badge bg-success">Present: ${s.present}</span>
        <span class="badge bg-danger">Absent: ${s.absent}</span><span class="badge bg-warning text-dark">Late: ${s.late}</span>
        <span class="badge bg-info">Rate: ${s.rate}%</span>
      </div>
      <table class="table table-sm"><thead><tr><th>Date</th><th>Status</th><th>Remarks</th></tr></thead><tbody>${rows}</tbody></table>`;
  };
}

// ── Schedules ────────────────────────────────────────

async function renderSchedules() {
  page().innerHTML = `
    <h4 class="section-title">Class Schedules</h4>
    <div class="row g-3 mb-4">
      <div class="col-md-8"><div class="card border-0 shadow-sm p-3">
        <div class="d-flex gap-2 align-items-end mb-3">
          <div class="flex-grow-1">${selectField('sch_cls','View Schedule for Class',classOpts())}</div>
          <button class="btn btn-primary mb-3" onclick="window._loadSchedule()">Load</button>
          <button class="btn btn-success mb-3" onclick="window._addSlot()"><i class="bi bi-plus-lg"></i> Add Slot</button>
        </div>
        <div id="schTable"></div>
      </div></div>
      <div class="col-md-4"><div class="card border-0 shadow-sm p-3">
        <h6 class="fw-bold mb-3"><i class="bi bi-person me-2"></i>Student Schedule</h6>
        ${selectField('sch_stu','Student',studentOpts())}
        <button class="btn btn-primary" onclick="window._viewStuSch()">View</button>
        <div id="stuSchResult" class="mt-3"></div>
      </div></div>
    </div>`;

  const days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
  const dayOpts = days.map(d => ({ value: d, label: d }));

  window._loadSchedule = async () => {
    const cid = val('sch_cls');
    if (!cid) return;
    const data = await api(`/schedules?class_id=${cid}`);
    if (!data.length) { $('#schTable').innerHTML = '<p class="text-muted">No schedule.</p>'; return; }
    let currentDay = '';
    const rows = data.map(r => {
      const dayCell = r.day_of_week !== currentDay ? `<td class="fw-bold" rowspan="1">${r.day_of_week}</td>` : '<td></td>';
      currentDay = r.day_of_week;
      return `<tr>${dayCell}<td>${r.start_time} - ${r.end_time}</td><td>${r.course_name} (${r.course_code})</td><td>${r.teacher_name||''}</td><td>${r.room||''}</td>
        <td><button class="btn btn-sm btn-outline-danger" onclick="window._delSlot(${r.id})"><i class="bi bi-trash"></i></button></td></tr>`;
    }).join('');
    $('#schTable').innerHTML = `<table class="table table-sm table-hover"><thead><tr><th>Day</th><th>Time</th><th>Course</th><th>Teacher</th><th>Room</th><th></th></tr></thead><tbody>${rows}</tbody></table>`;
  };

  window._addSlot = () => {
    showModal('Add Schedule Slot',
      selectField('sl_cls','Class',classOpts()) + selectField('sl_crs','Course',courseOpts()) + selectField('sl_day','Day',dayOpts) + field('sl_st','Start Time','time') + field('sl_et','End Time','time') + field('sl_rm','Room'),
      async () => { await api('/schedules', { method: 'POST', body: { class_id: valInt('sl_cls'), course_id: valInt('sl_crs'), day_of_week: val('sl_day'), start_time: val('sl_st'), end_time: val('sl_et'), room: val('sl_rm') } }); toast('Slot added'); window._loadSchedule(); }
    );
  };

  window._delSlot = async id => { if (confirm('Delete this slot?')) { await api(`/schedules/${id}`, { method: 'DELETE' }); toast('Slot deleted'); window._loadSchedule(); } };

  window._viewStuSch = async () => {
    const sid = val('sch_stu');
    if (!sid) return;
    const data = await api(`/schedules?student_id=${sid}`);
    if (!data.length) { $('#stuSchResult').innerHTML = '<p class="text-muted">No schedule (student may not be in a class).</p>'; return; }
    const rows = data.map(r => `<tr><td class="fw-semibold">${r.day_of_week}</td><td>${r.start_time}-${r.end_time}</td><td>${r.course_code}</td><td>${r.room||''}</td></tr>`).join('');
    $('#stuSchResult').innerHTML = `<table class="table table-sm"><thead><tr><th>Day</th><th>Time</th><th>Course</th><th>Room</th></tr></thead><tbody>${rows}</tbody></table>`;
  };
}

// ── Init ─────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  modal = new bootstrap.Modal($('#formModal'));
  navigate('dashboard');
});
