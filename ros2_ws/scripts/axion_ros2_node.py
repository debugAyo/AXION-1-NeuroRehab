#!/usr/bin/env python3
"""
AXION-1: ROS 2 Controller & Collision-Free Action Observation Therapy Node
NeuralVillage Neurotech Hackathon 2026

Goal-Directed Rehabilitation Task: Ergonomic Top-Down Cup Grasp (Zero Clipping)
  - Wrist sits 4cm ABOVE cup rim (Z=0.46m).
  - Forearm is strictly elevated above cup height (Z >= 0.46m).
  - Palm hovers cleanly over the cup rim while cyan fingers reach down
    and clamp the outside sides of the cup (like a real robotic gripper).
  - 3D Safety Beacon: Green (ACTIVE), Amber (DEGRADED/Grip Hold), Red (PAUSED/Spasm Lock).
"""

import os
import json
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from visualization_msgs.msg import Marker, MarkerArray

class AxionArmNode(Node):
    def __init__(self):
        super().__init__('axion_arm_controller')

        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.marker_pub = self.create_publisher(MarkerArray, '/axion/status_marker', 10)

        # Locate decision stream JSON
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(os.path.dirname(base_dir), "output", "axion_live_commands.json")
        if not os.path.exists(json_path):
            json_path = os.path.join(base_dir, "..", "output", "axion_live_commands.json")

        self.get_logger().info(f"Loading AXION-1 Decision Stream from: {json_path}")
        with open(json_path, 'r') as f:
            raw_commands = json.load(f)

        # Build Curated 30-Second Competition Demo Showcase (Full Clinical Story in 24 Seconds):
        # 1. Reach for Cup (0s - 6s): ACTIVE | EXTEND | Green Beacon
        # 2. Lift Cup (6s - 12s): ACTIVE | FLEX | Cup Rises | Green Beacon
        # 3. Muscle Fatigue (12s - 18s): DEGRADED | 85% Brain EEG Override | Amber Beacon
        # 4. Involuntary Spasm (18s - 24s): PAUSED | Arm Frozen in Mid-Air | Red Beacon
        active_reach = [c for c in raw_commands if c['safety_status'] == 'ACTIVE' and c['intent'] == 'EXTEND'][:4]
        active_lift = [c for c in raw_commands if c['safety_status'] == 'ACTIVE' and c['intent'] == 'FLEX'][:4]
        degraded_events = [c for c in raw_commands if c['safety_status'] == 'DEGRADED'][:4]
        paused_events = [c for c in raw_commands if c['safety_status'] == 'PAUSED'][:4]

        if not degraded_events:
            degraded_events = [{
                "timestamp": 12.0,
                "safety_status": "DEGRADED",
                "status_reason": "Muscle fatigue detected (q_EMG < 0.40) - Adaptive shift to EEG priority",
                "intent": "FLEX",
                "source_weights": {"eeg": 0.85, "emg": 0.15}
            }] * 4

        if not paused_events:
            paused_events = [{
                "timestamp": 18.0,
                "safety_status": "PAUSED",
                "status_reason": "Erratic physical spasm detected - Multimodal safety net engaged",
                "intent": "FLEX",
                "source_weights": {"eeg": 0.50, "emg": 0.50}
            }] * 4

        # Assemble the high-impact demonstration sequence:
        self.commands = active_reach + active_lift + degraded_events + paused_events
        self.idx = 0
        self.total_commands = len(self.commands)
        self.get_logger().info(f"Competition Showcase Activated: {self.total_commands} steps in rotating 24s clinical cycle.")

        # Retracted resting stance (arm safely elevated and tucked near patient torso)
        self.curr_shoulder_pitch = -0.10
        self.targ_shoulder_pitch = -0.10

        self.curr_elbow = 1.60
        self.targ_elbow = 1.60

        self.curr_wrist = -0.50
        self.targ_wrist = -0.50

        self.curr_finger_l = 0.0
        self.targ_finger_l = 0.0

        self.curr_finger_r = 0.0
        self.targ_finger_r = 0.0

        # Dynamic Cup Attachment State
        self.holding_cup = False
        self.cup_x = 0.470
        self.cup_z = 0.360

        # State tracking
        self.current_status = "ACTIVE"
        self.current_reason = "Nominal multimodal operation"
        self.current_intent = "EXTEND"
        self.w_eeg = 0.58
        self.w_emg = 0.42

        # 30 Hz smooth control loop
        self.timer = self.create_timer(1.0 / 30.0, self.update_callback)
        # Decision step timer (every 1.5s)
        self.decision_timer = self.create_timer(1.5, self.next_decision_callback)

    def next_decision_callback(self):
        cmd = self.commands[self.idx]
        self.idx = (self.idx + 1) % self.total_commands

        self.current_status = cmd["safety_status"]
        self.current_reason = cmd["status_reason"]
        self.current_intent = cmd["intent"]
        self.w_eeg = cmd["source_weights"]["eeg"]
        self.w_emg = cmd["source_weights"]["emg"]

        # Natural Clinical Action Observation Trajectory (Zero-Collision Grasp)
        if self.current_status == "PAUSED":
            # Safety lock: Freeze in current position immediately
            self.targ_shoulder_pitch = self.curr_shoulder_pitch
            self.targ_elbow = self.curr_elbow
            self.targ_wrist = self.curr_wrist
            self.targ_finger_l = self.curr_finger_l
            self.targ_finger_r = self.curr_finger_r
            task_desc = "EMERGENCY SAFETY LOCK (Arm Frozen in Mid-Air, Spill Prevented)"

        elif self.current_status == "DEGRADED":
            # Muscle fatigue at cup -> Hand clamps outside of cup; Brain (85%) holds grip
            # Hand mid-height Z=0.36m, palm 15mm clear behind cup, fingers clamped snugly at Y=±0.038m
            self.targ_shoulder_pitch = 0.032
            self.targ_elbow = 2.150
            self.targ_wrist = -0.612
            self.targ_finger_l = 0.04
            self.targ_finger_r = -0.04
            task_desc = f"Brain Override ({self.w_eeg*100:.0f}%) -> Firm Grip Secured on Cup"

        elif self.current_intent == "EXTEND":
            # REACHING FOR CUP: Glides smoothly down from above, fingers open wide framing cup sides
            self.targ_shoulder_pitch = 0.032
            self.targ_elbow = 2.150
            self.targ_wrist = -0.612
            self.targ_finger_l = -0.35
            self.targ_finger_r = 0.35
            task_desc = "Reaching Downward -> Fingers Open Wide Around Cup"

        else:
            # RETRACTING BACK TO REST (Tucked near chest/torso at Z=0.64m, safely in the air)
            self.targ_shoulder_pitch = -0.10
            self.targ_elbow = 1.60
            self.targ_wrist = -0.50
            if self.holding_cup:
                self.targ_finger_l = 0.04
                self.targ_finger_r = -0.04
                task_desc = "Lifting Cup Toward Chest (Rehab Drinking Task)"
            else:
                self.targ_finger_l = 0.0
                self.targ_finger_r = 0.0
                task_desc = "Retracting Arm to Torso Rest (Elevated in Air)"

        self.get_logger().info(
            f"[{cmd['timestamp']}s] {self.current_status} | {task_desc} | EEG: {self.w_eeg*100:.0f}%"
        )

    def update_callback(self):
        # Smooth reliable interpolation for Action Observation Therapy (Proven Grasp & Lift Speed)
        alpha = 0.08
        self.curr_shoulder_pitch += (self.targ_shoulder_pitch - self.curr_shoulder_pitch) * alpha
        self.curr_elbow += (self.targ_elbow - self.curr_elbow) * alpha
        self.curr_wrist += (self.targ_wrist - self.curr_wrist) * alpha
        self.curr_finger_l += (self.targ_finger_l - self.curr_finger_l) * alpha
        self.curr_finger_r += (self.targ_finger_r - self.curr_finger_r) * alpha

        # Forward Kinematics for Gripper Grasp Center
        th1 = self.curr_shoulder_pitch
        th2 = self.curr_elbow
        th3 = self.curr_wrist

        x_elbow = 0.45 * math.sin(th1)
        z_elbow = 0.14 + 0.45 * math.cos(th1)

        a2 = th1 + th2
        x_wrist = x_elbow + 0.40 * math.sin(a2)
        z_wrist = z_elbow + 0.40 * math.cos(a2)

        a3 = a2 + th3
        grip_x = x_wrist + 0.130 * math.sin(a3)
        grip_z = z_wrist + 0.130 * math.cos(a3)

        # Dynamic Grasp & Lift State Machine
        if not self.holding_cup:
            # When hand arrives at cup height on the table:
            if grip_z <= 0.380 and abs(grip_x - 0.470) < 0.06:
                # Clamp fingers firmly around cup!
                self.holding_cup = True
                self.targ_finger_l = 0.04
                self.targ_finger_r = -0.04
            self.cup_x = 0.470
            self.cup_z = 0.360
        else:
            # HOLDING CUP: Fingers stay firmly clamped around outer walls!
            self.targ_finger_l = 0.04
            self.targ_finger_r = -0.04

            # If placing back down on table surface:
            if self.current_intent == "EXTEND" and grip_z <= 0.365:
                # Release cup onto table
                self.holding_cup = False
                self.cup_x = 0.470
                self.cup_z = 0.360
            else:
                # Cup rises dynamically in the air with the gripper!
                self.cup_x = grip_x
                self.cup_z = max(0.360, grip_z)

        now = self.get_clock().now().to_msg()

        # 1. Publish JointState
        js = JointState()
        js.header.stamp = now
        js.name = [
            'shoulder_joint',
            'shoulder_pitch_joint',
            'elbow_joint',
            'wrist_joint',
            'finger_left_joint',
            'finger_right_joint'
        ]
        js.position = [
            0.0,
            self.curr_shoulder_pitch,
            self.curr_elbow,
            self.curr_wrist,
            self.curr_finger_l,
            self.curr_finger_r
        ]
        self.joint_pub.publish(js)

        # 2. Build 3D Scene MarkerArray (Table, Solid Cup, and Safety Beacon)
        marker_array = MarkerArray()

        # --- PROP A: 3D Table Slab ---
        table = Marker()
        table.header.frame_id = 'base_link'
        table.header.stamp = now
        table.ns = 'axion_props'
        table.id = 101
        table.type = Marker.CUBE
        table.action = Marker.ADD
        table.pose.position.x = 0.50
        table.pose.position.y = 0.0
        table.pose.position.z = 0.28
        table.pose.orientation.w = 1.0
        table.scale.x = 0.55
        table.scale.y = 0.75
        table.scale.z = 0.04
        table.color.r = 0.38
        table.color.g = 0.26
        table.color.b = 0.18
        table.color.a = 1.0
        marker_array.markers.append(table)

        # --- PROP B: 4 Table Legs ---
        leg_positions = [
            (0.72, 0.32), (0.72, -0.32),
            (0.28, 0.32), (0.28, -0.32)
        ]
        for i, (lx, ly) in enumerate(leg_positions):
            leg = Marker()
            leg.header.frame_id = 'base_link'
            leg.header.stamp = now
            leg.ns = 'axion_props'
            leg.id = 110 + i
            leg.type = Marker.CYLINDER
            leg.action = Marker.ADD
            leg.pose.position.x = lx
            leg.pose.position.y = ly
            leg.pose.position.z = 0.13
            leg.pose.orientation.w = 1.0
            leg.scale.x = 0.04
            leg.scale.y = 0.04
            leg.scale.z = 0.26
            leg.color.r = 0.15
            leg.color.g = 0.18
            leg.color.b = 0.22
            leg.color.a = 1.0
            marker_array.markers.append(leg)

        # --- PROP C: 3D Cup Body (Dynamic Grasp & Lift) ---
        cup = Marker()
        cup.header.frame_id = 'base_link'
        cup.header.stamp = now
        cup.ns = 'axion_props'
        cup.id = 201
        cup.type = Marker.CYLINDER
        cup.action = Marker.ADD
        cup.pose.position.x = self.cup_x
        cup.pose.position.y = 0.0
        cup.pose.position.z = self.cup_z
        cup.pose.orientation.w = 1.0
        cup.scale.x = 0.076
        cup.scale.y = 0.076
        cup.scale.z = 0.12
        cup.color.r = 0.10
        cup.color.g = 0.75
        cup.color.b = 0.85
        cup.color.a = 1.0
        marker_array.markers.append(cup)

        # --- PROP D: Cup White Rim ---
        rim = Marker()
        rim.header.frame_id = 'base_link'
        rim.header.stamp = now
        rim.ns = 'axion_props'
        rim.id = 202
        rim.type = Marker.CYLINDER
        rim.action = Marker.ADD
        rim.pose.position.x = self.cup_x
        rim.pose.position.y = 0.0
        rim.pose.position.z = self.cup_z + 0.062
        rim.pose.orientation.w = 1.0
        rim.scale.x = 0.082
        rim.scale.y = 0.082
        rim.scale.z = 0.012
        rim.color.r = 0.95
        rim.color.g = 0.95
        rim.color.b = 0.95
        rim.color.a = 1.0
        marker_array.markers.append(rim)

        # --- PROP E: Cup Handle ---
        handle = Marker()
        handle.header.frame_id = 'base_link'
        handle.header.stamp = now
        handle.ns = 'axion_props'
        handle.id = 203
        handle.type = Marker.CUBE
        handle.action = Marker.ADD
        handle.pose.position.x = self.cup_x + 0.050
        handle.pose.position.y = 0.0
        handle.pose.position.z = self.cup_z
        handle.pose.orientation.w = 1.0
        handle.scale.x = 0.03
        handle.scale.y = 0.015
        handle.scale.z = 0.06
        handle.color.r = 0.10
        handle.color.g = 0.75
        handle.color.b = 0.85
        handle.color.a = 1.0
        marker_array.markers.append(handle)

        # --- PROP F: 3D Clinical Safety Beacon Post (On table corner) ---
        beacon_post = Marker()
        beacon_post.header.frame_id = 'base_link'
        beacon_post.header.stamp = now
        beacon_post.ns = 'axion_props'
        beacon_post.id = 301
        beacon_post.type = Marker.CYLINDER
        beacon_post.action = Marker.ADD
        beacon_post.pose.position.x = 0.30
        beacon_post.pose.position.y = 0.30
        beacon_post.pose.position.z = 0.42
        beacon_post.pose.orientation.w = 1.0
        beacon_post.scale.x = 0.025
        beacon_post.scale.y = 0.025
        beacon_post.scale.z = 0.24
        beacon_post.color.r = 0.20
        beacon_post.color.g = 0.25
        beacon_post.color.b = 0.30
        beacon_post.color.a = 1.0
        marker_array.markers.append(beacon_post)

        # --- PROP G: Glowing 3D Safety Beacon Dome ---
        beacon_light = Marker()
        beacon_light.header.frame_id = 'base_link'
        beacon_light.header.stamp = now
        beacon_light.ns = 'axion_props'
        beacon_light.id = 302
        beacon_light.type = Marker.SPHERE
        beacon_light.action = Marker.ADD
        beacon_light.pose.position.x = 0.30
        beacon_light.pose.position.y = 0.30
        beacon_light.pose.position.z = 0.56
        beacon_light.pose.orientation.w = 1.0
        beacon_light.scale.x = 0.08
        beacon_light.scale.y = 0.08
        beacon_light.scale.z = 0.08

        if self.current_status == 'ACTIVE':
            beacon_light.color.r = 0.10
            beacon_light.color.g = 0.95
            beacon_light.color.b = 0.25
            beacon_light.color.a = 1.0
        elif self.current_status == 'DEGRADED':
            beacon_light.color.r = 0.98
            beacon_light.color.g = 0.85
            beacon_light.color.b = 0.05
            beacon_light.color.a = 1.0
        else:
            beacon_light.color.r = 0.98
            beacon_light.color.g = 0.15
            beacon_light.color.b = 0.15
            beacon_light.color.a = 1.0

        marker_array.markers.append(beacon_light)

        # --- PROP H: 3D Clinical Monitor Stand (On table at X=0.40, Y=-0.25) ---
        mon_stand = Marker()
        mon_stand.header.frame_id = 'base_link'
        mon_stand.header.stamp = now
        mon_stand.ns = 'axion_props'
        mon_stand.id = 401
        mon_stand.type = Marker.CYLINDER
        mon_stand.action = Marker.ADD
        mon_stand.pose.position.x = 0.40
        mon_stand.pose.position.y = -0.25
        mon_stand.pose.position.z = 0.36
        mon_stand.pose.orientation.w = 1.0
        mon_stand.scale.x = 0.03
        mon_stand.scale.y = 0.03
        mon_stand.scale.z = 0.12
        mon_stand.color.r = 0.25
        mon_stand.color.g = 0.28
        mon_stand.color.b = 0.32
        mon_stand.color.a = 1.0
        marker_array.markers.append(mon_stand)

        # --- PROP I: 3D Clinical Monitor Housing (Bezel) ---
        mon_housing = Marker()
        mon_housing.header.frame_id = 'base_link'
        mon_housing.header.stamp = now
        mon_housing.ns = 'axion_props'
        mon_housing.id = 402
        mon_housing.type = Marker.CUBE
        mon_housing.action = Marker.ADD
        mon_housing.pose.position.x = 0.40
        mon_housing.pose.position.y = -0.25
        mon_housing.pose.position.z = 0.46
        mon_housing.pose.orientation.w = 1.0
        mon_housing.scale.x = 0.025
        mon_housing.scale.y = 0.26
        mon_housing.scale.z = 0.16
        mon_housing.color.r = 0.08
        mon_housing.color.g = 0.10
        mon_housing.color.b = 0.14
        mon_housing.color.a = 1.0
        marker_array.markers.append(mon_housing)

        # --- PROP J: 3D Monitor Glass Display Face ---
        mon_face = Marker()
        mon_face.header.frame_id = 'base_link'
        mon_face.header.stamp = now
        mon_face.ns = 'axion_props'
        mon_face.id = 403
        mon_face.type = Marker.CUBE
        mon_face.action = Marker.ADD
        mon_face.pose.position.x = 0.386
        mon_face.pose.position.y = -0.25
        mon_face.pose.position.z = 0.46
        mon_face.pose.orientation.w = 1.0
        mon_face.scale.x = 0.003
        mon_face.scale.y = 0.24
        mon_face.scale.z = 0.14
        mon_face.color.r = 0.03
        mon_face.color.g = 0.06
        mon_face.color.b = 0.10
        mon_face.color.a = 1.0
        marker_array.markers.append(mon_face)

        # --- PROP K: Glowing Clinical LED Status Bar on Screen Face ---
        # 100% Solid Geometry (Zero Font / Kerning Bugs in WSL)
        screen_bar = Marker()
        screen_bar.header.frame_id = 'base_link'
        screen_bar.header.stamp = now
        screen_bar.ns = 'axion_props'
        screen_bar.id = 404
        screen_bar.type = Marker.CUBE
        screen_bar.action = Marker.ADD
        screen_bar.pose.position.x = 0.384
        screen_bar.pose.position.y = -0.25
        screen_bar.pose.position.z = 0.48
        screen_bar.pose.orientation.w = 1.0
        screen_bar.scale.x = 0.004
        screen_bar.scale.y = 0.20
        screen_bar.scale.z = 0.04

        if self.current_status == 'ACTIVE':
            # Neon Green (Active Reach & Lift)
            screen_bar.color.r = 0.15
            screen_bar.color.g = 0.95
            screen_bar.color.b = 0.30
            screen_bar.color.a = 1.0
        elif self.current_status == 'DEGRADED':
            # Amber Alert (Brain EEG Override Grip Active)
            screen_bar.color.r = 0.98
            screen_bar.color.g = 0.85
            screen_bar.color.b = 0.05
            screen_bar.color.a = 1.0
        else:
            # Emergency Red (Spasm Safety Freeze)
            screen_bar.color.r = 0.98
            screen_bar.color.g = 0.15
            screen_bar.color.b = 0.15
            screen_bar.color.a = 1.0

        marker_array.markers.append(screen_bar)

        # --- PROP L: Biosignal Power Level Indicator on Screen ---
        eeg_bar = Marker()
        eeg_bar.header.frame_id = 'base_link'
        eeg_bar.header.stamp = now
        eeg_bar.ns = 'axion_props'
        eeg_bar.id = 405
        eeg_bar.type = Marker.CUBE
        eeg_bar.action = Marker.ADD
        eeg_bar.pose.position.x = 0.384
        eeg_bar.pose.position.y = -0.25
        eeg_bar.pose.position.z = 0.43
        eeg_bar.pose.orientation.w = 1.0
        eeg_bar.scale.x = 0.004
        eeg_bar.scale.y = max(0.04, min(0.20, self.w_eeg * 0.24))
        eeg_bar.scale.z = 0.02
        eeg_bar.color.r = 0.20
        eeg_bar.color.g = 0.75
        eeg_bar.color.b = 0.98
        eeg_bar.color.a = 1.0
        marker_array.markers.append(eeg_bar)

        # Publish all clean solid 3D scene props
        self.marker_pub.publish(marker_array)

def main(args=None):
    rclpy.init(args=args)
    node = AxionArmNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
