const fs = require('fs');
const { exec } = require('child_process');

function appendRow(spreadsheetId, range, values) {
  const input = JSON.stringify({
    args: ['sheets', 'spreadsheets', 'values', 'append', '--params',
      JSON.stringify({
        spreadsheetId,
        range,
        valueInputOption: 'RAW',
        insertDataOption: 'INSERT_ROWS'
      })
    ],
    json: { values }
  });

  return new Promise((resolve, reject) => {
    const proc = exec('node C:/ADHD_agent/scripts/gws_stdin.js', {
      maxBuffer: 10 * 1024 * 1024,
      timeout: 120000
    }, (err, stdout, stderr) => {
      if (err && !stdout) return reject(new Error(err.message + '\n' + stderr));
      try { resolve(JSON.parse(stdout)); }
      catch(e) { resolve({ raw: stdout }); }
    });
    proc.stdin.write(input);
    proc.stdin.end();
  });
}

async function main() {
  const p2_3516 = JSON.parse(fs.readFileSync('C:/Users/linkang/AppData/Local/Temp/gws_p2_3516_full.json','utf8'));
  const sheetId = '1LWGp8sxiB6YSmG3Rl9FgSBOdjMKODc7oT4CwhXMCdl8';

  for (let i = 0; i < p2_3516.values.length; i++) {
    const row = [...p2_3516.values[i]];
    row[1] = row[1].replace('4月循环', '6月拓荒节');

    console.log(`Writing row ${i+1}/11: ${row[0]} ${row[1]}...`);
    try {
      const r = await appendRow(sheetId, 'metro_minigame_level!A1', [row]);
      const info = r.updates ? r.updates.updatedRange : JSON.stringify(r).substring(0,100);
      console.log(`  OK: ${info}`);
    } catch(e) {
      console.error(`  FAILED: ${e.message.substring(0,200)}`);
    }
  }
  console.log('\nAll done!');
}

main().catch(e => console.error('Fatal:', e));
