#!/usr/bin/env bash
# Official DQI verifier (102,400 shots) at one or more salts; '' is the default salt.
# usage: QCC_DATA=<competition data> bash dqi/verify.sh dqi.kmb OUTPREFIX '' s1 s2
set -euo pipefail
: "${QCC_DATA:?set QCC_DATA to the competition data folder (holds kickmix/ and verifiers/)}"
c=$(realpath "$1"); out=$(realpath -m "$2"); shift 2
cd "$QCC_DATA/verifiers"
for s in "$@"; do
  f="${out}_salt_${s:-none}.json"
  PYTHONPATH="$QCC_DATA/kickmix:$QCC_DATA/verifiers" python -m dqi.verify_submission_dqi "$c" --max-workers 2 --salt "$s" > "$f"
  python -c "import json,sys; d=json.load(open(sys.argv[1])); print('salt=%r' % sys.argv[2], d['status'], 'value errors', d['value_errors'], 'phase errors', d['phase_errors'], 'T %.1f' % d['toffoli_count'], 'Q', d['num_qubits'], 'R %.5f' % d['repetition_factor'], 'cost %.6e' % d['score'])" "$f" "$s"
done
