#!/usr/bin/env python3
"""
build_day3_dataset.py — generator for day3_auth_enriched_v1.csv
================================================================
Takes the Day-2 auth log (8,945 real rows from the RBA dataset, Wiefling et al.)
and adds the three things it is missing for an unsupervised-detection lab:

  A  ~350 ordinary users given a REAL multi-login history
     (today 8,471 of 8,518 usernames appear exactly ONCE, so any
      "has this account done anything before?" feature is dead on arrival)
  B  15 new account-takeover cases  (success after a failure burst)
  C  24 HARD NEGATIVES — innocent logins that look guilty

Every original row keeps all of its field values. Only the `index` column is
renumbered, because the merged file is re-sorted into timestamp order.
`Round-Trip Time [ms]` is dropped: 94% null in the source.

Deliberate design choices, so the lab cannot be won by a cheap shortcut:
  * 5 of the 15 new takeovers use a REAL browser user-agent  -> cannot grep for python-requests
  * 6 of the 15 happen in business hours                     -> hour-of-day is not a free giveaway
  * only ~1/3 of new attacker IPs get `Is Attack IP = True`  -> the blocklist still misses most attacks
  * all synthetic timestamps carry random microseconds       -> no whole-second tell
  * NO "synthetic" column in the CSV                         -> the answer key ships separately

Outputs:
  day3_auth_enriched_v1.csv   the dataset the students load
  day3_answer_key.csv         index -> attack_type, revealed only AFTER scoring
"""

import numpy as np
import pandas as pd

SEED = 20260912
rng = np.random.default_rng(SEED)

SRC = "day2_auth_logs.csv"
OUT_DATA = "day3_auth_enriched_v1.csv"
OUT_KEY = "day3_answer_key.csv"

# The five campaign accounts that define "attack" behaviourally in the Day-3 deck
# (all their rows = 387; the `Is Attack IP` blocklist flags only 51 of them).
CAMPAIGN_ACCOUNTS = [
    "user_a44feb", "user_fd805b", "user_840bfc", "user_a4549c", "user_c99b98"
]
ORIGINAL_ATO = ["user_840bfc", "user_a4549c", "user_c99b98"]

src = pd.read_csv(SRC)
src["ts"] = pd.to_datetime(src["Login Timestamp"])
COLS = [c for c in src.columns if c not in ("ts", "Round-Trip Time [ms]")]

T0, T1 = src.ts.min(), src.ts.max()

# ---------------------------------------------------------------- helpers
def stamp(ts):
    """Format a timestamp the way the source file does, always with microseconds."""
    return ts.strftime("%Y-%m-%d %H:%M:%S.") + f"{ts.microsecond // 1000:03d}"

def jitter_ip(ip):
    """Same /24 as the user's usual address, different host — a normal DHCP change."""
    parts = ip.split(".")
    if len(parts) != 4:
        return ip
    parts[3] = str(int(rng.integers(2, 254)))
    return ".".join(parts)

def daytime(day_offset, night=False):
    """A plausible login moment. Ordinary people log in during the day."""
    base = T0.normalize() + pd.Timedelta(days=int(day_offset))
    hour = int(rng.integers(0, 5)) if night else int(rng.choice(
        [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
        p=[.04, .07, .09, .09, .08, .07, .07, .07, .07, .07, .06, .05, .05, .05, .04, .03]))
    return base + pd.Timedelta(hours=hour, minutes=int(rng.integers(0, 60)),
                               seconds=int(rng.integers(0, 60)),
                               milliseconds=int(rng.integers(1, 999)))

# Scripted clients an attacker's tooling announces itself with
SCRIPTED_UA = [
    ("Go-http-client/2.0", "Go-http-client 2.0", "Other", "desktop"),
    ("python-requests/2.31.0", "Python Requests 2.31", "Other", "desktop"),
    ("curl/8.4.0", "Curl 8.4.0", "Other", "desktop"),
    ("Mozilla/5.0 (compatible; hydra)", "Other", "Other", "desktop"),
]
# Real browsers — an attacker who bothers to set a plausible header
BROWSER_UA = [
    ("Mozilla/5.0  (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko Chrome/124.0.6367.91 Safari/537.36",
     "Chrome 124.0.6367", "Windows 10", "desktop"),
    ("Mozilla/5.0  (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko Version/17.4 Safari/605.1.15",
     "Safari 17.4", "Mac OS X 10.15.7", "desktop"),
    ("Mozilla/5.0  (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko Version/17.4 Mobile Safari/604.1",
     "Mobile Safari 17.4", "iOS 17.4", "mobile"),
]

# Hosting / VPN networks that real credential-stuffing traffic arrives from
ATTACK_NETS = [
    ("45.83.90.",    "NL", "North Holland", "Amsterdam",  9009),
    ("185.234.218.", "GB", "England",       "London",     209588),
    ("92.118.39.",   "RO", "Bucharest",     "Bucharest",  51167),
    ("103.152.118.", "SG", "Singapore",     "Singapore",  16509),
    ("188.166.42.",  "IN", "Maharashtra",   "Mumbai",     14061),
    ("179.60.147.",  "BR", "Sao Paulo",     "Sao Paulo",  262287),
    ("45.134.26.",   "TR", "Istanbul",      "Istanbul",   208091),
    ("156.146.51.",  "CA", "Ontario",       "Toronto",    60068),
    ("194.36.111.",  "FR", "Ile-de-France", "Paris",      16276),
    ("43.225.189.",  "VN", "Hanoi",         "Hanoi",      131353),
    ("196.196.53.",  "ZA", "Gauteng",       "Johannesburg", 37153),
    ("5.181.233.",   "DE", "Hesse",         "Frankfurt",  24940),
    ("103.27.202.",  "HK", "Hong Kong",     "Hong Kong",  45090),
    ("185.107.56.",  "PL", "Masovia",       "Warsaw",     202425),
    ("102.129.145.", "MX", "Mexico City",   "Mexico City", 46844),
]
# Countries an ordinary Norwegian might genuinely log in from on holiday
TRAVEL = [
    ("ES", "Andalusia", "Malaga", 12430, "81.40.22."),
    ("IT", "Tuscany", "Florence", 30722, "79.31.140."),
    ("GR", "Attica", "Athens", 3329, "94.68.71."),
    ("US", "New York", "New York", 701, "74.108.19."),
    ("FR", "Provence", "Nice", 15557, "88.185.6."),
    ("PT", "Lisbon", "Lisbon", 8657, "85.244.7."),
    ("TH", "Bangkok", "Bangkok", 45758, "183.88.210."),
    ("GB", "Scotland", "Edinburgh", 2856, "86.15.44."),
    ("DK", "Capital Region", "Copenhagen", 3292, "80.62.117."),
    ("NL", "North Holland", "Amsterdam", 1136, "82.174.90."),
]

new_rows = []      # dicts, appended in build order
key_rows = []      # (Login Timestamp, Username, attack_type) -> resolved to index later

def emit(ts, username, uid, ip, country, region, city, asn, ua, browser, os_name,
         device, success, atk_ip, ato, key=None):
    new_rows.append({
        "index": None,
        "Login Timestamp": stamp(ts),
        "Username": username,
        "User ID": uid,
        "IP Address": ip,
        "Country": country,
        "Region": region,
        "City": city,
        "ASN": asn,
        "User Agent String": ua,
        "Browser Name and Version": browser,
        "OS Name and Version": os_name,
        "Device Type": device,
        "Login Successful": success,
        "Is Attack IP": atk_ip,
        "Is Account Takeover": ato,
    })
    if key:
        key_rows.append({"Login Timestamp": stamp(ts), "Username": username,
                         "attack_type": key})

# ---------------------------------------------------------------- candidate pool
# Ordinary Norwegian desktop/mobile accounts that appear exactly once and succeeded.
counts = src.Username.value_counts()
singles = set(counts[counts == 1].index)
pool = src[(src.Username.isin(singles)) & (src.Country == "NO")
           & (src["Login Successful"]) & (~src.Username.isin(CAMPAIGN_ACCOUNTS))][COLS]
pool = pool.sample(frac=1.0, random_state=SEED).reset_index(drop=True)

HIST_N, ATO_N, TRAVEL_N, FAT_N, DEV_N = 350, 15, 10, 8, 6
need = HIST_N + ATO_N + TRAVEL_N + FAT_N + DEV_N
assert len(pool) >= need, f"pool too small: {len(pool)} < {need}"

cut = np.cumsum([HIST_N, ATO_N, TRAVEL_N, FAT_N, DEV_N])
hist_users = pool.iloc[:cut[0]]
ato_users = pool.iloc[cut[0]:cut[1]]
travel_users = pool.iloc[cut[1]:cut[2]]
fat_users = pool.iloc[cut[2]:cut[3]]
dev_users = pool.iloc[cut[3]:cut[4]]

# ======================================================== A — real user histories
# 2-9 extra logins each, same home network, same browser, mostly successful.
# ~8% of them are a single mistyped password immediately followed by a success —
# which is what ordinary human error actually looks like in a log.
def own(r, ts, ip, success, key=None, ua=None):
    """One login from this user's own device and network."""
    u = ua or (r["User Agent String"], r["Browser Name and Version"],
               r["OS Name and Version"], r["Device Type"])
    emit(ts, r["Username"], r["User ID"], ip, r["Country"], r["Region"], r["City"],
         r["ASN"], u[0], u[1], u[2], u[3], success, False, False, key=key)

everyone = pd.concat([hist_users, ato_users, travel_users, fat_users, dev_users])
for _, r in everyone.iterrows():
    for _ in range(int(rng.integers(2, 10))):
        ts = daytime(rng.integers(0, 7))
        ip = jitter_ip(r["IP Address"])
        if rng.random() < 0.08:      # fat finger, then straight back in
            own(r, ts, ip, False)
            ts = ts + pd.Timedelta(seconds=int(rng.integers(8, 50)),
                                   milliseconds=int(rng.integers(1, 999)))
        own(r, ts, ip, True)

# ======================================================== B — 15 new takeovers
# Known-good account -> burst of failures from ONE new foreign IP -> success.
for i, (_, r) in enumerate(ato_users.iterrows()):
    prefix, country, region, city, asn = ATTACK_NETS[i]
    ip = prefix + str(int(rng.integers(3, 250)))
    # 5 of 15 use a real browser UA; the rest announce themselves as tooling
    ua, browser, os_name, device = (BROWSER_UA[i % len(BROWSER_UA)] if i % 3 == 0
                                    else SCRIPTED_UA[i % len(SCRIPTED_UA)])
    # 6 of 15 in business hours, so "it happened at night" is not the answer
    at_night = (i % 5) not in (0, 1)
    start = daytime(rng.integers(1, 7), night=at_night)
    # Only about a third of these IPs ever make it onto the blocklist
    on_blocklist = bool(rng.random() < 0.33)
    tries = int(rng.integers(5, 13))
    t = start
    for _ in range(tries):
        emit(t, r["Username"], r["User ID"], ip, country, region, city, asn, ua,
             browser, os_name, device, False, on_blocklist, False,
             key="takeover_attempt")
        t = t + pd.Timedelta(seconds=int(rng.integers(4, 16)),
                             milliseconds=int(rng.integers(1, 999)))
    emit(t, r["Username"], r["User ID"], ip, country, region, city, asn, ua,
         browser, os_name, device, True, on_blocklist, True,
         key="takeover_success")

# ======================================================== C — hard negatives
# C1  Holiday. Foreign, successful, real browser, no failures. INNOCENT.
for i, (_, r) in enumerate(travel_users.iterrows()):
    country, region, city, asn, prefix = TRAVEL[i]
    ip = prefix + str(int(rng.integers(3, 250)))
    for _ in range(int(rng.integers(1, 4))):
        emit(daytime(rng.integers(2, 7)), r["Username"], r["User ID"], ip, country,
             region, city, asn, r["User Agent String"],
             r["Browser Name and Version"], r["OS Name and Version"],
             r["Device Type"], True, False, False, key="hard_negative_travel")

# C2  Genuinely forgot the password: 3-5 failures then success — but from the
#     user's OWN home IP, own browser. Looks like a burst. Is not one.
for _, r in fat_users.iterrows():
    ip = jitter_ip(r["IP Address"])
    t = daytime(rng.integers(0, 7))
    for _ in range(int(rng.integers(3, 6))):
        own(r, t, ip, False, key="hard_negative_forgot_password")
        t = t + pd.Timedelta(seconds=int(rng.integers(15, 90)),
                             milliseconds=int(rng.integers(1, 999)))
    own(r, t, ip, True, key="hard_negative_forgot_password")

# C3  Bought a new laptop. New device, same country, first try. INNOCENT.
for i, (_, r) in enumerate(dev_users.iterrows()):
    own(r, daytime(rng.integers(3, 7)), jitter_ip(r["IP Address"]), True,
        key="hard_negative_new_device", ua=BROWSER_UA[i % len(BROWSER_UA)])

# ---------------------------------------------------------------- merge
add = pd.DataFrame(new_rows)
base = src[COLS].copy()
out = pd.concat([base, add[COLS]], ignore_index=True)
out["ts"] = pd.to_datetime(out["Login Timestamp"])
out = out.sort_values("ts", kind="mergesort").reset_index(drop=True)
out["index"] = np.arange(1, len(out) + 1)

# Answer key: the five original campaigns, plus every row we just injected.
key = pd.DataFrame(key_rows)
lookup = out.set_index(["Login Timestamp", "Username"])["index"]
key["index"] = [lookup.loc[(t, u)] for t, u in zip(key["Login Timestamp"], key["Username"])]

orig = out[out.Username.isin(CAMPAIGN_ACCOUNTS)].copy()
orig["attack_type"] = np.where(
    orig["Is Account Takeover"], "takeover_success_original",
    np.where(orig["Device Type"] == "bot", "bot_brute_force",
             np.where(orig["Login Successful"], "campaign_account_legit_login",
                      "credential_stuffing")))

answer = pd.concat([
    orig[["index", "Username", "attack_type"]],
    key[["index", "Username", "attack_type"]],
]).sort_values("index")

out[COLS].to_csv(OUT_DATA, index=False)
answer.to_csv(OUT_KEY, index=False)

print(f"{OUT_DATA}: {len(out):,} rows ({len(base):,} original + {len(add):,} added)")
print(f"{OUT_KEY}: {len(answer):,} rows")
print("\nadded rows by kind:")
print(pd.Series([k["attack_type"] for k in key_rows]).value_counts().to_string())
print(f"  (plus {len(add) - len(key_rows):,} ordinary history logins)")
print("\nanswer key by kind:")
print(answer.attack_type.value_counts().to_string())
