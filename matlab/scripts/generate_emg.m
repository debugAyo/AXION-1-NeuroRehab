function [emg_raw, emg_clean, emg_fs, emg_labels] = generate_emg(duration_s, fs, labels_eeg)
% GENERATE_EMG  Simulate realistic surface EMG for motor rehabilitation
%   AXION-1 Project | NeuralVillage Neurotech Hackathon 2026

    emg_fs = fs;
    num_channels = 4;
    emg_labels = {'Flexor_Digitorum', 'Extensor_Digitorum', ...
                  'Flexor_Carpi_Radialis', 'Extensor_Carpi_Ulnaris'};
    
    num_samples = duration_s * fs;
    t = (0:num_samples-1) / fs;
    emg_raw = zeros(num_channels, num_samples);
    
    for ch = 1:num_channels
        noise = randn(1, num_samples);
        f_emg_low  = 20;
        f_emg_high = min(75, fs/2 - 1);
        [b, a] = butter(3, [f_emg_low, f_emg_high] / (fs/2), 'bandpass');
        emg_base = filtfilt(b, a, noise);
        
        if nargin >= 3 && ~isempty(labels_eeg)
            envelope = double(labels_eeg ~= 0);
            win = round(0.3 * fs);
            envelope = movmean(envelope, win);
        else
            envelope = double(mod(t, 6) < 3);
            envelope = movmean(envelope, round(0.5 * fs));
        end
        
        scale = 1 + (3 + rand()) * envelope;
        emg_raw(ch, :) = emg_base .* scale + 0.3 * sin(2*pi*50*t + rand()*2*pi) + 0.1 * sin(2*pi*0.5*t + rand()*2*pi);
    end
    
    emg_clean = zeros(size(emg_raw));
    for ch = 1:num_channels
        [b, a] = butter(4, [20, min(75, fs/2-1)] / (fs/2), 'bandpass');
        filtered = filtfilt(b, a, emg_raw(ch, :));
        [b_n, a_n] = iirnotch(50 / (fs/2), 2 / (fs/2));
        filtered = filtfilt(b_n, a_n, filtered);
        emg_clean(ch, :) = abs(filtered);
    end
end
