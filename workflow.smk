# Load configuration
configfile: "config.yaml"

# Input parameters from the config file
INPUT_DIR = config["input_dir"]
REFERENCE_GENOME = config["reference_genome"]
THREADS = config["threads"]
OUTPUT_DIR = config["output_dir"]
NORMAL_SAMPLE = config["normal_sample"]
TUMOR_SAMPLE = config["tumor_sample"]

# Define the final outputs for the workflow (only for normal and tumor)
rule all:
    input:
        OUTPUT_DIR + "/fastqc/multiqc_report.html",
        OUTPUT_DIR + "/alignment/" + NORMAL_SAMPLE + ".sorted.bam",
        OUTPUT_DIR + "/alignment/" + TUMOR_SAMPLE + ".sorted.bam",
        OUTPUT_DIR + "/mutations/" + TUMOR_SAMPLE + "_somatic_mutations_filtered.vcf",
        OUTPUT_DIR + "/mutations/" + TUMOR_SAMPLE + "_background_mutation_stats.txt",
        OUTPUT_DIR + "/mutations/" + TUMOR_SAMPLE + "_somatic_mutations.tsv"

# FastQC rule
rule fastqc:
    input:
        r1=INPUT_DIR + "/" + NORMAL_SAMPLE + "_R1_001.fastq.gz",
        r2=INPUT_DIR + "/" + NORMAL_SAMPLE + "_R2_001.fastq.gz"
    output:
        html_r1=OUTPUT_DIR + "/fastqc/" + NORMAL_SAMPLE + "_R1_001_fastqc.html",
        html_r2=OUTPUT_DIR + "/fastqc/" + NORMAL_SAMPLE + "_R2_001_fastqc.html"
    threads: THREADS
    shell:
        """
        fastqc {input.r1} {input.r2} --outdir {OUTPUT_DIR}/fastqc --threads {threads}
        """

# FastQC for Tumor Sample
rule fastqc_tumor:
    input:
        r1=INPUT_DIR + "/" + TUMOR_SAMPLE + "_R1_001.fastq.gz",
        r2=INPUT_DIR + "/" + TUMOR_SAMPLE + "_R2_001.fastq.gz"
    output:
        html_r1=OUTPUT_DIR + "/fastqc/" + TUMOR_SAMPLE + "_R1_001_fastqc.html",
        html_r2=OUTPUT_DIR + "/fastqc/" + TUMOR_SAMPLE + "_R2_001_fastqc.html"
    threads: THREADS
    shell:
        """
        fastqc {input.r1} {input.r2} --outdir {OUTPUT_DIR}/fastqc --threads {threads}
        """

# MultiQC rule
rule multiqc:
    input:
        waitfile = expand(OUTPUT_DIR + "/fastqc/{sample}_R1_001_fastqc.html", sample=[NORMAL_SAMPLE, TUMOR_SAMPLE]),
    params:
        inputdir = OUTPUT_DIR + "/fastqc/"
    output:
        OUTPUT_DIR + "/fastqc/multiqc_report.html"
    shell:
        """
        multiqc {params.inputdir} --outdir {OUTPUT_DIR}/fastqc
        """

# Alignment rule
rule align_normal:
    input:
        r1=INPUT_DIR + "/" + NORMAL_SAMPLE + "_R1_001.fastq.gz",
        r2=INPUT_DIR + "/" + NORMAL_SAMPLE + "_R2_001.fastq.gz"
    output:
        bam=OUTPUT_DIR + "/alignment/" + NORMAL_SAMPLE + ".sorted.bam",
        bai=OUTPUT_DIR + "/alignment/" + NORMAL_SAMPLE + ".sorted.bam.bai"
    threads: THREADS
    shell:
        """
        bwa mem -t {threads} {REFERENCE_GENOME} {input.r1} {input.r2} -R "@RG\\tID:{NORMAL_SAMPLE}\\tSM:{NORMAL_SAMPLE}\\tPL:Illumina\\tLB:Illumina" | \
        samtools view -bS - | \
        samtools sort -o {output.bam}
        samtools index {output.bam}
        """

# Alignment rule for Tumor
rule align_tumor:
    input:
        r1=INPUT_DIR + "/" + TUMOR_SAMPLE + "_R1_001.fastq.gz",
        r2=INPUT_DIR + "/" + TUMOR_SAMPLE + "_R2_001.fastq.gz"
    output:
        bam=OUTPUT_DIR + "/alignment/" + TUMOR_SAMPLE + ".sorted.bam",
        bai=OUTPUT_DIR + "/alignment/" + TUMOR_SAMPLE + ".sorted.bam.bai"
    threads: THREADS
    shell:
        """
        bwa mem -t {threads} {REFERENCE_GENOME} {input.r1} {input.r2} -R "@RG\\tID:{TUMOR_SAMPLE}\\tSM:{TUMOR_SAMPLE}\\tPL:Illumina\\tLB:Illumina" | \
        samtools view -bS - | \
        samtools sort -o {output.bam}
        samtools index {output.bam}
        """

# Somatic Mutation Calling (Mutect2) for Tumor vs Normal
rule somatic_mutation_calling:
    input:
        normal=OUTPUT_DIR + "/alignment/" + NORMAL_SAMPLE + ".sorted.bam",
        tumor=OUTPUT_DIR + "/alignment/" + TUMOR_SAMPLE + ".sorted.bam"
    output:
        vcf=OUTPUT_DIR + "/mutations/" + TUMOR_SAMPLE + "_somatic_mutations.vcf",
        filtered_vcf=OUTPUT_DIR + "/mutations/" + TUMOR_SAMPLE + "_somatic_mutations_filtered.vcf"
    threads: THREADS
    shell:
        """
        gatk Mutect2 \
            -R {REFERENCE_GENOME} \
            -I {input.tumor} \
            -I {input.normal} \
            --normal-sample {NORMAL_SAMPLE} \
            --tumor-sample {TUMOR_SAMPLE} \
            -O {output.vcf}

        gatk FilterMutectCalls \
            -R {REFERENCE_GENOME} \
            -V {output.vcf} \
            -O {output.filtered_vcf}
        """

# Background Mutation Calculation Rule
rule calculate_background_mutation_level:
    input:
        vcf=OUTPUT_DIR + "/mutations/" + TUMOR_SAMPLE + "_somatic_mutations_filtered.vcf"
    output:
        stats=OUTPUT_DIR + "/mutations/" + TUMOR_SAMPLE + "_background_mutation_stats.txt",
        outvcf= OUTPUT_DIR + "/mutations/" + TUMOR_SAMPLE + "_somatic_mutations.tsv"
    shell:
        """
        python3 scripts/calculate_background_mutation.py -i {input.vcf} -o {output.outvcf} -s {output.stats}
        """
