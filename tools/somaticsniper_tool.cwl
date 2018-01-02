#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/somaticsniper-tool:1.0

inputs:
  ref:
    type: File
    doc: FILE REQUIRED reference sequence in the FASTA format
    inputBinding:
      position: 1
      prefix: -f
    secondaryFiles:
      - '.fai'

  map_q:
    type: int
    doc: filtering reads with mapping quality less than this value
    default: 0
    inputBinding:
      position: 2
      prefix: -q

  base_q:
    type: int
    doc: filtering somatic snv output with somatic quality less than this value
    default: 15
    inputBinding:
      position: 3
      prefix: -Q

  loh:
    type: boolean
    doc: do not report LOH variants as determined by genotypes (T/F)
    default: true
    inputBinding:
      position: 4
      prefix: -L

  gor:
    type: boolean
    doc: do not report Gain of Reference variants as determined by genotypes (T/F)
    default: true
    inputBinding:
      position: 5
      prefix: -G

  psc:
    type: boolean
    doc: disable priors in the somatic calculation. Increases sensitivity for solid tumors (T/F)
    default: false
    inputBinding:
      position: 6
      prefix: -p

  ppa:
    type: boolean
    doc: Use prior probabilities accounting for the somatic mutation rate (T/F)
    default: false
    inputBinding:
      position: 7
      prefix: -J

  pps:
    type: float
    doc: prior probability of a somatic mutation (implies -J)
    default: 0.01
    inputBinding:
      position: 8
      prefix: -s

  theta:
    type: float
    doc: theta in maq consensus calling model (for -c/-g)
    default: 0.85
    inputBinding:
      position: 9
      prefix: -T

  nhap:
    type: int
    doc: number of haplotypes in the sample
    default: 2
    inputBinding:
      position: 10
      prefix: -N

  pd:
    type: float
    doc: prior of a difference between two haplotypes
    default: 0.001
    inputBinding:
      position: 11
      prefix: -r

  fout:
    type: string
    doc: output format (classic/vcf/bed)
    default: 'vcf'
    inputBinding:
      position: 12
      prefix: -F

  tumor:
    type: File
    doc: input tumor bam
    inputBinding:
      position: 13
    secondaryFiles:
      - '.bai'

  normal:
    type: File
    doc: input normal bam
    inputBinding:
      position: 14
    secondaryFiles:
      - '.bai'

outputs:
  output:
    type: File
    outputBinding:
      glob: $(inputs.tumor.nameroot + '.raw.vcf')

baseCommand: ['bam-somaticsniper']
arguments:
  - valueFrom: $(inputs.tumor.nameroot + '.raw.vcf')
    position: 99
