# iPC text mining workflow

![alt text](https://github.com/cirillodavide/ipc_textmining/blob/master/img/iPC_textmining.png?raw=true)

## Example execution

Build the image:
```
sudo docker build -t ipc-textmining .
```

Run the image inside a conatiner and access it:
```
sudo docker run --name=test-container --rm -it ipc-textmining bash
```

If it is already running, just execute the container:
```
sudo docker exec -it test-container bash
```

Enter the directory ipc_textmining and run a job passing two arguments (the query and a job tag) 
```
cd ipc_textmining
python3 bin/master_script.py "carcinoma, hepatocellular/genetics [mesh] AND hepatoblastoma/genetics [mesh]" "HCC_HB"
```

Job progress is displayed:
![alt text](https://github.com/cirillodavide/ipc_textmining/blob/master/img/progress.PNG?raw=true)

Output files are stored inside the directory data and subdirectory named as the job tag:

<kbd>abstracts.xml</kbd> XML containing the selected abstracts. \
<kbd>abstracts.pkl</kbd> Pickled dictionary of PMIDs and abstract texts. \
<kbd>annotated_abstracts.tsv</kbd> Abstract texts with masked PTC annotations. \
<kbd>vocab_entities.tsv</kbd> Table reporting PTC annotations and their correponding masking identifiers. \
<kbd>norm_table.tsv</kbd> Table reporting position and normalized tokens in the abstracts. \
<kbd>word2vec.model</kbd> GenSim model that generated the vector embeddings of the abstract tokens. \
<kbd>embeddings.kv</kbd> GenSim file containing the vector embeddings of the abstract tokens. \
<kbd>word_distances.pkl</kbd> Pickled dictonary reporting the num of abstracts with each pair of tokens and average number of other tokens between them in the abstracts. \
<kbd>edgelist_distances.tsv</kbd> Table reporting global text features (d: average number of separating words; N: number of co-occurring abstracts), corresponding empirical p-values and their combination (Fisher's method). \
<kbd>edgelist_word2vec.tsv</kbd> Table reporting local text features (cosine_sim: cosine similarity between word embeddings). \
