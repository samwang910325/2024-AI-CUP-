
## 環境需求

本專案基於以下環境開發：

- **Python 版本**: Python 3.12.3
- **所需套件**: 詳見 `requirements.txt` 文件，可使用以下指令安裝所有依賴項：
    ```bash
    pip install -r requirements.txt
    ```

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
列出本專案依賴的 Python 套件及其版本。使用 `pip install -r requirements.txt` 來安裝所有依賴。

### 4. `README.md`
專案的主要說明文件，包括目錄結構、環境需求、專案說明、超參數設定和資源配置建議。

## 超參數設定與資源配置

本專案中會需要使用 OpenAPI，模型是gpt-4o-mini，但由於有對資料先進行篩選，因此tokens數並不會太高

### 資源配置建議

- 需要進行連網

## 資料集說明

使用官方提供的資料集進行自動化處理，並無人工修改。

## 執行步驟

1. 下載並解壓縮資料集，放置於指定資料夾。
2. 安裝所需的 Python 套件：

    ```bash
    pip install -r requirements.txt
    ```

3. 分別執行 `parse.py` 及 `BM25+api.py`