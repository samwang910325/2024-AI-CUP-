# parse.py 使用說明

`parse.py` 是用於解析問題和參考資料的腳本，執行後會生成包含問題內容的 `parse.json` 文件。

## 使用方法

```bash
python parse.py -q <question_path> -r <reference_path>

例如
python parse.py -q ../datasets/dataset/questions_preliminary.json -r ../datasets/dataset/reference
