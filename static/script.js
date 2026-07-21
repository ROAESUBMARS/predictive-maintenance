// ── Toast Notification System ────────────────────────────────────────────────
function showToast(message, type = 'info', duration = 4000) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:999999;display:flex;flex-direction:column;gap:10px;max-width:380px;';
        document.body.appendChild(container);
    }
    const icons = { info: 'fa-circle-info', success: 'fa-circle-check', warning: 'fa-triangle-exclamation', error: 'fa-circle-xmark' };
    const colors = { info: '#58a6ff', success: '#3fb950', warning: '#f5a623', error: '#f85149' };
    const toast = document.createElement('div');
    toast.style.cssText = `background:rgba(22,27,34,0.97);border:1px solid ${colors[type]};border-left:4px solid ${colors[type]};border-radius:10px;padding:14px 18px;display:flex;align-items:flex-start;gap:12px;box-shadow:0 8px 32px rgba(0,0,0,0.5);backdrop-filter:blur(12px);opacity:0;transform:translateX(30px);transition:all 0.3s ease;pointer-events:auto;`;
    toast.innerHTML = `<i class="fa-solid ${icons[type]}" style="color:${colors[type]};margin-top:2px;flex-shrink:0;"></i><span style="color:#e6edf3;font-size:13px;line-height:1.5;font-family:'Inter',sans-serif;">${message}</span><button onclick="this.parentElement.remove()" style="background:none;border:none;color:#8b949e;cursor:pointer;font-size:16px;margin-left:auto;padding:0;line-height:1;flex-shrink:0;">×</button>`;
    container.appendChild(toast);
    requestAnimationFrame(() => { toast.style.opacity = '1'; toast.style.transform = 'translateX(0)'; });
    setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateX(30px)'; setTimeout(() => toast.remove(), 300); }, duration);
}
// ─────────────────────────────────────────────────────────────────────────────

function getApiUrl(endpoint) {
    const input = document.getElementById('api-url');
    let base = input ? input.value.trim() : '';
    if (!base) {
        base = window.location.origin;
    }
    base = base.replace(/\/+$/, '');
    return base + endpoint;
}

async function authFetch(url, options = {}) {
    options.headers = options.headers || {};
    const token = sessionStorage.getItem('auth_token') || '';
    if (token) {
        options.headers['Authorization'] = 'Bearer ' + token;
        options.headers['X-Admin-Key'] = token;
    }
    const response = await fetch(url, options);
    if (response.status === 401) {
        showToast("Session expired or unauthorized. Please log in again.", 'error', 5000);
        logout();
        throw new Error("Unauthorized");
    }
    return response;
}

const PUMPS = [
  {id:'HP-01', name:'Pump Unit 1', location:'Deck A - Port', status:'red',    fault:'Overheating Detected',      severity:'Critical', temp:96,  pressure:104, vib:0.031, oil:55, time:'12 min ago'},
  {id:'HP-02', name:'Pump Unit 2', location:'Deck A - Starboard', status:'green', fault:'Normal',        severity:'Normal',   temp:74,  pressure:101, vib:0.024, oil:68, time:'2 min ago'},
  {id:'HP-03', name:'Pump Unit 3', location:'Engine Room', status:'yellow', fault:'High Vibration',      severity:'Medium',   temp:79,  pressure:99,  vib:0.041, oil:60, time:'34 min ago'},
  {id:'HP-04', name:'Pump Unit 4', location:'Cargo Bay', status:'green',  fault:'Normal',                severity:'Normal',   temp:76,  pressure:103, vib:0.022, oil:71, time:'8 min ago'},
  {id:'HP-05', name:'Pump Unit 5', location:'Deck B', status:'yellow',    fault:'Low Oil Level',          severity:'Medium',   temp:81,  pressure:96,  vib:0.030, oil:27, time:'19 min ago'},
  {id:'HP-06', name:'Pump Unit 6', location:'Aux Room', status:'green',   fault:'Normal',                 severity:'Normal',   temp:73,  pressure:105, vib:0.021, oil:74, time:'5 min ago'},
  {id:'HP-07', name:'Pump Unit 7', location:'Deck A - Port', status:'red', fault:'Pressure Failure',      severity:'High',     temp:72,  pressure:61,  vib:0.027, oil:58, time:'3 min ago'},
  {id:'HP-08', name:'Pump Unit 8', location:'Engine Room', status:'green', fault:'Normal',                severity:'Normal',   temp:75,  pressure:102, vib:0.025, oil:69, time:'1 min ago'},
  {id:'HP-09', name:'Pump Unit 9', location:'Cargo Bay', status:'green',  fault:'Normal',                 severity:'Normal',   temp:77,  pressure:100, vib:0.023, oil:65, time:'6 min ago'},
  {id:'HP-10', name:'Pump Unit 10', location:'Deck B', status:'green',    fault:'Normal',                  severity:'Normal',   temp:74,  pressure:104, vib:0.020, oil:72, time:'4 min ago'},
  {id:'HP-11', name:'Pump Unit 11', location:'Aux Room', status:'yellow', fault:'Coolant Leak',            severity:'High',     temp:74,  pressure:103, vib:0.021, oil:63, time:'27 min ago'},
  {id:'HP-12', name:'Pump Unit 12', location:'Deck A - Starboard', status:'green', fault:'Normal',         severity:'Normal',   temp:76,  pressure:99,  vib:0.026, oil:70, time:'9 min ago'},
];

const PRESETS = {
    normal: { temp: 70, pres: 100, vib: 0.020, flow: 300, oil: 60, rpm: 1500, leak: 0 },
    overheating: { temp: 95, pres: 120, vib: 0.020, flow: 300, oil: 60, rpm: 1500, leak: 0 },
    high_vibration: { temp: 70, pres: 100, vib: 0.055, flow: 300, oil: 60, rpm: 1500, leak: 0 },
    pressure_failure: { temp: 70, pres: 68, vib: 0.020, flow: 300, oil: 60, rpm: 1500, leak: 0 },
    low_oil: { temp: 70, pres: 100, vib: 0.020, flow: 300, oil: 18, rpm: 1500, leak: 0 },
    coolant_leak: { temp: 70, pres: 100, vib: 0.020, flow: 300, oil: 60, rpm: 1500, leak: 1 }
};

let telemetryChart;
let weibullChart;
let probabilityChart;
let contributionsChart;
let chartData = {
    labels: [],
    datasets: [
        { label: 'Vibration (g)', borderColor: '#f0883e', backgroundColor: 'rgba(240, 136, 62, 0.2)', borderWidth: 2.5, pointRadius: 3, pointBackgroundColor: '#f0883e', fill: false, data: [], tension: 0.4, yAxisID: 'yVib' },
        { label: 'Flow Rate (lpm)', borderColor: '#58a6ff', backgroundColor: 'rgba(88, 166, 255, 0.2)', borderWidth: 2.5, pointRadius: 3, pointBackgroundColor: '#58a6ff', fill: false, data: [], tension: 0.4, yAxisID: 'yFlow' },
        { label: 'Oil Level (%)', borderColor: '#3fb950', backgroundColor: 'rgba(63, 185, 80, 0.2)', borderWidth: 2.5, pointRadius: 3, pointBackgroundColor: '#3fb950', fill: false, data: [], tension: 0.4, yAxisID: 'yOil' }
    ]
};
const MAX_DATA_POINTS = 20;

let liveTelemetryInterval = null;
let currentDiagnosis = null;
let chatMessages = [];
let currentRole = null;
let pendingRole = null;

let workOrders = [
    {
        id: 'WO-8992',
        fault: 'Bearing Replacement',
        assignee: 'Tech: Mike Ross',
        priority: 'High',
        status: 'In Progress',
        time: 'Day 2 (14 hrs)',
        unlocked: false,
        diagnosis: {
            fault_name: 'Bearing Replacement',
            primary_actions: [
                'Shut down pump and lock out power.',
                'Disassemble pump coupling and bearings casing.',
                'Inspect bearings for pitting, scoring, or thermal discoloration.',
                'Replace damaged bearings and pack with fresh grease.',
                'Reassemble bearing housing and check shaft alignment.'
            ],
            spare_parts: ['Replacement roller bearings', 'Bearing seal kit', 'Lithium grease']
        }
    }
];
let currentTechName = '';
let activeTechWO = null;
let activeSimulationAnomaly = null;

// Initial Setup on load
document.addEventListener('DOMContentLoaded', () => {
    initSharedElements();
    attachEventListeners();
    updateRawDataTable();

    // Restore saved theme configuration
    const savedTheme = localStorage.getItem('nmu_active_theme');
    if (savedTheme) {
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) themeSelect.value = savedTheme;
        applyTheme(savedTheme);
    }

    // Restore saved role session
    const savedRole = localStorage.getItem('nmu_active_role');
    const savedEmail = localStorage.getItem('nmu_login_email');
    if (savedRole) {
        if (savedEmail) {
            const loginEmail = document.getElementById('login-email');
            if (loginEmail) loginEmail.value = savedEmail;
        }
        enterApp(savedRole);
    }
});

// App Entry & Exit Router
function enterApp(role) {
    currentRole = role;
    
    // Save authentication details in localStorage
    localStorage.setItem('nmu_active_role', role);
    const loginEmailInput = document.getElementById('login-email');
    let loggedInEmail = loginEmailInput ? loginEmailInput.value.trim() : '';
    if (!loggedInEmail) {
        loggedInEmail = localStorage.getItem('nmu_login_email') || '';
    }
    if (loggedInEmail) {
        localStorage.setItem('nmu_login_email', loggedInEmail);
        const alertEmailInput = document.getElementById('alert-email-input');
        if (alertEmailInput) {
            alertEmailInput.value = loggedInEmail;
        }
    }
    
    // Hide login, show app
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('app').style.display = 'flex';
    
    // Configure badge details
    const badge = document.getElementById('role-badge');
    const roleData = {
        tech: { label: '🔧 Maintenance Technician', cls: 'tech' },
        eng:  { label: '⚙️ Maintenance Engineer', cls: 'eng' },
        rel:  { label: '📊 Reliability Engineer', cls: 'rel' }
    }[role];
    badge.className = 'role-badge ' + roleData.cls;
    badge.textContent = roleData.label;

    // Toggle Shell Views
    document.getElementById('view-technician').style.display = 'none';
    document.getElementById('view-engineer').style.display = 'none';
    document.getElementById('view-reliability').style.display = 'none';

    const sidebar = document.getElementById('app-sidebar');
    const contentHeader = document.getElementById('content-header');
    const toggleBtn = document.getElementById('toggle-sidebar-btn');

    // Reset collapsed state on role switch
    sidebar.classList.remove('collapsed');
    const toggleIcon = document.querySelector('#toggle-sidebar-btn i');
    if (toggleIcon) toggleIcon.className = 'fa-solid fa-sliders';

    if (role === 'tech') {
        sidebar.style.display = 'block';
        contentHeader.style.display = 'flex';
        if (toggleBtn) toggleBtn.style.display = 'block';
        document.getElementById('view-technician').style.display = 'block';
        
        // Identify active tech profile from login email
        const email = document.getElementById('login-email').value.trim();
        const techMap = {
            'sarah@nmu.edu.ng': 'Sarah Jenkins',
            'mike@nmu.edu.ng': 'Mike Ross',
            'david@nmu.edu.ng': 'David Chen'
        };
        currentTechName = techMap[email] || 'Sarah Jenkins';
        
        document.getElementById('tech-assigned-name').innerHTML = `<i class="fa-solid fa-user"></i> Tech: ${currentTechName}`;
        document.getElementById('tech-welcome-title').textContent = `Welcome, ${currentTechName.split(' ')[0]}`;
        
        renderTechRoster();
        renderTechWorkOrders();
    } else if (role === 'eng') {
        sidebar.style.display = 'block';
        contentHeader.style.display = 'flex';
        if (toggleBtn) toggleBtn.style.display = 'block';
        document.getElementById('view-engineer').style.display = 'block';
        renderEngineerWorkOrdersTable();
        
        if (typeof window.triggerEngWelcomeAnimation === 'function') {
            window.triggerEngWelcomeAnimation();
        }
    } else if (role === 'rel') {
        sidebar.style.display = 'none';
        contentHeader.style.display = 'none';
        if (toggleBtn) toggleBtn.style.display = 'none';
        document.getElementById('view-reliability').style.display = 'block';
        // Delay chart instantiation to guarantee DOM rendering
        setTimeout(initReliabilityCharts, 100);
    }
}

function logout() {
    // Clear intervals
    if (liveTelemetryInterval) {
        clearInterval(liveTelemetryInterval);
        document.getElementById('live-telemetry-toggle').checked = false;
    }
    
    // Clear saved session details
    localStorage.removeItem('nmu_active_role');
    localStorage.removeItem('nmu_login_email');
    sessionStorage.removeItem('auth_token');
    
    document.getElementById('login-screen').style.display = 'flex';
    document.getElementById('app').style.display = 'none';
    currentRole = null;
}

// Chart Initializations
function initSharedElements() {
    // 1. Telemetry Chart (Engineer View)
    const ctx = document.getElementById('telemetryChart').getContext('2d');
    const now = new Date();
    for(let i=MAX_DATA_POINTS; i>0; i--) {
        const t = new Date(now.getTime() - i * 1000);
        chartData.labels.push(t.toLocaleTimeString([], {hour12: false, second: '2-digit'}));
        chartData.datasets[0].data.push(0.020);
        chartData.datasets[1].data.push(300);
        chartData.datasets[2].data.push(60);
    }
    telemetryChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#8b949e' } } },
            scales: {
                x: { ticks: { color: '#8b949e' }, grid: { color: '#21262d' } },
                yVib: {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Vibration (g)', color: '#f0883e' },
                    ticks: { color: '#f0883e' },
                    grid: { color: '#21262d' },
                    suggestedMin: 0.010,
                    suggestedMax: 0.060
                },
                yFlow: {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: 'Flow Rate (lpm)', color: '#58a6ff' },
                    ticks: { color: '#58a6ff' },
                    grid: { drawOnChartArea: false },
                    suggestedMin: 200,
                    suggestedMax: 400
                },
                yOil: {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: 'Oil Level (%)', color: '#3fb950' },
                    ticks: { color: '#3fb950' },
                    grid: { drawOnChartArea: false },
                    suggestedMin: 0,
                    suggestedMax: 100
                }
            },
            animation: { duration: 0 }
        }
    });

    // Populate Reliability Fleet Map Elements
    const mapContainer = document.getElementById('fleet-map');
    mapContainer.innerHTML = '';
    let normalCount = 0, warningCount = 0, criticalCount = 0;

    PUMPS.forEach(p => {
        if (p.status === 'green') normalCount++;
        else if (p.status === 'yellow') warningCount++;
        else if (p.status === 'red') criticalCount++;

        const div = document.createElement('div');
        div.className = `fleet-tile ${p.status}`;
        div.onclick = () => showToast(`<strong>${p.name}</strong> — ${p.fault} <span style="opacity:0.7">(${p.severity})</span>`, p.status === 'red' ? 'error' : p.status === 'yellow' ? 'warning' : 'success');
        div.innerHTML = `
            <div>${p.status==='red'?'🔴':p.status==='yellow'?'🟡':'🟢'}</div>
            <div class="fl-id">${p.id}</div>
        `;
        mapContainer.appendChild(div);
    });

    document.getElementById('fleet-normal-count').textContent = normalCount;
    document.getElementById('fleet-warning-count').textContent = warningCount;
    document.getElementById('fleet-critical-count').textContent = criticalCount;

    // 2. Probability Chart (Fault Prediction Analysis Panel)
    const probCtx = document.getElementById('probabilityChart').getContext('2d');
    probabilityChart = new Chart(probCtx, {
        type: 'bar',
        data: {
            labels: ['Normal', 'Overheating', 'Vibration', 'Pressure Fail', 'Low Oil', 'Coolant Leak'],
            datasets: [{
                label: 'Probability',
                data: [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                backgroundColor: 'rgba(88, 166, 255, 0.6)',
                borderColor: '#58a6ff',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { min: 0, max: 1, ticks: { color: '#8b949e' }, grid: { color: '#21262d' } },
                y: { ticks: { color: '#8b949e' }, grid: { color: '#21262d' } }
            }
        }
    });

    // 3. Contributions Chart (Fault Prediction Analysis Panel)
    const contrCtx = document.getElementById('contributionsChart').getContext('2d');
    contributionsChart = new Chart(contrCtx, {
        type: 'bar',
        data: {
            labels: ['Temp', 'Pressure', 'Vibration', 'Flow Rate', 'Oil Level', 'RPM', 'Coolant Leak'],
            datasets: [{
                label: 'Deviation (Z-score)',
                data: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                backgroundColor: 'rgba(212, 160, 23, 0.6)',
                borderColor: '#d4a017',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { min: 0, ticks: { color: '#8b949e' }, grid: { color: '#21262d' } },
                y: { ticks: { color: '#8b949e' }, grid: { color: '#21262d' } }
            }
        }
    });
}

function initReliabilityCharts() {
    if (weibullChart) weibullChart.destroy();
    
    const wCtx = document.getElementById('weibullChart').getContext('2d');
    weibullChart = new Chart(wCtx, {
        type: 'bar',
        data: {
            labels: ['0-50','50-100','100-150','150-200','200-250','250-300','300+'],
            datasets: [{
                label: 'Failure count by pump age (cycles)',
                data: [2, 5, 9, 14, 8, 4, 1],
                backgroundColor: '#58a6ff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#8b949e' } } },
            scales: {
                x: { ticks: { color: '#8b949e' }, grid: { color: '#21262d' } },
                y: { ticks: { color: '#8b949e' }, grid: { color: '#21262d' } }
            }
        }
    });
}

function attachEventListeners() {
    // Sensor sliders
    const inputs = ['temp', 'pres', 'vib', 'flow', 'oil', 'rpm'];
    inputs.forEach(id => {
        const slider = document.getElementById(`${id}-slider`);
        const valSpan = document.getElementById(`${id}-val`);
        slider.addEventListener('input', (e) => {
            valSpan.textContent = e.target.value;
            updateRawDataTable();
        });
    });

    // Preset scenarios selector
    document.getElementById('preset-select').addEventListener('change', (e) => {
        const preset = PRESETS[e.target.value];
        if (preset) {
            setSliderValue('temp', preset.temp);
            setSliderValue('pres', preset.pres);
            setSliderValue('vib', preset.vib);
            setSliderValue('flow', preset.flow);
            setSliderValue('oil', preset.oil);
            setSliderValue('rpm', preset.rpm);
            document.getElementById('leak-select').value = preset.leak;
            updateRawDataTable();
            
            // Sync active simulation anomaly tracking
            activeSimulationAnomaly = (e.target.value === 'nominal' || e.target.value === 'normal') ? null : e.target.value;
        }
    });

    document.getElementById('leak-select').addEventListener('change', updateRawDataTable);

    document.getElementById('run-diagnostic-btn').addEventListener('click', () => runDiagnostic());

    const liveToggle = document.getElementById('live-telemetry-toggle');
    if (liveToggle) {
        liveToggle.addEventListener('change', (e) => {
            if (liveTelemetryInterval) clearInterval(liveTelemetryInterval);
            if (e.target.checked) {
                simulateLiveTelemetry(); // Trigger immediate first telemetry tick instantly
                liveTelemetryInterval = setInterval(simulateLiveTelemetry, 2000);
                showToast('<i class="fa-solid fa-satellite-dish"></i> Live Telemetry Streaming Active', 'success', 2500);
            } else {
                showToast('Live Telemetry Paused', 'warning', 2000);
            }
        });
    }

    // Make the Live Telemetry Stream card clickable to instantly toggle telemetry
    const chartCard = document.querySelector('.chart-card');
    if (chartCard) {
        chartCard.title = 'Click to toggle Live Telemetry Stream';
        chartCard.addEventListener('click', (e) => {
            if (e.target.closest('.live-toggle') || e.target.id === 'live-telemetry-toggle') return;
            if (liveToggle) {
                liveToggle.checked = !liveToggle.checked;
                liveToggle.dispatchEvent(new Event('change'));
            }
        });
    }

    document.getElementById('send-chat-btn').addEventListener('click', sendChatMessage);
    document.getElementById('chat-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });

    // Generate Work Order
    document.getElementById('generate-wo-btn').addEventListener('click', () => {
        const assignee = document.getElementById('wo-assignee').value;
        const priority = document.getElementById('wo-priority').value;
        const hours = document.getElementById('wo-est-hours').value || 0;
        const days = document.getElementById('wo-est-days').value || 0;
        
        if (!currentDiagnosis) {
            showToast('Please run a diagnostic first to determine the fault.', 'warning');
            return;
        }

        const faultName = currentDiagnosis.fault_code === 0 ? "General Inspection" : currentDiagnosis.fault_name;
        const woNumber = 'WO-' + Math.floor(1000 + Math.random() * 9000);
        
        let timeStr = '';
        if (days > 0) timeStr += `Day ${days} `;
        if (hours > 0) timeStr += `(${hours} hrs)`;
        if (!timeStr) timeStr = 'Not started';

        // Add to global workOrders database
        workOrders.push({
            id: woNumber,
            fault: faultName,
            assignee: assignee,
            priority: priority,
            status: 'New',
            time: timeStr,
            unlocked: false,
            diagnosis: {
                fault_name: faultName,
                primary_actions: currentDiagnosis.primary_actions || ['Inspect pump components.', 'Clear active fault alerts.'],
                spare_parts: currentDiagnosis.spare_parts || []
            }
        });

        // Reset inputs
        document.getElementById('wo-est-hours').value = '';
        document.getElementById('wo-est-days').value = '';
        
        renderEngineerWorkOrdersTable();
        showToast(`Work Order <strong>${woNumber}</strong> generated and assigned to ${assignee.replace('Tech: ', '')}.`, 'success');
    });

    // Tech verification handlers
    document.getElementById('tech-open-qr-btn').addEventListener('click', () => {
        document.getElementById('tech-qr-modal').style.display = 'flex';
    });

    document.getElementById('tech-simulate-scan-btn').addEventListener('click', () => {
        document.getElementById('tech-qr-modal').style.display = 'none';
        if (activeTechWO) {
            activeTechWO.unlocked = true;
            if (activeTechWO.status === 'New') {
                activeTechWO.status = 'In Progress';
            }
            selectTechWorkOrder(activeTechWO);
            showToast(`Asset Verified. Work Order <strong>${activeTechWO.id}</strong> unlocked.`, 'success');
        }
    });

    document.getElementById('tech-complete-wo-btn').addEventListener('click', () => {
        if (activeTechWO) {
            activeTechWO.status = 'Completed';
            activeSimulationAnomaly = null; // Restore system to nominal on complete
            const presetSelect = document.getElementById('preset-select');
            if (presetSelect) {
                presetSelect.value = 'normal';
                presetSelect.dispatchEvent(new Event('change'));
            }
            
            if (typeof window.triggerFulfillmentAnimation === 'function') {
                window.triggerFulfillmentAnimation();
            } else {
                showToast(`Work Order <strong>${activeTechWO.id}</strong> completed. Pump returning to nominal baseline.`, 'success', 5000);
            }
            renderTechWorkOrders();
        }
    });

    // Login Form Submit Handler
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value.trim();
        const role = pendingRole;

        const btn = e.target.querySelector('button[type="submit"]');
        const origText = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Authenticating...';

        try {
            const response = await fetch(getApiUrl('/api/login'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, role })
            });
            const result = await response.json();
            
            if (!response.ok) {
                showToast(result.error || 'Authentication failed.', 'error');
                return;
            }

            sessionStorage.setItem('auth_token', result.token);
            document.getElementById('login-modal').style.display = 'none';
            document.getElementById('login-password').value = '';
            enterApp(role);
        } catch (err) {
            console.error(err);
            showToast('Error communicating with authentication server.', 'error');
        } finally {
            btn.innerHTML = origText;
        }
    });

    document.getElementById('close-login-modal-btn').addEventListener('click', () => {
        document.getElementById('login-modal').style.display = 'none';
        document.getElementById('login-password').value = '';
        pendingRole = null;
    });

    document.getElementById('theme-select').addEventListener('change', (e) => {
        applyTheme(e.target.value);
    });

    document.getElementById('toggle-sidebar-btn').addEventListener('click', () => {
        const sidebar = document.getElementById('app-sidebar');
        sidebar.classList.toggle('collapsed');
        const icon = document.querySelector('#toggle-sidebar-btn i');
        if (icon) {
            if (sidebar.classList.contains('collapsed')) {
                icon.className = 'fa-solid fa-angles-right';
                document.getElementById('toggle-sidebar-btn').title = "Expand Sensors Panel";
            } else {
                icon.className = 'fa-solid fa-sliders';
                document.getElementById('toggle-sidebar-btn').title = "Collapse Sensors Panel";
            }
        }
    });
}

function openLoginModal(role) {
    pendingRole = role;
    const emailMap = {
        tech: 'tech@nmu.edu.ng',
        eng: 'eng@nmu.edu.ng',
        rel: 'rel@nmu.edu.ng'
    };
    const titleMap = {
        tech: '🔧 Technician Authentication',
        eng: '⚙️ Engineer Authentication',
        rel: '📊 Reliability Authentication'
    };
    document.getElementById('login-email').value = emailMap[role];
    document.getElementById('login-modal-title').textContent = titleMap[role];
    document.getElementById('login-modal').style.display = 'flex';
    document.getElementById('login-password').focus();
}

function applyTheme(theme) {
    localStorage.setItem('nmu_active_theme', theme);
    document.body.classList.remove('theme-light', 'theme-high-contrast');
    if (theme === 'light') {
        document.body.classList.add('theme-light');
    } else if (theme === 'high-contrast') {
        document.body.classList.add('theme-high-contrast');
    }

    const tickColor = theme === 'light' ? '#24292f' : (theme === 'high-contrast' ? '#ffff00' : '#8b949e');
    const gridColor = theme === 'light' ? '#d0d7de' : (theme === 'high-contrast' ? '#ffffff' : '#21262d');

    const charts = [telemetryChart, probabilityChart, contributionsChart, weibullChart];
    charts.forEach(chart => {
        if (chart) {
            if (chart.options.scales && chart.options.scales.x) {
                chart.options.scales.x.ticks.color = tickColor;
                chart.options.scales.x.grid.color = gridColor;
            }
            if (chart.options.scales && chart.options.scales.y) {
                chart.options.scales.y.ticks.color = tickColor;
                chart.options.scales.y.grid.color = gridColor;
            }
            if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
                chart.options.plugins.legend.labels.color = tickColor;
            }
            chart.update();
        }
    });

    // Update named axes on the telemetry chart (yVib, yFlow, yOil)
    if (telemetryChart && telemetryChart.options.scales) {
        ['yVib', 'yFlow', 'yOil'].forEach(axisId => {
            const axis = telemetryChart.options.scales[axisId];
            if (axis) {
                if (axis.ticks) axis.ticks.color = tickColor;
                if (axis.grid) axis.grid.color = gridColor;
                if (axis.title) axis.title.color = tickColor;
            }
        });
        telemetryChart.update();
    }
}

function renderTechRoster() {
    const rosterList = document.getElementById('tech-roster-list');
    if (!rosterList) return;
    rosterList.innerHTML = '';
    
    const techs = [
        { name: 'Sarah Jenkins', email: 'sarah@nmu.edu.ng' },
        { name: 'Mike Ross', email: 'mike@nmu.edu.ng' },
        { name: 'David Chen', email: 'david@nmu.edu.ng' }
    ];
    
    techs.forEach(t => {
        const btn = document.createElement('button');
        btn.className = `primary-btn`;
        btn.style.width = '100%';
        btn.style.textAlign = 'left';
        btn.style.padding = '10px 14px';
        btn.style.fontSize = '12px';
        btn.style.margin = '4px 0';
        
        if (t.name === currentTechName) {
            btn.style.background = 'var(--accent)';
            btn.style.color = '#000000';
            btn.style.fontWeight = '700';
            btn.style.border = '1px solid var(--accent)';
        } else {
            btn.style.background = 'rgba(255,255,255,0.05)';
            btn.style.color = 'var(--text-primary)';
            btn.style.border = '1px solid var(--card-border)';
        }
        
        btn.innerHTML = `<i class="fa-solid fa-user-gear"></i> ${t.name}`;
        btn.addEventListener('click', () => {
            switchTechnicianProfile(t.name);
        });
        rosterList.appendChild(btn);
    });
}

function switchTechnicianProfile(name) {
    currentTechName = name;
    
    // Sync current technician email to session memory
    const emailMap = {
        'Sarah Jenkins': 'sarah@nmu.edu.ng',
        'Mike Ross': 'mike@nmu.edu.ng',
        'David Chen': 'david@nmu.edu.ng'
    };
    const email = emailMap[name] || 'sarah@nmu.edu.ng';
    const loginEmailInput = document.getElementById('login-email');
    if (loginEmailInput) loginEmailInput.value = email;
    localStorage.setItem('nmu_login_email', email);
    
    document.getElementById('tech-assigned-name').innerHTML = `<i class="fa-solid fa-user"></i> Tech: ${currentTechName}`;
    document.getElementById('tech-welcome-title').textContent = `Welcome, ${currentTechName.split(' ')[0]}`;
    renderTechRoster();
    renderTechWorkOrders();
}

function renderEngineerWorkOrdersTable() {
    const tbody = document.getElementById('active-wo-table');
    if (!tbody) return;
    tbody.innerHTML = '';
    workOrders.forEach(wo => {
        const tr = document.createElement('tr');
        let statusBadge = '';
        if (wo.status === 'New') {
            statusBadge = `<span class="badge" style="background:rgba(88,166,255,0.15); color:var(--accent);">New</span>`;
        } else if (wo.status === 'In Progress') {
            statusBadge = `<span class="badge" style="background:rgba(245,158,11,0.2); color:var(--warning);">In Progress</span>`;
        } else {
            statusBadge = `<span class="badge" style="background:rgba(63,185,80,0.2); color:var(--success);">Completed</span>`;
        }
        tr.innerHTML = `
            <td>${wo.id}</td>
            <td>${wo.fault}</td>
            <td>${wo.assignee.replace('Tech: ', '')}</td>
            <td>${statusBadge}</td>
            <td style="text-align:right;">${wo.time}</td>
        `;
        tbody.appendChild(tr);
    });
}

function renderTechWorkOrders() {
    const container = document.getElementById('tech-wo-selector-container');
    const list = document.getElementById('tech-wo-list');
    const activeContainer = document.getElementById('tech-active-wo-container');
    const noWoState = document.getElementById('tech-no-wo-state');
    
    if (!list) return;
    list.innerHTML = '';
    
    // Filter active work orders for this tech
    const activeWO = workOrders.filter(w => w.assignee.includes(currentTechName) && w.status !== 'Completed');
    
    if (activeWO.length === 0) {
        container.style.display = 'none';
        activeContainer.style.display = 'none';
        noWoState.style.display = 'block';
        activeTechWO = null;
    } else {
        noWoState.style.display = 'none';
        container.style.display = 'block';
        
        activeWO.forEach(wo => {
            const card = document.createElement('div');
            card.className = `glass-card`;
            card.style.cursor = 'pointer';
            card.style.padding = '12px 18px';
            card.style.minWidth = '140px';
            card.style.border = activeTechWO && activeTechWO.id === wo.id ? '2px solid var(--accent)' : '1px solid var(--card-border)';
            card.innerHTML = `
                <div style="font-weight: 700; font-size: 14px;">${wo.id}</div>
                <div style="font-size: 11px; color: var(--text-secondary); margin: 4px 0;">${wo.fault}</div>
                <span class="badge" style="font-size: 10px; background: rgba(255,255,255,0.05);">${wo.priority}</span>
            `;
            card.addEventListener('click', () => {
                selectTechWorkOrder(wo);
                renderTechWorkOrders();
            });
            list.appendChild(card);
        });

        const stillExists = activeWO.some(w => activeTechWO && w.id === activeTechWO.id);
        if (!stillExists) {
            selectTechWorkOrder(activeWO[0]);
        } else {
            selectTechWorkOrder(activeTechWO);
        }
    }
}

function selectTechWorkOrder(wo) {
    activeTechWO = wo;
    document.getElementById('tech-active-wo-container').style.display = 'block';
    
    if (!wo.unlocked) {
        document.getElementById('tech-locked-state').style.display = 'block';
        document.getElementById('tech-locked-wo-id').textContent = wo.id;
        document.getElementById('tech-unlocked-state').style.display = 'none';
    } else {
        document.getElementById('tech-locked-state').style.display = 'none';
        document.getElementById('tech-unlocked-state').style.display = 'block';
        
        // Populate checklist & parts
        document.getElementById('tech-wo-title').textContent = `${wo.id}: ${wo.fault}`;
        
        let desc = 'No diagnostic details provided.';
        if (wo.diagnosis && wo.diagnosis.fault_name) {
            desc = `High probability of <strong>${wo.diagnosis.fault_name}</strong> detected on HP-01. Follow standard operating procedures below to resolve.`;
        }
        document.getElementById('tech-wo-desc').innerHTML = desc;
        
        // Checklist
        const taskList = document.getElementById('tech-task-list');
        taskList.innerHTML = '';
        const actions = (wo.diagnosis && wo.diagnosis.primary_actions) ? wo.diagnosis.primary_actions : ['Inspect pump.', 'Verify clearance.'];
        actions.forEach((act, i) => {
            const row = document.createElement('div');
            row.className = 'task-row';
            row.style.display = 'flex';
            row.style.gap = '10px';
            row.style.marginBottom = '8px';
            row.innerHTML = `
                <input type="checkbox" id="task-${i}">
                <label for="task-${i}" style="font-size: 13px; cursor: pointer;">${act}</label>
            `;
            taskList.appendChild(row);
        });

        // Parts
        const partsList = document.getElementById('tech-parts-list');
        partsList.innerHTML = '';
        const parts = (wo.diagnosis && wo.diagnosis.spare_parts) ? wo.diagnosis.spare_parts : [];
        if (parts.length === 0) {
            partsList.innerHTML = '<p style="color:var(--text-secondary); font-size:12px;">No specific spare parts required.</p>';
        } else {
            parts.forEach(part => {
                const badge = document.createElement('span');
                badge.className = 'badge';
                badge.style.margin = '4px';
                badge.style.background = 'rgba(255,255,255,0.05)';
                badge.style.border = '1px solid var(--card-border)';
                badge.style.padding = '6px 12px';
                badge.textContent = part;
                partsList.appendChild(badge);
            });
        }
    }
}

function setSliderValue(id, value) {
    const slider = document.getElementById(`${id}-slider`);
    slider.value = value;
    document.getElementById(`${id}-val`).textContent = value;
}

function getSensorData() {
    return {
        Temperature_C: parseFloat(document.getElementById('temp-slider').value),
        Pressure_psi: parseFloat(document.getElementById('pres-slider').value),
        Vibration_g: parseFloat(document.getElementById('vib-slider').value),
        Flow_Rate_lpm: parseFloat(document.getElementById('flow-slider').value),
        Oil_Level_pct: parseFloat(document.getElementById('oil-slider').value),
        RPM: parseFloat(document.getElementById('rpm-slider').value),
        Coolant_Leak: parseInt(document.getElementById('leak-select').value),
        Operating_Hours: 240.0
    };
}

function updateRawDataTable() {
    const data = getSensorData();
    const tbody = document.getElementById('raw-data-table');
    tbody.innerHTML = '';
    for (const [key, value] of Object.entries(data)) {
        if (key === 'Operating_Hours') continue;
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${key.replace(/_/g, ' ')}</td><td>${value}</td>`;
        tbody.appendChild(tr);
    }
}

async function runDiagnostic(silent = false) {
    const data = getSensorData();
    
    // Add alert recipient configurations from UI
    const emailInput = document.getElementById('alert-email-input');
    const phoneInput = document.getElementById('alert-phone-input');
    if (emailInput) data.alert_email = emailInput.value.trim();
    if (phoneInput) data.alert_phone = phoneInput.value.trim();

    const btn = document.getElementById('run-diagnostic-btn');
    if (!silent) {
        btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Analyzing...';
    }
    
    if (!silent && typeof window.triggerDiagnosticAnimation === 'function') {
        window.triggerDiagnosticAnimation();
    }
    
    const startTime = Date.now();
    
    try {
        const response = await authFetch(getApiUrl('/predict'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        if (result.error) {
            console.error(result.error);
            if (!silent) showToast('Error running diagnostic. Check API connection.', 'error');
            return;
        }

        currentDiagnosis = result.ai_recommendation;
        currentDiagnosis.fault_code = result.fault_code; 
        currentDiagnosis.recommendation = result.recommendation;
        currentDiagnosis.severity = result.severity;

        // Fetch maintenance schedule details
        let schedResult = null;
        try {
            const schedResponse = await authFetch(getApiUrl('/schedule'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    fault_code: result.fault_code,
                    confidence: result.probabilities ? result.probabilities[result.fault_code] : 0.87,
                    operating_hours: data.Operating_Hours || 100.0
                })
            });
            schedResult = await schedResponse.json();
        } catch (schedErr) {
            console.error("Scheduler Error:", schedErr);
        }
        
        // Enforce minimum 4-second diagnostic display (manual runs only)
        if (!silent) {
            const elapsed = Date.now() - startTime;
            const remaining = 4000 - elapsed;
            if (remaining > 0) {
                await new Promise(resolve => setTimeout(resolve, remaining));
            }
        }

        updateDashboard(result, schedResult);
        updateChartPoint(data.Vibration_g, data.Flow_Rate_lpm, data.Oil_Level_pct);

    } catch (err) {
        console.error(err);
    } finally {
        if (!silent) {
            btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Run Diagnostic';
            if (typeof window.stopDiagnosticAnimation === 'function') {
                window.stopDiagnosticAnimation();
            }
        }
    }
}

function updateDashboard(result, schedResult) {
    const ai = result.ai_recommendation;
    const isOptimal = result.fault_code === 0;

    // Topbar Backend Info
    document.getElementById('backend-mode').textContent = result.mode === 'ml_model' ? 'ML MODEL' : 'RULE-BASED';
    document.getElementById('confidence-val').textContent = (ai.confidence * 100).toFixed(1) + '%';

    // ENGINEER VIEW KPIs
    document.getElementById('kpi-health').textContent = isOptimal ? '100/100' : (ai.risk_level === 'High' ? '45/100' : '65/100');
    const kpiStatus = document.getElementById('kpi-status');
    kpiStatus.textContent = isOptimal ? 'Optimal' : result.fault;
    kpiStatus.className = 'kpi-value ' + (isOptimal ? 'status-optimal' : (result.severity === 'critical' ? 'status-critical' : 'status-warning'));
    document.getElementById('kpi-savings').textContent = isOptimal ? '$14.2k' : '$0.0k';

    // ENGINEER VIEW Diagnostic Box
    const panel = document.getElementById('diagnostic-content');
    if (isOptimal) {
        panel.className = 'status-box optimal';
        panel.innerHTML = `
            <h4><i class="fa-solid fa-circle-check"></i> System is operating nominally.</h4>
            <p>${result.recommendation}</p>
        `;
    } else {
        panel.className = `status-box ${result.severity === 'critical' ? 'critical' : 'warning'}`;
        const actions = ai.primary_actions.map(a => `<li>${a}</li>`).join('');
        panel.innerHTML = `
            <h4><i class="fa-solid fa-triangle-exclamation"></i> FAULT DETECTED: ${ai.fault_name}</h4>
            <p>${result.recommendation}</p>
            <div class="diag-details">
                <strong>Severity:</strong> ${result.severity.toUpperCase()} <br/>
                <strong>Urgency:</strong> ${ai.urgency_level} <br/>
                <strong>Primary Actions:</strong>
                <ul>${actions}</ul>
            </div>
        `;
    }

    // Render technician details too
    renderTechnicianView(ai, isOptimal);

    // Render maintenance scheduler widget in both Engineer and Reliability views
    renderSchedulerView(schedResult);
    renderReliabilitySchedulerView(schedResult);

    // Update Prediction Analysis Charts
    if (result.probabilities && probabilityChart) {
        probabilityChart.data.datasets[0].data = result.probabilities;
        probabilityChart.update();
    }

    if (result.feature_contributions && contributionsChart) {
        const fc = result.feature_contributions;
        contributionsChart.data.datasets[0].data = [
            fc.Temperature_C || 0,
            fc.Pressure_psi || 0,
            fc.Vibration_g || 0,
            fc.Flow_Rate_lpm || 0,
            fc.Oil_Level_pct || 0,
            fc.RPM || 0,
            fc.Coolant_Leak || 0
        ];
        contributionsChart.update();
    }

    // Update HP-01 fleet map tile to reflect latest diagnostic result
    const hp01 = PUMPS.find(p => p.id === 'HP-01');
    if (hp01) {
        hp01.fault = result.fault;
        hp01.severity = result.severity === 'ok' ? 'Normal' : result.severity.charAt(0).toUpperCase() + result.severity.slice(1);
        hp01.status = result.fault_code === 0 ? 'green' : (result.severity === 'critical' ? 'red' : 'yellow');
        hp01.time = 'just now';
        renderFleetMap();
    }

    // Sync live telemetry to 3D Digital Twin model
    if (typeof update3DModelTelemetry === 'function') {
        const sensorData = getSensorData();
        update3DModelTelemetry(sensorData.Temperature_C, sensorData.Vibration_g, result.fault_code);
    }
}

function renderSchedulerView(sched) {
    const panel = document.getElementById('scheduler-content');
    if (!panel) return;

    if (!sched) {
        panel.className = 'status-box optimal';
        panel.innerHTML = `<p style="color:var(--text-secondary); font-size:13px; margin:0;">Run diagnostic to generate maintenance schedule.</p>`;
        return;
    }

    const costUSD = sched.estimated_cost;
    const costNGN = costUSD * 1600;
    const costStr = `₦${costNGN.toLocaleString()} ($${costUSD})`;

    let severityClass = 'optimal';
    if (sched.severity === 'critical') severityClass = 'critical';
    else if (sched.severity === 'high') severityClass = 'warning';
    else if (sched.severity === 'medium') severityClass = 'warning';

    panel.className = `status-box ${severityClass}`;

    const tasksHTML = sched.tasks.map(t => `<li><i class="fa-solid fa-check" style="color:var(--success); font-size:11px; margin-right:6px;"></i>${t}</li>`).join('');
    const partsHTML = sched.spare_parts.length > 0 
        ? sched.spare_parts.map(p => `<span class="badge" style="margin:2px 4px 2px 0; background:rgba(255,255,255,0.05); border:1px solid var(--card-border); font-size:11px;">${p}</span>`).join('')
        : '<span style="color:var(--text-secondary); font-size:12px;">No parts required.</span>';
    const toolsHTML = sched.tools_needed.length > 0 
        ? sched.tools_needed.map(t => `<span class="badge" style="margin:2px 4px 2px 0; background:rgba(255,255,255,0.05); border:1px solid var(--card-border); font-size:11px;">${t}</span>`).join('')
        : '<span style="color:var(--text-secondary); font-size:12px;">No specific tools.</span>';
    const staffHTML = sched.required_staff.map(s => `<li><i class="fa-solid fa-user-gear" style="color:var(--accent); font-size:11px; margin-right:6px;"></i>${s}</li>`).join('');

    panel.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
            <div>
                <h4 style="font-size:16px; margin:0; font-weight:700;"><i class="fa-solid fa-business-time"></i> AI-Optimized Action Plan</h4>
                <p style="font-size:12px; color:var(--text-secondary); margin-top:2px;">${sched.description}</p>
            </div>
            <span class="badge" style="background:rgba(248,81,73,0.15); color:var(--danger); border:1px solid var(--danger); font-size:11px;">Priority ${sched.priority}/10</span>
        </div>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:12px; margin-bottom:16px; background:rgba(255,255,255,0.02); padding:12px; border-radius:8px; border: 1px solid var(--card-border);">
            <div style="text-align:center;">
                <div style="font-size:10px; color:var(--text-secondary); text-transform:uppercase;">Scheduled Date</div>
                <div style="font-size:14px; font-weight:700; color:var(--accent); margin-top:4px;">${sched.next_scheduled_date}</div>
                <div style="font-size:10px; color:var(--text-secondary);">(${sched.days_until_maintenance} days)</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:10px; color:var(--text-secondary); text-transform:uppercase;">Est. Cost</div>
                <div style="font-size:14px; font-weight:700; color:var(--success); margin-top:4px;">${costStr}</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:10px; color:var(--text-secondary); text-transform:uppercase;">Est. Duration</div>
                <div style="font-size:14px; font-weight:700; color:var(--text-primary); margin-top:4px;">${sched.estimated_duration_hours} hrs</div>
            </div>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px;">
            <div>
                <strong style="font-size:12px; color:var(--text-secondary); display:block; margin-bottom:6px;">Staff Required:</strong>
                <ul style="list-style:none; padding:0; font-size:12px; line-height:1.6;">${staffHTML}</ul>
            </div>
            <div>
                <strong style="font-size:12px; color:var(--text-secondary); display:block; margin-bottom:6px;">Recommended Action:</strong>
                <p style="font-size:12.5px; font-weight:600; color:var(--accent); margin:0;">${sched.recommended_action}</p>
            </div>
        </div>

        <div style="margin-bottom:16px;">
            <strong style="font-size:12px; color:var(--text-secondary); display:block; margin-bottom:4px;">Tasks Checklist:</strong>
            <ul style="list-style:none; padding:0; font-size:12px; line-height:1.6;">${tasksHTML}</ul>
        </div>

        <div style="margin-bottom:16px; display:flex; flex-direction:column; gap:6px;">
            <div>
                <strong style="font-size:12px; color:var(--text-secondary); margin-right:8px;">Parts Required:</strong>
                <div style="display:inline-block;">${partsHTML}</div>
            </div>
            <div>
                <strong style="font-size:12px; color:var(--text-secondary); margin-right:8px;">Tools Required:</strong>
                <div style="display:inline-block;">${toolsHTML}</div>
            </div>
        </div>

        <div style="border-top:1px solid var(--card-border); padding-top:12px; font-size:11.5px; line-height:1.5;">
            <strong style="color:var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i> Delay Impact Assessment (Risk: ${sched.impact_if_delayed.risk_level})</strong>
            <p style="color:var(--text-secondary); margin-top:2px;">Consequences: ${sched.impact_if_delayed.potential_consequences} (Failure Probability: ${(sched.impact_if_delayed.failure_probability*100).toFixed(0)}%)</p>
        </div>
    `;
}

function renderReliabilitySchedulerView(sched) {
    const panel = document.getElementById('reliability-scheduler-content');
    if (!panel) return;

    if (!sched) {
        panel.innerHTML = `<p style="color:var(--text-secondary); font-size:13px; margin:0;">No active schedule generated. Run a diagnostic in the Technician or Engineer view to evaluate equipment health.</p>`;
        return;
    }

    const costUSD = sched.estimated_cost;
    const costNGN = costUSD * 1600;
    const costStr = `₦${costNGN.toLocaleString()} ($${costUSD})`;

    panel.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:12px;">
            <div>
                <h3 style="font-size:18px; font-weight:700; margin:0;"><i class="fa-solid fa-microchip"></i> AI Maintenance Schedule Optimization</h3>
                <p style="font-size:12px; color:var(--text-secondary); margin-top:2px;">Consolidated strategist report for the next predicted fleet action.</p>
            </div>
            <div style="display:flex; gap:8px;">
                <span class="badge" style="background:rgba(88,166,255,0.15); color:var(--accent); font-size:11px;">Type: ${sched.maintenance_type.toUpperCase()}</span>
                <span class="badge" style="background:rgba(245,158,11,0.15); color:var(--warning); font-size:11px;">Risk Level: ${sched.impact_if_delayed.risk_level}</span>
            </div>
        </div>

        <div class="kpi-grid" style="margin-bottom:16px;">
            <div class="card glass-card" style="text-align:center; padding:12px;">
                <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase;">Opt. Next Scheduled Date</div>
                <div style="font-size:20px; font-weight:700; color:var(--accent); margin-top:6px;">${sched.next_scheduled_date}</div>
                <div style="font-size:11px; color:var(--success); margin-top:4px;">In ${sched.days_until_maintenance} days</div>
            </div>
            <div class="card glass-card" style="text-align:center; padding:12px;">
                <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase;">Optimized Service Cost</div>
                <div style="font-size:20px; font-weight:700; color:var(--success); margin-top:6px;">${costStr}</div>
                <div style="font-size:11px; color:var(--text-secondary); margin-top:4px;">Savings vs reactive: ~45%</div>
            </div>
            <div class="card glass-card" style="text-align:center; padding:12px;">
                <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase;">Critical Path Priority</div>
                <div style="font-size:20px; font-weight:700; color:var(--danger); margin-top:6px;">${sched.priority} / 10</div>
                <div style="font-size:11px; color:var(--text-secondary); margin-top:4px;">Urgency: ${sched.priority > 7 ? 'Critical Action Required' : 'Standard Routine'}</div>
            </div>
        </div>

        <div class="glass-card" style="background:rgba(255,255,255,0.02); padding:16px; border:1px solid var(--card-border); margin:0;">
            <h4 style="font-size:13px; color:var(--text-primary); margin-bottom:8px;"><i class="fa-solid fa-chart-line"></i> Reliability Strategy & Prognostics</h4>
            <div style="font-size:12.5px; line-height:1.6; display:flex; flex-direction:column; gap:8px;">
                <div><strong>Recommended Strategic Action:</strong> <span style="color:var(--accent); font-weight:600;">${sched.recommended_action}</span></div>
                <div><strong>Staff Allocation:</strong> ${sched.required_staff.join(', ')}</div>
                <div><strong>Expected Downtime Duration:</strong> ${sched.estimated_duration_hours} hours</div>
                <div><strong>Consequence of Delay:</strong> <span style="color:var(--text-secondary);">${sched.impact_if_delayed.potential_consequences}</span></div>
            </div>
        </div>
    `;
}

function renderTechnicianView(ai, isOptimal) {
    const techStatusBox = document.getElementById('tech-status-box');
    const techTaskList = document.getElementById('tech-task-list');
    const techPartsList = document.getElementById('tech-parts-list');

    if (isOptimal) {
        techStatusBox.className = 'status-box optimal';
        techStatusBox.innerHTML = `
            <h1 style="font-size:26px; margin-bottom:8px;"><i class="fa-solid fa-circle-check"></i> System Optimal</h1>
            <p>No immediate maintenance required.</p>
        `;
        techTaskList.innerHTML = '<p class="text-muted">No active tasks.</p>';
        techPartsList.innerHTML = '<p class="text-muted">No parts required.</p>';
    } else {
        const severityClass = ai.severity === 'critical' ? 'critical' : 'warning';
        techStatusBox.className = `status-box ${severityClass}`;
        techStatusBox.innerHTML = `
            <h1 style="font-size:26px; margin-bottom:8px;"><i class="fa-solid fa-triangle-exclamation"></i> ${ai.fault_name}</h1>
            <p>Requires immediate attention.</p>
        `;

        techTaskList.innerHTML = ai.primary_actions.map((task, idx) => `
            <div class="task-item" onclick="this.classList.toggle('done')">
                <input type="checkbox" class="task-checkbox" id="task-${idx}">
                <label class="task-label" for="task-${idx}">${task}</label>
            </div>
        `).join('');

        techPartsList.innerHTML = ai.spare_parts && ai.spare_parts.length > 0 
            ? ai.spare_parts.map(p => `
                <span class="part-item">
                    <i class="fa-solid fa-wrench"></i> ${p} &nbsp;
                    <span class="stock-ok" style="color:var(--success); font-weight:700">✓ In stock</span>
                </span>
            `).join('')
            : '<p class="text-muted">No specific parts flagged.</p>';
    }
}

function simulateLiveTelemetry() {
    const tempSlider = document.getElementById('temp-slider');
    if (!tempSlider) return;

    // 3.5% chance to trigger a random operational anomaly if currently nominal
    if (!activeSimulationAnomaly && Math.random() < 0.035) {
        const anomalies = ['overheating', 'high_vibration', 'pressure_failure', 'low_oil', 'coolant_leak'];
        activeSimulationAnomaly = anomalies[Math.floor(Math.random() * anomalies.length)];
        console.log(`[Simulation] Anomaly triggered: ${activeSimulationAnomaly}`);
        
        // Update the preset selector UI to reflect the drifting state
        const presetSelect = document.getElementById('preset-select');
        if (presetSelect) presetSelect.value = activeSimulationAnomaly;
    }

    let temp, pres, vib, flow, oil, rpm;

    if (activeSimulationAnomaly) {
        const target = PRESETS[activeSimulationAnomaly];
        if (target) {
            // Gradual pull towards anomaly parameters
            temp = parseFloat(tempSlider.value) + (target.temp - parseFloat(tempSlider.value)) * 0.15 + (Math.random() * 2 - 1.0);
            pres = parseFloat(document.getElementById('pres-slider').value) + (target.pres - parseFloat(document.getElementById('pres-slider').value)) * 0.15 + (Math.random() * 4 - 2.0);
            vib = parseFloat(document.getElementById('vib-slider').value) + (target.vib - parseFloat(document.getElementById('vib-slider').value)) * 0.15 + (Math.random() * 0.003 - 0.0015);
            flow = parseFloat(document.getElementById('flow-slider').value) + (target.flow - parseFloat(document.getElementById('flow-slider').value)) * 0.15 + (Math.random() * 10 - 5.0);
            oil = parseFloat(document.getElementById('oil-slider').value) + (target.oil - parseFloat(document.getElementById('oil-slider').value)) * 0.15 + (Math.random() * 2 - 1.0);
            rpm = parseFloat(document.getElementById('rpm-slider').value) + (target.rpm - parseFloat(document.getElementById('rpm-slider').value)) * 0.15 + (Math.random() * 40 - 20.0);
            
            if (target.leak === 1 && Math.random() < 0.4) {
                document.getElementById('leak-select').value = "1";
            }
        }
    } else {
        // Slight natural drift around standard nominal baselines
        temp = parseFloat(tempSlider.value) + (70 - parseFloat(tempSlider.value)) * 0.05 + (Math.random() * 2 - 1.0);
        pres = parseFloat(document.getElementById('pres-slider').value) + (100 - parseFloat(document.getElementById('pres-slider').value)) * 0.05 + (Math.random() * 4 - 2.0);
        vib = parseFloat(document.getElementById('vib-slider').value) + (0.02 - parseFloat(document.getElementById('vib-slider').value)) * 0.05 + (Math.random() * 0.002 - 0.001);
        flow = parseFloat(document.getElementById('flow-slider').value) + (300 - parseFloat(document.getElementById('flow-slider').value)) * 0.05 + (Math.random() * 6 - 3.0);
        oil = parseFloat(document.getElementById('oil-slider').value) + (60 - parseFloat(document.getElementById('oil-slider').value)) * 0.05 + (Math.random() * 1.5 - 0.75);
        rpm = parseFloat(document.getElementById('rpm-slider').value) + (1500 - parseFloat(document.getElementById('rpm-slider').value)) * 0.05 + (Math.random() * 30 - 15.0);
        
        if (document.getElementById('leak-select').value === "1" && Math.random() < 0.2) {
            document.getElementById('leak-select').value = "0";
        }
    }

    setSliderValue('temp', Math.min(Math.max(temp, 20), 150).toFixed(1));
    setSliderValue('pres', Math.min(Math.max(pres, 0), 200).toFixed(1));
    setSliderValue('vib', Math.min(Math.max(vib, 0), 0.1).toFixed(3));
    setSliderValue('flow', Math.min(Math.max(flow, 0), 1000).toFixed(0));
    setSliderValue('oil', Math.min(Math.max(oil, 0), 100).toFixed(0));
    setSliderValue('rpm', Math.min(Math.max(rpm, 0), 5000).toFixed(0));

    updateRawDataTable();
    runDiagnostic(true); // silent=true: skip animation and spinner during live telemetry
}

function updateChartPoint(vib, flow, oil) {
    const now = new Date();
    chartData.labels.push(now.toLocaleTimeString([], {hour12: false, second: '2-digit'}));
    chartData.datasets[0].data.push(parseFloat(vib));
    chartData.datasets[1].data.push(parseFloat(flow));
    chartData.datasets[2].data.push(parseFloat(oil));
    
    if (chartData.labels.length > MAX_DATA_POINTS) {
        chartData.labels.shift();
        chartData.datasets[0].data.shift();
        chartData.datasets[1].data.shift();
        chartData.datasets[2].data.shift();
    }
    telemetryChart.update();
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    // Remove any existing suggestions pills first
    const oldPills = document.getElementById('chat-suggestions');
    if (oldPills) oldPills.remove();

    appendChatMessage('user', text);
    input.value = '';
    chatMessages.push({ role: 'user', content: text });

    const typingId = appendTypingIndicator();

    const payload = {
        messages: chatMessages,
        sensor_data: getSensorData(),
        diagnosis: currentDiagnosis,
        persona: currentRole === 'tech' ? 'Mechanical Technician' : 'Maintenance Engineer'
    };

    try {
        const response = await authFetch(getApiUrl('/chat'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        removeElement(typingId);
        
        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            const errMsg = errData.error || `HTTP error ${response.status}`;
            appendChatMessage('ai', `⚠️ ${errMsg}`);
            return;
        }

        // Setup streaming container
        const hist = document.getElementById('chat-history');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai-msg markdown-content';
        hist.appendChild(messageDiv);
        hist.scrollTop = hist.scrollHeight;

        let totalTypedText = "";
        let thinkingAccordion = null;
        let responseSpan = null;

        let tokenQueue = [];
        let streamDone = false;

        // Adaptive typing interval loop (runs at a controlled professional speed)
        const typingInterval = setInterval(() => {
            if (tokenQueue.length === 0) {
                if (streamDone) {
                    clearInterval(typingInterval);
                    chatMessages.push({ role: 'assistant', content: totalTypedText });
                    renderQuestionSuggestions();
                }
                return;
            }

            // Adaptive speed: drain characters faster if network sent a large buffer
            let take = 1;
            if (tokenQueue.length > 60) take = 2;
            if (tokenQueue.length > 150) take = 4;
            if (tokenQueue.length > 300) take = 8;

            let batch = "";
            for (let i = 0; i < take && tokenQueue.length > 0; i++) {
                batch += tokenQueue.shift();
            }

            totalTypedText += batch;

            // Check for thinking blocks and render appropriately
            if (totalTypedText.includes("<thinking>")) {
                if (!thinkingAccordion) {
                    thinkingAccordion = document.createElement('div');
                    thinkingAccordion.className = 'thinking-accordion';
                    thinkingAccordion.innerHTML = `
                        <div class="thinking-header">
                            <span><i class="fa-solid fa-brain fa-spin"></i> Thinking.....</span>
                            <i class="fa-solid fa-chevron-down fold-icon"></i>
                        </div>
                        <div class="thinking-content"></div>
                    `;
                    messageDiv.appendChild(thinkingAccordion);

                    thinkingAccordion.querySelector('.thinking-header').addEventListener('click', () => {
                        thinkingAccordion.classList.toggle('collapsed');
                    });
                }

                const hasClosedThinking = totalTypedText.includes("</thinking>");
                const thinkingMatch = totalTypedText.match(/<thinking>([\s\S]*?)(?:<\/thinking>|$)/);
                if (thinkingMatch && thinkingMatch[1]) {
                    thinkingAccordion.querySelector('.thinking-content').textContent = thinkingMatch[1].trim();
                }

                if (hasClosedThinking) {
                    thinkingAccordion.querySelector('.thinking-header span').innerHTML = `<i class="fa-solid fa-circle-check" style="color:var(--success)"></i> Diagnostics Check Complete`;
                    if (!thinkingAccordion.classList.contains('collapsed')) {
                        thinkingAccordion.classList.add('collapsed');
                    }

                    const parts = totalTypedText.split("</thinking>");
                    const mainResponse = parts[1] || "";

                    if (!responseSpan) {
                        responseSpan = document.createElement('div');
                        responseSpan.className = 'response-body';
                        messageDiv.appendChild(responseSpan);
                    }
                    responseSpan.innerHTML = formatMarkdown(mainResponse);
                }
            } else {
                if (!responseSpan) {
                    responseSpan = document.createElement('div');
                    responseSpan.className = 'response-body';
                    messageDiv.appendChild(responseSpan);
                }
                responseSpan.innerHTML = formatMarkdown(totalTypedText);
            }
            hist.scrollTop = hist.scrollHeight;
        }, 40);

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let streamBuffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                streamDone = true;
                break;
            }

            streamBuffer += decoder.decode(value, { stream: true });
            const lines = streamBuffer.split("\n");
            streamBuffer = lines.pop();

            for (const line of lines) {
                const trimmed = line.trim();
                if (trimmed.startsWith("data: ")) {
                    try {
                        const parsed = JSON.parse(trimmed.slice(6));
                        if (parsed.error) {
                            clearInterval(typingInterval);
                            messageDiv.innerHTML = `<div style="color:var(--danger)">⚠️ ${parsed.error}</div>`;
                            return;
                        }
                        if (parsed.text) {
                            // Queue characters for typing loop
                            for (let i = 0; i < parsed.text.length; i++) {
                                tokenQueue.push(parsed.text[i]);
                            }
                        }
                    } catch (e) {
                        console.error("Error parsing JSON line:", e, line);
                    }
                }
            }
        }

    } catch (err) {
        console.error(err);
        removeElement(typingId);
        appendChatMessage('ai', 'Failed to communicate with AI Copilot.');
    }
}

function renderQuestionSuggestions() {
    // Remove any existing suggestions pills first
    const oldPills = document.getElementById('chat-suggestions');
    if (oldPills) oldPills.remove();

    const hist = document.getElementById('chat-history');
    
    // Get suggestions based on diagnostic code
    let faultCode = 0;
    if (currentDiagnosis && currentDiagnosis.fault_code !== undefined) {
        faultCode = currentDiagnosis.fault_code;
    }
    
    const suggestionsMap = {
        0: [
            "What preventive maintenance should we plan next?",
            "Show MTBF stats of pump systems.",
            "What is the target vibration baseline?"
        ],
        1: [
            "How do I clean the radiator fins?",
            "What tools are needed to inspect the bearing casing?",
            "What are the torque settings for bearing assembly?"
        ],
        2: [
            "How do I check shaft alignment?",
            "What type of grease should be packed in the bearings?",
            "How to test for structural looseness?"
        ],
        3: [
            "How to bleed air from pressure lines?",
            "What are the standard relief valve limits?",
            "Check for hydraulic leak indicators."
        ],
        4: [
            "What grade of oil is recommended?",
            "Where are the standard oil leak points?",
            "How do I calibrate the oil level sensor?"
        ],
        5: [
            "How to inspect the coolant pipe seals?",
            "What is the coolant mixture ratio?",
            "How do I bleed the coolant lines?"
        ]
    };

    const suggestions = suggestionsMap[faultCode] || suggestionsMap[0];
    
    const container = document.createElement('div');
    container.id = 'chat-suggestions';
    container.className = 'suggestion-pills';
    
    suggestions.forEach(q => {
        const btn = document.createElement('button');
        btn.className = 'suggestion-pill';
        btn.textContent = q;
        btn.addEventListener('click', () => {
            document.getElementById('chat-input').value = q;
            sendChatMessage();
        });
        container.appendChild(btn);
    });
    
    hist.appendChild(container);
    hist.scrollTop = hist.scrollHeight;
}

function appendChatMessage(role, htmlContent) {
    const hist = document.getElementById('chat-history');
    const div = document.createElement('div');
    div.className = `message ${role === 'user' ? 'user-msg' : 'ai-msg markdown-content'}`;
    div.innerHTML = htmlContent;
    hist.appendChild(div);
    hist.scrollTop = hist.scrollHeight;
}

function appendTypingIndicator() {
    const id = 'typing-' + Date.now();
    const hist = document.getElementById('chat-history');
    const div = document.createElement('div');
    div.id = id;
    div.className = 'message ai-msg';
    div.innerHTML = `<span style="font-size: 13px; color: var(--text-secondary); font-style: italic;"><i class="fa-solid fa-spinner fa-spin"></i> Thinking.....</span>`;
    hist.appendChild(div);
    hist.scrollTop = hist.scrollHeight;
    return id;
}

function removeElement(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function formatMarkdown(text) {
    if(!text) return text;
    let html = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br/>');
        
    html = html.replace(/<br\/>- (.*?)(?=<br\/>|$)/g, '<ul><li>$1</li></ul>');
    html = html.replace(/<\/ul><ul>/g, ''); 
    
    return html;
}
