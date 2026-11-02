"""Failure census: run two DQI circuits on the same verifier-distributed shots and report every failing shot of either.

usage: python census.py A.kmb B.kmb NBATCH MASTERSEED [WORKERS]
Set QCC_DATA to the competition data folder.
"""
import sys, concurrent.futures, multiprocessing as mp
import numpy as np
import os
from pathlib import Path as _P
_D = _P(os.environ['QCC_DATA'])   # competition data folder: kickmix/, verifiers/
sys.path[:0] = [str(_D / 'kickmix'), str(_D / 'verifiers')]
import kickmix as km
from dqi import verify_submission_dqi as V

pa, pb, nbat, master = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
workers = int(sys.argv[5]) if len(sys.argv) > 5 else 2
spec = V.ProblemSpecDQI.benchmark_instance()
wp = V.optimal_dqi_weights(spec.m, spec.max_errors, spec.degree, spec.r) ** 2
tables = V.FieldTables(km.GF2Field(spec.degree))
circs = []
for p in (pa, pb):
    c = km.Circuit.from_file(p, format='kmb'); sq, mb, anc = V.validate_registers(c, spec)
    circs.append((c, km.array(sq), km.array(mb), anc))
seeds = np.random.SeedSequence(master).generate_state(2 * nbat, dtype=np.uint64).reshape(-1, 2)
bs = 256

def run(i):
    rs, ss = int(seeds[i, 0]), int(seeds[i, 1])
    w = np.random.default_rng(rs).choice(len(wp), size=bs, p=wp)
    syn, mb, ph = V.sample_shots(spec, tables, np.random.default_rng(rs), bs, wp)
    out = []
    for name, (c, SA, MA, anc) in zip('AB', circs):
        sim = km.Simulator(batch_size=bs, debug_print=False, counting_operations=False, seed=ss)
        sim.use_same_registers_as(c)
        inp = V.to_bits(syn, 12)
        sim.write_across_shots(SA, inp); sim.write_across_shots(MA, V.to_bits(mb, 12))
        sim.do(c)
        pf = sim.read_phase_flipped_across_shots(); rd = sim.read_across_shots(SA) ^ inp; junk = sim.read_across_shots(anc)
        ve = rd.any(axis=0) | junk.any(axis=0); pe = (pf ^ ph) & ~ve
        for s in np.flatnonzero(ve | pe):
            out.append((name, i, int(s), int(w[s]), 'value' if ve[s] else 'phase'))
    return i, out

if __name__ == '__main__':
    tot = {'A': 0, 'B': 0}
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context('fork')) as pool:
        for i, out in pool.map(run, range(nbat)):
            for o in out:
                tot[o[0]] += 1; print('FAIL', *o, flush=True)
            if i % 50 == 49: print('done', (i + 1) * bs, 'shots', tot, flush=True)
    print('total', tot, 'shots', nbat * bs)
