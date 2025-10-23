#!/usr/bin/env python3
"""
Land Demand Calculator (LAO / RP3)

Python 3.12 module and CLI for estimating gross acres needed to accommodate new
residents and associated employment, plus persons-per-acre by use.

Indentation: tabs (per Bill's preference).

Key features
- Replicates the interactive artifact math in Python
- Single-scenario and batch modes (CSV or JSON input)
- Outputs: pretty console, JSON, CSV
- Presets: suburban, compact, tampa (placeholder), phoenix (placeholder)

Drop-in suggestion for RP3 repo
- Path: tools/rp3_land_demand.py (or rp3/land_demand.py if you prefer a package)
- Run: python tools/rp3_land_demand.py run --preset tampa --residents 150000

Notes
- Tampa and Phoenix presets are planning placeholdersâ€”calibrate with latest
  MPO/MAG/BEA assumptions (PPH, mixes, jobs/acre, civic standards, etc.).
- This is a planning-level tool; local entitlements and site constraints govern.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


# ------------------------------ Data Model ------------------------------ #

@dataclass
class LandDemandParams:
	residents: float = 100000.0
	pph: float = 2.6
	vacancy_pct: float = 8.0
	res_gross_up_pct: float = 25.0
	sf_share_pct: float = 70.0
	sf_density: float = 3.0
	mf_share_pct: float = 30.0
	mf_density: float = 20.0
	jobs_per_unit: float = 1.2
	emp_gross_up_pct: float = 10.0
	office_share_pct: float = 25.0
	office_jpa: float = 100.0
	retail_share_pct: float = 25.0
	retail_jpa: float = 40.0
	ind_share_pct: float = 50.0
	ind_jpa: float = 15.0
	civic_acres_per_1000: float = 8.0

	def normalized_shares(self) -> Dict[str, float]:
		"""Return normalized residential and employment shares that sum to 1.0."""
		r_sum = max(self.sf_share_pct + self.mf_share_pct, 1e-9)
		e_sum = max(
			self.office_share_pct + self.retail_share_pct + self.ind_share_pct,
			1e-9,
		)
		return {
			"sf": self.sf_share_pct / r_sum,
			"mf": self.mf_share_pct / r_sum,
			"off": self.office_share_pct / e_sum,
			"ret": self.retail_share_pct / e_sum,
			"ind": self.ind_share_pct / e_sum,
		}


def calc(params: LandDemandParams) -> Dict[str, Any]:
	"""Compute acres by use, jobs, units, and persons-per-acre.

	Returns a structured dictionary suitable for JSON or CSV flattening.
	"""
	sh = params.normalized_shares()
	residents = float(params.residents)
	pph = float(params.pph)
	vac = params.vacancy_pct / 100.0
	res_gross_up = params.res_gross_up_pct / 100.0

	households = residents / pph if pph > 0 else 0.0
	units = households * (1.0 + vac)
	sf_units = units * sh["sf"]
	mf_units = units * sh["mf"]

	res_acres_net = 0.0
	if params.sf_density > 0:
		res_acres_net += sf_units / params.sf_density
	if params.mf_density > 0:
		res_acres_net += mf_units / params.mf_density
	res_acres = res_acres_net * (1.0 + res_gross_up)

	jobs = units * params.jobs_per_unit
	emp_gross_up = params.emp_gross_up_pct / 100.0
	off_jobs = jobs * sh["off"]
	ret_jobs = jobs * sh["ret"]
	ind_jobs = jobs * sh["ind"]

	emp_acres_net = 0.0
	if params.office_jpa > 0:
		emp_acres_net += off_jobs / params.office_jpa
	if params.retail_jpa > 0:
		emp_acres_net += ret_jobs / params.retail_jpa
	if params.ind_jpa > 0:
		emp_acres_net += ind_jobs / params.ind_jpa

	emp_acres = emp_acres_net * (1.0 + emp_gross_up)
	civic_acres = (residents / 1000.0) * params.civic_acres_per_1000
	total_acres = res_acres + emp_acres + civic_acres
	sq_miles = total_acres / 640.0 if total_acres else 0.0

	def safe_div(a: float, b: float) -> Optional[float]:
		return (a / b) if (b and math.isfinite(a / b)) else None

	ppa_res = safe_div(residents, res_acres)
	ppa_emp = safe_div(residents, emp_acres)
	ppa_civ = safe_div(residents, civic_acres)
	ppa_overall = safe_div(residents, total_acres)

	return {
		"inputs": asdict(params),
		"normalized_shares_pct": {
			"sf": sh["sf"] * 100.0,
			"mf": sh["mf"] * 100.0,
			"office": sh["off"] * 100.0,
			"retail": sh["ret"] * 100.0,
			"industrial": sh["ind"] * 100.0,
		},
		"results": {
			"households": households,
			"units": units,
			"jobs": jobs,
			"acres": {
				"residential": res_acres,
				"employment": emp_acres,
				"civic": civic_acres,
				"total": total_acres,
			},
			"square_miles": sq_miles,
			"acres_per_1000_residents": {
				"residential": safe_div(res_acres, residents / 1000.0) if residents else None,
				"employment": safe_div(emp_acres, residents / 1000.0) if residents else None,
				"civic": safe_div(civic_acres, residents / 1000.0) if residents else None,
				"total": safe_div(total_acres, residents / 1000.0) if residents else None,
			},
			"persons_per_acre": {
				"residential": ppa_res,
				"employment": ppa_emp,
				"civic": ppa_civ,
				"overall": ppa_overall,
			},
		},
	}


# ------------------------------ Presets ------------------------------ #

PRESETS: Dict[str, LandDemandParams] = {
	"suburban": LandDemandParams(
		residents=100000, pph=2.6, vacancy_pct=8, res_gross_up_pct=25,
		sf_share_pct=70, sf_density=3, mf_share_pct=30, mf_density=20,
		jobs_per_unit=1.2, emp_gross_up_pct=10,
		office_share_pct=25, office_jpa=100,
		retail_share_pct=25, retail_jpa=40,
		ind_share_pct=50, ind_jpa=15,
		civic_acres_per_1000=8,
	),
	"compact": LandDemandParams(
		residents=100000, pph=2.4, vacancy_pct=8, res_gross_up_pct=20,
		sf_share_pct=40, sf_density=6, mf_share_pct=60, mf_density=35,
		jobs_per_unit=1.2, emp_gross_up_pct=5,
		office_share_pct=35, office_jpa=150,
		retail_share_pct=25, retail_jpa=60,
		ind_share_pct=40, ind_jpa=20,
		civic_acres_per_1000=6,
	),
	"tampa": LandDemandParams(
		# Placeholder â€“ confirm with Tampa Bay MPO/BEA
		residents=150000, pph=2.55, vacancy_pct=8, res_gross_up_pct=24,
		sf_share_pct=65, sf_density=3.5, mf_share_pct=35, mf_density=22,
		jobs_per_unit=1.15, emp_gross_up_pct=10,
		office_share_pct=28, office_jpa=110,
		retail_share_pct=27, retail_jpa=45,
		ind_share_pct=45, ind_jpa=16,
		civic_acres_per_1000=7.5,
	),
	"phoenix": LandDemandParams(
		# Placeholder â€“ confirm with MAG/BEA
		residents=300000, pph=2.7, vacancy_pct=7.5, res_gross_up_pct=25,
		sf_share_pct=68, sf_density=3.2, mf_share_pct=32, mf_density=24,
		jobs_per_unit=1.2, emp_gross_up_pct=10,
		office_share_pct=23, office_jpa=95,
		retail_share_pct=22, retail_jpa=38,
		ind_share_pct=55, ind_jpa=14,
		civic_acres_per_1000=8,
	),
}


def get_preset(name: str) -> LandDemandParams:
	key = name.lower()
	if key not in PRESETS:
		raise KeyError(f"Unknown preset '{name}'. Valid: {', '.join(PRESETS)}")
	return PRESETS[key]


# --------------------------- CSV/JSON helpers -------------------------- #

CSV_OUTPUT_COLUMNS: List[str] = [
	"scenario",
	"residents",
	"pph",
	"vacancy_pct",
	"res_gross_up_pct",
	"sf_share_pct",
	"sf_density",
	"mf_share_pct",
	"mf_density",
	"jobs_per_unit",
	"emp_gross_up_pct",
	"office_share_pct",
	"office_jpa",
	"retail_share_pct",
	"retail_jpa",
	"ind_share_pct",
	"ind_jpa",
	"civic_acres_per_1000",
	"units",
	"jobs",
	"acres_residential",
	"acres_employment",
	"acres_civic",
	"acres_total",
	"square_miles",
	"acres_per_1k_residential",
	"acres_per_1k_employment",
	"acres_per_1k_civic",
	"acres_per_1k_total",
	"ppa_residential",
	"ppa_employment",
	"ppa_civic",
	"ppa_overall",
]


def flatten_for_csv(name: str, res: Dict[str, Any]) -> Dict[str, Any]:
	p = res["inputs"]
	r = res["results"]
	apk = r["acres_per_1000_residents"]
	row = {
		"scenario": name,
		"residents": p["residents"],
		"pph": p["pph"],
		"vacancy_pct": p["vacancy_pct"],
		"res_gross_up_pct": p["res_gross_up_pct"],
		"sf_share_pct": p["sf_share_pct"],
		"sf_density": p["sf_density"],
		"mf_share_pct": p["mf_share_pct"],
		"mf_density": p["mf_density"],
		"jobs_per_unit": p["jobs_per_unit"],
		"emp_gross_up_pct": p["emp_gross_up_pct"],
		"office_share_pct": p["office_share_pct"],
		"office_jpa": p["office_jpa"],
		"retail_share_pct": p["retail_share_pct"],
		"retail_jpa": p["retail_jpa"],
		"ind_share_pct": p["ind_share_pct"],
		"ind_jpa": p["ind_jpa"],
		"civic_acres_per_1000": p["civic_acres_per_1000"],
		"units": r["units"],
		"jobs": r["jobs"],
		"acres_residential": r["acres"]["residential"],
		"acres_employment": r["acres"]["employment"],
		"acres_civic": r["acres"]["civic"],
		"acres_total": r["acres"]["total"],
		"square_miles": r["square_miles"],
		"acres_per_1k_residential": apk["residential"],
		"acres_per_1k_employment": apk["employment"],
		"acres_per_1k_civic": apk["civic"],
		"acres_per_1k_total": apk["total"],
		"ppa_residential": r["persons_per_acre"]["residential"],
		"ppa_employment": r["persons_per_acre"]["employment"],
		"ppa_civic": r["persons_per_acre"]["civic"],
		"ppa_overall": r["persons_per_acre"]["overall"],
	}
	return row


# ------------------------------- Printing ------------------------------ #

def fmt(n: Optional[float], d: int = 1) -> str:
	if n is None:
		return "â€”"
	try:
		return f"{n:,.{d}f}"
	except Exception:
		return str(n)


def print_pretty(name: str, res: Dict[str, Any]) -> None:
	r = res["results"]
	apk = r["acres_per_1000_residents"]
	print(f"Scenario: {name}")
	print("-" * (10 + len(name)))
	print(f"Housing units needed:\t{fmt(r['units'], 0)}")
	print(f"Jobs supported:\t\t{fmt(r['jobs'], 0)}")
	print(f"Total gross acres:\t{fmt(r['acres']['total'], 0)} ac")
	print(f"Square miles:\t\t{fmt(r['square_miles'], 2)} sq mi")
	print()
	print("Acres by Use")
	print("Category\t\tAcres\t\tPer 1,000 residents")
	print(f"Residential (gross)\t{fmt(r['acres']['residential'],0)}\t\t{fmt(apk['residential'],1)}")
	print(f"Employment (gross)\t{fmt(r['acres']['employment'],0)}\t\t{fmt(apk['employment'],1)}")
	print(f"Community/Civic\t\t{fmt(r['acres']['civic'],0)}\t\t{fmt(apk['civic'],1)}")
	print(f"Total\t\t\t{fmt(r['acres']['total'],0)}\t\t{fmt(apk['total'],1)}")
	print()
	print("Persons per Acre by Use")
	print("Category\t\tPersons per acre")
	print(f"Residential (gross)\t{fmt(r['persons_per_acre']['residential'],1)}")
	print(f"Employment (gross)\t{fmt(r['persons_per_acre']['employment'],1)}")
	print(f"Community/Civic\t\t{fmt(r['persons_per_acre']['civic'],1)}")
	print(f"Overall (weighted)\t{fmt(r['persons_per_acre']['overall'],1)}")


# ------------------------------- Parsers ------------------------------- #

def add_common_args(p: argparse.ArgumentParser) -> None:
	p.add_argument("--residents", type=float)
	p.add_argument("--pph", type=float)
	p.add_argument("--vacancy-pct", dest="vacancy_pct", type=float)
	p.add_argument("--res-gross-up-pct", dest="res_gross_up_pct", type=float)
	p.add_argument("--sf-share-pct", dest="sf_share_pct", type=float)
	p.add_argument("--sf-density", dest="sf_density", type=float)
	p.add_argument("--mf-share-pct", dest="mf_share_pct", type=float)
	p.add_argument("--mf-density", dest="mf_density", type=float)
	p.add_argument("--jobs-per-unit", dest="jobs_per_unit", type=float)
	p.add_argument("--emp-gross-up-pct", dest="emp_gross_up_pct", type=float)
	p.add_argument("--office-share-pct", dest="office_share_pct", type=float)
	p.add_argument("--office-jpa", dest="office_jpa", type=float)
	p.add_argument("--retail-share-pct", dest="retail_share_pct", type=float)
	p.add_argument("--retail-jpa", dest="retail_jpa", type=float)
	p.add_argument("--ind-share-pct", dest="ind_share_pct", type=float)
	p.add_argument("--ind-jpa", dest="ind_jpa", type=float)
	p.add_argument("--civic-per-1000", dest="civic_acres_per_1000", type=float)


def make_arg_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog="rp3_land_demand",
		description=(
			"LAO Land Demand: compute acres needed and persons-per-acre for growth "
			"scenarios (Python 3.12, tabs)."
		),
	)
	sp = parser.add_subparsers(dest="cmd", required=True)

	# run
	run_p = sp.add_parser("run", help="Run a single scenario")
	run_p.add_argument("--preset", choices=list(PRESETS), help="Starting preset")
	run_p.add_argument("--name", default="scenario", help="Scenario name label")
	add_common_args(run_p)
	run_p.add_argument("--stdout-format", choices=["pretty", "json", "csv"], default="pretty")
	run_p.add_argument("--out-json", type=Path)
	run_p.add_argument("--out-csv", type=Path)

	# batch
	batch_p = sp.add_parser("batch", help="Run a batch from CSV or JSON list")
	batch_p.add_argument("--input", type=Path, required=True, help="CSV or JSON file with scenarios")
	batch_p.add_argument("--out-csv", type=Path, help="Write merged results to CSV")
	batch_p.add_argument("--out-json", type=Path, help="Write list of results to JSON")

	# presets list
	pres_p = sp.add_parser("presets", help="List available presets")

	return parser


# ------------------------------- Commands ------------------------------ #

def params_from_namespace(ns: argparse.Namespace, base: Optional[LandDemandParams]) -> LandDemandParams:
	p = asdict(base if base else LandDemandParams())
	for k, v in vars(ns).items():
		if k in p and v is not None:
			p[k] = v
	return LandDemandParams(**p)


def cmd_run(ns: argparse.Namespace) -> int:
	base = get_preset(ns.preset) if ns.preset else LandDemandParams()
	params = params_from_namespace(ns, base)
	res = calc(params)
	name = ns.name

	if ns.stdout_format == "pretty":
		print_pretty(name, res)
	elif ns.stdout_format == "json":
		print(json.dumps({"scenario": name, **res}, indent=2))
	else:  # csv
		row = flatten_for_csv(name, res)
		writer = csv.DictWriter(sys.stdout, fieldnames=CSV_OUTPUT_COLUMNS)
		writer.writeheader()
		writer.writerow(row)

	if ns.out_json:
		ns.out_json.write_text(json.dumps({"scenario": name, **res}, indent=2))
	if ns.out_csv:
		with ns.out_csv.open("w", newline="") as f:
			writer = csv.DictWriter(f, fieldnames=CSV_OUTPUT_COLUMNS)
			writer.writeheader()
			writer.writerow(flatten_for_csv(name, res))
	return 0


def load_batch_input(path: Path) -> List[Dict[str, Any]]:
	if path.suffix.lower() == ".json":
		obj = json.loads(path.read_text())
		if isinstance(obj, dict) and "scenarios" in obj:
			obj = obj["scenarios"]
		if not isinstance(obj, list):
			raise ValueError("JSON input must be a list of scenario dicts or {scenarios:[...]}")
		return obj
	elif path.suffix.lower() == ".csv":
		rows: List[Dict[str, Any]] = []
		with path.open("r", newline="") as f:
			reader = csv.DictReader(f)
			for row in reader:
				rows.append(row)
		return rows
	else:
		raise ValueError("Unsupported input type. Use .csv or .json")


def coerce_params(d: Dict[str, Any]) -> LandDemandParams:
	# Accept strings from CSV and coerce if keys match dataclass
	defaults = asdict(LandDemandParams())
	vals: Dict[str, Any] = {}
	for k, v in defaults.items():
		if k in d and d[k] is not None and d[k] != "":
			try:
				vals[k] = type(v)(d[k])
			except Exception:
				# Fallback: try float
				try:
					vals[k] = float(d[k])
				except Exception:
					vals[k] = v
		else:
			vals[k] = v
	return LandDemandParams(**vals)


def cmd_batch(ns: argparse.Namespace) -> int:
	items = load_batch_input(ns.input)
	rows: List[Dict[str, Any]] = []

	for i, item in enumerate(items, start=1):
		name = str(item.get("scenario") or item.get("name") or f"scenario_{i}")
		preset = item.get("preset")
		base = get_preset(preset) if preset else LandDemandParams()
		# Merge: CSV/JSON entries can override preset
		merged = {**asdict(base), **{k: v for k, v in item.items() if k in asdict(base)}}
		params = coerce_params(merged)
		res = calc(params)
		rows.append(flatten_for_csv(name, res))

	# Output
	if ns.out_csv:
		with ns.out_csv.open("w", newline="") as f:
			writer = csv.DictWriter(f, fieldnames=CSV_OUTPUT_COLUMNS)
			writer.writeheader()
			writer.writerows(rows)
	else:
		# Default to stdout CSV
		writer = csv.DictWriter(sys.stdout, fieldnames=CSV_OUTPUT_COLUMNS)
		writer.writeheader()
		writer.writerows(rows)

	if ns.out_json:
		# Recompute full JSON payloads for completeness
		full_results: List[Dict[str, Any]] = []
		for row in items:
			name = str(row.get("scenario") or row.get("name") or "scenario")
			preset = row.get("preset")
			base = get_preset(preset) if preset else LandDemandParams()
			merged = {**asdict(base), **{k: v for k, v in row.items() if k in asdict(base)}}
			params = coerce_params(merged)
			res = calc(params)
			full_results.append({"scenario": name, **res})
		ns.out_json.write_text(json.dumps(full_results, indent=2))
	return 0


def cmd_presets(_: argparse.Namespace) -> int:
	print("Available presets:")
	for k, v in PRESETS.items():
		print(f"- {k}")
	return 0


# --------------------------------- Main -------------------------------- #

def main(argv: Optional[List[str]] = None) -> int:
	parser = make_arg_parser()
	ns = parser.parse_args(argv)
	if ns.cmd == "run":
		return cmd_run(ns)
	if ns.cmd == "batch":
		return cmd_batch(ns)
	if ns.cmd == "presets":
		return cmd_presets(ns)
	return 0


if __name__ == "__main__":
	sys.exit(main())