# Antibiotic Resistant Gene (ARG) Identifier
A workflow that accelerates identification of ARG-like sequences with CARD RGI.
Built and tested on GNU/Linux.

## Steps
1. Filter fasta sequences for those that contain possible ARGs
2. Run RGI against the filtered fasta file
3. Create fasta file for each ARO with all predicted ARGs

## Install anaconda environment and dependencies
> `$ ./build.sh`


## Run workflow
> `$ source ./dependencies/miniconda/bin/activate && python runner.py [fasta_file]`
