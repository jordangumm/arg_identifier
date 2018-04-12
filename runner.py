import os, sys
import click

import pandas as pd
from pyflux import FluxWorkflowRunner
from subprocess import call


class Runner(FluxWorkflowRunner):
    def __init__(self, contigs_fasta, reference, output_dp, mem, ppn):
        self.contigs_fasta = contigs_fasta
        self.reference = reference
        self.output_dp = output_dp

        self.mem = mem
        self.ppn = ppn

    def workflow(self):
        """ method invoked on class instance run call """
        fp = os.path.dirname(os.path.abspath(__file__))
        card = os.path.join(fp, 'dependencies/data/card/model/card.json')
        conda = os.path.join(fp, 'dependencies/miniconda/bin/activate')
        load_py3 = 'source activate py3'
        identifier = os.path.join(fp, 'identifier.py')

        max_cores = self.getNCores()
        if max_cores == 'unlimited': max_cores = self.ppn

        max_mem = self.getMemMb()
        if max_mem == 'unlimited': max_mem = self.mem

        pblat_output = os.path.join(self.output_dp, 'pblat')
        self.addTask("pblat", nCores=max_cores, memMb=max_mem,
                 command='source {} && pblat -noHead -threads={} {} {} {}'.format(conda, max_cores,
                                                    self.reference, self.contigs_fasta, pblat_output))

        filtered_fasta = os.path.join(self.output_dp, 'filtered.fasta')
        self.addTask("psl_filter", nCores=max_cores, memMb=max_mem,
             command='source {} && python {} psl_filter -f {} -p {} -o {}'.format(conda, identifier,
                                            self.contigs_fasta, pblat_output, filtered_fasta),
             dependencies=['pblat',])

        rgi_output = os.path.join(self.output_dp, 'rgi_output')
        self.addTask("rgi_screen", nCores=max_cores, memMb=max_mem,
             command='source {} && {} && rgi load --afile {} --local && rgi main -a DIAMOND -n {} -i {} -o {} --local'.format(
                                                        conda, load_py3, card, max_cores, filtered_fasta, rgi_output),
             dependencies=['psl_filter',])

        rgi_txt = rgi_output+'.txt'
        arg_output = os.path.join(self.output_dp, 'predicted_args')
        self.addTask("create_fastas", nCores=max_cores, memMb=max_mem,
            command='source {} && python {} build -r {} -o {}'.format(conda, identifier, rgi_txt, arg_output),
            dependencies=['rgi_screen',])

 
@click.command()
@click.argument('contigs_fasta')
@click.option('--reference', '-r', default=None)
@click.option('--output', '-o', default='./output')
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
    if not reference:
        fp = os.path.dirname(os.path.abspath(__file__))
        reference = os.path.join(fp, 'dependencies/data/card/model/nucleotide_fasta_protein_homolog_model.fasta')

    workflow_runner = Runner(contigs_fasta=contigs_fasta, reference=reference, output_dp=output, mem=mem, ppn=ppn)

    if flux:
        if not account: sys.exit('To attempt a submission to the flux cluster you need to supply an --account/-a')
        if dispatch:
            full_dp = os.path.dirname(os.path.abspath(__file__))
            activate = 'source {}'.format(os.path.join(full_dp, 'dependencies', 'miniconda', 'bin', 'activate'))
            runner_fp = os.path.join(full_dp, 'runner.py')
            qsub = 'qsub -N pyflux_handler -A {} -q fluxm -l nodes=1:ppn=1,mem=2000mb,walltime={}'.format(account, walltime)
            print 'echo "{} && python {} {} -r {} -o {} -a {} -p {} -m {} -w {} --flux --no-dispatch" | {}'.format(activate, runner_fp,
                                               contigs_fasta, reference, output, account, ppn, mem, walltime, qsub)
            call('echo "{} && python {} {} -r {} -o {} -a {} -p {} -m {} -w {} --flux --no-dispatch" | {}'.format(activate, runner_fp,
                                               contigs_fasta, reference, output, account, ppn, mem, walltime, qsub), shell=True)
        else:
            workflow_runner.run(mode='flux', dataDirRoot=log_output_dp, nCores=ppn, memMb=mem,
                                schedulerArgList=['-N', 'arg_identifier',
                                                  '-A', account,
                                                  '-l', 'nodes=1:ppn={},mem={}mb,walltime={}'.format(ppn, mem, walltime)])
    else:
        print 'local mem={} ppn={}'.format(mem, ppn)
        workflow_runner.run(mode='local', dataDirRoot=log_output_dp, nCores=ppn, memMb=mem)


if __name__ == "__main__":
    runner()
