// 롱폼 34편 각각의 스튜디오 분석(지난 28일: 조회수·시청시간·구독자)을 innerText로 수집
const { chromium } = require("D:/work/vibe-blog/node_modules/playwright");
const fs = require("fs");

const SCRATCH = "C:/Users/김영일/AppData/Local/Temp/claude/D--work/e701cbed-e977-472d-87ad-d2d75153c33d/scratchpad";
const vids = JSON.parse(fs.readFileSync(SCRATCH + "/longform_today.json", "utf8"))
  .filter(v => v.views_now !== null && v.views_now !== undefined);

(async () => {
  const ctx = await chromium.launchPersistentContext("D:/work/ai-singer/yt-auto/profile", {
    channel: "chrome", headless: false, viewport: null,
    args: ["--disable-blink-features=AutomationControlled", "--window-size=1400,900"],
  });
  const page = ctx.pages()[0] || (await ctx.newPage());
  page.setDefaultTimeout(30000);

  const out = [];
  for (let i = 0; i < vids.length; i++) {
    const v = vids[i];
    try {
      await page.goto(`https://studio.youtube.com/video/${v.id}/analytics/tab-overview/period-default`,
        { waitUntil: "domcontentloaded" });
      await page.waitForTimeout(7000);
      const text = await page.evaluate(() => document.body.innerText);
      out.push({ id: v.id, title: v.title, date: v.date, raw: text.slice(0, 5000) });
      console.log(`${i + 1}/${vids.length} ok ${v.id}`);
    } catch (e) {
      out.push({ id: v.id, title: v.title, date: v.date, error: e.message });
      console.log(`${i + 1}/${vids.length} ERR ${v.id} ${e.message}`);
    }
    fs.writeFileSync(SCRATCH + "/studio_metrics_raw.json", JSON.stringify(out, null, 1), "utf8");
  }
  await ctx.close();
  console.log("완료: " + out.length + "개");
})().catch(e => { console.error("오류:", e.message); process.exit(1); });
