"""Per-task ratios and the competition score from official verifier outputs.

usage: python scripts/score.py --invsqrt INV.json --dqi DQI.json --chem CHEM.json
       python scripts/score.py --invsqrt-cost 100568.5 --dqi DQI.json --chem CHEM.json
Score = cube root of the product of the three ratios reference cost / cost (the geometric mean).
"""
import argparse, json

# reference (baseline) costs, as used in public verified releases of this competition
REFERENCE = {'invsqrt': 2076774.233715282, 'dqi': 24439473914136.668, 'dfthcsos': 3355599588.3155365}


def cost(path):
    d = json.load(open(path))
    assert d['status'] == 'PASS', (path, d['status'])
    return float(d['score'])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--invsqrt'); ap.add_argument('--invsqrt-cost', type=float)
    ap.add_argument('--dqi', required=True); ap.add_argument('--chem', required=True)
    a = ap.parse_args()
    costs = {'invsqrt': a.invsqrt_cost if a.invsqrt_cost else cost(a.invsqrt), 'dqi': cost(a.dqi), 'dfthcsos': cost(a.chem)}
    prod = 1.0
    for task, c in costs.items():
        r = REFERENCE[task] / c; prod *= r
        print(f'{task:9s} cost {c:.6e}  ratio {r:.4f}')
    print(f'score {prod ** (1 / 3):.5f}')


if __name__ == '__main__':
    main()
