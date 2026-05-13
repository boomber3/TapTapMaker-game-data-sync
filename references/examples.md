# 各类游戏数据同步示例

## 目录

1. 关卡地图（2D 平台跳跃）
2. 角色属性（RPG）
3. 道具数据库（背包系统）
4. 波次配置（塔防）
5. 对话脚本（剧情游戏）

---

## 1. 关卡地图（2D 平台跳跃）

docs/LevelConfig.json：
```json
{
  "name": "Level 1",
  "tilemap": [[1,1,1],[1,0,1],[1,1,1]],
  "spawnX": 1,
  "spawnY": 1
}
```

scripts/LevelData.lua（转换后）：
```lua
return {
    name = "Level 1",
    tilemap = {{1,1,1},{1,0,1},{1,1,1}},
    spawnX = 1,
    spawnY = 1
}
```

---

## 2. 角色属性（RPG）

docs/HeroConfig.json：
```json
{"name":"Warrior","hp":100,"attack":25,"skills":["slash","block"]}
```

scripts/HeroData.lua：
```lua
return {name="Warrior", hp=100, attack=25, skills={"slash","block"}}
```

---

## 3. 道具数据库（背包系统）

docs/ItemsConfig.json：
```json
{"items":[{"id":"sword_001","name":"铁剑","damage":15}]}
```

scripts/ItemsData.lua：
```lua
return {items={{id="sword_001", name="铁剑", damage=15}}}
```

---

## 4. 波次配置（塔防）

docs/WavesConfig.json：
```json
{"waves":[{"enemies":["goblin","goblin"],"interval":2.0}]}
```

scripts/WavesData.lua：
```lua
return {waves={{enemies={"goblin","goblin"}, interval=2.0}}}
```

---

## 5. 对话脚本（剧情游戏）

docs/DialogueConfig.json：
```json
{"scenes":[{"id":"intro","lines":[{"speaker":"老者","text":"世界需要你。"}]}]}
```

scripts/DialogueData.lua：
```lua
return {
    scenes = {
        {id="intro", lines={{speaker="老者", text="世界需要你。"}}}
    }
}
```

---

## 游戏端通用加载模式

```lua
local levelData    = require("LevelData")
local heroData     = require("HeroData")
local itemsData    = require("ItemsData")
local wavesData    = require("WavesData")
local dialogueData = require("DialogueData")
```
