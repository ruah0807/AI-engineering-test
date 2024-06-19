from food2vec.semantic_nutrition import Estimator
import numpy as np

estimator=Estimator()

embedding1 = estimator.embed('I don not want to eat an apple')
embedding2 = estimator.embed('I ate an apple')
relationship = estimator.cosine(embedding1,embedding2)
print(relationship)