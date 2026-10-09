# germline-variant-pipeline

Germline short-variant calling on exome data: FASTQ to annotated, prioritized variants,
benchmarked against the GIAB truth set.

**Headline result:** 99.45% SNP precision, and a measurement showing that GATK's
recommended `SOR > 3.0` filter discards 131 true SNPs to remove 2 false ones on
capture-based exome data — a 9.3-point recall loss for 0.1 points of precision.

Full write-up: [report/REPORT.md](report/REPORT.md)

## Dataset

| Item | Value |
|---|---|
| Sample | NA12878 / HG001 (Genome in a Bottle) |
| Sequencing centre | Garvan Institute of Medical Research |
| Instrument | Illumina HiSeq 2500 |
| Reads | 2 × 101 bp, paired-end |
| Capture kit | Nextera Rapid Capture Expanded Exome |
| Library / lanes | NIST7035, lane L001 only |
| Reference | GRCh38, no-alt analysis set |
| Truth set | GIAB v4.2.1 (GRCh38) |

HG001 was chosen because a validated truth set exists for it, so the pipeline can be
measured rather than just run.

## Pipeline
