// Parse __NUXT__ payload from fifaaddict SSR pages -> el_stats.json
const fs = require('fs');
const path = require('path');
const dir = path.join(__dirname, 'elpages');
const out = {};
for (const f of fs.readdirSync(dir)) {
  if (!f.endsWith('.html')) continue;
  const t = fs.readFileSync(path.join(dir, f), 'utf8');
  const i = t.indexOf('window.__NUXT__=');
  if (i < 0) { console.error('no nuxt', f); continue; }
  const end = t.indexOf('</script>', i);
  let expr = t.slice(i + 'window.__NUXT__='.length, end);
  expr = expr.replace(/;\s*$/, '');
  let nuxt;
  try { nuxt = eval('(' + expr + ')'); } catch (e) { console.error('eval fail', f, e.message); continue; }
  const d = nuxt.data && nuxt.data[0];
  if (!d || !d.foPlayerSSRdb) { console.error('no db', f); continue; }
  const uid = f.replace('.html', '');
  out[uid] = {
    player: d.foPlayerSSRdb,
    traits: d.foTraitsSSR || null,
    price: d.foPriceSSR || null,
  };
}
fs.writeFileSync(path.join(__dirname, 'el_stats.json'), JSON.stringify(out));
console.log('parsed', Object.keys(out).length);
