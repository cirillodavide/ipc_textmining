from gensim.models import Word2Vec, KeyedVectors
from gensim.test.utils import common_texts, get_tmpfile
from tqdm import tqdm
import pandas as pd

def vectors(normalized_table):
	df = normalized_table
	sent = df.groupby('pmid')['token'].apply(list).tolist()
	
	embedding_size = 50
	model_file = "data/word2vec.model"
	path = get_tmpfile(model_file)
	model = Word2Vec(sent, min_count = 1, size = embedding_size, workers = 3, window = 3, sg = 1)
	model.save(model_file)
	
	vocab = dict([(k, v.index) for k, v in model.wv.vocab.items()])
	vocab_size = len(vocab)
	embedding_dict = {}
	for key, value in vocab.items():
		embedding_dict[key] = model[key]
	return(embedding_dict)
