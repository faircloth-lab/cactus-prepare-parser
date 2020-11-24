# Purpose

If you are running [cactus](https://github.com/ComparativeGenomicsToolkit/cactus) serially for a multi-way alignment, preparing SLURM submission scripts from the `cactus-prepare` output can be tedious. This script automates that process.

# Requirements

* Python 3

# Usage

Modify the information in `align_header.txt` to your liking.  Then run:

```bash
python cactus_prepare_parser.py \
    --cactus-prepare slurm-cactus-prepare.stdout \
    --output-dir my-slurm-scripts
```

Then submit the resulting scripts.  They are split into difference directories by task (`pre-process`, `align`, `HAL merging`).