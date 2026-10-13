# A glucose–HbA1c distribution law for monitoring glycaemic control in diabetes

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23330009.svg)](https://doi.org/10.5281/zenodo.23330009) · Web tool: https://glucosehba1c.netlify.app

Analysis code for the manuscript *"A glucose–HbA1c distribution law for monitoring glycaemic control in diabetes: development at a Vietnamese district hospital and external validation in Vietnam and the United States"* (submitted).

The law links the **distributions** of fasting plasma glucose and HbA1c by matching their quantiles:

HbA1c(u) = e^α × glucose(u)^β

It is derived in 229 outpatients with type 2 diabetes at Le Van Thinh Hospital (Ho Chi Minh City) and validated in 279 outpatients at Sa Dec General Hospital (Dong Thap) and in 391 adults with diagnosed diabetes in NHANES August 2021–August 2023 (fasting subsample). Once anchored with a few local HbA1c values, the law predicts the HbA1c distribution of groups for which only glucose is available.

## Web tool
`index.html` (English) maps a population's glucose distribution to its expected HbA1c distribution by percentile.
- **Exponent β**: fitted to the user's own glucose and HbA1c values, or taken from a reference population (Le Van Thinh Hospital, Sa Dec General Hospital, NHANES 2021–2023).
- **Position**: anchored to the median of the user's HbA1c values (recommended), the user's own fit, or the reference position.
- **Uncertainty**: bootstrap 95% CIs for every output (reference bootstrap draws combined with resampling of the user's data) and sample-size ratings for the glucose sample, the own fit and the anchor.
- **Output**: percentile map (P5–P95) and share above an HbA1c threshold.
- **Look-up**: a single glucose value is placed in the user's glucose distribution (percentile) and mapped to the HbA1c value at the same percentile, with a 95% CI; labelled as a rank equivalent, not an individual prediction.

Example data can be loaded for each reference: NHANES 2021–2023 as the actual public values; the two hospitals as values reconstructed from their glucose and HbA1c percentiles (same distributions and law, not patient records, unpaired). A comparison table shows the results for the user's data under each β source. Hospital references are otherwise embedded only as aggregated summaries (49 percentiles and 500 bootstrap estimates of α and β); no hospital records are included. User data are processed in the browser only. Deployed on Netlify (`netlify.toml`). Research use only, not for diagnosis or treatment decisions.

## Repository structure
```
index.html web tool
code/      analysis, figure and manuscript-building scripts (run from this folder)
           *.json = summary results (no individual-level data)
data/      NHANES 2021–2023 fasting extract (public domain)
figures/   figures as PNG (Fig. 1–4, Fig. S1)
```

## Reproducing the analysis
Python ≥ 3.12 (`pip install -r requirements.txt`); Node.js ≥ 18 (`npm install`) only to rebuild the manuscript.

```bash
cd code
python analysis.py      # development (Le Van Thinh), internal and external (Sa Dec) validation   [needs hospital data]
python duration.py      # law vs regression across diabetes-duration groups (Table S4)           [needs hospital data]
python samplesize.py    # minimum sample sizes (Table 4)                                         [needs hospital data]
python nhanes.py        # external validation in NHANES 2021–2023 (Table 3)                      [needs hospital data for the development parameters]
python figs.py          # Fig. 1, Fig. 2, Fig. S1                                                [needs hospital data]
python fig3.py && python fig4.py   # Fig. 4 and Fig. 3 from the saved *.json results (no data needed)
node build_jdmd.js      # manuscript and Online Resource -> ../manuscript/
```
The summary results (`code/*.json`) are included, together with the rendered PNG figures, so Fig. 3–4 and the manuscript can be rebuilt without the hospital data. All simulations use fixed random seeds.

## Data availability
- **NHANES** (`data/`): public domain, National Center for Health Statistics. Only the August 2021–August 2023 cycle is used.
- **Hospital data**: de-identified data from Le Van Thinh Hospital and Sa Dec General Hospital are **not public** (patient privacy and hospital regulations). They are available from the corresponding author on reasonable request, subject to the approval of both hospitals. Scripts expect them in `data_private/` (`thinh_deid.xlsx`, `sadec_deid.xlsx`), which is excluded by `.gitignore`.

## Notes
- Le Van Thinh dates: in the first extraction (Sep–Nov 2025) Excel stored day and month swapped; `analysis.py` corrects this (checked against the sample IDs). Study period: 2025-09 to 2026-03.
- Ethics: approved by the Ethics Committee in Biomedical Research of Van Lang University (No. 07/2026/HĐĐĐ-IRB-VN01.078, 4 February 2026); informed consent waived (retrospective, de-identified data).
- Parts of the analysis code were developed with the assistance of a large language model (Claude, Anthropic); all code was reviewed and run by the authors.

## Citation
Lam TK. Glucose–HbA1c distribution law: analysis code and web tool. Version 1.0.0. Zenodo; 2026. https://doi.org/10.5281/zenodo.23330009 (all versions: https://doi.org/10.5281/zenodo.23330006). See also `CITATION.cff`. Corresponding author: Thanh Kien Lam, Faculty of Medical Technology, Van Lang University (thanh.lk@vlu.edu.vn).

## Licence
Code: MIT. NHANES data: public domain. Figures: © the authors.
