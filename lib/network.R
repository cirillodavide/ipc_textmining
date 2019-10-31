library(igraph)

tab <- read.table("data/medulloblastoma/edgelist.tsv",sep='\t',header=T)

tab <- tab[tab$comb_pvalue<0.01,]
tab <- tab[tab$word_1!="Species_9606" & tab$word_2!="Species_9606",]
net <- simplify(graph_from_data_frame(tab,directed=FALSE))
net <- delete.vertices(net, V(net)[degree(net)==0])
co <- layout_nicely(net)

plot(net,
	vertex.size=4,
	layout=co,
	vertex.label.cex=0.3,
	vertex.label.color="black",
	vertex.label.dist=1,
)