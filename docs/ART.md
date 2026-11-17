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

## Návštěvníci (v2, `art/proto/visitors.py`)

- **Chibi proporce:** dospělý 7×10 px (hlava 4 řádky), dítě 5×8, selektivní obrys. Vzhled = pleť (6) × účes (7) × barva vlasů (8) × oblečení (triko/šaty/kalhoty) × doplněk.
- **4 izometrické směry** (SE, SW k nám, NE, NW zády; levý/pravý je zrcadlo) a **chůze o 4 snímcích** (stoj, levá noha, stoj, pravá noha, houpání rukou).
- **Typy** (odpovídají „typům návštěvníků“ z přání v komentáři): `plain`, `family` (rodič s kočárkem), `schoolkid` (batoh), `photographer` (foťák, vesta, čepice), `balloon` (1–3 balónky), `tourist` (klobouk, mapa), `grandpa` (hůl, šedé vlasy), `icecream` (dítě se zmrzlinou), `supporter` (zlatá hvězdička nad hlavou = Přítel zoo).
- **Vzhled z handle:** `new_spec(seed)`, seed = hash @handle, takže každý návštěvník vypadá pokaždé stejně a je poznat. Kombinací je desítky tisíc.
- Výstupy: `styles/visitors_types.png`, `visitors_crowd.png`, `visitors_walk.gif`, `C_hybrid_scene_visitors.png`.
- Slabiny: bez bočního pohledu, jen zepředu/zezadu; chůze je jednoduchá; žádné sezení na lavičce, krmení zvířat ani focení (další animace).

## Test: replikace cizího stylu zvířat (`art/proto/painted.py`, 17. 11. 2026)

Vzor: `art/reference/animal_style_sample.png` (malovaný pixel art, přirozené proporce, hodně tónů, obrys v odstínu zvířete, stín na zemi).
Postavil jsem nový renderer: siluety z polygonů, objem z mapy výšky (vzdálenost od okraje) + osvětlení, 6tónová rampa s posunem odstínu, textura srsti, stín na zemi, vzory (skvrny, pruhy) přes tělo.
**Výsledek:** materiál, barevnost, stíny a „malovaný“ dojem se přiblížily vzoru (srovnání `styles/painted_vs_reference.png`).
**Slabé místo:** anatomie a siluety. Vzor má ručně vymodelované tvary (ohnuté nohy, výrazné hlavy), moje polygony jsou tužší, hlavy jednodušší, lev má oddělený ocas.
**Závěr:** pro finální zvířata v tomhle stylu je lepší PixelLab se stylovým obrázkem (nebo ruční dokreslení), můj renderer se hodí na rychlé návrhy, stíny a sjednocení barev.

## Měřítko (oprava 17. 11. 2026)

První verze měla zvířata obří vůči návštěvníkům. Pravidlo teď: **dospělý návštěvník = 10 px výšky** (14 s obrysem a stínem).
Zvíře v kohoutku je výškou po hřbet zhruba jako dospělý, slon ~2×, žirafa ~2,5×, tučňák a želva menší. Měřítko je v `animals.py` (`ANIMAL_K`: slon 0.56, žirafa 0.46, zebra/lev/panda/hroch 0.5 …).
Kontrola: `styles/scale_check_visitors_vs_animals.png` (dva návštěvníci a všech 13 zvířat vedle sebe). Při přidání nového zvířete ho vždy porovnat s tímhle obrázkem.
Parcely k zastavění jsou ploché (vyšlapaná zem, čárkovaný obrys, pásky v rozích) a cedule „?“ je před nimi, bez kůlů.

## Vegetace (v2, `art/proto/vegetation.py`)

Staré stromy (kulička a smrček) nahrazeny malovanými: kupy listí se stínováním a vnitřním obrysem, kůra, stín na zemi (renderer z `painted.py`).
Druhy: 3 duby, smrk, bříza, palma, akácie, baobab, bambus, třešeň, 2 keře, květiny, rákosí, trs trávy. Palma, akácie, baobab (savana), bambus a třešeň (Asie) jsou připravené pro rodiny výběhů.
V mapě: louky mají mix (30 % stromy, jinak keře/květiny/tráva), okraj je řídký les, před bránou volno, rybníček má rákosí. Arch: `styles/vegetation_sheet.png`.

## PixelLab (povoleno uživatelem 17. 11. 2026: dekorace, lavičky, základní sada zvířat, bez animací)

Nástroj: `tools/pixellab.py` (klíč jen v prostředí `PIXELLAB_API_KEY`, nikdy v repu). Pojistky: **ledger** `art/pixellab/ledger.jsonl` (stejný název = nic se neodešle), fronta max 6 úloh, jedno odeslání bez automatických opakování, zůstatek `balance`.
Úspornost: **jeden obrázek = celý sheet** (jedna úloha za 5–9 generací, ceník podle delší strany: ≤96 px 5, ≤128 px 6, ≤256 px 9), pak řez na sprity (`art/proto/slice_pixellab.py`).
Použito: `animals_sheet_1` (256², 9 gen, 12 zvířat ve velkém rozlišení pro karty a close-upy), `animals_sheet_small_1` (128², 6 gen, 12 zvířat v měřítku mapy), `decor_sheet_small_1` (128², 6 gen, 16 dekorací). `buildings_sheet_1` (256², 9 gen: chýše, stáj, pagoda, tučňáčí dům, domek na stromě, akvárium, kavárna, obchod, voliéra) a `buildings_sheet_2` (256², 9 gen: kolotoč, kolo, nádraží, hřiště, toalety, nemocnice, pokladna, kamenná brána, popcorn). **Celkem 39 generací.**
Stylové kotvy (nahrávají se jako `style_image`, v nativním rozlišení): `art/pixellab/anchor_wildlife.png` (vzor od uživatele) a `anchor_decor_small.png` (naše rekvizity).
Sprity v mapě: `a_<zvíře>` (PixelLab, stín přebarven na poloprůhledný), `d_<dekorace>`; moje původní zvířata zůstávají jako `old_a_*`.
Další sheety dělat stejně (jeden sheet, kotva stylu, před odesláním zkontrolovat ledger).

## Hustota pixelů (oprava 17. 11. 2026): „chunky“ budovy

První sheety staveb z PixelLabu (`buildings_sheet_1/2`, 256²) měly zhruba **2× jemnější pixelovou hustotu** než moje sprity a návštěvníci (okna 1–2 px, textury střech, drobné detaily), takže na mapě nesedělo měřítko.
Zmenšení na půlku nepomohlo (rozmazané). Správný postup: **generovat v menším plátně a s kotvou z našich chunky spritů**:
`buildings_sheet_3_chunky` (192², 6 gen), `buildings_sheet_4_chunky` (192², 6 gen) a samostatné ruské kolo `ferris_chunky` (64×80, 5 gen, kolo ze sheetu bylo rozpadlé).
Prompt: „chunky low-detail, early 1990s city builder, thick outline, windows 3–4 px, no tiny textures“ + kotva `anchor_buildings_chunky.png`; kotva MUSÍ být menší než plátno (jinak ji PixelLab odmítne bez účtování).
Původní detailní sprity zůstaly v `art/pixellab/sprites_detailed/` (vhodné pro karty a close-upy). Srovnání: `styles/density_mine_vs_pixellab.png` (nahoře moje, uprostřed detailní, dole chunky).
**Celkem 56 generací** (zůstatek viz `tools/pixellab.py balance`). Pravidlo pro další generování: nejdřív ověřit, kolik pixelů má okno a dveře vs. návštěvník (10 px), a velikost plátna volit podle toho.

### Hustota zvířat a dekorací (kontrola 17. 11. 2026)

První PixelLab sheety zvířat a dekorací (128²) byly také příliš jemné a velké: koš byl vysoký jako návštěvník, lavička 2× větší než moje, zvířata ~1,3× větší s jemnými texturami (zebra jako šachovnice).
Opraveno stejným postupem jako u budov, ale na ještě menším plátně a s kotvou z našich spritů:
`animals_sheet_chunky_1` (112×96, 6 gen, zvířata 18–26 px, kotva `anchor_animals_chunky.png`) a `decor_sheet_chunky_1` (96×96, 5 gen, dekorace 12–18 px, kotva `anchor_decor_chunky.png`).
Stín pod zvířaty se přidává ve slicru (`add_shadow`). Pravidlo velikosti plátna: ≤96 px = drobné rekvizity, ~112 = zvířata, 192 = budovy, 256 jen pro karty/close-upy.
Detailnější verze všech sheetů jsou v `art/pixellab/sprites_detailed/` (karty, close-upy). Srovnání: `styles/density_animals_decor.png` (řádek 1 moje zvířata, 2 nové PixelLab, 3 moje rekvizity, 4 nové dekorace).
**Celkem 67 generací** (zůstatek 1 151).

Plán:
- **Kulisy, zvířata, budovy, terén:** vlastní generace (kód) nebo PixelLab (`create_object_pro_flash`, izometrie) – podle toho, co vypadá lépe; vždy s paletou výše.
- **Návštěvníci (stovky variant, chůze 4–8 směrů):** PixelLab `create_character` + animace (postup z fronty: `tools/pixellab.py`, ledger proti duplikátům, `sprite_qa.py`). Generace jsou omezené, proto jednou správně.
- **Z fronty vzít:** `tools/pixellab.py`, `tools/sprite_qa.py`, `tools/sprite_fix.py`, `tools/palette_lock.py`, `tools/import-anim.py`, pravidla z `docs/PIXELLAB_BRIEF.md` (jeden směr na volání, ledger, kontrola plovoucích pixelů).
- PixelLab klíč v tomto repu zatím není; do prostředí ho dodáme stejně jako ve frontě (síťová proxy / tajemství).

## Seznam assetů fáze 1

Terén: tráva (3 varianty), cesta, voda, led, písek (savana), džungle. Plot, brána s nápisem, kasa, stánek s cukrovou vatou, lavička, strom ×3, keř, květiny.
Zvířata: slon, žirafa, zebra, flamingo, tučňák, lev, panda, opice, želva. Návštěvníci: viz výše.
