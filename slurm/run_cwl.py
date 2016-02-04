import argparse
import pipelineUtil
import uuid
import os
import postgres
import setupLog
import logging
import tempfile

def get_input_file(fromlocation, tolocation, logger):
    """ download a file and return its location"""

    exit_code = pipelineUtil.download_from_cleversafe(logger, fromlocation, tolocation)

    if exit_code:
        raise Exception("Cannot download file: %s" %(fromlocation))

    outlocation = os.path.join(tolocation, os.path.basename(fromlocation))
    return outlocation

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run variant calling CWL")
    required = parser.add_argument_group("Required input parameters")
    required.add_argument("--ref", default=None, help="path to reference genome", required=True)
    required.add_argument("--normal", default=None, help="path to normal bam file", required=True)
    required.add_argument("--tumor", default=None, help="path to tumor bam file", required=True)
    required.add_argument("--normal_id", default=None, help="UUID for normal BAM", required=True)
    required.add_argument("--tumor_id", default=None, help="UUID for tumor BAM", required=True)
    required.add_argument("--case_id", default=None, help="UUID for case", required=True)
    required.add_argument("--username", default=None, help="Username for postgres", required=True)
    required.add_argument("--password", default=None, help="Password for postgres", required=True)
    required.add_argument("--refindex", default=None, help="Path to ref index on object store", required=True)
    required.add_argument("--cwl", default=None, help="Path to CWL code", required=True)

    optional = parser.add_argument_group("Optional input parameters")
    optional.add_argument("--s3dir", default="s3://bioinformatics_scratch/", help="path to output files")
    optional.add_argument("--basedir", default="/mnt/SCRATCH/", help="Base directory for computations")

    args = parser.parse_args()

    if not os.path.isdir(args.basedir):
        raise Exception("Could not find path to base directory: %s" %args.basedir)

    #create directory structure
    casedir = tempfile.mkdtemp(prefix="%s_" %args.case_id, dir=args.basedir)
    workdir = tempfile.mkdtemp(prefix="workdir_", dir=casedir)
    inp = tempfile.mkdtemp(prefix="input_", dir=casedir)
    index = tempfile.mkdtemp(prefix="index_", dir=casedir)

    #generate a random uuid
    vcf_uuid = uuid.uuid4()
    vcf_file = "%s.vcf" %(str(vcf_uuid))

    #setup logger
    log_file = os.path.join(workdir, "%s.somaticsniper.cwl.log" %str(vcf_uuid))
    logger = setupLog.setup_logging(logging.INFO, str(vcf_uuid), log_file)

    #logging inputs
    logger.info("normal_bam_path: %s" %(args.normal))
    logger.info("tumor_bam_path: %s" %(args.tumor))
    logger.info("normal_bam_id: %s" %(args.normal_id))
    logger.info("tumor_bam_id: %s" %(args.tumor_id))
    logger.info("case_id: %s" %(args.case_id))
    logger.info("vcf_id: %s" %(str(vcf_uuid)))

    #download reference file
    logger.info("getting reference: %s" %args.ref)
    reference = get_input_file(args.ref, index, logger)

    #download reference index
    logger.info("getting reference index: %s" %args.refindex)
    reference_index = get_input_file(args.refindex, index, logger)

    #download normal bam
    logger.info("getting normal bam: %s" %args.normal)
    bam_norm = get_input_file(args.normal, inp, logger)

    #download tumor bam
    logger.info("getting tumor bam: %s" %args.tumor)
    bam_tumor = get_input_file(args.tumor, inp, logger)

    os.chdir(workdir)
    #run cwl command
    cmd = ['/home/ubuntu/.virtualenvs/p2/bin/cwl-runner', "--debug", args.cwl,
            "--ref", reference,
            "--normal", bam_norm,
            "--tumor", bam_tumor,
            "--normal_id", args.normal_id,
            "--tumor_id", args.tumor_id,
            "--case_id", args.case_id,
            "--username", args.username,
            "--password", args.password,
            "--snp", vcf_file,
            ]

    cwl_exit = pipelineUtil.run_command(cmd, logger)

    #establish connection with database

    DATABASE = {
        'drivername': 'postgres',
        'host' : 'pgreadwrite.osdc.io',
        'port' : '5432',
        'username': args.username,
        'password' : args.password,
        'database' : 'prod_bioinfo'
    }


    engine = postgres.db_connect(DATABASE)


    if cwl_exit:

        postgres.add_status(engine, args.case_id, str(vcf_uuid), [args.normal_id, args.tumor_id], "FAILED", "unknown")

    #upload results to s3

    snp_location = os.path.join(args.s3dir, 'somaticsniper', str(vcf_uuid))
    vcf_upload_location = os.path.join(snp_location, vcf_file)

    ec_1 = pipelineUtil.upload_to_cleversafe(logger, vcf_upload_location, os.path.join(workdir, vcf_file))

    ec_2 = pipelineUtil.upload_to_cleversafe(logger, os.path.join(snp_location, "%s.somaticsniper.cwl.log" %(str(vcf_uuid))), log_file)

    ec_3 = pipelineUtil.upload_to_cleversafe(logger, os.path.join(snp_location, "%s.somaticsniper.log" %(str(vcf_uuid))),
                                             os.path.join(workdir, "%s.somaticsniper.log" %args.case_id))


    if not(ec_1 and ec_2 and ec_3):

        postgres.add_status(engine, args.case_id, str(vcf_uuid), [args.normal_id, args.tumor_id], "COMPLETED", vcf_upload_location)

    else:

        postgres.add_status(engine, args.case_id, str(vcf_uuid), [args.normal_id, args.tumor_id], "FAILED", snp_location)

    #remove work and input directories
    pipelineUtil.remove_dir(casedir)
    #pipelineUtil.remove_dir(index)
    #pipelineUtil.remove_dir(inp)
    #pipelineUtil.remove_dir(workdir)
