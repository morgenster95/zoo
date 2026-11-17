// Katalog staveb. Cena v mincích, `sprite` = název v atlasu (assets/props.json), `lot` = jak se zapíše do parcely.
// Majitel hry vždy sám vybírá, které položky se nabídnou k hlasování (data/queue.json), takže ceny jsou jen vodítko.
export const CATALOG = {
  // výzdoba
  bench:        { key: 'BENCH',    name: 'Park bench',            group: 'decor',   price: 20,   lot: { t: 'build', sprite: 'd_bench_wood' } },
  flowers:      { key: 'FLOWERS',  name: 'Flower garden',         group: 'decor',   price: 40,   lot: { t: 'build', sprite: 'd_planter' } },
  oak:          { key: 'TREE',     name: 'Shade tree',            group: 'decor',   price: 60,   lot: { t: 'build', sprite: 'oak1' } },
  lamp:         { key: 'LAMP',     name: 'Street lamp',           group: 'decor',   price: 30,   lot: { t: 'build', sprite: 'd_lamp' } },
  fountain:     { key: 'FOUNTAIN', name: 'Stone fountain',        group: 'decor',   price: 150,  lot: { t: 'build', sprite: 'd_fountain' } },
  statue:       { key: 'STATUE',   name: 'Founders statue',       group: 'decor',   price: 250,  lot: { t: 'build', sprite: 'd_statue' } },
  balloons:     { key: 'BALLOONS', name: 'Balloon stand',         group: 'decor',   price: 80,   lot: { t: 'build', sprite: 'd_balloons' } },
  picnic:       { key: 'PICNIC',   name: 'Picnic area',           group: 'decor',   price: 90,   lot: { t: 'build', sprite: 'd_picnic' } },
  // služby
  cart:         { key: 'ICECREAM', name: 'Ice cream cart',        group: 'service', price: 100,  lot: { t: 'build', sprite: 'd_kiosk' } },
  cafe:         { key: 'CAFE',     name: 'Modern café',           group: 'service', price: 300,  lot: { t: 'build', sprite: 'b_modern' } },
  shop:         { key: 'SHOP',     name: 'Gift shop',             group: 'service', price: 350,  lot: { t: 'build', sprite: 'b_classic' } },
  // výběhy
  giraffes:     { key: 'GIRAFFES', name: 'Giraffe paddock',       group: 'enclosure', price: 600,  lot: { t: 'paddock', animals: ['giraffe', 'giraffe'], house: 'b_african' } },
  elephants:    { key: 'ELEPHANT', name: 'Elephant yard',         group: 'enclosure', price: 900,  lot: { t: 'paddock', animals: ['elephant', 'elephant'], house: 'b_african' } },
  lions:        { key: 'LIONS',    name: 'Lion rock',             group: 'enclosure', price: 700,  lot: { t: 'paddock', animals: ['lion', 'lion'], house: 'b_african' } },
  pandas:       { key: 'PANDA',    name: 'Panda garden',          group: 'enclosure', price: 800,  lot: { t: 'paddock', animals: ['panda', 'panda'], house: 'b_asian' } },
  tigers:       { key: 'TIGERS',   name: 'Tiger grove',           group: 'enclosure', price: 750,  lot: { t: 'paddock', animals: ['tiger', 'tiger'], house: 'b_asian' } },
  penguins:     { key: 'PENGUINS', name: 'Penguin pool',          group: 'enclosure', price: 500,  lot: { t: 'build', sprite: 'b_igloo', animals: ['penguin', 'penguin', 'penguin'] } },
  hippos:       { key: 'HIPPOS',   name: 'Hippo lagoon',          group: 'enclosure', price: 650,  lot: { t: 'pond', animals: ['hippo', 'hippo'] } },
  monkeys:      { key: 'MONKEYS',  name: 'Monkey hill',           group: 'enclosure', price: 450,  lot: { t: 'paddock', animals: ['monkey', 'monkey', 'monkey'], house: 'b_andes' } },
  // atrakce
  carousel:     { key: 'CAROUSEL', name: 'Carousel',              group: 'attraction', price: 800,  lot: { t: 'build', sprite: 'b_carousel' } },
  aviary:       { key: 'AVIARY',   name: 'Glass aviary',          group: 'attraction', price: 1000, lot: { t: 'build', sprite: 'b_dome' } },
};

export const itemByKey = (key) => Object.entries(CATALOG).find(([, v]) => v.key === String(key).toUpperCase());
