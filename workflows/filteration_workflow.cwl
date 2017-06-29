#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  - id: vcf
    type: File
  - id: pileup
    type: File
  - id: base_q
    type: string
  - id: reference
    type: File
  - id: tumor_bam
    type: File
  - id: prefix
    type: string

outputs:
  - id: POST_LOH_FILTER
    type: File
    outputSource: loh_filter/output
  - id: POST_FP_FILTER_PASS
    type: File
    outputSource: fp_filter/output_pass
  - id: POST_FP_FILTER_FAIL
    type: File
    outputSource: fp_filter/output_fail
  - id: POST_HC_FILTER
    type: File
    outputSource: highconfidence_filter/output
  - id: SITE_LIST
    type: File
    outputSource: prepare_site_list/output
  - id: READCOUNT
    type: File
    outputSource: bam_readcount/output

steps:
  - id: loh_filter
    run: ../tools/loh_filter.cwl
    in:
      - id: vcf
        source: vcf
      - id: pileup
        source: pileup
    out:
      - id: output

  - id: prepare_site_list
    run: ../tools/prepare_site_list.cwl
    in:
      - id: vcf
        source: loh_filter/output
    out:
      - id: output

  - id: bam_readcount
    run: ../tools/bam_readcount.cwl
    in:
      - id: base_q
        source: base_q
      - id: ref
        source: reference
      - id: site_list
        source: prepare_site_list/output
      - id: tumor_bam
        source: tumor_bam
      - id: out
        source: prefix
        valueFrom: $(self + '.readcount')
    out:
      - id: output

  - id: fp_filter
    run: ../tools/fp_filter.cwl
    in:
      - id: vcf
        source: loh_filter/output
      - id: readcount
        source: bam_readcount/output
    out:
      - id: output_pass
      - id: output_fail

  - id: highconfidence_filter
    run: ../tools/highconfidence_filter.cwl
    in:
      - id: vcf
        source: fp_filter/output_pass
    out:
      - id: output
