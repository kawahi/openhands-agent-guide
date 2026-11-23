# 04. Agent 如何操作外部世界：Tools 與 MCP 協定

## Function Calling（函式呼叫）機制
LLM 本質上只能輸出文字。要讓它操作電腦，開發者會預先定義好工具的 JSON Schema（名稱、用途、參數格式）。當 LLM 判斷需要查資料時，會輸出特定格式的呼叫請求，由外層程式代為執行後把結果餵回給 LLM。

## 什麼是 MCP（Model Context Protocol）？
過去每接一個新工具（如 GitHub、Google Drive、本地資料庫），都要重寫一套串接程式。**MCP** 是為 AI Agent 設計的「通用轉接頭（類似 USB-C 標準）」：
- **MCP Server**：將本地檔案系統、Git 或資料庫包裝成標準介面。
- **MCP Client**：Agent 主程式只要支援 MCP，就能即插即用各種工具，大幅降低開發複雜度。

> **延伸閱讀**：請參閱 [[05-hands-on-openhands]] 查看實際開發環境的應用。
