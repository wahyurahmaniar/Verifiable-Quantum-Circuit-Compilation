"""Search exact product plans for the three low stages of each ANGLE circuit of a word table.

usage: python plan.py --words submission.npz --plans plans/new --k 0,1,...,14 [--seeds 6]

Per circuit k and stage (low masks 1-7, 8-11, 12-15) it runs mrmeows' kernel planners (third_party) with group-3
relations and plane modes 'all', 'triples' and 'pairs', stepping the relation count up while a plan still exists,
and keeps the plan with the fewest products in plans/kK_MODE_sS.json. MODE is 'nolsb' when the LSB outputs are
low-linear (they are then loaded by build.py's two LSB products per word), else 'all'.
Run on the C40 table, this search reproduces plans/c40 file for file (about 90 s for all 15 circuits).
"""
import argparse, json, os, sys, time
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / 'third_party' / 'mrmeows_planners')]
import rank_parity as core
from balanced_plan import plan_balanced
from streamed_plan import plan_tensor

SL = {1: (1, 8), 2: (8, 12), 3: (12, 16)}


def lsb_structured(ac):
    lsb = [7 * j for j in range(5)]
    sub = ac[1:85, 1:, :][:, :, lsb]
    return all(not sub[:, l - 1, :].any() for l in range(1, 16) if l not in (1, 2, 4, 8))


def plan_circuit(words, k, pdir, seeds):
    delta = core.delta_batch(words, 5, k); ac = core.coefficients(delta, 8, 4)
    mode = 'nolsb' if lsb_structured(ac) else 'all'
    outs = [o for o in range(35) if not (mode == 'nolsb' and o % 7 == 0)]; m = len(outs)
    res = []
    for st in (1, 2, 3):
        lo, hi = SL[st]; L = hi - lo; sub = ac[1:, lo:hi, :][:, :, outs]
        path = f'{pdir}/k{k}_{mode}_s{st}.json'; best = None
        cfgs = [(plan_tensor, 'cyclic', 3, pm) for pm in ('all', 'triples')] + \
               [(plan_balanced, 'balanced', 3, pm) for pm in ('all', 'triples', 'pairs')]
        if L == 4:
            cfgs += [(plan_tensor, 'cyclic', 4, 'original'), (plan_tensor, 'cyclic', 4, 'pairs')]
        for fn, name, g, pm in cfgs:
            # start low enough to always succeed, then step the relation count up (keeping parity)
            n = (L * m) % 2 + (10 if L == 4 else 20)
            if best is not None:
                n = L * m - 2 * (best['pairs'] - 1)
            while True:
                got = None
                for s in range(seeds):
                    try:
                        t, r = fn(sub, group_size=g, nrelations=n, seed=s, trials=24, plane_mode=pm)
                    except ValueError:
                        t = None
                    if t is not None:
                        got = (t, r, s); break
                if got is None:
                    break
                t, r, s = got
                if best is None or r['pairs'] < best['pairs']:
                    best = {'pairs': r['pairs'], 'fn': name, 'group_size': g, 'plane_mode': pm, 'nrelations': n, 'seed': s,
                            'outs': outs, 'low_masks': list(range(lo, hi)), 'terms': t}
                    json.dump(best, open(path, 'w'))
                n = L * m - 2 * (best['pairs'] - 1)
        res.append(best['pairs'])
    print(f'k{k} {mode}: stages {res} -> products {sum(res)} (+{10 if mode == "nolsb" else 0} LSB)', flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--words', required=True)
    ap.add_argument('--plans', required=True)
    ap.add_argument('--k', default=','.join(str(i) for i in range(15)))
    ap.add_argument('--seeds', type=int, default=6, help='seeds tried per relation count')
    a = ap.parse_args()
    words = np.load(a.words)['angle_words'].copy()
    os.makedirs(a.plans, exist_ok=True)
    for k in (int(x) for x in a.k.split(',')):
        t0 = time.time(); plan_circuit(words, k, a.plans, a.seeds); print(f'  ({time.time() - t0:.0f} s)', flush=True)


if __name__ == '__main__':
    main()
