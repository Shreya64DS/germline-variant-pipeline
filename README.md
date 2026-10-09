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

FASTQ → FastQC 0.12.1 → fastp 1.3.7 → BWA-MEM 0.7.19 → samtools 1.20 →
GATK 4.6.2 MarkDuplicates → BQSR → HaplotypeCaller → VariantFiltration →
mosdepth 0.3.8 → RTG vcfeval 3.12 → Ensembl VEP (REST API) → 7 candidate variants

BQSR onwards runs on chr20 only. Alignment uses the whole genome, because aligning to a
single chromosome would force reads from paralogous regions elsewhere onto chr20 and
create false variants.

## Results

### QC and alignment

| Metric | Value |
|---|---|
| Input read pairs | 20,203,002 |
| Retained after trimming | 19,096,781 (94.5%) |
| Reads with adapter trimmed | 4,733,470 (12.4%) |
| Insert size peak | 140 bp |
| Mapped | 99.997% |
| Properly paired | 99.46% |
| Duplicate rate | 6.12% |
| Bases at >=10x on chr20 | 1,816,338 (2.82%) |

### Benchmark (chr20, GIAB high-confidence ∩ callable, 1,709,535 bp)

| Call set | TP | FP | FN | Precision | Recall |
|---|---|---|---|---|---|
| PASS only | 1,263 | 7 | 152 | 0.9945 | 0.8926 |
| PASS + MQ40 restored | 1,264 | 8 | 151 | 0.9937 | 0.8933 |
| PASS + SOR3 restored | 1,394 | 9 | 21 | 0.9936 | 0.9852 |
| All records | 1,400 | 13 | 15 | 0.9908 | 0.9894 |

Indels (PASS): precision 0.7845, recall 0.8922.

137 of the 152 missed SNPs had been called correctly and then filtered out. Restoring
SOR3-filtered calls recovers 131 of them for 2 false positives; restoring MQ40-filtered
calls recovers 1 out of 224. SOR measures strand bias, which is a reliable artifact
signal in whole-genome data but not in hybrid capture, where probes bind non-randomly
and real strand imbalance appears at target edges.

### Prioritization

| Stage | Remaining |
|---|---|
| Raw calls | 7,491 |
| PASS | 6,896 |
| DP >= 10 and GQ >= 20 | 1,892 |
| Rare (AF < 1%) and HIGH/MODERATE impact | 7 |

The DP/GQ gate removes 73% of PASS calls. None of GATK's hard filters examine read depth
or genotype quality, so a two-read call can satisfy all of them. This also explains the
1,547 calls with no population frequency: of the 907 that also lacked an rsID, 901 had
DP < 10. Apparent novelty here tracks thin coverage, not new biology.

Final candidates: DEFB125, CTSA, ARFGEF2, CASS4, CIMIP1, DIDO1, GMEB2. All heterozygous,
none actionable, which is the expected result for a healthy sample. Two ClinVar
"pathogenic" matches (PRNP, JAG1) were resolved as annotation artifacts — see the report.

## Repository layout

workflow/vep_rest.py — annotation via the Ensembl REST API
report/REPORT.md — full write-up
docs/results/ — benchmark summaries and QC metrics

## Reproducing

All inputs are public: FASTQs from GIAB (the `s3://giab` AWS mirror was roughly seven
times faster than the NCBI FTP endpoint), GRCh38 no-alt from NCBI, known-sites VCFs from
the Broad resource bundle, and the v4.2.1 truth set from the GIAB release directory.
Annotation uses the public Ensembl REST API, so no local cache is required.

## Limitations

One lane of two, chr20 only, hard filters rather than VQSR, REST-based annotation
(frequencies are per-site maxima and should be re-checked per variant), and no CADD,
REVEL or gnomAD constraint data.
