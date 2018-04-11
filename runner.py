import os, sys
import click

import pandas as pd
from pyflux import FluxWorkflowRunner
from subprocess import call


class Runner(FluxWorkflowRunner):
    def __init__(self, contigs_fasta, reference, output_dp):
        self.contigs_fasta = contigs_fasta
        self.reference = reference
        self.output_dp = output_dp

    def workflow(self):
        """ method invoked on class instance run call """
        fp = os.path.dirname(os.path.abspath(__file__))
        card = os.path.join(fp, './dependencies/data/card/model/card.json')
        conda = os.path.join(fp, './dependencies/miniconda/bin/activate')
        load_py3 = 'source activate py3'
        identifier = os.path.join(fp, 'identifier.py')

        pblat_output = os.path.join(self.output_dp, 'pblat.psl')
        self.addTask("pblat", nCores=self.getNCores(), memMb=self.getMemMb(),
             command='source {} && pblat -noHead -threads={} {} {} {}'.format(conda, self.getNCores(),
                                            self.contigs_fasta, self.reference, pblat_output))

        filtered_fasta = os.path.join(self.output_dp, 'filtered.fasta')
        self.addTask("psl_filter", nCores=self.getNCores(), memMb=self.getMemMb(),
             command='source {} && python {} psl_filter -f {} -p {} -o {}'.format(conda, identifier,
                                            self.contigs_fasta, pblat_output, filtered_fasta),
             dependencies=['pblat',])

        rgi_output = os.path.join(self.output_dp, 'rgi_output')
        self.addTask("rgi_screen", nCores=self.getNCores(), memMb=self.getMemMb(),
             command='source {} && {} && rgi load --afile {} --local && rgi main -a DIAMOND -n {} -i {} -o {} --local'.format(
                                                        conda, load_py3, card, self.getNCores(), filtered_fasta, rgi_output),
             dependencies=['psl_filter',])

        rgi_txt = rgi_output+'.txt'
        arg_output = os.path.join(self.output_dp, 'predicted_args')
        self.addTask("create_fastas", nCores=self.getNCores(), memMb=self.getMemMb(),
            command='source {} && python {} build -r {} -o {}'.format(conda, identifier, rgi_txt, arg_output),
            dependencies=['rgi_screen',])
        
         




@click.command()
@click.argument('contigs_fasta')
@click.option('--reference', '-r', default='./dependencies/data/card/model/nucleotide_fasta_protein_homolog_model.fasta')
@click.option('--output', '-o', default=None)
@click.option('--flux/--no-flux', default=False)
@click.option('--dispatch/--no-dispatch', default=True)
@click.option('--account', '-a')
@click.option('--ppn', '-p', default=4)
@click.option('--mem', '-m', default='20000') # current limitation, only handles mb
@click.option('--walltime', '-w', default='2:00:00')
def runner(contigs_fasta, reference, output, flux, dispatch, account, ppn, mem, walltime):
    """ Analysis Workflow Management

    Sets up Pyflow WorkflowRunner and launches locally by default or via flux
    """
    if not output: output = os.path.join('./', 'output')
    log_output_dp = os.path.join(output, 'logs')
    workflow_runner = Runner(contigs_fasta=contigs_fasta, reference=reference, output_dp=output)

    if flux:
        if not account: sys.exit('To attempt a submission to the flux cluster you need to supply an --account/-a')
        if dispatch:
            full_dp = os.path.dirname(os.path.abspath(__file__))
            activate = 'source {}'.format(os.path.join(full_dp, 'dependencies', 'miniconda', 'bin', 'activate'))
            runner_fp = os.path.join(full_dp, 'runner.py')
            qsub = 'qsub -N pyflux_handler -A {} -q fluxm -l nodes=1:ppn=1,mem=2000mb,walltime={}'.format(account, walltime)
            call('echo "{} && python {} {} -r {} -o {} -a {} -p {} -m {} -w {} --flux --no-dispatch" | {}'.format(activate, runner_fp,
                                               contigs_fasta, reference, output, account, ppn, mem, walltime, qsub), shell=True)
        else:
            workflow_runner.run(mode='flux', dataDirRoot=log_output_dp, nCores=ppn, memMb=mem,
                                schedulerArgList=['-N', 'viral_runner',
                                                  '-A', account,
                                                  '-l', 'nodes=1:ppn={},mem={}mb,walltime={}'.format(ppn, mem, walltime)])
    else:
        workflow_runner.run(mode='local', dataDirRoot=log_output_dp, nCores=ppn, memMb=mem)


if __name__ == "__main__":
    runner()
