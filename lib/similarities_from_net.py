import pandas as pd
from gensim.models import Word2Vec
import sys

tag = sys.argv[1]

model = Word2Vec.load('data/'+tag+'/word2vec.model')

df = pd.read_csv('data/'+tag+'/edgelist.tsv',sep='\t')
vocab = pd.read_csv('data/'+tag+'/vocab_entities.tsv',sep='\t',header=None)
vocab.columns = ['word','token']

df = df[df['comb_pvalue']<0.01]
di = dict(zip(vocab.word,vocab.token))
di_rev = dict(zip(vocab.token,vocab.word))
df = df.replace({'word_1': di})
df = df.replace({'word_2': di})
lst = []
for i in set(df['word_1']):
	for j in set(df['word_2']):
		if i != j:
			lst.append([di_rev[i],di_rev[j],model.wv.similarity(i,j)])
		else:
			pass
outfile = 'data/'+tag+'/edgelist_word2vec.tsv'
dff = pd.DataFrame.from_records(lst)
dff.columns = ['word_1','word_2','cosine_sim']
dff.to_csv(outfile,index=None,sep='\t')