function [features, W, labels_out] = extract_csp_features(eeg_clean, fs, annotations, m)
% EXTRACT_CSP_FEATURES  Common Spatial Pattern feature extraction
%   AXION-1 Project | NeuralVillage Neurotech Hackathon 2026

    if nargin < 4, m = 3; end
    nChan = size(eeg_clean, 1);
    epoch_duration = 3.0;
    epoch_samples  = round(epoch_duration * fs);
    
    epochs = [];
    labels_out = [];
    
    for i = 1:length(annotations)
        onset_sample = round(annotations(i).onset * fs) + 1;
        end_sample   = onset_sample + epoch_samples - 1;
        if end_sample > size(eeg_clean, 2), continue; end
        
        if annotations(i).label == 1 || annotations(i).label == 2
            epoch = eeg_clean(:, onset_sample:end_sample);
            epochs = cat(3, epochs, epoch);
            labels_out(end+1, 1) = annotations(i).label;
        end
    end
    
    nTrials = size(epochs, 3);
    if nTrials == 0
        error('No valid epochs found!');
    end
    
    idx_c1 = find(labels_out == 1);
    idx_c2 = find(labels_out == 2);
    
    R1 = zeros(nChan);
    R2 = zeros(nChan);
    
    for i = 1:length(idx_c1)
        X = epochs(:, :, idx_c1(i));
        R1 = R1 + (X * X') / trace(X * X');
    end
    R1 = R1 / length(idx_c1);
    
    for i = 1:length(idx_c2)
        X = epochs(:, :, idx_c2(i));
        R2 = R2 + (X * X') / trace(X * X');
    end
    R2 = R2 / length(idx_c2);
    
    Rc = R1 + R2;
    regularization = 1e-6 * trace(Rc) / nChan;
    Rc_reg = Rc + regularization * eye(nChan);
    
    [W_full, D] = eig(R1, Rc_reg);
    [~, sortIdx] = sort(diag(D), 'descend');
    W_full = W_full(:, sortIdx);
    
    m = min(m, floor(nChan / 2));
    selectedIdx = [1:m, (nChan-m+1):nChan];
    W_selected = W_full(:, selectedIdx);
    W = W_full;
    
    features = zeros(nTrials, 2*m);
    for t = 1:nTrials
        X = epochs(:, :, t);
        Z = W_selected' * X;
        v = var(Z, 0, 2);
        features(t, :) = log(v / sum(v))';
    end
end
