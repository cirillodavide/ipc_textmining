from itertools import combinations
from operator import itemgetter
from collections import defaultdict
import pandas as pd
from tqdm import tqdm
import pickle

def distances(normalized_table,out_pkl):
    lst = list(normalized_table.groupby("pmid").apply(lambda x: x['token'].tolist()))

    elms = set(x for l in lst for x in l)

    def test1():
        d = defaultdict(list)
        for i in tqdm(lst): # for each abstract
            combs = set(list(combinations(i, 2)))
            combs_sorted = [sorted(i) for i in combs]
            for j in combs_sorted: # for each word pairs combination
                if j[0] != j[1]:
                    a = [k for k,val in enumerate(i) if val==j[0]]
                    b = [k for k,val in enumerate(i) if val==j[1]]
                    for aa in a:
                        for bb in b:
                            v = sorted([aa,bb])
                            d[tuple(j)].append(abs(v[0]-v[1]+1)) # append distance
                else:
                    pass
        return(d)

    d = test1()
    d = {k: (len(v),sum(v)/len(v)) for k, v in d.items()} # num of abstracts w/ both entities and average distance between the two entities 
    
    f = open(out_pkl,"wb")
    pickle.dump(d,f)
    f.close()