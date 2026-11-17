# ZOO (pracovní název)

Instagramová hra: každý follower je **návštěvník zoo**. Zoo se staví komunitně: počet návštěvníků otevírá mapu, každý návštěvník přináší 10 mincí,
hlasováním se rozhoduje, co se postaví na volných parcelách. Světlý hravý izometrický pixel art, anglicky pro celý svět.

Mechanicky je to kopie hry **Mud & Iron** (repo `morgenster95/fronta`) bez bojů a smrti.

- Návrh mechanik a ekonomika: [`docs/DESIGN.md`](docs/DESIGN.md) · hosting a data bez Firebase: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) · grafika: [`docs/ART.md`](docs/ART.md) · pokyny pro Claude: [`CLAUDE.md`](CLAUDE.md)

## Co už funguje (fáze 1: web a data)

- **Web** (`web/`, Vite + PixiJS): izometrická mapa, chodící návštěvníci (4 směry, chůze), kasa s tabulí mincí, hledání @handle, karta návštěvníka, zoom a posun.
- **Engine** (`engine/`, čisté JS, testy `npm test`): mapa (silnice po 6 dlaždicích, parcely 5×5), pevná místa pro návštěvníky (nikdo se nepřesouvá), otevírání oblasti podle počtu, ekonomika.
- **Data** (`tools/`): stav v `data/state.json`, výstup po malých dávkách (`zoo.json`, `looks/*.bin`, `h/*.json`, `v/*.json`), falešná soupiska `npm run data:fake`.
- **Grafika** (`art/proto/`): generátory spritů v Pythonu (Pillow), export do jednoho atlasu `npm run assets`.
- Měřeno: 4 000 návštěvníků = ~2–3 ms CPU na snímek, celý web 1,9 MB (z toho atlas 247 kB), data 4 000 návštěvníků ~1 MB v dávkách.

## Vývoj

```bash
npm install
npm run data:build     # data z data/state.json (12 ukázkových návštěvníků)
npm run data:fake      # nebo 4 000 falešných (web/public/data, není v gitu)
npm run dev            # http://localhost:5173
npm test               # testy enginu
npm run assets         # přegeneruje sprity (python3 + Pillow)
```

Zatím **není** napojený Instagram ani přihlášení; nasazení na Cloudflare Pages je připravené (`.github/workflows/deploy.yml`), čeká na účet a tajemství.
