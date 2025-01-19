import argparse
import pandas as pd
import io
import numpy as np


def parse_vcf(input_file):
    """Parse a VCF file, skipping header lines, and return a Pandas DataFrame."""
    with open(input_file, 'r') as vcf:
        content = [line for line in vcf if not line.startswith("#")]
    data = "".join(content)

    # Parse the data into a DataFrame
    df = pd.read_csv(io.StringIO(data), sep="\t", header=None)
    df.columns = ["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT", "TUMOR", "NORMAL"]
    return df


def count_somatic_mutations(df):
    """
    Count somatic mutations present in the Tumor sample but absent in the Normal tissue.
    Returns the filtered DataFrame and the count of somatic mutations.
    """
    # Extract genotype information from the TUMOR and NORMAL columns
    # Format assumed as "GT:AD:AF:..." (Genotype: Allele Depth: Allele Frequency: ...)
    df["TUMOR_GT"] = df["TUMOR"].str.split(":").str[0]
    df["NORMAL_GT"] = df["NORMAL"].str.split(":").str[0]

    # Filter for somatic mutations: Tumor is heterozygous (0/1 or 1/1), Normal is homozygous reference (0/0)
    somatic_mutations = df[
        (df["FILTER"] == "PASS") &  # Filter on 'PASS'
        (df["TUMOR_GT"].isin(["0/1", "1/1"])) &  # Tumor is heterozygous or homozygous variant
        (df["NORMAL_GT"] == "0/0")  # Normal is homozygous reference
    ]

    return somatic_mutations, len(somatic_mutations)


def calculate_background_mutation_level(df):
    """
    Calculate the median background mutation level in the normal tissue.
    This assumes mutations in normal tissue are likely sequencing errors.
    """
    # Extract the Allele Frequency (AF) from the NORMAL column
    # The AF values are assumed to be comma-separated; we take the first value
    df["NORMAL_AF"] = df["NORMAL"].str.split(":").str[2].str.split(",").str[0].astype(float)

    # Consider mutations with low AF in the normal tissue (e.g., <0.1 or other threshold)
    normal_background = df[(df["NORMAL_AF"] < 0.1) & (df["FILTER"] == "PASS")]

    # Calculate the median background mutation level
    background_median = np.median(normal_background["NORMAL_AF"])
    return background_median, normal_background


def calculate_reads_per_million(background_median, threshold=10):
    """
    Calculate the number of reads per million (RPM) required to confidently call a mutation.
    The threshold is used to define a "confidence" factor above the background mutation level.
    """
    # Assuming we want mutations to have at least 10 times the background level to be confident
    rpm_threshold = threshold * background_median
    return rpm_threshold


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process VCF file to extract somatic mutations and calculate background mutation level.")
    parser.add_argument("-i", "--input", required=True, help="Input VCF file.")
    parser.add_argument("-o", "--output", required=True, help="Output file to save results (somatic mutations).")
    parser.add_argument("-s", "--stats", required=True, help="Output file to save stats (background mutation level and RPM).")

    args = parser.parse_args()

    # Parse the VCF file
    df = parse_vcf(args.input)

    # Count somatic mutations
    somatic_mutations, count = count_somatic_mutations(df)

    # Save the somatic mutations results to the output file
    somatic_mutations.to_csv(args.output, sep="\t", index=False)
    print(f"Found {count} somatic mutations present in the Tumor sample but absent in the Normal tissue.")
    print(f"Somatic mutations saved to {args.output}.")

    # Calculate the background mutation level
    background_median, normal_background = calculate_background_mutation_level(df)

    # Calculate RPM threshold
    rpm_threshold = calculate_reads_per_million(background_median)

    # Save the normal background mutations and stats to the stats file
    with open(args.stats, 'w') as stats_file:
        stats_file.write(f"Total somatic mutations: {count}\n")
        stats_file.write(f"Median background mutation level (AF in normal tissue): {background_median}\n")
        stats_file.write(f"Reads per million threshold for confident mutation calling: {rpm_threshold}\n")
        stats_file.write(f"Somatic mutations details saved to: {args.output}\n")
    print(f"Stats saved to {args.stats}.")


if __name__ == "__main__":
    main()
