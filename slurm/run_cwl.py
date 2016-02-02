import argparse
import pipelineUtil
import uuid
import os
import postgres

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
    index = os.path.join(basedir, "index")
    workdir = os.path.join(basedir, "workdir")
    inp = os.path.join(basedir, "input")
    os.mkdir(index)
    os.mkdir(workdir)
    os.mkdir(inp)

    #generate a random uuid
    vcf_uuid = uuid.uuid4()

    #setup logger
    log_file = "%s.somaticsniper.cwl.log" %vcf_uuid
    logger = setupLog.setup_logging(logging.INFO, vcf_uuid, log_file)

    #download bam files
    reference = os.path.join(index, "GRCh38.d1.vd1.fa")
    if not os.path.isfile(reference):
        pipelineUtil.download_from_cleversafe(logger, args.ref, index)
        reference = os.path.join(index, os.path.basename(args.ref))

    reference_index = os.path.join(index, "GRCh38.d1.vd1.fa.fai")
    if not  os.path.isfile(reference_index):
        pipelineUtil.download_from_cleversafe(logger, args.refindex, index)
        reference_index = os.path.join(index, os.path.basename(args.refindex))

    pipelineUtil.download_from_cleversafe(logger, args.normal, inp)
    bam_norm = os.path.join(inp, os.path.basename(args.normal))

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
            "--snp","%s.snp" %uuid_vcf
            ]

    pipelineUtil.run_command(cmd, logger)

    #upload results to s3
    s3dir = 's3://bioinformatics_scratch/ss_cwl_test/'
    pipelineUtil.upload_to_cleversafe(logger, os.path.join(s3dir, "snp_test"), os.path.join(workdir, "%s.snp" %uuid_vcf))
    pipelineUtil.upload_to_cleverasfe(logger, os.path.join(s3dir, "test_log"), log_file)

    #update results on postgres


