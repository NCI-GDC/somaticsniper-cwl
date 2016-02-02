#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --workdir=/mnt/scratch/

normal="XX_NORMAL_BAM_PATH_XX"
tumor="XX_TUMOR_BAM_PATH_XX"
normal_id="XX_NORMAL_GDC_ID_XX"
tumor_id="XX_TUMOR_GDC_ID_XX"
case_id="XX_CASE_ID_XX"

deploy_key="s3://bioinformatics_scratch/deploy_key/coclean_cwl_deploy_rsa"
basedir="/mnt/SCRATCH/test"
ref="s3://bioinformatics_scratch/GRCh38.d1.vd1.fa"
refindex="s3://bioinformatics_scratch/GRCh38.v1.d1.fa.fai"
username="username"
password="password"
repository="https://github.com/NCI-GDC/somaticsniper-cwl.git"

cwl="${HOME}/nci-gdc/somaticsniper-cwl/tools/somaticsniper-tool.cwl.yaml"


#function clone_cwl
#{
#    export http_proxy=http://cloud-proxy:3128; export https_proxy=http://cloud-proxy:3128;
#    cd ${DATA}
#    #check if key is in known hosts
#    ssh-keygen -H -F github.com | grep "Host github.com found: line 1 type RSA" -
#    if [ $? -q 0 ]
#    then
#        git clone -b slurm $repository
#    else # if not known, get key, check it, then add it
#        ssh-keyscan github.com >> githubkey
#        echo `ssh-keygen -lf githubkey` | grep 16:27:ac:a5:76:28:2d:36:63:1b:56:4d:eb:df:a6:48
#        if [ $? -q 0 ]
#        then
#            cat githubkey >> ${HOME}/.ssh/known_hosts
#            git clone -b slurm $repository
#        else
#            echo "Improper github key:  `ssh-keygen -lf githubkey`"
#            exit 1
#        fi
#    fi
#}

echo "get cwl"
#clone_cwl()

/usr/bin/python /home/ubuntu/somaticsniper-cwl/slurm/run_cwl.py --ref $ref --refindex $refindex --normal $normal --tumor $tumor --normal_id $normal_id --tumor_id $tumor_id --case_id $case_id --username $username --password $password --basedir $basedir --cwl $cwl
