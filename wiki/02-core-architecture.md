# 02. AI Agent 的四大核心組件

一個完整的 AI Agent 系統由 **LLM 大腦** 與三個關鍵外部模組構成：

## 1. 大腦（LLM Core）
負責語意理解、邏輯推理與指令生成（例如 Gemini、Claude、GPT 系列模型）。大腦本身不具備執行能力，必須依賴外圍架構。

## 2. 規劃模組（Planning）
面對複雜任務時，Agent 不會一步到位，而是進行任務拆解（Task Decomposition）：
- **子目標拆解**：將「建立網站」拆分為「設計架構 → 撰寫 HTML → 測試版面 → 部署」。
- **自我反思（Self-Reflection）**：評估上一步的產出是否符合預期，決定重做或前進。

## 3. 記憶模組（Memory）
- **短期記憶（Short-term Memory）**：當下任務的對話歷史與執行軌跡（Context Window）。
- **長期記憶（Long-term Memory）**：透過外部檔案（如 AGENTS.md、LLM Wiki 或向量資料庫）保存的跨任務知識與規範。

## 4. 工具調用（Tool Use）
賦予 Agent 雙手的能力，常見工具包括：終端機指令執行（Bash/PowerShell）、檔案讀寫（File Editor）、網頁搜尋與外部 API 呼叫。

> **延伸閱讀**：請參閱 [[03-agent-workflows-and-loops]] 了解這些組件如何透過迴圈協作。
