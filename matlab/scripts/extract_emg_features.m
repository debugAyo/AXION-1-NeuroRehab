function [emg_features, feature_names] = extract_emg_features(emg_clean, fs, window_s, overlap)
% EXTRACT_EMG_FEATURES  Time-domain EMG feature extraction
%   AXION-1 Project | NeuralVillage Neurotech Hackathon 2026

    if nargin < 3, window_s = 1.0; end
    if nargin < 4, overlap = 0.5; end
    
    [nChan, nSamples] = size(emg_clean);
    winLen  = round(window_s * fs);
    stepLen = round(winLen * (1 - overlap));
    nWindows = floor((nSamples - winLen) / stepLen) + 1;
    
    nFeatures = 6;
    emg_features = zeros(nWindows, nChan * nFeatures);
    feature_base = {'RMS', 'MAV', 'ZCR', 'WL', 'SSC', 'VAR'};
    feature_names = {};
    for ch = 1:nChan
        for f = 1:nFeatures
            feature_names{end+1} = sprintf('CH%d_%s', ch, feature_base{f}); %#ok
        end
    end
    
    for w = 1:nWindows
        startIdx = (w-1) * stepLen + 1;
        endIdx   = startIdx + winLen - 1;
        
        for ch = 1:nChan
            x = emg_clean(ch, startIdx:endIdx);
            N = length(x);
            col_offset = (ch-1) * nFeatures;
            
            emg_features(w, col_offset + 1) = sqrt(mean(x.^2));
            emg_features(w, col_offset + 2) = mean(abs(x));
            zc = sum(abs(diff(sign(x))) > 0);
            emg_features(w, col_offset + 3) = zc / N;
            emg_features(w, col_offset + 4) = sum(abs(diff(x)));
            dx = diff(x);
            ssc = sum(abs(diff(sign(dx))) > 0);
            emg_features(w, col_offset + 5) = ssc / (N - 2);
            emg_features(w, col_offset + 6) = var(x);
        end
    end
end
