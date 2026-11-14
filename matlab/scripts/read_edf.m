function [data, header] = read_edf(filename)
% READ_EDF  Read European Data Format (EDF/EDF+) files
%   [data, header] = read_edf(filename)
%
%   AXION-1 Project | NeuralVillage Neurotech Hackathon 2026

    fid = fopen(filename, 'rb');
    if fid == -1
        error('Cannot open file: %s', filename);
    end
    
    try
        header.version     = strtrim(fread(fid, 8, '*char')');
        header.patient     = strtrim(fread(fid, 80, '*char')');
        header.recording   = strtrim(fread(fid, 80, '*char')');
        header.startdate   = strtrim(fread(fid, 8, '*char')');
        header.starttime   = strtrim(fread(fid, 8, '*char')');
        header.headerBytes = str2double(fread(fid, 8, '*char')');
        header.reserved    = strtrim(fread(fid, 44, '*char')');
        header.numRecords  = str2double(fread(fid, 8, '*char')');
        header.duration    = str2double(fread(fid, 8, '*char')');
        header.numSignals  = str2double(fread(fid, 4, '*char')');
        
        ns = header.numSignals;
        
        header.labels       = cellstr(reshape(fread(fid, 16*ns, '*char')', 16, ns)');
        header.transducer   = cellstr(reshape(fread(fid, 80*ns, '*char')', 80, ns)');
        header.physDim      = cellstr(reshape(fread(fid, 8*ns, '*char')', 8, ns)');
        header.physMin      = str2double(cellstr(reshape(fread(fid, 8*ns, '*char')', 8, ns)'))';
        header.physMax      = str2double(cellstr(reshape(fread(fid, 8*ns, '*char')', 8, ns)'))';
        header.digMin       = str2double(cellstr(reshape(fread(fid, 8*ns, '*char')', 8, ns)'))';
        header.digMax       = str2double(cellstr(reshape(fread(fid, 8*ns, '*char')', 8, ns)'))';
        header.prefilter    = cellstr(reshape(fread(fid, 80*ns, '*char')', 80, ns)');
        header.samplesPerRecord = str2double(cellstr(reshape(fread(fid, 8*ns, '*char')', 8, ns)'))';
        fread(fid, 32*ns, '*char');
        
        for i = 1:ns
            header.labels{i} = strtrim(regexprep(header.labels{i}, '\.+$', ''));
        end
        
        header.fs = header.samplesPerRecord(1) / header.duration;
        
        scaleFactor = (header.physMax - header.physMin) ./ ...
                      (header.digMax - header.digMin);
        offset = header.physMax - scaleFactor .* header.digMax;
        
        refSamples = header.samplesPerRecord(1);
        totalSamples = header.numRecords * refSamples;
        data = zeros(ns, totalSamples);
        
        for rec = 1:header.numRecords
            for sig = 1:ns
                nSamp = header.samplesPerRecord(sig);
                rawSamples = fread(fid, nSamp, 'int16');
                if nSamp == refSamples
                    startIdx = (rec-1) * nSamp + 1;
                    endIdx   = startIdx + nSamp - 1;
                    data(sig, startIdx:endIdx) = rawSamples' * scaleFactor(sig) + offset(sig);
                end
            end
        end
        
    catch ME
        fclose(fid);
        rethrow(ME);
    end
    
    fclose(fid);
end
