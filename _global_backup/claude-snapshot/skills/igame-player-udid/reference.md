# iGame Player UDID Query Reference

## Endpoint

- Method: `GET`
- URL: `https://ms-inner-gateway-dev.tap4fun.com/ark/game/players`
- Query params:
  - `keywords=<userId>`
  - `type=1`
  - `pageIndex=1`
  - `pageSize=100`

## Required headers

- `authorization: Bearer <token>`
- `clientid: <clientId>`
- `gameid: 1090` (X3 default)
- `regionid: 201`
- `origin: https://igame-dev.tap4fun.com`
- `referer: https://igame-dev.tap4fun.com/`

## Response extraction

From `data[0]` read:

- `udid`
- `userId`
- `userName`
- `serverId`
- `serverName`

## Troubleshooting

- `401 请登录`: token expired; refresh login/token
- `success=false` with code: permission/scope issue
- `total=0` or empty data: userId not found under current game/region
