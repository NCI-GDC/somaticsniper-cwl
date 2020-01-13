# GDC SomaticSniper CWL
![Version badge](https://img.shields.io/badge/SomaticSniper-1.0.5.0-<COLOR>.svg)

The purpose of SomaticSniper is to identify single nucleotide positions that are different between tumor and normal. It takes a tumor bam and a normal bam and compares the two to determine the differences.

Original SomaticSniper: http://gmt.genome.wustl.edu/packages/somatic-sniper/index.html

## Docker

All the docker images are built from `Dockerfile`s at https://github.com/NCI-GDC/somaticsniper-tool.

## CWL

https://www.commonwl.org/

The CWL are tested under multiple `cwltools` environments. The most tested one is:
* cwltool 1.0.20180306163216


## For external users

There is a production-ready GDC CWL workflow at https://github.com/NCI-GDC/gdc-somatic-variant-calling-workflow, which uses this repo as a git submodule.

Please notice that you may want to change the docker image host of `dockerPull:` for each CWL.

To use CWL directly from this repo, we recommend to run
* `tools/multi_somaticsniper.cwl` on an array of tumor/normal mpileup files.

To run CWL:

```
>>>>>>>>>>Multi SomaticSniper<<<<<<<<<<
cwltool tools/multi_somaticsniper.cwl  -h
/home/ubuntu/.virtualenvs/p2/bin/cwltool 1.0.20180306163216
Resolved 'tools/multi_somaticsniper.cwl' to 'file:///mnt/SCRATCH/githubs/submodules/s/somaticsniper-cwl/tools/multi_somaticsniper.cwl'
usage: tools/multi_somaticsniper.cwl [-h] [--base_q BASE_Q] [--fout FOUT]
                                     [--gor] [--loh] [--map_q MAP_Q] --mpileup
                                     MPILEUP [--nhap NHAP] --normal_input
                                     NORMAL_INPUT [--pd PD] --ppa [--pps PPS]
                                     --psc --reference REFERENCE
                                     [--theta THETA] --thread_count
                                     THREAD_COUNT --tumor_input TUMOR_INPUT
                                     [job_order]

positional arguments:
  job_order             Job input json file

optional arguments:
  -h, --help            show this help message and exit
  --base_q BASE_Q       filtering somatic snv output with somatic quality less
                        than this value
  --fout FOUT           output format (classic/vcf/bed)
  --gor                 do not report Gain of Reference variants as determined
                        by genotypes (T/F)
  --loh                 do not report LOH variants as determined by genotypes
                        (T/F)
  --map_q MAP_Q         filtering reads with mapping quality less than this
                        value
  --mpileup MPILEUP     mpileup file on t/n pair
  --nhap NHAP           number of haplotypes in the sample
  --normal_input NORMAL_INPUT
  --pd PD               prior of a difference between two haplotypes
  --ppa                 Use prior probabilities accounting for the somatic
                        mutation rate (T/F)
  --pps PPS             prior probability of a somatic mutation (implies -J)
  --psc                 disable priors in the somatic calculation. Increases
                        sensitivity for solid tumors (T/F)
  --reference REFERENCE
                        human reference genome
  --theta THETA         theta in maq consensus calling model (for -c/-g)
  --thread_count THREAD_COUNT
  --tumor_input TUMOR_INPUT
```

## For GDC users

See https://github.com/NCI-GDC/gdc-somatic-variant-calling-workflow.
