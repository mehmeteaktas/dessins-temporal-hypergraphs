% Part of https://github.com/<user>/dessins-temporal-hypergraphs -- regenerates a figure of the paper.
%% rotation_from_data.m -- regenerates Figure 'rotation_from_data' (fig:negative) in MATLAB.
% Negative control: rotations read from the data. For random samples of 250-2000 threads
% (5 samples per size and community), local faces per 100 cycles, 100(F-c)/beta1, for five rotation systems
% on the same hypergraph. Bars: mean over samples; error bars: standard deviation over samples.
% All numbers are exactly the values plotted in the Python version.
clear; close all;

fs = 14;
set(groot, 'defaultAxesFontSize', fs);
set(groot, 'defaultAxesTitleFontSizeMultiplier', 1);
set(groot, 'defaultAxesLabelFontSizeMultiplier', 1);
set(groot, 'defaultTextFontSize', fs);

%% ------------------------------------------------------------------ data
sizes = [250 500 1000 2000];   % threads per sample
kind_labels = {'random (both)', 'shuffled in thread', 'timestamp', 'reply tree', 'face-maximizing'};
kind_colors = [0.7059 0.6980 0.6627; 0.5333 0.5294 0.5020; 0.1137 0.6196 0.4588; 0.3255 0.2902 0.7176; 0.8471 0.3529 0.1882];

% P(s): community s. mean / sd are 4x5 matrices: rows = sample sizes, columns = rotation systems
% in the order of kind_labels. beta1 = mean cycle rank of the samples of each size.
% tree_differs = share of threads with >=3 participants whose reply-tree order differs from the
% timestamp order (as a cyclic order).
P = struct([]);

% ---- Data Science
P(1).name = 'Data Science';
P(1).mean = [25.5626 20.6830 17.3643 19.4696 81.4664;
    8.5666 8.3450 6.9610 7.4943 51.0116;
    2.6259 2.8835 2.8424 2.7352 29.1100;
    1.1336 1.4764 1.4024 1.3043 20.0840];
P(1).sd   = [7.9323 9.3536 11.1673 9.5648 13.6128;
    1.5330 2.8562 2.4362 1.9785 4.2999;
    0.4932 0.3849 0.7265 0.8895 1.9344;
    0.1396 0.1427 0.4620 0.2901 1.8515];
P(1).beta1 = [15.6 71.2 253.2 858.8];
P(1).tree_differs = 0.0757;

% ---- Biology
P(2).name = 'Biology';
P(2).mean = [3.0955 2.8974 3.0838 3.5374 32.8778;
    1.4647 1.5373 1.3339 1.6079 23.8434;
    0.6193 0.7862 0.5968 0.6292 17.5951;
    0.3034 0.4634 0.3508 0.3795 12.7330];
P(2).sd   = [0.2878 0.3794 0.9727 0.9015 2.7370;
    0.1937 0.1661 0.2602 0.5048 0.8613;
    0.1048 0.1283 0.2669 0.2115 0.6770;
    0.0345 0.0280 0.1274 0.1430 0.8656];
P(2).beta1 = [176.2 463.8 1185.0 2777.4];
P(2).tree_differs = 0.1291;

%% ------------------------------------------------------------------ figure
fig = figure('Color','w','Units','inches','Position',[0.5 1 15 5.2]);
tl = tiledlayout(1,2,'TileSpacing','compact','Padding','compact');
ax_all = gobjects(1,2);
for s = 1:numel(P)
    ax = nexttile; hold(ax,'on'); ax_all(s) = ax;
    hb = bar(ax, 1:numel(sizes), P(s).mean, 'grouped', 'BarWidth', 0.9, 'EdgeColor', 'none');
    for k = 1:numel(hb)
        hb(k).FaceColor = kind_colors(k,:);
        % error bars at the centre of each bar
        errorbar(ax, hb(k).XEndPoints, P(s).mean(:,k)', P(s).sd(:,k)', 'k', ...
            'LineStyle', 'none', 'LineWidth', 1.2, 'CapSize', 0, 'HandleVisibility', 'off');
    end
    ticks = arrayfun(@(i) sprintf('%d threads\\newline\\beta_1\\approx%.0f', sizes(i), P(s).beta1(i)), ...
        1:numel(sizes), 'UniformOutput', false);
    set(ax, 'XTick', 1:numel(sizes), 'XTickLabel', ticks, 'TickLabelInterpreter', 'tex');
    xlim(ax, [0.45 numel(sizes)+0.55]);
    title(ax, sprintf('%s: reply tree \\neq timestamp in %.0f%% of threads (\\geq3 people)', ...
        P(s).name, 100*P(s).tree_differs));
    ylabel(ax, 'local faces per 100 cycles');
    box(ax, 'off');
end
linkaxes(ax_all, 'y');   % shared y-axis
ylim(ax_all(1), [0 inf]);
lg = legend(hb, kind_labels, 'NumColumns', 5, 'Orientation', 'horizontal', 'Box', 'off', 'FontSize', fs);
lg.Layout.Tile = 'south';

exportgraphics(fig, 'rotation_from_data_matlab.pdf', 'ContentType', 'vector');

set(groot, 'defaultAxesFontSize', 'remove', 'defaultAxesTitleFontSizeMultiplier', 'remove', ...
    'defaultAxesLabelFontSizeMultiplier', 'remove', 'defaultTextFontSize', 'remove');
