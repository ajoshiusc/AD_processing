#!/usr/bin/env python3
"""Build PET-based cohort tables, figures, and motor-connectivity analysis.

This script intentionally keeps the PET status definition explicit: amyloid
positivity is based on OASIS-3/PUP tracer-specific RSF mean cortical SUVR
cutoffs from the OASIS-3 data dictionary.
"""

from __future__ import annotations

import re
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.io as sio
from PIL import Image, ImageDraw, ImageFont
from scipy import stats
from statsmodels.stats.multitest import multipletests
from tqdm import tqdm


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1]
FIG_DIR = OUT / "figs"
TABLE_DIR = OUT / "tables"

PET_CUTOFFS = {"PIB": 1.42, "AV45": 1.19}
LEN_TIME = 164
ROIS = [147, 225, 373, 247, 186, 187, 188, 189, 227, 145]
ROI_SHORT_NAMES = [
    "PreCG sup",
    "PostCG sup",
    "Parahip",
    "Sup parietal",
    "R ant cing",
    "L ant cing",
    "R mid cing",
    "L mid cing",
    "PostCG inf",
    "PreCG inf",
]


def session_day_from_text(text: str) -> float:
    match = re.search(r"(?:_|-)d(\d+)", str(text))
    return float(match.group(1)) if match else np.nan


def load_pup() -> pd.DataFrame:
    pup = pd.read_csv(ROOT / "csv_files" / "OASIS3_PUP.csv")
    pup = pup.dropna(subset=["PET_fSUVR_rsf_TOT_CORTMEAN"]).copy()
    pup["Subject"] = pup["MRId"].str.slice(0, 8)
    pup["mr_day"] = pup["MRId"].map(session_day_from_text)
    pup["pet_day"] = pup["id"].map(session_day_from_text)
    pup["amyloid_cutoff"] = pup["tracer"].map(PET_CUTOFFS)
    pup["amyloid_positive"] = pup["PET_fSUVR_rsf_TOT_CORTMEAN"] > pup["amyloid_cutoff"]
    return pup


def closest_pet_for_rows(rows: pd.DataFrame, pup: pd.DataFrame, day_col: str) -> pd.DataFrame:
    merged = rows.merge(
        pup[
            [
                "Subject",
                "tracer",
                "mr_day",
                "pet_day",
                "PET_fSUVR_rsf_TOT_CORTMEAN",
                "amyloid_cutoff",
                "amyloid_positive",
                "id",
            ]
        ],
        on="Subject",
        how="left",
    )
    merged["pet_mri_abs_days"] = (merged["pet_day"] - merged[day_col]).abs()
    merged = merged.sort_values(["Subject", day_col, "pet_mri_abs_days"])
    return merged.drop_duplicates(subset=rows.columns.tolist(), keep="first")


def add_clinical_demographics(rows: pd.DataFrame, day_col: str) -> pd.DataFrame:
    clinical = pd.read_csv(ROOT / "csv_files" / "ADRC_Clinical_Data_aajoshi_5_14_2021_1_47_36.csv")
    clinical["clinical_day"] = clinical["Label"].astype(str).str.extract(r"_d(\d+)").astype(float)
    clinical = clinical.dropna(subset=["clinical_day"]).copy()

    annotated = []
    for _, row in rows.iterrows():
        visits = clinical[clinical["Subject"] == row["Subject"]].copy()
        if visits.empty:
            annotated.append((np.nan, "", np.nan, np.nan))
            continue
        visits["clinical_mri_abs_days"] = (visits["clinical_day"] - row[day_col]).abs()
        visit = visits.sort_values("clinical_mri_abs_days").iloc[0]
        annotated.append(
            (
                float(visit["ageAtEntry"]) if pd.notna(visit["ageAtEntry"]) else np.nan,
                str(visit["Gender"]),
                float(visit["clinical_day"]),
                float(visit["clinical_mri_abs_days"]),
            )
        )

    rows = rows.copy()
    rows[["age_at_clinical", "sex", "clinical_day_matched", "clinical_mri_abs_days"]] = annotated
    rows["age_at_clinical"] = pd.to_numeric(rows["age_at_clinical"], errors="coerce")
    rows["clinical_day_matched"] = pd.to_numeric(rows["clinical_day_matched"], errors="coerce")
    rows["clinical_mri_abs_days"] = pd.to_numeric(rows["clinical_mri_abs_days"], errors="coerce")
    return rows


def build_pet_linked_cohort(pup: pd.DataFrame) -> pd.DataFrame:
    cohort = pd.read_csv(
        ROOT / "csv_files" / "OASIS_all_subjects_with_mmse_cdr_avgs_suvr_closest_clinical_day_mmse_cdr.csv"
    )
    cohort = cohort.dropna(subset=["closest_day_suvr_value", "closest_day_mmse_value"]).copy()
    cohort = cohort[cohort["closest_day_mmse_value"] > 24].copy()

    matched = cohort.merge(
        pup[
            [
                "Subject",
                "tracer",
                "mr_day",
                "pet_day",
                "PET_fSUVR_rsf_TOT_CORTMEAN",
                "amyloid_cutoff",
                "id",
            ]
        ],
        on="Subject",
        how="left",
    )
    matched["pup_mr_suvr_abs_days"] = (
        matched["mr_day"] - matched["closest_suvr_day"]
    ).abs()
    matched["suvr_abs_diff"] = (
        matched["PET_fSUVR_rsf_TOT_CORTMEAN"] - matched["closest_day_suvr_value"]
    ).abs()
    matched["pet_mri_abs_days"] = (matched["pet_day"] - matched["mri_day"]).abs()
    matched = matched.sort_values(
        ["Subject", "mri_day", "pup_mr_suvr_abs_days", "suvr_abs_diff"]
    )
    matched = matched.drop_duplicates(subset=cohort.columns.tolist(), keep="first")
    matched["amyloid_positive"] = matched["closest_day_suvr_value"] > matched["amyloid_cutoff"]
    matched = matched.rename(
        columns={
            "PET_fSUVR_rsf_TOT_CORTMEAN": "matched_pup_suvr_rsf",
            "id": "matched_pet_pup_id",
        }
    )
    good_subids = set((ROOT / "src" / "good_subids.txt").read_text().splitlines())
    matched["in_good_subids"] = matched["Subject"].isin(good_subids)
    matched = add_clinical_demographics(matched, "mri_day")
    matched.to_csv(TABLE_DIR / "pet_linked_cohort.csv", index=False)
    return matched


def write_summary_tables(cohort: pd.DataFrame) -> None:
    group = cohort.groupby("amyloid_positive", dropna=False)
    summary = group.agg(
        n=("Subject", "size"),
        age_mean=("age_at_clinical", "mean"),
        age_sd=("age_at_clinical", "std"),
        female_n=("sex", lambda s: int((s == "female").sum())),
        male_n=("sex", lambda s: int((s == "male").sum())),
        pib_n=("tracer", lambda s: int((s == "PIB").sum())),
        av45_n=("tracer", lambda s: int((s == "AV45").sum())),
        cdr0_n=("closest_day_cdr_value", lambda s: int((s == 0).sum())),
        cdr05_n=("closest_day_cdr_value", lambda s: int((s == 0.5).sum())),
        cdr1_n=("closest_day_cdr_value", lambda s: int((s == 1).sum())),
        mmse_mean=("closest_day_mmse_value", "mean"),
        mmse_sd=("closest_day_mmse_value", "std"),
        cdr_mean=("closest_day_cdr_value", "mean"),
        cdr_sd=("closest_day_cdr_value", "std"),
        suvr_mean=("closest_day_suvr_value", "mean"),
        suvr_sd=("closest_day_suvr_value", "std"),
        pet_mri_median_days=("pet_mri_abs_days", "median"),
        pet_mri_mean_days=("pet_mri_abs_days", "mean"),
        pet_mri_max_days=("pet_mri_abs_days", "max"),
    )
    summary.index = summary.index.map({False: "A-", True: "A+"})
    summary.to_csv(TABLE_DIR / "pet_group_summary.csv")

    tests = {
        "age_ttest_p": stats.ttest_ind(
            cohort.loc[~cohort["amyloid_positive"], "age_at_clinical"],
            cohort.loc[cohort["amyloid_positive"], "age_at_clinical"],
            equal_var=False,
            nan_policy="omit",
        ).pvalue,
        "sex_chi2_p": stats.chi2_contingency(
            pd.crosstab(cohort["amyloid_positive"], cohort["sex"])
        ).pvalue,
        "mmse_ttest_p": stats.ttest_ind(
            cohort.loc[~cohort["amyloid_positive"], "closest_day_mmse_value"],
            cohort.loc[cohort["amyloid_positive"], "closest_day_mmse_value"],
            equal_var=False,
            nan_policy="omit",
        ).pvalue,
        "cdr_mannwhitney_p": stats.mannwhitneyu(
            cohort.loc[~cohort["amyloid_positive"], "closest_day_cdr_value"],
            cohort.loc[cohort["amyloid_positive"], "closest_day_cdr_value"],
            alternative="two-sided",
        ).pvalue,
        "suvr_spearman_mmse_rho": stats.spearmanr(
            cohort["closest_day_suvr_value"], cohort["closest_day_mmse_value"], nan_policy="omit"
        ).statistic,
        "suvr_spearman_mmse_p": stats.spearmanr(
            cohort["closest_day_suvr_value"], cohort["closest_day_mmse_value"], nan_policy="omit"
        ).pvalue,
        "good_subids_n": int(cohort["in_good_subids"].sum()),
        "good_subids_a_pos": int(
            (cohort["in_good_subids"] & cohort["amyloid_positive"]).sum()
        ),
        "good_subids_a_neg": int(
            (cohort["in_good_subids"] & ~cohort["amyloid_positive"]).sum()
        ),
    }
    pd.DataFrame([tests]).to_csv(TABLE_DIR / "pet_group_tests.csv", index=False)


def plot_pet_cohort(cohort: pd.DataFrame) -> None:
    plt.rcParams.update({"font.size": 9, "font.family": "DejaVu Sans"})
    fig = plt.figure(figsize=(7.2, 5.2), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1.0])
    ax0 = fig.add_subplot(gs[0, :])
    ax1 = fig.add_subplot(gs[1, 0])
    ax2 = fig.add_subplot(gs[1, 1])

    colors = {"PIB": "#3A6EA5", "AV45": "#C54B3C"}
    for tracer, grp in cohort.groupby("tracer"):
        ax0.hist(
            grp["closest_day_suvr_value"],
            bins=np.linspace(0.45, 4.3, 34),
            alpha=0.52,
            color=colors.get(tracer, "0.5"),
            label=f"{tracer} (n={len(grp)})",
        )
    ax0.axvline(PET_CUTOFFS["AV45"], color=colors["AV45"], lw=1.4, ls="--")
    ax0.axvline(PET_CUTOFFS["PIB"], color=colors["PIB"], lw=1.4, ls="--")
    ax0.text(PET_CUTOFFS["AV45"] + 0.03, ax0.get_ylim()[1] * 0.92, "AV45 A+ cutoff")
    ax0.text(PET_CUTOFFS["PIB"] + 0.03, ax0.get_ylim()[1] * 0.78, "PiB A+ cutoff")
    ax0.set_xlabel("RSF mean cortical SUVR")
    ax0.set_ylabel("Subjects")
    ax0.legend(frameon=False, ncol=2)
    ax0.spines[["top", "right"]].set_visible(False)

    labels = ["A-", "A+"]
    values = [
        cohort.loc[~cohort["amyloid_positive"], "closest_day_mmse_value"],
        cohort.loc[cohort["amyloid_positive"], "closest_day_mmse_value"],
    ]
    bp = ax1.boxplot(values, tick_labels=labels, patch_artist=True, widths=0.55)
    for patch, color in zip(bp["boxes"], ["#7A9E7E", "#B55D60"]):
        patch.set_facecolor(color)
        patch.set_alpha(0.65)
    rng = np.random.default_rng(42)
    for i, vals in enumerate(values, start=1):
        x = rng.normal(i, 0.035, size=len(vals))
        ax1.plot(x, vals, ".", ms=2.5, color="0.2", alpha=0.35)
    ax1.set_ylabel("MMSE closest to MRI")
    ax1.set_title("Preserved global cognition (MMSE > 24)")
    ax1.spines[["top", "right"]].set_visible(False)

    cdr_values = [
        cohort.loc[~cohort["amyloid_positive"], "closest_day_cdr_value"],
        cohort.loc[cohort["amyloid_positive"], "closest_day_cdr_value"],
    ]
    bp = ax2.boxplot(cdr_values, tick_labels=labels, patch_artist=True, widths=0.55)
    for patch, color in zip(bp["boxes"], ["#7A9E7E", "#B55D60"]):
        patch.set_facecolor(color)
        patch.set_alpha(0.65)
    for i, vals in enumerate(cdr_values, start=1):
        x = rng.normal(i, 0.035, size=len(vals))
        ax2.plot(x, vals, ".", ms=2.5, color="0.2", alpha=0.35)
    ax2.set_ylabel("CDR closest to MRI")
    ax2.set_title("Clinical dementia rating")
    ax2.spines[["top", "right"]].set_visible(False)

    fig.savefig(FIG_DIR / "pet_cohort_summary.pdf")
    fig.savefig(FIG_DIR / "pet_cohort_summary.png", dpi=300)
    plt.close(fig)


def combine_pet_thickness_maps() -> None:
    files = [
        ("Left lateral", ROOT / "src/outputs/LeftLateral_thickness_pvc_smooth0fdrpval_sig.png"),
        ("Left medial", ROOT / "src/outputs/LeftMedial_thickness_pvc_smooth0fdrpval_sig.png"),
        ("Right lateral", ROOT / "src/outputs/RightLateral_thickness_pvc_smooth0fdrpval_sig.png"),
        ("Right medial", ROOT / "src/outputs/RightMedial_thickness_pvc_smooth0fdrpval_sig.png"),
    ]
    images = [(label, Image.open(path).convert("RGB")) for label, path in files]
    width, height = images[0][1].size
    label_h = 90
    canvas = Image.new("RGB", (2 * width, 2 * (height + label_h)), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 42)
    except OSError:
        font = ImageFont.load_default()
    for idx, (label, image) in enumerate(images):
        row = idx // 2
        col = idx % 2
        x = col * width
        y = row * (height + label_h)
        draw.text((x + 35, y + 24), label, fill=(20, 20, 20), font=font)
        canvas.paste(image, (x, y + label_h))
    canvas.save(FIG_DIR / "pet_thickness_suvr_fdr.png")

    fig, ax = plt.subplots(figsize=(7.5, 7.5))
    ax.imshow(canvas)
    ax.axis("off")
    fig.savefig(FIG_DIR / "pet_thickness_suvr_fdr.pdf", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def run_cdr0_thickness_sensitivity(cohort: pd.DataFrame) -> None:
    """Run a stricter CDR=0 PET/SUVR cortical-thickness sensitivity analysis."""

    sys.path.insert(0, str(ROOT / "src"))
    from grayord_utils import vis_grayord_sigpval

    bfp_path = "/home/ajoshi/Projects/bfp"
    fsl_path = "/usr/share/fsl/5.0"
    surface_out = FIG_DIR / "cdr0_thickness_surface"
    surface_out.mkdir(parents=True, exist_ok=True)

    cdr0 = cohort[
        (cohort["closest_day_cdr_value"] == 0)
        & (cohort["closest_day_mmse_value"] > 24)
        & (cohort["in_good_subids"])
    ].copy()
    cdr0_total = len(cdr0)
    cdr0_a_neg = int((~cdr0["amyloid_positive"]).sum())
    cdr0_a_pos = int(cdr0["amyloid_positive"].sum())
    cdr0 = cdr0[cdr0["FileName"].map(lambda p: Path(p).is_file())].copy()
    if len(cdr0) < 2:
        pd.DataFrame(
            [
                {
                    "n": cdr0_total,
                    "a_neg": cdr0_a_neg,
                    "a_pos": cdr0_a_pos,
                    "thickness_files_available": len(cdr0),
                    "min_p": np.nan,
                    "min_q_fdr": np.nan,
                    "fdr_sig_vertices": np.nan,
                    "uncorrected_p_lt_0_05_vertices": np.nan,
                    "note": "Raw thickness .mat files were not mounted; sensitivity map was not regenerated.",
                }
            ]
        ).to_csv(TABLE_DIR / "cdr0_pet_thickness_suvr_summary.csv", index=False)
        return
    reg_var = cdr0["closest_day_suvr_value"].to_numpy(dtype=np.float64)

    thickness = np.zeros((96854, len(cdr0)), dtype=np.float64)
    for i, fname in enumerate(tqdm(cdr0["FileName"], desc="CDR=0 thickness")):
        thickness[:, i] = sio.loadmat(fname)["data"].squeeze()
    bad = ~np.isfinite(np.sum(thickness, axis=1))
    thickness[bad, :] = 0

    corr_val = np.zeros(thickness.shape[0], dtype=np.float64)
    corr_pval = np.ones(thickness.shape[0], dtype=np.float64)
    for vertex in tqdm(range(thickness.shape[0]), desc="CDR=0 SUVR/thickness"):
        corr_val[vertex], corr_pval[vertex] = stats.pearsonr(thickness[vertex, :], reg_var)

    finite = np.isfinite(corr_pval)
    corr_pval_fdr = np.ones_like(corr_pval)
    corr_pval_fdr[finite] = multipletests(corr_pval[finite], method="fdr_bh")[1]

    np.savez(
        TABLE_DIR / "cdr0_pet_thickness_suvr_stats.npz",
        corr_val=corr_val,
        corr_pval=corr_pval,
        corr_pval_fdr=corr_pval_fdr,
        subject=cdr0["Subject"].to_numpy(),
        amyloid_positive=cdr0["amyloid_positive"].to_numpy(dtype=bool),
        suvr=reg_var,
    )

    pd.DataFrame(
        [
            {
                "n": len(cdr0),
                "a_neg": int((~cdr0["amyloid_positive"]).sum()),
                "a_pos": int(cdr0["amyloid_positive"].sum()),
                "thickness_files_available": len(cdr0),
                "min_p": float(np.nanmin(corr_pval)),
                "min_q_fdr": float(np.nanmin(corr_pval_fdr)),
                "fdr_sig_vertices": int((corr_pval_fdr < 0.05).sum()),
                "uncorrected_p_lt_0_05_vertices": int((corr_pval < 0.05).sum()),
                "note": "",
            }
        ]
    ).to_csv(TABLE_DIR / "cdr0_pet_thickness_suvr_summary.csv", index=False)

    for pval, name in [
        (corr_pval, "cdr0_thickness_pvc_suvr_smooth0"),
        (corr_pval_fdr, "cdr0_thickness_pvc_suvr_smooth0fdr"),
    ]:
        vis_grayord_sigpval(
            pval=pval,
            sig_alpha=0.05,
            surf_name=name,
            out_dir=str(surface_out),
            smooth_iter=0,
            bfp_path=bfp_path,
            fsl_path=fsl_path,
        )

    files = [
        ("Left lateral", surface_out / "LeftLateral_cdr0_thickness_pvc_suvr_smooth0fdrpval_sig.png"),
        ("Left medial", surface_out / "LeftMedial_cdr0_thickness_pvc_suvr_smooth0fdrpval_sig.png"),
        ("Right lateral", surface_out / "RightLateral_cdr0_thickness_pvc_suvr_smooth0fdrpval_sig.png"),
        ("Right medial", surface_out / "RightMedial_cdr0_thickness_pvc_suvr_smooth0fdrpval_sig.png"),
    ]
    images = [(label, Image.open(path).convert("RGB")) for label, path in files]
    width, height = images[0][1].size
    label_h = 90
    canvas = Image.new("RGB", (2 * width, 2 * (height + label_h)), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 42)
    except OSError:
        font = ImageFont.load_default()
    for idx, (label, image) in enumerate(images):
        row = idx // 2
        col = idx % 2
        x = col * width
        y = row * (height + label_h)
        draw.text((x + 35, y + 24), label, fill=(20, 20, 20), font=font)
        canvas.paste(image, (x, y + label_h))
    canvas.save(FIG_DIR / "cdr0_pet_thickness_suvr_fdr.png")

    fig, ax = plt.subplots(figsize=(7.5, 7.5))
    ax.imshow(canvas)
    ax.axis("off")
    fig.savefig(FIG_DIR / "cdr0_pet_thickness_suvr_fdr.pdf", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def normalize_ts(x: np.ndarray) -> np.ndarray:
    x = x - x.mean(axis=0, keepdims=True)
    denom = np.linalg.norm(x, axis=0, keepdims=True)
    denom[denom == 0] = 1
    return x / denom


def build_fmri_pet_rows(pup: pd.DataFrame) -> pd.DataFrame:
    fmri = pd.read_csv(ROOT / "csv_files" / "oasis3_bfp_mmse.csv")
    fmri = fmri[fmri["mmse"] > 24].copy()
    fmri["mri_day"] = fmri["FileName"].map(session_day_from_text)
    fmri = fmri[fmri["FileName"].map(lambda p: Path(p).is_file())].copy()
    matched = closest_pet_for_rows(fmri, pup, "mri_day")
    matched = matched.dropna(subset=["amyloid_positive"]).copy()
    matched.to_csv(TABLE_DIR / "pet_fmri_motor_connectivity_subjects.csv", index=False)
    return matched


def run_motor_connectivity(fmri_rows: pd.DataFrame) -> None:
    atlas = sio.loadmat(ROOT.parent / "bfp" / "supp_data" / "USCBrain_grayordinate_labels.mat")
    labels = np.mod(np.squeeze(atlas["labels"]), 1000)
    roi_indices = [np.where(labels == roi)[0] for roi in ROIS]

    conn = np.zeros((len(fmri_rows), len(ROIS), len(ROIS)), dtype=np.float64)
    kept = []
    for row_index, row in tqdm(
        list(fmri_rows.reset_index(drop=True).iterrows()), desc="PET motor connectivity"
    ):
        try:
            data = sio.loadmat(row["FileName"])["dtseries"][:, :LEN_TIME].T
        except Exception as exc:  # pragma: no cover - recorded in output table
            print(f"Skipping {row['Subject']} because {exc}")
            continue
        roi_ts = np.column_stack([data[:, idx].mean(axis=1) for idx in roi_indices])
        if not np.isfinite(roi_ts).all():
            print(f"Skipping {row['Subject']} because ROI time series contain non-finite values")
            continue
        roi_ts = normalize_ts(roi_ts)
        if not np.isfinite(roi_ts).all():
            print(f"Skipping {row['Subject']} because normalized ROI time series are non-finite")
            continue
        conn[len(kept)] = roi_ts.T @ roi_ts
        kept.append(row_index)

    conn = conn[: len(kept)]
    fmri_rows = fmri_rows.reset_index(drop=True).iloc[kept].copy()
    fmri_rows.to_csv(TABLE_DIR / "pet_fmri_motor_connectivity_subjects_used.csv", index=False)

    a_pos = fmri_rows["amyloid_positive"].to_numpy(dtype=bool)
    conn_neg = conn[~a_pos]
    conn_pos = conn[a_pos]
    mean_neg = conn_neg.mean(axis=0)
    mean_pos = conn_pos.mean(axis=0)
    diff = mean_pos - mean_neg

    pvals = np.ones((len(ROIS), len(ROIS)))
    effects = np.zeros_like(pvals)
    for i in range(len(ROIS)):
        for j in range(len(ROIS)):
            x = conn_pos[:, i, j]
            y = conn_neg[:, i, j]
            pvals[i, j] = stats.mannwhitneyu(x, y, alternative="two-sided").pvalue
            pooled = np.sqrt(((x.size - 1) * x.var(ddof=1) + (y.size - 1) * y.var(ddof=1)) / (x.size + y.size - 2))
            effects[i, j] = 0 if pooled == 0 else (x.mean() - y.mean()) / pooled

    upper = np.triu_indices(len(ROIS), k=1)
    qvals = np.ones_like(pvals)
    qvals[upper] = multipletests(pvals[upper], method="fdr_bh")[1]
    qvals[(upper[1], upper[0])] = qvals[upper]
    np.fill_diagonal(qvals, 1)

    np.savez(
        TABLE_DIR / "pet_motor_connectivity.npz",
        conn=conn,
        amyloid_positive=a_pos,
        mean_neg=mean_neg,
        mean_pos=mean_pos,
        diff=diff,
        pvals=pvals,
        qvals=qvals,
        effects=effects,
        rois=np.array(ROIS),
        roi_names=np.array(ROI_SHORT_NAMES),
    )

    long_rows = []
    for i in range(len(ROIS)):
        for j in range(i + 1, len(ROIS)):
            long_rows.append(
                {
                    "roi_i": ROI_SHORT_NAMES[i],
                    "roi_j": ROI_SHORT_NAMES[j],
                    "mean_a_neg": mean_neg[i, j],
                    "mean_a_pos": mean_pos[i, j],
                    "difference_a_pos_minus_a_neg": diff[i, j],
                    "cohens_d": effects[i, j],
                    "p": pvals[i, j],
                    "q_fdr": qvals[i, j],
                }
            )
    pd.DataFrame(long_rows).sort_values("p").to_csv(
        TABLE_DIR / "pet_motor_connectivity_edges.csv", index=False
    )

    covariates = fmri_rows[["amyloid_positive", "Age", "Gender"]].copy()
    covariates["amyloid_positive"] = covariates["amyloid_positive"].astype(float)
    covariates["male"] = covariates["Gender"].astype(str).str.upper().str.startswith("M").astype(float)
    covariates["Age"] = pd.to_numeric(covariates["Age"], errors="coerce")
    covar_matrix = np.column_stack(
        [
            np.ones(len(covariates)),
            covariates["amyloid_positive"].to_numpy(dtype=float),
            covariates["Age"].to_numpy(dtype=float),
            covariates["male"].to_numpy(dtype=float),
        ]
    )
    covar_ok = np.isfinite(covar_matrix).all(axis=1)
    adjusted_rows = []
    for i in range(len(ROIS)):
        for j in range(i + 1, len(ROIS)):
            y = conn[:, i, j]
            ok = covar_ok & np.isfinite(y)
            x_ok = covar_matrix[ok]
            y_ok = y[ok]
            if len(y_ok) <= x_ok.shape[1]:
                beta = se = t_stat = p_amyloid = np.nan
            else:
                beta_hat, *_ = np.linalg.lstsq(x_ok, y_ok, rcond=None)
                resid = y_ok - x_ok @ beta_hat
                dof = len(y_ok) - x_ok.shape[1]
                sigma2 = float((resid @ resid) / dof)
                cov_beta = sigma2 * np.linalg.pinv(x_ok.T @ x_ok)
                se_beta = np.sqrt(np.diag(cov_beta))
                beta = float(beta_hat[1])
                se = float(se_beta[1])
                t_stat = beta / se if se > 0 else np.nan
                p_amyloid = float(2 * stats.t.sf(abs(t_stat), dof)) if np.isfinite(t_stat) else np.nan
            adjusted_rows.append(
                {
                    "roi_i": ROI_SHORT_NAMES[i],
                    "roi_j": ROI_SHORT_NAMES[j],
                    "n": int(ok.sum()),
                    "beta_amyloid_adjusted_age_sex": beta,
                    "se_amyloid": se,
                    "t_amyloid": t_stat,
                    "p_amyloid": p_amyloid,
                }
            )
    adjusted = pd.DataFrame(adjusted_rows)
    finite_p = adjusted["p_amyloid"].notna()
    adjusted["q_fdr_amyloid"] = np.nan
    adjusted.loc[finite_p, "q_fdr_amyloid"] = multipletests(
        adjusted.loc[finite_p, "p_amyloid"], method="fdr_bh"
    )[1]
    adjusted.sort_values("p_amyloid").to_csv(
        TABLE_DIR / "pet_motor_connectivity_edges_age_sex_adjusted.csv", index=False
    )

    vmin, vmax = -0.45, 0.45
    fig, axes = plt.subplots(1, 3, figsize=(9.8, 3.35), constrained_layout=True)
    matrices = [mean_neg, mean_pos, diff]
    titles = [
        f"A- (n={conn_neg.shape[0]})",
        f"A+ (n={conn_pos.shape[0]})",
        "A+ minus A-",
    ]
    cmaps = ["viridis", "viridis", "coolwarm"]
    ranges = [(0, 1), (0, 1), (vmin, vmax)]
    for ax, mat, title, cmap, (lo, hi) in zip(axes, matrices, titles, cmaps, ranges):
        im = ax.imshow(mat, vmin=lo, vmax=hi, cmap=cmap)
        ax.set_title(title)
        ax.set_xticks(range(len(ROIS)))
        ax.set_yticks(range(len(ROIS)))
        ax.set_xticklabels(ROI_SHORT_NAMES, rotation=65, ha="right", fontsize=6)
        ax.set_yticklabels(ROI_SHORT_NAMES, fontsize=6)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
    fig.savefig(FIG_DIR / "pet_motor_connectivity.pdf")
    fig.savefig(FIG_DIR / "pet_motor_connectivity.png", dpi=300)
    plt.close(fig)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    pup = load_pup()
    cohort = build_pet_linked_cohort(pup)
    write_summary_tables(cohort)
    plot_pet_cohort(cohort)
    combine_pet_thickness_maps()
    run_cdr0_thickness_sensitivity(cohort)

    fmri_rows = build_fmri_pet_rows(pup)
    run_motor_connectivity(fmri_rows)


if __name__ == "__main__":
    main()
