# HG001 chr20 germline variant calling

Exome data for GIAB sample HG001 (NA12878), FASTQ to annotated variants, benchmarked
against the GIAB v4.2.1 truth set.

## Data

NA12878 / HG001, Garvan HiSeq 2500, Nextera Rapid Capture Expanded Exome, 2 × 101 bp.
Library NIST7035, lane L001 only (the second lane was skipped to keep the download
manageable). Aligned to GRCh38 no-alt.

## Pipeline

fastp → BWA-MEM → samtools sort → GATK MarkDuplicates → BQSR → HaplotypeCaller →
hard filters → RTG vcfeval → VEP (REST API).

Alignment used the whole genome; recalibration, calling and benchmarking were
restricted to chr20. Aligning to a single chromosome would push reads from similar
regions elsewhere onto chr20 and create false variants.

## QC

| | |
|---|---|
| Read pairs in / out of fastp | 20,203,002 → 19,096,781 (94.5%) |
| Reads with adapter trimmed | 4,733,470 (12.4%) |
| Insert size peak | 140 bp |
| Mapped | 99.997% |
| Properly paired | 99.46% |
| Duplicate rate | 6.12% |
| Bases at ≥10x on chr20 | 1,816,338 (2.82%) |

The 140 bp insert with 101 bp reads explains the adapter content: many fragments are
shorter than the read, so the sequencer runs off the end of the DNA into the adapter.

## Calls

7,491 raw calls on chr20 (6,708 SNPs, 783 indels). Hard filtering removed 595, leaving
6,896 PASS.

| Filter | Removed |
|---|---|
| SOR3 (strand bias) | 321 |
| MQ40 (mapping quality) | 224 |
| QD2 | 33 |
| Combinations | 17 |

## Benchmark

`rtg vcfeval`, inside regions that are both GIAB high-confidence and covered at ≥10x
here (1,709,535 bp).

**SNPs**

| Call set | TP | FP | FN | Precision | Recall |
|---|---|---|---|---|---|
| PASS only | 1,263 | 7 | 152 | 0.9945 | 0.8926 |
| PASS + MQ40 restored | 1,264 | 8 | 151 | 0.9937 | 0.8933 |
| PASS + SOR3 restored | 1,394 | 9 | 21 | 0.9936 | 0.9852 |
| All records | 1,400 | 13 | 15 | 0.9908 | 0.9894 |

**Indels (PASS):** TP 91, FP 25, FN 11, precision 0.7845, recall 0.8922.

Precision is good, recall is not. 137 of the 152 missed SNPs had been called correctly
and then filtered out. Splitting the filters apart shows SOR3 is responsible: restoring
those calls recovers 131 true positives and adds 2 false ones. Restoring MQ40 calls
recovers 1 out of 224, so that filter is working as intended.

SOR measures strand bias, which is a good artifact signal in whole-genome data where
fragments land randomly. Capture probes don't bind randomly, so real strand imbalance
shows up at target edges. The WGS-tuned threshold is too strict here.

Indels are worse than SNPs, mostly on precision. Indels in repeats are harder to
sequence and harder to align, and one lane of coverage doesn't help.

## Prioritization

| Stage | Remaining |
|---|---|
| Raw | 7,491 |
| PASS | 6,896 |
| DP ≥ 10 and GQ ≥ 20 | 1,892 |
| Rare (AF < 1% or absent) and HIGH/MODERATE impact | 7 |

The DP/GQ gate removes 73% of PASS calls. None of GATK's hard filters look at depth or
genotype quality, so a two-read call can pass all of them. This also explains the 1,547
calls with no population frequency: of the 907 that also had no rsID, 901 had DP < 10.
Apparent novelty here is thin coverage, not new biology.

The 7 candidates: DEFB125, CTSA, ARFGEF2, CASS4, CIMIP1, DIDO1, GMEB2. All heterozygous,
all well covered, none actionable. No gene has a second hit. DIDO1 is the only HIGH
impact one, but the variant sits at the 5th base of the splice donor, the least
constrained position in the motif, so its effect is uncertain rather than damaging.

Two variants matched ClinVar "pathogenic" and both were false alarms. PRNP carries five
contradictory clinical labels at once, which happens when ClinVar reports on a position
with several submitted alleles rather than the one in the sample; at 33% population
frequency it can't be causing a rare disease. JAG1 is synonymous, present in 46% of
people, and fails the quality gate anyway (DP 8, GQ 10).

## Limitations

One lane, chr20 only, hard filters rather than VQSR. Annotation used the Ensembl REST
API rather than a local cache, and frequencies were taken as the maximum across alleles
at a site, so per-variant frequencies should be re-checked before being relied on. No
CADD, REVEL or gene constraint data.

## What I'd change

Add DP and GQ thresholds to the filtering step. Loosen SOR for capture data. Add the
second lane and re-benchmark. Use a local VEP cache. Port the whole thing to Snakemake
so it runs in one command.
