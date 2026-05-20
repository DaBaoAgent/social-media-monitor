"""抖音数据采集器"""
import os, sys, json, time, re
os.environ['PYTHONUTF8'] = '1'
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

STATE_FILE = os.path.expanduser(r"~\.hermes\browser-profiles\douyin_state.json")

def parse_stats(body):
    flat = body.replace('\n', '|')
    stats = {"fans": "0", "liked": "0", "follows": "0", "posts": "0", "nickname": "", "douyin_id": ""}
    m = re.search(r'关注\|([\d.万w]+)\|粉丝\|([\d.万w]+)\|获赞\|([\d.万w]+)', flat)
    if m:
        stats['follows'] = m.group(1)
        stats['fans'] = m.group(2)
        stats['liked'] = m.group(3)
    m = re.search(r'作品\|(\d+)', flat)
    if m: stats['posts'] = m.group(1)
    m = re.search(r'抖音号[：:]\s*(\S+)', flat)
    if m: stats['douyin_id'] = m.group(1)
    return stats

accounts = [
    ("大宝", "64231236223", "https://v.douyin.com/FS1X9oK0V4M/"),
    ("工厂直租", "64762519553", "https://v.douyin.com/NMOoob6UBrQ/"),
]
result = {"platform": "抖音", "time": time.strftime("%Y-%m-%d %H:%M"), "accounts": {}}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
    context = browser.new_context(storage_state=STATE_FILE, viewport={'width': 1280, 'height': 900})
    for name, did, link in accounts:
        page = context.new_page()
        try:
            page.goto(link, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(5000)
            stats = parse_stats(page.evaluate('() => document.body.innerText'))
            stats['name'] = name
            result["accounts"][name] = stats
        except Exception as e:
            result["accounts"][name] = {"name": name, "error": str(e)[:200]}
        finally:
            page.close()
    browser.close()

output = os.path.expanduser(r"~\.hermes\data\douyin_dashboard.json")
os.makedirs(os.path.dirname(output), exist_ok=True)
with open(output, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
for n, a in result["accounts"].items():
    e = a.get("error","")
    if e: print(f"  {n}: {e}")
    else: print(f"  {n}: 粉丝:{a['fans']} 获赞:{a['liked']} 关注:{a['follows']} 作品:{a['posts']}")
