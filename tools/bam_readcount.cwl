#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: quay.io/shenglai/bam_readcount:1.0

inputs:
  - id: base_q
    type: string
    default: '15'
    inputBinding:
      position: 1
      prefix: -b

  - id: ref
    type: File
    inputBinding:
      position: 2
      prefix: -f
    secondaryFiles:
      - '.fai'

  - id: site_list
    type: File
    inputBinding:
      position: 3
      prefix: -l

  - id: tumor_bam
    type: File
    inputBinding:
      position: 4
    secondaryFiles:
      - '.bai'

  - id: out
    type: string
    inputBinding:
      position: 5
      prefix: '>'

outputs:
  - id: output
    type: File
    outputBinding:
      glob: $(inputs.out)

baseCommand: ['bam-readcount']
