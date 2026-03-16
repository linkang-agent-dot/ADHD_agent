const fs = require('fs');
const path = require('path');

const runGwsPath = path.join(
  process.env.APPDATA, 'npm', 'node_modules',
  '@googleworkspace', 'cli', 'run-gws.js'
);

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  const { args, json } = JSON.parse(input);
  const fullArgs = [...args];
  if (json) fullArgs.push('--json', JSON.stringify(json));
  process.argv = ['node', runGwsPath, ...fullArgs];
  require(runGwsPath);
});
