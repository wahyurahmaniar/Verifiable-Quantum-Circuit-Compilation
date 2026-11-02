#!/usr/bin/env bash
# Rebuild our 892-qubit DQI circuit from ahoirg's pinned source bundle (about 4 min, 2.5 GB RAM, 576 MB output).
# usage: QCC_DATA=<competition data> QCC_ASSETS=<ahoirg's qcc-reproducible-circuit-assets> bash dqi/build.sh WORKDIR
# WORKDIR must not exist yet. The result is WORKDIR/dqi.kmb (SHA-256 c453c7ac...).
set -euo pipefail
: "${QCC_DATA:?set QCC_DATA to the competition data folder (holds kickmix/ and verifiers/)}"
: "${QCC_ASSETS:?set QCC_ASSETS to the qcc-reproducible-circuit-assets folder (holds build_dqi.py, dqi-source-bundle.json)}"
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=$(realpath -m "${1:?usage: bash dqi/build.sh WORKDIR}")
BUNDLE_SHA=a7f22360aa7d1f5137b8cd2c6525e7eb05f826a031fcd751ce56f388aee5fafe
SCRIPT_SHA=80c39449bff91743b43d63e46e39a6e39ca40b46e252b9fff2f52acc56cacd8a
OUT_SHA=c453c7ac1bcce98ccf4d61c2881ccd23ac7db0e47fb31813a2e9fcdcd2390765
check() { echo "$2  $1" | sha256sum -c --quiet - || { echo "SHA-256 mismatch: $1" >&2; exit 1; }; }
check "$QCC_ASSETS/dqi-source-bundle.json" $BUNDLE_SHA
check "$QCC_ASSETS/build_dqi.py" $SCRIPT_SHA
RUN=$(mktemp -d)
trap 'rm -f "$RUN/build_dqi_g892.py" "$RUN/build_dqi_g892.py.orig"; rmdir "$RUN" 2>/dev/null || true' EXIT
# ahoirg's script has CRLF line ends; the patch is against the LF form
sed 's/\r$//' "$QCC_ASSETS/build_dqi.py" > "$RUN/build_dqi_g892.py"
patch -s "$RUN/build_dqi_g892.py" < "$HERE/build_dqi_g892.patch"
cd "$RUN"
HYBRID_SRC="$HERE/hybrid_g892.py" PYTHONPATH="$QCC_DATA/kickmix${PYTHONPATH:+:$PYTHONPATH}" \
  python -B build_dqi_g892.py --guard 892 --zfset 18,19,20 --patches "$HERE/patches/g892.json" \
  --bundle "$QCC_ASSETS/dqi-source-bundle.json" --bundle-sha256 $BUNDLE_SHA --work "$WORK"
check "$WORK/dqi.kmb" $OUT_SHA && echo "OK: $WORK/dqi.kmb is our 892-qubit build"
