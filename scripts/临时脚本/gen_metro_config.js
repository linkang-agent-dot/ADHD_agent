const fs = require('fs');

// Load all data
const p2_3516 = JSON.parse(fs.readFileSync('C:/Users/linkang/AppData/Local/Temp/gws_p2_3516_full.json','utf8'));
const p2_3517 = JSON.parse(fs.readFileSync('C:/Users/linkang/AppData/Local/Temp/gws_p2_3517_full.json','utf8'));
const x2_3510 = JSON.parse(fs.readFileSync('C:/Users/linkang/AppData/Local/Temp/gws_x2_3510_labor_allcols.json','utf8'));

const x2Labor = x2_3510.values;

// Headers
const h3516 = ['A_INT_id','C_STR_comment','A_MAP_level_design','A_MAP_level_design_b','A_MAP_auto_requirement','A_MAP_status_checkpoint','A_MAP_status_exitdoor','A_MAP_research_exitdoor','A_MAP_hero_in_mine','A_MAP_research_mineshaft_actv','A_MAP_research_checkpoint_actv','A_FLT_research_coef','A_FLT_hero_coef','A_INT_research_power_need','A_INT_hero_power_need'];
const h3517 = ['A_INT_id','C_STR_comment','A_ARR_level_group','A_MAP_requirement','A_INT_worker_limit','A_ARR_free_chest','A_ARR_level_scale','S_ARR_level_grade','A_INT_type','A_ARR_ad_free_chest','A_ARR_uw_level_group'];
const h3510 = ['A_INT_id','C_STR_comment','A_INT_plan_employ_level','A_INT_plan_employ_times','A_INT_plan_production','C_INT_plan_hero_level_production','A_ARR_level_group','A_ARR_research','A_ARR_hero_data','A_INT_mutant_mine','A_INT_iap_special','A_ARR_iap_scene','A_ARR_iap_normal','C_MAP_lc_name','A_INT_plan_monster','C_ARR_plan_display_key_map_units','C_INT_plan_display_key_rock_drop','C_STR_asset_path','C_STR_scene_path','S_ARR_plan_map_units','A_FLT_boss_total_hp','C_STR_weather_prefeb'];
const h2112 = ['A_INT_id','S_STR_comment','A_STR_constant','A_INT_index','S_INT_priority','A_INT_base_activity_id','A_MAP_filter','A_MAP_text','A_ARR_activity_components','A_MAP_description','A_INT_ui_template','S_INT_rank_group','S_STR_banner_obj_url','S_STR_banner_url','S_STR_banner_version','A_INT_default_displaykey','A_INT_icon_displaykey','A_INT_show_hud','A_INT_calendar','A_ARR_calendar_reward','S_STR_calendar_banner_url','A_INT_dependent','S_STR_mini_banner_url','C_INT_display_flags','A_INT_country_use_type'];

// Build 3516 data
const data3516 = p2_3516.values.map(row => {
  const r = [...row];
  r[1] = row[1].replace('4月循环', '6月拓荒节');
  return r;
});

// Build 3517 data
const data3517 = p2_3517.values.map(row => {
  const r = [...row];
  r[1] = row[1].replace('4月循环', '6月拓荒节');
  return r;
});

// Build 3510 data
const newLG = JSON.stringify([35171082,35171083,35171084,35171085]);
const data3510 = x2Labor.map(row => [...row]);
data3510[0][0] = '35103322'; data3510[0][1] = '6月拓荒节-schema3';
data3510[1][0] = '35103422'; data3510[1][1] = '6月拓荒节-schema4';
data3510[2][0] = '35103522'; data3510[2][1] = '6月拓荒节-schema5';
data3510.forEach(r => r[6] = newLG);

// Build 2112 data
const filter2112 = '{"op":"ge","typ":"building","id":111811,"val":999}';
const text2112 = '{"label":"LC_EVENT_labor_mine_2024","title":"LC_EVENT_labor_mine_2024"}';
const desc2112 = '{"rule":"LC_METRO_actv_rule_1"}';
const schemas = [
  {id:'TBD_S3', comment:'合成小游戏活动-6月拓荒节版本-schema3', constant:'metro_minigame_labor26_festival_1_schema3', actv:35103322},
  {id:'TBD_S4', comment:'合成小游戏活动-6月拓荒节版本-schema4', constant:'metro_minigame_labor26_festival_2_schema4', actv:35103422},
  {id:'TBD_S5', comment:'合成小游戏活动-6月拓荒节版本-schema5', constant:'metro_minigame_labor26_festival_3_schema5', actv:35103522}
];
const data2112 = schemas.map(s => {
  const comps = JSON.stringify([
    {"typ":"rank","id":21222131},
    {"typ":"metro_minigame_actv_grade","id":21215163},
    {"typ":"metro_minigame_actv","id":s.actv},
    {"typ":"retake","id":21371044},
    {"typ":"retake","id":21371045}
  ]);
  return [s.id, s.comment, s.constant, '0', '49995', '21121618', filter2112, text2112, comps, desc2112, '21191184', '1', '', 'assets/operation/P2dlcimg/activityImg/EventBanner_BG_310.png', '1', '0', '0', '21121491', '0', '[]', '', '0', '', '0', '0'];
});

// HTML generator
function esc(s) { return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function makeTable(title, headers, rows, note) {
  let h = `<h2>${title}</h2>`;
  if (note) h += `<p class="note">${note}</p>`;
  h += '<table><thead><tr>';
  headers.forEach(hd => h += `<th>${esc(hd)}</th>`);
  h += '</tr></thead><tbody>';
  rows.forEach(row => {
    h += '<tr>';
    headers.forEach((hd,i) => {
      const val = row[i] !== undefined ? row[i] : '';
      const cls = String(val).length > 100 ? ' class="long"' : '';
      h += `<td${cls}>${esc(val)}</td>`;
    });
    h += '</tr>';
  });
  h += '</tbody></table>';
  return h;
}

let html = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>X2 6月拓荒节挖矿活动配置</title>
<style>
body { font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; background: #fafafa; }
h1 { color: #1a1a1a; border-bottom: 3px solid #0066cc; padding-bottom: 10px; }
h2 { color: #0066cc; margin-top: 40px; border-bottom: 2px solid #0066cc; padding-bottom: 5px; }
.note { color: #666; font-size: 13px; margin: 5px 0 10px; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 11px; }
th { background: #0066cc; color: white; padding: 6px 8px; text-align: left; white-space: nowrap; position: sticky; top: 0; z-index: 1; }
td { border: 1px solid #ddd; padding: 4px 6px; max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; cursor: pointer; }
td.long { max-width: 300px; }
td:hover { white-space: normal; word-break: break-all; background: #fffce0; }
tr:nth-child(even) { background: #f5f5f5; }
tr:hover { background: #e8f0fe; }
.summary { background: #f0f7ff; border: 1px solid #b8d4f0; padding: 15px; border-radius: 8px; margin: 20px 0; }
.warn { color: #cc3300; font-weight: bold; }
.copy-btn { background: #0066cc; color: white; border: none; padding: 5px 12px; border-radius: 4px; cursor: pointer; margin: 5px 0; font-size: 12px; }
.copy-btn:hover { background: #0052a3; }
.copy-btn.copied { background: #28a745; }
</style>
<script>
function copyTable(tableId) {
  const table = document.getElementById(tableId);
  const rows = table.querySelectorAll('tr');
  let tsv = '';
  rows.forEach(row => {
    const cells = row.querySelectorAll('th, td');
    const vals = [];
    cells.forEach(cell => vals.push(cell.textContent));
    tsv += vals.join('\\t') + '\\n';
  });
  navigator.clipboard.writeText(tsv).then(() => {
    const btn = document.querySelector('[onclick*="' + tableId + '"]');
    btn.textContent = '已复制!';
    btn.classList.add('copied');
    setTimeout(() => { btn.textContent = '复制表格(TSV)'; btn.classList.remove('copied'); }, 2000);
  });
}
function copyDataOnly(tableId) {
  const table = document.getElementById(tableId);
  const rows = table.querySelectorAll('tbody tr');
  let tsv = '';
  rows.forEach(row => {
    const cells = row.querySelectorAll('td');
    const vals = [];
    cells.forEach(cell => vals.push(cell.textContent));
    tsv += vals.join('\\t') + '\\n';
  });
  navigator.clipboard.writeText(tsv).then(() => {
    const btn = document.querySelector('[onclick*="DataOnly"][onclick*="' + tableId + '"]');
    btn.textContent = '已复制!';
    btn.classList.add('copied');
    setTimeout(() => { btn.textContent = '只复制数据(无表头)'; btn.classList.remove('copied'); }, 2000);
  });
}
</script>
</head><body>
<h1>X2 6月拓荒节 — 挖矿活动配置</h1>
<div class="summary">
<b>配置总览：4 张表 21 行</b><br>
• <b>3516</b> metro_minigame_level: 11 行（子关地图，从 P2 复制）<br>
• <b>3517</b> metro_minigame_level_group: 4 行（关卡分组，从 P2 复制）<br>
• <b>3510</b> metro_minigame_activity_group: 3 行（活动组装，基于 X2 拓荒节修改）<br>
• <b>2112</b> activity_config: 3 行（活动定义，基于 X2 模板）<br>
<br><span class="warn">⚠ 2112 的 ID 列标记为 TBD_S3/S4/S5，需要你分配实际 ID</span><br>
<span class="warn">⚠ 点击单元格可展开查看完整 JSON</span>
</div>`;

html += '<button class="copy-btn" onclick="copyTable(\'t3516\')">复制表格(TSV)</button> ';
html += '<button class="copy-btn" onclick="copyDataOnly(\'t3516\')">只复制数据(无表头)</button>';
html += makeTable('表1: 3516 metro_minigame_level（11行）', h3516, data3516, '从 P2 复制，comment 改为 6月拓荒节。粘贴到 X2 3516 QA tab 末尾。').replace('<table>', '<table id="t3516">');

html += '<button class="copy-btn" onclick="copyTable(\'t3517\')">复制表格(TSV)</button> ';
html += '<button class="copy-btn" onclick="copyDataOnly(\'t3517\')">只复制数据(无表头)</button>';
html += makeTable('表2: 3517 metro_minigame_level_group（4行）', h3517, data3517, '从 P2 复制，comment 改为 6月拓荒节。粘贴到 X2 3517 QA tab 末尾。').replace('<table>', '<table id="t3517">');

html += '<button class="copy-btn" onclick="copyTable(\'t3510\')">复制表格(TSV)</button> ';
html += '<button class="copy-btn" onclick="copyDataOnly(\'t3510\')">只复制数据(无表头)</button>';
html += makeTable('表3: 3510 metro_minigame_activity_group（3行）', h3510, data3510, '基于 X2 拓荒节修改，level_group 换成新 4 个。粘贴到 X2 3510 QA tab 末尾。').replace('<table>', '<table id="t3510">');

html += '<button class="copy-btn" onclick="copyTable(\'t2112\')">复制表格(TSV)</button> ';
html += '<button class="copy-btn" onclick="copyDataOnly(\'t2112\')">只复制数据(无表头)</button>';
html += makeTable('表4: 2112 activity_config（3行）', h2112, data2112, '<span class="warn">ID 需手动分配！</span> 基于 X2 24拓荒节模板，metro_minigame_actv 指向新 3510 ID。').replace('<table>', '<table id="t2112">');

html += '</body></html>';

fs.writeFileSync('C:/Users/linkang/x2_labor_metro_config.html', html, 'utf8');
console.log('Done! File:', 'C:/Users/linkang/x2_labor_metro_config.html');
console.log('Size:', Math.round(html.length/1024), 'KB');
