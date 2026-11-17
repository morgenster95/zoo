# Návrh: Mud & Iron → ZOO

Zdroj: repo `morgenster95/fronta` (engine/, ingest/, tools/, web/, themes/). Jádro je psané „nezávisle na tématu“ (`engine/`, `themes/<id>/`),
takže přepis je hlavně nové téma + odstranění boje.

## Mapování mechanik

| Mud & Iron | ZOO |
|---|---|
| Follower = voják, komentář `CONCORD`/`HEGEMONY` | Follower = **návštěvník**, komentář s klíčovým slovem zóny (`SAVANA`, `JUNGLE`, `ARCTIC`, `OCEAN`…) |
| Dvě frakce, jedna strana napořád | **Zóny/habitaty** (návštěvník si vybere oblíbenou, nikdo proti nikomu) |
| Mapa zákopů, 32 sektorů, otevírá se po 8 | Mapa zoo: sektory se otevírají podle zaplnění, cesty, náměstí, výběhy |
| Slot v zákopu (trvalé místo) | Trvalé místo návštěvníka: lavička, cesta, fronta u stánku, před výběhem |
| Role (puškař, medik, kuchař…) | **Typy návštěvníků**: rodič s kočárkem, školák, fotograf, prodavač balónků, ošetřovatel-nadšenec, důchodce s krmením, turista s mapou; přání z komentáře („I want to be a photographer“) |
| Denní tah 13:00 UTC, příběhy ze šablon (`engine/story.js`) | Denní tah: zápis do **deníku návštěvníka** (zvíře kýchlo, balónek uletěl, ztracený lístek, selfie se žirafou) |
| Kronika dne, Trench Gazette | **Zoo Gazette**: noviny dne, nováčci jmenovitě, nejlepší příhody |
| Hlasování o stavbách (HOSPITAL / PILLBOXES) | Hlasování, **co se postaví dál** (`PENGUINS` / `PANDA` / `CAROUSEL`), platí od příští vlny |
| Závod o kótu: kdo první naverbuje 100 | **Závod zón**: která zóna první dosáhne 100 návštěvníků, odemkne nové zvíře a oslavu |
| Povýšení, hrdina | Odznaky: Věrný návštěvník (X dní v řadě), Krmič, Fotograf měsíce |
| Smrt, nástupce z rodu, ranění, nezvěstní | **Odpadá.** Max. „ztratil se a našel“. Rodinný přívěsek (děti, vnuci) možná později jako vtip |
| Boj, bombardování, bunkry, letadla, výpravy, dráty | **Odpadá celé** (`battle.js`, `race.js` částečně, `orders.js`, `shells.js`, `pilots.js`, `wiring.js`, `valley.js`, `house.js` ven) |
| Převzetí vojáka (`ENLIST-XXXX`) | Převzetí návštěvníka (kód v komentáři), viz ARCHITECTURE |
| War Bonds / Patreon (hvězda nad hlavou) | **Přátelé zoo** (podporovatelé): zlatá hvězdička / vlaječka |
| Reely: scénáře renderované z webu (`web/src/reel-*.js`, `tools/record-reel.mjs`) | Stejný princip, scény: otevření výběhu, příjezd nového zvířete, ranní fronta u brány |

## Co z fronty použít přímo

Generické (po úpravě názvů): `engine/rng.js`, `engine/mapgen.js` (jiné dlaždice a generátor cest/výběhů), `engine/roster.js` (soupiska, shardy zápisů,
přání rolí z komentářů), `engine/story.js` + `engine/chronicle.js` (šablony příběhů, kronika), `engine/soldier.js` → `visitor.js`,
`ingest/poll-comments.mjs`, `ingest/publish.mjs`, `ingest/triggers.mjs`, `tools/loop.sh`, `tools/lib.mjs`, `tools/build-data.mjs`, `tools/fake-roster.mjs`,
workflows `front-loop`, `watchdog`, `refresh-token`, `media`, `reel`; web: `terrain.js`, `camera.js`, `ui.js` (hledání @handle, karta, sdílení), `life.js` (život na mapě: chodící návštěvníci).
Hlavně ověřená odolnost smyčky (čistý reset z `origin/main` každé kolo, issues při selhání, watchdog).

Jádro mapy ve frontě je 2D shora (dlaždice 16 px); zoo chceme **izometricky 2:1** (jako reference), takže `terrain.js`/`camera.js` se přepíšou na izometrickou projekci
(PixiJS zůstává, řazení podle hloubky `i+j`, jako v `art/proto/make_proto.py`).

## Milníky

1. **Základ:** repo, téma `zoo`, mapa (cesty, brána, 4 výběhy), 4 000 falešných návštěvníků na izometrické mapě, hledání @handle, karta návštěvníka.
2. **Ingest:** komentář → návštěvník (a odpověď bota), denní tah se zápisy z šablon, Zoo Gazette.
3. **Hra kolem toho:** hlasování o stavbách, závod zón, odznaky, přání typů.
4. **Provoz a marketing:** hosting a data (viz ARCHITECTURE), reely z webu, fronta příspěvků.

## Otevřené otázky (pro uživatele)

- Finální název a @handle účtu na IG.
- Jazyk (fronta je anglicky pro USA/UK; zoo také?).
- Zóny: 4 (SAVANA, JUNGLE, ARCTIC, OCEAN) nebo jedna zoo bez soupeření?
- Zda nechat „závod“ mezi zónami, nebo jen společné odemykání (příjemnější pro komunitu, žádný „poražený“).

## Výchozí pozice a ekonomika (rozhodnuto 17. 11. 2026)

**Start = absolutně malá, chudá zoo** (`art/proto/mini_zoo.py`, ukázka `art/proto/styles/mini_zoo_start.png`): chudá dřevěná brána, kasa, jeden výběh se 2 zebrami, loužička s 2 plameňáky,
2 lavičky, bedny, seno, plevel, hodně holé hlíny a **3 prázdné parcely** (kolíky s provazem a cedulí „?“), kam se bude stavět podle hlasování.

**Kasa u vstupu ukazuje mince.** Pravidlo: **každý návštěvník (follower) = 10 mincí.** Zůstatek = 10 × (počet návštěvníků) − utraceno za stavby.
Nová stavba se zaplatí z mincí; hlasování určuje, CO se postaví, mince, ČÍM se zaplatí. Ceny jsou k doladění (první návrh):
lavička 20, stánek 150, kavárna 300, malý výběh 500, velký výběh 1 000, nové zvíře 200–1 500, okrasná stavba 400.
Mince se nikdy nevracejí na 0 a nikdo o ně nepřijde (follower, který odejde, mince nesebere).

**Rodiny budov** (`styles/building_families.png`): `classic` (hrázděný dům, výchozí), `modern` (plochá střecha, prosklení, dřevěné lamely, solární panely),
`african` (kulatá chýše se slaměnou střechou a bílým vzorem), `asian` (pagoda), `andes` (stupňovitá barevná stavba). Výběh dostane rodinu podle zvířat (savana = africká, panda = asijská atd.),
moderní pro zázemí (kavárna, obchod, vstup po rozšíření). Starší dřevěné budovy zůstávají pro chudý začátek.
