#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement
  - class: SubworkflowFeatureRequirement

inputs:
  - id: normal_input
    type: File
    doc: normal input bam for samtools splitting
  - id: tumor_input
    type: File
    doc: tumor input bam for samtools splitting
  - id: region
    type: string
    doc: "chromosomes region for samtools splitting (e.g chr1:1-3000)"
  - id: reference
    type: File
    doc: human reference genome
  - id: prefix
    type: string
    doc: prefix for outputs
  - id: map_q
    type: string
    default: '0'
    doc: filtering reads with mapping quality less than this value
  - id: base_q
    type: string
    default: '15'
    doc: filtering somatic snv output with somatic quality less than this value
  - id: loh
    type: boolean
    default: false
    doc: do not report LOH variants as determined by genotypes (T/F)
  - id: gor
    type: boolean
    default: false
    doc: do not report Gain of Reference variants as determined by genotypes (T/F)
  - id: psc
    type: boolean
    default: false
    doc: disable priors in the somatic calculation. Increases sensitivity for solid tumors (T/F)
  - id: ppa
    type: boolean
    default: false
    doc: Use prior probabilities accounting for the somatic mutation rate (T/F)
  - id: pps
    type: string
    default: '0.01'
    doc: prior probability of a somatic mutation (implies -J)
  - id: theta
    type: string
    default: '0.85'
    doc: theta in maq consensus calling model (for -c/-g)
  - id: nhap
    type: string
    default: '2'
    doc: number of haplotypes in the sample
  - id: pd
    type: string
    default: '0.001'
    doc: prior of a difference between two haplotypes
  - id: fout
    type: string
    default: 'vcf'
    doc: output format (classic/vcf/bed)

outputs:
  - id: RAW_VCF
    type: File
    outputSource: somaticsniper_calling/output
  - id: POST_LOH_VCF
    type: File
    outputSource: filteration_workflow/POST_LOH_FILTER
  - id: POST_FP_PASS_VCF
    type: File
    outputSource: filteration_workflow/POST_FP_FILTER_PASS
  - id: POST_FP_FAIL_VCF
    type: File
    outputSource: filteration_workflow/POST_FP_FILTER_FAIL
  - id: POST_HC_VCF
    type: File
    outputSource: filteration_workflow/POST_HC_FILTER
  - id: SITE_LIST
    type: File
    outputSource: filteration_workflow/SITE_LIST
  - id: READCOUNT
    type: File
    outputSource: filteration_workflow/READCOUNT

steps:
  - id: samtools_workflow
    run: samtools_workflow.cwl.yaml
    in:
      - id: normal_input
        source: normal_input
      - id: tumor_input
        source: tumor_input
      - id: region
        source: region
      - id: reference
        source: reference
      - id: prefix
        source: prefix
    out:
      - id: normal_chunk
      - id: tumor_chunk
      - id: chunk_mpileup

  - id: somaticsniper_calling
    run: ../tools/somaticsniper_tool.cwl.yaml
    in:
      - id: ref
        source: reference
      - id: map_q
        source: map_q
      - id: base_q
        source: base_q
      - id: loh
        source: loh
      - id: gor
        source: gor
      - id: psc
        source: psc
      - id: ppa
        source: ppa
      - id: pps
        source: pps
      - id: theta
        source: theta
      - id: nhap
        source: nhap
      - id: pd
        source: pd
      - id: fout
        source: fout
      - id: normal
        source: samtools_workflow/normal_chunk
      - id: tumor
        source: samtools_workflow/tumor_chunk
      - id: out
        source: prefix
        valueFrom: $(self + '.raw.vcf')
    out:
      - id: output

  - id: filteration_workflow
    run: filteration_workflow.cwl.yaml
    in:
      - id: vcf
        source: somaticsniper_calling/output
      - id: pileup
        source: samtools_workflow/chunk_mpileup
      - id: base_q
        source: base_q
      - id: reference
        source: reference
      - id: tumor_bam
        source: samtools_workflow/tumor_chunk
      - id: prefix
        source: prefix
    out:
      - id: POST_LOH_FILTER
      - id: POST_FP_FILTER_PASS
      - id: POST_FP_FILTER_FAIL
      - id: POST_HC_FILTER
      - id: SITE_LIST
      - id: READCOUNT
