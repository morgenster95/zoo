# Reel „Hook: Day 1“ (kopie struktury vzorového virálního videa)

Vzor: screen recording `ScreenRecording_11-17-2026 23-21-32_1.mp4` (@kingsfollowgame, „Day 1 of Kingsfollow“, 60 s, 9:16, titulky po 1–3 slovech, hlas + hudba).
Naše verze: `marketing/reels/hook/out.mp4` (≈41 s, 1080×1920, 30 fps), **natočeno v enginu** (web/reel.html), bez webového rozhraní.

## Struktura vzoru → zoo

| Vzor (čas ≈) | Zoo verze (řádek skriptu) |
|---|---|
| 0–8 s: tři vesnice pod sebou (Instagram/TikTok/YouTube po 1 vesničanovi), „WE GAVE TIKTOK ONE…“ | `intro`: úvodní záběr chudé zoo, štítek DAY 1, **počáteční stav 500 mincí / 0 návštěvníků** |
| 8–24 s: HUD (GOLD 500, VILLAGERS 1), „1 FOLLOWER = 1 VILLAGER + 10 GOLD“, příchod vesničana | `visitor`, `coins`: první návštěvník projde bránou, **+10 se vznáší u brány a částka nad pokladnou i HUD roste**, panel „1 FOLLOWER = 1 VISITOR + 10 COINS“ |
| „A PROBLEM / NO WALLS! / SINGLE WALL AND IT'S OVER“ | `poor`, `escape`: červený panel NO FENCE!, zebra uteče po cestě |
| −200 gold, modrý „blueprint“ palisády se po dílech mění v pevnou | `fence`: **−200**, ghost plotu (průhledná tyrkysová) → pevný díl s „pop“ a prachem, zebra se vrací dřív, než se plot uzavře |
| „MOST LIKED COMMENT DECIDES WHAT HAPPENS NEXT“, kamera se oddálí | `vote`: panel + 3 karty (CAFE 300, PLAYGROUND 250, PENGUINS 500), na parcele **po jedné „vyskočí“ budova** (pop, jiskry, prach) |
| „1 SHARE = MERCHANT CARAVAN +20 GOLD“, karavana přijede | `bus`: „1 SHARE = SCHOOL BUS +20 COINS“, žlutý autobus, houkání, +20 |
| „WHAT SHOULD WE CALL OUR VILLAGE?“ + „FOLLOW TO MOVE IN“ | `cta`: „WHAT SHOULD WE CALL OUR ZOO?“ + lišta **FOLLOW TO VISIT** |

Rozdíl: ve vzoru jsou 3 platformy (3 vesnice). Zoo je zatím jen na Instagramu, proto úvod není rozdělený na 3 panely.
Počáteční fond 500 mincí (`START_COINS`) je nové pravidlo hry převzaté ze vzoru (pozor: mění zůstatek, viz `engine/layout.js`).

## Jak to vzniká (vše deterministické, funkce času)

```bash
python3 tools/reel-audio.py voice marketing/reels/hook   # hlas (macOS say) + timeline.json (čas každého slova)
node tools/reel-events.mjs marketing/reels/hook          # události (zvukové efekty, příchody, plot)
python3 tools/reel-audio.py mix marketing/reels/hook     # hlas + hudba + efekty = audio.wav
FFMPEG=/cesta/k/ffmpeg node tools/record-reel.mjs hook    # snímky z Chrome (puppeteer) → out.mp4
node tools/record-reel.mjs hook --still 12.5 --still 20   # jen náhledové snímky do stills/
```
Soubory: `web/src/reel-script.js` (plán, příchody, plot, události), `web/src/reel.js` (vykreslení: HUD, titulky, efekty), `marketing/reels/hook/script.json` (text hlasu).
Hlas je zatím macOS „Samantha“ (zdarma, robotický); pro ostrý reel jej vyměnit za lepší TTS nebo nahrávku, časování se přepočítá samo (`voice`).
