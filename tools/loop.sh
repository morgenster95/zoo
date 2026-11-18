#!/usr/bin/env bash
# Smyčka zoo (spouští .github/workflows/zoo-loop.yml), převzatá z fronty: každých 5 min komentáře a followeři z IG → stav hry,
# odpovědi novým návštěvníkům, commit stavu. Nezávisí na plánovači GitHubu (ten spouští cron nespolehlivě).
#
# Odolnost: každé kolo začíná z čistého origin/main, chyba v kole smyčku neukončí, kolize při pushi = kolo se zopakuje,
# opakované potíže = GitHub issue (přijde e-mail). Web zatím nenasazuje (čeká na Cloudflare, viz deploy.yml).
set -u

MINUTES=${LOOP_MINUTES:-330}
END=$(( $(date +%s) + MINUTES * 60 ))
FAILS=0

alert() { # štítek, nadpis, text
  [ -n "$(gh issue list --label "$1" --state open --json number -q '.[0].number' 2>/dev/null)" ] && return
  gh label create "$1" --color B60205 2>/dev/null || true
  printf '%s\n\nIssue se zavře samo, až to zase půjde.\n' "$3" | gh issue create --title "$2" --label "$1" --body-file - || true
}
resolve() { # štítek, komentář
  for n in $(gh issue list --label "$1" --state open --json number -q '.[].number' 2>/dev/null); do gh issue close "$n" -c "$2" || true; done
}

# jedno kolo; 0 = hotovo, 1 = chyba, 2 = kolize při pushi (zopakovat hned)
round() {
  git fetch -q origin main && git reset -q --hard origin/main || { echo "sync repa selhal"; return 1; }
  node ingest/sync.mjs || { echo "sync IG selhal"; return 1; }
  git add data/state.json
  if ! git diff --cached --quiet; then
    git commit -qm "loop: $(date -u +%FT%TZ)" || return 1
    git push -q origin HEAD:main || { echo "push kolize, kolo se zopakuje"; return 2; }
  fi
  return 0
}

while [ "$(date +%s)" -lt "$END" ]; do
  for attempt in 1 2 3; do
    round
    rc=$?
    [ $rc -ne 2 ] && break
    sleep $(( attempt * 5 ))
  done
  if [ $rc -eq 0 ]; then
    FAILS=0
    resolve loop-trouble "Smyčka zase běží bez chyb."
  else
    FAILS=$((FAILS + 1))
    echo "kolo selhalo ($FAILS× po sobě)"
    [ $FAILS -ge 3 ] && alert loop-trouble "Smyčka má potíže" "Poslední $FAILS kola smyčky selhala (komentáře, commit nebo push). Podrobnosti v logu běhu zoo-loop."
  fi
  sleep "${LOOP_SLEEP:-300}"
done
