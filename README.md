
## 環境需求

本專案基於以下環境開發：

- **Python 版本**: Python 3.12.3
- **所需套件**: 詳見 `requirements.txt` 文件

## 專案說明

### 1. `Preprocess` 資料夾
包含資料的前處理程式碼。

- `parse.py`: 此檔案負責對原始資料進行前處理
- `README.md`: 說明資料前處理的步驟與使用方式。

### 2. `Model` 資料夾
包含檢索的程式碼。

- `BM25+api.py`: 檢索模型的核心程式碼，包含評估方法。
- `README.md`: 說明模型的使用方式和相關設定。

### 3. `requirements.txt`
列出本專案需要用到的 Python 套件及其版本。使用 `pip install -r requirements.txt` 來安裝所需的套件。

## 環境配置

本專案中需使用 OpenAI API，模型是gpt-4o-mini，但由於有對資料先進行篩選，因此tokens數並不會太高

## 資料集說明

使用官方提供的資料集進行自動化處理，並無人工修改。

## 執行步驟

1. 下載並解壓縮資料集。
2. 安裝所需的 Python 套件：

    ```bash
    pip install -r requirements.txt
    ```
3. 分別執行 `Preprocess/parse.py` 及 `Model/BM25+api.py`
