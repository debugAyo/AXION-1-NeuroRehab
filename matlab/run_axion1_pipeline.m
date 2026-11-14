%% ===================================================================
%   AXION-1: Master Pipeline Runner (Task A - MATLAB)
%   NeuralVillage Neurotech Hackathon 2026
% ===================================================================

clear; clc; close all;
addpath('scripts');

fprintf('===============================================================\n');
fprintf('  AXION-1: Master Biosignal Processing Pipeline\n');
fprintf('===============================================================\n\n');

subjects = {'S001', 'S002', 'S003'};
runs = {'R04', 'R08', 'R12'};

all_eeg_features = [];
all_emg_features = [];
all_quality_eeg = [];
all_quality_emg = [];
all_labels = [];

fprintf('[+] Processing multi-subject PhysioNet dataset...\n');
fprintf('Outputs will be saved to output/ and figures/\n');
