# germline-variant pipel
A reproducible pipeline that takes raw exome sequencing reads and produces a short,
ranked list of biologically meaningful germline variants, with its accuracy measured
against a gold-standard truth set.t-pipeline


Germline variant calling from exome data: FASTQ to annotated, prioritized variants,
benchmarked against the GIAB truth set.

## Dataset

| Item | Value |
|---|---|
| Sample | NA12878 / HG001 (Genome in a Bottle) |
| Sequencing centre | Garvan Institute of Medical Research |
| Instrument | Illumina HiSeq 2500 |
| Reads | 2 x 101 bp, paired-end |
| Capture kit | Nextera Rapid Capture Exome and Expanded Exome |
| Library / lanes | NIST7035, lanes L001 and L002 |
| Reference | GRCh38, no-alt analysis set |
| Truth set | GIAB v4.2.1 (GRCh38) |

#Status

In progress. Documentation is written as each phase is completed.

Total reads: 20,203,002 read pairs (2 x 101 bp)

## Results

SNP calls on chr20, benchmarked against GIAB v4.2.1 inside regions that are both
high-confidence in the truth set and covered at >=10x here:

| Call set | Precision | Recall |
|---|---|---|
| PASS only | 0.9945 | 0.8926 |
| SOR3-filtered calls restored | 0.9936 | 0.9852 |

The SOR > 3.0 filter removed 131 true SNPs and only 2 false ones. Full analysis in
[report/REPORT.md](report/REPORT.md).
