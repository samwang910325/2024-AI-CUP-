# BM25+api.py 使用說明

`BM25+api.py` 是一個使用 BM25 與 OpenAI API 進行問題檢索的程式碼。該程式碼會根據查詢內容使用 BM25 模型計算文本的相似度，接著挑選分數前 K高的文本結合 OpenAI API 選出最符合問題的文本。

## 功能概述

- 使用 BM25 演算法對文本進行檢索排序。  
- 使用 OpenAI API 進一步確認最佳的匹配文本。
- 輸出最佳匹配結果 `BM25withAPI_results.json`。

## 使用前的準備

### 替換 OpenAI API Key

在執行此程式碼之前，請確保替換程式碼中的 API Key。
打開 `BM25+api.py`，將 `API_KEY_PLACEHOLDER` 替換為您自己的 OpenAI API Key：

```python
client = openai.OpenAI(
    api_key='API_KEY_PLACEHOLDER'  # 替換為您的 API Key
)

