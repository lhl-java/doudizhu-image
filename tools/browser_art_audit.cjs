#!/usr/bin/env node
'use strict';

// Real-browser capture, not a visual approval oracle. All persisted evidence stays in this project.
// Example: node tools/browser_art_audit.cjs --output .work/browser-art-audit
// Optional: --screens 08-join-room,38-mail --aspects wide,standard --base-url http://127.0.0.1:8771
// AUDIT_PLAYWRIGHT_PATH and AUDIT_CHROME_PATH override the two local dependency defaults below.
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const os = require('node:os');

const ROOT = path.resolve(__dirname, '..');
const defaults = {
  playwright: 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright',
  chrome: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
};
function options(argv) {
  const result = { output: '.work/browser-art-audit', baseUrl: 'http://127.0.0.1:8771', aspects: 'wide,standard', screens: '' };
  for (let i = 0; i < argv.length; i += 2) {
    const name = { '--output': 'output', '--base-url': 'baseUrl', '--aspects': 'aspects', '--screens': 'screens' }[argv[i]];
    if (!name || !argv[i + 1]) throw new Error('Expected --output, --base-url, --aspects, or --screens followed by a value');
    result[name] = argv[i + 1];
  }
  return result;
}
function insideProject(value) {
  const resolved = path.resolve(ROOT, value);
  const relative = path.relative(ROOT, resolved);
  if (!relative || relative.startsWith('..' + path.sep) || relative === '..' || path.isAbsolute(relative)) {
    throw new Error('Evidence path must be a directory inside this project: ' + value);
  }
  return resolved;
}
async function ensureLocalDirectory(value) {
  const result = insideProject(value);
  let existing = result;
  while (true) {
    try { await fs.access(existing); break; } catch { existing = path.dirname(existing); }
  }
  const real = await fs.realpath(existing);
  const realRoot = await fs.realpath(ROOT);
  const relative = path.relative(realRoot, real);
  if (relative.startsWith('..' + path.sep) || relative === '..' || path.isAbsolute(relative)) {
    throw new Error('Evidence directory escapes project through a link: ' + value);
  }
  await fs.mkdir(result, { recursive: true });
  return result;
}
const sha256 = buffer => crypto.createHash('sha256').update(buffer).digest('hex');
const posixRelative = file => path.relative(ROOT, file).split(path.sep).join('/');
const fixedSources = [
  'docs/FULL_GAME_ART_CONTRACT.md', 'runtime/art-preview.html', 'runtime/art-preview.js',
  'runtime/art-preview.css', 'runtime/state-art.css', 'runtime/state-art.mjs',
  'runtime/table-art.mjs', 'runtime/screens.json', 'runtime/state-art.json',
  'runtime/copy.zh-CN.json', 'assets/game/manifest.json', 'assets/game/runtime-index.json',
  'assets/animations/characters/player.mjs', 'assets/animations/characters/manifest.json',
  'assets/characters/daotong/character.json', 'assets/characters/taohua/character.json',
  'assets/characters/hulu/character.json', 'assets/fx/manifest.json', 'tools/browser_art_audit.cjs',
];
async function sourceEvidence() {
  return Promise.all(fixedSources.map(async file => {
    const bytes = await fs.readFile(insideProject(file));
    return { file, bytes: bytes.length, sha256: sha256(bytes) };
  }));
}
async function writeJson(file, data) {
  insideProject(file);
  await fs.writeFile(file, JSON.stringify(data, null, 2) + '\n', 'utf8');
}

async function main() {
  const opts = options(process.argv.slice(2));
  const out = await ensureLocalDirectory(opts.output);
  const base = new URL(opts.baseUrl);
  if (!['127.0.0.1', 'localhost', '[::1]'].includes(base.hostname) || base.protocol !== 'http:') {
    throw new Error('Only a local HTTP project preview is permitted');
  }
  const aspects = opts.aspects.split(',');
  if (aspects.some(a => !['wide', 'standard'].includes(a))) throw new Error('Aspect must be wide or standard');
  const screenManifest = JSON.parse(await fs.readFile(insideProject('runtime/screens.json'), 'utf8'));
  const stateManifest = JSON.parse(await fs.readFile(insideProject('runtime/state-art.json'), 'utf8'));
  const requested = opts.screens ? new Set(opts.screens.split(',')) : null;
  const screens = screenManifest.screens.filter(s => !requested || requested.has(s.id));
  if (!screens.length || (requested && screens.length !== requested.size)) throw new Error('Unknown or empty screen selection');
  const initialSources = await sourceEvidence();
  const playwrightPath = process.env.AUDIT_PLAYWRIGHT_PATH || defaults.playwright;
  const chromePath = process.env.AUDIT_CHROME_PATH || defaults.chrome;
  const { chromium } = require(playwrightPath);
  const browser = await chromium.launch({ executablePath: chromePath, headless: true, args: ['--disable-background-networking'] });
  const report = {
    schemaVersion: 1, startedAt: new Date().toISOString(), projectRoot: ROOT,
    entry: new URL('runtime/art-preview.html', base.href.endsWith('/') ? base : base.href + '/').href,
    method: 'Headless Chrome executing the real local preview, native DOM change/click events, visible image decode, real stage PNG capture. Animations remain enabled.',
    claim: 'Capture and browser diagnostics only. Screenshot count and absence of runtime errors do not establish visual approval or target-client acceptance.',
    browser: { version: browser.version(), executable: chromePath, playwrightPath, headless: true },
    environment: { node: process.version, platform: os.platform(), release: os.release(), viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1, locale: 'zh-CN', timezoneId: 'America/New_York' },
    scope: { screens: screens.length, states: screens.reduce((n, s) => n + s.states.length, 0), aspects },
    sourceEvidence: initialSources, captures: [], errors: [], pageErrors: [], httpErrors: [], requestFailures: [], blockedExternalRequests: [],
    humanVisualApproval: false, targetClientVerified: false,
  };
  const context = await browser.newContext({ viewport: report.environment.viewport, deviceScaleFactor: 1, locale: 'zh-CN', timezoneId: 'America/New_York', reducedMotion: 'no-preference' });
  let activeCondition = 'initial-load';
  let page;
  await context.route('**/*', async route => {
    const requestUrl = new URL(route.request().url());
    if (['data:', 'blob:'].includes(requestUrl.protocol) || requestUrl.origin === base.origin) return route.continue();
    report.blockedExternalRequests.push({ condition: activeCondition, url: requestUrl.href });
    return route.abort('blockedbyclient');
  });
  try {
    page = await context.newPage();
    page.on('pageerror', error => report.pageErrors.push({ condition: activeCondition, message: String(error), stack: error.stack }));
    page.on('response', response => { if (response.status() >= 400) report.httpErrors.push({ condition: activeCondition, url: response.url(), status: response.status() }); });
    page.on('requestfailed', request => report.requestFailures.push({ condition: activeCondition, url: request.url(), error: request.failure()?.errorText }));
    const response = await page.goto(report.entry, { waitUntil: 'networkidle', timeout: 30000 });
    if (!response?.ok()) throw new Error('Preview entry did not return success');
    const servedSource = await response.body();
    if (sha256(servedSource) !== initialSources.find(x => x.file === 'runtime/art-preview.html').sha256) {
      throw new Error('Local service is not serving this project entry bytes');
    }
    await page.waitForFunction(() => window.ART_PREVIEW?.screenCount === 60 && document.querySelector('#pages [data-page]'), undefined, { timeout: 30000 });
    await page.evaluate(() => document.fonts.ready);

    async function ready() {
      const notes = [];
      try {
        await page.waitForFunction(() => {
          const canvases = document.querySelectorAll('#canvas canvas[data-actor]');
          return !canvases.length || Boolean(window.ART_PREVIEW.actorPlayer());
        }, undefined, { timeout: 15000 });
      } catch (error) { notes.push({ kind: 'actor-readiness-timeout', error: String(error) }); }
      const decoded = await page.evaluate(async () => {
        const visible = el => { const r = el.getBoundingClientRect(), s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.display !== 'none' && s.visibility !== 'hidden'; };
        const imgs = [...document.querySelectorAll('#stage img')].filter(visible);
        const imageResults = await Promise.all(imgs.map(async el => {
          try { await el.decode(); return { url: el.currentSrc || el.src, loaded: el.naturalWidth > 0, width: el.naturalWidth, height: el.naturalHeight }; }
          catch (error) { return { url: el.currentSrc || el.src, loaded: false, error: String(error) }; }
        }));
        const cssUrls = new Set();
        for (const el of document.querySelectorAll('#stage, #stage *')) {
          if (!visible(el)) continue;
          const s = getComputedStyle(el);
          for (const value of [s.backgroundImage, s.borderImageSource]) {
            for (const match of value.matchAll(/url\(["']?(.*?)["']?\)/g)) cssUrls.add(match[1]);
          }
        }
        const cssResults = await Promise.all([...cssUrls].map(async url => {
          const im = new Image(); im.src = url;
          try { await im.decode(); return { url, loaded: im.naturalWidth > 0, width: im.naturalWidth, height: im.naturalHeight }; }
          catch (error) { return { url, loaded: false, error: String(error) }; }
        }));
        await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        return { visibleImages: imageResults.length, cssImages: cssResults.length, brokenImages: imageResults.filter(x => !x.loaded), brokenCssImages: cssResults.filter(x => !x.loaded) };
      });
      return { notes, ...decoded };
    }
    async function capture(screen, stateIndex, aspect) {
      const stateInfo = stateIndex === null ? null : stateManifest.states.find(s => s.screen === screen.id && s.index === stateIndex);
      const stem = `${screen.id}--${stateIndex === null ? 'base' : 'state-' + String(stateIndex).padStart(2, '0')}--${aspect}`;
      activeCondition = stem;
      const readiness = await ready();
      const diagnostic = await page.evaluate(() => {
        const stage = document.querySelector('#stage'), sr = stage.getBoundingClientRect();
        const box = el => { const r = el.getBoundingClientRect(); return { x: +(r.left - sr.left).toFixed(2), y: +(r.top - sr.top).toFixed(2), width: +r.width.toFixed(2), height: +r.height.toFixed(2) }; };
        const visible = el => { const r = el.getBoundingClientRect(), s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.display !== 'none' && s.visibility !== 'hidden'; };
        const panels = [...stage.querySelectorAll('.panel,.grid,.rows,.state-focus,.state-result,.state-inline,.state-table-note,.panel>div[style*="display:grid"]')].filter(visible).map(el => {
          const r = el.getBoundingClientRect(), css = getComputedStyle(el);
          const ancestorClips = [];
          for (let parent = el.parentElement; parent && stage.contains(parent); parent = parent.parentElement) {
            const s = getComputedStyle(parent), pr = parent.getBoundingClientRect();
            const clipX = s.overflowX !== 'visible', clipY = s.overflowY !== 'visible';
            if (!clipX && !clipY) continue;
            const left = pr.left + parent.clientLeft, top = pr.top + parent.clientTop;
            const clipped = { left: clipX ? Math.max(0, left - r.left) : 0, top: clipY ? Math.max(0, top - r.top) : 0, right: clipX ? Math.max(0, r.right - left - parent.clientWidth) : 0, bottom: clipY ? Math.max(0, r.bottom - top - parent.clientHeight) : 0 };
            if (Object.values(clipped).some(n => n > 1)) ancestorClips.push({ ancestor: parent.id ? '#' + parent.id : parent.tagName.toLowerCase() + (parent.className ? '.' + String(parent.className).trim().split(/\s+/).join('.') : ''), overflowX: s.overflowX, overflowY: s.overflowY, clipped: Object.fromEntries(Object.entries(clipped).map(([k, v]) => [k, +v.toFixed(2)])) });
          }
          return { selector: el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).trim().split(/\s+/).join('.') : ''), ...box(el), clientWidth: el.clientWidth, clientHeight: el.clientHeight, scrollWidth: el.scrollWidth, scrollHeight: el.scrollHeight, scrollLeft: el.scrollLeft, scrollTop: el.scrollTop, overflowX: css.overflowX, overflowY: css.overflowY, outsideStage: { left: +(Math.max(0, sr.left - r.left)).toFixed(2), top: +(Math.max(0, sr.top - r.top)).toFixed(2), right: +(Math.max(0, r.right - sr.right)).toFixed(2), bottom: +(Math.max(0, r.bottom - sr.bottom)).toFixed(2) }, ancestorClips, childCount: el.children.length };
        });
        return { stage: { width: +sr.width.toFixed(2), height: +sr.height.toFixed(2), className: stage.className }, panels, panelDiagnosticsOnly: true, currentPage: window.ART_PREVIEW.page(), currentStateValue: document.querySelector('#state').value, stateArtId: document.querySelector('[data-state-art]')?.dataset.stateArt || null, actor: window.ART_PREVIEW.actorPlayer()?.actor || null, skin: window.ART_PREVIEW.actorPlayer()?.skin || null, fontStatus: document.fonts.status, fontFamily: getComputedStyle(stage).fontFamily, activeAnimations: stage.getAnimations({ subtree: true }).map(a => ({ playState: a.playState, currentTime: a.currentTime, animationName: a.animationName || null })) };
      });
      const screenshotFile = path.join(out, 'screenshots', stem + '.png');
      const bytes = await page.locator('#stage').screenshot({ path: screenshotFile, type: 'png', animations: 'allow', timeout: 30000 });
      const item = { condition: stem, capturedAt: new Date().toISOString(), screen: screen.id, title: screen.title, template: screen.template, aspect, kind: stateIndex === null ? 'base-screen' : 'state', state: stateInfo ? { index: stateIndex, id: stateInfo.id, name: stateInfo.name, layout: stateInfo.layout } : null, ...readiness, diagnostic, screenshot: { file: posixRelative(screenshotFile), bytes: bytes.length, sha256: sha256(bytes), animations: 'allow' }, visualApproval: 'pending_manual_review' };
      if (diagnostic.currentPage !== screen.id || (stateInfo && diagnostic.stateArtId !== stateInfo.id)) item.conditionMismatch = true;
      await writeJson(path.join(out, 'conditions', stem + '.json'), item);
      report.captures.push(item);
      const expected = aspects.length * screens.reduce((n, s) => n + 1 + s.states.length, 0);
      console.log(JSON.stringify({ progress: report.captures.length, total: expected, condition: stem, brokenImages: item.brokenImages.length + item.brokenCssImages.length, readinessNotes: item.notes.length, conditionMismatch: Boolean(item.conditionMismatch) }));
    }

    await ensureLocalDirectory(path.join(out, 'screenshots'));
    await ensureLocalDirectory(path.join(out, 'conditions'));
    for (const aspect of aspects) {
      await page.evaluate(value => { const select = document.querySelector('#aspect'); select.value = value; select.dispatchEvent(new Event('change', { bubbles: true })); }, aspect);
      for (const screen of screens) {
        activeCondition = `${screen.id}--navigate--${aspect}`;
        await page.evaluate(id => { const button = document.querySelector(`[data-page="${id}"]`); if (!button) throw new Error('Missing page button ' + id); button.click(); }, screen.id);
        await capture(screen, null, aspect);
        for (let stateIndex = 0; stateIndex < screen.states.length; stateIndex++) {
          activeCondition = `${screen.id}--state-${stateIndex}--${aspect}`;
          // Dispatch even for zero: the base screen has no state overlay despite select.value already being "0".
          await page.evaluate(index => { const select = document.querySelector('#state'); select.value = String(index); select.dispatchEvent(new Event('change', { bubbles: true })); }, stateIndex);
          await capture(screen, stateIndex, aspect);
        }
      }
    }
  } catch (error) {
    report.errors.push({ condition: activeCondition, message: String(error), stack: error.stack });
    process.exitCode = 1;
  } finally {
    const finalSources = await sourceEvidence();
    report.sourceEvidenceAfter = finalSources;
    report.sourceFilesChangedDuringRun = finalSources.filter(x => x.sha256 !== initialSources.find(y => y.file === x.file)?.sha256).map(x => x.file);
    report.finishedAt = new Date().toISOString();
    report.summary = { captureCount: report.captures.length, brokenImageConditions: report.captures.filter(x => x.brokenImages.length || x.brokenCssImages.length).length, readinessIssueConditions: report.captures.filter(x => x.notes.length).length, conditionMismatches: report.captures.filter(x => x.conditionMismatch).length, pageErrors: report.pageErrors.length, httpErrors: report.httpErrors.length, requestFailures: report.requestFailures.length, sourceChanged: report.sourceFilesChangedDuringRun.length > 0 };
    report.status = report.errors.length || report.summary.brokenImageConditions || report.summary.readinessIssueConditions || report.summary.conditionMismatches || report.pageErrors.length || report.httpErrors.length || report.requestFailures.length || report.blockedExternalRequests.length || report.sourceFilesChangedDuringRun.length ? 'browser_diagnostics_found_issues' : 'captured_pending_visual_review';
    await writeJson(path.join(out, 'report.json'), report);
    await browser.close();
    console.log(JSON.stringify({ completed: true, status: report.status, ...report.summary, report: posixRelative(path.join(out, 'report.json')) }));
    if (report.status === 'browser_diagnostics_found_issues') process.exitCode = 1;
  }
}
main().catch(error => { console.error(error.stack || String(error)); process.exitCode = 1; });
