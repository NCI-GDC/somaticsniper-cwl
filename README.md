GDC Somaticsniper (v1.0.5) pipeline
---
Python Wrapper

```
/home/ubuntu/.virtualenvs/p2/bin/python slurm/gdc_somaticsniper_pipeline.py -h
```

CWL

1.  For filtering with builtin scripts
```
/home/ubuntu/.virtualenvs/p2/bin/cwltool workflow/filteration_workflow.cwl -h
```
2. For whole pipeline from bam splitting to variant calling and filtering
```
/home/ubuntu/.virtualenvs/p2/bin/cwltool workflow/somaticsniper_workflow.cwl workflow/template_input.json
```
Note: The scattered outputs from workflow should be sorted and merged by `tools/picard-sortvcf.cwl`.

Docker

Dockerfiles for CWL tools could be found at `docker/`
