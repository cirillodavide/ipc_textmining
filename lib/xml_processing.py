from bs4 import BeautifulSoup
import pickle, os
from tqdm import tqdm
 
def clean_xml(in_xml,out_xml):

    input = open(in_xml,"r",encoding='utf-8')
    output = open(out_xml,"w",encoding='utf-8')

    output.write(input.readline())
    output.write("<PubmedArticleSet>")

    tpl = ("<PubmedArticleSet>","</PubmedArticleSet>","<!DOCTYPE","<?xml")
    for line in input:
        if not line.lstrip().startswith(tpl):
            output.write(line)

    output.write("</PubmedArticleSet>")

    input.close()
    output.close()

def parse_xml(xml_file,out_pkl):
	
	dictPMID = {}
	xml_clean_file = "{0}_{2}{1}".format((*os.path.splitext(xml_file) + ('clean',)))
	clean_xml(xml_file,xml_clean_file)
	infile = open(xml_clean_file,"r",encoding='utf-8')
	contents = infile.read()
	soup = BeautifulSoup(contents,'lxml-xml')

	articles = soup.select('PubmedArticle')
	print(len(articles))
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
	os.remove(xml_clean_file)
