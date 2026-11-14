"""
AXION-1: Master Runner for Task B (Machine Learning & Adaptive Fusion)
NeuralVillage Neurotech Hackathon 2026

Runs both steps of Task B end-to-end:
  Step 1: Train classifiers (EEG, EMG, Multimodal) -> models/axion_models.joblib
  Step 2: Run Adaptive Fusion Engine -> output/axion_live_commands.json
"""

import os
import subprocess
import sys

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    print("=" * 65)
    print("  AXION-1 — Task B Pipeline Execution")
    print("  Adaptive Neuro-Mirroring Interface for Motor Rehabilitation")
    print("=" * 65)

    # 1. Run Model Training
    print("\n>>> STEP 1: Training Intent Classifiers (EEG, EMG, Multimodal)...")
    from train_axion_ml import main as train_models
    train_models()

    # 2. Run Adaptive Engine Simulation
    print("\n>>> STEP 2: Running Real-Time Adaptive Weight Shifter & Safety...")
    from axion_adaptive_engine import run_adaptive_simulation
    run_adaptive_simulation()

    print("\n" + "=" * 65)
    print("  [SUCCESS] Task B is 100% complete!")
    print("  Output generated at: output/axion_live_commands.json")
    print("  Ready for Task C (ROS 2 / RViz2 3D Arm Visualization)")
    print("=" * 65)

if __name__ == "__main__":
    main()
