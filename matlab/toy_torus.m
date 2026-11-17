% Part of https://github.com/<user>/dessins-temporal-hypergraphs -- regenerates a figure of the paper.
%% toy_torus.m -- panel (c) of fig:static: the dessin of row 3 of tab:static-rotations on the torus.
% Drawn as a square [0,L]^2 whose opposite sides are glued (single arrows: left/right, double: top/bottom).
% Hypergraph a = {1,2,3}, b = {1,2,4}, c = {3,4}; darts numbered as in the table:
%   1 = 1a, 2 = 2a, 3 = 3a, 4 = 1b, 5 = 2b, 6 = 4b, 7 = 3c, 8 = 4c.
% Rotations read counterclockwise off this drawing: a: (1 2 3), b: (4 5 6), c: (7 8)  -> row 3,
% one face, g = 1. Purple: cycle 1 a 2 b (wraps left/right). Orange: cycle a 3 c 4 b 2 (wraps top/bottom).
clear; close all;

fs = 14;                     % vertex labels
fsd = 12;                    % dart numbers
set(groot, 'defaultAxesFontSize', fs);
set(groot, 'defaultTextFontSize', fs);

%% ------------------------------------------------------------------ data
names  = {'1', '2', '3', '4', 'a', 'b', 'c'};
isUser = [true true true true false false false];
darts  = [1 5; 2 5; 3 5; 1 6; 2 6; 4 6; 3 7; 4 7];      % [user thread], dart k = row k

L = 6;
P = [1.1 3.0; 3.6 3.0; 2.35 4.5; 4.85 1.4; 2.35 3.0; 4.85 3.0; 3.6 5.3];   % rows: 1 2 3 4 a b c
off = zeros(8, 2);
off(4,:) = [-1 0];           % dart 4 (1b) wraps through the left/right sides
off(8,:) = [0 -1];           % dart 8 (4c) wraps through the top/bottom sides

C1   = [0.3255 0.2902 0.7176];   % purple
C2   = [0.8471 0.3529 0.1882];   % orange
dark = [0 0 0];
sqc  = [0.9451 0.9373 0.9098];

%% ------------------------------------------------------------------ figure
fig = figure('Color','w','Units','inches','Position',[1 1 5 5]);
ax = axes(fig, 'Position', [0.03 0.03 0.94 0.94]); hold(ax,'on'); axis(ax,'equal'); axis(ax,'off');
patch(ax, [0 L L 0], [0 0 L L], sqc, 'EdgeColor','none');

for k = [1 2 5 4]            % purple cycle: 1a 2a 2b 1b
    torus_edge(ax, P, darts(k,:), off(k,:), L, [0 0], C1, 3);
end
for k = [3 7 8 6]            % orange cycle: 3a 3c 4c 4b
    torus_edge(ax, P, darts(k,:), off(k,:), L, [0 0], C2, 3);
end
for k = [5 2]                % 2b and 2a also belong to the orange cycle: shifted copy
    torus_edge(ax, P, darts(k,:), off(k,:), L, [0 -0.13], C2, 3);
end

% dart numbers at the middle of each dart (for a wrapping dart: of its first piece)
for k = 1:8
    m = torus_edge(ax, P, darts(k,:), off(k,:), L, [0 0], 'none', 0.01);
    text(ax, m(1), m(2), num2str(k), 'FontSize', fsd, 'BackgroundColor', 'w', 'Margin', 1, ...
        'HorizontalAlignment','center', 'VerticalAlignment','middle');
end

% vertices
for i = 1:7
    if isUser(i)
        plot(ax, P(i,1), P(i,2), 'o', 'MarkerSize', 26, 'MarkerFaceColor', dark, 'MarkerEdgeColor', dark);
        text(ax, P(i,1), P(i,2), names{i}, 'Color', 'w', 'HorizontalAlignment','center');
    else
        plot(ax, P(i,1), P(i,2), 'o', 'MarkerSize', 26, 'MarkerFaceColor', 'w', ...
            'MarkerEdgeColor', dark, 'LineWidth', 2);
        text(ax, P(i,1), P(i,2), names{i}, 'FontAngle', 'italic', 'HorizontalAlignment','center');
    end
end

% square border and gluing marks
plot(ax, [0 L L 0 0], [0 0 L L 0], '-', 'Color', dark, 'LineWidth', 1.5);
plot(ax, [0 L], [L/2 L/2], '^', 'MarkerSize', 9, 'MarkerFaceColor', dark, 'MarkerEdgeColor', dark);
plot(ax, [L/2-0.15 L/2+0.15 L/2-0.15 L/2+0.15], [0 0 L L], '>', 'MarkerSize', 9, ...
    'MarkerFaceColor', dark, 'MarkerEdgeColor', dark);
xlim(ax, [-0.3 L+0.3]); ylim(ax, [-0.3 L+0.3]);

exportgraphics(fig, 'toy_torus.pdf', 'ContentType', 'vector');
set(groot, 'defaultAxesFontSize', 'remove', 'defaultTextFontSize', 'remove');

%% ------------------------------------------------------------------ local functions
function mid = torus_edge(ax, P, dart, k, L, shift, col, lw)
% draw dart [user thread] on the square; k = lift of the thread end in units of L.
% Returns the midpoint of the first drawn piece (used for the dart number).
pu = P(dart(1),:) + shift; pt = P(dart(2),:) + shift;
pieces = {[pu; pt + L*k]};
if any(k), pieces{end+1} = [pu - L*k; pt]; end
mid = [NaN NaN];
for i = 1:numel(pieces)
    [a, b, ok] = clipseg(pieces{i}(1,:), pieces{i}(2,:), L);
    if ok
        if ~strcmp(col, 'none')
            plot(ax, [a(1) b(1)], [a(2) b(2)], '-', 'Color', col, 'LineWidth', lw);
        end
        if any(isnan(mid)), mid = (a + b) / 2; end
    end
end
end

function [a, b, ok] = clipseg(p, q, L)
% Liang-Barsky clipping of segment p-q to [0,L]^2
d = q - p; t0 = 0; t1 = 1; ok = true;
Pc = [-d(1), d(1), -d(2), d(2)];
Qc = [p(1), L - p(1), p(2), L - p(2)];
for i = 1:4
    if Pc(i) == 0
        if Qc(i) < 0, ok = false; break; end
    else
        rr = Qc(i) / Pc(i);
        if Pc(i) < 0, t0 = max(t0, rr); else, t1 = min(t1, rr); end
    end
end
if t0 > t1, ok = false; end
a = p + t0*d; b = p + t1*d;
end
