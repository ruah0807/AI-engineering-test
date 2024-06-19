from food2vec.semantic_nutrition import Estimator

#Estimator 초기화
estimator = Estimator()

#자연어 검색을 통한 영양 정보 추정
match = estimator.natural_search("I ate a sweetpotato")
print(match)


# import food2vec
# print(dir(food2vec))