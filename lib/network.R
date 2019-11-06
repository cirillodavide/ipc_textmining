library(igraph)   
library(ggraph)   
library(graphlayouts)

args <- commandArgs(trailingOnly=TRUE)
edgelist <- args[1] # data/medulloblastoma/edgelist_annotated.tsv
tab <- read.table(edgelist,sep='\t',header=T)

tab <- tab[tab$comb_pvalue<0.01,]
#tab <- tab[tab$word_1!="Species_9606" & tab$word_2!="Species_9606",]
net <- simplify(graph_from_data_frame(tab,directed=FALSE))
net <- delete.vertices(net, V(net)[degree(net)==0])

set.seed(666)
p1 <- ggraph(net,layout='stress', bbox = 40)+
  geom_edge_link(width=0.2,colour='#0096FF')+
  geom_node_point(col="darkgrey",size=0.8)+
  geom_node_text(aes(label = name),repel=TRUE,size=2,fontface='bold',col='black')+
  theme_graph()

pdf("ggraph.pdf",width=10)
print(p1)
dev.off()