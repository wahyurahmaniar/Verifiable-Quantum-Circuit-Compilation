# DQI: 893 to 892 qubits

The idea is explained in the main [README](../README.md#dqi-one-qubit-less-panel-c). This folder holds the build and verification scripts and the evidence for each change. The base is ahoirg's 893-qubit build (hybrid6-guard893: SomeJoint's q18 decoder with yoyobar's one-carry pole history), rebuilt from its pinned source bundle; our files change it at build time.

## Where the qubit comes from

The 893-qubit peak sits only in unextract, at two spots per homogeneous node: the F6 chart flag inside normalize_first_half and the width-adaptive GF(64) inverse. Live there: 840 syndrome qubits, the current pole, the explicit P6 flag, R (24), D (24) and 3 chart flags. Holding P6 as a measured bit instead of a qubit frees one.

## Changes

| # | Change | File |
|---|---|---|
| 1 | P6 is measured (HMR) in the forward pass and recomputed in the reverse of node 7 as zero(N word of group 6), 23 Toffolis; a CZ with the stored bit then repays the measurement. This also handles random group-6 poles (seen once in 102,400 shots: w 30, N = 0, L ≠ 0), which the carry form P7 AND zero(marker) misses. | `hybrid_g892.py`, `patches/g892.json` |
| 2 | 892-qubit guard for the width-adaptive kernels. | `build_dqi_g892.patch` (`--guard 892`) |
| 3 | No pole branch for groups 7 and 8; the carry bank runs over groups 9-16. Poles are structural: P<sub>g</sub> = 1 if and only if the error weight w is odd and w ≤ 2g − 1 (102,400-shot probe), so groups 7 and 8 need w ≤ 15, about 3e-8 per shot. | `patches/g892.json` (frozen_chart, carry start 9) |
| 4 | The zero flags of folds 18-20 in the syndrome synthesis are not computed. They follow F<sub>j</sub> = 1 if and only if w ≤ 32 − j with matching parity (checked for w 10-35), so they are 0 unless w ≤ 14. | `build_dqi_g892.patch` (`--zfset 18,19,20`), `patches/g892.json` |
| 5 | The carry test P(g − 1) = P(g) AND zero(marker) reads 12, 12, 16, 20 and 22 of the 24 marker bits for P9 to P13. A false positive needs w = 2g − 1 and a marker that is zero only in the bits read: at most about 3e-8 per shot. | `patches/g892.json` (`POLE_BITS`) |

What was tried and dropped: recomputing P(g − 1) as zero(N word) without the AND fails at every even w ≤ 2g − 1 (N = L = 0 there but D ≠ 0, no pole); 256 of 256 shots failed at w = 16.

## Results (official verifier)

| Build | Salt | Value errors | Phase errors | Mean T | Q | R | Cost |
|---|---|---:|---:|---:|---:|---:|---:|
| 893 (public) | s1 | 0 | 0 | 407,444.1 | 893 | 1.19126 | 3.87059e11 |
| 893 (public) | s2 | 0 | 0 | 407,443.9 | 893 | 1.19126 | 3.87059e11 |
| 893 (public) | s3 | 0 | 1 | 407,444.1 | 893 | 1.19673 | 3.88837e11 |
| 892 (ours) | '' | 0 | 0 | 407,005.2 | 892 | 1.19126 | 3.85777e11 |
| 892 (ours) | s1 | 0 | 0 | 407,004.8 | 892 | 1.19126 | 3.85777e11 |
| 892 (ours) | s2 | 0 | 0 | 407,004.9 | 892 | 1.19126 | 3.85777e11 |

Static Toffolis 482,802 to 482,341. On Kaggle's own draw the 892 file had 2 failing shots (score 23.93) and the 893 file none (23.97677).

## Files

- `build.sh`: checks the inputs' SHA-256, patches ahoirg's `build_dqi.py`, builds, checks the output SHA-256 (`c453c7ac...`).
- `verify.sh`: official verifier at one or more salts.
- `build_dqi_g892.patch`: our options for ahoirg's build script (guard, edit file, zero-flag hook).
- `patches/g892.json`: text edits applied to the bundle's files before the build.
- `hybrid_g892.py`: the replacement `external_node_chain` (must stay byte-identical for the output hash).
- `tools/`: failure census of two circuits on the same shots, fixed-weight stress runs, per-shot diagnosis of the official batches.
