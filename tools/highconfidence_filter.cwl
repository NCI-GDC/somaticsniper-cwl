class: CommandLineTool
cwlVersion: v1.0
id: highconfidence_filter
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
  SomaticSniper builtin highconfidence filter.

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
      glob: $(inputs.vcf.basename + '.hc')

baseCommand: ['perl', '/opt/somatic-sniper-1.0.5.0/src/scripts/highconfidence.pl']
