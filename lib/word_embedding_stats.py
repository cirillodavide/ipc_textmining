import pickle

f = open('data/ewing_sarcoma/word2vec_similarities.pkl','r+b')
f.seek(0)
word2vec_similarities = pickle.loads(f.read())

print(word2vec_similarities)