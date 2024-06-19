from food2vec.semantic_nutrition import Estimator

#Estimator 초기화
estimator = Estimator()

#자연어 검색을 통한 영양 정보 추정
match = estimator.natural_search("I ate an apple")
# print(match)

# # 단어 또는 구문 임베딩
# embedding1 = estimator.embed('apple')
# embedding2 = estimator.embed('I ate an apple')
# print(embedding1,embedding2)

embedding1 = estimator.embed('orange')
embedding2 = estimator.embed('apple')
relationship = estimator.cosine(embedding1,embedding2)
print(relationship)