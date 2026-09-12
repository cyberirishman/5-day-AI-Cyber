# Day 3 · Lab 6 — dataset provenance

**Files in `day3_lab6/` in the course repo:**

| File | Rows | What it is |
|---|---|---|
| `day3_auth_enriched_v1.csv` | 11,494 | the login log students load |
| `day3_answer_key.csv` | 611 | which rows were really attacks — revealed only at Step 8 |
| `Day3_Anomaly_Lab_v1.ipynb` | — | the lab notebook, opened via its Colab badge |
| `build_day3_dataset.py` | — | the generator, kept for provenance and reproducibility |

Raw URLs the notebook uses (these are hard-coded, do not rename the files):

```
https://raw.githubusercontent.com/cyberirishman/5-day-AI-Cyber/main/day3_lab6/day3_auth_enriched_v1.csv
https://raw.githubusercontent.com/cyberirishman/5-day-AI-Cyber/main/day3_lab6/day3_answer_key.csv
```

---

## Where the data comes from

The base is **`day2_auth_logs.csv`** — 8,945 rows, itself drawn from the published
**RBA dataset** (Wiefling, Lo Iacono, Dürmuth — *"Is This Really You? An Empirical Study
on Risk-Based Authentication Applied in the Wild"*, IFIP SEC 2019). Norwegian online
service, real logins, pseudonymised accounts and IP addresses.

**Every one of those 8,945 rows keeps all of its original field values.** Two changes only:

1. `Round-Trip Time [ms]` was **dropped** — 8,395 of 8,945 values were empty (94%).
2. The `index` column was **renumbered** 1…11,494, because the merged file is re-sorted
   into timestamp order.

The **387 rows of the five campaign accounts are byte-identical** to the Day-2 file
(verified). So every number on Day-3 slides 25 and 30 — 387 attack lines, 51 flagged by
the blocklist, `is_foreign` 0.907, recall 0.89 → 1.00 — still holds on this file.

`day2_auth_logs.csv` itself is **untouched**, so nothing on Day 2 changes.

---

## Why anything was added at all

The source file cannot support a history-based detector:

| | source | enriched |
|---|---|---|
| rows | 8,945 | 11,494 |
| accounts appearing **exactly once** | 8,471 of 8,518 | 8,082 of 8,518 |
| accounts with ≥ 2 logins | 47 | **436** |
| accounts with ≥ 5 logins | 5 | **324** |
| accounts with a success after a failure | 4 | **149** |
| account takeovers | **3** | **18** (0.16%) |

With 95% of rows belonging to an account that appears once, *"how many times has this
account failed before?"* is zero almost everywhere and the feature is dead on arrival.
The fix was **history, not more attacks**.

---

## What was added — exactly

### A · Ordinary login histories — 2,325 rows, 389 accounts

389 accounts that originally appeared once (Norwegian, successful, not campaign
accounts) were each given **2–9 extra logins** spread over the 7-day window: same ASN,
same `/24`, last octet varied (home broadband behaviour), same browser and OS, plausible
daytime hours. **8% of these include one mistyped password immediately followed by a
success** — ordinary human error.

These rows are **not** in the answer key. They are simply normal life.

### B · 15 new account takeovers — 156 rows

Each: an account from group A with an established history → **5–12 failures from ONE new
foreign IP inside 40–120 seconds** → **one success**. 15 distinct hosting/VPN networks
across NL, GB, RO, SG, IN, BR, TR, CA, FR, VN, ZA, DE, HK, PL, MX.

Deliberate design so the lab cannot be won by a shortcut:

| Choice | Why |
|---|---|
| **5 of 15 use a real browser user-agent** (Chrome 124 / Safari 17.4 / iOS) | students cannot just grep for `python-requests` |
| **6 of 15 happen in business hours** | "it was at night" is not the answer |
| **only ~1/3 of the new attacker IPs get `Is Attack IP = True`** | the blocklist still misses most attacks, which is the point of the whole day |
| **all synthetic timestamps carry random milliseconds** | no whole-second tell (the source has exactly 21 such rows; the enriched file still has exactly 21) |
| **no `synthetic` column in the CSV** | the answer key ships as a separate file |

### C · Hard negatives — 68 rows. **These are the pedagogically important ones.**

Innocent logins engineered to look guilty, so the lab produces real false positives:

| Kind | Rows | What it is |
|---|---|---|
| `hard_negative_travel` | 21 | a real user on holiday — foreign, successful, own browser, no failures (ES, IT, GR, US, FR, PT, TH, GB, DK, NL) |
| `hard_negative_forgot_password` | 41 | 3–5 failures then success — **from the user's own home IP and own browser** |
| `hard_negative_new_device` | 6 | first login from a new laptop or phone, same country, first try |

Measured outcome: the Isolation Forest's top 600 flags **33 of the 41** forgot-password
rows and only **2 of the 21** travel rows. That is the honest limit of the technique and
Step 10 of the notebook is built on it — behaviourally, "I forgot my password" and
"someone is guessing my password" are nearly the same event.

---

## Holdout — how we know the detector is not just finding the generator

The **3 original takeovers are untouched real-dataset rows.** If the detector were only
recognising my generator, the 15 synthetic takeovers would cluster at the top and the 3
originals would sit far below. They do not — they interleave:

```
Isolation Forest rank of all 18 takeovers (out of 11,494 rows)
  synthetic:  88  98 112 123 134 143 146 160 177 198 201 205 222 268 273
  ORIGINAL:  169 202 259          <-- untouched real rows, mixed straight in
```

---

## Measured results (seed 42, reproducible)

Answer key: **537 attack rows (4.7%)**, 68 hard negatives.

| Detector | Alerts reviewed | Precision | Recall | Takeovers found | False alarms |
|---|---|---|---|---|---|
| Isolation Forest | 120 | 100.0% | 22.3% | 3/18 | 0 |
| Isolation Forest | 240 | 100.0% | 44.7% | 15/18 | 0 |
| **Isolation Forest** | **600** | **87.2%** | **97.4%** | **18/18** | **77** |
| Autoencoder (Keras) | 120 | 87.5% | 19.6% | 0/18 | 15 |
| Autoencoder (Keras) | 240 | 93.8% | 41.9% | 6/18 | 15 |
| Autoencoder (Keras) | 600 | 84.3% | 94.2% | 18/18 | 94 |

For comparison, from Day-3 slides 29 and 30 on the same underlying data:

| Approach | Recall | False alarms | Needs a label? |
|---|---|---|---|
| Decision Tree on `Is Attack IP` | 0.89 | 669 | yes |
| Decision Tree on campaign behaviour | 1.00 | 247 | yes |
| **Isolation Forest, no label at all** | **0.97** | **77** | **no** |

**The Isolation Forest beats the neural network at every threshold**, and ranks all 18
takeovers higher. That is deliberate teaching content, not a disappointment: on eight
tidy numeric columns there is no deep structure for a network to find, and the simpler
method has fewer ways to go wrong.

---

## Features used (labels excluded)

`fail` · `foreign` · `night` · `bot` · `prev_fail_user` · `prev_fail_ip` ·
`new_country` · `log_gap`

The three history features are computed **causally — past rows only**, by walking the
log in timestamp order. The notebook demonstrates the wrong way first
(`groupby().transform()` over the whole file), which stamps June 8th's failure count
onto a June 2nd row, and names it: **data leakage**.

Coverage in the enriched file: `prev_fail_user > 0` on 1,198 rows,
`prev_fail_ip > 0` on 856, `new_country` on 68.

### Two features that honestly do not work, and are kept anyway

- **`night`** — attack rows are 10.0% night against a 7.8% baseline. Nearly no signal.
  Kept so students can see for themselves that a feature everyone assumes matters
  does not. **No night-weighting was applied to the synthetic attacks** — inflating it
  would have manufactured the signal we are teaching them to distrust.
- **raw `User Agent String`** — 3,686 distinct values in 8,945 source rows, effectively
  unique per row. Useless directly; `bot` and "new device for this account" are the
  usable derivatives.

---

## Regenerating

```bash
python3 build_day3_dataset.py     # needs day2_auth_logs.csv in the same directory
```

`SEED = 20260912`. Same seed, same file, byte for byte.

---

*Generated 2026-09-12 for Day 3 · Lab 6 — "Finding Attacks With No Labels At All".*
