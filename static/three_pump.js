// ═════════════════════════════════════════════════════════════════════════════
// THREE.JS 3D DIGITAL TWIN & LANDING PAGE VISUALIZER
// NMU AI Predictive Maintenance System — Cutaway Hydraulic Gear Pump Model
// ═════════════════════════════════════════════════════════════════════════════

let landingBgScene, landingBgCamera, landingBgRenderer, landingParticles;
let pumpScene, pumpCamera, pumpRenderer, pumpGroup, driveGearMesh, drivenGearMesh, fluidMesh;
let active3DMode = 'solid'; // 'solid', 'hologram', 'thermal'
let current3DTelemetry = { temp: 74, vib: 0.024, fault: 0 };
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

// Build 3D Technical Cutaway Gear Pump Procedural Model (Matching Technical Blueprint Image)
function build3DPumpModel() {
    pumpGroup = new THREE.Group();

    // ── Color Palette & Materials ──
    const darkNavyMat = new THREE.MeshStandardMaterial({
        color: 0x162842,
        metalness: 0.8,
        roughness: 0.3
    });

    const steelMat = new THREE.MeshStandardMaterial({
        color: 0xc4d1e2,
        metalness: 0.95,
        roughness: 0.15
    });

    const brassMat = new THREE.MeshStandardMaterial({
        color: 0xd4a017,
        metalness: 0.85,
        roughness: 0.25
    });

    const ghostWireMat = new THREE.MeshBasicMaterial({
        color: 0x58a6ff,
        wireframe: true,
        transparent: true,
        opacity: 0.4
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
        opacity: 0.7,
        roughness: 0.2
    });

    // 1. FRONT SQUARE MOUNTING FLANGE (WITH 4 CORNER BOLT HOLES)
    const flangeShape = new THREE.Shape();
    const w = 2.4, h = 2.4, r = 0.3;
    flangeShape.moveTo(-w + r, -h);
    flangeShape.lineTo(w - r, -h);
    flangeShape.quadraticCurveTo(w, -h, w, -h + r);
    flangeShape.lineTo(w, h - r);
    flangeShape.quadraticCurveTo(w, h, w - r, h);
    flangeShape.lineTo(-w + r, h);
    flangeShape.quadraticCurveTo(-w, h, -w, h - r);
    flangeShape.lineTo(-w, -h + r);
    flangeShape.quadraticCurveTo(-w, -h, -w + r, -h);

    const extrudeSettings = { depth: 0.4, bevelEnabled: true, bevelSegments: 3, steps: 1, bevelSize: 0.08, bevelThickness: 0.08 };
    const flangeGeo = new THREE.ExtrudeGeometry(flangeShape, extrudeSettings);
    const flangeMesh = new THREE.Mesh(flangeGeo, darkNavyMat);
    flangeMesh.position.set(0, 0, 3.2);
    pumpGroup.add(flangeMesh);

    // 4 Corner Bolt Holes
    const holePos = [[-1.8, -1.8], [1.8, -1.8], [-1.8, 1.8], [1.8, 1.8]];
    holePos.forEach(([hx, hy]) => {
        const holeGeo = new THREE.CylinderGeometry(0.28, 0.28, 0.6, 16);
        const holeMesh = new THREE.Mesh(holeGeo, steelMat);
        holeMesh.position.set(hx, hy, 3.4);
        holeMesh.rotation.x = Math.PI / 2;
        pumpGroup.add(holeMesh);
    });

    // Concentric Circular Hub Rings on Front Flange
    for (let rVal of [1.6, 1.1]) {
        const ringGeo = new THREE.TorusGeometry(rVal, 0.08, 16, 32);
        const ringMesh = new THREE.Mesh(ringGeo, steelMat);
        ringMesh.position.set(0, 0, 3.65);
        pumpGroup.add(ringMesh);
    }

    // 2. DRIVE SHAFT WITH KEYWAY SLOT
    const shaftGeo = new THREE.CylinderGeometry(0.55, 0.55, 2.6, 32);
    const shaftMesh = new THREE.Mesh(shaftGeo, steelMat);
    shaftMesh.position.set(0, 0, 4.5);
    shaftMesh.rotation.x = Math.PI / 2;
    pumpGroup.add(shaftMesh);

    // Keyway Drive Slot
    const keywayGeo = new THREE.BoxGeometry(0.18, 0.2, 1.0);
    const keywayMesh = new THREE.Mesh(keywayGeo, brassMat);
    keywayMesh.position.set(0, 0.55, 4.5);
    pumpGroup.add(keywayMesh);

    // 3. CUTAWAY PUMP HOUSING (3/4 SOLID, 1/4 CUTAWAY EXPOSING GEARS)
    const housingGeo = new THREE.CylinderGeometry(2.2, 2.2, 5.2, 32, 1, false, 0, Math.PI * 1.45);
    const housingMesh = new THREE.Mesh(housingGeo, darkNavyMat);
    housingMesh.position.set(0, 0, 0.6);
    housingMesh.rotation.x = Math.PI / 2;
    housingMesh.rotation.y = Math.PI * 0.15;
    pumpGroup.add(housingMesh);

    // Ghosted Wireframe Casing (matching dotted blueprint lines in image)
    const ghostGeo = new THREE.CylinderGeometry(2.22, 2.22, 5.22, 24);
    const ghostMesh = new THREE.Mesh(ghostGeo, ghostWireMat);
    ghostMesh.position.set(0, 0, 0.6);
    ghostMesh.rotation.x = Math.PI / 2;
    pumpGroup.add(ghostMesh);

    // Rear Mounting Flange Plate
    const rearFlangeMesh = new THREE.Mesh(flangeGeo, darkNavyMat);
    rearFlangeMesh.position.set(0, 0, -2.2);
    pumpGroup.add(rearFlangeMesh);

    // Side Mounting Bracket Feet
    const footGeo = new THREE.BoxGeometry(1.0, 0.5, 1.6);
    const footLeft = new THREE.Mesh(footGeo, darkNavyMat);
    footLeft.position.set(-1.8, -2.1, 0.6);
    pumpGroup.add(footLeft);

    // Side Suction Port (Inlet Opening)
    const portGeo = new THREE.CylinderGeometry(0.7, 0.7, 0.8, 24);
    const portMesh = new THREE.Mesh(portGeo, steelMat);
    portMesh.position.set(-2.0, 0, 1.2);
    portMesh.rotation.z = Math.PI / 2;
    pumpGroup.add(portMesh);

    // 4. INTERNAL INTERMESHING PRECISION GEARS (VISIBLE THROUGH CUTAWAY)
    function createGear(radius, teeth, depth) {
        const gearGroup = new THREE.Group();
        const coreGeo = new THREE.CylinderGeometry(radius, radius, depth, 32);
        const coreMesh = new THREE.Mesh(coreGeo, steelMat);
        coreMesh.rotation.x = Math.PI / 2;
        gearGroup.add(coreMesh);

        for (let i = 0; i < teeth; i++) {
            const angle = (i / teeth) * Math.PI * 2;
            const toothGeo = new THREE.BoxGeometry(0.18, 0.35, depth);
            const toothMesh = new THREE.Mesh(toothGeo, brassMat);
            toothMesh.position.set(Math.cos(angle) * radius, Math.sin(angle) * radius, 0);
            toothMesh.rotation.z = angle;
            gearGroup.add(toothMesh);
        }
        return gearGroup;
    }

    driveGearMesh = createGear(0.9, 14, 1.4);
    driveGearMesh.position.set(0, 0.5, 0.6);
    pumpGroup.add(driveGearMesh);

    drivenGearMesh = createGear(0.9, 14, 1.4);
    drivenGearMesh.position.set(0, -0.6, 0.6);
    pumpGroup.add(drivenGearMesh);

    // Inner Shaft connecting drive gear
    const innerShaftGeo = new THREE.CylinderGeometry(0.35, 0.35, 4.5, 24);
    const innerShaftMesh = new THREE.Mesh(innerShaftGeo, steelMat);
    innerShaftMesh.position.set(0, 0.5, 0.8);
    innerShaftMesh.rotation.x = Math.PI / 2;
    pumpGroup.add(innerShaftMesh);

    // 5. FLUID RESERVOIR TANK & SOLENOID ASSEMBLY (LEFT SIDE)
    const tankGroup = new THREE.Group();

    // Outer Glass Tank
    const tankGeo = new THREE.BoxGeometry(2.6, 1.8, 3.2);
    const tankMesh = new THREE.Mesh(tankGeo, glassMat);
    tankGroup.add(tankMesh);

    // Wireframe Tank Outline
    const tankWire = new THREE.Mesh(tankGeo, ghostWireMat);
    tankGroup.add(tankWire);

    // Inner Fluid Level
    const fluidGeo = new THREE.BoxGeometry(2.5, 1.1, 3.1);
    fluidMesh = new THREE.Mesh(fluidGeo, fluidMat);
    fluidMesh.position.set(0, -0.3, 0);
    tankGroup.add(fluidMesh);

    // Vertical Dip Tube inside tank
    const tubeGeo = new THREE.CylinderGeometry(0.18, 0.18, 1.6, 16);
    const tubeMesh = new THREE.Mesh(tubeGeo, steelMat);
    tubeMesh.position.set(-0.4, 0.1, 0);
    tankGroup.add(tubeMesh);

    // Solenoid Control Valve mounted on top of tank
    const solenoidGeo = new THREE.CylinderGeometry(0.4, 0.4, 1.2, 24);
    const solenoidMesh = new THREE.Mesh(solenoidGeo, darkNavyMat);
    solenoidMesh.position.set(-0.4, 1.4, 0);
    tankGroup.add(solenoidMesh);

    const capGeo = new THREE.CylinderGeometry(0.45, 0.45, 0.2, 24);
    const capMesh = new THREE.Mesh(capGeo, steelMat);
    capMesh.position.set(-0.4, 2.1, 0);
    tankGroup.add(capMesh);

    // Fluid Hose connecting Tank to Pump Inlet Port
    const hosePoints = [
        new THREE.Vector3(-0.4, 1.4, 0),
        new THREE.Vector3(-2.4, 1.4, 0),
        new THREE.Vector3(-3.8, 0, 1.2)
    ];
    const curve = new THREE.CatmullRomCurve3(hosePoints);
    const hoseGeo = new THREE.TubeGeometry(curve, 20, 0.14, 8, false);
    const hoseMesh = new THREE.Mesh(hoseGeo, steelMat);
    tankGroup.add(hoseMesh);

    tankGroup.position.set(-5.2, -1.0, 0.6);
    pumpGroup.add(tankGroup);

    // 6. TELEMETRY HOTSPOT CALLOUT NODES (MATCHING BLUEPRINT IMAGE)
    const nodesData = [
        { name: 'Drive Shaft Keyway', pos: [0, 0.6, 4.6], color: 0x58a6ff },
        { name: 'Internal Gear Mesh (Vibration Target)', pos: [0, 0.4, 0.6], color: 0xf85149 },
        { name: 'Pump Volute Chamber', pos: [0, 1.8, -0.6], color: 0x3fb950 },
        { name: 'Fluid Reservoir & Solenoid', pos: [-5.2, 0.6, 0.6], color: 0xf5a623 }
    ];

    nodesData.forEach(n => {
        const nodeGeo = new THREE.SphereGeometry(0.28, 16, 16);
        const nodeMat = new THREE.MeshBasicMaterial({ color: n.color });
        const nodeMesh = new THREE.Mesh(nodeGeo, nodeMat);
        nodeMesh.position.set(...n.pos);
        nodeMesh.userData = { name: n.name };
        pumpGroup.add(nodeMesh);

        // Ring pulse around node
        const ringGeo = new THREE.TorusGeometry(0.45, 0.04, 16, 32);
        const ringMat = new THREE.MeshBasicMaterial({ color: n.color, transparent: true, opacity: 0.7 });
        const ringMesh = new THREE.Mesh(ringGeo, ringMat);
        ringMesh.position.set(...n.pos);
        ringMesh.rotation.x = Math.PI / 2;
        pumpGroup.add(ringMesh);
    });

    return pumpGroup;
}

// Initialize 3D Pump Viewer in specified canvas
function initPump3DViewer(canvasId, containerId) {
    const canvas = document.getElementById(canvasId);
    const container = document.getElementById(containerId);
    if (!canvas || !container || !window.THREE) return;

    pumpScene = new THREE.Scene();
    pumpCamera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    pumpCamera.position.set(9, 6, 12);

    pumpRenderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    pumpRenderer.setSize(container.clientWidth, container.clientHeight);
    pumpRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Studio Technical Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    pumpScene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x58a6ff, 1.4);
    dirLight1.position.set(12, 18, 12);
    pumpScene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xbc8cff, 0.8);
    dirLight2.position.set(-12, -10, -12);
    pumpScene.add(dirLight2);

    // Build Model
    const model = build3DPumpModel();
    pumpScene.add(model);
    pumpCamera.lookAt(-1, 0, 1);

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
        pumpCamera.position.z = Math.max(6, Math.min(22, pumpCamera.position.z));
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

// Render Mode Toggle
function set3DRenderMode(mode) {
    active3DMode = mode;
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
                const temp = current3DTelemetry.temp || 70;
                const heatColor = temp > 88 ? 0xf85149 : (temp > 80 ? 0xf5a623 : 0x3fb950);
                child.material = new THREE.MeshStandardMaterial({
                    color: heatColor,
                    emissive: heatColor,
                    emissiveIntensity: 0.4,
                    metalness: 0.4,
                    roughness: 0.4
                });
            } else {
                // Restore solid
                const darkNavyMat = new THREE.MeshStandardMaterial({ color: 0x162842, metalness: 0.8, roughness: 0.3 });
                const steelMat = new THREE.MeshStandardMaterial({ color: 0xc4d1e2, metalness: 0.95, roughness: 0.15 });
                child.material = (child.geometry.type.includes('Cylinder') && child.scale.x < 1.0) ? steelMat : darkNavyMat;
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
    current3DTelemetry = { temp, vib, fault: faultCode };

    if (fluidMesh) {
        // Adjust fluid height based on oil/coolant level
        const levelPct = current3DTelemetry.oil || 60;
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
        initPump3DViewer('dash-pump-3d-canvas', 'dash-pump-3d-container');
    }, 200);
});
