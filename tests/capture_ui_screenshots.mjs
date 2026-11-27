import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const require = createRequire(import.meta.url);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const appData = process.env.APPDATA || '';
const playwrightCandidates = [
  'playwright',
  path.join(appData, 'npm', 'node_modules', '@playwright', 'cli', 'node_modules', 'playwright'),
  path.join(appData, 'npm', 'node_modules', 'playwright'),
];
let chromium;
for (const candidate of playwrightCandidates) {
  try {
    ({ chromium } = require(candidate));
    if (chromium) break;
  } catch {}
}
if (!chromium) throw new Error('Playwright module not found. Install playwright or @playwright/cli.');

const ROOT = path.resolve(__dirname, '..');
const OUT_DIR = path.join(ROOT, 'docs', 'assets');
fs.mkdirSync(OUT_DIR, { recursive: true });

async function waitForServer(url, retries = 30) {
  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(url);
      if (res.ok) return true;
    } catch {}
    await new Promise((r) => setTimeout(r, 300));
  }
  throw new Error(`Server did not respond at ${url}`);
}

async function main() {
  const srv = spawn('python', ['run.py', 'server'], { cwd: ROOT, stdio: 'pipe' });
  let browser;
  const pageErrors = [];

  try {
    await waitForServer('http://127.0.0.1:8765/api/status');
    browser = await chromium.launch({
      headless: true,
      executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    });
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    page.on('pageerror', (err) => pageErrors.push(err.message));

    await page.goto('http://127.0.0.1:8765/index.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(OUT_DIR, 'ui-01-ingest.png'), fullPage: false });

    const tabs = [
      { sel: '[data-tab="tab-presets"]', file: 'ui-02-presets.png' },
      { sel: '[data-tab="tab-sound"]', file: 'ui-03-sound.png' },
      { sel: '[data-tab="tab-export"]', file: 'ui-04-export.png' },
    ];
    for (const t of tabs) {
      await page.click(t.sel);
      await page.waitForTimeout(300);
      await page.screenshot({ path: path.join(OUT_DIR, t.file), fullPage: false });
    }

    await page.click('#link-user-guide');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    await page.screenshot({ path: path.join(OUT_DIR, 'ui-05-user-guide.png'), fullPage: true });

    console.log('Captured 5 UI screenshots successfully. PageErrors:', pageErrors.length);
    if (pageErrors.length > 0) {
      console.error('Page errors:', pageErrors);
      process.exitCode = 1;
    }
  } finally {
    if (browser) await browser.close();
    srv.kill();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
