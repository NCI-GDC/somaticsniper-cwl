'''
Main wrapper script for Somaticsniper (v1.0.5) pipeline
'''
import os
import time
import argparse
import logging
import sys
import uuid
import tempfile
import utils.s3
import utils.pipeline
import datetime
import socket
import json
import string
import postgres.status
import postgres.utils
import postgres.mixins
import glob
from sqlalchemy.exc import NoSuchTableError

def is_nat(x):
    '''
    Checks that a value is a natural number.
    '''
    if int(x) > 0:
        return int(x)
    raise argparse.ArgumentTypeError('%s must be positive, non-zero' % x)

def get_args():
    '''
    Loads the parser
    '''
    # Main parser
    parser = argparse.ArgumentParser(description="Somaticsniper (v1.0.5) Pipeline")
    # Args
    required = parser.add_argument_group("Required input parameters")
    # Metadata from input table
    required.add_argument("--case_id", default=None, help="Case ID, internal production id.")
    required.add_argument("--tumor_gdc_id", default=None, help="Tumor GDC ID, GDC portal id.")
    required.add_argument("--tumor_s3_url", default=None, help="S3_URL, s3 url of the tumor input.")
    required.add_argument("--t_s3_profile", required=True, help="S3 profile name for project tenant.")
    required.add_argument("--t_s3_endpoint", required=True, help="S3 endpoint url for project tenant.")
    required.add_argument("--normal_gdc_id", default=None, help="Normal GDC ID, GDC portal id.")
    required.add_argument("--normal_s3_url", default=None, help="S3_URL, s3 url of the normal input.")
    required.add_argument("--n_s3_profile", required=True, help="S3 profile name for project tenant.")
    required.add_argument("--n_s3_endpoint", required=True, help="S3 endpoint url for project tenant.")
    # Parameters for pipeline
    required.add_argument("--basedir", default="/mnt/SCRATCH/", help="Base directory for computations.")
    required.add_argument("--refdir", required=True, help="Path to reference directory.")
    required.add_argument("--cwl", required=True, help="Path to CWL workflow.")
    required.add_argument("--s3dir", default="s3://", help="S3bin for uploading output files.")
    required.add_argument("--s3_profile", required=True, help="S3 profile name for project tenant.")
    required.add_argument("--s3_endpoint", required=True, help="S3 endpoint url for project tenant.")
    # Parameters for parallelization
    required.add_argument("--block", type=is_nat, default=30000000, help="Parallel block size.")
    required.add_argument('--thread_count', type=is_nat, default=8, help='Threads count.')

    return parser.parse_args()

def run_pipeline(args, statusclass, metricsclass):
    '''
    Executes the CWL pipeline and record status/metrics tables
    '''
    if not os.path.isdir(args.basedir):
        raise Exception("Could not find path to base directory: %s" %args.basedir)
    # Generate a uuid
    output_id = str(uuid.uuid4())
    hostname = socket.gethostname()
    # Get datetime start
    datetime_start = str(datetime.datetime.now())
    # Create directory structure
    jobdir = tempfile.mkdtemp(prefix="{0}_{1}_".format("somaticsniper", str(output_id)), dir=args.basedir)
    workdir = tempfile.mkdtemp(prefix="workdir_", dir=jobdir)
    inputdir = tempfile.mkdtemp(prefix="input_", dir=jobdir)
    resultdir = tempfile.mkdtemp(prefix="result_", dir=jobdir)
    refdir = args.refdir
    # Setup logger
    log_file = os.path.join(resultdir, "{0}.{1}.cwl.log".format("somaticsniper", str(output_id)))
    logger = utils.pipeline.setup_logging(logging.INFO, str(output_id), log_file)
    # Logging inputs
    logger.info("pipeline: somaticsniper")
    logger.info("hostname: {}".format(hostname))
    logger.info("case_id: {}".format(args.case_id))
    logger.info("tumor_gdc_id: {}".format(args.tumor_gdc_id))
    logger.info("normal_gdc_id: {}".format(args.normal_gdc_id))
    logger.info("datetime_start: {}".format(datetime_start))
    # Setup start point
    cwl_start = time.time()
    # Getting refs
    logger.info("getting resources")
    reference_data        = utils.pipeline.load_reference_json()
    reference_fasta_path  = os.path.join(refdir, reference_data["reference_fasta"])
    reference_fasta_fai   = os.path.join(refdir, reference_data["reference_fasta_index"])
    reference_fasta_dict  = os.path.join(refdir, reference_data["reference_fasta_dict"])
    map_q                 = reference_data["map_q"]
    base_q                = reference_data["base_q"]
    loh                   = reference_data["loh"]
    gor                   = reference_data["gor"]
    psc                   = reference_data["psc"]
    ppa                   = reference_data["ppa"]
    pps                   = reference_data["pps"]
    theta                 = reference_data["theta"]
    nhap                  = reference_data["nhap"]
    pd                    = reference_data["pd"]
    fout                  = reference_data["fout"]
    postgres_config       = os.path.join(refdir, reference_data["pg_config"])
    # Logging pipeline info
    cwl_version    = reference_data["cwl_version"]
    docker_version = reference_data["docker_version"]
    logger.info("cwl_version: {}".format(cwl_version))
    logger.info("docker_version: {}".format(docker_version))
    # Download input
    normal_bam = os.path.join(inputdir, os.path.basename(args.normal_s3_url))
    normal_download_exit_code = utils.s3.aws_s3_get(logger, args.normal_s3_url, inputdir,
                                             args.n_s3_profile, args.n_s3_endpoint, recursive=False)
    tumor_bam = os.path.join(inputdir, os.path.basename(args.tumor_s3_url))
    tumor_download_exit_code = utils.s3.aws_s3_get(logger, args.tumor_s3_url, inputdir,
                                             args.t_s3_profile, args.t_s3_endpoint, recursive=False)
    download_end_time = time.time()
    download_time = download_end_time - cwl_start
    if not (normal_download_exit_code != 0 or tumor_download_exit_code != 0):
        logger.info("Download successfully. Normal bam is %s, and tumor bam is %s." % (normal_bam, tumor_bam))
    else:
        cwl_elapsed = download_time
        datetime_end = str(datetime.datetime.now())
        engine = postgres.utils.get_db_engine(postgres_config)
        exit_code_list = [int(normal_download_exit_code), int(tumor_download_exit_code)]
        download_exit_code = next((x for x in exit_code_list if x != 0), None)
        postgres.utils.set_download_error(download_exit_code, logger, engine,
                                          args.case_id, args.tumor_gdc_id, args.normal_gdc_id, output_id,
                                          datetime_start, datetime_end,
                                          hostname, cwl_version, docker_version,
                                          download_time, cwl_elapsed, statusclass, metricsclass)
        # Exit
        sys.exit(download_exit_code)
    # Build index
    normal_bam_index = utils.pipeline.get_index(logger, inputdir, normal_bam)
    tumor_bam_index = utils.pipeline.get_index(logger, inputdir, tumor_bam)
    # Create input json
    input_json_list = []
    for i, block in enumerate(utils.pipeline.fai_chunk(reference_fasta_fai, args.blocksize)):
        input_json_file = os.path.join(resultdir, '{0}.{4}.{1}.{2}.{3}.mutect.inputs.json'.format(str(output_id), block[0], block[1], block[2], i))
        input_json_data = {
          "reference": {"class": "File", "path": reference_fasta_path},
          "normal_input": {"class": "File", "path": normal_bam},
          "tumor_input": {"class": "File", "path": tumor_bam},
          "region": "{0}:{1}-{2}".format(block[0], block[1], block[2]),
          "prefix": '{}_{}_{}'.format(block[0], str(block[1]).replace('0000001', '0M1'), utils.pipeline.replace_last(str(block[2]), '000000', 'M', 1)),
          "map_q": map_q,
          "base_q": base_q,
          "loh": loh,
          "gor": gor,
          "psc": psc,
          "ppa": ppa,
          "pps": pps,
          "theta": theta,
          "nhap": nhap,
          "pd": pd,
          "fout": fout
        }
        with open(input_json_file, 'wt') as o:
            json.dump(input_json_data, o, indent=4)
        input_json_list.append(input_json_file)
    logger.info("Preparing input json")
    # Run CWL
    os.chdir(workdir)
    logger.info('Running CWL workflow')
    cmds = list(utils.pipeline.cmd_template(inputdir = inputdir, workdir = workdir, cwl_path = args.cwl, input_json = input_json_list, output_id = output_id))
    ss_cwl_exit = utils.pipeline.multi_commands(cmds, args.thread_count, logger)
    cwl_failure = False
    if ss_cwl_exit:
        cwl_failure = True
    # Compress the outputs and CWL logs
    os.chdir(jobdir)
    output_tar = os.path.join(resultdir, "%s.%s.tar.bz2" % ("somaticsniper", str(output_id)))
    logger.info("Compressing workflow outputs: %s" % (output_tar))
    utils.pipeline.targz_compress(logger, output_tar, os.path.basename(workdir), cmd_prefix=['tar', '-cjvf'])
    upload_dir_location = os.path.join(args.s3dir, str(output_id))
    upload_file_location = os.path.join(upload_dir_location, output_tar)
    # Get md5 and file size
    md5 = utils.pipeline.get_md5(output_tar)
    file_size = utils.pipeline.get_file_size(output_tar)
    # Upload output
    upload_start = time.time()
    logger.info("Uploading workflow output to %s" % (upload_file_location))
    upload_exit  = utils.s3.aws_s3_put(logger, upload_dir_location, resultdir, args.s3_profile, args.s3_endpoint, recursive=True)
    # Establish connection with database
    engine = postgres.utils.get_db_engine(postgres_config)
    # End time
    cwl_end = time.time()
    upload_time = cwl_end - upload_start
    cwl_elapsed = cwl_end - cwl_start
    datetime_end = str(datetime.datetime.now())
    logger.info("datetime_end: %s" % (datetime_end))
    # Get status info
    logger.info("Get status/metrics info")
    status, loc = postgres.status.get_status(upload_exit, cwl_exit, upload_file_location, upload_dir_location, logger)
    # Get metrics info
    time_metrics = utils.pipeline.get_time_metrics(log_file)
    # Set status table
    logger.info("Updating status")
    postgres.utils.add_pipeline_status(engine, args.case_id, args.tumor_gdc_id, args.normal_gdc_id, output_id,
                                       status, loc, datetime_start, datetime_end,
                                       md5, file_size, hostname, cwl_version, docker_version, statusclass)
    # Set metrics table
    logger.info("Updating metrics")
    postgres.utils.add_pipeline_metrics(engine, args.case_id, args.tumor_gdc_id, args.normal_gdc_id, download_time,
                                        upload_time, str(args.thread_count), cwl_elapsed,
                                        sum(time_metrics['system_time']),
                                        sum(time_metrics['user_time']),
                                        sum(time_metrics['wall_clock']),
                                        sum(time_metrics['percent_of_cpu']),
                                        sum(time_metrics['maximum_resident_set_size']),
                                        status, metricsclass)
    # Remove job directories, upload final log file
    logger.info("Uploading main log file")
    utils.s3.aws_s3_put(logger, upload_dir_location + '/' + os.path.basename(log_file), log_file, args.s3_profile, args.s3_endpoint, recursive=False)
    #utils.pipeline.remove_dir(jobdir)

if __name__ == '__main__':
    # Get args
    args = get_args()
    # Setup postgres classes
    class SomaticsniperStatus(postgres.mixins.StatusTypeMixin, postgres.utils.Base):
        __tablename__ = 'somaticsniper_vc_cwl_status'
    class SomaticsniperMetrics(postgres.mixins.MetricsTypeMixin, postgres.utils.Base):
        __tablename__ = 'somaticsniper_vc_cwl_metrics'
    # Run pipeline
    run_pipeline(args, SomaticsniperStatus, SomaticsniperMetrics)
