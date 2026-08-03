# Effect Texture Samples

参考样本库。每张都是合规的 Unity 特效贴图（RGB=(255,255,255) + Alpha 蒙版 + 2^N 正方形），用于：

1. 首次生成时给 Agent 看一眼目标格式，校准对"白模贴图"的理解
2. `effect_texture_postprocess.py` 的回归测试基准

| 文件 | 源路径 | 形态 |
|------|-------|------|
| common_icon_CrossServer_Wonder2.png | 项目 Unity 客户端 `client/Assets/x3/Res/Effect/Textures/obj/` | 王冠纪念碑剪影，256×256，alpha 可见占比 33.9% |

新增样本时：只放**合规**的贴图（务必满足 RGB 全白 + Alpha 带形状 + 2^N），并在本表追加一行。
