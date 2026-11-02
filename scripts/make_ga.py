"""Draw graphical_abstract.png (repository root): the system behind this repository.

(a) pipeline from pinned inputs through our code and the official verifiers to the submission,
(b) structure of one ANGLE circuit, (c) the q18 DQI decoder stages with our five changes.

usage: python scripts/make_ga.py [--pdf]
Font: Times New Roman when installed, else a metric-compatible serif (Liberation Serif, TeX Gyre Termes).
Every text is checked to sit inside its box and not to touch any other text.
"""
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

ROOT = Path(__file__).resolve().parents[1]
C = dict(surface='#ffffff', ink='#0b0b0b', ink2='#52514e', ours_fill='#e8f1fc', ours_edge='#2a78d6',
         pub_fill='#f3f2ef', pub_edge='#898781', off_fill='#fdefe8', off_edge='#eb6834', arrow='#52514e',
         wire='#a9a7a0', badge='#2a78d6')
T1, T2 = 10.5, 9.5          # title and detail font sizes (pt)


class Canvas:
    """One panel drawn in inches (1 data unit = 1 inch); records texts for the overlap check."""

    def __init__(self, fig, rect):
        W, H = fig.get_size_inches()
        x, y, w, h = rect
        self.ax = fig.add_axes([x / W, y / H, w / W, h / H])
        self.ax.set_xlim(0, w); self.ax.set_ylim(0, h); self.ax.axis('off')
        self.texts = []

    def text(self, x, y, s, size=T2, color=None, box=None, **kw):
        t = self.ax.text(x, y, s, fontsize=size, color=color or C['ink'], ha=kw.pop('ha', 'center'),
                         va=kw.pop('va', 'center'), zorder=5, **kw)
        self.texts.append((t, box))
        return t

    def width(self, t):
        r = self.ax.figure.canvas.get_renderer()
        bb = t.get_window_extent(r)
        inv = self.ax.transData.inverted()
        return inv.transform((bb.x1, 0))[0] - inv.transform((bb.x0, 0))[0]

    def box(self, x0, y0, w, h, kind, lines=()):
        fill, edge = {'ours': (C['ours_fill'], C['ours_edge']), 'pub': (C['pub_fill'], C['pub_edge']),
                      'off': (C['off_fill'], C['off_edge'])}[kind]
        p = FancyBboxPatch((x0, y0), w, h, boxstyle='round,pad=0,rounding_size=0.05', facecolor=fill,
                           edgecolor=edge, linewidth=1.0, zorder=3)
        self.ax.add_patch(p)
        n, step = len(lines), 0.175
        for i, (s, size) in enumerate(lines):
            yy = y0 + h / 2 + (n - 1) * step / 2 - i * step
            self.text(x0 + w / 2, yy, s, size=size, color=C['ink'] if i == 0 else C['ink2'], box=p)
        return p

    def arrow(self, p, q):
        self.ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=8, linewidth=0.9,
                                          color=C['arrow'], shrinkA=0, shrinkB=0, zorder=2))

    def badge(self, x, y, n, r=0.072):
        self.ax.add_patch(Circle((x, y), r, facecolor=C['badge'], edgecolor='none', zorder=6))
        self.ax.text(x, y - 0.004, str(n), fontsize=7.5, color='#ffffff', ha='center', va='center',
                     fontweight='bold', zorder=7)


def panel_pipeline(cv):
    lanes = {'chem': 1.48, 'dqi': 0.90, 'inv': 0.32}
    bh, bw = 0.46, 1.40
    cols = [0.85, 2.45, 4.05, 5.65, 7.25]
    lx = 0.15
    for kind, label in (('ours', 'Our code and outputs'), ('pub', 'Public input'), ('off', 'Official verifier')):
        cv.box(lx, 1.96, 0.26, 0.15, kind)
        t = cv.text(lx + 0.36, 2.035, label, size=T2, color=C['ink2'], ha='left')
        lx += 0.36 + cv.width(t) + 0.45
    y = lanes['chem'] - bh / 2
    cv.box(cols[0] - bw / 2, y, bw, bh, 'pub', [('C40 table', T1), ('(9, 143, 40) words', T2)])
    cv.box(cols[1] - bw / 2, y, bw, bh, 'ours', [('plan.py', T1), ('GF(2) product plans', T2)])
    cv.box(cols[2] - bw / 2, y, bw, bh, 'ours', [('loader.py', T1), ('exact ANGLE emitter', T2)])
    cv.box(cols[3] - bw / 2, y, bw, bh, 'ours', [('15 ANGLE circuits', T1), ('4,503 Toffolis per pass', T2)])
    cv.box(cols[4] - bw / 2, y, bw, bh, 'off', [('dfthcsos verifier', T1), ('all 1,363 addresses', T2)])
    y = lanes['dqi'] - bh / 2
    cv.box(cols[0] - bw / 2, y, bw, bh, 'pub', [('q18 DQI source', T1), ('893-qubit bundle', T2)])
    x0 = cols[1] - bw / 2
    cv.box(x0, y, cols[2] + bw / 2 - x0, bh, 'ours', [('dqi/build.sh', T1), ('5 patches, rebuild, SHA-256 check', T2)])
    cv.box(cols[3] - bw / 2, y, bw, bh, 'ours', [('dqi.kmb', T1), ('892 qubits', T2)])
    cv.box(cols[4] - bw / 2, y, bw, bh, 'off', [('DQI verifier', T1), ('102,400 shots per salt', T2)])
    y = lanes['inv'] - bh / 2
    cv.box(cols[0] - bw / 2, y, bw, bh, 'pub', [('invsqrt.kmb', T1), ('62 qubits', T2)])
    fx0, fx1 = 8.24, 9.85
    fy0, fy1 = lanes['inv'] - bh / 2, lanes['chem'] + bh / 2
    p = cv.box(fx0, fy0, fx1 - fx0, fy1 - fy0, 'ours')
    mid = (fx0 + fx1) / 2
    for yy, s, size, col in ((1.36, 'score.py', T1, C['ink']), (1.18, 'geometric mean', T2, C['ink2']),
                             (0.62, 'package.sh', T1, C['ink']), (0.44, 'submission.zip', T2, C['ink2'])):
        cv.text(mid, yy, s, size=size, color=col, box=p)
    for a, b in zip(cols[:-1], cols[1:]):
        cv.arrow((a + bw / 2, lanes['chem']), (b - bw / 2, lanes['chem']))
    for a, b in ((0, 1), (2, 3), (3, 4)):
        cv.arrow((cols[a] + bw / 2, lanes['dqi']), (cols[b] - bw / 2, lanes['dqi']))
    for lane in ('chem', 'dqi'):
        cv.arrow((cols[4] + bw / 2, lanes[lane]), (fx0, lanes[lane]))
    cv.arrow((cols[0] + bw / 2, lanes['inv']), (fx0, lanes['inv']))
    cv.text(4.85, lanes['inv'] + 0.12, 'used unchanged', size=T2, color=C['ink2'])


def panel_loader(cv):
    ax = cv.ax
    ys = {'high': 2.45, 'cache': 2.15, 'low': 1.85, 'slots': 1.55, 'words': 1.25}
    labels = {'high': 'high bits (7)', 'cache': 'high cache (78)', 'low': 'low bits (4)', 'slots': 'low slots (4)',
              'words': 'words (5 × 8)'}
    x_start, x_end = 1.22, 5.72
    for k, y in ys.items():
        ax.plot([x_start, x_end], [y, y], color=C['wire'], linewidth=0.9, zorder=1, solid_capstyle='butt')
        cv.text(1.14, y, labels[k], size=T2, color=C['ink2'], ha='right')
    pad = 0.13
    top, bot, cache_bot = ys['high'] + pad, ys['words'] - pad, ys['cache'] - pad
    cv.box(1.30, cache_bot, 0.58, top - cache_bot, 'ours', [('cache', T1), ('78 AND', T2)])
    stages = [('stage 1', 'low 1-7', '4 slots', '106 products'), ('stage 2', 'low 8-11', '3 slots', '61 products'),
              ('stage 3', 'low 12-15', '4 slots', '61 products')]
    sx = 1.96
    for st in stages:
        cv.box(sx, bot, 0.85, top - bot, 'ours', [(st[0], T1)] + [(s, T2) for s in st[1:]])
        sx += 0.92
    cv.box(4.72, bot, 0.50, top - bot, 'ours', [('pure', T2), ('CNOT', T2)])
    cv.box(5.29, cache_bot, 0.42, top - cache_bot, 'ours', [('clear', T2), ('MBU', T2)])
    # one product: brackets under the Toffoli, the two mixed terms and the pure terms
    pieces = [r'$(h_1 \oplus l_2)\,(h_2 \oplus l_1)$', r'$\ =\ $', r'$h_1 l_1 \oplus h_2 l_2$', r'$\ \oplus\ $',
              r'$h_1 h_2 \oplus l_1 l_2$']
    y0 = 0.74
    arts = [ax.text(0, y0, s, fontsize=10.5, color=C['ink'], ha='left', va='baseline', zorder=5) for s in pieces]
    widths = [cv.width(a) for a in arts]
    x = (x_start + x_end) / 2 - sum(widths) / 2
    spans = []
    for a, w in zip(arts, widths):
        a.set_x(x); spans.append((x, x + w)); x += w
        cv.texts.append((a, None))
    yb = 0.56
    for (xa, xb), label in ((spans[0], 'one Toffoli'), (spans[2], 'two mixed terms'), (spans[4], 'CNOTs')):
        ax.plot([xa, xa, xb, xb], [yb + 0.06, yb, yb, yb + 0.06], color=C['ink2'], linewidth=0.8, zorder=4)
        cv.text((xa + xb) / 2, yb - 0.15, label, size=T2, color=C['ink2'])


def panel_dqi(cv):
    w, h = 0.70, 0.36
    xs = [0.43, 1.25, 2.07, 2.89, 3.71]
    ytop, ybot = 2.22, 1.46
    for x, s in zip(xs, ['prepare', 'extract', 'synthesis', 'convert', 'scan']):
        cv.box(x - w / 2, ytop - h / 2, w, h, 'pub', [(s, T2)])
    for x, s in zip(xs, ['restore', 'unextract', 'unsynthesis', 'unconvert']):
        cv.box(x - w / 2, ybot - h / 2, w, h, 'pub', [(s, T2)])
    for a, b in zip(xs[:-1], xs[1:]):
        cv.arrow((a + w / 2, ytop), (b - w / 2, ytop))
    for a, b in zip(xs[1:4], xs[0:3]):
        cv.arrow((a - w / 2, ybot), (b + w / 2, ybot))
    cv.ax.plot([xs[4], xs[4]], [ytop - h / 2, ybot], color=C['arrow'], linewidth=0.9, zorder=2)
    cv.arrow((xs[4], ybot), (xs[3] + w / 2, ybot))
    step = 0.17
    above, below = ytop + h / 2 + 0.11, ybot - h / 2 - 0.11
    for x, y, ns in ((xs[1], above, [1, 3]), (xs[2], above, [4]), (xs[1], below, [1, 2, 3, 5]), (xs[2], below, [4])):
        for i, n in enumerate(ns):
            cv.badge(x + (i - (len(ns) - 1) / 2) * step, y, n)
    items = ['P6 measured in extract, recomputed at node 7 in unextract', '892-qubit guard at the unextract peak',
             'no pole branch in groups 7, 8; carry bank 9-16', 'no zero flags in folds 18-20',
             'carry tests read 12-22 of the 24 marker bits']
    y = 0.94
    for n, s in enumerate(items, 1):
        cv.badge(0.22, y, n)
        cv.text(0.38, y, s, size=T2, color=C['ink'], ha='left')
        y -= 0.185


def check(fig, canvases):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    allt = [(t.get_window_extent(r), t.get_text(), box) for cv in canvases for t, box in cv.texts]
    for bb, s, box in allt:
        if box is not None:
            pb = box.get_window_extent(r)
            assert pb.x0 + 4 <= bb.x0 and bb.x1 <= pb.x1 - 4 and pb.y0 + 1 <= bb.y0 and bb.y1 <= pb.y1 - 1, ('text leaves its box', s)
    for i in range(len(allt)):
        for j in range(i + 1, len(allt)):
            a, b = allt[i][0], allt[j][0]
            if a.x0 < b.x1 - 1 and b.x0 < a.x1 - 1 and a.y0 < b.y1 - 1 and b.y0 < a.y1 - 1:
                raise AssertionError(('texts overlap', allt[i][1], allt[j][1]))


def main():
    plt.rcParams.update({'font.family': 'serif', 'mathtext.fontset': 'stix', 'pdf.fonttype': 42,
                         'font.serif': ['Times New Roman', 'Liberation Serif', 'TeX Gyre Termes', 'Nimbus Roman',
                                        'DejaVu Serif']})
    W, H = 10.0, 5.80
    fig = plt.figure(figsize=(W, H), facecolor=C['surface'])
    a = Canvas(fig, (0.0, 3.40, 10.0, 2.25))
    b = Canvas(fig, (0.0, 0.34, 5.76, 2.62))
    d = Canvas(fig, (5.82, 0.34, 4.18, 2.62))
    panel_pipeline(a); panel_loader(b); panel_dqi(d)
    for (x, y), s in (((5.0, 3.08), '(a)'), ((2.85, 0.06), '(b)'), ((5.82 + 2.09, 0.06), '(c)')):
        fig.text(x / W, y / H, s, ha='center', va='bottom', fontsize=10.5, color=C['ink'])
    check(fig, (a, b, d))
    outs = [ROOT / 'graphical_abstract.png'] + ([ROOT / 'graphical_abstract.pdf'] if '--pdf' in sys.argv else [])
    for out in outs:
        fig.savefig(out, dpi=220, facecolor=C['surface'])
        print('wrote', out.name)


if __name__ == '__main__':
    main()
