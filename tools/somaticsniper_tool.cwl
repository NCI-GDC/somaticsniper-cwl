#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/somaticsniper-tool:1.0

inputs:
  - id: ref
    type: File
    doc: FILE REQUIRED reference sequence in the FASTA format
    inputBinding:
      position: 1
      prefix: -f
    secondaryFiles:
      - '.fai'

  - id: map_q
    type: int
    doc: filtering reads with mapping quality less than this value
    default: 0
    inputBinding:
      position: 2
      prefix: -q

  - id: base_q
    type: int
    doc: filtering somatic snv output with somatic quality less than this value
    default: 15
    inputBinding:
      position: 3
      prefix: -Q

  - id: loh
    type: boolean
    doc: do not report LOH variants as determined by genotypes (T/F)
    default: true
    inputBinding:
      position: 4
      prefix: -L

  - id: gor
    type: boolean
    doc: do not report Gain of Reference variants as determined by genotypes (T/F)
    default: true
    inputBinding:
      position: 5
      prefix: -G

  - id: psc
    type: boolean
    doc: disable priors in the somatic calculation. Increases sensitivity for solid tumors (T/F)
    default: false
    inputBinding:
      position: 6
      prefix: -p

  - id: ppa
    type: boolean
    doc: Use prior probabilities accounting for the somatic mutation rate (T/F)
    default: false
    inputBinding:
      position: 7
      prefix: -J

  - id: pps
    type: float
    doc: prior probability of a somatic mutation (implies -J)
    default: 0.01
    inputBinding:
      position: 8
      prefix: -s

  - id: theta
    type: float
    doc: theta in maq consensus calling model (for -c/-g)
    default: 0.85
    inputBinding:
      position: 9
      prefix: -T

  - id: nhap
    type: int
    doc: number of haplotypes in the sample
    default: 2
    inputBinding:
      position: 10
      prefix: -N

  - id: pd
    type: float
    doc: prior of a difference between two haplotypes
    default: 0.001
    inputBinding:
      position: 11
      prefix: -r

  - id: fout
    type: string
    doc: output format (classic/vcf/bed)
    default: 'vcf'
    inputBinding:
      position: 12
      prefix: -F

  - id: tumor
    type: File
    doc: input tumor bam
    inputBinding:
      position: 13
    secondaryFiles:
      - '.bai'

  - id: normal
    type: File
    doc: input normal bam
    inputBinding:
      position: 14
    secondaryFiles:
      - '.bai'

  - id: out
    type: string
    doc: output name
    inputBinding:
      position: 15

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.out)

baseCommand: ['bam-somaticsniper']
