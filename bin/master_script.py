import sys
sys.path.append('lib')
import xml_processing, word_normalization, word_embedding, pubtator_annotations, word_distance
import subprocess
import shlex
import os
import pickle
import csv
import pandas as pd

mesh = 'medulloblastoma'

if not os.path.exists('data/'+mesh+'.annotated_abstracts.tsv'):

	#retrive abstracts via mesh term and store in one single xml
	print('abstracts fetching')
	p = subprocess.Popen(['perl','lib/xml_retriever.pl',mesh,'data/'+mesh+'.xml'])
	p.wait()

	#extract PMIDs and abstract and pickle it as a dictionary
	print('abstracts preocessing')
	_ = xml_processing.parse_xml('data/'+mesh+'.xml','data/'+mesh+'.pkl')

	#unpickle the dictionary
	pickle_in = open('data/'+mesh+'.pkl','rb')
	abstract_dict = pickle.load(pickle_in)

	#annotate abstracts using pubtatorcentral
	print('abstract annotations')
	annotated_abstracts, vocab_entities = pubtator_annotations.annotate(abstract_dict)
	df = pd.DataFrame(list(annotated_abstracts.items()), columns=['pmid', 'abstract'])
	df.to_csv('data/'+mesh+'.annotated_abstracts.tsv', sep="\t", index=False)
	df = pd.DataFrame(list(vocab_entities.items()), columns=['entity', 'encoded_entity'])
	df.to_csv('data/'+mesh+'.vocab_entities.tsv', sep="\t", index=False)

#text preocessing and normalization
print('word normalization')
df = pd.read_csv('data/'+mesh+'.annotated_abstracts.tsv', sep="\t")
annot_abstr_dict = dict(zip(df.pmid, df.abstract))
normalized_table = word_normalization.table(annot_abstr_dict)
normalized_table.to_csv('data/'+mesh+'.norm_table.tsv', sep="\t", index=False)

#word distances
print('word distances')
_ = word_distance.distances(normalized_table,'data/'+mesh+'.word_distances.pkl')

#word embeddings
print('word embedding')
embeddings = word_embedding.vectors(normalized_table)

'''
#compute word embeddings cosine similarity
'''

