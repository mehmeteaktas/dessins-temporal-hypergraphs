% Part of https://github.com/<user>/dessins-temporal-hypergraphs -- regenerates a figure of the paper.
%% ablation.m -- regenerates Figure 'ablation' (fig:ablation) in MATLAB.
% Net local faces per 100 cycles, 100(F-c)/beta1, at beta1 = 10,000, for each community and four setups.
% Values: mean over runs, read at the first point where beta1 >= 10,000 (exactly as in the Python figure).
clear; close all;

fs = 14;
set(groot, 'defaultAxesFontSize', fs);
set(groot, 'defaultAxesTitleFontSizeMultiplier', 1);
set(groot, 'defaultAxesLabelFontSizeMultiplier', 1);
set(groot, 'defaultTextFontSize', fs);

%% ------------------------------------------------------------------ data
names = {'Data Science', 'Artificial Intelligence', 'Biology', 'Astronomy', 'Academia'};
setup_labels = {'shuffled order, random rule', 'real order, random rule', 'real order, hub rule', 'real order, reply rule (main)'};
setup_colors = [0.8275 0.8196 0.7804; 0.5333 0.5294 0.5020; 0.4980 0.4667 0.8667; 0.2353 0.2039 0.5373];
% V: rows = communities (order of names), columns = setups (order of setup_labels)
V = [2.3378 3.9188 4.2687 4.5086;
     4.9648 7.9491 9.2707 9.1912;
     4.5613 7.9910 9.2656 9.2068;
     6.1092 8.4653 9.0792 9.2871;
     2.5732 8.6103 9.4436 9.4343];

%% ------------------------------------------------------------------ figure
fig = figure('Color','w','Units','inches','Position',[0.5 1 14 5.5]);
ax = axes(fig); hold(ax,'on');
hb = bar(ax, 1:numel(names), V, 'grouped', 'BarWidth', 0.85, 'EdgeColor', 'none');
for k = 1:numel(hb)
    hb(k).FaceColor = setup_colors(k,:);
    % value labels above each bar
    text(ax, hb(k).XEndPoints, hb(k).YEndPoints + 0.12, compose('%.1f', V(:,k)), ...
        'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', 'FontSize', fs);
end
set(ax, 'XTick', 1:numel(names), 'XTickLabel', names);
xlim(ax, [0.45 numel(names) + 0.55]);
ylim(ax, [0 12]);
ylabel(ax, {'net local faces per 100 cycles', 'at \beta_1 = 10,000'});
legend(hb, setup_labels, 'NumColumns', 2, 'Location', 'northoutside', 'Box', 'off', 'FontSize', fs);
box(ax, 'off');

exportgraphics(fig, 'ablation_matlab.pdf', 'ContentType', 'vector');

set(groot, 'defaultAxesFontSize', 'remove', 'defaultAxesTitleFontSizeMultiplier', 'remove', ...
    'defaultAxesLabelFontSizeMultiplier', 'remove', 'defaultTextFontSize', 'remove');
