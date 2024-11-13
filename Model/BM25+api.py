import openai
import json
import numpy as np
import jieba
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
import re


def select_best_with_openai(top_n_ids, top_n_texts, query):
    """
    呼叫 OpenAI API 以選擇最佳答案。

    當最高分數的文本 ID 一致時，避免呼叫 API，直接返回文本的 ID。
    否則，根據提供的 query 和多個文本，向 OpenAI API 發送請求以選擇最佳匹配的文本 ID。

    Args:
        top_n_ids (list): 文本 ID 列表，按分數排序。
        top_n_texts (list): 與文本 ID 對應的文本內容。
        query (str): 用戶查詢的問題。

    Returns:
        int: 選擇的最佳文本 ID。
    """
    
    if all(element == top_n_ids[0] for element in top_n_ids):
        # 如果最高分數的文本都一樣，那就不用問 API 了 
        return top_n_ids[0]
    
    client = openai.OpenAI(
        api_key = '[YOUR KEY]'  
    )
  
    prompt = ( "你是一名銀行內部的經理人，在接下來的任務當中，會有一個問題，以及多個參考資料，請根據問題，挑選出此問題的解答最有可能出現在哪一個參考資料當中。回答時，僅需告訴我資料編號即可，例如你認為\"資料編號: 51\"有答案，請直接回答\"51\"。\n"
                "_________________________________\n"
                f"問題：{query}\n"
                "_________________________________\n"
    )
        
    for idx, text in zip(top_n_ids, top_n_texts):
        prompt += f"資料編號: 「{idx}」\n"
        prompt += f"內容:「{text.replace(" ", "").replace("\n", "")}」\n"
        prompt += "\n_________________________________\n"
    
  
    response = client.chat.completions.create( 
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": "system", "content": ""},
                  {"role": "user", "content": prompt}]
    )
    
    print(response)
    response_text = response.choices[0].message.content.strip()
    print(response_text)

    # 用正則抓出文本 id 
    score = int(re.search(r'\d+', response_text).group()) if re.search(r'\d+', response_text) else top_n_ids[0]

    return score


def load_parse_data(file_path):
    """
    從 JSON 文件中解析數據。

    Args:
        file_path (str): JSON 文件的路徑。

    Returns:
        dict: dataset 中的資料。
    """

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def preprocess_text(text):
    """
    對文本進行基本的預處理和斷詞。

    去除中文停用詞並使用 jieba 進行斷詞處理。

    Args:
        text (str): 原始文本。

    Returns:
        list: 預處理後的詞列表。
    """

    # 對文本進行基本處理，例如去除停用詞
    stop_words = set([
        '的', '了', '是', '在', '有', '和', '不', '人', '他', '她',
        '這', '那', '它', '我', '我們', '你', '你們', '他們', '會',
        '將', '要', '能', '就', '也', '但', '如果', '所以', '還',
        '又', '對', '和', '於', '之', '以', '來', '從', '等', '可',
        '所', '而', '也', '什麼', '哪', '怎麼', '為什麼', '誰', 
        '怎樣', '目前', '之前', '之後', '方面', '場合', '一個',
        '一些', '所有', '很', '太', '也許', '大概', '完全', '十分', '\n', ' '
    ])    

    words = [word for word in jieba.cut_for_search(text) if word not in stop_words]
    return words


def split_text_into_segments(text, segment_size=50):
    """
    將文本分段，每段具有指定的字數。

    Args:
        text (str): 要分段的原始文本。
        segment_size (int): 每段的字符數，這裡預設是 50。

    Returns:
        list: 文本分段的列表。
    """

    # 根據指定字數分段文本
    segments = [text[i:i + segment_size] for i in range(0, len(text), segment_size)]
    
    return segments


def count_similarity(parsed_data):
    """
    計算文本相似度，並使用 BM25 模型來計算文本分數

    根據查詢內容，對候選文本使用 BM25 模型進行相似度打分，
    並選擇最高分數的文本進行 OpenAI API 號召以最終選定文本。

    Args:
        parsed_data (dict): 待處理的查詢數據。

    Returns:
        list: 包含問題的 ID 和最佳匹配文本 ID 的結果。
    """

    output_results = []

    for item in parsed_data:
        query = item["query"]
        texts = item["text"]
        ids = item["source"]

        segmented_texts = []
        segmented_ids = []
        
        # 對文本切分，segment 的 size 設 50 
        for id, text in zip(ids, texts):
            segments = split_text_into_segments(text)
            segmented_texts.extend(segments)
            segmented_ids.extend([id] * len(segments))

        # 將文本和查詢轉換為小寫的詞列表（BM25 需要這種格式）
        tokenized_texts = [preprocess_text(text) for text in segmented_texts]
        tokenized_query = preprocess_text(query)

        # 構建 BM25 模型
        bm25 = BM25Okapi(tokenized_texts)
        bm25_scores = bm25.get_scores(tokenized_query)
        bm25_mean = np.mean(bm25_scores)
        bm25_std = np.std(bm25_scores)
        bm25_scores = (bm25_scores - bm25_mean) / bm25_std
        combined_scores = bm25_scores

        # 選擇分數最高的 45 名 
        top_n_indices = np.argsort(combined_scores)[-45:][::-1]  
        top_n_texts = [segmented_texts[i] for i in top_n_indices]
        top_n_ids = [segmented_ids[i] for i in top_n_indices]
        
        # 請 GPT 從這 45 名中挑選
        best_id = select_best_with_openai(top_n_ids, top_n_texts, query)

        result = {
            "qid": item["qid"],
            "retrieve": best_id,
        }
        output_results.append(result)

    return output_results


if __name__ == '__main__':
    parsed_data = load_parse_data('../Preprocess/parse.json')
    result = count_similarity(parsed_data)

    result_format = {
        "answers": result
    }
    with open('BM25withAPI_results.json', 'w', encoding='utf-8') as f:
        json.dump(result_format, f, ensure_ascii=False, indent=4)
