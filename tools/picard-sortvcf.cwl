#!/usr/bin/env cwl-runner

cwlVersion: v1.0

requirements:
  - $import: envvar-global.cwl
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: quay.io/shenglai/picard-sortvcf-tool:1.0a

class: CommandLineTool

inputs:
  - id: host
    type: string
    doc: Host ip for postgres database server.
    inputBinding:
      prefix: "--host"

  - id: vcf_path
    doc: Scattered outputs from Genotypegvcfs.
    type:
      type: array
      items: File
      inputBinding:
        prefix: "--vcf_path"

  - id: output_vcf
    type: string
    doc: File name for output vcf. Must be compressed. (e.g. output.vcf.gz)
    inputBinding:
      prefix: --output_vcf

  - id: reference_fasta_dict
    type: File
    doc: Dict file from human reference genome. (picard create index)
    inputBinding:
      prefix: --reference_fasta_dict

  - id: case_id
    type: string
    doc: Case id.
    inputBinding:
      prefix: --case_id

  - id: postgres_config
    type: File
    doc: Postgres config file.
    inputBinding:
      prefix: --postgres_config

outputs:
  - id: output_sorted_vcf
    type: File
    doc: Sorted vcf file.
    outputBinding:
      glob: $(inputs.output_vcf)
    secondaryFiles:
      - ".tbi"

  - id: log
    type: File
    doc: python log file
    outputBinding:
      glob: $(inputs.case_id+"_picard_sortvcf.log")

baseCommand: ["/home/ubuntu/.virtualenvs/p3/bin/python","/home/ubuntu/tools/picard_tool/main.py"]
