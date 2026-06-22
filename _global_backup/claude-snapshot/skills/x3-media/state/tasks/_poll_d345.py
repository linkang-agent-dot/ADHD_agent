import subprocess
import sys
import json
import time

call_grfal = r"C:\Users\linkang\.claude\skills\grfal-api\scripts\call_grfal.py"
grfal_task_id = "generate_image_d8b3062c_1781536259"

for attempt in range(60):
    time.sleep(20)
    cmd = [
        sys.executable, call_grfal,
        "--check-task", grfal_task_id,
        "--url", "http://172.20.90.45:6018",
        "--public-url", "none",
    ]
    result = subprocess.run(cmd, capture_output=True)
    stdout = result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
    stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""

    with open("_poll_d345.log", "a", encoding="utf-8") as f:
        f.write(f"[poll {attempt+1}] rc={result.returncode}\n")
        f.write(stdout[:2000] + "\n")
        if stderr:
            f.write("STDERR: " + stderr[:200] + "\n")

    try:
        data = json.loads(stdout)
        status = data.get("status", "")
        # terminal states: completed / failed / error, and NOT "running"/"pending"
        if status in ("completed", "failed", "error"):
            with open("_poll_d345_final.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            break
        # also break if success=true AND result URLs present
        if data.get("success") is True and data.get("result"):
            with open("_poll_d345_final.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            break
        if data.get("success") is False:
            with open("_poll_d345_final.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            break
    except Exception as e:
        with open("_poll_d345.log", "a", encoding="utf-8") as f:
            f.write(f"parse error: {e}\n")

with open("_poll_d345.log", "a", encoding="utf-8") as f:
    f.write("POLLING DONE\n")
