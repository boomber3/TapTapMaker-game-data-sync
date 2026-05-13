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

# Pixel Level Sync

## 背景：为什么不能直接读 JSON 文件

UrhoX 运行在 WASM 沙箱中，`File:ReadString()` 读取的是 **Urho3D 内部长度前缀二进制格式**，
无法读取普通 JSON 文本文件。直接用 File API 读 JSON 会静默失败，导致关卡数据为空。

**解决方案**：将 JSON 转换为 Lua table，以 `require("DefaultLevel")` 方式嵌入运行时。

## 工作流程

### 1. 获取 JSON 数据

用户通过以下任一方式提供关卡数据：
- 游戏内开发者模式点击"导出到剪贴板"，粘贴到 `docs/Levelconfig.json`
- 直接在对话中粘贴 JSON 文本（Claude 写入 `docs/Levelconfig.json`）
- 使用 `@Levelconfig.json` 引用已有文件

JSON 格式（游戏导出标准格式）：
```json
{
  "completedLevels": 0,
  "savedAt": "2026-05-13 12:00",
  "boards": [
    { "row,col": 1, "row,col": 1 },
    {},
    {}
  ]
}
```
- key 格式：`"row,col"`（字符串，均从 0 开始）
- value：颜色索引整数（1 = PALETTE 中第 1 个颜色，通常为黑色）
- boards 数组长度 = 关卡数量，空 `{}` 表示该关卡无像素

### 2. 运行转换脚本

```bash
python3 /workspace/.agent/skills/pixel-level-sync/scripts/json_to_lua.py \
    docs/Levelconfig.json \
    scripts/DefaultLevel.lua
```

脚本自动：
- 按 row,col 排序像素条目（便于 diff 阅读）
- 写入关卡数量注释
- 保留 savedAt 时间戳

### 3. 确认游戏加载代码正确

`scripts/main.lua`（或主入口文件）中的加载函数必须是：

```lua
function LoadDefaultLevel()
    local ok, defaultData = pcall(require, "DefaultLevel")
    if not ok or not defaultData then
        print("[关卡] 加载内置关卡数据失败: " .. tostring(defaultData))
        return
    end
    deserializeState(defaultData)
    print("[关卡] 内置关卡加载成功")
end
```

**禁止使用的写法**（静默失败）：
```lua
-- ❌ 这样读不到 JSON 内容
local f = File("levels/default_levels.json", FILE_READ)
local jsonStr = f:ReadString()  -- 返回空字符串或乱码
```

### 4. 构建项目

调用 UrhoX MCP build 工具后预览验证。

## deserializeState 约定

同步脚本假设游戏状态结构为：
```lua
state = {
    completedLevels = 0,
    boards = { {}, {}, {} },  -- 每个 board 是 { ["row,col"] = colorIndex }
}
```

`deserializeState(data)` 需将 `data.boards` 和 `data.completedLevels` 写入 `state`。
若项目结构不同，需相应调整转换脚本的输出格式或 LoadDefaultLevel 的读取逻辑。

## 文件约定

| 文件 | 用途 |
|------|------|
| `docs/Levelconfig.json` | 开发者存放游戏导出的原始 JSON（源文件） |
| `scripts/DefaultLevel.lua` | 转换后的 Lua 嵌入模块（构建产物，勿手动编辑） |

## 扩展：多颜色支持

当前关卡 JSON 中 value 固定为 `1`（单色）。若游戏支持多色，value 为颜色索引：
```json
{ "5,3": 1, "5,4": 2, "5,5": 3 }
```
转换脚本无需修改，直接保留原始 value 值。
