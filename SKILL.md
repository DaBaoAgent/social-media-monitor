---
name: mediapulse
description: "MediaPulse — 佳康顺三平台六账号新媒体数据脉搏。每日3次自动采集粉丝/获赞/贴文数，生成趋势报告推送QQ Bot。"
version: 1.0.0
icon: "📊"
platforms: [windows]
tags: [analytics, social-media, dashboard, monitoring, douyin, xiaohongshu, xianyu]
---

# MediaPulse — 新媒体数据脉搏

> 佳康顺康复辅具三平台（小红书/抖音/闲鱼）六账号数据监控系统。
> 每日 7:30 / 11:30 / 18:30 自动采集 → 推送到 QQ Bot。

---

## 监控矩阵

| 平台 | 账号 | ID |
|:-----|:-----|:---|
| 小红书 | 昆山轮椅租赁大宝 | 95392884153 |
| 小红书 | 昆山工厂轮椅直租 | 95480619590 |
| 抖音 | 昆山轮椅租赁（大宝） | 64231236223 |
| 抖音 | 昆山工厂轮椅直租 | 64762519553 |
| 闲鱼 | 昆山轮椅租赁大宝 | userId:2048277942 |
| 闲鱼 | 昆山工厂轮椅直租 | userId:2919374497 |

### 监控指标

| 指标 | 小红书 | 抖音 | 闲鱼 |
|------|:-----:|:----:|:----:|
| 粉丝数 | ✅ | ✅ | ✅ |
| 获赞总数 | ✅ | ✅ | — |
| 内容数 | ✅ 笔记 | ✅ 作品 | ✅ 宝贝 |
| 近5篇互动 | ✅ | ⏳ | ⏳ |

---

## 技术架构

```
mediapulse/
├── SKILL.md
├── scripts/
│   ├── collect_xhs.py       # 小红书: urllib + Cookie → __INITIAL_STATE__ JSON
│   ├── collect_douyin.py    # 抖音: Playwright headless + storage_state → 管道解析
│   ├── collect_xianyu.py    # 闲鱼: Playwright + Cookie注入 + 反检测
│   └── collect_all.py       # 汇总入口 → dashboard.json
└── references/
    ├── scraping-techniques.md  # 三平台采集技术详解（管道分隔/反检测/INITIAL_STATE）
    ├── xhs-collection-guide.md
    └── douyin-xianyu-collection-exploration.md
```

### 采集原理速查

| 平台 | 用时 | 技术栈 |
|------|:---:|--------|
| 小红书 | ~1s | Python urllib + Cookie → 正则提取 INITIAL_STATE |
| 抖音 | ~14s | Playwright headless → 管道分隔正则 |
| 闲鱼 | ~8s | Playwright + Cookie注入 + webdriver抹除 |

---

## 使用方式

### Cron 定时（已配置）
- 任务 ID: `7e2ddfec2e72`
- 时间: 每天 7:30 / 11:30 / 18:30
- 推送: QQ Bot

### Agent 手动运行
```python
import subprocess
python_exe = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe"
script = r"C:\Users\Administrator\.hermes\skills\mediapulse\scripts\collect_all.py"
subprocess.run([python_exe, script], capture_output=True, text=True, timeout=180)
# 读取 ~/.hermes/data/dashboard.json
```

### 单平台采集
```bash
python scripts/collect_xhs.py      # 小红书
python scripts/collect_douyin.py   # 抖音
python scripts/collect_xianyu.py   # 闲鱼
```

---

## 前置依赖

- Python 3.12+ with `xhs`, `playwright`
- Playwright Chromium installed
- Cookie: `~/.hermes/skills/crosspost/scripts/xhs_cookie.txt`
- Cookie: `~/.hermes/skills/crosspost/scripts/xianyu_cookies.json`
- 登录态: `~/.hermes/browser-profiles/douyin_state.json`

---

## 输出格式

`dashboard.json`:
```json
{
  "dashboard_time": "2026-05-20 15:28",
  "platforms": {
    "小红书": {"accounts": {"大宝": {"fans":"2","liked_total":"4","note_count":5}}},
    "抖音": {"accounts": {"大宝": {"fans":"11","liked":"43","posts":"21"}}},
    "闲鱼": {"accounts": {"大宝": {"fans":"6","items":"22"}}}
  }
}
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-05-20 | 初始版本。三平台采集全部跑通，Cron 已配置。 |

## 关联技能

- `crosspost` — 三平台图文发布（共享 Cookie/登录态）
- `context-mode` — 上下文优化
