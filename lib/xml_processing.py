from bs4 import BeautifulSoup
import pickle
from tqdm import tqdm
 
def parse_xml(xml_file,out_pkl):
	
	dictPMID = {}
	infile = open(xml_file,"r")
	contents = infile.read()
	soup = BeautifulSoup(contents, 'lxml')

	articles = soup.select('PubmedArticle')
	for i in tqdm(range(len(articles))):
		article = articles[i]
		pmid = article.select_one('PMID').text
		sent = []
		for j in article.select('Abstract'):
			for k in j.select('AbstractText'):
				sent.append(k.text)
		abstract = ' '.join(sent)
		dictPMID[pmid] = abstract	
	
	f = open(out_pkl,"wb")
	pickle.dump(dictPMID,f)
	f.close()
