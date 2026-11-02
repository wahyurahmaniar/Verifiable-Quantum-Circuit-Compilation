"""Re-run the official DQI verification batches and report every failing shot with its error weight and wrong wires.
usage: python diag_verify.py dqi.kmb [salt] [batch,list]   (salt '' is the default)
Set QCC_DATA to the competition data folder.
"""
import sys, json, concurrent.futures, multiprocessing as mp
import numpy as np
import os
from pathlib import Path as _P
_D = _P(os.environ['QCC_DATA'])   # competition data folder: kickmix/, verifiers/
sys.path[:0] = [str(_D / 'kickmix'), str(_D / 'verifiers')]
import kickmix as km
from dqi import verify_submission_dqi as V

path = sys.argv[1]; salt = sys.argv[2] if len(sys.argv) > 2 else ''
only = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 and sys.argv[3] else None
circuit = km.Circuit.from_file(path, format='kmb')
spec = V.ProblemSpecDQI.benchmark_instance()
h = V._circuit_sha256(circuit)
seed_src = sys.argv[4] if len(sys.argv) > 4 else None
if seed_src: h = V._circuit_sha256(km.Circuit.from_file(seed_src, format='kmb'))
base_seed = V._initial_seed(h, salt)
syn_q, mb_b, anc = V.validate_registers(circuit, spec)
SA, MA = km.array(syn_q), km.array(mb_b)
wp = V.optimal_dqi_weights(spec.m, spec.max_errors, spec.degree, spec.r) ** 2
tables = V.FieldTables(km.GF2Field(spec.degree))
bs = V.DEFAULT_BATCH_SIZE
starts = range(0, spec.num_shots, bs)
seeds = np.random.SeedSequence(base_seed, pool_size=8).generate_state(8 * len(starts), dtype=np.uint64).reshape(-1, 2, 4)
tasks = [(i, s, int.from_bytes(seeds[i, 0], 'little'), int.from_bytes(seeds[i, 1], 'little')) for i, s in enumerate(starts)]
if only is not None: tasks = [t for t in tasks if t[0] in only]

def run(task):
    i, start, rs, ss = task
    import os
    if os.environ.get('SIMSEED'): ss = int(os.environ['SIMSEED'])
    rng = np.random.default_rng(rs)
    weights = np.random.default_rng(rs).choice(len(wp), size=bs, p=wp)
    syn, mb, ph = V.sample_shots(spec, tables, rng, bs, wp)
    sim = km.Simulator(batch_size=bs, debug_print=False, counting_operations=False, seed=ss)
    sim.use_same_registers_as(circuit)
    inp = V.to_bits(syn, spec.degree)
    sim.write_across_shots(SA, inp); sim.write_across_shots(MA, V.to_bits(mb, spec.degree))
    sim.do(circuit)
    pf = sim.read_phase_flipped_across_shots()
    rd = sim.read_across_shots(SA) ^ inp
    junk = sim.read_across_shots(anc)
    ve = rd.any(axis=0) | junk.any(axis=0)
    pe = (pf ^ ph) & ~ve
    out = []
    for s in np.flatnonzero(ve | pe):
        out.append(dict(batch=i, shot=int(s), weight=int(weights[s]), value=bool(ve[s]), phase=bool(pe[s]),
                        syn_words=sorted(set(int(k) // 12 for k in np.flatnonzero(rd[:, s]))),
                        junk=[str(anc[k]) for k in np.flatnonzero(junk[:, s])][:20]))
    return out

if __name__ == '__main__':
    with concurrent.futures.ProcessPoolExecutor(max_workers=2, mp_context=mp.get_context('fork')) as pool:
        res = [r for rr in pool.map(run, tasks) for r in rr]
    print(json.dumps(dict(sha=h, failures=res), indent=1))
