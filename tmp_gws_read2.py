"""Check raw bytes from gws output."""
import subprocess
import sys

def gws_read_raw(spreadsheet_id, range_name):
    result = subprocess.run(
        f'gws sheets +read --spreadsheet {spreadsheet_id} --range "{range_name}"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return result.stdout

if __name__ == '__main__':
    spreadsheet_id = sys.argv[1]
    range_name = sys.argv[2]
    
    raw = gws_read_raw(spreadsheet_id, range_name)
    print(f'Total bytes: {len(raw)}')
    print(f'First 300 bytes: {repr(raw[:300])}')
    
    # Try different decodings
    for enc in ['utf-8', 'utf-8-sig', 'gbk', 'gb18030', 'cp936']:
        try:
            text = raw.decode(enc)
            print(f'\n{enc} decode works, first 200 chars: {text[:200]}')
            break
        except Exception as e:
            print(f'{enc} failed: {e}')
