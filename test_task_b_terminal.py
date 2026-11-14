"""
AXION-1: Real-Time Terminal Player for Task B
NeuralVillage Neurotech Hackathon 2026

Streams the ML decisions from output/axion_live_commands.json at 2x speed
in your terminal, showing live state transitions (ACTIVE, DEGRADED, PAUSED)
and weight shifts.
"""

import os
import json
import time

def bar(val, max_val=1.0, length=20, fill_char="█"):
    filled = int((val / max_val) * length)
    filled = max(0, min(length, filled))
    return fill_char * filled + "░" * (length - filled)

def main():
    json_path = os.path.join(os.path.dirname(__file__), "output", "axion_live_commands.json")
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found. Run run_task_b.py first!")
        return

    with open(json_path, "r") as f:
        commands = json.load(f)

    print("\n" + "=" * 70)
    print("  AXION-1: Live Terminal Test Stream (Task B Output)")
    print("  Press Ctrl+C at any time to stop.")
    print("=" * 70)
    time.sleep(1.0)

    for cmd in commands:
        t = cmd["timestamp"]
        status = cmd["safety_status"]
        intent = cmd["intent"]
        conf = cmd["confidence"]
        w_eeg = cmd["source_weights"]["eeg"]
        w_emg = cmd["source_weights"]["emg"]
        elbow = cmd["joint_angles_deg"]["elbow"]

        # Color codes
        if status == "ACTIVE":
            status_str = f"\033[92m● ACTIVE\033[0m   (Shared Control)"
        elif status == "DEGRADED":
            status_str = f"\033[93m▲ DEGRADED\033[0m (Brain Override: {w_eeg*100:.0f}%)"
        else:
            status_str = f"\033[91m✖ PAUSED\033[0m   (Safety Lockout)"

        eeg_bar = bar(w_eeg, length=15)
        emg_bar = bar(w_emg, length=15)

        print(f"[{t:5.1f}s] {status_str} | Intent: {intent:<6} (conf: {conf:.2f}) | Elbow: {elbow:4.1f}°")
        print(f"        EEG Weight: [{eeg_bar}] {w_eeg*100:4.1f}% | EMG Weight: [{emg_bar}] {w_emg*100:4.1f}%")
        print("-" * 70)

        time.sleep(0.12)  # Stream playback speed

    print("\n[✓] Stream finished successfully. Total windows played: ", len(commands))

if __name__ == "__main__":
    main()
