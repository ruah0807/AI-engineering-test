from typing import List, Tuple, Dict
from collections import defaultdict

def reciprocal_rank_fusion(results_list: List[List[Tuple[str,float]]], k: int = 60)-> List[Tuple[str, float]]:
    
    scores = defaultdict(float)
    for results in results_list:
        for rank, (doc_id, _) in enumerate(results):
            scores[doc_id] += 1 / (k + rank)
    combined_results = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    
    return combined_results


def model_e5_search(query: str) -> List[Tuple[str, float]]:
    
    return

def model_e5_multi_search(query: str) -> List[Tuple[str, float]]:
    
    return

def model_beg_m3_search(query: str) -> List[Tuple[str, float]]:
    
    return

def model_kf_deberta_search(query: str) -> List[Tuple[str, float]]:
    
    return