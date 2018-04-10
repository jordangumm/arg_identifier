import os, sys
import click

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
        conda = os.path.join(fp, './dependencies/miniconda/bin/activate')

        pblat_output = os.path.join(self.output_dp, 'pblat.psl')
        self.addTask("pblat", nCores=self.getNCores(), memMb=self.getMemMb(),
             command='source {} && pblat -threads={} {} {} {}'.format(conda, int(self.getNCores()),
                                            self.contigs_fasta, self.reference, pblat_output))




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
    if not output: output = os.path.join('./', 'bioinfo', 'arg_identifier')
    log_output_dp = os.path.join(output, 'bioinfo', 'logs', 'runner')
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
