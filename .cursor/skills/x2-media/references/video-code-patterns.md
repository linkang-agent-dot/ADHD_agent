# 视频集成 C# 代码模板

三种视频集成场景的代码模板、VideoRoot 路径对照表和参数速查。

---

## VideoRoot 路径对照表

| UI / Prefab | VideoRoot 路径 | StaticImage / 封面路径 | 说明 |
|---|---|---|---|
| Bubble 气泡 | `VideoRoot/MediaPlayer` | `VideoRoot/StaticImage` | 基类控制 |
| UIUnionBossMain | `BG/Stage/VideoRoot/MediaPlayer` | `BG/Stage/StaticImage` | 联盟 Boss 主界面 |
| UIUnionBossPop | `CenterOther/VideoRoot/MediaPlayer` | `CenterOther/Banner` | 联盟 Boss 弹窗 |
| UIActivityMain | `Animation/VideoRoot/MediaPlayer` | `Animation/Banner` 或 `Animation/StaticImage` | 活动主界面 |
| 直接挂载 | `MediaPlayer`（无父节点） | 无 | 简单场景 |

QuickPlayer 路径规则：将 `MediaPlayer` 替换为 `QuickPlayer`。

---

## 场景 A：Bubble 气泡

### 类名推断

| 输入 | 规则 | 示例 |
|------|------|------|
| prefab 名称 | `MenuBubbleXxx` | `MenuBubbleMeteorRobbed` |
| 对应类名 | 加 `Main` 前缀 | `MainMenuBubbleMeteorRobbed` |
| 文件路径 | `Assets/x2/Runtime/UI/BubbleInstances/{类名}.cs` | |

### 代码模板（新建）

模板文件：`templates/BubbleVideoPlayer.cs.template`

```csharp
namespace Logic
{
    public class {类名} : MainMenuBubbleVideoPlayerBase
    {
        protected override string VideoPath => "{VideoPath}";
        protected override string VideoCoverPath => "{VideoCoverPath}";
    }
}
```

若文件已存在，仅更新 VideoPath 和 VideoCoverPath 属性值。

---

## 场景 B：已有 UI 添加视频

### 前置检测

1. 读取目标 UI 脚本，确认继承基类
2. 读取目标 prefab 层级，推断 VideoRoot 相对路径
3. 检测是否已有 StaticImage / Banner 封面节点
4. 检查脚本中是否已有视频相关代码（避免重复）

### 必须添加的 using

```csharp
using System.Threading;  // CancellationTokenSource, CancellationToken
using Render;             // MediaPlayerControl, UIAreaVideoPlayer, VideoPlayerData, VideoDef
```

### 必须添加的字段

```csharp
private GameObject m_GoVideoRoot;
private UIAreaVideoPlayer m_VideoPlayer;
private CancellationTokenSource m_VideoPlayCts;
private TFWImage m_VideoMaskImage;
private GameObject m_GoStaticImage;  // 或 m_GoBanner
```

### 三段式代码

**OnLoad() 中添加**：

```csharp
m_GoVideoRoot = MediaPlayerControl.UseAVPro
    ? UIHelper.GetChild(gameObject, "{VideoRoot路径}/MediaPlayer")
    : UIHelper.GetChild(gameObject, "{VideoRoot路径}/QuickPlayer");
m_VideoPlayer = new UIAreaVideoPlayer(new UIData() { gameObject = m_GoVideoRoot });
m_GoVideoRoot.transform.parent.TryGetComponent<TFWImage>(out m_VideoMaskImage);
m_GoStaticImage = UIHelper.GetChild(gameObject, "{StaticImage路径}");
```

**OnShown() 中添加**：

```csharp
PlayBgVideo();
```

**OnHidden() 中添加**：

```csharp
m_VideoPlayer?.StopVideo();
m_VideoPlayCts?.Cancel();
m_VideoPlayCts?.Dispose();
m_VideoPlayCts = null;
```

**新增方法**（PlayBgVideo + PlayVideoAsync + HideVideoStaticImage）：

```csharp
#region 背景视频播放

private void PlayBgVideo()
{
    m_VideoPlayCts?.Cancel();
    m_VideoPlayCts?.Dispose();
    m_VideoPlayCts = new CancellationTokenSource();

    m_GoStaticImage?.TrySetActive(true);

    if (m_VideoMaskImage != null)
    {
        var c = m_VideoMaskImage.color;
        m_VideoMaskImage.color = new Color(c.r, c.g, c.b, 0);
    }

    if (m_VideoPlayer != null)
    {
        PlayVideoAsync(m_VideoPlayCts.Token).Forget();
    }
}

private async UniTaskVoid PlayVideoAsync(CancellationToken token)
{
    if (m_VideoPlayer == null) return;

    var playerData = new VideoPlayerData
    {
        m_UrlPath = VideoDef.VideoUrl("{VideoPath}"),
        m_IsLoop = true,
        m_ForcePlay = true,
        m_ClickShowSkip = false,
        m_IsTransparentVideo = false,
        m_FirstReadyCallback = () =>
        {
            HideVideoStaticImage().Forget();
        },
    };
    m_VideoPlayer.StopVideo();

    try
    {
        await UniTask.DelayFrame(5, cancellationToken: token);
    }
    catch (OperationCanceledException)
    {
        return;
    }

    if (!IsActive) return;
    if (!m_GoVideoRoot.transform.parent.gameObject.activeInHierarchy) return;

    m_VideoPlayer.DoPlay(playerData);
}

private async UniTaskVoid HideVideoStaticImage()
{
    try
    {
        await UniTask.Delay(100);
        m_GoStaticImage?.TrySetActive(false);

        if (m_VideoMaskImage != null)
        {
            var c = m_VideoMaskImage.color;
            m_VideoMaskImage.color = new Color(c.r, c.g, c.b, 1.0f / 255);
        }
    }
    catch (OperationCanceledException)
    {
    }
}

#endregion
```

---

## 场景 C：配置驱动

不自动生成代码，仅提供建议：

```csharp
var videoPath = VideoDef.VideoUrl(cfg.VideoPath);
```

建议配置表字段：`VideoPath`（string）、`VideoCover`（string，可选）。

---

## VideoPlayerData 参数速查

| 参数 | 类型 | 背景视频 | 气泡 SBS | 过场 CG |
|------|------|---------|---------|---------|
| m_UrlPath | string | VideoDef.VideoUrl(...) | 同左 | 同左 |
| m_IsLoop | bool | true | true | false |
| m_ForcePlay | bool | true | true | false |
| m_ClickShowSkip | bool | false | false | true |
| m_IsTransparentVideo | bool | false | true | false |
| m_FirstReadyCallback | Action | 隐藏封面 | 隐藏封面 | 可选 |
| m_PlayEndCallback | Action\<bool\> | 不需要 | 不需要 | 关闭UI/继续 |

---

## CancellationToken 生命周期（必须遵循）

```
PlayBgVideo():  Cancel 旧 CTS → Dispose 旧 CTS → new CTS → 传入 PlayVideoAsync
OnHidden():     StopVideo → Cancel → Dispose → 设为 null
```

**禁止**：
- 只 Cancel 不 Dispose（内存泄漏）
- 不判断 IsActive 就 DoPlay（已关闭 UI 重播）
- FirstReadyCallback 中做重操作
- PlayVideoAsync 中不 catch OperationCanceledException
