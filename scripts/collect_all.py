"""
MediaPulse 三平台全量数据采集器
汇总小红书/抖音/闲鱼 → dashboard.json
"""
import subprocess, os, json, time

PYTHON = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe"
SDIR = os.path.expanduser(r"~\.hermes\skills\mediapulse\scripts")
DDIR = os.path.expanduser(r"~\.hermes\data")
os.makedirs(DDIR, exist_ok=True)

results = {"dashboard_time": time.strftime("%Y-%m-%d %H:%M"), "platforms": {}}
platforms = [
    ("小红书", "collect_xhs.py", "xhs_dashboard.json"),
    ("抖音", "collect_douyin.py", "douyin_dashboard.json"),
    ("闲鱼", "collect_xianyu.py", "xianyu_dashboard.json"),
]

for platform, script, fname in platforms:
    sp = os.path.join(SDIR, script)
    try:
        r = subprocess.run([PYTHON, sp], capture_output=True, text=True, timeout=120)
        fp = os.path.join(DDIR, fname)
        if os.path.exists(fp):
            with open(fp, 'r', encoding='utf-8') as f:
                results["platforms"][platform] = json.load(f)
        else:
            results["platforms"][platform] = {"error": f"Missing: {fname}"}
    except Exception as e:
        results["platforms"][platform] = {"error": str(e)[:200]}

with open(os.path.join(DDIR, "dashboard.json"), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

for platform, pdata in results["platforms"].items():
    err = pdata.get("error", "")
    if err:
        print(f"  {platform}: {err}")
        continue
    for name, acc in pdata.get("accounts", {}).items():
        e = acc.get("error", "")
        if e:
            print(f"  {platform} {name}: {e}")
        else:
            fans = acc.get('fans', '?')
            liked = acc.get('liked', acc.get('liked_total', '?'))
            content = acc.get('posts', acc.get('items', acc.get('note_count', '?')))
            print(f"  {platform} {name}: 粉丝:{fans} | 获赞:{liked} | 内容:{content}")
