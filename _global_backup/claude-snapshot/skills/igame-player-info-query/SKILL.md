---
name: igame-player-info-query
description: Query iGame player basic info by serverId and userId from player info page context (e.g. /info/player/3200/27438). Use for X3 DEV player lookup, account status checks, device/udid checks, and quick profile verification.
---

# iGame Player Info Query

## Scope

- Query player details with `serverId + userId`.
- Primary use case: iGame player page URL like `/info/player/402/27438`.
- Read-only query only.

## Default behavior

- If environment is not specified, use `dev` (DEV gateway).
- X3 defaults: `gameid=1090`, `regionid=201`.
- Endpoint: `GET /ark/game_info/{userId}/basic?serverId={serverId}`.

## Authentication source priority

1. Explicit CLI args (`--token`, `--clientid`)
2. Local auth file `~/.igame-auth.json` (`token`, `clientId`)

## Execution command

```bash
python C:/Users/linkang/.claude/skills/igame-player-info-query/scripts/get_player_info.py --server-id 3200 --user-id 27438
```

Optional overrides:

```bash
python C:/Users/linkang/.claude/skills/igame-player-info-query/scripts/get_player_info.py --player-url "https://igame-dev.tap4fun.com/#/info/player/3200/27438"
python C:/Users/linkang/.claude/skills/igame-player-info-query/scripts/get_player_info.py --server-id 3200 --user-id 27438 --env dev --gameid 1090 --regionid 201
python C:/Users/linkang/.claude/skills/igame-player-info-query/scripts/get_player_info.py --server-id 3200 --user-id 27438 --raw
```

## Expected output

- Default output is a compact JSON object with:
  - `userId`, `userName`
  - `serverId`, `serverName`
  - `playerLevel`, `mainCastleLevel`, `power`
  - `vipLevel`, `totalCharge`
  - `lastLoginTime`
  - `registerUdid`, `loginUdid`
  - `accountStatus`, `chatStatus`
  - `accountId`, `characterId`
- `--raw` prints full API response payload.

## Agent behavior

When user provides player page link or says "查玩家信息":

1. Extract `serverId` and `userId` (from URL or text).
2. Execute the command above.
3. Return key player profile fields and any status/risk clues.
4. If auth expired (`401`), ask user to refresh login or update token/clientId.
