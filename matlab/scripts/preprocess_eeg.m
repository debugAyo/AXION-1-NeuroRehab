function [eeg_clean, fs, channelLabels] = preprocess_eeg(eeg_raw, hdr)
% PREPROCESS_EEG  Full EEG preprocessing for motor imagery BCI
%   [eeg_clean, fs, channelLabels] = preprocess_eeg(eeg_raw, hdr)
%
%   AXION-1 Project | NeuralVillage Neurotech Hackathon 2026

    fs = hdr.fs;
    allLabels = hdr.labels;
    
    motorChannels = {'C3', 'C1', 'Cz', 'C2', 'C4', ...
                     'FC3', 'FC1', 'FCz', 'FC2', 'FC4', ...
                     'CP3', 'CP1', 'CPz', 'CP2', 'CP4'};
    
    chanIdx = [];
    selectedLabels = {};
    for i = 1:length(motorChannels)
        for j = 1:length(allLabels)
            if strcmpi(strtrim(allLabels{j}), motorChannels{i})
                chanIdx(end+1) = j; %#ok
                selectedLabels{end+1} = motorChannels{i}; %#ok
                break;
            end
        end
    end
    
    if isempty(chanIdx)
        chanIdx = 1:min(size(eeg_raw, 1), 64);
        selectedLabels = allLabels(chanIdx);
    end
    
    eeg_selected = eeg_raw(chanIdx, :);
    channelLabels = selectedLabels;
    
    car_mean = mean(eeg_selected, 1);
    eeg_reref = eeg_selected - car_mean;
    
    f_low  = 7;
    f_high = 30;
    order  = 4;
    [b_bp, a_bp] = butter(order, [f_low, f_high] / (fs/2), 'bandpass');
    
    eeg_filt = zeros(size(eeg_reref));
    for ch = 1:size(eeg_reref, 1)
        eeg_filt(ch, :) = filtfilt(b_bp, a_bp, eeg_reref(ch, :));
    end
    
    f_notch = 50;
    bw_notch = 2;
    [b_notch, a_notch] = iirnotch(f_notch / (fs/2), bw_notch / (fs/2));
    
    eeg_notch = zeros(size(eeg_filt));
    for ch = 1:size(eeg_filt, 1)
        eeg_notch(ch, :) = filtfilt(b_notch, a_notch, eeg_filt(ch, :));
    end
    
    threshold_uv = 100;
    artifact_mask = any(abs(eeg_notch) > threshold_uv, 1);
    eeg_clean = eeg_notch;
    eeg_clean(:, artifact_mask) = 0;
end
