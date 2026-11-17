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

**Zkouška v2 (17. 11. 2026, `art/proto/zoo_art.py`, výstupy `art/proto/styles/`):** tři styly na stejné scéně (budovy z izometrických boxů se sedlovou střechou a šindelem,
věž, kupole, kolotoč, iglú, texturovaná tráva/cesta/dlažba, hustá zeleň, stovky návštěvníků). `A_reference` = nejvěrnější referenci (tmavší, sytá, silný obrys),
`B_playful` = světlý cukrový, `C_hybrid` = struktura reference + světlejší barvy. Styl se přepíná slovníkem `STYLES`.
Slabiny: zvířata jsou jednodušší než budovy, žádné animace, budovy mají jen jednu orientaci a málo detailů (okna, dveře, truhlíky).

## Zvířata: styl (v2, `art/proto/animals.py`)

Pravidla, která drží všech 13 zvířat (slon, žirafa, zebra, lev, tygr, panda, hroch, plameňák, tučňák, opice, nosorožec, medvěd, želva):
1. **Pohled z boku doprava**, doleva je zrcadlo. Světlo vlevo nahoře.
2. **Čtyřtónová rampa** na zvíře (světlo, základ, stín, hluboký stín), tělo = „koule“ s ditherem na přechodech, tenké části (krk, chobot, nohy) stínované podle okraje.
3. **Selektivní obrys:** tmavší odstín sousední barvy, ne jedna barva pro všechno (zvířata jsou měkčí než budovy).
4. **Oko 2×2 + odlesk, růžový ruměnec**, tmavá kopyta, vzory (skvrny, pruhy) jen uvnitř siluety.
5. **Velikost na mapě** (`K = 0.9`, žirafa 0.76 přes `ANIMAL_K`): slon ~45×38, žirafa ~34×56, tučňák ~12×16. `K = 1.0` je „hero“ velikost pro kartu a close-up.
6. Nové zvíře = nová rampa v `R`, funkce složená z částí (`blob`, `limb`, `line`, `poly`, `overlay`).

Zkouška: `art/proto/styles/C_animals_sheet.png` (arch obou směrů) a `C_hybrid_scene_new_animals.png` (ve scéně).
Známé slabiny: chybí chůze a jiné směry než bok (zepředu/zezadu), lev a hroch mají jednoduchou hlavu, žirafy na mapě jsou větší než budovy (zmenšit nebo zvětšit budovy).

Plán:
- **Kulisy, zvířata, budovy, terén:** vlastní generace (kód) nebo PixelLab (`create_object_pro_flash`, izometrie) – podle toho, co vypadá lépe; vždy s paletou výše.
- **Návštěvníci (stovky variant, chůze 4–8 směrů):** PixelLab `create_character` + animace (postup z fronty: `tools/pixellab.py`, ledger proti duplikátům, `sprite_qa.py`). Generace jsou omezené, proto jednou správně.
- **Z fronty vzít:** `tools/pixellab.py`, `tools/sprite_qa.py`, `tools/sprite_fix.py`, `tools/palette_lock.py`, `tools/import-anim.py`, pravidla z `docs/PIXELLAB_BRIEF.md` (jeden směr na volání, ledger, kontrola plovoucích pixelů).
- PixelLab klíč v tomto repu zatím není; do prostředí ho dodáme stejně jako ve frontě (síťová proxy / tajemství).

## Seznam assetů fáze 1

Terén: tráva (3 varianty), cesta, voda, led, písek (savana), džungle. Plot, brána s nápisem, kasa, stánek s cukrovou vatou, lavička, strom ×3, keř, květiny.
Zvířata: slon, žirafa, zebra, flamingo, tučňák, lev, panda, opice, želva. Návštěvníci: viz výše.
