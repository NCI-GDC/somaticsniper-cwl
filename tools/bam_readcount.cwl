class: CommandLineTool
cwlVersion: v1.0
id: bam_readcount.cwl
requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/bam_readcount:0.8.0
doc: |
  Caluclate BAM readcount.

inputs:
  base_q:
    type: string
    default: '15'
    inputBinding:
      position: 1
      prefix: -b

  ref:
    type: File
    inputBinding:
      position: 2
      prefix: -f
    secondaryFiles:
      - '.fai'

  site_list:
    type: File
    inputBinding:
      position: 3
      prefix: -l

  tumor_bam:
    type: File
    inputBinding:
      position: 4
    secondaryFiles:
      - '.bai'

  out_name:
    type: string
    inputBinding:
      position: 5
      prefix: '>'

outputs:
  output:
    type: File
    outputBinding:
      glob: $(inputs.out_name)

baseCommand: ['bam-readcount']
