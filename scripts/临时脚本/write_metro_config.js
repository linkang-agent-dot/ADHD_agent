const fs = require('fs');
const path = require('path');

const runGwsPath = path.join(
  process.env.APPDATA, 'npm', 'node_modules',
  '@googleworkspace', 'cli', 'run-gws.js'
);

function gws(args, json) {
  return new Promise((resolve, reject) => {
    const fullArgs = [...args];
    if (json) fullArgs.push('--json', JSON.stringify(json));

    // Fork a child process
    const { execFileSync } = require('child_process');
    const input = JSON.stringify({ args, json });
    try {
      const result = execFileSync('node', [
        path.join(__dirname, 'gen_gws_append.js')
      ], {
        input,
        encoding: 'utf8',
        maxBuffer: 10 * 1024 * 1024,
        timeout: 60000
      });
      resolve(JSON.parse(result));
    } catch (e) {
      reject(e);
    }
  });
}

// Simpler approach: write each append as a separate gws_stdin call
async function appendToSheet(spreadsheetId, range, values) {
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
    const { exec } = require('child_process');
    const proc = exec(`node C:/ADHD_agent/scripts/gws_stdin.js`, {
      maxBuffer: 10 * 1024 * 1024,
      timeout: 120000
    }, (err, stdout, stderr) => {
      if (err && !stdout) return reject(err);
      try {
        resolve(JSON.parse(stdout));
      } catch(e) {
        resolve({ raw: stdout, error: stderr });
      }
    });
    proc.stdin.write(input);
    proc.stdin.end();
  });
}

async function main() {
  // Load data
  const p2_3516 = JSON.parse(fs.readFileSync('C:/Users/linkang/AppData/Local/Temp/gws_p2_3516_full.json','utf8'));
  const p2_3517 = JSON.parse(fs.readFileSync('C:/Users/linkang/AppData/Local/Temp/gws_p2_3517_full.json','utf8'));
  const x2_3510 = JSON.parse(fs.readFileSync('C:/Users/linkang/AppData/Local/Temp/gws_x2_3510_labor_allcols.json','utf8'));

  // Prepare 3516 data (11 rows, rename comments)
  const data3516 = p2_3516.values.map(row => {
    const r = [...row];
    r[1] = row[1].replace('4月循环', '6月拓荒节');
    return r;
  });

  // Prepare 3517 data (4 rows, rename comments)
  const data3517 = p2_3517.values.map(row => {
    const r = [...row];
    r[1] = row[1].replace('4月循环', '6月拓荒节');
    return r;
  });

  // Prepare 3510 data (3 rows, modify from X2 existing)
  const newLG = JSON.stringify([35171082,35171083,35171084,35171085]);
  const data3510 = x2_3510.values.map(row => [...row]);
  data3510[0][0] = '35103322'; data3510[0][1] = '6月拓荒节-schema3';
  data3510[1][0] = '35103422'; data3510[1][1] = '6月拓荒节-schema4';
  data3510[2][0] = '35103522'; data3510[2][1] = '6月拓荒节-schema5';
  data3510.forEach(r => r[6] = newLG);

  // Write 3516
  console.log('Writing 3516 (11 rows)...');
  try {
    const r1 = await appendToSheet(
      '1LWGp8sxiB6YSmG3Rl9FgSBOdjMKODc7oT4CwhXMCdl8',
      'metro_minigame_level!A1',
      data3516
    );
    console.log('3516 result:', r1.updates ? `${r1.updates.updatedRows} rows written to ${r1.updates.updatedRange}` : JSON.stringify(r1).substring(0, 200));
  } catch(e) {
    console.error('3516 ERROR:', e.message || e);
  }

  // Write 3517
  console.log('\nWriting 3517 (4 rows)...');
  try {
    const r2 = await appendToSheet(
      '1MzZG2C1qdCotqQjh0v29XEGT5NWsxtyFGErn8uQGIPo',
      'metro_minigame_level_group!A1',
      data3517
    );
    console.log('3517 result:', r2.updates ? `${r2.updates.updatedRows} rows written to ${r2.updates.updatedRange}` : JSON.stringify(r2).substring(0, 200));
  } catch(e) {
    console.error('3517 ERROR:', e.message || e);
  }

  // Write 3510
  console.log('\nWriting 3510 (3 rows)...');
  try {
    const r3 = await appendToSheet(
      '1I4qvitjb1fPrfqcL-hLhsO-fsL41ZNPMLZDlYtSY1hA',
      'metro_minigame_activity_group!A1',
      data3510
    );
    console.log('3510 result:', r3.updates ? `${r3.updates.updatedRows} rows written to ${r3.updates.updatedRange}` : JSON.stringify(r3).substring(0, 200));
  } catch(e) {
    console.error('3510 ERROR:', e.message || e);
  }

  console.log('\nDone!');
}

main().catch(e => console.error('Fatal:', e));
