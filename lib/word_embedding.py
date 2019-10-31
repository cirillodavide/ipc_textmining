import gensim as gensim
from gensim.models import Word2Vec, KeyedVectors
from gensim.test.utils import common_texts, get_tmpfile
from gensim import corpora, models, similarities
from tqdm import tqdm
import pandas as pd
import numpy as np

def vectors(normalized_table,model_file,similarities_file,words_file):
	sent = normalized_table.groupby('pmid')['token'].apply(list).tolist()
	
	embedding_size = 50
	path = get_tmpfile(model_file)
	model = Word2Vec(sent, min_count = 1, size = embedding_size, workers = 3, window = 3, sg = 1)
	model.save(model_file)

	vocab = dict([(k, v.index) for k, v in model.wv.vocab.items()])
	
	outv = KeyedVectors(embedding_size)
	outv.index2word = model.wv.index2word
	np.savetxt(words_file, outv.index2word, fmt="%s")
	index = gensim.similarities.MatrixSimilarity(gensim.matutils.Dense2Corpus(model.wv.syn0.T))
	np.savetxt(similarities_file, index, fmt="%s")

'''
	vocab_size = len(vocab)
	embedding_dict = {}
	for key, value in vocab.items():
		embedding_dict[key] = model[key]
	return(embedding_dict)
'''