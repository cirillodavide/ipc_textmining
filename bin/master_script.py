import sys
sys.path.append('lib')
import xml_processing, word_normalization, word_embedding, pubtator_annotations, word_distance, network_inference
import subprocess
import shlex
import os
import pickle
import csv
import pandas as pd

mesh = sys.argv[1]
tag = sys.argv[2]

if not os.path.exists('data/'+tag):
	os.makedirs('data/'+tag)

if not os.path.exists('data/'+tag+'/annotated_abstracts.tsv'):

	#retrive abstracts via mesh term and store in one single xml
	print('abstracts fetching')
	p = subprocess.Popen(['perl','lib/xml_retriever.pl',mesh,'data/'+tag+'/abstracts.xml'])
	p.wait()

	#extract PMIDs and abstract and pickle it as a dictionary
	print('abstracts preocessing')
	_ = xml_processing.parse_xml('data/'+tag+'/abstracts.xml','data/'+tag+'/abstracts.pkl')

	#unpickle the dictionary
	pickle_in = open('data/'+tag+'/abstracts.pkl','rb')
	abstract_dict = pickle.load(pickle_in)

	#annotate abstracts using pubtatorcentral
	print('abstract annotations')
	annotated_abstracts, vocab_entities = pubtator_annotations.annotate(abstract_dict)
	df = pd.DataFrame(list(annotated_abstracts.items()), columns=['pmid', 'abstract'])
	df.to_csv('data/'+tag+'/annotated_abstracts.tsv', sep="\t", index=False)
	df = pd.DataFrame(list(vocab_entities.items()), columns=['entity', 'encoded_entity'])
	df.to_csv('data/'+tag+'/vocab_entities.tsv', sep="\t", index=False)

#text preocessing and normalization
print('word normalization')
df = pd.read_csv('data/'+tag+'/annotated_abstracts.tsv', sep="\t")
annot_abstr_dict = dict(zip(df.pmid, df.abstract))
normalized_table = word_normalization.table(annot_abstr_dict)
normalized_table.to_csv('data/'+tag+'/norm_table.tsv', sep="\t", index=False)

#word embeddings
print('word embedding')
embeddings = word_embedding.vectors(normalized_table,'data/'+tag+'/word2vec.model','data/'+tag+'/embeddings.kv')

#word distances
print('word distances')
_ = word_distance.distances(normalized_table,'data/'+tag+'/word_distances.pkl')

#network inference
print('network inference')
_ = network_inference.edgelists('data/'+tag+'/vocab_entities.tsv',
				'data/'+tag+'/word_distances.pkl',
				'data/'+tag+'/word2vec.model',
				'data/'+tag+'/edgelist_distances.tsv',
				'data/'+tag+'/edgelist_word2vec.tsv')

#create the network
#python lib/word_distances_stats.py tag
#python lib/annotate_edgelist.py tag
#python lib/similarities_from_net.py tag
#python lib/annotate_edgelist_word2vec.py tag



