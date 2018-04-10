#!/bin/bash

# unload potentially conflicting anaconda instances
{ # try
    module unload python-anaconda2 &&
    module unload python-anaconda3
} || { # catch
    echo 'module unloading failed: maybe module does not exist'
}


# install miniconda for local independent package management
wget http://repo.continuum.io/miniconda/Miniconda2-4.3.21-Linux-x86_64.sh -O miniconda.sh
mkdir dependencies
chmod 775 miniconda.sh
chmod 775 dependencies
bash miniconda.sh -b -p ./dependencies/miniconda
rm miniconda.sh

# install pblat
git clone https://github.com/icebert/pblat.git
cd pblat && make && mv pblat ../dependencies/miniconda/bin/ && cd ..
rm -r pblat

# activate conda virtual environment
source ./dependencies/miniconda/bin/activate

# add bioconda and r channel for easy dependency installations
conda install -y -c bioconda screed biopython
conda install -y pandas click pyyaml tqdm

# install RGI in conda env
wget https://card.mcmaster.ca/download/1/software-v4.0.2.tar.gz
tar xvf software-v4.0.2.tar.gz
rm software-v4.0.2.tar.gz
tar zxvf rgi-4.0.2.tar.gz
rm rgi-4.0.2.tar.gz
cd rgi-4.0.2 && pip install -e . && cd ..
rm -r rgi-4.0.2

# install pyflow for automated task management
wget https://github.com/Illumina/pyflow/releases/download/v1.1.17/pyflow-1.1.17.tar.gz
pip install pyflow-1.1.17.tar.gz
rm pyflow-1.1.17.tar.gz

# download card ontology and model
wget https://card.mcmaster.ca/download/5/ontology-v2.0.0.tar.gz
mkdir -p dependencies/data/card/ontology
tar xvf ontology-v2.0.0.tar.gz -C dependencies/data/card/ontology/
rm ontology-v2.0.0.tar.gz

wget https://card.mcmaster.ca/download/0/broadstreet-v2.0.0.tar.gz
mkdir -p dependencies/data/card/model
tar xvf broadstreet-v2.0.0.tar.gz -C dependencies/data/card/model/
rm broadstreet-v2.0.0.tar.gz
