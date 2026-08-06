# Unity MCP eval 未解析继承的 Singleton Instance

- 日期：2026-08-06
- 场景：客户端反查 TGS 邮箱总数/未读数。
- 错误：直接 eval `TFW.TgsHelper.Instance.GetBoxTotalNum(4)`。
- 结果：MissingMemberException，提示 `TgsHelper.Instance` 不存在。
- 原因：`Instance` 定义在泛型 Singleton 基类，MCP 轻量反射没有按该静态继承链解析。
- 正确做法：改用 invoke-chain/feval 变量方式，或直接走真实邮箱 UI；不要据此误判客户端没收到邮件。
- 防复发：MCP 访问继承来的静态单例属性失败时换调用通道，不把反射限制当业务结果。
