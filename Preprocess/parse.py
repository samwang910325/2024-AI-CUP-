import json
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
import os
from tqdm import tqdm
import argparse


def preprocessing(text):
    """
    對文本進行基本處理，去除中文常見停用詞。

    Args:
        text (str): 原始文本。

    Returns:
        str: 去除停用詞後的文本。
    """
    
    stop_words = set([
        '的', '了', '是', '在', '有', '和', '不', '人', '他', '她',
        '這', '那', '它', '我', '我們', '你', '你們', '他們', '會',
        '將', '要', '能', '就', '也', '但', '如果', '所以', '還',
        '又', '對', '和', '於', '之', '以', '來', '從', '等', '可',
        '所', '而', '也', '什麼', '哪', '怎麼', '為什麼', '誰', 
        '怎樣', '目前', '之前', '之後', '方面', '場合', '一個',
        '一些', '所有', '很', '太', '也許', '大概', '完全', '十分', '~', '\n', ' '
    ]) 

    words = [word for word in text if word not in stop_words]
    return "".join(words)


def parse_questions(file_path, dataset_base_path):
    """
    讀取問題 JSON 文件並解析為包含問題和相關來源的資料

    Args:
        file_path (str): 問題 JSON 文件的路徑。
        dataset_base_path (str): 存放參考資料的基本目錄路徑。

    Returns:
        list: 包含每個問題的字典列表，每個字典包含 qid、source、query、category 和 text。
    """
    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    questions = data.get("questions", [])
    parsed_data = []

    # 逐個提取每個問題的 qid, source, query, 和 category
    for question in tqdm(questions, desc="Parse Questions"):
        
        qid = question.get("qid")
        source = question.get("source")
        query = question.get("query")
        category = question.get("category")

        if category == 'faq':
            text = [parse_faq(f'{dataset_base_path}/faq/pid_map_content.json', s) for s in source]
        elif category == 'finance':
            text = [read_file(f'{dataset_base_path}/finance/{s}.pdf') for s in source]
        elif category == 'insurance':
            text = [read_file(f'{dataset_base_path}/insurance/{s}.pdf') for s in source]
        
        # 建構 dictionary 並加入 list
        parsed_data.append({
            "qid": qid,
            "source": source,
            "query": query,
            "category": category,
            "text": text
        })
      
    return parsed_data


def parse_pdf(file_path):
    """
    提取 PDF 文件中的文字內容，若無法直接提取則使用 OCR 辨識文字。

    Args:
        file_path (str): PDF 文件的路徑。

    Returns:
        str: 處理後的文本內容。
    """
    text_content = ""

    with fitz.open(file_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text = page.get_text()  # 嘗試直接提取文字
            if text.strip():  # 如果有文字，表示不是掃描檔
                text_content += text
            else: 
                # 使用 OCR 套件 
                pix = page.get_pixmap(dpi=300) 
                img_data = pix.pil_tobytes(format="png")  

                img = Image.open(io.BytesIO(img_data))
                #img = preprocess_image(img)
                
                text = pytesseract.image_to_string(img, lang="chi_tra+eng")  # 使用繁體中文語言包
                text_content += text
    
    return preprocessing(text_content.strip())


def parse_faq(file_path, id):
    """
    解析 FAQ 的問題，提取指定 ID 的問題和答案。

    Args:
        file_path (str): FAQ JSON 文件的路徑。
        id (str): 要查找的問題 ID。

    Returns:
        str: 該 ID 的問題和答案文本，如果找不到則返回提示訊息。
    """
    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file) 

    id = str(id) 
    
    if id in data:
        output = ""
        
        for qa in data[id]:
            question = qa["question"]
            answers = qa["answers"]
            
            output += f"問題: {question}\n答案: {'；'.join(answers)}\n[SEP]"
        return output.strip()
    else:
        return "找不到該 ID 的資料"


def read_file(file_path):
    """
    讀取並處理 PDF 文件文本，若文本已經輸出整理過則直接讀取。

    Args:
        file_path (str): PDF 文件的路徑。

    Returns:
        str: 預處理後的文本內容。
    """
    
    txt_file_path = file_path[:-3] + "txt"
    
    # 檢查 txt 文件是否存在(是否之前 parse 過)
    if os.path.exists(txt_file_path):
        with open(txt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return preprocessing(content)
    else:
        return preprocessing(parse_pdf(file_path))
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Parse questions and save as JSON.")
    parser.add_argument('-q', '--question_path', type=str, help="Path to the questions JSON file.")
    parser.add_argument('-r', '--reference_path', type=str, help="Path to the reference directory.")
    
    args = parser.parse_args()
    
    if not args.question_path or not args.reference_path:
        print("Usage: python parse.py -q <question_path> -r <reference_path>")
        print("Example: python parse.py -q /path/to/questions_example.json -r /path/to/reference")
        exit(1)
    
    question_path = args.question_path
    reference_path = args.reference_path
    parsed_list = parse_questions(question_path, reference_path)
    
    with open('parse.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_list, f, ensure_ascii=False, indent=4)