"""Generate synthetic Thai P&C insurance data for the Genie workshop.

Run from the repo root:
    python data/generate_data.py

Produces 5 CSVs in data/: customers, branches, agents, policies, claims.
Deterministic — same output every run.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
OUT = Path(__file__).parent

# Sized so the workshop loads fast but joins still produce interesting aggregates.
N_CUSTOMERS = 3_000
N_AGENTS = 50
N_BRANCHES = 10
N_POLICIES = 10_000
N_CLAIMS = 5_000

# Curated Thai-flavored reference lists (small + readable; not exhaustive).
THAI_FIRST_NAMES = [
    "Somchai", "Niran", "Anong", "Suda", "Pim", "Kanya", "Tawan", "Wichai",
    "Malee", "Apinya", "Chai", "Daeng", "Eak", "Fern", "Nok", "Ploy",
    "Pat", "Praew", "Tee", "Toon", "Mint", "Bua", "Nan", "Beam",
    "Mai", "Earth", "Bank", "Boss", "View", "Mild",
]
THAI_LAST_NAMES = [
    "Boonmee", "Srisuk", "Wongchai", "Phongphan", "Chaiyaporn", "Kittikun",
    "Sukhumvit", "Rattanapan", "Suwanphon", "Thongdee", "Charoensuk",
    "Sangthong", "Inthanon", "Phutthichai", "Kanchanaburi", "Watcharaphon",
    "Saetang", "Limthongkul", "Phromsiri", "Chaisawat",
]
PROVINCES = [
    "Bangkok", "Chiang Mai", "Phuket", "Khon Kaen", "Chonburi", "Nonthaburi",
    "Songkhla", "Surat Thani", "Udon Thani", "Nakhon Ratchasima", "Pathum Thani",
    "Samut Prakan", "Rayong", "Ayutthaya", "Hat Yai", "Krabi", "Chiang Rai",
    "Lampang", "Phitsanulok", "Trang",
]
REGIONS = {
    "Bangkok": "Central", "Nonthaburi": "Central", "Pathum Thani": "Central",
    "Samut Prakan": "Central", "Ayutthaya": "Central",
    "Chiang Mai": "North", "Chiang Rai": "North", "Lampang": "North", "Phitsanulok": "North",
    "Khon Kaen": "Northeast", "Udon Thani": "Northeast", "Nakhon Ratchasima": "Northeast",
    "Phuket": "South", "Songkhla": "South", "Surat Thani": "South",
    "Hat Yai": "South", "Krabi": "South", "Trang": "South",
    "Chonburi": "East", "Rayong": "East",
}
OCCUPATIONS = [
    "Government Officer", "Teacher", "Engineer", "Doctor", "Nurse",
    "Shop Owner", "Driver", "Farmer", "Office Worker", "Sales",
    "IT Specialist", "Accountant", "Hotel Staff", "Restaurant Owner",
    "Construction Worker",
]
MOTOR_SUBTYPES = ["motor_voluntary", "motor_compulsory"]
PROPERTY_SUBTYPES = ["property_fire", "property_allrisk", "property_flood"]
LOSS_TYPES_MOTOR = ["collision", "theft", "third_party_liability", "fire", "flood"]
LOSS_TYPES_PROPERTY = ["fire", "flood", "burglary", "storm", "water_damage"]
COMMISSION_TIERS = ["bronze", "silver", "gold"]
CLAIM_STATUSES = ["open", "paid", "denied", "pending"]
POLICY_STATUSES = ["active", "lapsed", "cancelled"]
PAYMENT_FREQS = ["monthly", "quarterly", "annual"]


def daterange_random(rng: random.Random, start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=rng.randint(0, delta))


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {path.name}: {len(rows):,} rows")


def main() -> None:
    rng = random.Random(SEED)
    today = date(2026, 5, 14)

    # --- branches ---
    branch_provinces = rng.sample(PROVINCES, N_BRANCHES)
    branches = []
    for i, prov in enumerate(branch_provinces, start=1):
        branches.append([
            f"B{i:03d}",
            f"{prov} Branch",
            prov,
            REGIONS.get(prov, "Central"),
            daterange_random(rng, date(2005, 1, 1), date(2020, 12, 31)).isoformat(),
        ])
    write_csv(
        OUT / "branches.csv",
        ["branch_id", "branch_name", "province", "region", "opened_date"],
        branches,
    )

    # --- agents ---
    agents = []
    for i in range(1, N_AGENTS + 1):
        first = rng.choice(THAI_FIRST_NAMES)
        last = rng.choice(THAI_LAST_NAMES)
        branch = rng.choice(branches)
        tier = rng.choices(COMMISSION_TIERS, weights=[0.5, 0.35, 0.15])[0]
        agents.append([
            f"A{i:04d}",
            f"{first} {last}",
            f"LIC-{rng.randint(10000, 99999)}",
            branch[0],
            daterange_random(rng, date(2010, 1, 1), date(2024, 12, 31)).isoformat(),
            tier,
        ])
    write_csv(
        OUT / "agents.csv",
        ["agent_id", "agent_name", "license_no", "branch_id", "hire_date", "commission_tier"],
        agents,
    )

    # --- customers ---
    customers = []
    for i in range(1, N_CUSTOMERS + 1):
        first = rng.choice(THAI_FIRST_NAMES)
        last = rng.choice(THAI_LAST_NAMES)
        dob = daterange_random(rng, date(1955, 1, 1), date(2005, 12, 31))
        province = rng.choice(PROVINCES)
        customers.append([
            f"C{i:05d}",
            first,
            last,
            dob.isoformat(),
            rng.choice(["M", "F"]),
            rng.choice(OCCUPATIONS),
            province,
            f"08{rng.randint(10000000, 99999999)}",
            f"{first.lower()}.{last.lower()}{i}@example.co.th",
            daterange_random(rng, date(2018, 1, 1), today).isoformat(),
        ])
    write_csv(
        OUT / "customers.csv",
        ["customer_id", "first_name", "last_name", "dob", "gender", "occupation",
         "province", "phone", "email", "customer_since"],
        customers,
    )

    # --- policies ---
    policies = []
    for i in range(1, N_POLICIES + 1):
        product_line = rng.choices(["motor", "property"], weights=[0.7, 0.3])[0]
        if product_line == "motor":
            subtype = rng.choice(MOTOR_SUBTYPES)
            sum_insured = rng.randint(200_000, 2_500_000)
            premium = int(sum_insured * rng.uniform(0.02, 0.05))
        else:
            subtype = rng.choice(PROPERTY_SUBTYPES)
            sum_insured = rng.randint(1_000_000, 20_000_000)
            premium = int(sum_insured * rng.uniform(0.003, 0.012))
        effective = daterange_random(rng, date(2023, 1, 1), date(2026, 5, 1))
        expiry = effective + timedelta(days=365)
        # Force ~70% currently in-force so attendees can ask "in-force policies" questions.
        if rng.random() < 0.3:
            effective = daterange_random(rng, date(2022, 1, 1), date(2024, 6, 1))
            expiry = effective + timedelta(days=365)
        status = rng.choices(POLICY_STATUSES, weights=[0.82, 0.13, 0.05])[0]
        policies.append([
            f"P{i:06d}",
            rng.choice(customers)[0],
            rng.choice(agents)[0],
            product_line,
            subtype,
            effective.isoformat(),
            expiry.isoformat(),
            sum_insured,
            premium,
            rng.choice(PAYMENT_FREQS),
            status,
        ])
    write_csv(
        OUT / "policies.csv",
        ["policy_id", "customer_id", "agent_id", "product_line", "product_subtype",
         "effective_date", "expiry_date", "sum_insured_thb", "annual_premium_thb",
         "payment_frequency", "status"],
        policies,
    )

    # --- claims ---
    # Only ~50% of policies generate at least one claim; some have multiple.
    claims = []
    claim_id = 1
    while len(claims) < N_CLAIMS:
        policy = rng.choice(policies)
        policy_id = policy[0]
        product_line = policy[3]
        eff_date = date.fromisoformat(policy[5])
        exp_date = date.fromisoformat(policy[6])
        # Loss date must fall inside the policy period.
        if exp_date <= eff_date:
            continue
        loss_date = daterange_random(rng, eff_date, min(exp_date, today))
        report_date = loss_date + timedelta(days=rng.randint(0, 14))
        loss_pool = LOSS_TYPES_MOTOR if product_line == "motor" else LOSS_TYPES_PROPERTY
        loss_type = rng.choice(loss_pool)
        sum_insured = int(policy[7])
        # Claim amount usually small fraction of sum insured.
        claim_amount = int(sum_insured * rng.uniform(0.02, 0.4))
        status = rng.choices(CLAIM_STATUSES, weights=[0.15, 0.6, 0.1, 0.15])[0]
        settle_date = ""
        if status in ("paid", "denied"):
            settle_date = (report_date + timedelta(days=rng.randint(7, 90))).isoformat()
        fraud_flag = rng.random() < 0.03
        claims.append([
            f"CL{claim_id:06d}",
            policy_id,
            loss_date.isoformat(),
            report_date.isoformat(),
            settle_date,
            loss_type,
            claim_amount,
            status,
            f"{rng.choice(THAI_FIRST_NAMES)} {rng.choice(THAI_LAST_NAMES)}",
            "true" if fraud_flag else "false",
        ])
        claim_id += 1
    write_csv(
        OUT / "claims.csv",
        ["claim_id", "policy_id", "loss_date", "report_date", "settle_date",
         "loss_type", "claim_amount_thb", "status", "adjuster_name", "fraud_flag"],
        claims,
    )

    print("\nDone. Files written to:", OUT)


if __name__ == "__main__":
    main()
