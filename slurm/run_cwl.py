import argparse
import pipelineUtil
import uuid
import os
import postgres
import setupLog
import logging

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run variant calling CWL")
    required = parser.add_argument_group("Required input parameters")
    required.add_argument("--ref", default="/mnt/SRCATCH/index/GRCh38.d1.vd1.fa", help="path to reference genome")
    required.add_argument("--normal", default=None, help="path to normal bam file")
    required.add_argument("--tumor", default=None, help="path to tumor bam file")
    required.add_argument("--normal_id", default=None, help="UUID for normal BAM")
    required.add_argument("--tumor_id", default=None, help="UUID for tumor BAM")
    required.add_argument("--case_id", default=None, help="UUID for case")
    required.add_argument("--username", default=None, help="Username for postgres")
    required.add_argument("--password", default=None, help="Password for postgres")
    required.add_argument("--basedir", default="/mnt/SCRATCH/", help="Base directory for computations")
    required.add_argument("--refindex", default="/mnt/SCRATCH/index/GRCh38.d1.vd1.fa.fai", help="Path to ref index on object store")
    required.add_argument("--cwl", default=None, help="Path to CWL code")

    args = parser.parse_args()

    #create directory structure
    index = os.path.join(args.basedir, "index")
    workdir = os.path.join(args.basedir, "workdir")
    inp = os.path.join(args.basedir, "input")

    if not os.path.isdir(index):
        os.mkdir(index)

    if not os.path.isdir(workdir):
        os.mkdir(workdir)

    if not os.path.isdir(inp):
        os.mkdir(inp)

    #generate a random uuid
    vcf_uuid = uuid.uuid4()
    vcf_file = "%s.snp" %(str(vcf_uuid))

    #setup logger
    log_file = "%s.somaticsniper.cwl.log" %vcf_uuid
    logger = setupLog.setup_logging(logging.INFO, str(vcf_uuid), log_file)

    #download bam files
    reference = os.path.join(index, "GRCh38.d1.vd1.fa")
    if not os.path.isfile(reference):
        print("getting reference")
        pipelineUtil.download_from_cleversafe(logger, args.ref, index)
        reference = os.path.join(index, os.path.basename(args.ref))

    reference_index = os.path.join(index, "GRCh38.d1.vd1.fa.fai")
    if not  os.path.isfile(reference_index):
        print("getting reference index")
        pipelineUtil.download_from_cleversafe(logger, args.refindex, index)
        reference_index = os.path.join(index, os.path.basename(args.refindex))

    print("getting normal bam")
    pipelineUtil.download_from_cleversafe(logger, args.normal, inp)
    bam_norm = os.path.join(inp, os.path.basename(args.normal))

    print("geeting tumor bam")
    pipelineUtil.download_from_cleversafe(logger, args.tumor,  inp)
    bam_tumor = os.path.join(inp, os.path.basename(args.tumor))

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

    pipelineUtil.run_command(cmd, logger)

    #upload results to s3
    s3dir = 's3://bioinformatics_scratch/ss_cwl_test/'
    snp_location = os.path.join(s3dir, 'somaticsniper', str(vcf_uuid))
    ec_1 = pipelineUtil.upload_to_cleversafe(logger, os.path.join(snp_location, vcf_file), os.path.join(workdir, vcf_file))
    ec_2 = pipelineUtil.upload_to_cleversafe(logger, os.path.join(snp_location, "%s.somaticsniper.cwl.log" %(str(vcf_uuid))), log_file)
    ec_3 = pipelineUtil.upload_to_cleversafe(logger, os.path.join(snp_location, "%s.somaticsniper.log" %(str(vcf_uuid))), os.path.join(workdir, "%s.somaticsniper.log" %args.case_id))
    #update results on postgres

    DATABASE = {
        'drivername': 'postgres',
        'host' : 'pgreadwrite.osdc.io',
        'port' : '5432',
        'username': args.username,
        'password' : args.password,
        'database' : 'prod_bioinfo'
    }

    engine = postgres.db_connect(DATABASE)

    if not(ec_1 and ec_2 and ec_3):

        postgres.add_status(engine, args.case_id, str(vcf_uuid), [args.normal_id, args.tumor_id], "COMPLETED", snp_location)

    else:

        postgres.add_status(engine, args.case_id, str(vcf_uuid), [args.normal_id, args.tumor_id], "FAILED", snp_location)

