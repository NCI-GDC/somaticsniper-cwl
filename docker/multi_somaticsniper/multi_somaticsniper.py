#!/usr/bin/env python
'''Internal multithreading SomaticSniper calling'''

import os
import argparse
import logging
import subprocess
import string
from multiprocessing import Pool
from functools import partial

def is_nat(x):
    '''Checks that a value is a natural number.'''
    if int(x) > 0:
        return int(x)
    raise argparse.ArgumentTypeError('%s must be positive, non-zero' % x)

def setup_logging(level, log_name, log_filename):
    '''Sets up a logger'''
    logger = logging.getLogger(log_name)
    logger.setLevel(level)
    if log_filename is None:
        shell_log = logging.StreamHandler()
    else:
        shell_log = logging.FileHandler(log_filename, mode='w')

    shell_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logger.addHandler(shell_log)
    return logger

def get_region(mpileup):
    '''ger region from mpileup filename'''
    namebase = os.path.basename(mpileup)
    base, ext = os.path.splitext(namebase)
    region = base.replace('-', ':', 1)
    return region, base

def run_command(cmd, logger=None, shell_var=False):
    '''Runs a subprocess'''
    child = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell_var, executable='/bin/bash')
    stdoutdata, stderrdata = child.communicate()
    exit_code = child.returncode
    if logger is not None:
        logger.info(cmd)
        stdoutdata = stdoutdata.split("\n")
        for line in stdoutdata:
            logger.info(line)
        stderrdata = stderrdata.split("\n")
        for line in stderrdata:
            logger.info(line)
    return exit_code

def annotate_filter(raw, post_filter, new):
    filter_pass = '##FILTER=<ID=PASS,Description="Accept as a high confident somatic mutation">'
    filter_reject = '##FILTER=<ID=REJECT,Description="Rejected as an unconfident somatic mutation">'
    filter_loh = '##FILTER=<ID=LOH,Description="Rejected as a loss of heterozygosity">'
    with open(raw, 'rb') as fin:
        line = fin.readlines()
        with open(post_filter, 'rb') as fcom:
            comp = fcom.readlines()
            hc = set(line).intersection(comp)
            with open(new, 'w') as fout:
                for i in line:
                    if i.startswith('##fileformat'):
                        fout.write(i)
                        fout.write('{}\n'.format(filter_pass))
                        fout.write('{}\n'.format(filter_reject))
                        fout.write('{}\n'.format(filter_loh))
                    elif i.startswith('#'):
                        fout.write(i)
                    elif i in hc:
                        new = i.split('\t')
                        new[6] = 'PASS'
                        fout.write('\t'.join(new))
                    elif i.split(':')[-2] == '3':
                        new = i.split('\t')
                        new[6] = 'LOH'
                        fout.write('\t'.join(new))
                    else:
                        new = i.split('\t')
                        new[6] = 'REJECT'
                        fout.write('\t'.join(new))

def somaticsniper(map_q, base_q, pps, theta, nhap, pd, fout, loh, gor, psc, ppa, ref, tumor, normal, mpileup):
    '''run somaticsniper workflow'''
    region, output_base = get_region(mpileup)
    log_file = '{}.somaticsniper.log'.format(output_base)
    logger = setup_logging(logging.INFO, output_base, log_file)
    output = output_base + '.vcf'
    calling_cmd = [
        'bam-somaticsniper',
        '-q', map_q,
        '-Q', base_q,
        '-s', pps,
        '-T', theta,
        '-N', nhap,
        '-r', pd,
        '-F', fout
    ]
    if loh: calling_cmd += ['-L']
    if gor: calling_cmd += ['-G']
    if psc: calling_cmd += ['-p']
    if ppa: calling_cmd += ['-J']
    calling_cmd += [
        '-f', ref,
        '<(samtools view -b {} {})'.format(tumor, region),
        '<(samtools view -b {} {})'.format(normal, region),
        output
    ]
    calling_output = run_command(' '.join(calling_cmd), logger, shell_var=True)
    if calling_output != 0:
        logger.info('Failed on somaticsniper calling')
    else:
        loh_filter_cmd = [
            'perl',
            '/somatic-sniper-1.0.5.0/src/scripts/snpfilter.pl',
            '--snp-file', output,
            '--indel-file', mpileup
        ]
        loh_output = output + '.SNPfilter'
        loh_cmd_output = run_command(' '.join(loh_filter_cmd), logger, shell_var=True)
        if loh_cmd_output != 0:
            logger.info('Failed on LOH filtering')
        else:
            hc_filter_cmd = [
                'perl',
                '/somatic-sniper-1.0.5.0/src/scripts/highconfidence.pl',
                '--snp-file', loh_output
            ]
            hc_output = loh_output + '.hc'
            hc_cmd_output = run_command(' '.join(hc_filter_cmd), logger, shell_var=True)
            if hc_cmd_output != 0:
                logger.info('Failed on HC filtering')
            else:
                annotated_vcf = output_base + '.annotated.vcf'
                annotate_filter(output, hc_output, annotated_vcf)

def main():
    '''main'''
    parser = argparse.ArgumentParser('Internal multithreading SomaticSniper calling.')
    # Required flags.
    parser.add_argument('-f', '--reference_path', required=True, help='Reference path.')
    parser.add_argument('-q', '--map_q', required=True, help='filtering reads with mapping quality less than this value.')
    parser.add_argument('-Q', '--base_q', required=True, help='filtering somatic snv output with somatic quality less than this value.')
    parser.add_argument('-L', '--loh', action="store_true", help='do not report LOH variants as determined by genotypes (T/F).')
    parser.add_argument('-G', '--gor', action="store_true", help='do not report Gain of Reference variants as determined by genotypes (T/F).')
    parser.add_argument('-p', '--psc', action="store_true", help='disable priors in the somatic calculation. Increases sensitivity for solid tumors (T/F).')
    parser.add_argument('-J', '--ppa', action="store_true", help='Use prior probabilities accounting for the somatic mutation rate (T/F).')
    parser.add_argument('-s', '--pps', required=True, help='prior probability of a somatic mutation (implies -J).')
    parser.add_argument('-T', '--theta', required=True, help='theta in maq consensus calling model (for -c/-g).')
    parser.add_argument('-N', '--nhap', required=True, help='number of haplotypes in the sample.')
    parser.add_argument('-r', '--pd', required=True, help='prior of a difference between two haplotypes.')
    parser.add_argument('-F', '--fout', required=True, help='output format (classic/vcf/bed).')
    parser.add_argument('-t', '--tumor_bam', required=True, help='Tumor bam file.')
    parser.add_argument('-n', '--normal_bam', required=True, help='Normal bam file.')
    parser.add_argument('-c', '--thread_count', type=is_nat, required=True, help='Number of thread.')
    parser.add_argument('-m', '--mpileup', action="append", required=True, help='mpileup files.')
    args = parser.parse_args()
    mpileup = args.mpileup
    threads = args.thread_count
    pool = Pool(int(threads))
    output = pool.map(partial(somaticsniper, args.map_q, args.base_q, args.pps, args.theta, args.nhap, args.pd, args.fout, args.loh, args.gor, args.psc, args.ppa, args.reference_path, args.tumor_bam, args.normal_bam), mpileup)

if __name__ == '__main__':
    main()
