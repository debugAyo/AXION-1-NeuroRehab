#!/bin/bash
# ===================================================================
#   AXION-1: Task C — 3D Arm RViz2 Launch Script for WSL
#   NeuralVillage Neurotech Hackathon 2026
# ===================================================================

cd "$(dirname "$0")"
WS_DIR=$(pwd)

echo "==============================================================="
echo "  Starting AXION-1 3D Simulation (ROS 2 + RViz2)"
echo "  Workspace: $WS_DIR"
echo "==============================================================="

# 1. Detect and Source ROS 2 installation
# Clean up any lingering background processes from previous runs first
pkill -9 -f robot_state_publisher 2>/dev/null
pkill -9 -f axion_ros2_node 2>/dev/null
sleep 0.5

if [ -f "/opt/ros/jazzy/setup.bash" ]; then
    source /opt/ros/jazzy/setup.bash
    echo "[+] Sourced ROS 2 Jazzy"
elif [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
    echo "[+] Sourced ROS 2 Humble"
fi

# 2. Make controller node executable
chmod +x "$WS_DIR/scripts/axion_ros2_node.py"

URDF_PATH="$WS_DIR/urdf/axion_arm.urdf"
RVIZ_CONFIG="$WS_DIR/rviz/axion_view.rviz"

# 3. Start robot_state_publisher using clean file argument (avoids CLI string truncation)
echo "[+] Starting robot_state_publisher with URDF..."
ros2 run robot_state_publisher robot_state_publisher "$URDF_PATH" &
RSP_PID=$!

sleep 1

# 4. Start controller & visual props node
echo "[+] Starting AXION-1 Action Observation Controller..."
python3 "$WS_DIR/scripts/axion_ros2_node.py" &
NODE_PID=$!

sleep 1

# Cleanup background processes on exit or interrupt
cleanup() {
    echo "Cleaning up ROS 2 processes..."
    kill $RSP_PID $NODE_PID 2>/dev/null
    pkill -9 -f robot_state_publisher 2>/dev/null
    pkill -9 -f axion_ros2_node 2>/dev/null
    echo "Done."
}
trap cleanup EXIT INT TERM

# 5. Launch RViz2
echo "[+] Launching RViz2..."
rviz2 -d "$RVIZ_CONFIG"
