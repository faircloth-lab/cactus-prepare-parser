# Purpose

If you are running [cactus](https://github.com/ComparativeGenomicsToolkit/cactus) serially for a multi-way alignment, preparing SLURM submission scripts from the `cactus-prepare` output can be tedious. This script automates that process.

# Requirements

* Python 3

# Usage
```bash
python cactus_prepare_parser.py \
    --cactus-prepare slurm-cactus-prepare-44028.out-qbc019 \ --output-dir my-slurm-scripts
```