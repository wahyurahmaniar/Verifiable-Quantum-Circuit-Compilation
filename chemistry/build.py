"""Build one ANGLE circuit angle_k_K.kmb from a word table and its product plans.

usage: python build.py --words submission.npz --plans plans/c40 --k K --out angle_k_K.kmb

The plan files plans/kK_MODE_s{1,2,3}.json come from plan.py. MODE 'all' plans all 35 output bits.
MODE 'nolsb' plans output bits 1-6 of each word; the LSB of every word is then loaded by two products per word,
AND(F0 + b1, F1 + b0) and AND(F2 + b3, F3 + b2), where b0..b3 are the low address bits and F0..F3 the high
coefficients of the LSB's low-linear part (the table's LSBs must be low-linear, as in the C40 table's batches 4-14).
kickmix comes from the competition data: set QCC_DATA to that folder (it holds kickmix/).
"""
import argparse, os, sys, time
from pathlib import Path
import json
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / 'third_party' / 'mrmeows_planners')]
if os.environ.get('QCC_DATA'):
    sys.path.insert(0, str(Path(os.environ['QCC_DATA']) / 'kickmix'))
import rank_parity as core
from loader import compile_circuit, to_kickmix, NA


def lsb_products(ac):
    """Two paired products per word for the LSB outputs (low-linear LSBs)."""
    extra = []
    for j in range(5):
        o = 7 * j
        F = []
        for i in range(4):
            col = ac[1:, 1 << i, o]                       # high monomials 1..85
            F.append(sum(int(col[h - 1]) << h for h in range(1, 86)))
        f40 = 1 << (8 * j)
        extra.append((f40, 1 << 2, F[0], 1 << 1, F[1]))   # (F0 + b1)(F1 + b0): mixed b1 F1 + b0 F0
        extra.append((f40, 1 << 8, F[2], 1 << 4, F[3]))   # (F2 + b3)(F3 + b2): mixed b3 F3 + b2 F2
    return extra


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--words', required=True, help='submission.npz with angle_words (NA x 75)')
    ap.add_argument('--plans', required=True, help='folder with kK_MODE_s{1,2,3}.json')
    ap.add_argument('--k', type=int, required=True, help='circuit index 0..14')
    ap.add_argument('--out', required=True, help='output .kmb')
    a = ap.parse_args()
    words = np.load(a.words)['angle_words'].copy()
    assert words.shape == (NA, 75), f'the loader layout is fixed to {NA} rows x 75 words, got {words.shape}'
    found = sorted(Path(a.plans).glob(f'k{a.k}_*_s1.json'))
    assert len(found) == 1, f'expected one stage-1 plan for k {a.k} in {a.plans}'
    mode = found[0].name.split('_')[1]
    delta = core.delta_batch(words, 5, a.k)
    ac = core.coefficients(delta, 8, 4)
    stages, outs = {}, None
    for s in (1, 2, 3):
        p = json.load(open(Path(a.plans) / f'k{a.k}_{mode}_s{s}.json'))
        stages[s] = p['terms']; outs = p['outs']
    extra = lsb_products(ac) if mode == 'nolsb' else []
    t0 = time.time()
    E = compile_circuit(delta, stages, outs, extra)
    c = to_kickmix(E)
    c.to_file(a.out, format='kmb')
    print(f'k {a.k} {mode}: Toffolis {E.tof}, qubits {c.num_qubits}, {time.time() - t0:.1f} s', flush=True)


if __name__ == '__main__':
    main()
