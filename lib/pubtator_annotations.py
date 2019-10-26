from bs4 import BeautifulSoup
import urllib
import os
import pickle
from tqdm import tqdm
from random import choices
from string import ascii_lowercase
from urllib.request import Request, urlopen
from urllib.error import  URLError

def download_url(url, attempts):
    for attempt in range(attempts):
        try:
            req = Request(url)
            response = urlopen(req)
        except URLError as e:
            if hasattr(e, 'reason'):
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('Error code: ', e.code)
        else:
            return response.read()

    return None

def annotate(abstract_dict):
	vocab_entities = {}
	annotated_abstracts = {}
	for pmid,abstract in tqdm(abstract_dict.items()):
		if abstract:
			url = 'https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocxml?pmids='+str(pmid)
			data = download_url(url,3)
			text = data.decode('utf-8')
			soup = BeautifulSoup(text,'xml')
			abstract_new = []
			end_0 = 0
			for passage in soup.find_all('passage'):
				if passage.find('infon', {'key': 'type'}).text == 'abstract':
					try:
						PTC_abstract = passage.find('text').text
						start_offset = passage.find('offset').text
						for annot in passage.find_all('annotation'):
							entity = annot.find('infon', {'key': 'identifier'})
							if not entity:
								entity = annot.find('infon', {'key': 'Identifier'})
							category = annot.find('infon', {'key': 'type'})
							try:
								entity = str(category.text)+'_'+str(entity.text)
								length = annot.find('location')['length']
								offset = annot.find('location')['offset']
								start = int(offset)-int(start_offset)
								end = int(offset)-int(start_offset)+int(length)
								#print(entity,start,end,PTC_abstract[start:end])
								if entity not in vocab_entities:
									encoded_entity = "x"+"".join(choices(ascii_lowercase, k=10))+"x"
									vocab_entities[entity] = encoded_entity
								abstract_new.append(PTC_abstract[end_0:start] + vocab_entities[entity] + PTC_abstract[end])
								end_0 = end+1
							except:
								pass
						abstract_new.append(PTC_abstract[end_0:])
					except:
						pass
			annotated_abstracts[pmid] = ''.join(abstract_new)
	return(annotated_abstracts, vocab_entities)
