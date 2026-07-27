#!/usr/bin/env bash
# Run the docs sample sweep: every code sample on the site is executed
# against the installed `kaappi` binary (see _common.py for the knobs).
#
#   scripts/sweep/run.sh              # everything
#   scripts/sweep/run.sh guide procs  # selected sections
set -u
cd "$(dirname "$0")/../.."

sections=("$@")
[ ${#sections[@]} -eq 0 ] && sections=(migrating cookbook guide procs eco playground)

fail=0
for s in "${sections[@]}"; do
  echo "===================== sweep: $s ====================="
  case "$s" in
    migrating)  python3 scripts/sweep/sweep_migrating.py docs/guide/migrating.md ;;
    cookbook)   python3 scripts/sweep/sweep_cookbook.py docs/cookbook \
                  && python3 scripts/sweep/sweep_cookbook2.py docs/cookbook ;;
    guide)      python3 scripts/sweep/sweep_guide.py docs/guide ;;
    procs)      python3 scripts/sweep/sweep_procs.py docs/procedures ;;
    eco)        python3 scripts/sweep/sweep_eco.py docs/ecosystem ;;
    playground) python3 scripts/sweep/sweep_playground.py ;;
    *)          echo "unknown section: $s"; exit 2 ;;
  esac || fail=1
done

if [ "$fail" -ne 0 ]; then
  echo "SWEEP: failures above"
  exit 1
fi
echo "SWEEP: all sections green"
