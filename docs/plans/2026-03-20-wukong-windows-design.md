# Wukong Watcher Windows 迁移设计

## 目标

将 `xuzizhanSTAN/wukong-watcher` 从仅支持 macOS 的自动化脚本，迁移为可在 Windows 上运行的版本，同时尽量保留现有的网页监控、截图、邀请码提取和重试逻辑。

## 当前实现拆解

原项目可分为 3 个子系统：

1. 网页监控
   使用 `Playwright` 打开悟空官网，维护 6 个错峰页面，等待首页动画稳定后截图固定区域。

2. OCR 识别
   当前通过 `ocr_card.swift` 调用 macOS `Vision` 做中文 OCR，再由 Python 正则从文本中提取邀请码。

3. 桌面端提交
   当前通过 `submit_wukong_code.swift` 调用 macOS 辅助功能 API，激活 `Wukong` 客户端、找到邀请码弹窗输入框、写入内容并回车提交，然后读取弹窗反馈。

其中第 1 部分天然跨平台，第 2 和第 3 部分是本次 Windows 迁移的核心。

## 推荐方案

推荐采用“保留 Python 主流程，抽出平台适配层”的方案：

- 继续保留 `watch_and_submit.py` 作为主控脚本
- 新增 Python 适配层，统一暴露 `ocr_card(image_path)` 和 `submit_code(code)` 两个接口
- macOS 继续复用现有 Swift 脚本
- Windows 新增 Python 实现：
  - OCR：优先使用 `RapidOCR` 或 `PaddleOCR`
  - 桌面自动化：优先使用 `pywinauto`，必要时退化为 `pyautogui`

这样能把平台差异压缩到很小的边界内，保留主逻辑不变，也便于以后继续支持两端。

## 方案对比

### 方案 A：直接改成 Windows only

做法：
- 直接把 `watch_and_submit.py` 中调用 Swift 的部分改成 Windows Python 实现

优点：
- 改动最少
- 最快出结果

缺点：
- 会破坏现有 macOS 版本
- 后续不好维护

### 方案 B：新增跨平台适配层

做法：
- 将 OCR 和提交逻辑抽象成后端接口
- macOS 与 Windows 各自实现

优点：
- 结构清晰
- 能保留现有 macOS 能力
- 适合后续继续调优 OCR 和控件定位

缺点：
- 首次改造略多于直接硬改

### 方案 C：先做“识码 + 提示”版，再补自动提交

做法：
- 先迁移网页监控和 OCR
- Windows 版先输出识别到的邀请码，或复制到剪贴板

优点：
- 可快速验证官网侧和 OCR 侧是否跑通

缺点：
- 没有完成自动提交闭环

## 推荐结论

推荐选择 **方案 B**。

原因：
- 它对原项目侵入最小
- Windows 和 macOS 都能保留
- 风险主要集中在 Windows 桌面控件定位，适配层结构能把这部分不确定性隔离开

## 建议文件结构

建议在原仓库中形成如下结构：

```text
wukong-watcher/
  watch_and_submit.py
  ocr_backend.py
  submit_backend.py
  windows_ocr.py
  windows_submit.py
  ocr_card.swift
  submit_wukong_code.swift
  requirements.txt
  README.md
  tests/
    test_extract_code.py
    test_platform_backends.py
```

说明：
- `ocr_backend.py` 负责根据平台分发到 macOS Swift 或 Windows Python OCR
- `submit_backend.py` 负责根据平台分发到 macOS Swift 或 Windows UI Automation
- Windows 的实现先尽量独立，不污染主流程

## Windows OCR 设计

### 目标

替代 `ocr_card.swift`，在 Windows 上返回与现有实现兼容的文本行列表。

### 候选库

1. `RapidOCR`
   优点：上手轻，中文效果通常比裸 `Tesseract` 更稳。
   缺点：需要额外模型依赖。

2. `PaddleOCR`
   优点：中文效果强，生态成熟。
   缺点：安装更重。

3. `Tesseract`
   优点：最常见。
   缺点：中文场景效果不稳定，训练数据也更麻烦。

### 推荐

优先用 `RapidOCR`。如果后续识别效果不足，再切换到 `PaddleOCR`。

### 接口约定

`windows_ocr.py` 应提供：

```python
def ocr_card(image_path: Path) -> list[str]:
    ...
```

返回值必须与当前 `ocr_card.swift` 的行为保持一致，即返回按行切分的字符串列表，供现有 `extract_code()` 继续复用。

## Windows 桌面自动化设计

### 目标

替代 `submit_wukong_code.swift`，在 Windows 上完成：

1. 激活 `Wukong` 桌面端窗口
2. 找到邀请码输入框
3. 输入邀请码
4. 触发提交
5. 读取反馈文案，判断成功 / 失败 / 未知

### 首选技术

使用 `pywinauto` 的 UIA 后端：

- 优先通过窗口标题、类名或 AutomationId 定位输入框
- 定位成功后直接 `set_edit_text()` 或 `type_keys()`
- 读取对话框中的提示文本进行结果判定

### 兜底方案

如果 UIA 无法稳定读到控件树，则退化为：

- 激活窗口
- 通过相对坐标点击输入框
- 粘贴邀请码
- 按回车
- 通过 OCR 或剪贴板/窗口文本判断结果

该方案稳定性较差，只作为保底。

## 主流程改造点

`watch_and_submit.py` 需要做的改造应尽量小：

1. 将 `ocr_card()` 调用改为来自 `ocr_backend.py`
2. 将 `submit_code()` 调用改为来自 `submit_backend.py`
3. 启动时打印当前平台和所选后端
4. 对 Windows 后端缺失依赖时给出清晰报错

其余逻辑例如：

- 6 页面错峰轮询
- `SETTLE_SECONDS = 6`
- 固定裁剪区域
- 识别失败后的重试
- `seen_codes` 去重

都尽量不改。

## 测试策略

### 单元测试

优先补这两类测试：

1. `extract_code()` 的样例测试
   覆盖：
   - 正常邀请码
   - “今日已领完”
   - 乱码或不完整文案

2. 平台分发逻辑测试
   覆盖：
   - Windows 选择 Windows backend
   - macOS 选择 macOS backend
   - 不支持平台时报错

### 手动验证

需要真实在 Windows 机器上做：

1. 仅运行 OCR，验证截图区域能识别出“当前邀请码”
2. 仅运行提交模块，验证能操作 `Wukong` 邀请码弹窗
3. 全链路运行，验证失败码会继续等待下一轮

## 主要风险

### 风险 1：Windows 客户端控件不可见

如果 `Wukong` 邀请码弹窗是自绘控件，`pywinauto` 可能拿不到标准输入框。

应对：
- 先用控件检查工具验证
- 若失败，降级到键鼠模拟

### 风险 2：Windows OCR 准确率不够

官网卡片区域较小、文案可能带装饰字体，OCR 效果会受影响。

应对：
- 保留预处理步骤，例如灰度、增强、放大
- 允许在 Windows OCR 实现中先做图像增强

### 风险 3：页面布局变化

截图区域仍然是硬编码坐标，官网改版后会失效。

应对：
- 保留调试脚本
- 后续可增加“整图截图 + OCR 框输出”用于 Windows 校准

## 验收标准

满足以下条件即可视为 Windows 迁移完成：

1. 在 Windows 上能启动 `watch_and_submit.py`
2. 能正常打开官网、截图并识别邀请码文本
3. 能自动将邀请码填写到 `Wukong` 客户端并提交
4. 对“已领完 / 有误 / 失效”能识别为失败并继续等待
5. 成功提交后能停止监控并输出成功日志
