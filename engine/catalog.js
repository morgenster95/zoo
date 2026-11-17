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
  cafe:         { key: 'CAFE',     name: 'Modern café',           group: 'service', price: 300,  lot: { t: 'build', sprite: 'bp_cafe' } },
  shop:         { key: 'SHOP',     name: 'Gift shop',             group: 'service', price: 350,  lot: { t: 'build', sprite: 'bp_shop' } },
  // výběhy
  giraffes:     { key: 'GIRAFFES', name: 'Giraffe paddock',       group: 'enclosure', price: 600,  lot: { t: 'paddock', animals: ['giraffe', 'giraffe'], house: 'bp_lodge' } },
  elephants:    { key: 'ELEPHANT', name: 'Elephant yard',         group: 'enclosure', price: 900,  lot: { t: 'paddock', animals: ['elephant', 'elephant'], house: 'bp_barn' } },
  lions:        { key: 'LIONS',    name: 'Lion rock',             group: 'enclosure', price: 700,  lot: { t: 'paddock', animals: ['lion', 'lion'], house: 'bp_lodge' } },
  pandas:       { key: 'PANDA',    name: 'Panda garden',          group: 'enclosure', price: 800,  lot: { t: 'paddock', animals: ['panda', 'panda'], house: 'bp_pagoda' } },
  tigers:       { key: 'TIGERS',   name: 'Tiger grove',           group: 'enclosure', price: 750,  lot: { t: 'paddock', animals: ['tiger', 'tiger'], house: 'bp_pagoda' } },
  penguins:     { key: 'PENGUINS', name: 'Penguin pool',          group: 'enclosure', price: 500,  lot: { t: 'build', sprite: 'bp_penguin_house', animals: ['penguin', 'penguin', 'penguin'] } },
  hippos:       { key: 'HIPPOS',   name: 'Hippo lagoon',          group: 'enclosure', price: 650,  lot: { t: 'pond', animals: ['hippo', 'hippo'] } },
  monkeys:      { key: 'MONKEYS',  name: 'Monkey hill',           group: 'enclosure', price: 450,  lot: { t: 'paddock', animals: ['monkey', 'monkey', 'monkey'], house: 'bp_treehouse' } },
  aquarium:     { key: 'AQUARIUM', name: 'Aquarium',              group: 'enclosure', price: 1200, lot: { t: 'build', sprite: 'bp_aquarium' } },
  playground:   { key: 'PLAY',     name: 'Playground',            group: 'service', price: 250,  lot: { t: 'build', sprite: 'bp_playground' } },
  toilets:      { key: 'TOILETS',  name: 'Restrooms',             group: 'service', price: 200,  lot: { t: 'build', sprite: 'bp_toilets' } },
  clinic:       { key: 'CLINIC',   name: 'Animal hospital',       group: 'service', price: 900,  lot: { t: 'build', sprite: 'bp_clinic' } },
  popcorn:      { key: 'POPCORN',  name: 'Popcorn kiosk',         group: 'service', price: 160,  lot: { t: 'build', sprite: 'bp_popcorn' } },
  // atrakce
  carousel:     { key: 'CAROUSEL', name: 'Carousel',              group: 'attraction', price: 800,  lot: { t: 'build', sprite: 'bp_carousel' } },
  ferris:       { key: 'FERRIS',   name: 'Ferris wheel',          group: 'attraction', price: 2500, lot: { t: 'build', sprite: 'bp_ferris' } },
  train:        { key: 'TRAIN',    name: 'Zoo train station',     group: 'attraction', price: 1800, lot: { t: 'build', sprite: 'bp_station' } },
  // vylepšení vstupu (nezabírá parcelu)
  stonegate:    { key: 'GATE',     name: 'Stone entrance gate',   group: 'landmark', price: 1500, lot: { t: 'upgrade', what: 'gate', sprite: 'bp_gate' } },
  ticketbooth:  { key: 'BOOTH',    name: 'New ticket booth',      group: 'landmark', price: 400,  lot: { t: 'upgrade', what: 'kasa', sprite: 'bp_ticket' } },
  aviary:       { key: 'AVIARY',   name: 'Glass aviary',          group: 'attraction', price: 1000, lot: { t: 'build', sprite: 'bp_aviary' } },
};

export const itemByKey = (key) => Object.entries(CATALOG).find(([, v]) => v.key === String(key).toUpperCase());
