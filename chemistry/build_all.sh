#!/usr/bin/env bash
# Build the 15 ANGLE circuits of a word table from its plans, then run the official dfthcsos verifier.
# usage: QCC_DATA=<competition data> bash chemistry/build_all.sh WORDS.npz PLANDIR OUTDIR
# For the C40 table: bash chemistry/build_all.sh c40/submission.npz chemistry/plans/c40 build/dfthcsos  (about 2 min)
set -euo pipefail
: "${QCC_DATA:?set QCC_DATA to the competition data folder (holds kickmix/ and verifiers/)}"
HERE=$(cd "$(dirname "$0")" && pwd)
WORDS=$(realpath "$1"); PLANS=$(realpath "$2"); OUT=$(realpath -m "$3")
mkdir -p "$OUT"
export PYTHONPATH="$QCC_DATA/kickmix:$QCC_DATA/verifiers${PYTHONPATH:+:$PYTHONPATH}"
for k in $(seq 0 14); do
  python "$HERE/build.py" --words "$WORDS" --plans "$PLANS" --k "$k" --out "$OUT/angle_k_$k.kmb"
done
cp "$WORDS" "$OUT/submission.npz"
cd "$QCC_DATA/verifiers"
python -m dfthcsos.verify "$OUT" > "$OUT.verify.json"
python -c "import json,sys; d=json.load(open(sys.argv[1])); r=d['resources']; print(d['status'], 'lambda_eff %.4f' % d['lambda_eff'], 'T', d['toffoli_count'], 'Q', d['num_qubits'], 'ANGLE Toffolis per pass', r['angles_toffoli_per_pass'], 'cost %.6e' % d['score'])" "$OUT.verify.json"
