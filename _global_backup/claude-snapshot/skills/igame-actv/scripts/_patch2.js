const fs = require('fs');
const f = 'C:/Users/linkang/.claude/skills/igame-actv/deploy-from-gantt.js';
let code = fs.readFileSync(f, 'utf-8');

// 1. Replace checkDuplicates function with new version that includes fuzzy matching
const oldCheck = `function checkDuplicates(configId, startTs, endTs) {
  const deployed = loadDeployedActivities();
  const conflicts = [];
  for (const d of deployed) {
    if (d.configId !== configId) continue;
    // Time overlap: startA < endB && startB < endA
    if (startTs < d.endTime && d.startTime < endTs) {
      const statusLabel = d.status === 5 ? '待审核' : '已上线';
      const s = new Date(d.startTime);
      const e = new Date(d.endTime);
      const sStr = \`\${s.getUTCMonth()+1}-\${s.getUTCDate()}\`;
      const eStr = \`\${e.getUTCMonth()+1}-\${e.getUTCDate()}\`;
      conflicts.push(\`id=\${d.id} [\${statusLabel}] \${d.name} \${sStr}~\${eStr}\`);
    }
  }
  return conflicts;
}`;

const newCheck = `function checkDuplicates(configId, startTs, endTs, actName) {
  const deployed = loadDeployedActivities();
  const conflicts = [];
  const fuzzyConflicts = [];

  for (const d of deployed) {
    // Time overlap check
    if (!(startTs < d.endTime && d.startTime < endTs)) continue;

    const statusLabel = d.status === 5 ? '待审核' : '已上线';
    const s = new Date(d.startTime);
    const e = new Date(d.endTime);
    const sStr = \`\${s.getUTCMonth()+1}-\${s.getUTCDate()}\`;
    const eStr = \`\${e.getUTCMonth()+1}-\${e.getUTCDate()}\`;
    const desc = \`id=\${d.id} [\${statusLabel}] \${d.name} \${sStr}~\${eStr}\`;

    if (d.configId === configId) {
      conflicts.push(desc);
    } else if (actName && fuzzyNameMatch(actName, d.name)) {
      fuzzyConflicts.push(desc + \` (configId=\${d.configId})\`);
    }
  }
  return { conflicts, fuzzyConflicts };
}

function fuzzyNameMatch(nameA, nameB) {
  const extract = (s) => (s.match(/[\\u4e00-\\u9fff]{2,}|[a-zA-Z0-9]{2,}/g) || []).map(w => w.toLowerCase());
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
}`;

if (!code.includes(oldCheck)) { console.error('checkDuplicates not found!'); process.exit(1); }
code = code.replace(oldCheck, newCheck);

// 2. Update the caller to pass actName and handle new return format
const oldCaller = `      const conflicts = checkDuplicates(act.configId, startTs, endTs);
      if (conflicts.length > 0) {
        console.log('  \\u2717 重复检测: 发现 ' + conflicts.length + ' 条冲突记录:');
        for (const c of conflicts) console.log('      ' + c);
        console.log('  \\u2717 已中止该期部署，请先处理冲突记录（删除或修改时间）');
        results.push({ act, segment: si, status: 'conflict', conflicts });
        continue;
      }`;

const newCaller = `      const { conflicts, fuzzyConflicts } = checkDuplicates(act.configId, startTs, endTs, act.name);
      if (conflicts.length > 0) {
        console.log('  \\u2717 重复检测: 发现 ' + conflicts.length + ' 条冲突记录（精确匹配 configId）:');
        for (const c of conflicts) console.log('      ' + c);
        console.log('  \\u2717 已中止该期部署，请先处理冲突记录（删除或修改时间）');
        results.push({ act, segment: si, status: 'conflict', conflicts });
        continue;
      }
      if (fuzzyConflicts.length > 0) {
        console.log('  ⚠ 模糊检查: 发现 ' + fuzzyConflicts.length + ' 条名称相似但 configId 不同的记录:');
        for (const c of fuzzyConflicts) console.log('      ' + c);
        console.log('  ⚠ 请确认是否为同一活动（configId 可能填错），确认无误后可继续部署');
        results.push({ act, segment: si, status: 'fuzzy-warn', fuzzyConflicts });
        continue;
      }`;

if (!code.includes(oldCaller)) { console.error('caller not found!'); process.exit(1); }
code = code.replace(oldCaller, newCaller);

fs.writeFileSync(f, code);
console.log('Done - updated checkDuplicates with fuzzy matching');
