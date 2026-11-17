# ZOO (pracovní název)

Instagramová hra: každý nový follower se stane **návštěvníkem zoo**. Kdo pod náš Reel napíše klíčové slovo, jeho človíček
se objeví na obří izometrické mapě zoo ve veselém světlém pixel artu. Zoo roste s počtem návštěvníků: nové výběhy, zvířata,
stánky. Každý den nový zápis v „deníku návštěvníka“, hlasuje se v komentářích, co se postaví dál.

Mechanicky je to kopie hry **Mud & Iron** (repo `morgenster95/fronta`), jen místo války stavíme zoo. Bez bojů, bez smrti, hravě.

- Co přebíráme a jak se to mapuje: [`docs/DESIGN.md`](docs/DESIGN.md)
- Web a hosting bez limitů Firebase: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Styl grafiky a postup (PixelLab / vlastní generace): [`docs/ART.md`](docs/ART.md)
- Pokyny pro Claude: [`CLAUDE.md`](CLAUDE.md)

## Stav

Fáze 0: průzkum, návrh a zkouška stylu. Zatím žádný kód hry.
Zkouška stylu: [`art/proto/zoo_proto.png`](art/proto/zoo_proto.png) (generuje `art/proto/make_proto.py`, Python + Pillow).
Reference: `art/reference/` (screenshoty z @kingsfollowgame, jen jako vodítko k pohledu a hustotě mapy).
