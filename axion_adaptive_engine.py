"""
AXION-1: Task B — Real-Time Adaptive Fusion Engine & Safety State Machine
NeuralVillage Neurotech Hackathon 2026

Core Innovation:
  Dynamically evaluates EEG and EMG confidence scores. When muscle fatigue
  or spasms occur (EMG quality < 0.40), the engine automatically shifts
  primary control weight to the EEG brain intent model, maintaining smooth
  3D arm movement without jitter or unintended motions.
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
from scipy.io import loadmat

def run_adaptive_simulation(csv_path=None, models_path=None, output_json=None, run_degradation_demo=True):
    base_dir = os.path.dirname(__file__)
    
    if csv_path is None:
        csv_path = os.path.join(base_dir, "output", "axion1_features.csv")
    if models_path is None:
        models_path = os.path.join(base_dir, "models", "axion_models.joblib")
    if output_json is None:
        output_json = os.path.join(base_dir, "output", "axion_live_commands.json")

    # 1. Load Trained Models & Artifacts
    print(f"[+] Loading trained models from: {models_path}")
    artifacts = joblib.load(models_path)
    model_eeg = artifacts["model_eeg"]
    model_emg = artifacts["model_emg"]
    eeg_cols = artifacts["eeg_cols"]
    emg_cols = artifacts["emg_cols"]

    # 2. Load Features CSV
    df = pd.read_csv(csv_path)
    print(f"[+] Processing {len(df)} time windows for adaptive execution...")

    # Load degraded quality stream if available (Figure 4 demo stream)
    deg_mat_path = os.path.join(base_dir, "output", "axion1_degraded_quality.mat")
    has_deg_mat = os.path.exists(deg_mat_path)
    
    q_eeg_deg_stream = None
    q_emg_deg_stream = None
    if has_deg_mat:
        try:
            mat = loadmat(deg_mat_path)
            q_eeg_deg_stream = mat['q_eeg_deg'].flatten()
            q_emg_deg_stream = mat['q_emg_deg'].flatten()
            print(f"[+] Loaded degraded quality scenario from: {deg_mat_path} ({len(q_eeg_deg_stream)} windows)")
        except Exception as e:
            print(f"[-] Could not load mat file: {e}")

    # Thresholds (from AXION-1 Interface Contract)
    DEGRADATION_THRESHOLD = 0.40
    SPASM_RMS_THRESHOLD = 6.0  # Spasm detection threshold

    command_stream = []
    active_count = 0
    degraded_count = 0
    paused_count = 0

    n_samples = len(df)
    for idx, row in df.iterrows():
        t = float(row["timestamp"])
        win_id = int(row["window_id"])

        # Extract features
        x_eeg = row[eeg_cols].values.reshape(1, -1)
        x_emg = row[emg_cols].values.reshape(1, -1)

        # Probabilities from each individual modality
        prob_eeg = model_eeg.predict_proba(x_eeg)[0]
        prob_emg = model_emg.predict_proba(x_emg)[0]

        # Use degraded quality profile if running degradation demo
        if run_degradation_demo and q_eeg_deg_stream is not None and idx < len(q_eeg_deg_stream):
            q_eeg = float(q_eeg_deg_stream[idx])
            q_emg = float(q_emg_deg_stream[idx])
        else:
            q_eeg = float(row["eeg_quality"])
            q_emg = float(row["emg_quality"])

        # Simulate spasm events in the middle phase (spasticity period)
        is_spasm = False
        if run_degradation_demo:
            # During 50% to 75% of demo, inject 3 spasms (matching MATLAB Fig 4)
            progress = idx / max(1, n_samples)
            if 0.55 < progress < 0.58 or 0.65 < progress < 0.68:
                is_spasm = True

        # Dynamic Adaptive Weight Computation
        denom = q_eeg + q_emg + 1e-9
        w_eeg = q_eeg / denom
        w_emg = q_emg / denom

        # Safety State Machine Logic
        if is_spasm:
            state = "PAUSED"
            reason = "Erratic physical spasm detected - Multimodal safety net engaged"
            w_eeg = 0.5
            w_emg = 0.5
            intent = "HOLD"
            confidence = 0.0
            joint_angles = {"shoulder": 0.0, "elbow": 45.0, "wrist": 0.0}
            paused_count += 1

        elif q_eeg < DEGRADATION_THRESHOLD and q_emg < DEGRADATION_THRESHOLD:
            state = "PAUSED"
            reason = "Dual biosignal loss of confidence - Paused for patient safety"
            intent = "HOLD"
            confidence = 0.0
            joint_angles = {"shoulder": 0.0, "elbow": 45.0, "wrist": 0.0}
            paused_count += 1

        elif q_emg < DEGRADATION_THRESHOLD:
            state = "DEGRADED"
            reason = "Muscle fatigue detected - Adaptive shift to EEG priority"
            # Override weights: prioritize EEG intent
            w_eeg = max(0.85, w_eeg)
            w_emg = 1.0 - w_eeg
            
            fused_probs = w_eeg * prob_eeg + w_emg * prob_emg
            pred_class = int(np.argmax(fused_probs) + 1)
            confidence = float(np.max(fused_probs))
            
            intent = "FLEX" if pred_class == 1 else "EXTEND"
            elbow_angle = 90.0 if intent == "FLEX" else 15.0
            joint_angles = {"shoulder": 15.0, "elbow": elbow_angle, "wrist": 10.0}
            degraded_count += 1

        else:
            state = "ACTIVE"
            reason = "Nominal multimodal operation"
            fused_probs = w_eeg * prob_eeg + w_emg * prob_emg
            pred_class = int(np.argmax(fused_probs) + 1)
            confidence = float(np.max(fused_probs))

            intent = "FLEX" if pred_class == 1 else "EXTEND"
            elbow_angle = 90.0 if intent == "FLEX" else 15.0
            joint_angles = {"shoulder": 15.0, "elbow": elbow_angle, "wrist": 10.0}
            active_count += 1

        cmd = {
            "timestamp": round(t, 3),
            "window_id": win_id,
            "safety_status": state,
            "status_reason": reason,
            "intent": intent,
            "confidence": round(confidence, 3),
            "source_weights": {
                "eeg": round(w_eeg, 3),
                "emg": round(w_emg, 3)
            },
            "signal_qualities": {
                "eeg_q": round(q_eeg, 3),
                "emg_q": round(q_emg, 3)
            },
            "joint_angles_deg": joint_angles
        }
        command_stream.append(cmd)

    # 4. Save Stream Output for Task C (ROS 2 / RViz2)
    with open(output_json, "w") as f:
        json.dump(command_stream, f, indent=2)

    print("\n--- Simulation Summary ---")
    print(f"  • Total Decision Windows: {len(command_stream)}")
    print(f"  • Active Windows (Green):   {active_count} ({active_count/len(command_stream)*100:.1f}%)")
    print(f"  • Degraded Windows (Amber): {degraded_count} ({degraded_count/len(command_stream)*100:.1f}%) [Adaptive Shift Active]")
    print(f"  • Paused Windows (Red):     {paused_count} ({paused_count/len(command_stream)*100:.1f}%) [Safety Net Triggered]")
    print(f"\n[✓] Exported live command stream to: {output_json}")

if __name__ == "__main__":
    run_adaptive_simulation()
