import click
import os

import screed
import pandas as pd


@click.group()
def cli():
    pass


@cli.command()
@click.option('--fasta_fp', '-f', required=True)
@click.option('--psl_fp', '-p', required=True)
@click.option('--output_fp', '-o', required=True)
def psl_filter(fasta_fp, psl_fp, output_fp):
    hits = pd.read_csv(psl_fp, sep='\t', names=['matches', 'misMatches', 'repMatches', 'nCount',
                                                  'qNumInsert', 'qBaseInsert', 'tNumInsert', 'tBaseInsert',
                                                  'strand', 'qName', 'qSize', 'qStart', 'qEnd',
                                                  'tName', 'tSize', 'tStart', 'tEnd',
                                                  'blockCount', 'blockSizes', 'qStarts', 'tStarts'])
    fasta_db = screed.read_fasta_sequences(fasta_fp)
    output = open(output_fp, 'w+')
    first_entry = True
    for seq in fasta_db:
        if seq in hits['qName'].unique():
            if first_entry:
                output.write('>{}\n{}'.format(fasta_db[seq].name, str(fasta_db[seq].sequence)))
                first_entry = False
            else:
                output.write('\n>{}\n{}'.format(fasta_db[seq].name, str(fasta_db[seq].sequence)))
    output.close()

@cli.command()
@click.option('--rgi_tsv', '-r', required=True)
@click.option('--output_dp', '-o', required=True)
def build(rgi_tsv, output_dp):
    if not os.path.exists(output_dp): os.makedirs(output_dp)
    rgi_df = pd.read_csv(rgi_tsv, sep='\t')
    for aro in rgi_df['Best_Hit_ARO'].unique():
        rgi_aros = rgi_df[rgi_df['Best_Hit_ARO'] == aro]
        output = open(os.path.join(output_dp, '{}.fasta'.format(aro.replace('/','_'))), 'w+')
        i = 0
        for _, arg in rgi_aros.iterrows():
            if i == 0: output.write('>{}\n{}'.format('{}|{}|{}'.format(
                                     arg['Best_Hit_ARO'], arg['Contig'], arg['Cut_Off']).replace(' ',''), 
                                     arg['Predicted_DNA']))
            else: output.write('\n>{}\n{}'.format('{}|{}|{}'.format(
                                arg['Best_Hit_ARO'], arg['Contig'], arg['Cut_Off']).replace(' ',''),
                                arg['Predicted_DNA']))
            i += 1
        output.close()


@cli.command()
@click.option('--fasta_fp', '-f', help='path to fasta file to split', required=True)
@click.option('--output_dp', '-o', help='path to directory to split fasta to', required=True)
@click.option('--split_num', '-n', help='number of seqs to include in each split', default=200000)
def split(fasta_fp, output_dp, split_num):
    if not os.path.exists(output_dp): os.makedirs(output_dp)
    fasta_db = screed.read_fasta_sequences(fasta_fp)

    n = 0
    first_entry = True
    for i, seq in enumerate(fasta_db):
        if i == 0:
            output = open(os.path.join(output_dp, 'tmp_{}.fasta'.format(n)), 'w+')
        elif i % split_num == 0:
            n += 1
            output.close()
            first_entry = True
            output = open(os.path.join(output_dp, 'tmp_{}.fasta'.format(n)), 'w+')
            
        if first_entry:
            output.write('>{}\n{}'.format(fasta_db[seq].name, str(fasta_db[seq].sequence)))
            first_entry = False
        else:
            output.write('\n>{}\n{}'.format(fasta_db[seq].name, str(fasta_db[seq].sequence)))
    output.close()
    


if __name__ == "__main__":
    cli()
