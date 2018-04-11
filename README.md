# Antibiotic Resistant Gene (ARG) Identifier
A workflow that accelerates identification of ARG-like sequences with CARD RGI.
Built and tested on GNU/Linux.

## Steps
1. Filter fasta sequences for those that contain possible ARGs
2. Run RGI against the filtered fasta file
3. Create fasta file for each ARO with all predicted ARGs

## Usage
```
Usage: runner.py [OPTIONS] CONTIGS_FASTA

  Analysis Workflow Management

  Sets up Pyflow WorkflowRunner and launches locally by default or via flux

Options:
  -r, --reference TEXT
  -o, --output TEXT
  --flux / --no-flux
  --dispatch / --no-dispatch
  -a, --account TEXT
  -p, --ppn INTEGER
  -m, --mem TEXT
  -w, --walltime TEXT
  --help                      Show this message and exit.
```

## Install anaconda environment and dependencies
> `$ ./build.sh`


## Run workflow
> `$ source ./dependencies/miniconda/bin/activate && python runner.py [CONTIGS_FASTA]`

## Run workflow on Flux
Depending on the size of the input fasta and/or reference, you may need to increase the memory `--mem` and processor count `--ppn`

> `source ./dependencies/miniconda/bin/activate && python runner.py [CONTIGS_FASTA] --flux --account [ACCOUNT]`
