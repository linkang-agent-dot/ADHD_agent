const fs = require('fs');
const data = require('C:/Users/linkang/festival_activities.json');
const items = data.map((d, i) => ({
  id: i + 1,
  festival: d.festival,
  year: d.year,
  title: d.title.replace(/\[\d+\]/g, '').trim(),
  url: d.url
}));

const data2026 = [
  {festival:'2026春节',year:'2026',title:'2026春节gacha回归',url:'https://wiki.tap4fun.com/pages/viewpage.action?pageId=233096639'},
  {festival:'2026春节',year:'2026',title:'MJ8鱿鱼游戏数据分析',url:'https://wiki.tap4fun.com/pages/viewpage.action?pageId=233096647'},
  {festival:'2026春节',year:'2026',title:'挖孔三期数据回归',url:'https://wiki.tap4fun.com/pages/viewpage.action?pageId=233087719'},
  {festival:'2026春节',year:'2026',title:'机甲转盘双倍活动',url:'https://wiki.tap4fun.com/pages/viewpage.action?pageId=233092027'},
  {festival:'2026春节',year:'2026',title:'春节-新大富翁（异族版）回归',url:'https://wiki.tap4fun.com/pages/viewpage.action?pageId=233093544'},
  {festival:'2026春节',year:'2026',title:'春节行军返场-一番赏',url:'https://wiki.tap4fun.com/pages/viewpage.action?pageId=233100686'},
  {festival:'2026春节',year:'2026',title:'钓鱼活动数据回归',url:'https://wiki.tap4fun.com/pages/viewpage.action?pageId=233088344'},
];

data2026.forEach(d => items.push({id: items.length + 1, ...d}));

const preCategories = {"1":"节日整体review","2":"掉落活动","3":"皮肤gacha","4":"GPT讲价消耗","5":"节日BP","6":"连锁礼包","7":"挖矿活动","8":"拜访活动","9":"红包","10":"巨猿活动","11":"单笔充值","12":"装饰券投放","13":"七日活动","14":"节日BP","15":"单笔充值","16":"巨猿活动","17":"挖矿活动","18":"消耗活动","19":"节日整体review","20":"皮肤gacha","21":"单笔充值","22":"节日BP","23":"兑换活动","24":"连锁礼包","25":"挖矿活动","26":"消耗活动","27":"装饰券投放","28":"七日活动","29":"消耗活动","30":"皮肤gacha","31":"单笔充值","32":"节日BP","34":"挖矿活动","35":"GPT讲价消耗","37":"七日活动","38":"掉落活动","39":"单笔充值","40":"节日BP","41":"折扣活动","42":"挖矿活动","43":"七日活动","45":"掉落活动","46":"装饰券投放","47":"皮肤gacha","48":"兑换活动","50":"机甲gacha","51":"皮肤gacha","52":"节日BP","53":"单笔充值","54":"行军表情","55":"装饰券投放","56":"掉落活动","57":"消耗活动","58":"七日活动","59":"挖矿活动","60":"单笔充值","61":"单笔充值","62":"折扣活动","63":"节日BP","64":"行军表情","65":"连锁礼包","66":"周卡","67":"消耗活动","68":"七日活动","69":"皮肤gacha","70":"巨猿活动","71":"掉落活动","72":"装饰券投放","73":"连锁礼包","74":"单笔充值","75":"GPT讲价消耗","76":"节日BP","77":"手札相册","78":"手札相册","79":"巨猿活动","80":"行军表情","81":"挖矿活动","82":"连锁礼包","83":"GPT讲价消耗","84":"签到活动","85":"七日活动","86":"皮肤gacha","88":"消耗活动","89":"手札相册","90":"掉落活动","91":"机甲gacha","92":"装饰券投放","93":"签到BP","94":"节日BP","96":"挖矿活动","97":"巨猿活动","98":"巨猿活动","99":"七日活动","100":"行军表情","101":"单笔充值","102":"掉落活动","103":"装饰券投放","104":"连锁礼包","105":"行军表情","106":"机甲gacha","107":"连锁礼包","108":"节日BP","109":"周卡","110":"巨猿活动","111":"皮肤gacha","112":"七日活动","113":"挖矿活动","114":"掉落活动","115":"装饰券投放","116":"GPT讲价消耗","118":"单笔充值","119":"签到BP","120":"单笔充值","121":"挖矿活动","122":"单笔充值","123":"GPT讲价消耗","124":"七日活动","126":"皮肤gacha","127":"节日BP","128":"装饰券投放","129":"折扣活动","130":"挖矿活动","131":"单笔充值","132":"折扣活动","134":"七日活动","136":"节日BP","138":"手札相册","139":"行军表情","140":"装饰券投放","141":"装饰券投放","142":"单笔充值","143":"皮肤gacha","144":"节日BP","145":"七日活动","146":"单笔充值","147":"巨猿活动","148":"挖矿活动","149":"掉落活动","150":"机甲gacha","151":"连锁礼包","152":"Bingo活动","153":"七日活动","154":"单笔充值","155":"挖矿活动","156":"掉落活动","157":"节日BP","158":"皮肤gacha","159":"七日活动","160":"装饰券投放","161":"节日BP","162":"皮肤gacha","163":"挖矿活动","164":"掉落活动","165":"单笔充值","166":"周卡","167":"节日BP","168":"挖矿活动","169":"机甲gacha","170":"GPT讲价消耗","171":"单笔充值","172":"行军表情","173":"转盘抽奖","174":"大富翁","175":"巨猿活动","176":"皮肤gacha","177":"挖矿活动","178":"单笔充值","179":"节日BP","180":"聚宝盆","181":"礼包团购","182":"巨猿活动","183":"单笔充值","184":"单笔充值","185":"挖矿活动","186":"机甲gacha","187":"皮肤gacha","188":"节日BP","189":"皮肤gacha","191":"巨猿活动","192":"挖矿活动","193":"单笔充值","194":"节日BP","196":"巨猿活动","197":"礼包团购","198":"大富翁","199":"机甲gacha","202":"GPT讲价消耗","203":"挖矿活动","204":"节日BP","205":"大富翁","206":"皮肤gacha","208":"行军表情","209":"礼包团购","210":"挖矿活动","211":"巨猿活动","213":"周卡","216":"挖矿活动","217":"大富翁","218":"皮肤gacha","219":"巨猿活动","220":"节日BP","221":"消耗活动","222":"挖矿活动","223":"挖矿活动","224":"七日活动","225":"单笔充值","227":"GPT讲价消耗","229":"连锁礼包","231":"皮肤gacha","233":"挖矿活动","234":"机甲gacha","235":"大富翁","236":"行军表情","244":"挖矿活动"};

const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>节日活动子模块归类</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1500px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 20px; }
        .stats { display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; justify-content: center; }
        .stat-card { background: white; padding: 15px 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-card h3 { font-size: 24px; color: #1890ff; }
        .stat-card p { color: #666; font-size: 14px; }
        .controls { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .controls input, .controls select { padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; }
        .controls button { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; color: white; }
        .btn-primary { background: #1890ff; }
        .btn-success { background: #52c41a; }
        .btn-warning { background: #faad14; }
        .btn-info { background: #13c2c2; }
        .table-container { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #fafafa; font-weight: 600; position: sticky; top: 0; }
        tr:hover { background: #f5f5f5; }
        .category-select { padding: 5px 8px; border: 1px solid #ddd; border-radius: 4px; min-width: 120px; }
        .category-select.categorized { background: #e6f7ff; border-color: #1890ff; }
        .custom-input { padding: 5px 8px; border: 1px solid #ddd; border-radius: 4px; width: 100px; display: none; }
        .custom-input.show { display: inline-block; }
        a { color: #1890ff; text-decoration: none; }
        .tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
        .tag-2024 { background: #fff7e6; color: #fa8c16; }
        .tag-2025 { background: #f6ffed; color: #52c41a; }
        .tag-2026 { background: #e6f7ff; color: #1890ff; }
        .custom-cats { margin-bottom: 15px; padding: 10px; background: #fffbe6; border-radius: 4px; border: 1px solid #ffe58f; }
    </style>
</head>
<body>
<div class="container">
    <h1>节日活动子模块归类 (2024-2026)</h1>
    <div class="custom-cats">
        <strong>添加自定义分类：</strong>
        <input type="text" id="newCatInput" placeholder="输入新分类名称" style="width:200px">
        <button class="btn-info" onclick="addCustomCategory()">添加</button>
        <span id="customCatList" style="margin-left:15px;color:#666;"></span>
    </div>
    <div class="stats">
        <div class="stat-card"><h3 id="totalCount">0</h3><p>总子活动数</p></div>
        <div class="stat-card"><h3 id="categorizedCount">0</h3><p>已归类</p></div>
        <div class="stat-card"><h3 id="uncategorizedCount">0</h3><p>未归类</p></div>
    </div>
    <div class="controls">
        <input type="text" id="searchInput" placeholder="搜索活动名称..." style="width:250px">
        <select id="filterFestival"><option value="">全部节日</option></select>
        <select id="filterCategory"><option value="">全部分类</option><option value="uncategorized">未归类</option></select>
        <button class="btn-primary" onclick="exportData()">导出JSON</button>
        <button class="btn-success" onclick="exportMarkdown()">导出Markdown</button>
        <button class="btn-warning" onclick="clearAll()">清空归类</button>
    </div>
    <div class="table-container">
        <table><thead><tr><th>#</th><th>节日</th><th>年份</th><th>子活动名称</th><th>分类</th></tr></thead><tbody id="tableBody"></tbody></table>
    </div>
</div>
<script>
const regressionData = ${JSON.stringify(items)};
const preCategories = ${JSON.stringify(preCategories)};
const defaultCategories = ['节日BP','签到BP','皮肤gacha','机甲gacha','单笔充值','七日活动','掉落活动','巨猿活动','连锁礼包','Bingo活动','消耗活动','聚宝盆','转盘抽奖','签到活动','兑换活动','挖矿活动','大富翁','GPT讲价消耗','礼包团购','装饰券投放','行军表情','周卡','手札相册','折扣活动','拜访活动','红包','节日整体review'];
let customCategories = JSON.parse(localStorage.getItem('customCategories') || '[]');
let categoryData = JSON.parse(localStorage.getItem('festivalSubCategories4') || 'null');
if (!categoryData) { categoryData = {...preCategories}; localStorage.setItem('festivalSubCategories4', JSON.stringify(categoryData)); }

function getAllCategories() { return ['', ...defaultCategories, ...customCategories, '其他']; }

function updateCategorySelects() {
    const cats = getAllCategories();
    const filterCat = document.getElementById('filterCategory');
    const cur = filterCat.value;
    filterCat.innerHTML = '<option value="">全部分类</option><option value="uncategorized">未归类</option>';
    cats.slice(1).forEach(c => { const o = document.createElement('option'); o.value = c; o.textContent = c; filterCat.appendChild(o); });
    filterCat.value = cur;
    document.getElementById('customCatList').textContent = customCategories.length ? '自定义: ' + customCategories.join(', ') : '';
}

function addCustomCategory() {
    const input = document.getElementById('newCatInput');
    const name = input.value.trim();
    if (name && !defaultCategories.includes(name) && !customCategories.includes(name)) {
        customCategories.push(name);
        localStorage.setItem('customCategories', JSON.stringify(customCategories));
        input.value = '';
        updateCategorySelects();
        filterAndRender();
    }
}

const festivals = [...new Set(regressionData.map(d => d.festival))];
const festivalSelect = document.getElementById('filterFestival');
festivals.forEach(f => { const o = document.createElement('option'); o.value = f; o.textContent = f; festivalSelect.appendChild(o); });

function getYearTag(year) {
    const cls = year === '2024' ? 'tag-2024' : year === '2025' ? 'tag-2025' : 'tag-2026';
    return '<span class="tag ' + cls + '">' + year + '</span>';
}

function renderTable(data) {
    const cats = getAllCategories();
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = data.map(item => {
        const cat = categoryData[item.id] || '';
        const opts = cats.map(c => '<option value="' + c + '"' + (c === cat ? ' selected' : '') + '>' + (c || '-- 选择 --') + '</option>').join('');
        return '<tr><td>' + item.id + '</td><td>' + item.festival + '</td><td>' + getYearTag(item.year) + '</td><td><a href="' + item.url + '" target="_blank">' + item.title + '</a></td><td><select class="category-select' + (cat ? ' categorized' : '') + '" onchange="setCategory(' + item.id + ', this.value, this)">' + opts + '</select><input type="text" class="custom-input" placeholder="自定义" onblur="setCustomCat(' + item.id + ', this)"></td></tr>';
    }).join('');
    updateStats();
}

function setCategory(id, cat, sel) {
    const input = sel.nextElementSibling;
    if (cat === '其他') { input.classList.add('show'); input.focus(); }
    else { input.classList.remove('show'); if (cat) categoryData[id] = cat; else delete categoryData[id]; localStorage.setItem('festivalSubCategories4', JSON.stringify(categoryData)); sel.className = 'category-select' + (cat ? ' categorized' : ''); updateStats(); }
}

function setCustomCat(id, input) {
    const val = input.value.trim();
    if (val) { categoryData[id] = val; if (!defaultCategories.includes(val) && !customCategories.includes(val)) { customCategories.push(val); localStorage.setItem('customCategories', JSON.stringify(customCategories)); updateCategorySelects(); } }
    localStorage.setItem('festivalSubCategories4', JSON.stringify(categoryData));
    filterAndRender();
}

function updateStats() {
    const total = regressionData.length;
    const categorized = Object.keys(categoryData).filter(k => categoryData[k]).length;
    document.getElementById('totalCount').textContent = total;
    document.getElementById('categorizedCount').textContent = categorized;
    document.getElementById('uncategorizedCount').textContent = total - categorized;
}

function filterAndRender() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const filterFest = document.getElementById('filterFestival').value;
    const filterCat = document.getElementById('filterCategory').value;
    let data = regressionData.filter(item => {
        const matchSearch = item.title.toLowerCase().includes(search) || item.festival.toLowerCase().includes(search);
        const matchFest = !filterFest || item.festival === filterFest;
        const cat = categoryData[item.id] || '';
        const matchCat = !filterCat || (filterCat === 'uncategorized' ? !cat : cat === filterCat);
        return matchSearch && matchFest && matchCat;
    });
    renderTable(data);
}

function exportData() {
    const result = regressionData.map(item => ({...item, category: categoryData[item.id] || ''}));
    const blob = new Blob([JSON.stringify(result, null, 2)], {type: 'application/json'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = '节日子活动归类.json'; a.click();
}

function exportMarkdown() {
    const grouped = {};
    regressionData.forEach(item => { const cat = categoryData[item.id] || '未归类'; if (!grouped[cat]) grouped[cat] = []; grouped[cat].push(item); });
    let md = '# 节日活动子模块归类\\n\\n';
    Object.keys(grouped).sort().forEach(cat => { md += '## ' + cat + '\\n\\n'; grouped[cat].forEach(item => { md += '- ' + item.festival + ' - [' + item.title + '](' + item.url + ')\\n'; }); md += '\\n'; });
    const blob = new Blob([md], {type: 'text/markdown'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = '节日子活动归类.md'; a.click();
}

function clearAll() {
    if (confirm('确定清空？将恢复为预分类状态')) { categoryData = {...preCategories}; localStorage.setItem('festivalSubCategories4', JSON.stringify(categoryData)); filterAndRender(); }
}

document.getElementById('searchInput').addEventListener('input', filterAndRender);
document.getElementById('filterFestival').addEventListener('change', filterAndRender);
document.getElementById('filterCategory').addEventListener('change', filterAndRender);
document.getElementById('newCatInput').addEventListener('keypress', function(e) { if(e.key === 'Enter') addCustomCategory(); });

updateCategorySelects();
filterAndRender();
</script>
</body>
</html>`;

fs.writeFileSync('C:/Users/linkang/节日活动回归归类_2024.html', html);
console.log('Done');
