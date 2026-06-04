---
name: unity-icon-extraction
description: 从 Unity 编辑器截图中提取图标资源并归档到 KB 的标准流程
metadata: 
  node_type: memory
  type: workflow
  originSessionId: 6f0b17ad-f15e-4a1c-94e0-088fe37592f0
---

# Unity 图标提取与归档流程

## 适用场景
- 需要从 Unity 编辑器的 Inspector 预览窗口中提取图标/Sprite 资源
- 图标可能在图集中，无法直接从文件系统定位
- 需要将提取的资源归档到项目 KB 中

## 标准流程（全自动）

### 触发条件
- 用户提供 Unity Inspector 预览窗口截图
- 提到"提取图标"、"复制图标"、"归档"、"保存这个图标"
- 或直接说"这个图标"、"这个资源"、"把这个复制出来"

### 自动执行（无需确认）
1. **项目识别**：从对话上下文或用户明确提到的项目关键词判断（P2/X2/X3）
2. **图标命名**：从截图 Inspector 信息或用户描述中提取资源名称
3. **图标裁剪**：自动裁剪预览区域，去掉底部文字
4. **直接归档**：保存到 `KB/产出-本地化与美术/{项目}/UI图标/`
5. **无中间文件**：不经过桌面或临时目录

### 实现代码

```python
from PIL import Image
import os

# 读取截图（从 .claude/image-cache）
img = Image.open(r'截图路径')
width, height = img.size

# 裁剪图标区域（去掉底部文字）
icon_height = int(height * 0.7)  # 根据实际调整比例
icon = img.crop((0, 0, width, icon_height))

# 自动确定项目和路径
project = "X3"  # 从对话上下文或用户明确的项目关键词判断
icon_name = "icon_global_integral"  # 从截图或用户描述提取

# 确保目录存在
kb_path = f"C:\\ADHD_agent\\KB\\产出-本地化与美术\\{project}\\UI图标"
os.makedirs(kb_path, exist_ok=True)

# 直接保存到 KB（无中间文件）
output_path = os.path.join(kb_path, f"{icon_name}.png")
icon.save(output_path)
print(f"已保存到: {output_path}")
```

### 3. 资源归档路径规范

**X3 项目**：
```
C:\ADHD_agent\KB\产出-本地化与美术\X3\UI图标\
```

**P2 项目**：
```
C:\ADHD_agent\KB\产出-本地化与美术\P2\UI图标\
```

**X2 项目**：
```
C:\ADHD_agent\KB\产出-本地化与美术\X2\UI图标\
```

### 4. 关键原则

**禁止中间产出文件**：
- ❌ 不要先保存到桌面再移动
- ✅ 直接保存到 KB 目标路径
- 如果已经产生桌面临时文件，提取后立即删除

**命名规范**：
- 保持 Unity 中的原始资源名称
- 格式：`{资源名称}.png`
- 示例：`icon_global_integral.png`

## 实战案例

**案例 1：X3 全球积分图标提取**（2026-05-25）
- 源资源：Unity Inspector 预览 `icon_global_integral`（256x256）
- 截图尺寸：148x149
- 提取命令：裁剪上部 70% 区域
- 最终路径：`C:\ADHD_agent\KB\产出-本地化与美术\X3\UI图标\icon_global_integral.png`
- 提取尺寸：148x104

## 注意事项

1. **尺寸问题**：截图预览窗口的尺寸可能小于原始资源，如需高清版本需从 Unity 中导出原图
2. **图集资源**：如果图标在 Atlas 中，文件系统搜索会失败，截图提取是最快方式
3. **裁剪比例**：根据预览窗口底部文字高度调整裁剪比例（通常 0.7-0.8）
4. **路径检查**：提取前确保目标目录存在，使用 `mkdir -p` 创建

## 触发词
- "提取图标"、"复制图标"、"导出图标"
- "Unity 截图提取"
- "归档到 KB"、"保存到 KB"
