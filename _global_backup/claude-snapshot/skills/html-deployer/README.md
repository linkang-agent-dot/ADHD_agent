# HTML 内网部署 Skill

将 HTML、Markdown（.md）或项目文件夹部署到内网 demo 服务器，生成 `https://demo.tap4fun.com/...` 访问地址。MD 文件会先转为 HTML 再部署，页面含「下载 MD」按钮。

## 项目结构

```
html-deployer-skill/
├── SKILL.md
├── README.md
└── .gitignore
```

## 使用方式

在 Cursor 中说关键词触发，Skill 直接执行 `SKILL.md` 内联命令（不创建脚本），零依赖。

**触发词**：`发布到 demo`、`部署到 demo`、`上传到 demo`、`生成预览地址`、`生成地址`、`生成链接`、`生成 URL`

**行为**：单文件 → 重命名为 index.html；.md → 转 HTML 后部署；目录 → 打包 tar.gz；需构建项目 → 自动修复 base 为 `./`

**非内网**：优先本机执行；或替换 `UPLOAD_SERVER` 为可访问入口；弱网可加 `--max-time`。
