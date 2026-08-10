// ── Live WebSocket Sensor Client ─────────────────────────────────────────────
(function() {
    let socket = null;
    let isWSConnected = false;

    function initWebSocket() {
        if (typeof io === 'undefined') {
            console.log('Socket.IO client library not loaded. Falling back to local simulation.');
            return;
        }

        const serverUrl = window.location.origin;
        console.log('🔌 Connecting to WebSocket server:', serverUrl);

        try {
            socket = io(serverUrl, {
                reconnection: true,
                reconnectionAttempts: 10,
                reconnectionDelay: 1000,
                timeout: 5000
            });

            socket.on('connect', () => {
                console.log('🟢 WebSocket connected! ID:', socket.id);
                isWSConnected = true;
                setLiveWSBadge(true);
                if (window.setLocalSimulationPaused) {
                    window.setLocalSimulationPaused(true);
                }
            });

            socket.on('disconnect', () => {
                console.log('🔴 WebSocket disconnected.');
                isWSConnected = false;
                setLiveWSBadge(false);
                if (window.setLocalSimulationPaused) {
                    window.setLocalSimulationPaused(false);
                }
            });

            socket.on('sensor_update', (allPumpsData) => {
                onSensorDataReceived(allPumpsData);
            });

        } catch (err) {
            console.warn('WebSocket connection error:', err);
            setLiveWSBadge(false);
        }
    }

    function setLiveWSBadge(connected) {
        const badge = document.getElementById('ws-live-badge');
        if (badge) {
            if (connected) {
                badge.style.display = 'inline-flex';
                badge.className = 'ws-badge connected';
                badge.innerHTML = '<i class="fa-solid fa-satellite-dish fa-spin"></i> LIVE WS';
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

    document.addEventListener('DOMContentLoaded', initWebSocket);
})();
