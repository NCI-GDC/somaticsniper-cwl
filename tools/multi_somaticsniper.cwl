#!/usr/bin/env cwl-runner

cwlVersion: v1.0

doc: |
    Run multithreading Somaticsniper (v1.0.5) pipeline

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/multi_somaticsniper:1.2

inputs:
  normal_input:
    type: File
    inputBinding:
      prefix: -n
    secondaryFiles:
     - '.bai'

  tumor_input:
    type: File
    inputBinding:
      prefix: -t
    secondaryFiles:
      - '.bai'

  thread_count:
    type: int
    inputBinding:
      prefix: -c

  mpileup:
    type:
      type: array
      items: File
      inputBinding:
        prefix: -m
    doc: mpileup file on t/n pair

  reference:
    type: File
    inputBinding:
      prefix: -f
    doc: human reference genome
    secondaryFiles:
      - '.fai'

  map_q:
    type: int
    inputBinding:
      prefix: -q
    default: 1
    doc: filtering reads with mapping quality less than this value

  base_q:
    type: int
    inputBinding:
      prefix: -Q
    default: 15
    doc: filtering somatic snv output with somatic quality less than this value

  loh:
    type: boolean
    inputBinding:
      prefix: -L
    default: true
    doc: do not report LOH variants as determined by genotypes (T/F)

  gor:
    type: boolean
    inputBinding:
      prefix: -G
    default: true
    doc: do not report Gain of Reference variants as determined by genotypes (T/F)

  psc:
    type: boolean
    inputBinding:
      prefix: -p
    default: false
    doc: disable priors in the somatic calculation. Increases sensitivity for solid tumors (T/F)

  ppa:
    type: boolean
    inputBinding:
      prefix: -J
    default: false
    doc: Use prior probabilities accounting for the somatic mutation rate (T/F)

  pps:
    type: float
    inputBinding:
      prefix: -s
    default: 0.01
    doc: prior probability of a somatic mutation (implies -J)

  theta:
    type: float
    inputBinding:
      prefix: -T
    default: 0.85
    doc: theta in maq consensus calling model (for -c/-g)

  nhap:
    type: int
    inputBinding:
      prefix: -N
    default: 2
    doc: number of haplotypes in the sample

  pd:
    type: float
    inputBinding:
      prefix: -r
    default: 0.001
    doc: prior of a difference between two haplotypes

  fout:
    type: string
    inputBinding:
      prefix: -F
    default: 'vcf'
    doc: output format (classic/vcf/bed)

outputs:
  ANNOTATED_VCF:
    type: File[]
    outputBinding:
      glob: '*.annotated.vcf'

baseCommand: ['python', '/bin/multi_somaticsniper.py']
