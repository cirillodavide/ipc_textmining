import pandas as pd
from collections import defaultdict
import mygene
import myvariant
import csv
import re, sys

tag = sys.argv[1]

#external annotations
mesh = 'src/MESH_MRCONSO.tsv'
msh = pd.read_csv(mesh,sep='\t')
msh_dict = dict(zip(msh.MESH, msh.term))

mg = mygene.MyGeneInfo()
def mygene(lst): # list of entrez IDs
	mg_dict = {}
	out = mg.querymany(lst, scopes='entrezgene')
	for i in out:
		try:
			symbol = i['symbol']
		except:
			symbol = i['query']
		mg_dict[i['query']] = symbol
	return(mg_dict)

mv = myvariant.MyVariantInfo()
def myvariant(lst): # list of dbsnp IDs
	mv_dict = defaultdict(list)
	out = mv.querymany(lst, scopes='dbsnp.rsid')
	for i in out:
		try:
			if i['notfound'] == 'True':
				mv_dict[i['query']].append(i['query'])
		except:
			try:
				k = i['snpeff']['ann']
				if type(k) is dict:
					mv_dict[i['query']].append(k['genename'])
				elif type(k) is list:
					for j in k:
						mv_dict[i['query']].append(j['genename'])
			except:
				k = i['dbsnp']['gene']
				mv_dict[i['query']].append(k['symbol'])

	for k,v in mv_dict.items():
		mv_dict[k] = ';'.join(list(set(v)))
	return(mv_dict)

def mut_preprocess(lst):
	d = defaultdict(list)
	l = [i.split(';') for i in lst]
	for i in range(len(l)):
		if len(l[i]) == 1:
			d[lst[i]].append(lst[i])
		else:
			for j in l[i]:
				if 'RS#:' in j:
					j = j.replace('(Expired)','')
					for k in j.split('|'): 
						k = k.replace('RS#:','rs')
						if 'rs' not in k:
							k = 'rs'+str(k)
						d[lst[i]].append(k)
				if 'CorrespondingGene:' in j:
					k = next(re.finditer(r'\d+$', j)).group(0)
					k = mg.querymany([k], scopes='entrezgene')[0]['symbol']
					d[lst[i]].append(k)

	lst = [item for sublist in d.values() for item in sublist]
	return(d,lst)

def gene_preprocess(lst):
	d = defaultdict(list)
	l = [i.split(';') for i in lst]
	for i in range(len(l)):
		if len(l[i]) == 1:
			d[lst[i]].append(lst[i])
		else:
			for j in l[i]:
				d[lst[i]].append(j)
	lst = [item for sublist in d.values() for item in sublist]
	return(d,lst)

#load files
textmined = 'data/'+tag+'/edgelist_word2vec.tsv'
tm = pd.read_csv(textmined,sep='\t')

tm_lst = pd.unique(tm[['word_1','word_2']].values.ravel('K'))
tm_dict = defaultdict(list)
for i in tm_lst:
	j = i.split("_",1)
	tm_dict[j[0]].append({i: j[1]})

#create dictionaries for conversion
SNP_dict = {}
ProteinMutation_dict = {}
DNAMutation_dict = {}
Gene_dict = {}
Disease_dict = {}
Chemical_dict = {}

for k,v in tm_dict.items():
	
	if k == 'SNP':
		lst = []
		for j in v:
			for k_j,v_j in j.items():
				lst.append(v_j)
		d = myvariant(lst)
		for k,v in d.items():
			SNP_dict['SNP_'+str(k)] = v
	
	if k == 'ProteinMutation':
		lst = []
		for j in v:
			for k_j,v_j in j.items():
				lst.append(v_j)
		d,lst = mut_preprocess(lst)
		d1 = myvariant(lst)
		for k,v in d.items():
			lst = []
			for i in v:
				if d1[i]:
					lst.append(d1[i])
				else:
					lst.append(i)
			ProteinMutation_dict['ProteinMutation_'+str(k)] = ';'.join(map(str, set(lst)))

	if k == 'DNAMutation':
		lst = []
		for j in v:
			for k_j,v_j in j.items():
				lst.append(v_j)
		d,lst = mut_preprocess(lst)
		d1 = myvariant(lst)
		for w,v in d.items():
			lst = []
			for i in v:
				if d1[i]:
					lst.append(d1[i])
				else:
					lst.append(i)
			DNAMutation_dict['DNAMutation'+str(w)] = ';'.join(map(str, set(lst)))
	
	if k == 'Gene':
		lst = []
		for j in v:
			for ki,vi in j.items():
				for i in vi.split(';'):
					lst.append(i)
		d,lst = gene_preprocess(lst)
		d1 = mygene(lst)
		for j in v:
			lst = []
			for ki,vi in j.items():
				for i in vi.split(';'):
					lst.append(d1[i])
				Gene_dict['Gene_'+str(vi)] = ';'.join(map(str, set(lst)))

	if k == 'Disease':
		lst = []
		for j in v:
			for ki,vi in j.items():
				try:
					Disease_dict['Disease_'+str(vi)] = msh_dict[vi]
				except:
					Disease_dict['Disease_'+str(vi)] = vi

	if k == 'Chemical':
		lst = []
		for j in v:
			for ki,vi in j.items():
				try:
					Chemical_dict['Chemical_'+str(vi)] = msh_dict[vi]
				except:
					Chemical_dict['Chemical_'+str(vi)] = vi

def merge_dicts(*dict_args):
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return(result)

result = merge_dicts(ProteinMutation_dict, SNP_dict, DNAMutation_dict, Gene_dict, Disease_dict, Chemical_dict)

tm['word_1'].replace(result, inplace=True)
tm['word_2'].replace(result, inplace=True)

tm.to_csv('data/'+tag+'/edgelist_annotated_word2vec.tsv',index=False,sep='\t',quoting=csv.QUOTE_NONNUMERIC)
