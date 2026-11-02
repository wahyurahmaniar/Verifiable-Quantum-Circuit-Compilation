# Credits

This repository adds two things: the chemistry ANGLE loaders and the 892-qubit DQI patch set. Everything else it builds on is public work by others, listed per component. Links point to the Kaggle pages the inputs come from.

## Competition

- Google Quantum AI and the competition authors: tasks, reference circuits, official verifiers and kickmix (Apache-2.0). [Competition](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation), [Qualtran](https://github.com/quantumlib/Qualtran).

## Chemistry (dfthcsos)

- **marculera (Lera)**: the (R, B, C) = (9, 143, 40) table (factorization, angle words, weights) and the public tensorqrom loaders we compare against; compact-group seed, row dealing and augmented-Lagrangian refit. [DF-THC 10x: compact groups from the Hamiltonian](https://www.kaggle.com/code/marculera/df-thc-10x-compact-groups-from-the-hamiltonian), [DFTHC Compact Pipeline](https://www.kaggle.com/datasets/marculera/dfthc-compact-pipeline).
- The lineage that work credits: **Ahmed Berat Ozer** (D(w) penalty, progressive rounding, refits; [DF-THC Group Compression Factorization](https://www.kaggle.com/datasets/ahmedberatozer/df-thc-group-compression-factorization)); **SomeJoint / Agniv Banerjee** (coded low bits and their loader structure; [QCC Our Chemistry B143 C60 XOR2](https://www.kaggle.com/datasets/somejoint/qcc-our-chemistry-b143-c60-xor2)); **mrmeows** (lookup emitter design, one-body word polish); **heliosli** and **Vladislav Lavrentev / lightningv08** (five-word ANGLE batching; [QCC Circuits Live](https://www.kaggle.com/datasets/heliosli/qcc-circuits-live), [Bezout Schur 5-Word QROM](https://www.kaggle.com/code/lightningv08/bezout-schur-5-word-qrom)); **kozykappa / Kozykorpesh** and **Sumit Chongder** (banked QROM, signed Givens gauge), **kozykappa** and **Artem1410 / anazemcev** (copy-column gauge, effective-normalization refinement; [Complete-Domain Affine Compilation](https://www.kaggle.com/code/kozykappa/quantum-ai-complete-domain-affine-compilation)); **haideptry** through **Phuc Thai / phucthaiv02 (DePie)** (per-group orthogonal gauge, refit after rounding; [DF-THC Retraining Study](https://www.kaggle.com/code/phucthaiv02/qcc-verified-portfolio-df-thc-retraining-study)); **Michael Rustad** (eight-bit B >= 129 regime, L-BFGS refits; [VQCC R10 Merged-Group Chemistry](https://www.kaggle.com/code/michaelrustad/vqcc-r10-merged-group-chemistry-12-87-lb)); **k256net** and **Dmitrii Gluzdov** (earlier factorization lineage).
- **mrmeows / team selenium**: the kernel planners in `third_party/mrmeows_planners`, from [QCC open circuits and sources](https://www.kaggle.com/datasets/mrmeows/qcc-1375-open-circuits) (Apache-2.0). Our `plan.py` calls them unchanged.

## DQI

- **Agniv Banerjee / SomeJoint** and the team credited in their source: the q18 decoder, arithmetic and converter source (Apache-2.0). [Quantum Circuits 23.46 Local GM: 900-Qubit DQI, version 23](https://www.kaggle.com/code/somejoint/quantum-circuits-23-46-local-gm-900-qubit-dqi?scriptVersionId=364288111), [QCC DQI 900 Undo, version 1](https://www.kaggle.com/datasets/somejoint/qcc-dqi-900-undo/versions/1). Their source credits Ahmed Berat Ozer (narrowing), Alex Chilton (Schur-decoder implementation), jday96314 (QuantumAI design and classical models; that repository states no license), mrmeows, Ozer and manwithacat (mask projection), and Dmitrii Gluzdov, ViberTeam and Phuc Thai / DePie (earlier decoder and phase-solve work). It also states that GPT-6 Astra Pro, Claude and AI-agent teams directed by Agniv Banerjee built and checked the q18 arithmetic and decoder.
- **yoyobar**: the one-carry pole history and conjunction ladder. [QCC Local SOTA 20261031, version 1](https://www.kaggle.com/datasets/yoyobar/qcc-local-sota-20261031/versions/1).
- **ahoirg**: the hybrid6-guard893 wrapper (explicit P6, carried groups 7-16, 893-qubit guard), the hash-pinned portable build and the dataset our build starts from. [QCC Reproducible Circuit Assets](https://www.kaggle.com/datasets/ahoirg/qcc-reproducible-circuit-assets).

## invsqrt (used unchanged)

- **Ehan Mallick**: the two 3-to-2 AND merges in the 62-qubit circuit. [Invsqrt 20.65](https://www.kaggle.com/code/ehanmallick/invsqrt-20-65-two-3-to-2-and-merges-on-y6225).
- **yoyobar** (62-qubit rework, made with GPT-6 Astra per its author; [notebook](https://www.kaggle.com/code/yoyobar/lb-22-99-invsqrt-101-62-qubits)), **Akmal Xodarev / busyaprime** ([notebook](https://www.kaggle.com/code/busyaprime/lb-22-72431-22x-cheaper-than-google-s-circuits)) and **mrmeows / team selenium** (architecture and arithmetic), **Ahmed Berat Ozer** (patch and distribution; [VQCC v18 Portfolio](https://www.kaggle.com/datasets/ahmedberatozer/vqcc-v18-portfolio/versions/1)), and the lineage they credit: heliosli, Phuc Thai / DePie, Dmitrii Gluzdov, marsyas.

## This repository

Our code was written with Claude (Anthropic) as a coding assistant.
