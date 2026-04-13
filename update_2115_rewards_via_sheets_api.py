import json
import os
import re
from pathlib import Path

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def load_rewards_updates(src_path: Path) -> list[dict]:
    """
    Build ValueRange updates that only target the reward column (G) of activity_task_QA.
    src_path is the captured gsheet_query output containing lines like:
      row 8421: <tsv...>
    """
    sheet = "activity_task_QA"
    reward_col = "G"

    updates: list[dict] = []
    with src_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.startswith("row "):
                continue
            m = re.match(r"^row (\d+): (.*)$", line)
            if not m:
                continue
            row_num = int(m.group(1))
            tsv = m.group(2)
            cols = tsv.split("\t")
            if len(cols) < 7:
                raise RuntimeError(f"Unexpected column count at row {row_num}: {len(cols)}")

            reward = cols[6]
            reward = reward.replace('"id":111110002,', '"id":111110305,')
            reward = reward.replace('"id":11119772,', '"id":11112500,')

            # Minify JSON to avoid whitespace surprises
            reward_obj = json.loads(reward)
            reward = json.dumps(reward_obj, ensure_ascii=False, separators=(",", ":"))

            updates.append(
                {
                    "range": f"{sheet}!{reward_col}{row_num}",
                    "values": [[reward]],
                }
            )

    old_left = [
        u
        for u in updates
        if "11119772" in u["values"][0][0] or "111110002" in u["values"][0][0]
    ]
    if old_left:
        raise RuntimeError(f"Old IDs still present in {len(old_left)} updates")
    return updates


def get_creds(token_path: Path, client_secret_path: Path | None) -> Credentials:
    """
    Prefer Application Default Credentials; fall back to local OAuth user flow.
    Token is stored under token_path for subsequent runs.
    """
    creds = None

    try:
        adc_creds, _ = google.auth.default(scopes=SCOPES)
        # If ADC gives us usable credentials, great.
        if adc_creds and adc_creds.valid:
            return adc_creds  # type: ignore[return-value]
        if adc_creds and hasattr(adc_creds, "refresh"):
            adc_creds.refresh(Request())
            return adc_creds  # type: ignore[return-value]
    except Exception:
        pass

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")
        return creds

    if not client_secret_path or not client_secret_path.exists():
        raise RuntimeError(
            "No usable Application Default Credentials found, and client_secret.json not provided.\n"
            "Please create/download an OAuth client secret JSON and set CLIENT_SECRET_PATH env var, "
            "or place client_secret.json next to this script."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def main() -> None:
    spreadsheet_id = "1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY"
    src_path = Path(
        r"C:\Users\linkang\.cursor\projects\c-ADHD-agent\agent-tools\0b00bf78-8d2b-4b25-aec3-8013bd928e85.txt"
    )

    # Token storage
    token_path = Path(r"C:\ADHD_agent\.cache\google\oauth_token.json")
    # OAuth client secret:
    # - Use env var if provided
    # - Else try C:\ADHD_agent\client_secret.json
    # - Else try local client_secret.json next to this script
    env_client_secret = os.environ.get("CLIENT_SECRET_PATH")
    candidates: list[Path] = []
    if env_client_secret:
        candidates.append(Path(env_client_secret))
    candidates.append(Path(r"C:\ADHD_agent\client_secret.json"))
    candidates.append(Path(__file__).with_name("client_secret.json"))

    client_secret_path = next((p for p in candidates if p.exists()), None)

    updates = load_rewards_updates(src_path)
    print(f"Prepared updates: {len(updates)}")
    print(f"First range: {updates[0]['range']}")

    creds = get_creds(token_path, client_secret_path)
    if hasattr(creds, "expired") and creds.expired and hasattr(creds, "refresh"):
        creds.refresh(Request())

    service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    body = {"valueInputOption": "RAW", "data": updates}
    resp = (
        service.spreadsheets()
        .values()
        .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
        .execute()
    )

    print(
        "Updated rows:",
        resp.get("totalUpdatedRows"),
        "cells:",
        resp.get("totalUpdatedCells"),
    )


if __name__ == "__main__":
    main()

