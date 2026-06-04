#!/usr/bin/env node
/**
 * deploy-from-table.js
 *
 * 从「按行枚举」格式的活动上线表读取排期，调用 iGame API 部署。
 *
 * 表头 (X2-占星节模板)：
 *   A 批次标识 (灰度服活动任务批次 / 正式服活动任务批次 / 无)
 *   B 部署日期 YYYY-MM-DD
 *   C configId  iGame 配置 ID
 *   D 活动名称
 *   E 跨服 0=单服 1=跨服
 *   F 开始时间 YYYY-MM-DD [HH:mm] UTC  (仅日期默认 00:00)
 *   G 结束时间 YYYY-MM-DD [HH:mm] UTC  (仅日期默认 前一天 23:59:59 UTC)
 *   H 结束展示截止 YYYY-MM-DD [HH:mm] 北京  (空 / "无" = 不延展)
 *   I 持续时间 H  (展示用，不强校验)
 *   J 服务器模式 schema | list | all
 *   K 服务器值   JSON 数组 / 逗号分隔 / schema 字符串
 *   L 排除服     可选 JSON 或逗号
 *   M 同步审核服 NO | YES (YES = 提前 1 天发审核服)
 *   N 备注       含「跨服排行」→ acrossServerRank=1
 *   O 状态       脚本回写
 *   P iGame ID   脚本回写
 *   Q 部署时间   脚本回写
 *   R 错误信息   脚本回写
 *
 * 用法：
 *   node deploy-from-table.js --sheet <id> --tab <name> --list
 *   node deploy-from-table.js --sheet <id> --tab <name> --deploy 2 --dry-run
 *   node deploy-from-table.js --sheet <id> --tab <name> --deploy 2-8
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const HOME = process.env.HOME || process.env.USERPROFILE;
const IGAME_QUERY = path.join(HOME, '.claude', 'skills', 'igame-skill', 'scripts', 'igame-query.js');

// ─── args ───
function parseArgs() {
  const a = process.argv.slice(2);
  const o = { list: false, dryRun: false };
  for (let i = 0; i < a.length; i++) {
    switch (a[i]) {
      case '--sheet': o.sheetId = a[++i]; break;
      case '--tab': o.tabName = a[++i]; break;
      case '--list': o.list = true; break;
      case '--deploy': o.deploy = a[++i]; break;
      case '--dry-run': o.dryRun = true; break;
      default: console.error('未知参数:', a[i]); process.exit(1);
    }
  }
  if (!o.sheetId || !o.tabName) {
    console.error('必须指定 --sheet 和 --tab');
    process.exit(1);
  }
  return o;
}

function expandIndices(str) {
  const out = new Set();
  for (const p of str.split(',')) {
    const t = p.trim();
    if (t.includes('-')) {
      const [s, e] = t.split('-').map(Number);
      for (let i = s; i <= e; i++) out.add(i);
    } else out.add(Number(t));
  }
  return [...out].sort((x, y) => x - y);
}

// ─── gws helpers ───
function gwsGet(params) {
  const json = JSON.stringify(params);
  const r = execSync(`gws sheets spreadsheets get --params ${JSON.stringify(json)}`, { encoding: 'utf-8', maxBuffer: 50*1024*1024 });
  return JSON.parse(r);
}

function readRange(sheetId, tabName, range) {
  const r = gwsGet({ spreadsheetId: sheetId, ranges: `'${tabName}'!${range}`, includeGridData: true,
    fields: 'sheets.data.rowData.values.formattedValue' });
  const rows = r.sheets[0].data[0].rowData || [];
  return rows.map(row => (row.values || []).map(c => (c.formattedValue || '').toString()));
}

// ─── time ───
function parseUtc(s, isEnd) {
  // accepts "YYYY-MM-DD" or "YYYY-MM-DD HH:mm" as UTC
  const m = s.trim().match(/^(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T](\d{1,2}):(\d{1,2}))?$/);
  if (!m) throw new Error(`时间格式不对: "${s}"`);
  const y = +m[1], mo = +m[2]-1, d = +m[3];
  if (m[4] !== undefined) return Date.UTC(y, mo, d, +m[4], +m[5], 0);
  if (isEnd) {
    // 仅写日期 → 前一天 23:59:59 UTC
    return Date.UTC(y, mo, d-1, 23, 59, 59);
  }
  return Date.UTC(y, mo, d, 0, 0, 0);
}

function parseBjShow(s) {
  // 结束展示截止 北京时间 → UTC 时间戳（减 8h）。空 / "无" → 0
  if (!s) return 0;
  const t = s.trim();
  if (!t || t === '无' || t.toUpperCase() === 'N/A') return 0;
  const m = t.match(/^(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T](\d{1,2}):(\d{1,2}))?$/);
  if (!m) throw new Error(`结束展示截止格式不对: "${s}"`);
  const y = +m[1], mo = +m[2]-1, d = +m[3];
  const hh = m[4] === undefined ? 0 : +m[4];
  const mm = m[4] === undefined ? 0 : +m[5];
  // 北京 = UTC+8，转 UTC ts
  return Date.UTC(y, mo, d, hh-8, mm, 0);
}

function fmtUtc(ts) {
  if (!ts) return '0';
  const d = new Date(ts);
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth()+1).padStart(2,'0')}-${String(d.getUTCDate()).padStart(2,'0')} ${String(d.getUTCHours()).padStart(2,'0')}:${String(d.getUTCMinutes()).padStart(2,'0')}:${String(d.getUTCSeconds()).padStart(2,'0')} UTC`;
}

// ─── parse server cell ───
function parseList(s) {
  if (!s) return [];
  const t = s.trim();
  if (!t) return [];
  if (t.startsWith('[')) return JSON.parse(t);
  return t.split(/[,;]\s*/).filter(Boolean).map(x => +x);
}

// ─── row → activity ───
function parseRows(rows) {
  // 找列头位置
  const out = [];
  let inFormal = false; // 进入「正式服活动任务批次」段
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    const a = (row[0] || '').trim();
    if (a === '灰度服活动任务批次' || a === '正式服活动任务批次') {
      inFormal = (a === '正式服活动任务批次');
      continue;
    }
    if (a.startsWith('必填 ·')) continue;   // 说明行
    if (a === '无' || !a) continue;
    if (!inFormal) continue;                 // 暂时跳过灰度段（"无"已经过滤）
    // 数据行
    const cfg = (row[2] || '').trim();
    if (!/^\d+$/.test(cfg)) continue;
    out.push({
      rowIndex: i + 1, // 1-based for sheet
      batch: a,
      deployDate: (row[1] || '').trim(),
      configId: cfg,
      name: (row[3] || '').trim(),
      acrossServer: +((row[4] || '0').trim()),
      startStr: (row[5] || '').trim(),
      endStr: (row[6] || '').trim(),
      showEndStr: (row[7] || '').trim(),
      durationH: (row[8] || '').trim(),
      mode: (row[9] || '').trim().toLowerCase(),
      serverVal: (row[10] || '').trim(),
      excludeVal: (row[11] || '').trim(),
      auditSync: ((row[12] || 'NO').trim().toUpperCase() === 'YES'),
      notes: (row[13] || '').trim(),
    });
  }
  return out;
}

// ─── server list 解析 ───
function buildServers(act) {
  const exclude = new Set(parseList(act.excludeVal));
  let servers;
  if (act.mode === 'list') {
    servers = parseList(act.serverVal).filter(s => !exclude.has(s));
  } else if (act.mode === 'all') {
    throw new Error(`mode=all 暂未实现，请改用 list（"${act.name}" 行${act.rowIndex}）`);
  } else if (act.mode === 'schema') {
    throw new Error(`mode=schema 暂未实现，请改用 list（"${act.name}" 行${act.rowIndex}）`);
  } else {
    throw new Error(`未知 mode="${act.mode}"（"${act.name}" 行${act.rowIndex}）`);
  }
  if (servers.length === 0) throw new Error(`空服务器列表（"${act.name}" 行${act.rowIndex}）`);

  // 单服 acrossServer=0 / 跨服全服 acrossServer=1 → 一组
  return [servers];
}

function buildPayload(act) {
  const startTime = parseUtc(act.startStr, false);
  const endTime = parseUtc(act.endStr, true);
  const endShowTime = parseBjShow(act.showEndStr); // 0 = 不延展
  const servers = buildServers(act);
  const acrossServerRank = act.notes.includes('跨服排行') ? 1 : 0;
  if (act.acrossServer === 0 && acrossServerRank === 1) {
    throw new Error(`单服活动不能 acrossServerRank=1（"${act.name}" 行${act.rowIndex}，备注=${act.notes}）`);
  }
  return {
    activityConfigId: act.configId,
    name: act.name,
    startTime,
    endTime,
    previewTime: 0,
    endShowTime: endShowTime || 0,
    acrossServer: act.acrossServer,
    acrossServerRank,
    servers,
  };
}

// ─── iGame ───
function igameWrite(apiPath, body) {
  const cmd = `node "${IGAME_QUERY}" write "${apiPath}" ${JSON.stringify(JSON.stringify(body))}`;
  const r = execSync(cmd, { encoding: 'utf-8' });
  return JSON.parse(r);
}

// ─── output helpers ───
function printActivities(acts) {
  console.log(`\n共 ${acts.length} 条活动（正式服批次）：\n`);
  for (let i = 0; i < acts.length; i++) {
    const a = acts[i];
    const acrossLabel = a.acrossServer ? (a.notes.includes('跨服排行') ? '跨服+排行' : '跨服') : '单服';
    const auditLabel = a.auditSync ? ' [审核服:YES]' : '';
    let serverCount = '?';
    try { serverCount = parseList(a.serverVal).length; } catch {}
    console.log(`#${i+1} ${a.name} (configId=${a.configId})`);
    console.log(`     ${a.startStr} ~ ${a.endStr}  [${acrossLabel}]${auditLabel}  ${a.mode}:${serverCount}服`);
    if (a.notes) console.log(`     备注: ${a.notes}`);
  }
  console.log('');
}

// ─── main ───
function main() {
  const opts = parseArgs();
  if (!fs.existsSync(IGAME_QUERY)) {
    console.error('igame-skill 未安装：', IGAME_QUERY);
    process.exit(1);
  }

  console.log(`读取活动表: ${opts.tabName}`);
  const rows = readRange(opts.sheetId, opts.tabName, 'A1:R200');
  const acts = parseRows(rows);
  if (acts.length === 0) {
    console.error('没有解析到任何活动行（请检查表头与正式服批次段）');
    process.exit(1);
  }

  if (opts.list) {
    printActivities(acts);
    return;
  }
  if (!opts.deploy) {
    console.error('未指定 --deploy <indices>（如 "2" 或 "2-8"）');
    process.exit(1);
  }

  const indices = expandIndices(opts.deploy);
  console.log(`\n[模式] ${opts.dryRun ? 'DRY-RUN（仅预览）' : '实际提交'}`);
  for (const idx of indices) {
    const a = acts[idx-1];
    if (!a) { console.error(`#${idx} 不存在，跳过`); continue; }
    console.log(`\n=== #${idx} ${a.name} (configId=${a.configId}) ===`);
    let payload;
    try {
      payload = buildPayload(a);
    } catch (e) {
      console.error('   ✗ 构造 payload 失败:', e.message);
      continue;
    }
    console.log(`   配置ID: ${payload.activityConfigId}`);
    console.log(`   起止 (UTC): ${fmtUtc(payload.startTime)} ~ ${fmtUtc(payload.endTime)}`);
    console.log(`   跨服: acrossServer=${payload.acrossServer}  acrossServerRank=${payload.acrossServerRank}`);
    console.log(`   分组数: ${payload.servers.length}    服务器总数: ${payload.servers.flat().length}`);
    console.log(`   endShowTime: ${payload.endShowTime || '0 (不延展)'}`);
    if (opts.dryRun) continue;
    try {
      const resp = igameWrite('activity/add_activity/submitActivity', [payload]);
      if (resp && resp.success) {
        const ids = (resp.data || []).map(x => x.id).join(',');
        console.log(`   ✓ 已提交，iGame id=${ids}`);
      } else {
        console.error(`   ✗ 提交失败: ${JSON.stringify(resp).substring(0,500)}`);
      }
    } catch (e) {
      console.error('   ✗ 请求异常:', e.message);
    }
  }
}

main();
