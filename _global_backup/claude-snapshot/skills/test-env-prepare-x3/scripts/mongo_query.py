#!/usr/bin/env python3
"""X3 Beta MongoDB 查询工具"""

import argparse
import json
import sys

from pymongo import MongoClient

MONGO_URI = "mongodb://root:M6D6YJLwPsC5RDZrpCmLx3jqaFeRp8Ye@x3-beta-nlb.a3games.com:27017/?directConnection=true&authSource=admin"


def get_client():
    return MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)


def get_db(server_id: int):
    return get_client()[f"gs_game_{server_id}"]


def query_player(server_id: int, player_id: int, fields: list[str] | None = None):
    db = get_db(server_id)
    projection = {f: 1 for f in fields} if fields else None
    player = db["ServerPlayer"].find_one({"_id": player_id}, projection)
    if not player:
        return {"error": f"玩家 {player_id} 不存在于 {server_id} 服"}
    return player


def list_collections(server_id: int):
    return sorted(get_db(server_id).list_collection_names())


def query_collection(server_id: int, collection: str, filter_doc: dict, limit: int = 10):
    db = get_db(server_id)
    results = list(db[collection].find(filter_doc).limit(limit))
    return results


def main():
    parser = argparse.ArgumentParser(description="X3 Beta MongoDB 查询")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("player", help="查询玩家数据")
    p.add_argument("--server", type=int, required=True)
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--fields", nargs="*", help="只返回指定字段")

    p = sub.add_parser("collections", help="列出数据库所有 collection")
    p.add_argument("--server", type=int, required=True)

    p = sub.add_parser("find", help="查询指定 collection")
    p.add_argument("--server", type=int, required=True)
    p.add_argument("--collection", required=True)
    p.add_argument("--filter", default="{}", help="MongoDB 查询 JSON")
    p.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()

    if args.cmd == "player":
        result = query_player(args.server, args.id, args.fields)
    elif args.cmd == "collections":
        result = list_collections(args.server)
    elif args.cmd == "find":
        result = query_collection(args.server, args.collection, json.loads(args.filter), args.limit)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, default=str, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
