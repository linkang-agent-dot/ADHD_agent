import json, re, os, glob, sys
sys.stdout.reconfigure(encoding='utf-8')

log_dir = r"C:\Users\linkang\AppData\Local\Temp\openclaw"
log_files = sorted(glob.glob(os.path.join(log_dir, "openclaw-*.log")))

for logf in log_files:
    fname = os.path.basename(logf)
    success = 0
    fail_794 = 0
    fail_other = 0
    errors = []
    
    with open(logf, encoding='utf-8', errors='replace') as f:
        for line in f:
            if 'embedded run agent end' not in line and 'embedded_run_agent_end' not in line:
                continue
            try:
                data = json.loads(line)
                info = data.get('1', {})
                if isinstance(info, dict) and info.get('event') == 'embedded_run_agent_end':
                    is_error = info.get('isError', False)
                    err_msg = info.get('error', '')
                    model = info.get('model', '?')
                    ts = data.get('time', '?')[:19]
                    
                    if is_error:
                        if '794' in str(err_msg):
                            fail_794 += 1
                        else:
                            fail_other += 1
                        errors.append((ts, model, str(err_msg)[:80]))
                    else:
                        success += 1
            except json.JSONDecodeError:
                pass
    
    print(f"\n=== {fname} ===")
    print(f"  Success: {success}, 794 errors: {fail_794}, Other errors: {fail_other}")
    if errors:
        print(f"  Error timeline:")
        for ts, model, err in errors:
            print(f"    {ts} | {model} | {err}")
