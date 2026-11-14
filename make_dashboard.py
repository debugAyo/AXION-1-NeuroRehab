import json
import os

def create_dashboard():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "output", "axion_live_commands.json")
    out_html = os.path.join(base_dir, "test_task_b_dashboard.html")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    json_str = json.dumps(data)
    total_steps = len(data) - 1

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AXION-1: 3D Adaptive Neuro-Mirroring Interface</title>
    <!-- Three.js + OrbitControls for True 3D Visualization -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #070d19; color: #f8fafc; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 15px; margin-bottom: 20px; }}
        h1 {{ font-size: 22px; font-weight: 800; color: #38bdf8; letter-spacing: -0.5px; }}
        .subtitle {{ font-size: 13px; color: #94a3b8; margin-top: 3px; }}
        .grid {{ display: grid; grid-template-columns: 1.3fr 1fr; gap: 20px; margin-bottom: 20px; }}
        .card {{ background: #0f172a; border-radius: 12px; padding: 20px; border: 1px solid #1e293b; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }}
        .status-badge {{ display: inline-flex; align-items: center; padding: 6px 16px; border-radius: 9999px; font-weight: 800; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .status-active {{ background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid #22c55e; }}
        .status-degraded {{ background: rgba(234, 179, 8, 0.15); color: #facc15; border: 1px solid #eab308; }}
        .status-paused {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #ef4444; }}
        .meter-container {{ margin: 18px 0; }}
        .meter-header {{ display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 7px; color: #cbd5e1; font-weight: 600; }}
        .meter-bar {{ height: 14px; background: #1e293b; border-radius: 7px; overflow: hidden; display: flex; }}
        .meter-fill-eeg {{ background: linear-gradient(90deg, #0284c7, #38bdf8); transition: width 0.15s ease; }}
        .meter-fill-emg {{ background: linear-gradient(90deg, #ea580c, #f97316); transition: width 0.15s ease; }}
        .three-box {{ width: 100%; height: 340px; background: #050914; border-radius: 10px; border: 1px solid #1e293b; position: relative; overflow: hidden; }}
        #three-canvas {{ width: 100%; height: 100%; display: block; cursor: grab; }}
        #three-canvas:active {{ cursor: grabbing; }}
        .hint-3d {{ position: absolute; bottom: 10px; left: 12px; font-size: 11px; color: #64748b; pointer-events: none; background: rgba(15,23,42,0.7); padding: 3px 8px; border-radius: 4px; }}
        .controls {{ display: flex; align-items: center; gap: 15px; background: #0f172a; padding: 15px 20px; border-radius: 12px; border: 1px solid #1e293b; }}
        button {{ background: #38bdf8; color: #0b1120; border: none; padding: 10px 22px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: all 0.2s; font-size: 13px; }}
        button:hover {{ background: #7dd3fc; }}
        input[type=range] {{ flex: 1; accent-color: #38bdf8; cursor: pointer; }}
        .time-label {{ font-family: monospace; font-size: 16px; font-weight: 700; color: #38bdf8; min-width: 75px; text-align: right; }}
        .metric-val {{ font-size: 28px; font-weight: 800; font-family: monospace; margin-top: 4px; }}
        .intent-badge {{ font-size: 20px; font-weight: 800; color: #38bdf8; background: #050914; padding: 4px 14px; border-radius: 6px; border: 1px solid #1e293b; }}
        .reason-box {{ margin-top: 10px; font-size: 12px; color: #94a3b8; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>AXION-1: 3D Neuro-Mirroring Interface</h1>
                <div class="subtitle">NeuralVillage Neurotech Hackathon 2026 · True 3D Action Observation Therapy Simulation</div>
            </div>
            <div id="status-pill" class="status-badge status-active">ACTIVE</div>
        </header>

        <div class="grid">
            <!-- 3D WebGL Simulation Box -->
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="font-weight:700; font-size:13px; color:#94a3b8; text-transform:uppercase;">3D Robotic / Mirroring Arm</span>
                    <span id="intent-text" class="intent-badge">FLEX</span>
                </div>
                <div class="three-box">
                    <canvas id="three-canvas"></canvas>
                    <div class="hint-3d">🖱️ Click & Drag to Orbit in 3D | Scroll to Zoom</div>
                </div>
                <div id="status-reason" class="reason-box">Nominal multimodal operation</div>
            </div>

            <!-- Dynamic Fusion & Metrics -->
            <div class="card">
                <div style="font-weight:700; font-size:13px; color:#94a3b8; text-transform:uppercase; margin-bottom:15px;">Dynamic Confidence Weights</div>
                
                <div class="meter-container">
                    <div class="meter-header">
                        <span>🧠 Brain (EEG) Weight</span>
                        <span id="eeg-pct" style="color:#38bdf8;">58%</span>
                    </div>
                    <div class="meter-bar"><div id="eeg-bar" class="meter-fill-eeg" style="width: 58%;"></div></div>
                </div>

                <div class="meter-container">
                    <div class="meter-header">
                        <span>⚡ Muscle (EMG) Weight</span>
                        <span id="emg-pct" style="color:#f97316;">42%</span>
                    </div>
                    <div class="meter-bar"><div id="emg-bar" class="meter-fill-emg" style="width: 42%;"></div></div>
                </div>

                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; margin-top:25px;">
                    <div style="background:#050914; padding:15px; border-radius:8px; border:1px solid #1e293b;">
                        <div style="font-size:11px; font-weight:700; color:#94a3b8;">CONFIDENCE</div>
                        <div id="conf-val" class="metric-val" style="color:#38bdf8;">0.88</div>
                    </div>
                    <div style="background:#050914; padding:15px; border-radius:8px; border:1px solid #1e293b;">
                        <div style="font-size:11px; font-weight:700; color:#94a3b8;">ELBOW ANGLE</div>
                        <div id="elbow-val" class="metric-val" style="color:#c084fc;">90°</div>
                    </div>
                </div>

                <div style="margin-top:20px; padding:12px; background:#050914; border-radius:8px; border:1px solid #1e293b; font-size:12px; color:#94a3b8; line-height:1.5;">
                    💡 <strong>Action Observation Therapy (AOT):</strong> The 3D avatar executes perfect, biomechanically smooth motor patterns to activate the patient's mirror neuron system and drive neuroplastic recovery.
                </div>
            </div>
        </div>

        <!-- Controls -->
        <div class="controls">
            <button id="play-btn" onclick="togglePlay()">PAUSE</button>
            <input type="range" id="scrub" min="0" max="{total_steps}" value="0" oninput="onScrub(this.value)">
            <span id="time-display" class="time-label">0.0 s</span>
            <select id="speed-select" style="background:#050914; color:#f8fafc; border:1px solid #1e293b; padding:8px 12px; border-radius:6px; font-weight:600;" onchange="speed = parseFloat(this.value)">
                <option value="1">1x Speed</option>
                <option value="2" selected>2x Speed</option>
                <option value="4">4x Speed</option>
            </select>
        </div>
    </div>

    <script>
        const commands = {json_str};
        let currentIndex = 0;
        let isPlaying = true;
        let speed = 2.0;

        // --- THREE.JS 3D SCENE SETUP ---
        const canvas = document.getElementById('three-canvas');
        const box = canvas.parentElement;
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x050914);

        const camera = new THREE.PerspectiveCamera(45, box.clientWidth / box.clientHeight, 0.1, 100);
        camera.position.set(2.8, 1.8, 2.8);

        const renderer = new THREE.WebGLRenderer({{ canvas: canvas, antialias: true }});
        renderer.setSize(box.clientWidth, box.clientHeight);
        renderer.shadowMap.enabled = true;

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.target.set(0, 0.7, 0);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
        dirLight.position.set(5, 10, 7);
        dirLight.castShadow = true;
        scene.add(dirLight);

        const statusLight = new THREE.PointLight(0x38bdf8, 2, 5);
        statusLight.position.set(0, 1.5, 0.5);
        scene.add(statusLight);

        // Grid Floor
        const grid = new THREE.GridHelper(6, 20, 0x1e293b, 0x0f172a);
        grid.position.y = 0;
        scene.add(grid);

        // Materials
        const baseMat = new THREE.MeshStandardMaterial({{ color: 0x334155, roughness: 0.4, metalness: 0.6 }});
        const limbMat = new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.3, metalness: 0.7 }});
        const jointMat = new THREE.MeshStandardMaterial({{ color: 0x38bdf8, roughness: 0.2, metalness: 0.8, emissive: 0x0284c7, emissiveIntensity: 0.2 }});
        const handMat = new THREE.MeshStandardMaterial({{ color: 0xf8fafc, roughness: 0.3, metalness: 0.5 }});

        // 1. Pedestal Base
        const baseGeom = new THREE.CylinderGeometry(0.35, 0.45, 0.2, 32);
        const baseMesh = new THREE.Mesh(baseGeom, baseMat);
        baseMesh.position.y = 0.1;
        scene.add(baseMesh);

        // 2. Shoulder Pivot
        const shoulderJoint = new THREE.Group();
        shoulderJoint.position.set(0, 0.2, 0);
        scene.add(shoulderJoint);

        const shoulderGeom = new THREE.SphereGeometry(0.18, 32, 32);
        const shoulderMesh = new THREE.Mesh(shoulderGeom, baseMat);
        shoulderJoint.add(shoulderMesh);

        // 3. Upper Arm Link
        const upperArmGroup = new THREE.Group();
        shoulderJoint.add(upperArmGroup);

        const upperArmGeom = new THREE.CylinderGeometry(0.1, 0.12, 0.9, 32);
        const upperArmMesh = new THREE.Mesh(upperArmGeom, limbMat);
        upperArmMesh.position.y = 0.45;
        upperArmGroup.add(upperArmMesh);

        // 4. Elbow Joint
        const elbowJoint = new THREE.Group();
        elbowJoint.position.set(0, 0.9, 0);
        upperArmGroup.add(elbowJoint);

        const elbowGeom = new THREE.SphereGeometry(0.14, 32, 32);
        const elbowMesh = new THREE.Mesh(elbowGeom, jointMat);
        elbowJoint.add(elbowMesh);

        // 5. Forearm Link
        const forearmGroup = new THREE.Group();
        elbowJoint.add(forearmGroup);

        const forearmGeom = new THREE.CylinderGeometry(0.08, 0.1, 0.8, 32);
        const forearmMesh = new THREE.Mesh(forearmGeom, limbMat);
        forearmMesh.position.y = 0.4;
        forearmGroup.add(forearmMesh);

        // 6. Wrist & 3D Hand
        const handGroup = new THREE.Group();
        handGroup.position.set(0, 0.8, 0);
        forearmGroup.add(handGroup);

        const palmGeom = new THREE.BoxGeometry(0.16, 0.18, 0.08);
        const palmMesh = new THREE.Mesh(palmGeom, handMat);
        handGroup.add(palmMesh);

        // Fingers (3D Prosthetic gripper)
        for (let i = -1; i <= 1; i++) {{
            const fingerGeom = new THREE.CylinderGeometry(0.02, 0.02, 0.14, 16);
            const fingerMesh = new THREE.Mesh(fingerGeom, jointMat);
            fingerMesh.position.set(i * 0.05, 0.15, 0);
            handGroup.add(fingerMesh);
        }}

        // Default initial resting posture
        upperArmGroup.rotation.z = -0.3; // Angle outward slightly
        upperArmGroup.rotation.x = -0.2;

        let targetElbowRad = 0;
        let currentElbowRad = 0;

        function animate3D() {{
            requestAnimationFrame(animate3D);

            // Smooth interpolation towards target joint angle
            currentElbowRad += (targetElbowRad - currentElbowRad) * 0.12;
            forearmGroup.rotation.z = currentElbowRad;

            controls.update();
            renderer.render(scene, camera);
        }}
        animate3D();

        window.addEventListener('resize', () => {{
            camera.aspect = box.clientWidth / box.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(box.clientWidth, box.clientHeight);
        }});

        // --- DASHBOARD UI UPDATES ---
        function updateUI(idx) {{
            const cmd = commands[idx];
            document.getElementById('time-display').innerText = cmd.timestamp.toFixed(1) + ' s';
            document.getElementById('scrub').value = idx;

            const pill = document.getElementById('status-pill');
            pill.className = 'status-badge status-' + cmd.safety_status.toLowerCase();
            pill.innerText = cmd.safety_status;

            document.getElementById('status-reason').innerText = cmd.status_reason;
            document.getElementById('intent-text').innerText = cmd.intent;

            const eegP = Math.round(cmd.source_weights.eeg * 100);
            const emgP = Math.round(cmd.source_weights.emg * 100);
            document.getElementById('eeg-pct').innerText = eegP + '%';
            document.getElementById('eeg-bar').style.width = eegP + '%';
            document.getElementById('emg-pct').innerText = emgP + '%';
            document.getElementById('emg-bar').style.width = emgP + '%';

            document.getElementById('conf-val').innerText = cmd.confidence.toFixed(2);
            document.getElementById('elbow-val').innerText = cmd.joint_angles_deg.elbow.toFixed(0) + '°';

            // Convert elbow degrees to 3D rotation radians
            const deg = cmd.joint_angles_deg.elbow;
            targetElbowRad = -(deg * Math.PI / 180);

            // Update 3D joint and lighting color according to status
            if (cmd.safety_status === 'ACTIVE') {{
                jointMat.color.setHex(0x38bdf8);
                jointMat.emissive.setHex(0x0284c7);
                statusLight.color.setHex(0x38bdf8);
            }} else if (cmd.safety_status === 'DEGRADED') {{
                jointMat.color.setHex(0xfacc15);
                jointMat.emissive.setHex(0xca8a04);
                statusLight.color.setHex(0xfacc15);
            }} else {{
                jointMat.color.setHex(0xf87171);
                jointMat.emissive.setHex(0xdc2626);
                statusLight.color.setHex(0xf87171);
            }}
        }}

        function step() {{
            if (!isPlaying) return;
            currentIndex = (currentIndex + 1) % commands.length;
            updateUI(currentIndex);
            setTimeout(step, (500 / speed));
        }}

        function togglePlay() {{
            isPlaying = !isPlaying;
            document.getElementById('play-btn').innerText = isPlaying ? 'PAUSE' : 'PLAY';
            if (isPlaying) step();
        }}

        function onScrub(val) {{
            currentIndex = parseInt(val);
            updateUI(currentIndex);
        }}

        updateUI(0);
        step();
    </script>
</body>
</html>
"""

    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)

    print("[✓] True 3D WebGL Dashboard created at:", out_html)

if __name__ == "__main__":
    create_dashboard()
