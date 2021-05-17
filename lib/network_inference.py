import pickle
import pandas as pd
import numpy as np
from tqdm import tqdm
import bisect
import scipy
from scipy import stats
from gensim.models import Word2Vec

def pvalue(x,ref):
	    p = []
	    for k in x:
		    n = bisect.bisect_right(ref, k)
		    p.append(n/(len(ref)+1)) # pseudocount to avoid p-value of zero
	    return(p)

def edgelists(vocab_entities, word_distances, model, outfile1, outfile2):

    entities = pd.read_csv(vocab_entities,sep='\t')
    entities_dict = dict(zip(entities.encoded_entity, entities.entity))

    pickle_in = open(word_distances,'rb')
    word_distances = pickle.load(pickle_in)

    model = Word2Vec.load(model)

    #word distances edglist
    lst = []
    lst_ref = []
    for k,v in word_distances.items():
	    if len(k[0])==12 and len(k[1])==12 and k[0].startswith('x') and k[1].startswith('x') and k[0].endswith('x') and k[1].endswith('x'):
		    try:
			    lst.append([entities_dict[k[0]],entities_dict[k[1]],v[1],v[0]])
		    except:
			    pass
	    else:
		    lst_ref.append([v[1],v[0]])

    df = pd.DataFrame(lst, columns=['word_1','word_2','d','N'])
    df_ref = pd.DataFrame(lst_ref, columns=['d','N'])

    d_ref = sorted(df_ref['d'])
    N_ref = sorted(df_ref['N'])

    df['d_pvalue'] = pvalue(df['d'],d_ref) # distances shorter than by chance
    df['N_pvalue'] = [1-i for i in pvalue(df['N'],N_ref)] # num of abstracts higher than by chance
    df['comb_pvalue'] = [scipy.stats.combine_pvalues(i,method='fisher')[1] for i in zip(df['d_pvalue'],df['N_pvalue'])]

    df.to_csv(outfile1,index=None,sep='\t')

    #word embeddings edglist

    vocab = pd.read_csv(vocab_entities,sep='\t',header=None)
    vocab.columns = ['word','token']

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
    
    dff = pd.DataFrame.from_records(lst)
    dff.columns = ['word_1','word_2','cosine_sim']
    dff.to_csv(outfile2,index=None,sep='\t')

    return()
