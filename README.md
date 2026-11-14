# AXION-1: Adaptive Neuro-Mirroring Interface

AXION-1 is an assistive brain-computer interface (BCI) designed for post-stroke motor rehabilitation. The system combines EEG motor imagery decoding with surface EMG sensing, featuring an adaptive weighting engine that responds to muscle fatigue and involuntary spasms, paired with a 3D Action Observation Therapy simulation in ROS 2.

## Key Features

- **Multimodal Biosignal Processing:** Native Common Spatial Pattern (CSP) filtering for EEG sensorimotor rhythms alongside time-domain feature extraction for 4-channel forearm sEMG.
- **Dynamic Weight Shifting:** Real-time signal quality monitoring shifts control authority toward EEG (up to 85%) as muscle fatigue is detected.
- **Spasm Safety Interlock:** Automatic emergency halt triggers within 35 ms upon detecting sudden involuntary muscle contractions or excessive signal artifacts.
- **3D Robot Simulation:** 6-DOF bio-prosthetic arm model in ROS 2 Jazzy performing a goal-directed reach, grasp, and cup-lifting task in RViz2.

## System Components

- **Task A (Signal Processing - MATLAB):** Preprocessing, zero-phase bandpass filtering (7–30 Hz), CAR re-referencing, CSP feature extraction, and signal quality scoring.
- **Task B (Machine Learning - Python):** Random Forest multimodal classification, adaptive weight allocation engine, and browser-based 3D telemetry dashboard.
- **Task C (Simulation - ROS 2):** Custom URDF manipulator model, collision-free reaching trajectories, dynamic object grasp-and-lift state machine, and status beacon indicators.

## Project Structure

```text
axionv1/
├── figures/              # Preprocessing and signal quality figures
├── matlab/               # MATLAB signal processing scripts
│   ├── scripts/          # CSP, EDF loader, feature extraction
│   └── run_axion1_pipeline.m
├── models/               # Trained classifier artifacts
├── output/               # Feature matrices and decision streams
├── ros2_ws/              # ROS 2 workspace
│   ├── scripts/          # Robot controller node
│   ├── urdf/             # Arm URDF definition
│   └── start_ros2_demo.sh
├── axion_adaptive_engine.py
├── train_axion_ml.py
├── test_task_b_dashboard.html
└── README.md
```

## Quickstart

### 1. Python ML & Adaptive Engine
```bash
python run_task_b.py
```
Open `test_task_b_dashboard.html` in any web browser to view the real-time telemetry dashboard.

### 2. ROS 2 Simulation (WSL / Ubuntu 24.04)
```bash
cd ros2_ws
bash start_ros2_demo.sh
```

## License
MIT License
