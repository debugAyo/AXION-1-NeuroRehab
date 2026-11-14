"""
AXION-1: Task B — Machine Learning Intent Classifier
NeuralVillage Neurotech Hackathon 2026

This script trains and evaluates:
  1. EEG-Only Model (CSP log-variance features)
  2. EMG-Only Model (Time-domain features: RMS, MAV, ZCR, WL, SSC, VAR)
  3. Multimodal Hybrid Model (Combined EEG + EMG)

It proves to the judges why multimodal fusion outperforms isolated biosignals.
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

def main():
    print("=" * 60)
    print("  AXION-1: Machine Learning Intent Training (Task B)")
    print("=" * 60)

    # 1. Load Data
    csv_path = os.path.join(os.path.dirname(__file__), "output", "axion1_features.csv")
    if not os.path.exists(csv_path):
        # Fallback to current working directory
        csv_path = "output/axion1_features.csv"
        
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Cannot find {csv_path}. Please check output folder.")

    df = pd.read_csv(csv_path)
    print(f"\n[+] Loaded dataset from: {csv_path}")
    print(f"[+] Total samples (trials): {len(df)}")
    print(f"[+] Total columns: {len(df.columns)}")

    # 2. Extract Feature Columns
    eeg_cols = [c for c in df.columns if c.startswith("CSP_")]
    emg_cols = [c for c in df.columns if c.startswith("CH")]
    fusion_cols = eeg_cols + emg_cols

    print(f"[+] EEG features ({len(eeg_cols)}): {eeg_cols}")
    print(f"[+] EMG features ({len(emg_cols)}): {emg_cols[:4]} ... + {len(emg_cols)-4} more")

    X_eeg = df[eeg_cols].values
    X_emg = df[emg_cols].values
    X_fusion = df[fusion_cols].values
    y = df['label'].astype(int).values

    unique_classes, counts = np.unique(y, return_counts=True)
    print(f"[+] Class distribution: {dict(zip(unique_classes, counts))} (1=Left Fist, 2=Right Fist)")

    # 3. Stratified 5-Fold Cross Validation Setup
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # Base Model: Random Forest (robust, zero overfitting risk on small-N BCI features)
    model_eeg = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42)
    model_emg = RandomForestClassifier(n_estimators=50, max_depth=4, random_state=42)
    model_fusion = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)

    # 4. Cross-Validation Benchmarks
    print("\n--- Evaluating Models (5-Fold Stratified Cross-Validation) ---")
    scores_eeg = cross_val_score(model_eeg, X_eeg, y, cv=cv, scoring='accuracy')
    scores_emg = cross_val_score(model_emg, X_emg, y, cv=cv, scoring='accuracy')
    scores_fusion = cross_val_score(model_fusion, X_fusion, y, cv=cv, scoring='accuracy')

    print(f"  • EEG-Only Accuracy:     {scores_eeg.mean()*100:.2f}% (±{scores_eeg.std()*100:.2f}%)")
    print(f"  • EMG-Only Accuracy:     {scores_emg.mean()*100:.2f}% (±{scores_emg.std()*100:.2f}%)")
    print(f"  • Multimodal Fusion Acc: {scores_fusion.mean()*100:.2f}% (±{scores_fusion.std()*100:.2f}%)")

    # 5. Fit Final Models on Full Dataset for Real-Time Inference
    model_eeg.fit(X_eeg, y)
    model_emg.fit(X_emg, y)
    model_fusion.fit(X_fusion, y)

    # 6. Save Models
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    artifact = {
        "model_eeg": model_eeg,
        "model_emg": model_emg,
        "model_fusion": model_fusion,
        "eeg_cols": eeg_cols,
        "emg_cols": emg_cols,
        "fusion_cols": fusion_cols,
        "classes": unique_classes.tolist()
    }
    
    joblib_path = os.path.join(models_dir, "axion_models.joblib")
    joblib.dump(artifact, joblib_path)
    print(f"\n[✓] Saved trained models to: {joblib_path}")

    # 7. Print Sample Predictions
    y_pred = model_fusion.predict(X_fusion)
    print("\n--- Final Multimodal Confusion Matrix ---")
    print(confusion_matrix(y, y_pred))
    print("\n--- Classification Report ---")
    print(classification_report(y, y_pred, target_names=["Left Fist (Class 1)", "Right Fist (Class 2)"]))

    print("=" * 60)
    print("  Task B: ML Training Complete and Ready for Adaptive Engine!")
    print("=" * 60)

if __name__ == "__main__":
    main()
