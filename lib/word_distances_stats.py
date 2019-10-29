import pickle
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

pickle_in = open('data/medulloblastoma/word_distances.pkl','rb')
abstract_dict = pickle.load(pickle_in)

vocab = pd.read_csv('data/medulloblastoma/vocab_entities.tsv',sep='\t')
vocab_dict = dict(zip(vocab.encoded_entity, vocab.entity))

lst = []
for k,v in abstract_dict.items():
	if len(k[0])==12 and len(k[1])==12 and k[0].startswith('x') and k[1].startswith('x') and k[0].endswith('x') and k[1].endswith('x'):
		try:
			lst.append([vocab_dict[k[0]],vocab_dict[k[1]],v[0],v[1]])
		except:
			pass


df = pd.DataFrame(lst, columns=['word_1','word_2','d','N'])

# barplot of entity counts

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
fig.savefig("data/medulloblastoma/entities_count.png")

# distribution plot

df['log_d'] = np.log(df['d']+1)
df['log_N'] = np.log(df['N']+1)
sns_plot = sns.jointplot(x="log_d", y="log_N", data=df, kind="kde")
sns_plot.savefig("data/medulloblastoma/word_distances.png")


