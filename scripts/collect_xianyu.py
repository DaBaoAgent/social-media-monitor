"""闲鱼数据采集器"""
import os, sys, json, time, re
os.environ['PYTHONUTF8'] = '1'
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

CF = os.path.expanduser(r"~\.hermes\skills\crosspost\scripts\xianyu_cookies.json")
with open(CF, 'r', encoding='utf-8') as f:
    COOKIES = json.load(f)
if isinstance(COOKIES, dict) and 'cookies' in COOKIES:
    COOKIES = COOKIES['cookies']

def parse_stats(body):
    flat = body.replace('\n', '|')
    stats = {"fans": "0", "follows": "0", "items": "0", "nickname": ""}
    m = re.search(r'([^|]{2,30})\|[^|]+\|(\d+)粉丝\|(\d+)关注', flat)
    if m:
        stats['nickname'] = m.group(1).strip()
        stats['fans'] = m.group(2)
        stats['follows'] = m.group(3)
    m = re.search(r'宝贝[^\d]*(\d+)', flat)
    if m: stats['items'] = m.group(1)
    return stats

accounts = [
    ("大宝", "https://m.tb.cn/h.RduQQ6G?tk=qyFY5GfsUy6"),
    ("工厂直租", "https://m.tb.cn/h.RXcbvDE?tk=VkYq5GfvO8z"),
]
result = {"platform": "闲鱼", "time": time.strftime("%Y-%m-%d %H:%M"), "accounts": {}}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
    context = browser.new_context(viewport={'width': 1280, 'height': 900},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
    context.add_cookies(COOKIES)
    for name, link in accounts:
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined}); window.chrome = { runtime: {} };")
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

output = os.path.expanduser(r"~\.hermes\data\xianyu_dashboard.json")
os.makedirs(os.path.dirname(output), exist_ok=True)
with open(output, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
for n, a in result["accounts"].items():
    e = a.get("error","")
    if e: print(f"  {n}: {e}")
    else: print(f"  {n}: {a.get('nickname','?')} 粉丝:{a['fans']} 关注:{a['follows']} 宝贝:{a['items']}")
