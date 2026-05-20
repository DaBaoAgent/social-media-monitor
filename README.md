# 📊 MediaPulse — 新媒体数据脉搏

<p align="center">
  <b>🤖 全自动三平台六账号新媒体数据监控系统</b><br>
  <sub>小红书 · 抖音 · 闲鱼 | 每日三次定时采集 | 一键推送 QQ</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/平台-小红书%20%7C%20抖音%20%7C%20闲鱼-ff2442?style=flat-square" alt="platforms">
  <img src="https://img.shields.io/badge/账号-6个-blue?style=flat-square" alt="accounts">
  <img src="https://img.shields.io/badge/采集-全自动-brightgreen?style=flat-square" alt="auto">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python" alt="python">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="license">
</p>

---

## 💡 这是什么？

**MediaPulse** 是专为新媒体运营打造的自动化数据看板。它能每天定时自动采集你在小红书、抖音、闲鱼三个平台上所有账号的核心数据——粉丝数、获赞数、贴文数、最近帖子互动情况——然后生成一份简洁的脉搏报告，推送到你的 QQ。

> 🔥 **不用每天手动截图看数据了。坐等消息就行。**

---

## 📈 实际数据预览

```
═══════════════════════════════════════
📊 MediaPulse 数据脉搏
🕐 2026-05-20 15:28
═══════════════════════════════════════

━━━ 🔴 小红书 ━━━
昆山轮椅租赁大宝     粉丝:2     获赞:4       笔记:5
昆山工厂轮椅直租     粉丝:2,312  获赞:21,274  笔记:5

━━━ 🟣 抖音 ━━━
昆山轮椅租赁（大宝）  粉丝:11    获赞:43      作品:21
昆山工厂轮椅直租     粉丝:1.8万  获赞:12      作品:19

━━━ 🟡 闲鱼 ━━━
昆山轮椅租赁大宝     粉丝:6     宝贝:22
昆山工厂轮椅直租     粉丝:2     宝贝:13
```

---

## 🎯 监控指标

| 指标 | 小红书 | 抖音 | 闲鱼 |
|------|:-----:|:----:|:----:|
| 📊 粉丝数 | ✅ | ✅ | ✅ |
| ❤️ 获赞总数 | ✅ | ✅ | — |
| 📝 内容数 | ✅ 笔记 | ✅ 作品 | ✅ 宝贝 |
| 🔍 近5篇互动 | ✅ | ⏳ 开发中 | ⏳ 开发中 |

---

## 🧬 技术架构

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  小红书采集  │    │   抖音采集    │    │  闲鱼采集    │
│  urllib+    │    │  Playwright  │    │  Playwright │
│  Cookie+    │    │  headless+   │    │  headless+  │
│  INITIAL_   │    │  storage_    │    │  Cookie注入  │
│  STATE解析  │    │  state       │    │  +反检测     │
└──────┬──────┘    └──────┬───────┘    └──────┬──────┘
       │                  │                    │
       └──────────────────┼────────────────────┘
                          ▼
                  ┌──────────────┐
                  │  collect_all │  ← 汇总入口
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │ dashboard.   │  ← JSON 数据
                  │    json      │
                  └──────┬───────┘
                         ▼
                  ┌──────────────┐
                  │   QQ Bot     │  ← 推送报告
                  └──────────────┘
```

| 平台 | 采集技术 | 单次耗时 | 核心原理 |
|------|---------|:------:|----------|
| 🔴 小红书 | Python urllib + Cookie | ~1s | 请求用户主页 → 解析 `__INITIAL_STATE__` JSON → 提取 interactions/notes |
| 🟣 抖音 | Playwright headless | ~14s | storage_state 登录态 → 短链接跳转用户主页 → 管道分隔正则解析 stat block |
| 🟡 闲鱼 | Playwright + Cookie注入 | ~8s | 注入18个Cookie + navigator.webdriver抹除 → 短链接跳转 → 正则解析 |
| **全量** | collect_all.py | **~27s** | 串行三平台 → 汇总 dashboard.json |

---

## ⚡ 快速开始

### 1. 安装依赖

```bash
pip install playwright xhs
playwright install chromium
```

### 2. 配置 Cookie / 登录态

```bash
# 小红书 Cookie
# 浏览器打开 creator.xiaohongshu.com → F12 → Application → Cookies
# 复制完整 Cookie 到 scripts/xhs_cookie.txt

# 抖音登录态
python scripts/douyin_login.py   # 弹出浏览器 → 扫码登录 → 自动保存

# 闲鱼 Cookie  
# 浏览器登录 goofish.com → 导出 Cookie JSON → scripts/xianyu_cookies.json
```

### 3. 修改监控账号

编辑各 `collect_*.py` 中的账号列表，填入你自己的账号信息。

### 4. 运行采集

```bash
# 全量采集三平台
python scripts/collect_all.py

# 或单平台采集
python scripts/collect_xhs.py      # 小红书
python scripts/collect_douyin.py   # 抖音
python scripts/collect_xianyu.py   # 闲鱼
```

### 5. 查看数据

```bash
cat examples/dashboard.json   # 或 ~/.hermes/data/dashboard.json
```

---

## ⏰ 定时任务（可选）

配合 Hermes Agent 的 cron 模块，每天自动运行三次：

```
7:30  → 早间数据脉搏
11:30 → 午间数据脉搏  
18:30 → 晚间数据脉搏
```

报告自动推送到 QQ Bot，无需手动查看。

---

## 📁 项目结构

```
MediaPulse/
├── README.md                   # 本文件
├── SKILL.md                    # 完整技术文档
├── scripts/
│   ├── collect_xhs.py          # 小红书采集器
│   ├── collect_douyin.py       # 抖音采集器
│   ├── collect_xianyu.py       # 闲鱼采集器
│   └── collect_all.py          # 全量汇总入口
└── examples/
    ├── dashboard.json          # 全量看板示例
    ├── xhs_dashboard.json      # 小红书数据示例
    ├── douyin_dashboard.json   # 抖音数据示例
    └── xianyu_dashboard.json   # 闲鱼数据示例
```

---

## 🔥 为什么开源这个项目？

新媒体运营最痛苦的不是写文案、拍视频，而是——**每天打开三四个 App，挨个截图看数据，手动复制到 Excel 里对比。**

MediaPulse 用不到 1000 行 Python 代码解决了这个问题：

- 🆓 **完全免费**，不需要任何付费 SaaS
- 🔒 **数据不出本地**，Cookie 只存在你自己的电脑上
- ⚡ **全自动**，配置一次，永久运行
- 📱 **推送即看**，数据自动发到 QQ，不用主动查看
- 🧩 **容易扩展**，增加新平台只需写一个采集器

---

## 🤝 贡献

本项目由 [DaBao](https://github.com/DaBaoAgent) 创建和维护。欢迎提 Issue 和 PR！

---

## 📜 License

MIT © 2026 DaBao
