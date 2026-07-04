# -*- coding: utf-8 -*-
# 6/27 롱폼 목록(조회수 스냅샷)과 오늘 실제 조회수를 비교해 최근 성장량을 계산
import re, json, sys, time, urllib.request

BASELINE = r"D:\work\ai-singer\yt-auto\롱폼_영상목록.txt"
OUT = r"C:\Users\김영일\AppData\Local\Temp\claude\D--work\e701cbed-e977-472d-87ad-d2d75153c33d\scratchpad\longform_today.json"

# 1) 베이스라인 파싱
txt = open(BASELINE, encoding="utf-8").read()
blocks = re.findall(
    r"\d+\. \[조회 ([\d,]+)\] (.+?)\n\s+ID\s+: (\S+)\n.+?\n\s+상태\s+: (\S+)\s+\|\s+날짜: (.+)",
    txt)
videos = []
for views, title, vid, vis, date in blocks:
    videos.append({
        "id": vid, "title": title.strip(),
        "views_0627": int(views.replace(",", "")),
        "vis_0627": vis, "date": date.strip(),
    })
print(f"베이스라인 {len(videos)}개 로드", file=sys.stderr)

# 2) 오늘 조회수 수집 (watch 페이지의 videoDetails.viewCount)
def fetch_views(vid):
    url = f"https://www.youtube.com/watch?v={vid}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Cookie": "CONSENT=YES+1",
    })
    html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
    m = re.search(r'"viewCount"\s*:\s*"(\d+)"', html)
    views = int(m.group(1)) if m else None
    lm = re.search(r'"likeCount"\s*:\s*"(\d+)"', html)
    likes = int(lm.group(1)) if lm else None
    dm = re.search(r'"lengthSeconds"\s*:\s*"(\d+)"', html)
    dur = int(dm.group(1)) if dm else None
    pm = re.search(r'"publishDate"\s*:\s*\{?"?simpleText"?:?"?([\d\-T:+]+)', html) or re.search(r'"publishDate"\s*:\s*"([^"]+)"', html)
    pub = pm.group(1) if pm else None
    return views, likes, dur, pub

for i, v in enumerate(videos):
    try:
        views, likes, dur, pub = fetch_views(v["id"])
        v["views_now"] = views
        v["likes"] = likes
        v["dur_sec"] = dur
        v["publish"] = pub
        print(f"{i+1}/{len(videos)} {v['id']} {views}", file=sys.stderr)
    except Exception as e:
        v["views_now"] = None
        v["error"] = str(e)
        print(f"{i+1}/{len(videos)} {v['id']} 오류 {e}", file=sys.stderr)
    time.sleep(0.4)

json.dump(videos, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장:", OUT, file=sys.stderr)

# 3) 요약 출력 (증가량 순)
ok = [v for v in videos if v.get("views_now") is not None]
for v in ok:
    v["delta"] = v["views_now"] - v["views_0627"]
ok.sort(key=lambda v: v["delta"], reverse=True)
print("\n=== 최근 7일 증가량 순 (6/27 → 7/4) ===")
for v in ok:
    print(f"+{v['delta']:>6,} | 총 {v['views_now']:>7,} | 좋아요 {v.get('likes') or 0:>4} | {v['date'][:12]} | {v['title'][:52]}")
