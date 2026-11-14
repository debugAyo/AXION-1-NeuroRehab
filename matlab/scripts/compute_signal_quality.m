function [quality_eeg, quality_emg] = compute_signal_quality(eeg_clean, emg_clean, fs, window_s, overlap)
% COMPUTE_SIGNAL_QUALITY  Real-time signal quality metrics
%   AXION-1 Project | NeuralVillage Neurotech Hackathon 2026

    if nargin < 4, window_s = 1.0; end
    if nargin < 5, overlap = 0.5; end
    
    winLen  = round(window_s * fs);
    stepLen = round(winLen * (1 - overlap));
    
    nSamples_eeg = size(eeg_clean, 2);
    nSamples_emg = size(emg_clean, 2);
    nWindows = floor((min(nSamples_eeg, nSamples_emg) - winLen) / stepLen) + 1;
    
    quality_eeg = zeros(nWindows, 1);
    quality_emg = zeros(nWindows, 1);
    
    for w = 1:nWindows
        s = (w-1) * stepLen + 1;
        e = s + winLen - 1;
        
        eeg_win = eeg_clean(:, s:min(e, nSamples_eeg));
        nfft = 2^nextpow2(size(eeg_win, 2));
        psd_total = mean(abs(fft(eeg_win, nfft, 2)).^2, 1);
        freqs = (0:nfft-1) * fs / nfft;
        
        band_idx = freqs >= 7 & freqs <= 30;
        total_idx = freqs >= 1 & freqs <= fs/2;
        band_power  = sum(psd_total(band_idx));
        total_power = sum(psd_total(total_idx));
        snr_metric = band_power / (total_power + eps);
        
        amp_std = mean(std(eeg_win, 0, 2));
        stability = 1 / (1 + amp_std / 50);
        artifact_free = 1 - mean(any(abs(eeg_win) > 100, 1));
        
        quality_eeg(w) = 0.4 * min(snr_metric * 5, 1) + 0.3 * stability + 0.3 * artifact_free;
        quality_eeg(w) = max(0, min(1, quality_eeg(w)));
        
        emg_win = emg_clean(:, s:min(e, nSamples_emg));
        rms_val = sqrt(mean(emg_win(:).^2));
        energy_metric = min(rms_val / 0.5, 1);
        
        if size(emg_win, 1) > 1
            C = corrcoef(emg_win');
            upper_tri = triu(C, 1);
            consistency = max(0, mean(upper_tri(upper_tri ~= 0)));
        else
            consistency = 1;
        end
        
        psd_emg = mean(abs(fft(emg_win, nfft, 2)).^2, 1);
        emg_band = freqs >= 20 & freqs <= min(75, fs/2);
        spectral_quality = min(3 * sum(psd_emg(emg_band)) / (sum(psd_emg(total_idx)) + eps), 1);
        
        quality_emg(w) = 0.4 * energy_metric + 0.3 * consistency + 0.3 * spectral_quality;
        quality_emg(w) = max(0, min(1, quality_emg(w)));
    end
end
