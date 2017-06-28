import sys
import subprocess
import logging
import os
import shutil
import hashlib
import gzip
import json
import io
from multiprocessing.dummy import Pool, Lock
from itertools import islice

def fai_chunk(fai_path, blocksize):
    #function for getting genome chunk from reference fai file
  seq_map = {}
  with open(fai_path) as handle:
    head = list(islice(handle, 25))
    for line in head:
      tmp = line.split("\t")
      seq_map[tmp[0]] = int(tmp[1])
    for seq in seq_map:
        l = seq_map[seq]
        for i in range(1, l, blocksize):
            yield (seq, i, min(i+blocksize-1, l))

def do_pool_commands(cmd, logger, lock = Lock()):
    logger.info('running chunk call: %s' % cmd)
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_stdout = output.communicate()[1]
    with lock:
        logger.info('contents of output=%s' % output_stdout.decode().format())
    return output.wait()

def multi_commands(cmds, thread_count, logger):
    pool = Pool(int(thread_count))
    output = pool.map(partial(do_pool_commands, logger=logger), cmds)
    return output

def setup_logging(level, log_name, log_filename):
    '''
    Sets up a logger
    '''
    logger = logging.getLogger(log_name)
    logger.setLevel(level)

    if log_filename is None:
        sh = logging.StreamHandler()
    else:
        sh = logging.FileHandler(log_filename, mode='w')

    sh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logger.addHandler(sh)
    return logger

def remove_dir(dirname):
    """ Remove a directory and all it's contents """

    if os.path.isdir(dirname):
        shutil.rmtree(dirname)
    else:
        raise Exception("Invalid directory: %s" % dirname)

def get_file_size(filename):
    ''' Gets file size '''
    fstats = os.stat(filename)
    return fstats.st_size

def get_md5(input_file):
    '''Estimates md5 of file '''
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(input_file, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

def get_time_metrics(time_file):
    ''' Extract time file outputs '''
    time_metrics = {
      "system_time": [],
      "user_time": [],
      "wall_clock": [],
      "percent_of_cpu": [],
      "maximum_resident_set_size": []
    }
    try:
        with open(time_file, "rt") as fh:
            for line in fh:
                line = line.strip()
                if 'User time (seconds):' in line:
                    time_metrics['user_time'].append(float(line.split(':')[4].strip()))
                if 'System time (seconds):' in line:
                    time_metrics['system_time'].append(float(line.split(':')[4].strip()))
                if 'Percent of CPU this job got:' in line:
                    time_metrics['percent_of_cpu'].append(int(line.split(':')[4].strip().rstrip('%')))
                if 'Elapsed (wall clock) time (h:mm:ss or m:ss):' in line:
                    value = ":".join(line.split(":")[7:])
                    #hour case
                    if value.count(':') == 2:
                        hours = int(value.split(':')[0])
                        minutes = int(value.split(':')[1])
                        seconds = float(value.split(':')[2])
                        total_seconds = (hours * 60 * 60) + (minutes * 60) + seconds
                        time_metrics['wall_clock'].append(total_seconds)
                    if value.count(':') == 1:
                        minutes = int(value.split(':')[0])
                        seconds = float(value.split(':')[1])
                        total_seconds = (minutes * 60) + seconds
                        time_metrics['wall_clock'].append(total_seconds)
                if ('Maximum resident set size (kbytes):') in line:
                    time_metrics['maximum_resident_set_size'].append(int(line.split(':')[4].strip()))
    except: pass

    return time_metrics

def get_index(logger, inputdir, input_bam):
    '''build input bam file index'''
    base, ext = os.path.splitext(os.path.basename(input_bam))
    bai_file = os.path.join(inputdir, base) + ".bai"
    index_cmd = ['samtools', 'index', input_bam]
    index_exit = run_command(index_cmd, logger)
    if index_exit == 0:
        logger.info("Build %s index successfully" % os.path.basename(input_bam))
        os.rename(input_bam+".bai", bai_file)
    else:
        logger.info("Failed to build %s index" % os.path.basename(input_bam))
        sys.exit(index_exit)
    return bai_file

def load_reference_json():
    ''' load resource JSON file '''
    reference_json_file = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
        "etc/reference.json")
    dat = {}
    with open(reference_json_file, 'r') as fh:
        dat = json.load(fh)
    return dat

def targz_compress(logger, filename, dirname, cmd_prefix=['tar', '-cjvf']):
    '''
    Runs tar -cjvf
    '''
    cmd = cmd_prefix + [filename, dirname]
    print cmd
    exit_code = run_command(cmd, logger=logger)

    return exit_code