# ZOO: pokyny pro Claude

Hra „každý follower = návštěvník zoo“, kopie mechaniky repa `morgenster95/fronta` (Mud & Iron). Čti `docs/DESIGN.md`, `docs/ARCHITECTURE.md`, `docs/ART.md`.

- Uživatel píše česky; hra a web jsou zatím otevřená otázka (viz DESIGN, otevřené otázky).
- Zdrojové repo fronty: `gh repo clone morgenster95/fronta`. Při přebírání kódu vždy odstranit boj/smrt, nic válečného.
- Grafika: světlá, hravá, izometrická 2:1, viz `docs/ART.md`. Generace v PixelLabu jsou omezené, před generováním vždy ledger (vzor ve frontě).
- Hosting: ne Firebase. Cloudflare Pages + R2 + Worker/D1 (viz ARCHITECTURE). Data nikdy neposílat jako jeden velký soubor, jen dávky.
- Tokeny a klíče jen v GitHub Secrets, nikdy do repa.
- Stav a rozhodnutí průběžně psát sem a do `docs/`.
