---
name: igame-player-udid
description: Query player UDID from iGame DEV by userId. Use when the user asks to find player udid/device id and provides a userId for X3/DEV.
---

# iGame Player UDID Query

## Scope

- This skill only handles player UDID lookup.
- Input is a player `userId` (numeric string).
- Output is `udid` plus quick context (`serverId`, `serverName`, `userName`).

## Default behavior

- Use DEV gateway: `https://ms-inner-gateway-dev.tap4fun.com`.
- Use X3 defaults: `gameid=1090`, `regionid=201`.
- Query endpoint: `GET /ark/game/players`.

## Authentication source priority

1. Explicit CLI args (`--token`, `--clientid`)
2. Local auth file: `~/.igame-auth.json` (`token`, `clientId`)

## Execution command

```bash
python C:/Users/linkang/.claude/skills/igame-player-udid/scripts/get_udid.py --user-id 26907
```

Optional overrides:

```bash
python C:/Users/linkang/.claude/skills/igame-player-udid/scripts/get_udid.py --user-id 26907 --gameid 1090 --regionid 201
```

## Expected output

- On success, print one JSON object:
  - `userId`
  - `udid`
  - `userName`
  - `serverId`
  - `serverName`
- If no record found, return non-zero with clear error.

## Agent behavior

When the user asks "查玩家 udid" and gives `userId`:

1. Run the command above.
2. Return only the matched player's UDID and minimal context.
3. If auth expired (`401`), ask user for latest browser token/clientid or refresh login.
