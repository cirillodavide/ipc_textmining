import re
import string
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from tqdm import tqdm
import pandas as pd
from itertools import compress

def normalize(pmid,text):
    text = text.lower() # convert to lower case
    text = ''.join(c for c in text if not c.isdigit()) # remove numbers
    text = text.strip() # remove white spaces
    tokenizer = RegexpTokenizer(r'\w+') # tokenize
    stopWords = set(stopwords.words('english')) # remove stopwords
    ps = PorterStemmer() # stemming
    lemmatizer = WordNetLemmatizer() # lemmatize

    tokens = tokenizer.tokenize(text)
    valid = [re.match('^[a-zA-Z]+$', i) is not None for i in tokens]
    tokens = list(compress(tokens, valid))
    lst = []
    cnt = 0
    for i in tokens:
        if not i in stopWords:
            lst.append([pmid,cnt,i,ps.stem(lemmatizer.lemmatize(i))])
            cnt += 1
    return(lst)

def table(abstract_dict):
    lst = []
    for pmid, text in tqdm(abstract_dict.items()):
        try:
            lst.append(normalize(pmid,text))
        except:
            print('check PMID',pmid)
    lst = [item for sublist in lst for item in sublist]
    df = pd.DataFrame(lst,columns=['pmid', 'position', 'word', 'token'])
    df.dropna(inplace=True)
    return(df)