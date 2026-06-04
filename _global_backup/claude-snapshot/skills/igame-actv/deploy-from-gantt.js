#!/usr/bin/env node
/**
 * deploy-from-gantt.js
 *
 * 从 Google Sheet 甘特图读取活动排期，通过 iGame API 部署活动。
 *
 * 前置依赖:
 *   - gws CLI (npm i -g @anthropic-ai/gws)
 *   - igame-skill (~/.claude/skills/igame-skill)
 *   - 认证文件 ~/.igame-auth.json
 *
 * 用法:
 *   node deploy-from-gantt.js --sheet <spreadsheet_id> --tab <sheet_name> --list
 *   node deploy-from-gantt.js --sheet <spreadsheet_id> --tab <sheet_name> --deploy 1,3,5-8
 *   node deploy-from-gantt.js --sheet <spreadsheet_id> --tab <sheet_name> --deploy 1,3,5-8 --dry-run
 *
 * 参数:
 *   --sheet <id>        Google Spreadsheet ID
 *   --tab <name>        页签名称
 *   --list              列出甘特图中所有活动及排期
 *   --deploy <indices>  按序号部署活动（如 "1,3,5-8"）
 *   --dry-run           仅预览，不实际部署
 *   --servers <json>    覆盖服务器列表（JSON数组）
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

// ─── Config ───
const HOME = process.env.HOME || process.env.USERPROFILE;
const IGAME_SKILL = path.join(HOME, '.claude', 'skills', 'igame-skill');
const IGAME_QUERY = path.join(IGAME_SKILL, 'scripts', 'igame-query.js');
const SERVER_CONFIG_FILE = path.resolve(__dirname, 'server-config.json');

// ─── Prerequisite checks ───
function checkPrerequisites() {
  const errors = [];
  try { execSync('which gws', { encoding: 'utf-8', stdio: 'pipe' }); }
  catch { errors.push('gws CLI 未安装。请运行: npm i -g @anthropic-ai/gws'); }

  if (!fs.existsSync(IGAME_QUERY)) {
    errors.push(`igame-skill 未安装。需要: ${IGAME_SKILL}`);
  }

  const authFile = path.join(HOME, '.igame-auth.json');
  if (!fs.existsSync(authFile)) {
    errors.push(`认证文件不存在: ${authFile}\n  请运行: bash ${IGAME_SKILL}/scripts/setup-auth.sh`);
  }

  if (errors.length > 0) {
    console.error('前置依赖检查失败:\n');
    for (const e of errors) console.error('  ✗ ' + e);
    console.error('');
    process.exit(1);
  }
}

// ─── Server config ───
let _serverConfig = null;
function loadServerConfig() {
  if (_serverConfig) return _serverConfig;
  if (!fs.existsSync(SERVER_CONFIG_FILE)) {
    console.error('服务器配置文件不存在:', SERVER_CONFIG_FILE);
    console.error('请运行: node scripts/fetch-server-config.js <share_id>');
    process.exit(1);
  }
  _serverConfig = JSON.parse(fs.readFileSync(SERVER_CONFIG_FILE, 'utf-8'));
  return _serverConfig;
}

// ─── Google Sheets ───
function gwsSheets(paramsObj) {
  const paramsJson = JSON.stringify(paramsObj);
  const result = execSync(`gws sheets spreadsheets get --params ${JSON.stringify(paramsJson)}`, {
    encoding: 'utf-8',
    maxBuffer: 10 * 1024 * 1024,
  });
  return JSON.parse(result);
}

// ─── Helpers ───

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { list: false, dryRun: false };
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--sheet': opts.sheetId = args[++i]; break;
      case '--tab': opts.tabName = args[++i]; break;
      case '--list': opts.list = true; break;
      case '--deploy': opts.deployIndices = args[++i]; break;
      case '--dry-run': opts.dryRun = true; break;
      case '--servers': opts.servers = JSON.parse(args[++i]); break;
      default:
        console.error('未知参数:', args[i]);
        process.exit(1);
    }
  }
  if (!opts.sheetId || !opts.tabName) {
    console.error('必须指定 --sheet 和 --tab');
    console.error('用法: node deploy-from-gantt.js --sheet <id> --tab <name> --list');
    process.exit(1);
  }
  return opts;
}

function parseIndexRange(str) {
  const indices = new Set();
  for (const part of str.split(',')) {
    const trimmed = part.trim();
    if (trimmed.includes('-')) {
      const [a, b] = trimmed.split('-').map(Number);
      for (let i = a; i <= b; i++) indices.add(i);
    } else {
      indices.add(Number(trimmed));
    }
  }
  return [...indices].sort((a, b) => a - b);
}

// ─── Gantt parser ───

function readGanttFromSheet(sheetId, tabName) {
  const metaRaw = gwsSheets({ spreadsheetId: sheetId, includeGridData: false });
  const sheet = metaRaw.sheets.find(s => s.properties.title === tabName);
  if (!sheet) {
    console.error(`页签 "${tabName}" 不存在。可用页签:`);
    for (const s of metaRaw.sheets) console.error(`  - ${s.properties.title}`);
    process.exit(1);
  }

  const headerRange = `'${tabName}'!A1:AQ10`;
  const headerData = gwsSheets({
    spreadsheetId: sheetId,
    ranges: headerRange,
    includeGridData: true,
    fields: 'sheets.data.rowData.values.formattedValue',
  });
  const headerRows = headerData.sheets[0].data[0].rowData || [];

  let dateRowIdx = -1;
  let dates = [];
  let dateColStart = -1;
  for (let r = 0; r < headerRows.length; r++) {
    const cells = headerRows[r].values || [];
    for (let c = 0; c < cells.length; c++) {
      const fv = cells[c].formattedValue || '';
      if (/^\d{1,2}-\d{1,2}$/.test(fv)) {
        dateRowIdx = r;
        dateColStart = c;
        for (let cc = c; cc < cells.length; cc++) {
          const d = (cells[cc].formattedValue || '').trim();
          if (/^\d{1,2}-\d{1,2}$/.test(d)) {
            dates.push(d);
          } else if (dates.length > 0) {
            break;
          }
        }
        break;
      }
    }
    if (dateRowIdx >= 0) break;
  }

  if (dateRowIdx < 0) {
    console.error('无法在前10行中找到日期行（格式如 3-12, 3-13...）');
    process.exit(1);
  }

  const activityStartRow = dateRowIdx + 2;
  const endColIdx = dateColStart + dates.length - 1;
  const endCol = endColIdx < 26
    ? String.fromCharCode(65 + endColIdx)
    : String.fromCharCode(64 + Math.floor(endColIdx / 26)) + String.fromCharCode(65 + (endColIdx % 26));

  const dataRange = `'${tabName}'!A${activityStartRow}:${endCol}80`;
  const actData = gwsSheets({
    spreadsheetId: sheetId,
    ranges: dataRange,
    includeGridData: true,
    fields: 'sheets.data.rowData.values.effectiveFormat.backgroundColor,sheets.data.rowData.values.formattedValue',
  });
  const actRows = actData.sheets[0].data[0].rowData || [];

  const activities = [];
  for (let idx = 0; idx < actRows.length; idx++) {
    const row = actRows[idx];
    const cells = row.values || [];
    const name = (cells[0] && cells[0].formattedValue) || '';
    const configId = (cells[1] && cells[1].formattedValue) || '';
    if (!name || !configId || !/^\d+$/.test(configId)) continue;

    const owner = (cells[2] && cells[2].formattedValue) || '';
    const crossType = (cells[4] && cells[4].formattedValue) || '';
    const online = (cells[5] && cells[5].formattedValue) || '';

    const segments = [];
    let curStart = null;
    let curColor = null;
    let curText = '';

    for (let j = dateColStart; j < Math.min(cells.length, dateColStart + dates.length); j++) {
      const cell = cells[j] || {};
      const bg = (cell.effectiveFormat && cell.effectiveFormat.backgroundColor) || {};
      const r = bg.red !== undefined ? bg.red : 1.0;
      const g = bg.green !== undefined ? bg.green : 1.0;
      const b = bg.blue !== undefined ? bg.blue : 1.0;
      const fv = cell.formattedValue || '';
      const isColored = !(r > 0.95 && g > 0.95 && b > 0.95);
      const colorHex = isColored ? `#${Math.round(r*255).toString(16).padStart(2,'0')}${Math.round(g*255).toString(16).padStart(2,'0')}${Math.round(b*255).toString(16).padStart(2,'0')}` : null;
      const di = j - dateColStart;

      if (isColored) {
        if (curStart === null) {
          curStart = di;
          curColor = colorHex;
          curText = fv;
        } else if (colorHex !== curColor) {
          segments.push({ start: dates[curStart], end: dates[di - 1], color: curColor, text: curText.trim() });
          curStart = di;
          curColor = colorHex;
          curText = fv;
        } else {
          if (fv) curText = curText ? curText + ' ' + fv : fv;
        }
      } else {
        if (curStart !== null) {
          segments.push({ start: dates[curStart], end: dates[di - 1], color: curColor, text: curText.trim() });
          curStart = null;
          curColor = null;
          curText = '';
        }
      }
    }
    if (curStart !== null) {
      const lastDi = Math.min(dates.length - 1, (cells.length - 1) - dateColStart);
      if (lastDi >= curStart) {
        segments.push({ start: dates[curStart], end: dates[lastDi], color: curColor, text: curText.trim() });
      }
    }

    activities.push({
      index: activities.length + 1,
      name,
      configId,
      owner,
      crossType,
      online: online.toUpperCase() === 'TRUE',
      segments,
    });
  }

  return { activities, dates };
}

// ─── iGame ───

function igameRead(apiPath, params) {
  const raw = execSync(`node "${IGAME_QUERY}" read "${apiPath}" ${JSON.stringify(JSON.stringify(params))}`, { encoding: 'utf-8' });
  return JSON.parse(raw);
}

function igameWrite(apiPath, params) {
  const raw = execSync(`node "${IGAME_QUERY}" write "${apiPath}" ${JSON.stringify(JSON.stringify(params))}`, { encoding: 'utf-8' });
  return JSON.parse(raw);
}

function dateToTimestamp(dateStr, year = 2026) {
  const [m, d] = dateStr.split('-').map(Number);
  return Date.UTC(year, m - 1, d, 0, 0, 0);
}

function dateToEndTimestamp(dateStr, year = 2026) {
  const [m, d] = dateStr.split('-').map(Number);
  return Date.UTC(year, m - 1, d + 1, 0, 0, 0);
}

let _igameCache = null;
function loadIgameActivities() {
  if (_igameCache) return _igameCache;
  _igameCache = new Map();
  for (const status of [2, 5, 1, 4]) {
    try {
      const result = igameRead('activity/config_list/getList', { pageIndex: 1, pageSize: 200, status });
      if (result.data) {
        for (const item of result.data) {
          if (!_igameCache.has(item.activityConfigId)) {
            _igameCache.set(item.activityConfigId, item);
          }
        }
      }
    } catch (e) { }
  }
  return _igameCache;
}

function lookupIgameName(configId) {
  return loadIgameActivities().get(configId) || null;
}

// ─── Duplicate check ───

let _deployedList = null;
function loadDeployedActivities() {
  if (_deployedList) return _deployedList;
  _deployedList = [];
  // status 5 = 待审核(部署申请中), status 4 = 已上线(待开始/进行中)
  for (const status of [5, 4]) {
    try {
      const result = igameRead('activity/config_list/getList', { pageIndex: 1, pageSize: 200, status });
      if (result.data) {
        for (const item of result.data) {
          _deployedList.push({
            id: item.id,
            configId: item.activityConfigId,
            name: item.name,
            startTime: item.startTime,
            endTime: item.endTime,
            status,
          });
        }
      }
    } catch (e) { }
  }
  return _deployedList;
}

function checkDuplicates(configId, startTs, endTs, actName) {
  const deployed = loadDeployedActivities();
  const conflicts = [];
  const fuzzyConflicts = [];

  for (const d of deployed) {
    // Time overlap check
    if (!(startTs < d.endTime && d.startTime < endTs)) continue;

    const statusLabel = d.status === 5 ? '待审核' : '已上线';
    const s = new Date(d.startTime);
    const e = new Date(d.endTime);
    const sStr = `${s.getUTCMonth()+1}-${s.getUTCDate()}`;
    const eStr = `${e.getUTCMonth()+1}-${e.getUTCDate()}`;
    const desc = `id=${d.id} [${statusLabel}] ${d.name} ${sStr}~${eStr}`;

    if (d.configId === configId) {
      conflicts.push(desc);
    } else if (actName && fuzzyNameMatch(actName, d.name)) {
      fuzzyConflicts.push(desc + ` (configId=${d.configId})`);
    }
  }
  return { conflicts, fuzzyConflicts };
}

function fuzzyNameMatch(nameA, nameB) {
  const extract = (s) => (s.match(/[\u4e00-\u9fff]{2,}|[a-zA-Z0-9]{2,}/g) || []).map(w => w.toLowerCase());
  const wordsA = extract(nameA);
  const wordsB = extract(nameB);
  if (wordsA.length === 0 || wordsB.length === 0) return false;
  let matches = 0;
  for (const wa of wordsA) {
    for (const wb of wordsB) {
      if (wa.includes(wb) || wb.includes(wa)) { matches++; break; }
    }
  }
  return matches / wordsA.length >= 0.5;
}

function expandSegments(segments) {
  if (segments.length <= 1) return segments;
  const expanded = [];
  for (let i = 0; i < segments.length; i++) {
    const seg = { ...segments[i] };
    if (seg.start === seg.end && i < segments.length - 1) {
      const nextStart = segments[i + 1].start;
      const [nm, nd] = nextStart.split('-').map(Number);
      const prev = new Date(Date.UTC(2026, nm - 1, nd - 1));
      seg.end = `${prev.getUTCMonth() + 1}-${prev.getUTCDate()}`;
    } else if (seg.start === seg.end && i === segments.length - 1 && i > 0) {
      const prevSeg = expanded[i - 1];
      const [ps, pe] = [prevSeg.start, prevSeg.end].map(d => {
        const [m, dd] = d.split('-').map(Number);
        return new Date(Date.UTC(2026, m - 1, dd));
      });
      const duration = (pe - ps) / (24 * 3600 * 1000);
      const [cm, cd] = seg.start.split('-').map(Number);
      const endDt = new Date(Date.UTC(2026, cm - 1, cd + duration));
      seg.end = `${endDt.getUTCMonth() + 1}-${endDt.getUTCDate()}`;
    }
    expanded.push(seg);
  }
  return expanded;
}

// ─── Schema / Server logic ───

function detectSchema(activityName) {
  const name = activityName.toLowerCase();
  if (/schema4-6|s4-6|s4_6/i.test(name)) return '4-6';
  if (/schema3-5|s3-5|s3_5/i.test(name)) return '3-5';
  if (/schema3-6|s3-6|s3_6/i.test(name)) return null;
  if (/schema6|[_-]s6[_\s(）)$]/i.test(name) || name.endsWith('-s6') || name.endsWith('_s6')) return '6';
  if (/schema5|[_-]s5[_\s(）)$]/i.test(name) || name.endsWith('-s5') || name.endsWith('_s5')) return '5';
  if (/schema4|[_-]s4[_\s(）)$]/i.test(name) || name.endsWith('-s4') || name.endsWith('_s4')) return '4';
  if (/schema3|[_-]s3[_\s(）)$]/i.test(name) || name.endsWith('-s3') || name.endsWith('_s3')) return '3';
  return null;
}

function getSchemaServers(schemaKey) {
  const cfg = loadServerConfig();
  const graySet = new Set(cfg.gray);
  if (schemaKey === '3-5') {
    return [...cfg.schema['3'], ...cfg.schema['4'], ...cfg.schema['5']];
  } else if (schemaKey === '4-6') {
    return [...cfg.schema['4'], ...cfg.schema['5'], ...cfg.schema['6']];
  } else if (schemaKey === '6') {
    return cfg.schema['6'].filter(s => !graySet.has(s));
  } else if (schemaKey === '5' || schemaKey === '4' || schemaKey === '3') {
    return [...cfg.schema[schemaKey]];
  } else {
    const all = [...cfg.schema['6'], ...cfg.schema['5'], ...cfg.schema['4'], ...cfg.schema['3']];
    return all.filter(s => !graySet.has(s));
  }
}

function getSchemaGroups(schemaKey) {
  const cfg = loadServerConfig();
  if (schemaKey === '3-5') {
    return cfg.crossGroups['3-5'] || [];
  } else if (schemaKey === '4-6') {
    const groups = [];
    if (cfg.crossGroups['4']) groups.push(...cfg.crossGroups['4']);
    if (cfg.crossGroups['5']) groups.push(...cfg.crossGroups['5']);
    if (cfg.crossGroups['6']) groups.push(...cfg.crossGroups['6']);
    return groups;
  } else if (schemaKey && cfg.crossGroups[schemaKey]) {
    return cfg.crossGroups[schemaKey];
  }
  const allGroups = [];
  for (const key of ['6', '3-5']) {
    if (cfg.crossGroups[key]) allGroups.push(...cfg.crossGroups[key]);
  }
  return allGroups;
}

function resolveServers(activity, overrideServers) {
  if (overrideServers) return overrideServers;
  const schemaKey = detectSchema(activity.name);
  const cross = activity.crossType || '';
  if (cross.includes('跨服') && cross.includes('分组')) {
    return getSchemaGroups(schemaKey);
  } else {
    const servers = getSchemaServers(schemaKey);
    return [servers];
  }
}

// ─── Main ───

async function main() {
  checkPrerequisites();
  const opts = parseArgs();

  console.log(`读取甘特图: ${opts.tabName}`);
  console.log('');

  const { activities, dates } = readGanttFromSheet(opts.sheetId, opts.tabName);

  if (activities.length === 0) {
    console.log('未找到任何活动。');
    return;
  }

  // ─── List mode ───
  if (opts.list || !opts.deployIndices) {
    console.log(`日期范围: ${dates[0]} ~ ${dates[dates.length - 1]} (${dates.length}天)`);
    console.log('');
    console.log(`共 ${activities.length} 条活动:\n`);
    console.log(`${'序号'.padEnd(4)} ${'活动ID'.padEnd(12)} ${'活动名'.padEnd(35)} ${'负责人'.padEnd(8)} ${'跨服'.padEnd(10)} ${'Schema'.padEnd(8)} ${'上线'.padEnd(4)} 排期`);
    console.log('-'.repeat(130));

    for (const act of activities) {
      const segStr = act.segments.map(s => {
        const label = s.text ? ` (${s.text})` : '';
        return `${s.start}~${s.end}${label}`;
      }).join(' | ');
      const onlineStr = act.online ? 'Y' : 'N';
      const schema = detectSchema(act.name) || '全服';
      console.log(`${String(act.index).padEnd(4)} ${act.configId.padEnd(12)} ${act.name.padEnd(35)} ${act.owner.padEnd(8)} ${act.crossType.padEnd(10)} ${schema.padEnd(8)} ${onlineStr.padEnd(4)} ${segStr}`);
    }
    console.log('');
    console.log('使用 --deploy <序号> 部署活动，如: --deploy 1,3,5-8');
    return;
  }

  // ─── Deploy mode ───
  const indices = parseIndexRange(opts.deployIndices);
  const toDeploy = activities.filter(a => indices.includes(a.index));

  if (toDeploy.length === 0) {
    console.log('未找到匹配的活动序号。');
    return;
  }

  console.log(`准备部署 ${toDeploy.length} 条活动${opts.dryRun ? ' (dry-run)' : ''}:\n`);

  const results = [];

  for (const act of toDeploy) {
    console.log(`[${act.index}] ${act.configId} ${act.name}`);

    const igameInfo = lookupIgameName(act.configId);
    const igameName = igameInfo ? igameInfo.name : act.name;
    const acrossServer = act.crossType.includes('跨服') ? 1 : 0;
    const acrossServerRank = act.crossType.includes('分组') ? 1 : 0;
    const schema = detectSchema(act.name) || '全服';

    if (igameInfo) {
      console.log(`  iGame名称: ${igameName}`);
    } else {
      console.log(`  iGame中未找到已有记录，使用甘特图名称`);
    }
    console.log(`  Schema: ${schema}  跨服: ${act.crossType || '单服'}`);

    const servers = resolveServers(act, opts.servers);
    if (servers.length === 0) {
      console.log('  ⚠ 无法确定服务器列表，跳过');
      results.push({ act, status: 'skipped', reason: '无服务器列表' });
      continue;
    }
    const totalServers = servers.reduce((sum, g) => sum + (Array.isArray(g) ? g.length : 1), 0);
    console.log(`  服务器: ${servers.length}组 共${totalServers}个`);

    const segments = expandSegments(act.segments);
    for (let si = 0; si < segments.length; si++) {
      const seg = segments[si];
      const periodLabel = segments.length > 1 ? ` (${act.segments[si].text || `第${si + 1}期`})` : '';
      const startTs = dateToTimestamp(seg.start);
      const endTs = dateToEndTimestamp(seg.end);

      const startDate = new Date(startTs);
      const endDate = new Date(endTs);
      const startStr = `${startDate.getUTCMonth()+1}-${startDate.getUTCDate()} 08:00`;
      const endStr = `${endDate.getUTCMonth()+1}-${endDate.getUTCDate()} 08:00`;

      console.log(`  ${periodLabel ? periodLabel.trim() : ''}  ${seg.start}~${seg.end}  (iGame: ${startStr} ~ ${endStr})`);

      // ─── Duplicate check ───
      const { conflicts, fuzzyConflicts } = checkDuplicates(act.configId, startTs, endTs, act.name);
      if (conflicts.length > 0) {
        console.log('  \u2717 重复检测: 发现 ' + conflicts.length + ' 条冲突记录（精确匹配 configId）:');
        for (const c of conflicts) console.log('      ' + c);
        console.log('  \u2717 已中止该期部署，请先处理冲突记录（删除或修改时间）');
        results.push({ act, segment: si, status: 'conflict', conflicts });
        continue;
      }
      if (fuzzyConflicts.length > 0) {
        console.log('  ⚠ 模糊检查: 发现 ' + fuzzyConflicts.length + ' 条名称相似但 configId 不同的记录:');
        for (const c of fuzzyConflicts) console.log('      ' + c);
        console.log('  ⚠ 请确认是否为同一活动（configId 可能填错），确认无误后可继续部署');
        results.push({ act, segment: si, status: 'fuzzy-warn', fuzzyConflicts });
        continue;
      }

      if (opts.dryRun) {
        console.log('  → [dry-run] 跳过实际部署');
        results.push({ act, segment: si, status: 'dry-run' });
        continue;
      }

      const MAX_GROUPS = 127;
      const serverBatches = [];
      if (servers.length > MAX_GROUPS) {
        for (let i = 0; i < servers.length; i += MAX_GROUPS) {
          serverBatches.push(servers.slice(i, i + MAX_GROUPS));
        }
      } else {
        serverBatches.push(servers);
      }

      for (let bi = 0; bi < serverBatches.length; bi++) {
        const batchLabel = serverBatches.length > 1 ? ` [批次${bi + 1}/${serverBatches.length}]` : '';
        const batchServers = serverBatches[bi];

        const activityItem = {
          activityConfigId: act.configId,
          name: igameName,
          startTime: startTs,
          endTime: endTs,
          previewTime: 0,
          endShowTime: 0,
          acrossServer,
          acrossServerRank,
          servers: batchServers,
        };

        try {
          const saveResult = igameWrite('activity/add_activity/submitActivity', [activityItem]);
          if (saveResult.success && saveResult.data) {
            const savedId = Array.isArray(saveResult.data) ? saveResult.data[0] : (saveResult.data.id || saveResult.data);
            console.log(`  → 提交成功${batchLabel} (id=${savedId}, ${batchServers.length}组)`);
            results.push({ act, segment: si, status: 'submitted', id: savedId });
          } else {
            console.log(`  → 提交失败${batchLabel}: ${saveResult.message || JSON.stringify(saveResult)}`);
            results.push({ act, segment: si, status: 'failed', error: saveResult.message });
          }
        } catch (e) {
          console.log(`  → 异常${batchLabel}: ${e.message}`);
          results.push({ act, segment: si, status: 'error', error: e.message });
        }
      }
    }
    console.log('');
  }

  // Summary
  console.log('─'.repeat(60));
  const saved = results.filter(r => r.status === 'saved' || r.status === 'submitted').length;
  const failed = results.filter(r => r.status === 'failed' || r.status === 'error').length;
  const conflicted = results.filter(r => r.status === 'conflict').length;
  const skipped = results.filter(r => r.status === 'skipped' || r.status === 'dry-run').length;
  console.log(`完成: 成功=${saved} 失败=${failed} 冲突=${conflicted} 跳过=${skipped}`);
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
