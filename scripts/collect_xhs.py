
"""
小红书数据采集器
用法: python collect_xhs.py
输出: ~/.hermes/data/xhs_dashboard.json
"""
import os, sys, json, re, urllib.request, ssl, gzip, time
os.environ['PYTHONUTF8'] = '1'
sys.stdout.reconfigure(encoding='utf-8')

def load_cookie():
    cookie_path = os.path.expanduser(r"~\.hermes\skills\crosspost\scripts\xhs_cookie.txt")
    return open(cookie_path, encoding='utf-8').read().strip()

COOKIE = load_cookie()

def scrape_user(uid, name):
    url = f"https://www.xiaohongshu.com/user/profile/{uid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": COOKIE,
    }
    ctx = ssl.create_default_context()
    ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        raw = resp.read()
        if resp.headers.get('Content-Encoding') == 'gzip':
            raw = gzip.decompress(raw)
        html = raw.decode('utf-8', errors='replace')
    
    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?})\s*</script>', html, re.DOTALL)
    if not match:
        return {"name": name, "error": "No INITIAL_STATE"}
    
    state = json.loads(match.group(1).replace('undefined', 'null'))
    upd = state["user"]["userPageData"]
    notes = state["user"]["notes"]
    
    interactions = upd.get("interactions", [])
    fans = follows = liked = "0"
    for i in interactions:
        t = i.get("type", "")
        if t == "fans": fans = i.get("count", "0")
        elif t == "follows": follows = i.get("count", "0")
        elif t == "interaction": liked = i.get("count", "0")
    
    recent = []
    for n in notes:
        nc = None
        if isinstance(n, list):
            for inner in n:
                if isinstance(inner, dict) and "noteCard" in inner:
                    nc = inner["noteCard"]; break
        elif isinstance(n, dict) and "noteCard" in n:
            nc = n["noteCard"]
        if nc:
            recent.append({
                "title": nc.get("displayTitle", "")[:50],
                "likes": nc.get("interactInfo", {}).get("likedCount", "0"),
                "note_id": n.get("id", "") if isinstance(n, dict) else "",
            })
        if len(recent) >= 5: break
    
    return {
        "name": name,
        "nickname": upd.get("basicInfo", {}).get("nickname", name),
        "red_id": upd.get("basicInfo", {}).get("redId", ""),
        "fans": fans,
        "follows": follows,
        "liked_total": liked,
        "note_count": len(notes),
        "recent_5": recent,
    }

# Collect
accounts = [
    ("67fd08c0000000000e013be3", "大宝"),
    ("67c2a9a9000000000e011363", "工厂直租"),
]

result = {"platform": "小红书", "time": time.strftime("%Y-%m-%d %H:%M"), "accounts": {}}
for uid, name in accounts:
    try:
        result["accounts"][name] = scrape_user(uid, name)
    except Exception as e:
        result["accounts"][name] = {"name": name, "error": str(e)[:200]}

output = os.path.expanduser(r"~\.hermes\data\xhs_dashboard.json")
os.makedirs(os.path.dirname(output), exist_ok=True)
with open(output, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"小红书数据采集完成: {output}")
for name, acc in result["accounts"].items():
    if "error" in acc:
        print(f"  {name}: ERROR - {acc['error']}")
    else:
        print(f"  {name}: {acc['nickname']} | 粉丝:{acc['fans']} | 获赞:{acc['liked_total']} | 笔记:{acc['note_count']}")
