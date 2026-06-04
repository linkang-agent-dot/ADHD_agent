# iGame Activity Deploy Reference

## Endpoints

### 1. 查询活动配置列表（搜索 activityConfigId）

- URL: `https://ms-inner-gateway-dev.tap4fun.com/ark/activity/query?refresh=true`
- Method: `GET`
- 返回全量活动配置（~878 条），字段: `id` / `cn` / `en`
- `id` 即 `activityConfigId`，按 `cn` 关键字匹配活动名称

### 2. 部署/开启活动

- URL: `https://ms-inner-gateway-dev.tap4fun.com/ark/activity/submit`
- Method: `POST`

## Required headers

- `authorization: Bearer <token>`
- `clientid: <clientId>`
- `gameid: 1090` (X3)
- `regionid: 201`
- `content-type: application/json`
- `origin: https://igame-dev.tap4fun.com`
- `referer: https://igame-dev.tap4fun.com/`

## Common errors

- `401 请登录`: token expired or wrong login context
- `ark_error_10018 没有权限`: account lacks permission for this API or wrong gateway/game scope
- `请求参数验证错误`: payload schema or field values invalid

## Getting latest valid auth quickly

1. Open `https://igame-dev.tap4fun.com`
2. DevTools -> Network -> trigger one real deploy
3. Copy as cURL (bash)
4. Use the latest `authorization` and `clientid` from that request
