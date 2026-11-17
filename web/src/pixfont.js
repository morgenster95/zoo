// Pixelové písmo 3×5 (soubor assets/font.json z art/proto/zoo_art.py) → canvas prvky pro HUD a tabuli mincí.
export function textCanvas(font, str, sc, color) {
  const w = [...str].reduce((a, ch) => a + ((font[ch] || font[' '])[0].length + 1) * sc, 0) - sc;
  const c = document.createElement('canvas'); c.width = Math.max(1, w); c.height = 5 * sc;
  const ctx = c.getContext('2d'); ctx.fillStyle = color;
  let x = 0;
  for (const ch of str) {
    const gl = font[ch] || font[' '];
    gl.forEach((row, yy) => [...row].forEach((v, xx) => { if (v === '1') ctx.fillRect(x + xx * sc, yy * sc, sc, sc); }));
    x += (gl[0].length + 1) * sc;
  }
  return c;
}

const COIN = ['01110', '11111', '11111', '11111', '01110'];
export function coinCanvas(sc) {
  const c = document.createElement('canvas'); c.width = 5 * sc; c.height = 5 * sc;
  const ctx = c.getContext('2d');
  COIN.forEach((row, y) => [...row].forEach((v, x) => { if (v === '1') { ctx.fillStyle = (x === 1 && (y === 1 || y === 2)) ? '#fff2a6' : (x === 4 || y === 4) ? '#d9962a' : '#ffc93c'; ctx.fillRect(x * sc, y * sc, sc, sc); } }));
  return c;
}

/** tabule nad kasou: cedule s mincí a číslem na dvou sloupcích (nativní rozlišení, zvětšuje svět) */
export function boardCanvas(font, coins) {
  const num = coins.toLocaleString('en-US');
  const tw = [...num].reduce((a, ch) => a + ((font[ch] || font[' '])[0].length + 1), 0) - 1;
  const bw = Math.max(34, tw + 16), bh = 16, H = bh + 14;
  const c = document.createElement('canvas'); c.width = bw + 2; c.height = H;
  const ctx = c.getContext('2d');
  const px = (x, y, w, h, col) => { ctx.fillStyle = col; ctx.fillRect(x, y, w, h); };
  px(7, bh - 1, 2, 13, '#7a5230'); px(bw - 8, bh - 1, 2, 13, '#7a5230');
  px(0, 0, bw, bh, '#3d2a28'); px(1, 1, bw - 2, bh - 2, '#fff3d6'); px(1, 1, bw - 2, 2, '#ffc93c'); px(1, bh - 4, bw - 2, 3, '#f6d98f');
  ctx.drawImage(coinCanvas(1), 3, 5);
  let x = 10;
  for (const ch of num) {
    const gl = font[ch] || font[' '];
    gl.forEach((row, yy) => [...row].forEach((v, xx) => { if (v === '1') px(x + xx, 5 + yy, 1, 1, '#d9742a'); }));
    x += gl[0].length + 1;
  }
  return c;
}
