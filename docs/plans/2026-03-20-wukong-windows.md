# Wukong Watcher Windows Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 `wukong-watcher` 增加 Windows 支持，在尽量保留现有主流程的前提下，用 Windows OCR 和 UI Automation 替换 macOS 专用能力。

**Architecture:** 保留 `watch_and_submit.py` 的 Playwright 监控和提码逻辑，将 OCR 与邀请码提交抽成两个平台后端模块。macOS 继续复用现有 Swift 脚本，Windows 使用 Python 后端实现 OCR 与客户端自动提交。

**Tech Stack:** Python 3.11+, Playwright, RapidOCR or PaddleOCR, pywinauto, pytest

---

### Task 1: Lock behavior with extraction tests

**Files:**
- Modify: `watch_and_submit.py`
- Create: `tests/test_extract_code.py`
- Test: `tests/test_extract_code.py`

**Step 1: Write the failing test**

```python
from watch_and_submit import extract_code


def test_extract_code_returns_code_from_normal_text():
    lines = ["当前邀请码：木母降青猪", "限量10000个", "领取说明"]
    assert extract_code(lines) == "木母降青猪"


def test_extract_code_returns_none_when_card_is_exhausted():
    lines = ["当前邀请码：木母降青猪", "今日已领完，请明日再来"]
    assert extract_code(lines) is None


def test_extract_code_returns_none_when_prefix_is_missing():
    lines = ["感谢支持", "领取说明"]
    assert extract_code(lines) is None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_extract_code.py -v`
Expected: FAIL because the repository has no test file yet.

**Step 3: Make `watch_and_submit.py` import-safe**

```python
if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
```
Keep extraction helpers at module scope so tests can import them without side effects.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_extract_code.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add watch_and_submit.py tests/test_extract_code.py
git commit -m "test: cover invite code extraction behavior"
```

### Task 2: Introduce platform backend dispatch

**Files:**
- Create: `ocr_backend.py`
- Create: `submit_backend.py`
- Modify: `watch_and_submit.py`
- Create: `tests/test_platform_backends.py`
- Test: `tests/test_platform_backends.py`

**Step 1: Write the failing test**

```python
from unittest.mock import patch

import ocr_backend
import submit_backend


def test_windows_ocr_backend_is_selected():
    with patch("platform.system", return_value="Windows"):
        func = ocr_backend.get_ocr_backend()
    assert callable(func)


def test_unknown_platform_submit_backend_raises():
    with patch("platform.system", return_value="Linux"):
        try:
            submit_backend.get_submit_backend()
        except RuntimeError as exc:
            assert "Unsupported platform" in str(exc)
        else:
            raise AssertionError("Expected RuntimeError")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_platform_backends.py -v`
Expected: FAIL because backend modules do not exist yet.

**Step 3: Write minimal implementation**

```python
# ocr_backend.py
import platform

from windows_ocr import ocr_card as windows_ocr_card


def get_ocr_backend():
    system = platform.system()
    if system == "Windows":
        return windows_ocr_card
    if system == "Darwin":
        from watch_and_submit import ocr_card as macos_ocr_card
        return macos_ocr_card
    raise RuntimeError(f"Unsupported platform: {system}")
```

```python
# submit_backend.py
import platform

from windows_submit import submit_code as windows_submit_code


def get_submit_backend():
    system = platform.system()
    if system == "Windows":
        return windows_submit_code
    if system == "Darwin":
        from watch_and_submit import submit_code as macos_submit_code
        return macos_submit_code
    raise RuntimeError(f"Unsupported platform: {system}")
```

Then update `watch_and_submit.py` to call `get_ocr_backend()` and `get_submit_backend()` once at startup.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_platform_backends.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add ocr_backend.py submit_backend.py watch_and_submit.py tests/test_platform_backends.py
git commit -m "refactor: add platform backends for OCR and submission"
```

### Task 3: Add Windows OCR backend

**Files:**
- Create: `windows_ocr.py`
- Modify: `requirements.txt`
- Optionally Modify: `test_crop_today.py`
- Test: `tests/test_platform_backends.py`

**Step 1: Write the failing test**

```python
from pathlib import Path

from windows_ocr import normalize_ocr_lines


def test_normalize_ocr_lines_filters_empty_text():
    raw_items = ["当前邀请码：木母降青猪", "", "领取说明"]
    assert normalize_ocr_lines(raw_items) == ["当前邀请码：木母降青猪", "领取说明"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_platform_backends.py -v`
Expected: FAIL because `windows_ocr.py` does not exist yet.

**Step 3: Write minimal implementation**

```python
from pathlib import Path

from rapidocr_onnxruntime import RapidOCR

_engine = RapidOCR()


def normalize_ocr_lines(raw_items: list[str]) -> list[str]:
    return [item.strip() for item in raw_items if item and item.strip()]


def ocr_card(image_path: Path) -> list[str]:
    result, _ = _engine(str(image_path))
    if not result:
        return []
    lines = [item[1] for item in result]
    return normalize_ocr_lines(lines)
```

Add dependency:

```text
rapidocr-onnxruntime
```

If OCR quality is poor, add image preprocessing in this file rather than changing `watch_and_submit.py`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_platform_backends.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add windows_ocr.py requirements.txt
git commit -m "feat: add Windows OCR backend"
```

### Task 4: Add Windows submit backend

**Files:**
- Create: `windows_submit.py`
- Modify: `requirements.txt`
- Test: manual validation on Windows

**Step 1: Write a narrow manual probe script**

```python
from pywinauto import Application

app = Application(backend="uia").connect(path="Wukong.exe")
window = app.top_window()
print(window.window_text())
print(window.descendants())
```

Save the probing code in `windows_submit.py` behind a debug flag or temporary helper function so you can inspect the real control tree first.

**Step 2: Run probe against the real client**

Run: `python windows_submit.py --inspect`
Expected: It prints the top window and child controls for the invite dialog.

**Step 3: Write minimal implementation**

```python
from pywinauto import Application
from pywinauto.keyboard import send_keys


def submit_code(code: str) -> str:
    app = Application(backend="uia").connect(title_re=".*Wukong.*")
    window = app.top_window()
    window.set_focus()

    edit = window.child_window(control_type="Edit")
    edit.set_edit_text(code)
    send_keys("{ENTER}")

    # TODO: inspect dialog text and map to SUCCESS / FAIL / UNKNOWN
    return "UNKNOWN"
```

Then iterate on selector strategy until you can:
- find the correct invite dialog
- read failure text like “邀请码有误” or “已领完”
- return `SUCCESS`, `FAIL:<text>`, or `UNKNOWN:<text>`

**Step 4: Run manual verification**

Run: `python windows_submit.py --code 测试邀请码`
Expected: The code is typed into the real invite dialog and the script prints a result string.

**Step 5: Commit**

```bash
git add windows_submit.py requirements.txt
git commit -m "feat: add Windows Wukong submit backend"
```

### Task 5: Wire the full flow and improve logs

**Files:**
- Modify: `watch_and_submit.py`
- Modify: `README.md`
- Test: manual end-to-end run on Windows

**Step 1: Add startup logging**

```python
print(f"[{now()}] platform => {platform.system()}", flush=True)
print(f"[{now()}] OCR backend ready", flush=True)
print(f"[{now()}] submit backend ready", flush=True)
```

**Step 2: Add clear dependency errors**

```python
try:
    ocr_impl = get_ocr_backend()
except ImportError as exc:
    raise RuntimeError("Windows OCR dependency missing; install requirements.txt") from exc
```

Do the same for submit backend loading.

**Step 3: Update README**

```markdown
## Windows support

- Install Python dependencies
- Run `playwright install chromium`
- Start Wukong and open the invite dialog
- Run `python watch_and_submit.py --max-minutes 180`
```

Also document:
- required Windows packages
- known limitations around UI Automation
- how to run the submit inspector

**Step 4: Run end-to-end verification**

Run: `python watch_and_submit.py --max-minutes 5`
Expected:
- watcher starts
- browser pages rotate normally
- OCR logs appear
- recognized code triggers Windows submit backend
- success stops the watcher or failure continues polling

**Step 5: Commit**

```bash
git add watch_and_submit.py README.md
git commit -m "feat: support Windows automation flow"
```

### Task 6: Add fallback and recovery notes

**Files:**
- Modify: `windows_submit.py`
- Modify: `README.md`
- Test: manual fallback validation on Windows

**Step 1: Add a fallback branch**

```python
def submit_code(code: str) -> str:
    try:
        return submit_via_uia(code)
    except Exception:
        return submit_via_keyboard_fallback(code)
```

**Step 2: Implement keyboard fallback**

```python
import pyautogui
import pyperclip


def submit_via_keyboard_fallback(code: str) -> str:
    pyperclip.copy(code)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")
    return "UNKNOWN"
```

**Step 3: Document when fallback is needed**

```markdown
If the invite dialog is not visible to UI Automation, use the keyboard fallback mode.
```

**Step 4: Run manual fallback verification**

Run: `python windows_submit.py --code 测试邀请码 --fallback`
Expected: The dialog still receives the code even when the `Edit` control is unavailable.

**Step 5: Commit**

```bash
git add windows_submit.py README.md
git commit -m "chore: add Windows fallback submission path"
```
