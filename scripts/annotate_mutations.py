import argparse
import pandas as pd

def load_reference_data(reference_file):
    """Load reference data from a CSV file."""
    try:
        reference_data = pd.read_csv(reference_file)
        return reference_data
    except Exception as e:
        print(f"Error loading reference file: {e}")
        exit(1)

def load_mutation_data(mutation_file):
    """Load mutation data from a TSV file."""
    try:
        mutation_data = pd.read_csv(mutation_file, sep='\t')
        return mutation_data
    except Exception as e:
        print(f"Error loading mutation file: {e}")
        exit(1)

def annotate_mutations(reference_data, mutation_data):
    """Annotate mutations with reference data."""
    annotated_data = []

    for _, mutation in mutation_data.iterrows():
        chrom = mutation['CHROM']
        position = mutation['POS']
        mutation_type = f"{mutation['REF']}->{mutation['ALT']}"  # Combine REF and ALT for mutation type

        # Filter reference data to match chromosome and position range
        matched_rows = reference_data[
            (reference_data['Chr'] == chrom) & 
            (reference_data['Absolute Start'] <= position) & 
            (reference_data['Absolute End'] >= position)
        ]

        if not matched_rows.empty:
            for _, row in matched_rows.iterrows():
                annotated_data.append({
                    'Chr': chrom,
                    'Position': position,
                    'Mutation': mutation_type,
                    'Gene': row['Gene'],
                    'Region': row['ID'],
                    'Reference Sequence': row['Sequence']
                })
        else:
            annotated_data.append({
                'Chr': chrom,
                'Position': position,
                'Mutation': mutation_type,
                'Gene': 'Not Found',
                'Region': 'Not Found',
                'Reference Sequence': 'Not Found'
            })

    return pd.DataFrame(annotated_data)


def main():
    parser = argparse.ArgumentParser(description="Annotate mutations using reference data.")
    parser.add_argument("--reference_file", required=True, help="Path to the reference data file (CSV format).")
    parser.add_argument("--mutation_file", required=True, help="Path to the mutation data file (TSV format).")
    parser.add_argument("--output_file", required=True, help="Path to the output annotated file.")
    
    args = parser.parse_args()

    # Load data
    reference_data = load_reference_data(args.reference_file)
    mutation_data = load_mutation_data(args.mutation_file)

    # Annotate mutations
    annotated_mutations = annotate_mutations(reference_data, mutation_data)

    # Save the output
    try:
        annotated_mutations.to_csv(args.output_file, sep='\t', index=False)
        print(f"Annotated mutations saved to {args.output_file}")
    except Exception as e:
        print(f"Error saving annotated file: {e}")
        exit(1)

if __name__ == "__main__":
    main()
