FROM ubuntu:latest
LABEL maintainer="davide.cirillo@bsc.es"

RUN apt-get update

#install perl stuff
RUN apt-get install --yes \
	build-essential \
	gcc-multilib \
	apt-utils \
	perl \
	expat \
	libexpat-dev \
	libssl-dev \
	libnet-ssleay-perl \
	libcrypt-ssleay-perl

RUN apt-get install -y cpanminus

RUN cpanm install LWP::UserAgent Time::Progress LWP::Protocol::https

#install python stuff
RUN apt-get install --yes \
	python3 \
	python3-pip

RUN pip3 install bs4 tqdm nltk pandas gensim lxml --break-system-packages
RUN python3 -m nltk.downloader stopwords
RUN python3 -m nltk.downloader wordnet

#install git stuff
RUN apt-get install --yes \
	git

RUN git clone https://github.com/cirillodavide/ipc_textmining.git
