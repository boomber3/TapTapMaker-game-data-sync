#\!/usr/bin/env python3
"""
json_to_lua.py - Convert game-exported JSON to a Lua embedded module.

Usage:
    python3 json_to_lua.py <input_json> <output_lua> [comment]

Examples:
    python3 json_to_lua.py docs/Levelconfig.json scripts/DefaultLevel.lua
    python3 json_to_lua.py docs/Characters.json  scripts/CharacterData.lua "角色属性表"
    python3 json_to_lua.py docs/Items.json       scripts/ItemDB.lua "道具数据库"
"""

import json, sys, os, re
from datetime import datetime


def _lua_key(k):
    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', k):
        return k
    return '["' + k.replace('\\', '\\\\').replace('"', '\\"') + '"]'


def _to_lua(value, indent=0):
    pad       = "    " * indent
    inner_pad = "    " * (indent + 1)

    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return "{:.10g}".format(value)
    if isinstance(value, str):
        esc = (value
               .replace('\\', '\\\\')
               .replace('"',  '\\"')
               .replace('\n', '\\n')
               .replace('\r', '\\r'))
        return '"' + esc + '"'
    if isinstance(value, list):
        if not value:
            return "{}"
        lines = [inner_pad + _to_lua(item, indent + 1) + "," for item in value]
        return "{\n" + "\n".join(lines) + "\n" + pad + "}"
    if isinstance(value, dict):
        if not value:
            return "{}"
        lines = [inner_pad + _lua_key(str(k)) + " = " + _to_lua(v, indent + 1) + ","
                 for k, v in value.items()]
        return "{\n" + "\n".join(lines) + "\n" + pad + "}"
    return '"' + str(value) + '"'


def convert(input_path, output_path, comment=None):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    saved_at = ""
    if isinstance(data, dict) and "savedAt" in data:
        saved_at = "  (导出时间: " + str(data["savedAt"]) + ")"

    sync_time   = datetime.now().strftime("%Y-%m-%d %H:%M")
    module_name = os.path.splitext(os.path.basename(output_path))[0]
    desc        = comment if comment else module_name

    header = (
        "-- {desc} -- 由游戏内编辑器导出并自动生成\n"
        "-- 源文件: {src}\n"
        "-- 同步时间: {time}{saved_at}\n"
        "-- 此文件由脚本生成，请勿手动编辑。如需更新请重新同步。\n"
    ).format(desc=desc, src=os.path.basename(input_path),
             time=sync_time, saved_at=saved_at)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header + "return " + _to_lua(data, indent=0) + "\n")

    print("[OK] {} -> {}".format(input_path, output_path))
    if isinstance(data, dict):
        print("     顶层字段: " + ", ".join(list(data.keys())[:8]))
    elif isinstance(data, list):
        print("     数组长度: {}".format(len(data)))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 json_to_lua.py <input_json> <output_lua> [描述注释]")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) >= 4 else None)
