# blender-fbx-render — Unity FBX 无头渲染预览图管线

把 Unity 工程里的 3D 建筑/道具 FBX 批量渲成 PNG 预览图（无需开 Unity）。
2026-07-09 P2 主城皮肤图库实战沉淀（53 款皮肤全量出图）。

## 依赖
- **Blender 4.2 portable**（本机未装，用时现下 ~380MB，解压即用）：
  `Invoke-WebRequest https://download.blender.org/release/Blender4.2/blender-4.2.3-windows-x64.zip -OutFile blender.zip`（走系统代理，PowerShell 可通，git-bash curl 不走代理会失败）
- **FBX2glTF.exe**（本目录已含，10MB）：兜底转换器，处理 Blender 导不了的 FBX

## 用法
```
blender.exe -b -P blender_render_skins.py -- [单个名字]   # 主批量脚本
blender.exe -b -P render_gaps.py                          # 失败款兜底（FBX2glTF 转 glb 再导）
```
脚本内改 ROOT / EXCLUDE / GAPS 即可换项目。输出 `renders/<名字>.png`（512px 透明底）。

## 五个必踩的坑（已在脚本里修好）
1. **Unity 贴图 alpha 是遮罩不是透明**：Blender 载入 TGA 后必须 `img.alpha_mode='CHANNEL_PACKED'`，否则 RGB 被 alpha 预乘 → 渲出来全黑。
2. **EEVEE 无头模式渲黑**：headless 没 GPU 上下文，灯光贴图全失效；必须用 `CYCLES` + `device='CPU'`（24 采样 512px 每个几秒，够快）。
3. **ASCII FBX Blender 拒导**（老美术资源常见）：`FBX2glTF -b -i x.fbx -o x` 转 glb 再 `import_scene.gltf`。
4. **带骨骼的 FBX 触发 Blender importer KeyError**（armature_setup bug）+ **`@aim` 后缀是动画文件不是模型**：跳过含 `@` 的 fbx，KeyError 的也走 glb 通道。
5. **`*Shadow.fbx` 是阴影面片不是模型**：文件名含 shadow 的一律跳过，否则渲出一张平地毯。

## 渲染前先查官方图标（map_dk_icons.py）——多数时候根本不用渲
P2 每个外显都有官方道具 ICON，渲染只是兜底。反查链：`Res\DisplayKey\Path_Prefab.asset`（key→prefab路径，按路径归到资源文件夹）→ `Path_Icon.asset`（同 key→图标路径）。图标可能在资源目录 / `UI\Sprite\ItemIcon\<key>.png` / 各 Gacha 活动 UI 目录。中文官方名在 `Editor\DisplayKey\Display_Prefab.asset` desc（unicode-escape，`encode('latin-1').decode('unicode_escape')` 解）。

## 材质绑定策略
FBX 导入后材质丢贴图引用，按名字匹配：材质名 → `{材质名}_Diffuse*.tga`（startswith → contains → 去 p2_ 前缀 → 全局第一张 Diffuse_High 兜底）。

## 配套（P2 主城皮肤图库那套）
scan_p2_cityskins.py（扫资源结构）→ collect_sprites.py（挖美术 Sprite PNG，认 .meta `textureType: 8`）→ make_final_thumbs.py（美术图优先/渲染兜底）→ gen_html.py（出图库网页）。
产出：`C:\ADHD_agent\KB\产出-本地化与美术\P2\主城皮肤图库\P2主城皮肤图库_资源结构全集.html`
