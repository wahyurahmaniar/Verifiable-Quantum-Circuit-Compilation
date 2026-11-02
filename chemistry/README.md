# Chemistry ANGLE loaders

The idea is explained in the main [README](../README.md#chemistry-paired-product-angle-loaders-panel-b). This folder holds the code and the plans for the C40 table.

## Files

- `loader.py`: the emitter (128 qubits: 11 selection, 40 word, 77 workspace, with the five bit-7 qubits borrowed until the end) and its exactness checks over all 1,363 addresses.
- `build.py`: one circuit `angle_k_K.kmb` from a word table and its three stage plans.
- `build_all.sh`: all 15 circuits, copies the table next to them, runs the official verifier.
- `plan.py`: the plan search (group-3 relations; plane modes all, triples and pairs); on the C40 table it reproduces `plans/c40` file for file in about 90 s.
- `plans/c40/`: the 45 plans `kK_MODE_sS.json`. MODE `all` plans all 35 output bits; MODE `nolsb` plans bits 1-6, and `build.py` adds the two LSB products per word.

## C40 counts

| Circuits | Plan mode | Products per stage | Products | Toffolis per circuit |
|---|---|---|---:|---:|
| k 0-2 | all | 106, 61, 61 | 228 | 317 |
| k 3 | all | 107, 61, 61 | 229 | 318 |
| k 4-14 | nolsb | 91, 52, 52 (+ 10 LSB) | 205 | 294 |

Toffolis per circuit = 78 (high cache) + 11 (low slots) + products. Per pass 4,503; with the fixed preparation and rotation costs (6,741), chemistry T = 2 x 4,503 + 6,741 = 15,747.

## Commands

```bash
python chemistry/plan.py --words TABLE.npz --plans build/plans                 # plans for a new table
python chemistry/build.py --words TABLE.npz --plans build/plans --k 0 --out angle_k_0.kmb
bash chemistry/build_all.sh TABLE.npz build/plans build/dfthcsos                # all 15 + official verifier
```
