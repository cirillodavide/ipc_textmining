import pandas as pd
from collections import defaultdict
import mygene
import csv

#load files
textmined = 'data/medulloblastoma/edgelist.tsv'
tm = pd.read_csv(textmined,sep='\t')

tm_lst = pd.unique(tm[['word_1', 'word_2']].values.ravel('K'))
tm_dict = defaultdict(list)
for i in tm_lst:
	j = i.split("_",1)
	try:
		tm_dict[j[0]].append({i: msh_dict[j[1]]})
	except:
		tm_dict[j[0]].append({i: j[1]})

#external annotations
mesh = 'src/MESH_MRCONSO.tsv'
msh = pd.read_csv(mesh,sep='\t')
msh_dict = dict(zip(msh.MESH, msh.term))

mg = mygene.MyGeneInfo()

#assign gene names to entrez entities
tomyg = []
for k,v in tm_dict.items():
	if k == 'Gene':
		for l in v:
			for ki,vi in l.items():
				for i in vi.split(';'):
					tomyg.append(str(i))
tomyg = set(tomyg)

mg_dict = {}
out = mg.querymany(tomyg, scopes='entrezgene')
for i in out:
	try:
		symbol = i['symbol']
	except:
		symbol = i['query']
	mg_dict[i['query']] = symbol

for k,v in tm_dict.items():
	if k == 'Gene':
		for l in v:
			tmp = []
			for ki,vi in l.items():
				for i in vi.split(';'):
					tmp.append(mg_dict[i])
				l[ki] = ';'.join(tmp)

#collapse to one dictionary and update the edgelist
result = {}
for k,v in tm_dict.items():
	for d in v:
		result.update(d)

tm['word_1'].replace(result, inplace=True)
tm['word_2'].replace(result, inplace=True)

tm.to_csv('data/medulloblastoma/edgelist_annotated.tsv',index=False,sep='\t',quoting=csv.QUOTE_NONNUMERIC)

