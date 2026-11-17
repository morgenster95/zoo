// Natočí reel v enginu: node tools/record-reel.mjs hook [--still 12.5 ...] [--from 0 --to 10]
// Spustí Vite, otevře web/reel.html v Chrome (headless) a snímek po snímku (30 fps) pošle do ffmpeg spolu se zvukem.
import { spawn, execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import puppeteer from 'puppeteer-core';
import { ROOT } from './lib.mjs';

const args = process.argv.slice(2);
const reel = args.find((a) => !a.startsWith('--')) || 'hook';
const stills = []; for (let k = 0; k < args.length; k++) if (args[k] === '--still') stills.push(Number(args[k + 1]));
const arg = (n, d) => (args.includes(n) ? Number(args[args.indexOf(n) + 1]) : d);
const dir = path.join(ROOT, 'marketing', 'reels', reel);
const FPS = 30, PORT = 5199;
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const FFMPEG = process.env.FFMPEG || 'ffmpeg';

fs.mkdirSync(path.join(ROOT, 'web', 'public', 'reels', reel), { recursive: true });
fs.copyFileSync(path.join(dir, 'timeline.json'), path.join(ROOT, 'web', 'public', 'reels', reel, 'timeline.json'));

const vite = spawn('npx', ['vite', '--port', String(PORT), '--strictPort'], { cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe'] });
await new Promise((ok, no) => { const t = setTimeout(() => no(new Error('vite nenaběhl')), 30000); vite.stdout.on('data', (d) => { if (String(d).includes('Local')) { clearTimeout(t); ok(); } }); });
const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new', args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--ignore-gpu-blocklist', '--hide-scrollbars', '--force-device-scale-factor=1'] });
try {
  const page = await browser.newPage();
  page.on('pageerror', (e) => console.log('PAGE ERROR', e.message));
  page.on('console', (m) => { if (m.type() === 'error') console.log('console:', m.text()); });
  await page.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
  await page.goto(`http://localhost:${PORT}/reel.html?reel=${reel}${args.includes('--clean') ? '&clean=1' : ''}${args.includes('--cam') ? '&cam=' + args[args.indexOf('--cam') + 1] : ''}`);
  await page.waitForFunction('window.__reel && window.__reel.ready', { timeout: 60000 });
  const total = await page.evaluate('window.__reel.total');
  const clip = { x: 0, y: 0, width: 1080, height: 1920 };
  if (stills.length) {
    const out = path.join(dir, args.includes('--clean') ? 'stills_clean' : 'stills'); fs.mkdirSync(out, { recursive: true });
    for (const t of stills) { await page.evaluate((x) => window.__reel.setTime(x), t); await page.screenshot({ path: path.join(out, `t${t.toFixed(1)}.png`), clip }); console.log('still', t); }
  } else {
    const from = arg('--from', 0), to = Math.min(arg('--to', total), total);
    const outFile = path.join(dir, args.includes('--from') ? 'preview.mp4' : 'out.mp4');
    const audio = path.join(dir, 'audio.wav');
    const ff = spawn(FFMPEG, ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', ...(fs.existsSync(audio) ? ['-ss', String(from), '-i', audio] : []),
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-r', String(FPS), ...(fs.existsSync(audio) ? ['-c:a', 'aac', '-b:a', '160k', '-shortest'] : []), outFile], { stdio: ['pipe', 'ignore', 'inherit'] });
    const frames = Math.floor((to - from) * FPS);
    for (let f = 0; f < frames; f++) {
      await page.evaluate((x) => window.__reel.setTime(x), from + f / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 94, clip });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      if (f % 60 === 0) console.log(`snímek ${f}/${frames}`);
    }
    ff.stdin.end(); await new Promise((r) => ff.on('close', r));
    console.log('hotovo:', outFile);
  }
} finally { await browser.close(); vite.kill(); }
