import pickle
import pandas as pd
import random
from sklearn.cluster import SpectralClustering
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn import metrics

#load dataset
pickle_in = open('data/medulloblastoma/word_distances.pkl','rb')
word_distances = pickle.load(pickle_in)

vocab = pd.read_csv('data/medulloblastoma/vocab_entities.tsv',sep='\t')
vocab_dict = dict(zip(vocab.encoded_entity, vocab.entity))

X = []
for k,v in word_distances.items():
	if len(k[0])==12 and len(k[1])==12 and k[0].startswith('x') and k[1].startswith('x') and k[0].endswith('x') and k[1].endswith('x'):
		try:
			b = np.array([v[0],v[1]])
			X.append(b)
		except:
			pass
X = np.asarray(X)

#clustering
sc = SpectralClustering(n_clusters=4, assign_labels="discretize")
clustering = sc.fit(X)
labels = clustering.labels_
plt.scatter(np.log(X[:,0]+1), np.log(X[:,1]+1), c=labels, cmap='rainbow', alpha=0.7, edgecolors='none',s=6)
plt.show()
