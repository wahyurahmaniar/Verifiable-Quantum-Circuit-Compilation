#!/usr/bin/env bash
# Assemble a Kaggle submission zip: dfthcsos/ (15 ANGLE circuits + submission.npz), dqi.kmb, invsqrt.kmb.
# usage: bash scripts/package.sh DFTHCSOS_DIR DQI.kmb INVSQRT.kmb OUT.zip
set -euo pipefail
D=$(realpath "$1"); Q=$(realpath "$2"); I=$(realpath "$3"); OUT=$(realpath -m "$4")
STAGE=$(mktemp -d); mkdir "$STAGE/dfthcsos"
cp "$D"/angle_k_{0..14}.kmb "$D/submission.npz" "$STAGE/dfthcsos/"
ln -s "$Q" "$STAGE/dqi.kmb"; ln -s "$I" "$STAGE/invsqrt.kmb"
(cd "$STAGE" && zip -q -r -D "$OUT" dfthcsos dqi.kmb invsqrt.kmb)
rm -f "$STAGE"/dfthcsos/* "$STAGE/dqi.kmb" "$STAGE/invsqrt.kmb"; rmdir "$STAGE/dfthcsos" "$STAGE"
unzip -l "$OUT" | tail -1
sha256sum "$OUT"
