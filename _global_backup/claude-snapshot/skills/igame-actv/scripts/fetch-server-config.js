#!/usr/bin/env node
/**
 * fetch-server-config.js
 *
 * 从 yych-tools API 拉取服务器分组数据，生成 server-config.json。
 *
 * 用法:
 *   node fetch-server-config.js <share_id>
 *   node fetch-server-config.js y6m1kl
 */

const fs = require('fs');
const path = require('path');

const API_BASE = 'https://yych-tools-api.anasta0910.workers.dev/load';
const OUT_FILE = path.resolve(__dirname, '..', 'server-config.json');

async function main() {
  const shareId = process.argv[2];
  if (!shareId) {
    console.error('用法: node fetch-server-config.js <share_id>');
    console.error('例:   node fetch-server-config.js y6m1kl');
    process.exit(1);
  }

  console.log(`拉取数据: ${API_BASE}/${shareId}`);
  const resp = await fetch(`${API_BASE}/${shareId}`);
  if (!resp.ok) {
    console.error(`请求失败: ${resp.status} ${resp.statusText}`);
    process.exit(1);
  }
  const json = await resp.json();

  // Parse server data
  const lines = json.data.split('\n').slice(1);
  const schema = {};
  const gray = [];
  for (const l of lines) {
    const [s, sch, g] = l.split('\t');
    if (!schema[sch]) schema[sch] = [];
    schema[sch].push(s);
    if (g === '1') gray.push(s);
  }

  // Parse cross-server groups
  const crossLines = json.crossData.split('\n').slice(1);
  const crossGroups = {};
  for (const l of crossLines) {
    const idx = l.indexOf('\t');
    const sch = l.substring(0, idx);
    const grp = l.substring(idx + 1);
    if (!crossGroups[sch]) crossGroups[sch] = [];
    crossGroups[sch].push(JSON.parse(grp).map(String));
  }

  fs.writeFileSync(OUT_FILE, JSON.stringify({ schema, gray, crossGroups }, null, 2));

  // Print summary
  console.log(`\n写入: ${OUT_FILE}`);
  console.log(`名称: ${json.name || '(无)'}`);
  for (const k of Object.keys(schema)) {
    console.log(`  schema${k}: ${schema[k].length} 个服务器`);
  }
  console.log(`  灰度: ${gray.length} 个服务器`);
  for (const k of Object.keys(crossGroups)) {
    console.log(`  跨服分组 ${k}: ${crossGroups[k].length} 组`);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
