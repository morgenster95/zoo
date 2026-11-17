# Grafika: světlé, hravé zoo

Reference: `art/reference/` (@kingsfollowgame: izometrický pixel art, hustě zalidněná mapa, tmavé hnědé panely s krémovým nápisem).
My držíme **pohled a hustotu**, měníme **náladu**: světlé, sytě zelené, pastelové, žádná špína.

## Pevná pravidla

1. **Izometrie 2:1**, dlaždice 32×16 px (jako reference). Řazení podle hloubky `i + j`.
2. **Světlá paleta**, měkký obrys místo černého (`#5b3f4a`, švestková). Stín jen jemný, spodní třetina tvaru tmavší.
3. **Měřítko:** návštěvník 8–9 px (dítě 7), slon ~34×28, žirafa ~26×42, strom ~26×34. Postavy mají být čitelné i v davu: barva trička je hlavní rozlišení.
4. **Paleta** (viz `art/proto/make_proto.py`, slovník `C`): tráva `#8fd96b #80cf5f #a3e47e`, cesta `#f5e2ae #ecd395`, voda `#6fc9f2 #9ee0fb`, led `#d6f3ff`,
   dřevo `#d99a5b #f0b977`, červená `#ef5b5b`, modrá `#4aa8dc`, žlutá `#ffc93c`, krém `#fff3d6`, hnědá `#6b4535`.
5. **HUD panel:** krémový s tmavým obrysem a žlutým proužkem (světlá obdoba panelů z reference), pixelový font.
6. Návštěvníci se liší barvou trička/kalhot/pleti/vlasů + doplňky (balónek, čepice, kočárek, dítě).

## Jak kreslíme

**Zkouška 17. 11. 2026:** celá scéna v [`art/proto/zoo_proto.png`](../art/proto/zoo_proto.png) je nakreslená procedurálně v Pythonu (Pillow):
tvary v nativním rozlišení, automatický obrys, stínování, pak zvětšení 3× bez vyhlazení. Styl sedí na veselou zoo, zvládám ho konzistentně.
Slabší místa: detailní zvířata (slon, žirafa jsou čitelní, ale jednoduší než ruční pixel art), animace chůze.

Plán:
- **Kulisy, zvířata, budovy, terén:** vlastní generace (kód) nebo PixelLab (`create_object_pro_flash`, izometrie) – podle toho, co vypadá lépe; vždy s paletou výše.
- **Návštěvníci (stovky variant, chůze 4–8 směrů):** PixelLab `create_character` + animace (postup z fronty: `tools/pixellab.py`, ledger proti duplikátům, `sprite_qa.py`). Generace jsou omezené, proto jednou správně.
- **Z fronty vzít:** `tools/pixellab.py`, `tools/sprite_qa.py`, `tools/sprite_fix.py`, `tools/palette_lock.py`, `tools/import-anim.py`, pravidla z `docs/PIXELLAB_BRIEF.md` (jeden směr na volání, ledger, kontrola plovoucích pixelů).
- PixelLab klíč v tomto repu zatím není; do prostředí ho dodáme stejně jako ve frontě (síťová proxy / tajemství).

## Seznam assetů fáze 1

Terén: tráva (3 varianty), cesta, voda, led, písek (savana), džungle. Plot, brána s nápisem, kasa, stánek s cukrovou vatou, lavička, strom ×3, keř, květiny.
Zvířata: slon, žirafa, zebra, flamingo, tučňák, lev, panda, opice, želva. Návštěvníci: viz výše.
