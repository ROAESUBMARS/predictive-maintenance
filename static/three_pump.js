// ═════════════════════════════════════════════════════════════════════════════
// THREE.JS 3D DIGITAL TWIN & LANDING PAGE VISUALIZER
// NMU AI Predictive Maintenance System
// ═════════════════════════════════════════════════════════════════════════════

let landingBgScene, landingBgCamera, landingBgRenderer, landingParticles;
let pumpScene, pumpCamera, pumpRenderer, pumpGroup, impellerGroup;
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

    const particleCount = 750;
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
        size: 3.5,
        vertexColors: true,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending
    });

    landingParticles = new THREE.Points(geometry, material);
    landingBgScene.add(landingParticles);

    let mouseX = 0, mouseY = 0;
    window.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX - window.innerWidth / 2) * 0.12;
        mouseY = (e.clientY - window.innerHeight / 2) * 0.12;
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

// Build 3D Hydraulic Pump Procedural Geometry
function build3DPumpModel() {
    pumpGroup = new THREE.Group();

    // Base Materials
    const bodyMat = new THREE.MeshStandardMaterial({
        color: 0x1f293d,
        metalness: 0.85,
        roughness: 0.25
    });

    const chromeMat = new THREE.MeshStandardMaterial({
        color: 0xd0d7de,
        metalness: 0.95,
        roughness: 0.1
    });

    const brassMat = new THREE.MeshStandardMaterial({
        color: 0xd4a017,
        metalness: 0.8,
        roughness: 0.3
    });

    const glowBlueMat = new THREE.MeshStandardMaterial({
        color: 0x58a6ff,
        emissive: 0x58a6ff,
        emissiveIntensity: 0.5,
        metalness: 0.5,
        roughness: 0.5
    });

    // 1. Motor Main Body (Cylinder)
    const motorGeo = new THREE.CylinderGeometry(2.0, 2.0, 5.0, 32);
    const motorMesh = new THREE.Mesh(motorGeo, bodyMat);
    motorMesh.position.x = -2.5;
    motorMesh.rotation.z = Math.PI / 2;
    pumpGroup.add(motorMesh);

    // Motor Cooling Fins (Array of Torus rings)
    for (let i = -2; i <= 2; i += 0.5) {
        const finGeo = new THREE.TorusGeometry(2.1, 0.07, 16, 32);
        const finMesh = new THREE.Mesh(finGeo, chromeMat);
        finMesh.position.x = -2.5 + i;
        finMesh.rotation.y = Math.PI / 2;
        pumpGroup.add(finMesh);
    }

    // Terminal Conduit Box
    const boxGeo = new THREE.BoxGeometry(1.4, 0.8, 1.4);
    const boxMesh = new THREE.Mesh(boxGeo, bodyMat);
    boxMesh.position.set(-2.5, 2.2, 0);
    pumpGroup.add(boxMesh);

    // 2. Shaft Housing & Coupling
    const shaftHousingGeo = new THREE.CylinderGeometry(1.3, 1.7, 1.8, 32);
    const shaftHousingMesh = new THREE.Mesh(shaftHousingGeo, chromeMat);
    shaftHousingMesh.position.x = 1.0;
    shaftHousingMesh.rotation.z = Math.PI / 2;
    pumpGroup.add(shaftHousingMesh);

    // 3. Volute Casing (Main Pump Housing)
    const voluteGeo = new THREE.TorusGeometry(2.0, 1.1, 24, 32);
    const voluteMesh = new THREE.Mesh(voluteGeo, bodyMat);
    voluteMesh.position.x = 2.8;
    voluteMesh.rotation.y = Math.PI / 2;
    pumpGroup.add(voluteMesh);

    // Volute Front Cover Plate
    const capGeo = new THREE.CylinderGeometry(2.0, 2.0, 0.5, 32);
    const capMesh = new THREE.Mesh(capGeo, brassMat);
    capMesh.position.x = 3.7;
    capMesh.rotation.z = Math.PI / 2;
    pumpGroup.add(capMesh);

    // 4. Suction Pipe (Inlet Manifold)
    const suctionGeo = new THREE.CylinderGeometry(0.9, 0.9, 2.0, 24);
    const suctionMesh = new THREE.Mesh(suctionGeo, chromeMat);
    suctionMesh.position.set(4.6, 0, 0);
    suctionMesh.rotation.z = Math.PI / 2;
    pumpGroup.add(suctionMesh);

    // Suction Flange Ring
    const flange1Geo = new THREE.TorusGeometry(1.1, 0.15, 16, 24);
    const flange1Mesh = new THREE.Mesh(flange1Geo, brassMat);
    flange1Mesh.position.set(5.4, 0, 0);
    flange1Mesh.rotation.y = Math.PI / 2;
    pumpGroup.add(flange1Mesh);

    // 5. Discharge Pipe (Top Vertical Outlet)
    const dischargeGeo = new THREE.CylinderGeometry(0.8, 0.8, 2.2, 24);
    const dischargeMesh = new THREE.Mesh(dischargeGeo, chromeMat);
    dischargeMesh.position.set(2.8, 2.2, 0);
    pumpGroup.add(dischargeMesh);

    // Discharge Flange Ring
    const flange2Geo = new THREE.TorusGeometry(1.0, 0.15, 16, 24);
    const flange2Mesh = new THREE.Mesh(flange2Geo, brassMat);
    flange2Mesh.position.set(2.8, 3.2, 0);
    flange2Mesh.rotation.x = Math.PI / 2;
    pumpGroup.add(flange2Mesh);

    // 6. Heavy Duty Steel Baseplate
    const baseGeo = new THREE.BoxGeometry(9.8, 0.4, 4.6);
    const baseMesh = new THREE.Mesh(baseGeo, bodyMat);
    baseMesh.position.set(0.5, -2.4, 0);
    pumpGroup.add(baseMesh);

    // 7. Rotating Internal Impeller
    impellerGroup = new THREE.Group();
    for (let b = 0; b < 6; b++) {
        const bladeGeo = new THREE.BoxGeometry(0.18, 1.4, 0.35);
        const bladeMesh = new THREE.Mesh(bladeGeo, glowBlueMat);
        bladeMesh.rotation.x = (b * Math.PI) / 3;
        bladeMesh.position.z = Math.sin((b * Math.PI) / 3) * 0.7;
        bladeMesh.position.y = Math.cos((b * Math.PI) / 3) * 0.7;
        impellerGroup.add(bladeMesh);
    }
    impellerGroup.position.set(2.8, 0, 0);
    pumpGroup.add(impellerGroup);

    // 8. Glowing Telemetry Nodes (Hotspots)
    const nodesData = [
        { name: 'Motor Bearings', pos: [-2.5, 2.4, 0], color: 0x58a6ff },
        { name: 'Volute Chamber', pos: [2.8, 0, 2.1], color: 0x3fb950 },
        { name: 'Discharge Valve', pos: [2.8, 3.4, 0], color: 0x58a6ff },
        { name: 'Mechanical Seal', pos: [1.0, 0, 1.4], color: 0xf5a623 }
    ];

    nodesData.forEach(n => {
        const nodeGeo = new THREE.SphereGeometry(0.3, 16, 16);
        const nodeMat = new THREE.MeshBasicMaterial({ color: n.color });
        const nodeMesh = new THREE.Mesh(nodeGeo, nodeMat);
        nodeMesh.position.set(...n.pos);
        nodeMesh.userData = { name: n.name };
        pumpGroup.add(nodeMesh);
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
    pumpCamera.position.set(7, 5, 11);

    pumpRenderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    pumpRenderer.setSize(container.clientWidth, container.clientHeight);
    pumpRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    pumpScene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x58a6ff, 1.3);
    dirLight1.position.set(10, 15, 10);
    pumpScene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xbc8cff, 0.9);
    dirLight2.position.set(-10, -10, -10);
    pumpScene.add(dirLight2);

    // Build Pump Model
    const model = build3DPumpModel();
    pumpScene.add(model);
    pumpCamera.lookAt(0, 0, 0);

    // Orbit Controls via Mouse Drag
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

        pumpGroup.rotation.y += deltaX * 0.01;
        pumpGroup.rotation.x += deltaY * 0.01;

        previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    // Zoom on wheel
    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        pumpCamera.position.z += e.deltaY * 0.01;
        pumpCamera.position.z = Math.max(5, Math.min(20, pumpCamera.position.z));
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

        if (impellerGroup) {
            impellerGroup.rotation.x += 0.08;
        }

        if (isAutoRotating && !isDragging && pumpGroup) {
            pumpGroup.rotation.y += 0.006;
        }

        // Apply vibration shake if telemetry detects high vibration
        if (current3DTelemetry.vib > 0.035 && pumpGroup) {
            pumpGroup.position.y = (Math.random() - 0.5) * (current3DTelemetry.vib * 2.5);
            pumpGroup.position.x = (Math.random() - 0.5) * (current3DTelemetry.vib * 2.5);
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
                // Solid Mode - Re-create solid materials
                const bodyMat = new THREE.MeshStandardMaterial({ color: 0x1f293d, metalness: 0.85, roughness: 0.25 });
                const chromeMat = new THREE.MeshStandardMaterial({ color: 0xd0d7de, metalness: 0.95, roughness: 0.1 });
                const brassMat = new THREE.MeshStandardMaterial({ color: 0xd4a017, metalness: 0.8, roughness: 0.3 });
                child.material = (child.geometry.type.includes('Torus') || child.geometry.type.includes('Cylinder') && child.position.x > 3) ? chromeMat : bodyMat;
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
