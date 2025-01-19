#!/bin/bash
snakemake -s workflow.smk --cores all --unlock
snakemake -s workflow.smk --cores all --rerun-incomplete
