from typing import List, Tuple, Dict
from collections import defaultdict
from urllib.parse import quote
from .e5_dense import model_e5_search
from .e5_multi import model_e5_multi_search
from .beg_m3 import model_beg_m3_search
from .kf_deberta import model_kf_deberta_search


def reciprocal_rank_fusion(results_list: List[Tuple[str, List[Tuple[str, float]]]], k: int = 60) -> List[Tuple[str, float, List[Tuple[str, float]]]]:
    
    scores = defaultdict(float)
    model_contributions = defaultdict(list)
    
    for model_name, results in results_list:
        for rank, (doc_id, _) in enumerate(results):
            score_contribution = 1 / (k + rank)
            scores[doc_id] += score_contribution
            model_contributions[doc_id].append((model_name, score_contribution))
    combined_results = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    
    return [(doc_id, score, model_contributions[doc_id]) for doc_id, score in combined_results]




def hybrid_search_pinecone(query: str, top_k: int = 10) -> List[Dict]:
    
    encoded_query = quote(query)
    
    results_model_e5_multi = model_e5_multi_search(encoded_query)
    results_model_e5 = model_e5_search(encoded_query)
    results_model_beg_m3 = model_beg_m3_search(encoded_query)
    results_model_kf_deberta = model_kf_deberta_search(encoded_query)
    
       # 각 모델의 이름과 함께 결과를 전달
    combined_results = reciprocal_rank_fusion([
        ('intfloat/multilingual-e5-large/multi', results_model_e5_multi),
        ('intfloat/multilingual-e5-large', results_model_e5),
        ('BAAI/bge-m3', results_model_beg_m3),
        ('upskyy/kf-deberta-multitask', results_model_kf_deberta)
    ])
    
    # 상위 top_k 결과 반환
    top_results = combined_results[:top_k]
    
    return [{'doc_id': doc_id, 'score': score, 'model_contributions': model_contributions} for doc_id, score, model_contributions in top_results]


# 모델별 기여도 집계 함수
def analyze_model_contributions(results: List[Dict]) -> Dict[str, float]:
    model_scores = defaultdict(float)
    
    for result in results :
        for model_name, contribution in result['model']