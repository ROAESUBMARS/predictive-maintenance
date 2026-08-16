// ── Live Telemetry Client (SSE / REST Polling Hybrid) ───────────
(function() {
    let eventSource = null;
    let pollingInterval = null;
    let isConnected = false;

    function initTelemetryClient() {
        trySSEOrPolling();
    }

    function trySSEOrPolling() {
        if (isConnected) return;

        // Try Server-Sent Events (SSE) stream endpoint first
        if (typeof EventSource !== 'undefined' && !eventSource && !pollingInterval) {
            console.log('📡 Attempting SSE stream: /api/telemetry/stream');
            try {
                eventSource = new EventSource('/api/telemetry/stream');
                eventSource.onopen = function() {
                    console.log('🟢 SSE Stream Connected!');
                    isConnected = true;
                    setLiveBadge(true, 'LIVE STREAM');
                    if (window.setLocalSimulationPaused) window.setLocalSimulationPaused(true);
                };
                eventSource.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        onSensorDataReceived(data);
                    } catch (e) {}
                };
                eventSource.onerror = function() {
                    console.warn('⚠️ SSE Stream disconnected. Switching to 1s REST Polling...');
                    if (eventSource) {
                        eventSource.close();
                        eventSource = null;
                    }
                    startRESTPolling();
                };
                return;
            } catch (err) {
                console.warn('SSE not supported or failed, falling back to REST polling');
            }
        }

        startRESTPolling();
    }

    function startRESTPolling() {
        if (pollingInterval || isConnected) return;

        console.log('🔄 Starting 1s REST Polling endpoint: /api/telemetry/live');
        
        async function fetchTick() {
            try {
                const res = await fetch('/api/telemetry/live');
                if (res.ok) {
                    const json = await res.json();
                    if (json && json.pumps) {
                        if (!isConnected) {
                            isConnected = true;
                            setLiveBadge(true, 'LIVE API');
                            if (window.setLocalSimulationPaused) window.setLocalSimulationPaused(true);
                        }
                        onSensorDataReceived(json.pumps);
                    }
                }
            } catch (err) {
                // If API fails, resume local simulation
                setLiveBadge(false);
                isConnected = false;
                if (window.setLocalSimulationPaused) window.setLocalSimulationPaused(false);
            }
        }

        fetchTick();
        pollingInterval = setInterval(fetchTick, 1000);
    }

    function setLiveBadge(connected, label = 'LIVE WS') {
        const badge = document.getElementById('ws-live-badge');
        if (badge) {
            if (connected) {
                badge.style.display = 'inline-flex';
                badge.className = 'ws-badge connected';
                badge.innerHTML = `<i class="fa-solid fa-satellite-dish fa-spin"></i> ${label}`;
            } else {
                badge.style.display = 'none';
            }
        }
    }

    function onSensorDataReceived(allPumpsData) {
        // Sync PUMPS array for Fleet Map & cards
        if (window.PUMPS && Array.isArray(window.PUMPS)) {
            window.PUMPS.forEach(p => {
                const live = allPumpsData[p.id];
                if (live) {
                    p.temp = live.temp;
                    p.pressure = live.pressure;
                    p.vib = live.vibration;
                    p.oil = live.oil;
                    p.status = live.status;
                    p.fault = live.fault;
                }
            });
            if (typeof window.updateRawDataTable === 'function') {
                window.updateRawDataTable();
            }
        }

        // Active selected pump (HP-01 by default)
        const activePumpId = window.activePumpId || 'HP-01';
        const activeData = allPumpsData[activePumpId] || allPumpsData['HP-01'];
        if (!activeData) return;

        // Update dashboard numeric displays
        const tempValEl = document.getElementById('temp-val');
        const presValEl = document.getElementById('pres-val');
        const vibValEl  = document.getElementById('vib-val');
        const flowValEl = document.getElementById('flow-val');
        const oilValEl  = document.getElementById('oil-val');
        const rpmValEl  = document.getElementById('rpm-val');

        if (tempValEl) tempValEl.textContent = activeData.temp.toFixed(1);
        if (presValEl) presValEl.textContent = activeData.pressure.toFixed(1);
        if (vibValEl)  vibValEl.textContent  = activeData.vibration.toFixed(3);
        if (flowValEl) flowValEl.textContent = activeData.flow.toFixed(0);
        if (oilValEl)  oilValEl.textContent  = activeData.oil.toFixed(0);
        if (rpmValEl)  rpmValEl.textContent  = activeData.rpm.toFixed(0);

        // Update active sliders smoothly
        setSliderIfExist('temp-slider', activeData.temp);
        setSliderIfExist('pres-slider', activeData.pressure);
        setSliderIfExist('vib-slider', activeData.vibration);
        setSliderIfExist('flow-slider', activeData.flow);
        setSliderIfExist('oil-slider', activeData.oil);
        setSliderIfExist('rpm-slider', activeData.rpm);

        // Feed telemetry chart
        if (typeof window.updateChartPoint === 'function') {
            window.updateChartPoint(activeData.vibration.toFixed(3), activeData.flow.toFixed(0), activeData.oil.toFixed(0));
        }

        // Feed 3D Model Telemetry if present
        if (typeof window.update3DModelTelemetry === 'function') {
            window.update3DModelTelemetry(activeData.temp, activeData.vibration, activeData.status === 'red' ? 1 : 0);
        }
    }

    function setSliderIfExist(id, val) {
        const el = document.getElementById(id);
        if (el) el.value = val;
    }

    document.addEventListener('DOMContentLoaded', initTelemetryClient);
})();
