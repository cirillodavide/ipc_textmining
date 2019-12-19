import pickle
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import bisect
import scipy
from scipy import stats
import csv, sys
from scipy.stats import spearmanr

tag = sys.argv[1]

pickle_in = open('data/'+tag+'/word_distances.pkl','rb')
word_distances = pickle.load(pickle_in)

entities = pd.read_csv('data/'+tag+'/vocab_entities.tsv',sep='\t')
entities_dict = dict(zip(entities.encoded_entity, entities.entity))

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

# def remove_outlier(df_in, col_name):
#     q1 = df_in[col_name].quantile(0.25)
#     q3 = df_in[col_name].quantile(0.75)
#     iqr = q3-q1 #Interquartile range
#     fence_low  = q1-1.5*iqr
#     fence_high = q3+1.5*iqr
#     df_out = df_in.loc[(df_in[col_name] > fence_low) & (df_in[col_name] < fence_high)]
#     return df_out

# df = remove_outlier(df,'d')
# df = remove_outlier(df,'N')
# df_ref = remove_outlier(df_ref,'d')
# df_ref = remove_outlier(df_ref,'N')

#select entities

d_ref = sorted(df_ref['d'])
N_ref = sorted(df_ref['N'])

def pvalue(x,ref):
	p = []
	for k in x:
		n = bisect.bisect_right(ref, k)
		p.append(n/(len(ref)+1)) # pseudocount to avoid p-value of zero
	return(p)

df['d_pvalue'] = pvalue(df['d'],d_ref) # distances shorter than by chance
df['N_pvalue'] = [1-i for i in pvalue(df['N'],N_ref)] # num of abstracts higher than by chance
df['comb_pvalue'] = [scipy.stats.combine_pvalues(i,method='fisher')[1] for i in zip(df['d_pvalue'],df['N_pvalue'])]

p = 0.01
d = df[df['comb_pvalue']<p]
print('max d with comb_pvalue<0.01:',d['d'].max())
print('min N with comb_pvalue<0.01:',d['N'].min())
corrS, _ = spearmanr(df['N'], df['d'])
print('Spearman correlation:',corrS)

df["-log10_comb_pvalue"] = -np.log10(df["comb_pvalue"])

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(5, 3))

sns.scatterplot(x="d", y="-log10_comb_pvalue", data=df, s=8, ax=axes[0])
axes[0].axhline(2, ls='--', c='grey',linewidth=1)
l = d['d'].max()
axes[0].axvline(l, ls='--', c='grey',linewidth=1)

sns.scatterplot(x="N", y="-log10_comb_pvalue", data=df, s=8, ax=axes[1])
axes[1].axhline(2, ls='--', c='grey',linewidth=1)
l = d['N'].min()
axes[1].axvline(l, ls='--', c='grey',linewidth=1)

fig.tight_layout()
fig.savefig('data/'+tag+'/fishers_p-values.png')

df.to_csv('data/'+tag+'/edgelist.tsv',sep='\t',index=False,quoting=csv.QUOTE_NONNUMERIC)

#barplot of entity counts

def select(entity):
	lst = []
	for col in ['word_1','word_2']:
		lst.append(df[df[col].str.startswith(entity)][col].tolist())
	lst = list(set([item for sublist in lst for item in sublist]))
	return(len(lst))

Disease = select('Disease')
Gene = select('Gene')
Chemical = select('Chemical')
Species = select('Species')
ProtMutations = select('ProteinMutation')
CellLine = select('CellLine')
DNAmutations = select('DNAMutation')
SNPs = select('SNP')

d = {'Disease':Disease,'Gene':Gene,'Chemical':Chemical,'Species':Species,'ProtMutations':ProtMutations,'DNAmutations':DNAmutations,'SNPs':SNPs,'CellLine':CellLine}
ec = pd.DataFrame(list(d.items()), columns = ['entity','count'])

fig, ax = plt.subplots()
fig.set_size_inches(11.7, 8.27)
g = sns.barplot(x="entity", y="count", data=ec)
for p in g.patches:
	g.annotate(format(p.get_height(), '.0f'), (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 10), textcoords = 'offset points')
fig.savefig('data/'+tag+'/entities_count.png')

#distribution plots

df['log_d'] = np.log(df['d']+1)
df['log_N'] = np.log(df['N']+1)
sns_plot = sns.jointplot(x="log_d", y="log_N", data=df, kind="kde")
sns_plot.savefig('data/'+tag+'/word_distances.png')

