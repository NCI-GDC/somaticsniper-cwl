class: CommandLineTool
cwlVersion: v1.0
id: prepare_site_list
requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/somaticsniper-tool:1.0.5.0
  - class: InitialWorkDirRequirement
    listing:
      - entry: $(inputs.vcf)
        entryname: $(inputs.vcf.basename)
        writable: True
doc: |
  SomaticSniper builtin "prepare_for_readcount.pl".

inputs:
  vcf:
    type: File
    inputBinding:
      position: 1
      prefix: --snp-file
      valueFrom: $(self.basename)

outputs:
  output:
    type: File
    outputBinding:
      glob: $(inputs.vcf.basename + '.pos')

baseCommand: ['perl', '/home/ubuntu/bin/somatic-sniper-1.0.5.0/src/scripts/prepare_for_readcount.pl']
