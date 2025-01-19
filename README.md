# FetchSomaticMutations
Hello, I have developed this pipeline as part of an interview assignment to perform somatic mutation analysis on tumor and normal samples. The design adheres to the specific protocols provided for the assignment, rather than clinical NGS standards. It includes steps for quality control, alignment, mutation calling, and background mutation calculation.

# Software Requirements:
Snakemake, BWA, Samtools, GATK Mutect2, FastQC, MultiQC, Python.

# Config File:
"The config file contains key parameters used in the pipeline. update before running"

input_dir: "InputDir" ## Directory path where input Fastq files are stored.

reference_genome: "Homo_sapiens_assembly19.fasta" ## Path to the reference genome (FASTA format).

threads: 10 ## Number of threads allocated for the pipeline

output_dir: "OutputDir" ## Directory path where output files will be saved

normal_sample: "PA221MH-lib09-P19-Norm_S1_L001" ## normal sample id (before _R*_001.fastq.gz) [Illumina paired fastq]

tumor_sample: "PA220KH-lib09-P19-Tumor_S2_L001" ## tumor sample id (before _R*_001.fastq.gz) [Illumina paired fastq]

