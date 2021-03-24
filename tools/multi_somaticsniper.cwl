class: CommandLineTool
cwlVersion: v1.0
id: multi_somaticsniper
requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/somaticsniper-tool:1.0.0-71.aeca01f
doc: |
    Multithreading on SomaticSniper (v1.0.5).

inputs:
  normal_input:
    type: File
    inputBinding:
      prefix: --normal-bam
    secondaryFiles:
     - '.bai'

  tumor_input:
    type: File
    inputBinding:
      prefix: --tumor-bam
    secondaryFiles:
      - '.bai'

  thread_count:
    type: int
    inputBinding:
      prefix: --thread-count

  mpileup:
    type:
      type: array
      items: File
      inputBinding:
        prefix: --mpileup
    doc: mpileup file on t/n pair

  reference:
    type: File
    inputBinding:
      prefix: --reference-path
    doc: human reference genome
    secondaryFiles:
      - '.fai'

  loh:
    type: boolean
    inputBinding:
      prefix: --loh
    default: true
    doc: do not report LOH variants as determined by genotypes (T/F)

  gor:
    type: boolean
    inputBinding:
      prefix: --gor
    default: true
    doc: do not report Gain of Reference variants as determined by genotypes (T/F)

  psc:
    type: boolean
    inputBinding:
      prefix: --psc
    default: false
    doc: disable priors in the somatic calculation. Increases sensitivity for solid tumors (T/F)

  ppa:
    type: boolean
    inputBinding:
      prefix: --ppa
    default: false
    doc: Use prior probabilities accounting for the somatic mutation rate (T/F)


  map_q:
    type: int
    inputBinding:
      prefix: --map-q
    default: 1
    doc: filtering reads with mapping quality less than this value

  base_q:
    type: int
    inputBinding:
      prefix: --base-q
    default: 15
    doc: filtering somatic snv output with somatic quality less than this value

  pps:
    type: float
    inputBinding:
      prefix: --pps
    default: 0.01
    doc: prior probability of a somatic mutation (implies -J)

  theta:
    type: float
    inputBinding:
      prefix: --theta
    default: 0.85
    doc: theta in maq consensus calling model (for -c/-g)

  nhap:
    type: int
    inputBinding:
      prefix: --nhap
    default: 2
    doc: number of haplotypes in the sample

  pd:
    type: float
    inputBinding:
      prefix: --pd
    default: 0.001
    doc: prior of a difference between two haplotypes

  fout:
    type: string
    inputBinding:
      prefix: --out-format
    default: 'vcf'
    doc: output format (classic/vcf/bed)

  timeout:
    type: int?
    inputBinding:
      position: 99
      prefix: --timeout
outputs:
  ANNOTATED_VCF:
    type: File
    outputBinding:
      glob: 'multi_somaticsniper_merged.vcf'

baseCommand: ''
