# Mechaniky: jak se zoo staví (návrh k odsouhlasení, 17. 11. 2026)

Základ je z fronty (denní rytmus, hlasování v komentářích, noviny), jen místo války staví zoo. Nic se neničí, nikdo neumírá, nikdo nepřichází o mince.

## 1. Příjem: mince
- **Každý nový follower = 1 návštěvník = 10 mincí**, okamžitě (kasa u brány počítá živě).
- Návštěvník nikdy neodejde a mince se nikdy neodečítají kvůli unfollow.
- Bez followu nejde nic: komentář může jen **přiřadit jméno** (viz 5), ne vytvořit návštěvníka.

## 2. Co se dá postavit (katalog, ceny jsou první odhad)
| Skupina | Příklady | Cena (mince) | Poznámka |
|---|---|---|---|
| Výzdoba | lavička, květinový záhon, fontána, koš | 20–150 | rychlé, levné, na malé parcely |
| Služby | vozík se zmrzlinou, kavárna, toalety, obchod se suvenýry, hřiště | 100–600 | zvyšují „hodnocení“ zoo, moderní rodina budov |
| Výběhy | malý výběh + 2 zvířata, velký výběh, voliéra, akvárium, terárium | 400–2 000 | styl budovy podle rodiny (savana = africká, panda = asijská…) |
| Atrakce | kolotoč, vláček, vyhlídková věž, obří kolo | 800–5 000 | zabírají víc parcel |
| Zvíře do existujícího výběhu | slon, žirafa, panda, tučňák… | 200–1 500 | levnější způsob, jak zoo oživit |
| Památky | brána z kamene, socha zakladatelů | 3 000+ | odemykají se milníky |

## 3. Parcely a růst mapy
- Mapa je mřížka bloků 5×5 (parcely) mezi silnicemi. Oblast se otevírá podle počtu návštěvníků (viz `engine/layout.js`).
- **Vždy jsou volné aspoň 2 parcely** (ceduli „?“ si hráči všimnou). Nový prstenec = nové volné parcely.
- Velká stavba (výběh, atrakce) zabere 2 až 4 sousední parcely; stavba se hlasuje na konkrétní parcelu (označená číslem na mapě).

## 4. Hlasování (komentáře pod postem, jako ve frontě)
- Rytmus: **ranní noviny 13:00 UTC** (výsledek minulého hlasování, nový den, nová stavba se otevře), **večerní post 23:00 UTC** (nové hlasování).
- Post nabídne **3 možnosti** z katalogu, vždy **dostupné ze zůstatku** (aspoň jedna levná, ať se zoo nezasekne). Hlasuje se klíčovým slovem v komentáři (`PANDA`, `CAFE`, `CAROUSEL`).
- **Jeden hlas na účet** (platí poslední); hlasovat smí kdokoli, kdo je návštěvník.
- Vítěz se zaplatí z mincí a **staví se přes noc** (na mapě stavba s lešením a dělníky), ráno je otevřeno a nové noviny ho ukážou.
- Při remíze rozhodne nejlevnější (nebo losování).

## 5. Návštěvník a jeho jméno
- Follow = anonymní návštěvník („Visitor #12408“, náhodný vzhled). 
- **Komentář s klíčovým slovem** (`ZOO`, `MINE`…) nebo DM propojí účet s návštěvníkem: dostane své jméno a **vzhled podle účtu**.
- Přání typu v komentáři („I want to be a photographer / grandpa / balloon fan“) mění vzhled postavičky (11 typů), jedno přání zdarma, pak 1× za 7 dní.
- **Podporovatel** (Patreon/Friend of the zoo) má zlatou hvězdičku nad hlavou.

## 6. Denní tah a noviny (Zoo Gazette)
- Každé ráno: kolik návštěvníků přibylo, co se otevřelo, výsledek hlasování, 3–5 příhod vybraných návštěvníků (šablony jako ve frontě: „@name fed the flamingos“, „@name lost a balloon“), nové jméno týdne.
- Každý návštěvník má na kartě **deník** s denními zápisy (kdo se přihlásil, ten se zapíše).

## 7. Milníky (velké okamžiky pro reely)
100, 500, 1 000, 5 000, 10 000 návštěvníků: odemknou novou skupinu katalogu, otevřou prstenec a pustí **slavnostní událost** (ohňostroj, páska se stříhá, balónky letí). Každý milník = jeden reel.

## 8. Rozhodnuto (17. 11. 2026)
- **Hlasování jednou denně** (večer otevřeno, ráno vyhodnoceno, rytmus jako fronta).
- **Mince jsou společné.** Neexistuje „vítěz bez peněz“: **možnosti vybírá majitel hry** (`data/queue.json`, pořadí = priorita), takže jsou vždy předem připravené a dostupné. Engine to hlídá: `openVote` odmítne nabídku dražší než zůstatek, `daily.mjs` ji přeskočí a napíše to do logu.
- **Stavba stojí okamžitě** po vyhodnocení. Bez hlasů (nebo při remíze) vyhrává první možnost v pořadí od majitele.
- **Vždy aspoň 2 volné parcely.** Když dojdou bloky, mapa se rozšíří o prstenec (`state.ring`), i když návštěvníků ještě není tolik.
- Implementace: `engine/catalog.js` (katalog), `engine/vote.js` (otevřít, hlas, vyhodnotit, parcely), `tools/daily.mjs` (denní tah), web ukazuje panel „Tonight's vote“. Testy v `engine/engine.test.js`.

## 9. Ještě otevřené
- Napojení Instagramu: komentáře → `castVote`, počet followerů → nové návštěvníky.
- Noviny (Zoo Gazette) a deníky návštěvníků, milníky 100/500/1 000/5 000/10 000.
- Velké stavby přes víc parcel (zatím 1 stavba = 1 parcela).
