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
        for i in tqdm(lst):
            combs = list(combinations(i, 2))
            combs_sorted = [sorted(i) for i in combs]
            for j in combs_sorted:
                a = i.index(j[0])
                b = i.index(j[1])
                d[tuple(j)].append(abs((a+1)-b))
        return(d)

    d = test1()
    d = {k: (sum(v),len(v),sum(v)/len(v)) for k, v in d.items()}
    
    f = open(out_pkl,"wb")
    pickle.dump(d,f)
    f.close()