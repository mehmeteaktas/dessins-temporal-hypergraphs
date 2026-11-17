% Part of https://github.com/<user>/dessins-temporal-hypergraphs -- regenerates a figure of the paper.
%% bracket.m -- regenerates Figure 'bracket' (fig:bracket) in MATLAB.
% Net local faces per 100 cycles, 100(F-c)/beta1, on the same samples of 1,000 threads per community:
% online random rule (floor), online reply rule (main), offline face maximization (ceiling).
% Bars: mean over five samples; error bars: standard deviation over the five samples.
% All numbers are exactly the values plotted in the Python version.
clear; close all;

fs = 14;
set(groot, 'defaultAxesFontSize', fs);
set(groot, 'defaultAxesTitleFontSizeMultiplier', 1);
set(groot, 'defaultAxesLabelFontSizeMultiplier', 1);
set(groot, 'defaultTextFontSize', fs);

%% ------------------------------------------------------------------ data
names = {'Data Science', 'Artificial Intelligence', 'Biology', 'Astronomy', 'Academia'};
setup_labels = {'online, random rule (floor)', 'online, reply rule (main)', 'offline face maximization (ceiling)'};
setup_colors = [0.7059 0.6980 0.6627; 0.3255 0.2902 0.7176; 0.8471 0.3529 0.1882];
% rows = communities (order of names), columns = setups (order of setup_labels)
M  = [10.5243 11.6330 32.0678;
      12.6982 14.0823 23.7364;
      8.7359 9.1305 17.4438;
      8.7973 9.7482 12.9871;
      4.9664 5.1322 10.0310];   % mean
SD = [2.1247 1.2868 3.7951;
      1.2886 1.3134 1.6167;
      0.5831 0.3571 0.8778;
      0.5439 0.5702 1.7075;
      0.2610 0.2881 0.6212];   % standard deviation
beta1 = [248 564 1168 2034 3436];   % mean beta1 of the samples (reply rule)

%% ------------------------------------------------------------------ figure
fig = figure('Color','w','Units','inches','Position',[0.5 1 14 5.5]);
ax = axes(fig); hold(ax,'on');
hb = bar(ax, 1:numel(names), M, 'grouped', 'BarWidth', 0.8, 'EdgeColor', 'none');
for k = 1:numel(hb)
    hb(k).FaceColor = setup_colors(k,:);
    errorbar(ax, hb(k).XEndPoints, M(:,k)', SD(:,k)', 'k', 'LineStyle', 'none', ...
        'LineWidth', 1.2, 'CapSize', 6, 'HandleVisibility', 'off');
end
% tick labels: community name, and beta1 of its samples on a second line
ticks = arrayfun(@(i) sprintf('%s\\newline\\beta_1\\approx%.0f', names{i}, beta1(i)), ...
    1:numel(names), 'UniformOutput', false);
set(ax, 'XTick', 1:numel(names), 'XTickLabel', ticks, 'TickLabelInterpreter', 'tex');
xlim(ax, [0.45 numel(names) + 0.55]);
ylim(ax, [0 inf]);
ylabel(ax, 'net local faces per 100 cycles');
legend(hb, setup_labels, 'Location', 'northeast', 'Box', 'off', 'FontSize', fs);
box(ax, 'off');

exportgraphics(fig, 'bracket_matlab.pdf', 'ContentType', 'vector');

set(groot, 'defaultAxesFontSize', 'remove', 'defaultAxesTitleFontSizeMultiplier', 'remove', ...
    'defaultAxesLabelFontSizeMultiplier', 'remove', 'defaultTextFontSize', 'remove');
