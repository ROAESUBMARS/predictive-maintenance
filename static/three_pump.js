// ═════════════════════════════════════════════════════════════════════════════
// THREE.JS 3D DIGITAL TWIN & LANDING PAGE VISUALIZER
// NMU AI Predictive Maintenance System — Dual-Motor Industrial HPU Skid Model
// ═════════════════════════════════════════════════════════════════════════════

let landingBgScene, landingBgCamera, landingBgRenderer, landingParticles;
let pumpScene, pumpCamera, pumpRenderer, pumpGroup;
let motorAMesh, motorBMesh, driveGearMesh, drivenGearMesh, fluidMesh, heatFanMesh;
let active3DMode = 'solid'; // 'solid', 'hologram', 'thermal', 'photo', 'split'
let current3DTelemetry = { temp: 74, vib: 0.024, fault: 0, motorA_rpm: 1750, motorB_rpm: 1748, oil_level: 82, pressure_bar: 185 };
let isAutoRotating = true;

// Initialize 3D Background Particle Constellation
function initLanding3DBg() {
    const canvas = document.getElementById('landing-3d-bg');
    if (!canvas || !window.THREE) return;

    landingBgScene = new THREE.Scene();
    landingBgCamera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 1000);
    landingBgCamera.position.z = 400;

    landingBgRenderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    landingBgRenderer.setSize(window.innerWidth, window.innerHeight);
    landingBgRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const particleCount = 800;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const color1 = new THREE.Color(0x58a6ff);
    const color2 = new THREE.Color(0xbc8cff);

    for (let i = 0; i < particleCount; i++) {
        positions[i * 3] = (Math.random() - 0.5) * 1400;
        positions[i * 3 + 1] = (Math.random() - 0.5) * 900;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 900;

        const mixedColor = color1.clone().lerp(color2, Math.random());
        colors[i * 3] = mixedColor.r;
        colors[i * 3 + 1] = mixedColor.g;
        colors[i * 3 + 2] = mixedColor.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
        size: 3.2,
        vertexColors: true,
        transparent: true,
        opacity: 0.55,
        blending: THREE.AdditiveBlending
    });

    landingParticles = new THREE.Points(geometry, material);
    landingBgScene.add(landingParticles);

    let mouseX = 0, mouseY = 0;
    window.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX - window.innerWidth / 2) * 0.1;
        mouseY = (e.clientY - window.innerHeight / 2) * 0.1;
    });

    window.addEventListener('resize', () => {
        if (!landingBgRenderer) return;
        landingBgCamera.aspect = window.innerWidth / window.innerHeight;
        landingBgCamera.updateProjectionMatrix();
        landingBgRenderer.setSize(window.innerWidth, window.innerHeight);
    });

    function animateBg() {
        requestAnimationFrame(animateBg);
        if (landingParticles) {
            landingParticles.rotation.y += 0.0008;
            landingParticles.rotation.x += 0.0004;
        }
        landingBgCamera.position.x += (mouseX - landingBgCamera.position.x) * 0.04;
        landingBgCamera.position.y += (-mouseY - landingBgCamera.position.y) * 0.04;
        landingBgCamera.lookAt(landingBgScene.position);
        landingBgRenderer.render(landingBgScene, landingBgCamera);
    }
    animateBg();
}

// Build 3D Technical Procedural Model of Heavy-Duty Dual-Motor HPU Skid System
function build3DPumpModel() {
    pumpGroup = new THREE.Group();

    // ── Color Palette & Materials ──
    const hpuBlueMat = new THREE.MeshStandardMaterial({
        color: 0x0f52ba,
        metalness: 0.7,
        roughness: 0.35
    });

    const motorBlueMat = new THREE.MeshStandardMaterial({
        color: 0x1d6ee2,
        metalness: 0.8,
        roughness: 0.3
    });

    const steelMat = new THREE.MeshStandardMaterial({
        color: 0xc4d1e2,
        metalness: 0.95,
        roughness: 0.15
    });

    const darkSteelMat = new THREE.MeshStandardMaterial({
        color: 0x2d3748,
        metalness: 0.8,
        roughness: 0.4
    });

    const panelGreyMat = new THREE.MeshStandardMaterial({
        color: 0xc8d1d9,
        metalness: 0.3,
        roughness: 0.5
    });

    const brassMat = new THREE.MeshStandardMaterial({
        color: 0xd4a017,
        metalness: 0.85,
        roughness: 0.25
    });

    const glassMat = new THREE.MeshPhysicalMaterial({
        color: 0x58a6ff,
        transparent: true,
        opacity: 0.35,
        roughness: 0.1,
        transmission: 0.9,
        thickness: 0.5
    });

    const fluidMat = new THREE.MeshStandardMaterial({
        color: 0x0969da,
        transparent: true,
        opacity: 0.75,
        roughness: 0.2
    });

    const hoseMat = new THREE.MeshStandardMaterial({
        color: 0x1a202c,
        roughness: 0.8,
        metalness: 0.1
    });

    // 1. BASE SKID STRUCTURAL TRAY & FRAME
    const skidBaseGeo = new THREE.BoxGeometry(10.5, 0.4, 7.5);
    const skidBaseMesh = new THREE.Mesh(skidBaseGeo, hpuBlueMat);
    skidBaseMesh.position.set(0, -2.4, 0);
    pumpGroup.add(skidBaseMesh);

    // Skid Outer Retaining Lips
    const lipFrontGeo = new THREE.BoxGeometry(10.5, 0.5, 0.3);
    const lipFront = new THREE.Mesh(lipFrontGeo, hpuBlueMat);
    lipFront.position.set(0, -2.15, 3.6);
    pumpGroup.add(lipFront);

    const lipBack = lipFront.clone();
    lipBack.position.set(0, -2.15, -3.6);
    pumpGroup.add(lipBack);

    // 2. DUAL ELECTRIC MOTORS (FRONT RIGHT & FRONT CENTER)
    function buildElectricMotor(nameLabel) {
        const mGroup = new THREE.Group();

        // Main Cylindrical Stator Housing
        const bodyGeo = new THREE.CylinderGeometry(1.05, 1.05, 2.8, 32);
        const bodyMesh = new THREE.Mesh(bodyGeo, motorBlueMat);
        bodyMesh.rotation.z = Math.PI / 2;
        mGroup.add(bodyMesh);

        // Cooling Fins Array around Stator
        for (let i = 0; i < 8; i++) {
            const finAngle = (i / 8) * Math.PI * 2;
            const finGeo = new THREE.BoxGeometry(2.6, 0.08, 0.12);
            const finMesh = new THREE.Mesh(finGeo, steelMat);
            finMesh.position.set(0, Math.cos(finAngle) * 1.1, Math.sin(finAngle) * 1.1);
            mGroup.add(finMesh);
        }

        // Rear Cooling Fan Guard Shroud & Mesh
        const shroudGeo = new THREE.CylinderGeometry(1.1, 1.1, 0.5, 32);
        const shroudMesh = new THREE.Mesh(shroudGeo, darkSteelMat);
        shroudMesh.rotation.z = Math.PI / 2;
        shroudMesh.position.set(1.5, 0, 0);
        mGroup.add(shroudMesh);

        const grilleRingGeo = new THREE.TorusGeometry(0.85, 0.06, 16, 24);
        const grilleMesh = new THREE.Mesh(grilleRingGeo, steelMat);
        grilleMesh.position.set(1.76, 0, 0);
        grilleMesh.rotation.y = Math.PI / 2;
        mGroup.add(grilleMesh);

        // Front End Bell & Drive Shaft
        const shaftGeo = new THREE.CylinderGeometry(0.35, 0.35, 1.2, 24);
        const shaftMesh = new THREE.Mesh(shaftGeo, steelMat);
        shaftMesh.rotation.z = Math.PI / 2;
        shaftMesh.position.set(-1.8, 0, 0);
        mGroup.add(shaftMesh);

        // Junction Electrical Box on Top of Motor
        const jboxGeo = new THREE.BoxGeometry(0.8, 0.5, 0.8);
        const jboxMesh = new THREE.Mesh(jboxGeo, darkSteelMat);
        jboxMesh.position.set(-0.2, 1.25, 0);
        mGroup.add(jboxMesh);

        return mGroup;
    }

    // Motor A (Front Left-Center)
    motorAMesh = buildElectricMotor("Motor A");
    motorAMesh.position.set(0.6, -1.2, 1.8);
    pumpGroup.add(motorAMesh);

    // Motor B (Front Right)
    motorBMesh = buildElectricMotor("Motor B");
    motorBMesh.position.set(3.6, -1.2, 1.8);
    pumpGroup.add(motorBMesh);

    // 3. MAIN HYDRAULIC RESERVOIR TANK (LEFT SKID ASSEMBLY)
    const tankGroup = new THREE.Group();

    // Blue Tank Body
    const tankGeo = new THREE.BoxGeometry(4.2, 3.6, 5.8);
    const tankMesh = new THREE.Mesh(tankGeo, hpuBlueMat);
    tankGroup.add(tankMesh);

    // Front Inspection Access Plate (Circular Hatch)
    const hatchGeo = new THREE.CylinderGeometry(0.7, 0.7, 0.12, 24);
    const hatchMesh = new THREE.Mesh(hatchGeo, darkSteelMat);
    hatchMesh.position.set(-2.11, -0.6, 0.8);
    hatchMesh.rotation.z = Math.PI / 2;
    tankGroup.add(hatchMesh);

    // Oil Sight Gauge Glass on Tank Side
    const sightGeo = new THREE.BoxGeometry(0.1, 1.4, 0.3);
    const sightMesh = new THREE.Mesh(sightGeo, glassMat);
    sightMesh.position.set(-2.12, 0.2, 2.0);
    tankGroup.add(sightMesh);

    // Inner Hydraulic Fluid Level Visualization
    const fluidGeo = new THREE.BoxGeometry(4.0, 2.6, 5.6);
    fluidMesh = new THREE.Mesh(fluidGeo, fluidMat);
    fluidMesh.position.set(0, -0.4, 0);
    tankGroup.add(fluidMesh);

    // 4. CUTAWAY PRECISION GEAR SECTION ON TANK FRONT
    function createGear(radius, teeth, depth) {
        const gearGroup = new THREE.Group();
        const coreGeo = new THREE.CylinderGeometry(radius, radius, depth, 32);
        const coreMesh = new THREE.Mesh(coreGeo, steelMat);
        coreMesh.rotation.x = Math.PI / 2;
        gearGroup.add(coreMesh);

        for (let i = 0; i < teeth; i++) {
            const angle = (i / teeth) * Math.PI * 2;
            const toothGeo = new THREE.BoxGeometry(0.16, 0.32, depth);
            const toothMesh = new THREE.Mesh(toothGeo, brassMat);
            toothMesh.position.set(Math.cos(angle) * radius, Math.sin(angle) * radius, 0);
            toothMesh.rotation.z = angle;
            gearGroup.add(toothMesh);
        }
        return gearGroup;
    }

    driveGearMesh = createGear(0.75, 12, 1.0);
    driveGearMesh.position.set(-0.2, 0.4, 2.92);
    tankGroup.add(driveGearMesh);

    drivenGearMesh = createGear(0.75, 12, 1.0);
    drivenGearMesh.position.set(-0.2, -0.6, 2.92);
    tankGroup.add(drivenGearMesh);

    tankGroup.position.set(-2.8, -0.4, -0.6);
    pumpGroup.add(tankGroup);

    // 5. REAR TUBULAR FRAME & ELECTRICAL CONTROL / PLC CABINET (RIGHT REAR)
    const frameGroup = new THREE.Group();

    // Tubular Steel Support Columns
    const postGeo = new THREE.CylinderGeometry(0.18, 0.18, 4.8, 16);
    const p1 = new THREE.Mesh(postGeo, hpuBlueMat);
    p1.position.set(3.2, 0, -2.6);
    frameGroup.add(p1);

    const p2 = p1.clone();
    p2.position.set(4.6, 0, -2.6);
    frameGroup.add(p2);

    const p3 = p1.clone();
    p3.position.set(4.6, 0, 1.2);
    frameGroup.add(p3);

    // Grey Enclosure Box (PLC Control Cabinet)
    const cabinetGeo = new THREE.BoxGeometry(0.4, 4.2, 3.2);
    const cabinetMesh = new THREE.Mesh(cabinetGeo, panelGreyMat);
    cabinetMesh.position.set(4.4, 0.6, -0.6);
    frameGroup.add(cabinetMesh);

    // Door Handle & Panel Bezel
    const bezelGeo = new THREE.BoxGeometry(0.08, 3.8, 2.8);
    const bezelMesh = new THREE.Mesh(bezelGeo, darkSteelMat);
    bezelMesh.position.set(4.18, 0.6, -0.6);
    frameGroup.add(bezelMesh);

    // Conduit Pipes connecting Control Panel to Motors
    const conduitGeo = new THREE.CylinderGeometry(0.1, 0.1, 3.5, 12);
    const c1 = new THREE.Mesh(conduitGeo, steelMat);
    c1.position.set(3.8, -0.8, 0.2);
    c1.rotation.z = Math.PI / 3;
    frameGroup.add(c1);

    pumpGroup.add(frameGroup);

    // 6. TOP AIR HEAT EXCHANGER & RADIATOR COOLING FAN (TOP TANK MOUNT)
    const coolerGroup = new THREE.Group();

    // Heat Exchanger Housing
    const coolerBodyGeo = new THREE.BoxGeometry(2.2, 1.2, 2.2);
    const coolerBodyMesh = new THREE.Mesh(coolerBodyGeo, hpuBlueMat);
    coolerGroup.add(coolerBodyMesh);

    // Round Top Fan Shroud
    const shroudGeo = new THREE.CylinderGeometry(0.8, 0.8, 0.3, 24);
    const shroudMesh = new THREE.Mesh(shroudGeo, darkSteelMat);
    shroudMesh.position.set(0, 0.7, 0);
    coolerGroup.add(shroudMesh);

    // Fan Blade Mesh Inside Shroud
    const fanGeo = new THREE.BoxGeometry(1.3, 0.05, 0.22);
    heatFanMesh = new THREE.Mesh(fanGeo, steelMat);
    heatFanMesh.position.set(0, 0.82, 0);
    coolerGroup.add(heatFanMesh);

    const fanCross = heatFanMesh.clone();
    fanCross.rotation.y = Math.PI / 2;
    coolerGroup.add(fanCross);

    coolerGroup.position.set(-2.8, 2.2, -0.6);
    pumpGroup.add(coolerGroup);

    // 7. HIGH-PRESSURE HYDRAULIC HOSES & MANIFOLD TUBING
    function createHose(pts) {
        const curve = new THREE.CatmullRomCurve3(pts);
        const tubeGeo = new THREE.TubeGeometry(curve, 24, 0.12, 8, false);
        return new THREE.Mesh(tubeGeo, hoseMat);
    }

    const hose1 = createHose([
        new THREE.Vector3(-1.2, 1.6, -0.6),
        new THREE.Vector3(-0.4, 2.2, 0.8),
        new THREE.Vector3(0.6, 0.2, 1.8)
    ]);
    pumpGroup.add(hose1);

    const hose2 = createHose([
        new THREE.Vector3(-1.2, 1.2, -0.6),
        new THREE.Vector3(1.2, 2.0, 0.6),
        new THREE.Vector3(3.6, 0.2, 1.8)
    ]);
    pumpGroup.add(hose2);

    return pumpGroup;
}

// Initialize 3D Pump Viewer in specified canvas
function initPump3DViewer(canvasId, containerId) {
    const canvas = document.getElementById(canvasId);
    const container = document.getElementById(containerId);
    if (!canvas || !container || !window.THREE) return;

    pumpScene = new THREE.Scene();
    pumpCamera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    pumpCamera.position.set(11, 7, 14);

    pumpRenderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    pumpRenderer.setSize(container.clientWidth, container.clientHeight);
    pumpRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Studio Technical Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
    pumpScene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x58a6ff, 1.5);
    dirLight1.position.set(12, 18, 12);
    pumpScene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xbc8cff, 0.85);
    dirLight2.position.set(-12, -10, -12);
    pumpScene.add(dirLight2);

    // Build Model
    const model = build3DPumpModel();
    pumpScene.add(model);
    pumpCamera.lookAt(0, 0, 0);

    // Orbit Drag Controls
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };

    canvas.addEventListener('mousedown', (e) => {
        isDragging = true;
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener('mouseup', () => { isDragging = false; });

    canvas.addEventListener('mousemove', (e) => {
        if (!isDragging || !pumpGroup) return;
        const deltaX = e.clientX - previousMousePosition.x;
        const deltaY = e.clientY - previousMousePosition.y;

        pumpGroup.rotation.y += deltaX * 0.008;
        pumpGroup.rotation.x += deltaY * 0.008;

        previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    // Zoom on wheel
    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        pumpCamera.position.z += e.deltaY * 0.01;
        pumpCamera.position.z = Math.max(6, Math.min(26, pumpCamera.position.z));
    }, { passive: false });

    // Window Resize
    window.addEventListener('resize', () => {
        if (!container || !pumpRenderer) return;
        pumpCamera.aspect = container.clientWidth / container.clientHeight;
        pumpCamera.updateProjectionMatrix();
        pumpRenderer.setSize(container.clientWidth, container.clientHeight);
    });

    // Animation Loop
    function render3DPump() {
        requestAnimationFrame(render3DPump);

        // Spin Internal Gears in opposite intermeshing directions
        if (driveGearMesh && drivenGearMesh) {
            driveGearMesh.rotation.z += 0.05;
            drivenGearMesh.rotation.z -= 0.05;
        }

        // Spin Heat Exchanger Radiator Fan
        if (heatFanMesh) {
            heatFanMesh.rotation.y += 0.12;
        }

        if (isAutoRotating && !isDragging && pumpGroup) {
            pumpGroup.rotation.y += 0.005;
        }

        // Apply vibration shake if telemetry detects high vibration
        if (current3DTelemetry.vib > 0.035 && pumpGroup) {
            pumpGroup.position.y = (Math.random() - 0.5) * (current3DTelemetry.vib * 2.2);
            pumpGroup.position.x = (Math.random() - 0.5) * (current3DTelemetry.vib * 2.2);
        } else if (pumpGroup) {
            pumpGroup.position.set(0, 0, 0);
        }

        pumpRenderer.render(pumpScene, pumpCamera);
    }
    render3DPump();
}

// ═════════════════════════════════════════════════════════════════════════════
// PHYSICAL HPU PHOTO SPEC & HOTSPOT HUD OVERLAY SYSTEM
// ═════════════════════════════════════════════════════════════════════════════

const hpuHotspots = [
    {
        key: 'motor_a',
        name: 'Drive Motor A (Primary)',
        top: '68%',
        left: '48%',
        type: 'warning',
        icon: 'fa-bolt',
        metrics: { rpm: '1,750 RPM', vib: '0.042 in/s (ALERT)', temp: '78.5 °C', load: '88%' },
        desc: 'Primary 45kW 3-Phase Electric Induction Motor. Elevated vibration frequency detected on front bearing.'
    },
    {
        key: 'motor_b',
        name: 'Drive Motor B (Secondary)',
        top: '62%',
        left: '72%',
        type: 'success',
        icon: 'fa-microchip',
        metrics: { rpm: '1,748 RPM', vib: '0.018 in/s (NOMINAL)', temp: '64.2 °C', load: '45%' },
        desc: 'Auxiliary 45kW Electric Motor. Operating in synchronized load-sharing mode with clean vibration harmonics.'
    },
    {
        key: 'reservoir',
        name: 'Hydraulic Oil Reservoir Skid',
        top: '52%',
        left: '26%',
        type: 'success',
        icon: 'fa-oil-can',
        metrics: { level: '82% (Nominal)', temp: '54.0 °C', ISO_clean: 'ISO 16/14/11', pressure: '185 Bar' },
        desc: '800-Liter Heavy Duty Steel Oil Reservoir Tank with integral sight glass and suction strainers.'
    },
    {
        key: 'panel',
        name: 'PLC & Electrical Control Cabinet',
        top: '36%',
        left: '84%',
        type: 'success',
        icon: 'fa-server',
        metrics: { voltage: '415 V (3-Phase)', current: '64 A', plc_status: 'ONLINE', bus: 'Modbus TCP' },
        desc: 'IP65 Rated Control Enclosure housing main circuit breakers, star-delta starters, and AI edge gateway.'
    },
    {
        key: 'cooler',
        name: 'Air Heat Exchanger & Fan Module',
        top: '18%',
        left: '44%',
        type: 'success',
        icon: 'fa-fan',
        metrics: { air_flow: '4,200 m³/h', fan_rpm: '1,450 RPM', delta_t: '-12.5 °C' },
        desc: 'Top-mounted air-to-oil heat exchanger unit with thermostatic fan control.'
    },
    {
        key: 'manifold',
        name: 'High-Pressure Hoses & Manifold',
        top: '32%',
        left: '32%',
        type: 'warning',
        icon: 'fa-diagram-project',
        metrics: { bar: '185 Bar', flow: '120 L/min', pulse: 'Low Ripple' },
        desc: 'Flexible wire-braided hydraulic pressure hoses with quick-disconnect test points.'
    }
];

function initHPUPhotoOverlay() {
    const container = document.getElementById('pump-3d-container');
    if (!container) return;

    let photoOverlay = document.getElementById('hpu-photo-overlay');
    if (!photoOverlay) {
        photoOverlay = document.createElement('div');
        photoOverlay.id = 'hpu-photo-overlay';
        photoOverlay.className = 'hpu-photo-overlay';
        photoOverlay.style.backgroundImage = 'url("static/hydraulic_power_unit.png")';
        photoOverlay.style.display = 'none';

        // Render Hotspot Pins
        hpuHotspots.forEach(spot => {
            const el = document.createElement('div');
            el.className = `hpu-hotspot ${spot.type}`;
            el.style.top = spot.top;
            el.style.left = spot.left;
            el.onclick = (e) => showHPUHotspotPopover(spot, e);

            el.innerHTML = `
                <div class="hpu-hotspot-pulse"></div>
                <div class="hpu-hotspot-pin"><i class="fa-solid ${spot.icon}"></i></div>
            `;
            photoOverlay.appendChild(el);
        });

        container.appendChild(photoOverlay);
    }
}

function showHPUHotspotPopover(spot, e) {
    e.stopPropagation();
    let old = document.getElementById('hpu-telemetry-popover');
    if (old) old.remove();

    const popover = document.createElement('div');
    popover.id = 'hpu-telemetry-popover';
    popover.className = 'hpu-telemetry-popover';

    const topNum = parseFloat(spot.top);
    const leftNum = parseFloat(spot.left);

    // Smart Y alignment: open downwards if near top (<45%), upwards if near bottom
    let translateY = '-105%';
    let posY = spot.top;
    if (topNum < 45) {
        translateY = '20px';
    }

    // Smart X alignment: shift right if near left edge, shift left if near right edge
    let translateX = '-50%';
    if (leftNum < 35) {
        translateX = '0%';
    } else if (leftNum > 65) {
        translateX = '-100%';
    }

    popover.style.top = posY;
    popover.style.left = spot.left;
    popover.style.transform = `translate(${translateX}, ${translateY})`;

    let metricsHTML = '';
    for (let [k, v] of Object.entries(spot.metrics)) {
        metricsHTML += `<div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;"><span style="color:var(--text-secondary); text-transform:capitalize;">${k.replace('_', ' ')}:</span><strong style="color:var(--accent);">${v}</strong></div>`;
    }

    popover.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; border-bottom:1px solid var(--card-border); padding-bottom:6px;">
            <strong style="font-size:12px; color:var(--text-primary);"><i class="fa-solid ${spot.icon}" style="color:var(--accent); margin-right:6px;"></i>${spot.name}</strong>
            <button onclick="document.getElementById('hpu-telemetry-popover').remove()" style="background:none; border:none; color:var(--text-secondary); cursor:pointer; font-size:14px; padding:2px 6px;"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <div style="margin-bottom:10px;">${metricsHTML}</div>
        <p style="font-size:10.5px; color:var(--text-secondary); line-height:1.4;">${spot.desc}</p>
    `;

    document.getElementById('pump-3d-container').appendChild(popover);
}

// Render Mode Toggle (Solid CAD, Hologram, Thermal Heatmap, Photo Spec, Split Dual Twin)
function set3DRenderMode(mode) {
    active3DMode = mode;
    const canvas = document.getElementById('pump-3d-canvas');
    const photoOverlay = document.getElementById('hpu-photo-overlay');

    // Update active button state styling
    document.querySelectorAll('.hpu-mode-btn').forEach(btn => {
        if (btn.getAttribute('data-mode') === mode) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    if (mode === 'photo') {
        if (canvas) canvas.style.display = 'none';
        if (photoOverlay) {
            photoOverlay.style.display = 'block';
            photoOverlay.style.width = '100%';
            photoOverlay.style.left = '0';
        }
        return;
    } else if (mode === 'split') {
        if (canvas) {
            canvas.style.display = 'block';
            canvas.style.width = '50%';
            canvas.style.float = 'left';
        }
        if (photoOverlay) {
            photoOverlay.style.display = 'block';
            photoOverlay.style.width = '50%';
            photoOverlay.style.left = '50%';
        }
        if (pumpRenderer && pumpCamera) {
            const container = document.getElementById('pump-3d-container');
            if (container) {
                pumpCamera.aspect = (container.clientWidth * 0.5) / container.clientHeight;
                pumpCamera.updateProjectionMatrix();
                pumpRenderer.setSize(container.clientWidth * 0.5, container.clientHeight);
            }
        }
        return;
    } else {
        if (canvas) {
            canvas.style.display = 'block';
            canvas.style.width = '100%';
        }
        if (photoOverlay) photoOverlay.style.display = 'none';
        if (pumpRenderer && pumpCamera) {
            const container = document.getElementById('pump-3d-container');
            if (container) {
                pumpCamera.aspect = container.clientWidth / container.clientHeight;
                pumpCamera.updateProjectionMatrix();
                pumpRenderer.setSize(container.clientWidth, container.clientHeight);
            }
        }
    }

    if (!pumpGroup) return;

    pumpGroup.traverse((child) => {
        if (child.isMesh && child.geometry.type !== 'SphereGeometry') {
            if (mode === 'hologram') {
                child.material = new THREE.MeshBasicMaterial({
                    color: 0x58a6ff,
                    wireframe: true,
                    transparent: true,
                    opacity: 0.6
                });
            } else if (mode === 'thermal') {
                const temp = current3DTelemetry.temp || 74;
                const isMotor = child === motorAMesh || child === motorBMesh;
                const heatColor = (isMotor && temp > 76) ? 0xf85149 : (temp > 70 ? 0xf5a623 : 0x3fb950);
                child.material = new THREE.MeshStandardMaterial({
                    color: heatColor,
                    emissive: heatColor,
                    emissiveIntensity: 0.45,
                    metalness: 0.4,
                    roughness: 0.4
                });
            } else {
                // Restore solid HPU colors
                const hpuBlueMat = new THREE.MeshStandardMaterial({ color: 0x0f52ba, metalness: 0.7, roughness: 0.35 });
                const steelMat = new THREE.MeshStandardMaterial({ color: 0xc4d1e2, metalness: 0.95, roughness: 0.15 });
                child.material = (child.geometry.type.includes('Cylinder') && child.scale.x < 1.0) ? steelMat : hpuBlueMat;
            }
        }
    });
}

// Toggle Auto Rotation
function toggle3DRotation() {
    isAutoRotating = !isAutoRotating;
    const btn = document.getElementById('btn-3d-rotate');
    if (btn) {
        btn.innerHTML = isAutoRotating ? '<i class="fa-solid fa-pause"></i> Pause' : '<i class="fa-solid fa-play"></i> Auto Rotate';
    }
}

// Update 3D Telemetry State from Dashboard
function update3DModelTelemetry(temp, vib, faultCode) {
    current3DTelemetry.temp = temp;
    current3DTelemetry.vib = vib;
    current3DTelemetry.fault = faultCode;

    if (fluidMesh) {
        const levelPct = current3DTelemetry.oil_level || 82;
        fluidMesh.scale.y = Math.max(0.2, levelPct / 100);
    }

    if (active3DMode === 'thermal') {
        set3DRenderMode('thermal');
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        initLanding3DBg();
        initPump3DViewer('pump-3d-canvas', 'pump-3d-container');
        initHPUPhotoOverlay();
    }, 200);
});
