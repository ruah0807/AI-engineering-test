from typing import List, Tuple, Dict
from collections import defaultdict
from urllib.parse import quote
from .e5_dense import model_e5_search
from .e5_multi import model_e5_multi_search
from .beg_m3 import model_beg_m3_search
from .kf_deberta import model_kf_deberta_search


def reciprocal_rank_fusion(results_list: List[List[Tuple[str,float]]], k: int = 60)-> List[Tuple[str, float]]:
    
    scores = defaultdict(float)
    for results in results_list:
        for rank, (doc_id, _) in enumerate(results):
            scores[doc_id] += 1 / (k + rank)
    combined_results = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    
    return combined_results




def hybrid_search_pinecone(query: str, top_k: int = 10) -> List[Dict]:
    
    encoded_query = quote(query)
    
    results_model_e5_multi = model_e5_multi_search(encoded_query)
    results_model_e5 = model_e5_search(encoded_query)
    results_model_beg_m3 = model_beg_m3_search(encoded_query)
    results_model_kf_deberta = model_kf_deberta_search(encoded_query)
    
    # RRF를 사용하여 결합된 결과 계산
    combined_results = reciprocal_rank_fusion([results_model_e5_multi, results_model_e5, results_model_beg_m3, results_model_kf_deberta])
    
    # 상위 top_k 결과 반환
    top_results = combined_results[:top_k]
    
    return [{'doc_id': doc_id, 'score': score} for doc_id, score in top_results]