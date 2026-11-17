#!/usr/bin/env node
// Stage 1: candidate discovery.
// Drives a headless Chromium (Playwright) through GitHub's public repository
// search with a fixed list of queries, records every result in search order,
// and checks whether each repository has a Dockerfile at its root.
// Output: data/candidates_raw.json
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');

const SINCE = '2025-11-17';            // "pushed within the last 12 months"
const STARS = '15..400';               // real projects, but not famous ones
const PAGES = 3;                       // result pages taken per query
const BASE = `stars:${STARS} pushed:>${SINCE} archived:false fork:false`;
// group -> list of fixed queries (framework topics that imply a runnable service)
const QUERIES = {
  python: ['topic:fastapi language:Python', 'topic:flask language:Python', 'topic:django language:Python', 'topic:telegram-bot language:Python'],
  node:   ['topic:express language:TypeScript', 'topic:nestjs language:TypeScript', 'topic:express language:JavaScript', 'topic:discord-bot language:TypeScript'],
  go:     ['topic:gin language:Go', 'topic:self-hosted language:Go', 'topic:rest-api language:Go'],
  java:   ['topic:spring-boot language:Java', 'topic:spring-boot language:Kotlin'],
  ruby:   ['topic:rails language:Ruby', 'topic:sinatra language:Ruby'],
  php:    ['topic:laravel language:PHP', 'topic:symfony language:PHP'],
  rust:   ['topic:axum language:Rust', 'topic:actix-web language:Rust'],
};
const sleep = ms => new Promise(r => setTimeout(r, ms));

function rootDockerfile(fullName) {
  try {
    const code = execFileSync('curl', ['-sS', '-o', '/dev/null', '-m', '20', '-w', '%{http_code}',
      `https://raw.githubusercontent.com/${fullName}/HEAD/Dockerfile`], { encoding: 'utf8' });
    return code.trim() === '200';
  } catch (e) { return false; }
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const seen = new Set();
  const out = [];
  for (const [group, queries] of Object.entries(QUERIES)) {
    for (const q of queries) {
      for (let p = 1; p <= PAGES; p++) {
        const full = `${q} ${BASE}`;
        const url = `https://github.com/search?q=${encodeURIComponent(full)}&type=repositories&p=${p}`;
        let results = [];
        for (let attempt = 0; attempt < 3; attempt++) {
          try {
            const resp = await page.goto(url, { timeout: 45000, waitUntil: 'domcontentloaded' });
            if (resp.status() === 429) { await sleep(60000); continue; }
            const raw = await page.evaluate(() => {
              const s = document.querySelector('script[data-target="react-app.embeddedData"]');
              return s ? s.textContent : null;
            });
            results = JSON.parse(raw).payload.blackbirdSearchRoute.results || [];
            break;
          } catch (e) { await sleep(15000); }
        }
        console.error(`[${group}] "${q}" p${p}: ${results.length} results`);
        results.forEach((r, i) => {
          const name = r.hl_name.replace(/<\/?em>/g, '');
          if (seen.has(name)) return;
          seen.add(name);
          out.push({
            full_name: name, group, query: q, page: p, rank: i + 1,
            stars: r.followers, language: r.language,
            description: (r.hl_trunc_description || '').replace(/<\/?em>/g, ''),
            topics: r.topics || [], updated_at: r.repo.repository.updated_at,
          });
        });
        await sleep(5000);
      }
    }
  }
  await browser.close();
  for (const c of out) { c.root_dockerfile = rootDockerfile(c.full_name); }
  fs.writeFileSync('data/candidates_raw.json', JSON.stringify({
    generated: new Date().toISOString(), since: SINCE, stars: STARS, pages_per_query: PAGES,
    queries: QUERIES, candidates: out }, null, 1));
  const by = {};
  out.forEach(c => { by[c.group] = by[c.group] || [0, 0]; by[c.group][0]++; if (c.root_dockerfile) by[c.group][1]++; });
  console.error('group: [found, with root Dockerfile]', JSON.stringify(by));
})();
