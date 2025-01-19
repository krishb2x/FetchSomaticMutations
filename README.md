# FetchSomaticMutations
Hello, I developed this pipeline as part of an interview assignment to analyze somatic mutations in tumor and normal samples. The design follows specific assignment protocols rather than adhering to clinical NGS standards.
This includes steps for quality control, alignment, mutation calling, background mutation calculation and custom annotation.

# Environment:
Linux-based OS

# Software Requirements:
Snakemake, BWA, Samtools, GATK Mutect2, FastQC, MultiQC, Python3.10, pyvcf.

# Config File:
"The config file contains key parameters used in the pipeline. update before running"
1. input_dir: "InputDir" ## Directory path where input Fastq files are stored.
2. reference_genome: "Ref/Homo_sapiens_assembly19.fasta" ## Path to the reference genome.
3. threads: 10 ## Number of threads allocated for the pipeline.
4. output_dir: "OutputDir" ## Directory path where output files will be saved.
5. normal_sample: "PA221MH-lib09-P19-Norm_S1_L001" ## normal sample id (before _R*_001.fastq.gz) [Illumina paired fastq]
6. tumor_sample: "PA220KH-lib09-P19-Tumor_S2_L001" ## tumor sample id (before _R*_001.fastq.gz) [Illumina paired fastq]
7. ref_file: "file.csv" ## custom annotation file

# Running Steps:
1. Install the Software Requirements
2. Clone the Git repository to your local machine : git clone https://github.com/krishb2x/FetchSomaticMutations
3. Navigate to the directory where you cloned the repository : cd FetchSomaticMutations
4. update the config file
5. run the Trigger.sh file: bash Trigger.sh 

