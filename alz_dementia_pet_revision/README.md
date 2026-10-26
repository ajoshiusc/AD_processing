# PET-based Alzheimer's & Dementia manuscript package

This directory contains the manuscript package.

- `motor_AD_PET_revision.tex`: main manuscript.
- `figs/`: all figures referenced by the manuscript.
- `tables/`: PET-linked cohort tables, CDR 0 surface-sensitivity status, and connectivity outputs.
- `analysis/build_pet_revision_outputs.py`: reproducible script used to build the PET cohort, figures, PET-defined motor-connectivity analysis, and age/sex-adjusted connectivity table.
- `ref.bib`: bibliography.
- `Highlights.tex`, `ResearchInContext.tex`, `CoverLetter.tex`: submission support files.

Run the analysis from the repository root:

```bash
.venv/bin/python alz_dementia_pet_revision/analysis/build_pet_revision_outputs.py
```

Compile the manuscript from this directory:

```bash
latexmk -pdf motor_AD_PET_revision.tex
```

Note: the PET/SUVR cortical-thickness figure uses the derived surface maps already present in `src/outputs`. The raw vertexwise thickness `.mat` files required for a new surface workflow are not available in this package, so the script records that a CDR 0-only or age/sex-adjusted surface rerun could not be regenerated.
