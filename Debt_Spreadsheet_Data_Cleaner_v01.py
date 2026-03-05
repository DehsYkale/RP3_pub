import pandas as pd
import numpy as np
import lao

folder_source = 'F:/Research Department/MIMO/zData/Debt/Property Radar/'
file_input  = folder_source + 'TX 2026-02-24.csv'
file_output = folder_source + 'TX 2026-02-24_clean.csv'

lGroup_keys = ['1st Amount', '1st Rec Date', '1st Orig Lender']

def most_common(s):
	"""Return most frequent non-null value; NaN if all null."""
	s = s.dropna()
	if s.empty:
		return np.nan
	return s.mode().iloc[0]

def merge_group(g):
	row = {}

	# --- APN: join all unique values
	row['APN'] = ', '.join(g['APN'].dropna().unique())

	# --- Numeric aggregations
	row['Lot Acres']  = g['Lot Acres'].sum()
	row['Latitude']   = g['Latitude'].mean()
	row['Longitude']  = g['Longitude'].mean()

	# --- Purchase Date: most recent
	pd_series = pd.to_datetime(g['Purchase Date'], errors='coerce')
	row['Purchase Date'] = pd_series.max().strftime('%#m/%#d/%Y') if pd_series.notna().any() else np.nan

	# --- Purchase Amt: sum
	row['Purchase Amt'] = g['Purchase Amt'].sum() if g['Purchase Amt'].notna().any() else np.nan

	# --- All other columns: most common value
	skip = {'APN', 'Lot Acres', 'Latitude', 'Longitude', 'Purchase Date', 'Purchase Amt'}
	for col in g.columns:
		if col not in skip:
			row[col] = most_common(g[col])

	return pd.Series(row)

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(file_input)
original_cols = df.columns.tolist()
print(f'Loaded {len(df):,} rows')

# ── Split single vs multi ─────────────────────────────────────────────────────
counts   = df.groupby(lGroup_keys, dropna=False)[lGroup_keys[0]].transform('count')
singles  = df[counts == 1].copy()
multis   = df[counts >  1].copy()

print(f'Single-parcel rows : {len(singles):,}')
print(f'Multi-parcel rows  : {len(multis):,}  → {multis.groupby(lGroup_keys).ngroups:,} groups')

# ── Merge multi-parcel groups ─────────────────────────────────────────────────
merged = (
	multis.groupby(lGroup_keys, dropna=False)
	.apply(merge_group, include_groups=False)
	.reset_index()          # brings lGroup_keys back as columns
)
print(f'Merged into        : {len(merged):,} rows')

# ── Combine and restore column order ─────────────────────────────────────────
out = pd.concat([singles, merged], ignore_index=True)
out = out[original_cols]   # restore original column order

mask_small = ~out['APN'].str.contains(',', na=False) & (out['Lot Acres'] < 5)
out = out[~mask_small]

print(f'After acreage filter: {len(out):,} rows  (removed {mask_small.sum():,} single-APN rows under 5 acres)')

out.to_csv(file_output, index=False)
print(f'\nSaved → {file_output}')

lao.openFile(file_output)