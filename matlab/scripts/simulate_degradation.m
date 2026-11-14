function [eeg_degraded, emg_degraded, degradation_profile] = simulate_degradation(eeg_clean, emg_clean, fs, scenario)
% SIMULATE_DEGRADATION  Inject realistic signal degradation for AXION-1 demo
%   AXION-1 Project | NeuralVillage Neurotech Hackathon 2026

    if nargin < 4, scenario = 'full_demo'; end
    nSamples = min(size(eeg_clean, 2), size(emg_clean, 2));
    eeg_degraded = eeg_clean(:, 1:nSamples);
    emg_degraded = emg_clean(:, 1:nSamples);
    t = (0:nSamples-1) / fs;
    
    degradation_profile = struct();
    degradation_profile.time = t;
    degradation_profile.emg_scale = ones(1, nSamples);
    degradation_profile.noise_level = zeros(1, nSamples);
    degradation_profile.scenario_label = strings(1, nSamples);
    
    p1 = round(0.25 * nSamples);
    p2 = round(0.50 * nSamples);
    p3 = round(0.75 * nSamples);
    
    degradation_profile.scenario_label(1:p1) = "clean";
    fatigue_ramp = linspace(1, 0.15, p2-p1);
    emg_degraded(:, p1+1:p2) = emg_degraded(:, p1+1:p2) .* fatigue_ramp;
    degradation_profile.emg_scale(p1+1:p2) = fatigue_ramp;
    degradation_profile.scenario_label(p1+1:p2) = "fatigue";
    
    emg_degraded(:, p2+1:p3) = emg_degraded(:, p2+1:p3) * 0.15;
    degradation_profile.emg_scale(p2+1:p3) = 0.15;
    degradation_profile.scenario_label(p2+1:p3) = "spasticity";
    
    for i = 1:3
        spasm_len = round(0.4 * fs);
        onset = p2 + randi(p3 - p2 - spasm_len);
        spasm_amp = 8 * rand() + 4;
        emg_degraded(:, onset:onset+spasm_len-1) = spasm_amp * randn(size(emg_clean, 1), spasm_len);
        degradation_profile.emg_scale(onset:onset+spasm_len-1) = spasm_amp;
    end
    
    recovery_ramp = linspace(0.15, 0.6, nSamples - p3);
    emg_degraded(:, p3+1:end) = emg_clean(:, p3+1:nSamples) .* recovery_ramp;
    degradation_profile.emg_scale(p3+1:end) = recovery_ramp;
    degradation_profile.scenario_label(p3+1:end) = "recovery";
end
