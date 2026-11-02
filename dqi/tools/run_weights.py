"""Run a full DQI circuit on shots with fixed error weights; report value/phase failures per weight.
usage: python run_weights.py dqi.kmb 15,16,31 [batches]   (256 shots per batch and weight)
Set QCC_DATA to the competition data folder.
"""
import sys
import numpy as np
import os
from pathlib import Path as _P
_D = _P(os.environ['QCC_DATA'])   # competition data folder: kickmix/, verifiers/
sys.path[:0] = [str(_D / 'kickmix'), str(_D / 'verifiers')]
import kickmix as km
from dqi import verify_submission_dqi as V

path = sys.argv[1]; weights = [int(x) for x in sys.argv[2].split(',')]; nb = int(sys.argv[3]) if len(sys.argv) > 3 else 1
circuit = km.Circuit.from_file(path, format='kmb')
spec = V.ProblemSpecDQI.benchmark_instance()
syn_q, mb_b, anc = V.validate_registers(circuit, spec)
SA, MA = km.array(syn_q), km.array(mb_b)
tables = V.FieldTables(km.GF2Field(spec.degree))
order = tables.order; rows = np.arange(1, spec.n + 1, dtype=np.int64)[:, None]
bs = 256
for w in weights:
    fails = 0
    for rep in range(nb):
        rng = np.random.default_rng(1000 * w + rep)
        mb = rng.integers(0, order, size=(bs, spec.m), endpoint=True, dtype=np.int64)
        syn = np.zeros((bs, spec.n), dtype=np.int64); ph = np.zeros(bs, dtype=bool)
        for s in range(bs):
            pos = rng.choice(spec.m, size=w, replace=False); vals = rng.integers(1, order, size=w, endpoint=True, dtype=np.int64)
            syn[s] = np.bitwise_xor.reduce(tables.antilog[(tables.log[vals][None, :] + rows * pos[None, :]) % order], axis=1)
            ph[s] = sum(int(x).bit_count() for x in vals & mb[s, pos]) & 1 == 1
        sim = km.Simulator(batch_size=bs, debug_print=False, counting_operations=False, seed=w + 17 * rep)
        sim.use_same_registers_as(circuit)
        inp = V.to_bits(syn, 12)
        sim.write_across_shots(SA, inp); sim.write_across_shots(MA, V.to_bits(mb, 12))
        sim.do(circuit)
        pf = sim.read_phase_flipped_across_shots(); rd = sim.read_across_shots(SA) ^ inp; junk = sim.read_across_shots(anc)
        ve = rd.any(axis=0) | junk.any(axis=0); pe = (pf ^ ph) & ~ve
        fails += int((ve | pe).sum())
    print(path.split('/')[-2], 'weight', w, 'failures', fails, 'of', nb * bs, flush=True)
