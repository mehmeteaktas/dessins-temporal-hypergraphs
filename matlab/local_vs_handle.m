% Part of https://github.com/<user>/dessins-temporal-hypergraphs -- regenerates a figure of the paper.
%% local_vs_handle.m -- regenerates Figure 'local_vs_handle' (fig:local-handle) in MATLAB.
% Local and global cycles of the toy hypergraph a={1,2,3}, b={1,2,4}, c={3,4} (beta1 = 2).
% (a) a rotation system on the sphere (drawn in the plane): F = 3, g = 0, both cycles local.
% (b) a rotation system on the torus, drawn as a square with opposite sides glued: F = 1, g = 1.
% (c) schematic torus with the two loops of the handle.
% Vertex coordinates are the ones used in the Python version; there, the rotations read
% counterclockwise off each drawing were checked to give F = 3, g = 0 in (a) and F = 1, g = 1 in (b).
clear; close all;

fs = 14;
set(groot, 'defaultAxesFontSize', fs);
set(groot, 'defaultAxesTitleFontSizeMultiplier', 1);
set(groot, 'defaultAxesLabelFontSizeMultiplier', 1);
set(groot, 'defaultTextFontSize', fs);

%% ------------------------------------------------------------------ data
% vertices: 1-4 are users (black), 5-7 are threads a, b, c (white)
names  = {'1', '2', '3', '4', 'a', 'b', 'c'};
isUser = [true true true true false false false];
% darts (incidences) as [user, thread]:  1a 2a 3a 1b 2b 4b 3c 4c
darts = [1 5; 2 5; 3 5; 1 6; 2 6; 4 6; 3 7; 4 7];

% colors
C1   = [0.3255 0.2902 0.7176];   % purple: cycle 1-a-2-b
C2   = [0.8471 0.3529 0.1882];   % orange: cycle a-3-c-4-b-2
F1   = [0.8078 0.7961 0.9647];   % face A fill
F2   = [0.9608 0.7686 0.7020];   % face B fill
gry  = [0.3725 0.3686 0.3529];   % ordinary edges
dark = [0.1725 0.1725 0.1647];   % vertices, square border
sqc  = [0.9451 0.9373 0.9098];   % torus square
torc = [0.8510 0.8392 0.8000];   % torus surface (c)

% (a) plane coordinates, rows in the order of names
Pa = [0 1.2; 0 -1.2; -2.6 0; 2.6 0; -1.3 0; 1.3 0; 0 -2.5];
cyc1 = [1 5 2 6];          % 1 a 2 b
cyc2 = [5 3 7 4 6 2];      % a 3 c 4 b 2

% (b) torus square [0,L]^2 and the lift of each dart's thread end (in units of L)
L  = 6;
Pb = [1.0 3.0; 4.0 3.0; 2.5 4.5; 5.4 1.4; 2.5 3.0; 5.4 3.0; 4.0 5.3];
off = zeros(size(darts,1), 2);
off(4,:) = [-1 0];         % dart 1b wraps through the left/right sides
off(8,:) = [0 -1];         % dart 4c wraps through the top/bottom sides
purple_darts = [1 2 5 4];  % 1a 2a 2b 1b
orange_darts = [3 7 8 6];  % 3a 3c 4c 4b  (+ 2b and 2a, drawn shifted)

%% ------------------------------------------------------------------ figure
fig = figure('Color','w','Units','inches','Position',[0.5 1 19 7]);
tl = tiledlayout(1,3,'TileSpacing','compact','Padding','compact');

% ---------------- (a) sphere
ax = nexttile; hold(ax,'on'); axis(ax,'equal'); axis(ax,'off');
patch(ax, Pa(cyc2,1), Pa(cyc2,2), F2, 'EdgeColor','none', 'FaceAlpha',0.6);
patch(ax, Pa(cyc1,1), Pa(cyc1,2), F1, 'EdgeColor','none', 'FaceAlpha',0.9);
for k = 1:size(darts,1)
    plot(ax, Pa(darts(k,:),1), Pa(darts(k,:),2), '-', 'Color', gry, 'LineWidth', 1.3);
end
c1 = [cyc1 cyc1(1)];
plot(ax, Pa(c1,1), Pa(c1,2), '-', 'Color', C1, 'LineWidth', 3.5);
c2 = [cyc2 cyc2(1)];
for k = 1:numel(cyc2)
    p = Pa(c2(k),:); q = Pa(c2(k+1),:);
    if isequal(sort(c2(k:k+1)), [2 5]) || isequal(sort(c2(k:k+1)), [2 6])   % edges shared with cycle 1
        [p, q] = shifted(p, q, 0.11);
    end
    plot(ax, [p(1) q(1)], [p(2) q(2)], '-', 'Color', C2, 'LineWidth', 3.5);
end
draw_vertices(ax, Pa, names, isUser, dark, fs);
text(ax, 0.25, 0.3, 'face A', 'Color', C1);
text(ax, -1.0, -1.4, 'face B', 'Color', C2);
text(ax, 1.9, 1.3, 'outer face', 'Color', gry);
text(ax, 0, -3.1, {'both cycles bound a face (a disk):', 'local cycles', ...
    'F = 3, g = 0:  \beta_1 = (F-c)+2g = 2+0'}, 'HorizontalAlignment','center', 'VerticalAlignment','top');
xlim(ax, [-3.2 3.2]); ylim(ax, [-5.0 1.9]);
title(ax, '(a) Sphere: two local cycles');

% ---------------- (b) torus as a square with opposite sides glued
ax = nexttile; hold(ax,'on'); axis(ax,'equal'); axis(ax,'off');
patch(ax, [0 L L 0], [0 0 L L], sqc, 'EdgeColor','none');
for k = 1:size(darts,1)
    torus_edge(ax, Pb, darts(k,:), off(k,:), L, [0 0], gry, 1.3);
end
for k = purple_darts
    torus_edge(ax, Pb, darts(k,:), off(k,:), L, [0 0], C1, 3.5);
end
for k = orange_darts
    torus_edge(ax, Pb, darts(k,:), off(k,:), L, [0 0], C2, 3.5);
end
for k = [5 2]   % 2b and 2a also belong to the orange cycle: draw a shifted copy
    torus_edge(ax, Pb, darts(k,:), off(k,:), L, [0 -0.12], C2, 3.5);
end
draw_vertices(ax, Pb, names, isUser, dark, fs);
% square border and gluing marks: single arrows on left/right, double arrows on top/bottom
plot(ax, [0 L L 0 0], [0 0 L L 0], '-', 'Color', dark, 'LineWidth', 1.6);
plot(ax, [0 L], [L/2 L/2], '^', 'MarkerSize', 9, 'MarkerFaceColor', dark, 'MarkerEdgeColor', dark);
plot(ax, [L/2-0.15 L/2+0.15 L/2-0.15 L/2+0.15], [0 0 L L], '>', 'MarkerSize', 9, ...
    'MarkerFaceColor', dark, 'MarkerEdgeColor', dark);
text(ax, L/2, -0.4, {'left/right sides glued,', 'top/bottom sides glued'}, 'Color', gry, ...
    'HorizontalAlignment','center', 'VerticalAlignment','top');
text(ax, L/2, -1.9, {'neither cycle bounds a face:', 'global cycles (one handle)', ...
    'F = 1, g = 1:  \beta_1 = (F-c)+2g = 0+2'}, 'HorizontalAlignment','center', 'VerticalAlignment','top');
xlim(ax, [-0.4 L+0.4]); ylim(ax, [-4.4 L+0.3]);
title(ax, '(b) Torus: the same two cycles are global');

% ---------------- (c) schematic torus
ax = nexttile; hold(ax,'on'); axis(ax,'off');
R = 2.0; r = 0.8;
[uu, vv] = meshgrid(linspace(0, 2*pi, 80), linspace(0, 2*pi, 40));
X = (R + r*cos(vv)) .* cos(uu);
Y = (R + r*cos(vv)) .* sin(uu);
Z = r*sin(vv);
surf(ax, X, Y, Z, 'FaceColor', torc, 'EdgeColor', 'none', 'FaceAlpha', 0.45);
camlight(ax, 'headlight'); lighting(ax, 'gouraud');
t  = linspace(0, 2*pi, 200);
v0 = pi/2.6;    % longitude: goes around the hole
plot3(ax, (R + r*cos(v0))*cos(t), (R + r*cos(v0))*sin(t), r*sin(v0)*ones(size(t)), '-', 'Color', C1, 'LineWidth', 3.5);
u0 = -pi/2.4;   % meridian: goes through the tube
plot3(ax, (R + r*cos(t))*cos(u0), (R + r*cos(t))*sin(u0), r*sin(t), '-', 'Color', C2, 'LineWidth', 3.5);
axis(ax, 'equal');
view(ax, 28, 32);   % = matplotlib azim -62, elev 32
xlim(ax, [-2.6 2.6]); ylim(ax, [-2.6 2.6]); zlim(ax, [-1.1 1.1]);
text(ax, 0.5, 0.08, {'one loop goes around the hole,', 'the other through the tube;', ...
    'neither can be shrunk to a point:', '\Delta g = 1 adds 2 to \beta_1'}, 'Units', 'normalized', ...
    'HorizontalAlignment','center', 'VerticalAlignment','top');
title(ax, '(c) What a handle adds (schematic)');

exportgraphics(fig, 'local_vs_handle_matlab.pdf', 'ContentType', 'vector');

set(groot, 'defaultAxesFontSize', 'remove', 'defaultAxesTitleFontSizeMultiplier', 'remove', ...
    'defaultAxesLabelFontSizeMultiplier', 'remove', 'defaultTextFontSize', 'remove');

%% ------------------------------------------------------------------ local functions
function draw_vertices(ax, P, names, isUser, dark, fs)
% black filled circles with white labels for users, white circles with black labels for threads
for i = 1:size(P,1)
    if isUser(i)
        plot(ax, P(i,1), P(i,2), 'o', 'MarkerSize', 24, 'MarkerFaceColor', dark, 'MarkerEdgeColor', dark);
        text(ax, P(i,1), P(i,2), names{i}, 'Color', 'w', 'FontSize', fs, ...
            'HorizontalAlignment','center', 'VerticalAlignment','middle');
    else
        plot(ax, P(i,1), P(i,2), 'o', 'MarkerSize', 24, 'MarkerFaceColor', 'w', ...
            'MarkerEdgeColor', dark, 'LineWidth', 1.6);
        text(ax, P(i,1), P(i,2), names{i}, 'Color', dark, 'FontSize', fs, ...
            'HorizontalAlignment','center', 'VerticalAlignment','middle');
    end
end
end

function [p, q] = shifted(p, q, d)
% move the segment p-q sideways by distance d (to draw two cycles along the same edge)
n = [-(q(2)-p(2)), q(1)-p(1)]; n = n / norm(n);
p = p + d*n; q = q + d*n;
end

function torus_edge(ax, P, dart, k, L, shift, col, lw)
% draw dart [user thread] on the square [0,L]^2; k = lift of the thread end in units of L.
% A wrapping dart is drawn as two pieces: one leaving the square, one re-entering on the glued side.
pu = P(dart(1),:) + shift; pt = P(dart(2),:) + shift;
pieces = {[pu; pt + L*k]};
if any(k)
    pieces{end+1} = [pu - L*k; pt];
end
for i = 1:numel(pieces)
    [a, b, ok] = clipseg(pieces{i}(1,:), pieces{i}(2,:), L);
    if ok
        plot(ax, [a(1) b(1)], [a(2) b(2)], '-', 'Color', col, 'LineWidth', lw);
    end
end
end

function [a, b, ok] = clipseg(p, q, L)
% Liang-Barsky clipping of segment p-q to the square [0,L]^2
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
