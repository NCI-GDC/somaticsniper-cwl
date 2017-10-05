#!/usr/bin/env cwl-runner

cwlVersion: v1.0

doc: |
    Run Somaticsniper (v1.0.5) pipeline

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement
  - class: SubworkflowFeatureRequirement

inputs:
  normal_input:
    type: File
    doc: normal input bam for samtools splitting
  tumor_input:
    type: File
    doc: tumor input bam for samtools splitting
  mpileup:
    type: File
    doc: mpileup file on t/n pair
  reference:
    type: File
    doc: human reference genome
  map_q:
    type: int
    default: 1
    doc: filtering reads with mapping quality less than this value
  base_q:
    type: int
    default: 15
    doc: filtering somatic snv output with somatic quality less than this value
  loh:
    type: boolean
    default: true
    doc: do not report LOH variants as determined by genotypes (T/F)
  gor:
    type: boolean
    default: true
    doc: do not report Gain of Reference variants as determined by genotypes (T/F)
  psc:
    type: boolean
    default: false
    doc: disable priors in the somatic calculation. Increases sensitivity for solid tumors (T/F)
  ppa:
    type: boolean
    default: false
    doc: Use prior probabilities accounting for the somatic mutation rate (T/F)
  pps:
    type: float
    default: 0.01
    doc: prior probability of a somatic mutation (implies -J)
  theta:
    type: float
    default: 0.85
    doc: theta in maq consensus calling model (for -c/-g)
  nhap:
    type: int
    default: 2
    doc: number of haplotypes in the sample
  pd:
    type: float
    default: 0.001
    doc: prior of a difference between two haplotypes
  fout:
    type: string
    default: 'vcf'
    doc: output format (classic/vcf/bed)

outputs:
  RAW_VCF:
    type: File
    outputSource: somaticsniper_calling/output
  POST_LOH_VCF:
    type: File
    outputSource: filteration_workflow/POST_LOH_FILTER
  POST_HC_VCF:
    type: File
    outputSource: filteration_workflow/POST_HC_FILTER

steps:
  somaticsniper_calling:
    run: ../tools/somaticsniper_tool.cwl
    in:
      ref: reference
      map_q: map_q
      base_q: base_q
      loh: loh
      gor: gor
      psc: psc
      ppa: ppa
      pps: pps
      theta: theta
      nhap: nhap
      pd: pd
      fout: fout
      normal: normal_input
      tumor: tumor_input
    out:
      - id: output

  filteration_workflow:
    run: filteration_workflow.cwl
    in:
      - id: vcf
        source: somaticsniper_calling/output
      - id: pileup
        source: mpileup
    out:
      - id: POST_LOH_FILTER
      - id: POST_HC_FILTER
