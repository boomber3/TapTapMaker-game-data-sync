---
name: taptapmaker-game-data-sync
description: |
  将开发者在 UrhoX 游戏内编辑器中创作的数据同步到项目代码中。适用于以下场景：
  (1) 用户说"为我同步关卡数据"、"配置关卡 JSON"、"更新关卡"、"导入我的关卡"
  (2) 用户提供了 @Levelconfig.json 或粘贴了关卡 JSON 文本
  (3) 用户反馈关卡在游戏中显示为空白
  (4) 用户需要将游戏内编辑的角色属性、道具数据库、波次配置、对话脚本等数据同步到项目
  核心工作：把 JSON 数据转换为 Lua 嵌入模块（scripts/XxxData.lua），
  并确保游戏通过 require("XxxData") 加载，而非 File:ReadString()。
---

# TapTap Maker 游戏数据同步

## 背景：为什么不能直接读 JSON 文件

UrhoX 运行在 WASM 沙箱中，File:ReadString() 读取的是 Urho3D 内部长度前缀二进制格式，
无法读取普通 JSON 文本文件。直接用 File API 读 JSON 会静默失败，导致数据为空。

解决方案：将 JSON 转换为 Lua table，以 require("XxxData") 方式嵌入运行时。

## 工作流程（4 步）

### 步骤 1 — 在游戏内导出数据到剪贴板

在游戏的开发者/编辑器模式中，将当前数据序列化为 JSON 并写入剪贴板：

```lua
local function exportToClipboard()
    local data = serializeCurrentData()
    local jsonStr = cjson.encode(data)
    ui.useSystemClipboard = true
    ui:SetClipboardText(jsonStr)
    print("[导出] 已复制到剪贴板")
end
```

### 步骤 2 — 将 JSON 存入 docs/ 目录

粘贴剪贴板内容，保存为项目文档：

```
docs/
└── XxxConfig.json    # 游戏导出的原始数据（源文件，可 git 追踪）
```

若用户直接在对话中粘贴 JSON，Claude 代为写入对应 docs/ 文件。

### 步骤 3 — 运行转换脚本

```bash
python3 TapTapMaker-game-data-sync/scripts/json_to_lua.py \
    docs/XxxConfig.json \
    scripts/XxxData.lua
```

脚本将任意 JSON 结构转换为合法 Lua table，自动处理特殊 key 引号。

### 步骤 4 — 游戏端用 require() 加载

```lua
function LoadData()
    local ok, data = pcall(require, "XxxData")
    if not ok or not data then
        print("[数据] 加载失败: " .. tostring(data))
        return
    end
    applyData(data)
    print("[数据] 加载成功")
end
```

调用 UrhoX MCP build 工具构建后预览验证。

## 关键约定

| 文件 | 用途 |
|------|------|
| docs/XxxConfig.json | 游戏导出的原始 JSON（源文件，可追踪） |
| scripts/XxxData.lua | 转换后的 Lua 模块（构建产物，勿手动编辑） |

禁止使用（静默失败）：

```lua
-- File:ReadString() 读不到 JSON 内容
local f = File("config.json", FILE_READ)
local jsonStr = f:ReadString()  -- 返回空字符串
```

必须使用：

```lua
local ok, data = pcall(require, "XxxData")
```

## 各类数据示例

详见 references/examples.md，包含：关卡地图、角色属性、道具数据库、波次配置、对话脚本。
