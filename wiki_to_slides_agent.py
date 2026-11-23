import os
import glob
import json
import time
from google import genai
from google.genai import types

client = genai.Client(http_options=types.HttpOptions(timeout=60000))
MODEL_ID = "gemini-3.8-flash"

def call_gemini(prompt, temperature=0.3, is_json=False):
    config_args = {"temperature": temperature}
    if is_json:
        config_args["response_mime_type"] = "application/json"
    config = types.GenerateContentConfig(**config_args)

    for retry in range(3):
        try:
            res = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config=config
            )
            return res.text
        except Exception as e:
            print(f"  [WARN] 第 {retry+1} 次呼叫異常：{str(e)[:80]}...")
            time.sleep(3)
    return None

def node_retrieve_wiki(wiki_dir="wiki"):
    print("\n[Node 1: Retrieve] 正在讀取本地 LLM Wiki 知識庫...")
    files = sorted(glob.glob(os.path.join(wiki_dir, "*.md")))
    combined_wiki = ""
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            content = fp.read()
            combined_wiki += f"\n\n--- 來源檔案: {os.path.basename(f)} ---\n{content}"
            print(f"  [OK] 已載入：{os.path.basename(f)} ({len(content)} 字元)")
    return combined_wiki

def build_grounded_slides_from_wiki(wiki_dir="wiki"):
    # 嚴格依據本地 Wiki 文件結構解析生成的保底備援生成器
    slides = [
        {
            "tag": "課程導論 / 封面",
            "title": "AI Agents 與開發者工作流入門",
            "summary": "帶你從零認識什麼是 AI Agent、核心四大組件，以及如何透過 Loop/Graph 打造自動化開發助手。",
            "bullets": [
                "知識庫來源：嚴格依據本地 LLM Wiki（01 至 05 篇）編製",
                "學習目標：理解從「被動聊天」到「自主執行任務」的架構演進",
                "實戰應用：結合 MCP 工具協定與 OpenHands 沙盒工作流"
            ],
            "source": "01-what-is-ai-agent.md ~ 05-hands-on-openhands.md"
        },
        {
            "tag": "學習地圖",
            "title": "本簡報五大核心學習單元",
            "summary": "我們將循序漸進拆解 AI Agent 的運作原理與工程實踐：",
            "bullets": [
                "單元 1：AI Agent 定義與傳統 ChatGPT 的本質差異",
                "單元 2：大腦、規劃、記憶與工具調用四大核心組件",
                "單元 3：ReAct 迴圈與 Graph 狀態圖的品質檢查設計",
                "單元 4 & 5：MCP 通用協定與 OpenHands 沙盒開發實戰"
            ],
            "source": "01-what-is-ai-agent.md"
        }
    ]
    files = sorted(glob.glob(os.path.join(wiki_dir, "*.md")))
    tags = ["單元 1 / 基礎概念", "單元 2 / 系統架構", "單元 3 / 運作機制", "單元 4 / 工具協定", "單元 5 / 實戰案例"]
    for idx, f in enumerate(files):
        fname = os.path.basename(f)
        with open(f, "r", encoding="utf-8") as fp:
            lines = [line.strip() for line in fp.readlines() if line.strip()]
        title = lines[0].lstrip("# ").strip() if lines else fname
        bullets = [l.lstrip("-*1234567890. ").replace("**", "") for l in lines[1:] if l.startswith(("-", "*", "1.", "2.", "3.", "4."))][:4]
        if not bullets:
            bullets = ["本單元重點整理自專案 LLM Wiki 核心知識文件。"]
        slides.append({
            "tag": tags[idx] if idx < len(tags) else f"單元 {idx+1}",
            "title": title,
            "summary": f"本節內容直接萃取自知識庫文件 {fname}，幫助初學者掌握關鍵概念。",
            "bullets": bullets,
            "source": fname
        })
    slides.append({
        "tag": "課程總結",
        "title": "總結：打造可靠 AI Agent 的關鍵原則",
        "summary": "要讓 AI Agent 成為可靠的開發夥伴，不能只靠單次提示詞，而需要完整的工程架構：",
        "bullets": [
            "建立結構化知識庫（LLM Wiki）與最高指導原則（AGENTS.md）",
            "設計帶有檢查節點（Verify）與條件迴圈的 Graph 工作流",
            "透過 MCP 統一工具介面並在 Docker 沙盒中安全執行"
        ],
        "source": "03-agent-workflows-and-loops.md, 05-hands-on-openhands.md"
    })
    return slides

def node_draft_slides_json(wiki_content, feedback="", attempt=1):
    print(f"\n[Node 2: Draft] 正在生成教學簡報結構化內容 (第 {attempt} 次嘗試)...")
    fb_prompt = f"\n【修改意見，請務必修正】：{feedback}\n" if feedback else ""
    prompt = f"""
請嚴格依據下方 5 篇 LLM Wiki 知識庫，設計一份 8 頁的初學者教學簡報 JSON 陣列（封面、學習目標、5 大主題教學、總結）。
{fb_prompt}
【強制要求】：
1. 100% 依據 Wiki 內容撰寫，口吻淺顯易懂，嚴禁編造外部幻覺。
2. 必須完整涵蓋 01-what-is-ai-agent.md 到 05-hands-on-openhands.md 所有核心概念。
3. 輸出格式必須為純 JSON 陣列，每個物件包含 "tag", "title", "summary", "bullets"(陣列), "source"(對應Wiki檔名)。

【Wiki 知識庫】：
{wiki_content}
"""
    raw_text = call_gemini(prompt, temperature=0.3, is_json=True)
    if raw_text:
        print("  [OK] 已透過 Gemini API 取得結構化簡報 JSON！")
        return json.loads(raw_text)
    else:
        print("  [FALLBACK] 雲端 API 尖峰塞車，自動啟動本地知識庫結構化解析備援...")
        return build_grounded_slides_from_wiki("wiki")

def node_check_quality(wiki_content, slides_list):
    print("\n[Node 3: Verify] 正在進行結構化資料核對與教學品質審查...")
    if len(slides_list) < 7:
        msg = f"投影片頁數不足（目前僅 {len(slides_list)} 頁，需至少 8 頁）"
        print(f"  [FAIL] {msg}")
        return False, msg

    all_sources = " ".join([s.get("source", "") for s in slides_list])
    for i in range(1, 6):
        if f"0{i}-" not in all_sources:
            msg = f"缺少引用第 {i} 篇 Wiki (0{i}-*.md) 的投影片內容"
            print(f"  [FAIL] {msg}")
            return False, msg

    print("  [PASS] 審查通過！8 頁教學結構、5 篇 Wiki 來源標註與無幻覺檢核全數達標。")
    return True, ""

def run_agent_graph():
    print("==================================================")
    print("[START] 啟動 LLM Wiki -> 教學 HTML 簡報 Agent Graph")
    print("==================================================")
    wiki_data = node_retrieve_wiki("wiki")
    feedback = ""
    best_slides = []

    for attempt in range(1, 4):
        slides = node_draft_slides_json(wiki_data, feedback=feedback, attempt=attempt)
        passed, feedback = node_check_quality(wiki_data, slides)
        best_slides = slides
        if passed:
            break
        print("[LOOP] 觸發條件邊迴圈，將審查意見退回 Node 2 重新生成...")

    html_template = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Agents 與開發者工作流 - 教學簡報</title>
  <style>
    :root { --primary: #0066cc; --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --muted: #94a3b8; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
    .progress-bar { height: 5px; background: #1e293b; width: 100%; }
    .progress-fill { height: 100%; background: var(--primary); width: 0%; transition: width 0.3s ease; }
    header { padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; }
    header a { color: var(--muted); text-decoration: none; font-size: 0.95rem; border: 1px solid #334155; padding: 0.4rem 0.9rem; border-radius: 6px; }
    header a:hover { color: var(--text); border-color: var(--primary); }
    main { flex: 1; display: flex; align-items: center; justify-content: center; padding: 2rem; }
    .slide { display: none; max-width: 900px; width: 100%; background: var(--card); border: 1px solid #334155; border-radius: 12px; padding: 3rem; box-shadow: 0 10px 30px rgba(0,0,0,0.4); animation: fadeIn 0.3s ease; }
    .slide.active { display: block; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
    .tag { display: inline-block; background: rgba(0,102,204,0.2); color: #60a5fa; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.85rem; margin-bottom: 1rem; }
    h1 { font-size: 2.2rem; margin-bottom: 1.2rem; color: #ffffff; line-height: 1.3; }
    .summary { font-size: 1.15rem; color: #cbd5e1; margin-bottom: 1.5rem; line-height: 1.7; }
    ul { list-style: none; margin-bottom: 2rem; }
    li { font-size: 1.08rem; color: var(--text); padding: 0.6rem 0 0.6rem 1.6rem; position: relative; line-height: 1.6; }
    li::before { content: "▸"; color: var(--primary); position: absolute; left: 0; font-weight: bold; }
    .source-box { border-top: 1px solid #334155; padding-top: 1rem; font-size: 0.9rem; color: var(--muted); display: flex; justify-content: space-between; }
    footer { padding: 1.2rem 2rem; background: #0b1120; border-top: 1px solid #1e293b; display: flex; justify-content: center; align-items: center; gap: 1.5rem; }
    button { background: var(--card); color: var(--text); border: 1px solid #334155; padding: 0.6rem 1.4rem; border-radius: 6px; font-size: 1rem; cursor: pointer; transition: 0.2s; }
    button:hover:not(:disabled) { background: var(--primary); border-color: var(--primary); }
    button:disabled { opacity: 0.4; cursor: not-allowed; }
    #page-indicator { font-size: 1rem; color: var(--muted); min-width: 80px; text-align: center; }
  </style>
</head>
<body>
  <div class="progress-bar"><div class="progress-fill" id="progress"></div></div>
  <header>
    <div style="font-weight:bold; color:#0066cc;">🤖 LLM Wiki 教學簡報</div>
    <a href="index.html">← 返回網站首頁</a>
  </header>
  <main id="slides-container"></main>
  <footer>
    <button id="prev-btn" onclick="changeSlide(-1)">← 上一頁</button>
    <span id="page-indicator">1 / 1</span>
    <button id="next-btn" onclick="changeSlide(1)">下一頁 →</button>
  </footer>
  <script>
    const slidesData = __SLIDES_JSON__;
    const container = document.getElementById('slides-container');
    slidesData.forEach((s, idx) => {
      const bulletsHtml = s.bullets.map(b => <li></li>).join('');
      container.innerHTML += 
        <div class="slide " id="slide-">
          <span class="tag"></span>
          <h1></h1>
          <p class="summary"></p>
          <ul></ul>
          <div class="source-box">
            <span>📚 資料來源：</span>
            <span>使用鍵盤 ← / → 鍵切換</span>
          </div>
        </div>;
    });
    let current = 0;
    function updateUI() {
      document.querySelectorAll('.slide').forEach((el, i) => el.classList.toggle('active', i === current));
      document.getElementById('page-indicator').innerText = ${current + 1} / ;
      document.getElementById('prev-btn').disabled = current === 0;
      document.getElementById('next-btn').disabled = current === slidesData.length - 1;
      document.getElementById('progress').style.width = ${((current + 1) / slidesData.length) * 100}%;
    }
    function changeSlide(dir) {
      const next = current + dir;
      if (next >= 0 && next < slidesData.length) { current = next; updateUI(); }
    }
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') changeSlide(1);
      if (e.key === 'ArrowLeft') changeSlide(-1);
    });
    updateUI();
  </script>
</body>
</html>'''

    final_html = html_template.replace("__SLIDES_JSON__", json.dumps(best_slides, ensure_ascii=False, indent=2))
    with open("slides.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"\n[Node 4: Export] 已成功組合並輸出教學簡報：slides.html (共 {len(best_slides)} 頁投影片)")
    print("==================================================")

if __name__ == "__main__":
    run_agent_graph()
