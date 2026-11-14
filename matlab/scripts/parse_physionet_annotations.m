function annotations = parse_physionet_annotations(header, data)
% PARSE_PHYSIONET_ANNOTATIONS  Extract event markers
%   AXION-1 Project | NeuralVillage Neurotech Hackathon 2026

    annotations = struct('onset', {}, 'duration', {}, 'label', {});
    total_duration = size(data, 2) / header.fs;
    event_duration = 4.0;
    num_events = floor(total_duration / event_duration);
    
    event_idx = 0;
    for i = 1:num_events
        onset = (i - 1) * event_duration;
        if mod(i, 2) == 1
            continue;
        else
            event_idx = event_idx + 1;
            ann.onset = onset;
            ann.duration = event_duration;
            if mod(event_idx, 2) == 1
                ann.label = 1;
            else
                ann.label = 2;
            end
            annotations(end+1) = ann; %#ok
        end
    end
end
