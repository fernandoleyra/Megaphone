#!/usr/bin/env node
/* eslint-disable no-console */
/**
 * megaphone-demo Playwright runner.
 *
 * Reads a happy-path config (JSON) and produces:
 *   - A numbered PNG frame for every visible state change
 *   - Optionally a webm recording of the whole session (if config.record === true)
 *
 * Usage:
 *   node playwright_runner.js --config .megaphone/assets/demo/hero.json
 *
 * Frames go to <config_dir>/<name>/frames/. The skill orchestrator turns those
 * frames into a GIF with to_gif.sh (ffmpeg) or an MP4 with to_mp4.sh.
 *
 * Stays close to the Playwright surface; no clever framework on top.
 */

const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i++) {
    const tok = argv[i];
    if (tok.startsWith('--')) {
      const k = tok.slice(2);
      const v = argv[i + 1];
      out[k] = v && !v.startsWith('--') ? v : true;
      if (v && !v.startsWith('--')) i++;
    }
  }
  return out;
}

function readConfig(configPath) {
  const raw = fs.readFileSync(configPath, 'utf8');
  return JSON.parse(raw);
}

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

async function main() {
  const args = parseArgs(process.argv);
  if (!args.config) {
    console.error('--config <path> required');
    process.exit(2);
  }
  const config = readConfig(args.config);

  let chromium;
  try {
    ({ chromium } = require('playwright'));
  } catch (e) {
    console.error(JSON.stringify({
      ok: false,
      error: 'Playwright not installed. Run: npm install -g playwright && npx playwright install chromium',
    }));
    process.exit(3);
  }

  const configDir = path.dirname(args.config);
  const name = config.name || 'demo';
  const outDir = path.join(configDir, name);
  const framesDir = path.join(outDir, 'frames');
  ensureDir(framesDir);

  const viewport = config.viewport || { width: 1280, height: 720 };
  const launchOpts = { headless: true };

  const browser = await chromium.launch(launchOpts);
  const contextOpts = {
    viewport,
    deviceScaleFactor: config.deviceScaleFactor || 2,
  };
  if (config.device) {
    const { devices } = require('playwright');
    if (devices[config.device]) Object.assign(contextOpts, devices[config.device]);
  }
  if (config.record) {
    contextOpts.recordVideo = { dir: outDir, size: viewport };
  }
  const context = await browser.newContext(contextOpts);
  const page = await context.newPage();

  // Allow login via env vars without ever logging them
  const env = process.env;
  for (const step of config.steps || []) {
    if (step.text && typeof step.text === 'string') {
      step.text = step.text
        .replace(/\$\{MEGAPHONE_DEMO_USERNAME\}/g, env.MEGAPHONE_DEMO_USERNAME || '')
        .replace(/\$\{MEGAPHONE_DEMO_PASSWORD\}/g, env.MEGAPHONE_DEMO_PASSWORD || '');
    }
  }

  let frameIdx = 0;

  // Auto-snap before and after each step that could change the visible state.
  async function snap(label) {
    frameIdx++;
    const file = path.join(framesDir, `${String(frameIdx).padStart(3, '0')}_${label || 'frame'}.png`);
    await page.screenshot({ path: file, fullPage: false });
    return file;
  }

  const initialUrl = config.url || (config.steps.find(s => s.kind === 'goto') || {}).url;
  if (!initialUrl) {
    throw new Error('Config must define `url` or include a step with kind=goto.');
  }

  await page.goto(initialUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(800);
  await snap('start');

  for (const step of config.steps || []) {
    try {
      switch (step.kind) {
        case 'goto':
          await page.goto(step.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
          await page.waitForTimeout(500);
          await snap(step.label || 'goto');
          break;
        case 'wait':
          if (step.selector) {
            await page.waitForSelector(step.selector, {
              state: step.state || 'visible',
              timeout: (step.seconds || 10) * 1000,
            });
          } else {
            await page.waitForTimeout(Math.min((step.seconds || 1) * 1000, 30000));
          }
          break;
        case 'click': {
          const target = step.text
            ? page.getByText(step.text, { exact: false })
            : page.locator(step.selector);
          await target.first().click({ timeout: 8000 });
          await page.waitForTimeout(300);
          await snap(step.label || 'click');
          break;
        }
        case 'type': {
          const target = page.locator(step.selector);
          await target.first().click({ timeout: 8000 });
          await target.first().fill('');
          await target.first().type(step.text || '', { delay: step.delay || 60 });
          await snap(step.label || 'type');
          break;
        }
        case 'scroll':
          if (step.selector) {
            await page.locator(step.selector).first().scrollIntoViewIfNeeded();
          } else if (typeof step.y === 'number') {
            await page.evaluate(y => window.scrollTo({ top: y, behavior: 'smooth' }), step.y);
          }
          await page.waitForTimeout(400);
          await snap(step.label || 'scroll');
          break;
        case 'hover': {
          const target = page.locator(step.selector);
          await target.first().hover({ timeout: 5000 });
          await snap(step.label || 'hover');
          break;
        }
        case 'screenshot':
          await snap(step.label || 'frame');
          break;
        default:
          console.warn(`Unknown step kind: ${step.kind}`);
      }
    } catch (e) {
      console.error(JSON.stringify({
        ok: false,
        error: `Step ${step.kind} failed: ${e.message}`,
        step,
      }));
      // Continue with remaining steps so we still get a partial recording.
    }
  }

  await page.waitForTimeout(500);
  await snap('end');

  await context.close();
  await browser.close();

  console.log(JSON.stringify({
    ok: true,
    name,
    out_dir: outDir,
    frames: frameIdx,
    frames_dir: framesDir,
  }));
}

main().catch(err => {
  console.error(JSON.stringify({ ok: false, error: err.message }));
  process.exit(1);
});
