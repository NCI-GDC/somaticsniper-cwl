#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - $import: envvar-global.cwl
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/somaticsniper-tool:1.0
  - class: InitialWorkDirRequirement
    listing:
      - entry: $(inputs.vcf)
        entryname: $(inputs.vcf.basename)
        writable: True

inputs:
  - id: vcf
    type: File
    inputBinding:
      position: 1
      prefix: --snp-file
      valueFrom: $(self.basename)

  - id: readcount
    type: File
    inputBinding:
      position: 1
      prefix: --readcount-file

outputs:
  - id: output_pass
    type: File
    outputBinding:
      glob: $(inputs.vcf.basename + '.fp_pass')

  - id: output_fail
    type: File
    outputBinding:
      glob: $(inputs.vcf.basename + '.fp_fail')

baseCommand: ['perl', '/home/ubuntu/bin/somatic-sniper-1.0.5.0/src/scripts/fpfilter.pl']
