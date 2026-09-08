#!/usr/bin/env python3
"""
Generator for Day 2 · Lab 3b — Normalization: Put Every Column on the Same Ruler.

The shipped notebook is BUILT FROM THIS SCRIPT and never hand-edited.
To change the lab: edit here, re-run, re-test, then copy the .ipynb to
the Day 2 github_upload/ folder.

    python3 build_3b.py            -> writes Lab3b_Normalization_Homes.ipynb
"""

import json

OUT = "Lab3b_Normalization_Homes.ipynb"

cells = []


def md(text):
    cells.append({"cell_type": "markdown", "metadata": {},
                  "source": text.strip("\n").splitlines(keepends=True)})


def code(text):
    cells.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                  "outputs": [], "source": text.strip("\n").splitlines(keepends=True)})


# ---------------------------------------------------------------- title -----
md(r"""
<a href="https://colab.research.google.com/github/cyberirishman/5-day-AI-Cyber/blob/main/Lab3b_Normalization_Homes.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>


# Day 2 · Lab 3b — Normalization: Put Every Column on the Same Ruler

**AI for Cybersecurity Professionals · Day 2: AI for Defense**

In **Lab 3a** we *cleaned* the house data. Now the data is spotless — but there's still a hidden
problem that can blind a model, and it has nothing to do with dirt. It's about **scale**.

- `bedrooms` runs 1-6
- `age_years` runs 0-100
- `sqft` runs from ~500 to ~3,800

Many models measure how "similar" two houses are using **distance**. When one column is
measured in *thousands* and another in *single digits*, the big-number column drowns out the
others — even if the small-number columns are what really decide the price.

### What we are actually trying to achieve

We are going to **predict the price of a house** from three facts about it: its number of
bedrooms, its floor area, and its age. Then we will measure **how wrong our predictions are, in
dollars**, and we will do that twice:

1. once with the columns left in their **raw** units, and
2. once with the columns **normalized** onto a common 0-1 ruler.

Everything else is held fixed — same data, same model, same houses held back for testing, even
the same random split. **Scaling is the only thing that changes.** So any difference in the
dollar error is caused by scaling and by nothing else. That is the whole design of this lab.

### What you'll do in each step

| Step | What happens |
|---|---|
| **1** | Load the libraries, and meet **KNN** — the distance-based model we will use — and **MinMaxScaler**, the normalizer. |
| **2** | Load the already-clean house data **straight from GitHub** — nothing to upload. |
| **3** | See the scale mismatch: how far each column actually spans. |
| **4** | Hand-work the distance between two houses on **raw** numbers — and watch `sqft` swallow it. |
| **5** | **Normalize** every column to a 0-1 ruler. |
| **6** | Re-do the same distance on **scaled** numbers — now all three features count. |
| **7** | Set up the experiment: split **800 houses to learn from / 200 to be tested on**, and build the same model twice. |
| **8** | Predict **one real house** both ways, and look at which houses each model thought were "similar". |
| **9** | Grade the unscaled model on all **200** test houses. |
| **10** | Grade the scaled model on the **same 200** houses, and compare. |
| **11** | Chart the result two ways: total error, and every prediction against its true price. |

> **Nothing to download or upload.** Open this notebook from its **Open in Colab** badge above
> and the data loads itself from GitHub.

> No prior Python needed — every block of code is explained in the comments (the grey text
> after a `#`).
""")

# --------------------------------------------------------------- step 1 -----
md("## Step 1 — Set up our tools")

code(r'''
# ---- The usual toolboxes ------------------------------------------------------
#   pandas     : tables (a table = a "DataFrame")
#   numpy      : fast maths on numbers
#   matplotlib : draws charts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- The model we will use: k-Nearest-Neighbors, "KNN" ------------------------
#
# WHAT KNN DOES, IN ONE SENTENCE:
#   To put a price on a house it has never seen, KNN looks through the houses it
#   already knows, picks the k that are MOST SIMILAR to it, and averages their prices.
#   That average IS the prediction. There is no formula, no line of best fit --
#   it is "find me five houses like this one and see what they went for".
#
# WE USE k = 5, so every prediction is the average price of 5 known houses.
#
# WHAT "MOST SIMILAR" MEANS:
#   KNN measures similarity as DISTANCE. It subtracts the two houses feature by
#   feature (bedrooms - bedrooms, sqft - sqft, age - age), squares each difference,
#   adds them up, and takes the square root. Small total = similar houses.
#
# WHY THAT MATTERS SO MUCH HERE:
#   Those subtractions happen in whatever units the columns arrive in. A 500 sqft
#   gap produces the number 500; a 2-bedroom gap produces the number 2. Squared,
#   that is 250,000 against 4. So "distance" becomes almost entirely a question of
#   square footage, and bedrooms and age barely register. KNN is not broken --
#   it is faithfully measuring what we gave it. We gave it a bad ruler.
#
#   KNN is deliberately the simplest model that shows this, but the problem is not
#   unique to KNN: any method that measures distance or adds up weighted features
#   (neural networks included) suffers from it.
from sklearn.neighbors import KNeighborsRegressor

# ---- Splitting the data, and grading the result -------------------------------
from sklearn.model_selection import train_test_split   # splits data into train vs. test
from sklearn.metrics import mean_squared_error         # measures how wrong the model is
from sklearn.metrics import mean_absolute_error        # a second, simpler error measure

# ---- The normalizer -----------------------------------------------------------
# MinMaxScaler rewrites every column so its smallest value becomes 0 and its
# largest becomes 1. That is the "same ruler" idea, in one tool.
from sklearn.preprocessing import MinMaxScaler

pd.set_option("display.max_columns", 20)
print("Libraries loaded. Ready to go.")
''')

# --------------------------------------------------------------- step 2 -----
md(r"""
## Step 2 — Load the already-clean data

We reuse `homes_clean.csv` from Lab 3a — read **straight from the internet**, so there is
nothing to upload and no file path to get wrong on Mac, Windows or Linux. There is no cleaning
in this lab, and that is the whole point: cleaning is held constant so scaling is the only
thing that changes.
""")

code(r'''
# ---- Where the data comes from ------------------------------------------------
# Note this is the RAW GitHub address (raw.githubusercontent.com), which returns the
# file itself. A normal github.com link returns a web PAGE and pandas cannot read it.
DATA_URL  = "https://raw.githubusercontent.com/cyberirishman/5-day-AI-Cyber/main/homes_clean.csv"
DATA_FILE = "homes_clean.csv"    # only used by the offline fallbacks below

import os   # lets us ask the computer whether a file exists on disk

# ---- Same loader as Lab 3a: internet first, then local file, then upload box ----
def load_csv(url="", fname=""):
    """Load the CSV from a URL, or a local file, or (on Colab) an upload box."""
    if url:
        try:
            return pd.read_csv(url)
        except Exception as problem:
            print("Could not read from the internet:", problem)
            print("Falling back to a local copy...")
    for path in [fname, os.path.join("data", fname)]:
        if fname and os.path.exists(path):
            return pd.read_csv(path)
    from google.colab import files
    uploaded = files.upload()
    return pd.read_csv(list(uploaded.keys())[0])

# ---- Load it ------------------------------------------------------------------
homes = load_csv(DATA_URL, DATA_FILE)

print("Loaded", len(homes), "clean houses.")
homes.head()    # first 5 rows, so we can see the columns we are about to scale
''')

md(r"""
**What you should see:** `Loaded 1000 clean houses.` and a tidy four-column table with no `$`
signs, no blanks and no silly values — Lab 3a already dealt with all of that.
""")

# --------------------------------------------------------------- step 3 -----
md(r"""
## Step 3 — See the scale mismatch

Look at the min and max of each column. Notice how much bigger `sqft` is than the others.
""")

code(r'''
# ---- How far does each column actually span? -----------------------------------
# .agg(["min", "max"]) applies BOTH of those calculations to each column at once
# and returns a small summary table.
ranges = homes[["bedrooms", "sqft", "age_years"]].agg(["min", "max"])
print(ranges)

# int(...) just chops off the decimal point so the sentence reads cleanly.
print("\nsqft spans about", int(homes["sqft"].max() - homes["sqft"].min()),
      "-- while bedrooms spans only", int(homes["bedrooms"].max() - homes["bedrooms"].min()))
''')

# --------------------------------------------------------------- step 4 -----
md(r"""
## Step 4 — Hand-worked example: distance between two houses (RAW)

Take two houses that differ by **2 bedrooms, 500 sqft, and 10 years**. Distance-based models
square each difference and add them up. Watch what happens.
""")

code(r'''
# ---- Two made-up houses with easy round differences ------------------------------
# The { } braces make a "dictionary": a set of name -> value pairs.
# We invent these two so the arithmetic is easy to follow by hand.
house_A = {"bedrooms": 3, "sqft": 2000, "age_years": 40}
house_B = {"bedrooms": 5, "sqft": 2500, "age_years": 50}

# ---- How different are they, feature by feature? ---------------------------------
d_bed  = house_B["bedrooms"]  - house_A["bedrooms"]     # = 2
d_sqft = house_B["sqft"]      - house_A["sqft"]         # = 500
d_age  = house_B["age_years"] - house_A["age_years"]    # = 10

print("Raw differences:  bedrooms {}, sqft {}, age {}".format(d_bed, d_sqft, d_age))

# ---- Squaring is what distance maths does ----------------------------------------
# ** means "to the power of", so d_bed**2 is d_bed squared.
# Squaring is why a big raw number does not just win -- it wins overwhelmingly.
print("Squared:          bedrooms {}, sqft {}, age {}".format(d_bed**2, d_sqft**2, d_age**2))

total = d_bed**2 + d_sqft**2 + d_age**2
print("sqft accounts for {:.2%} of the total distance".format(d_sqft**2 / total))
''')

md(r"""
`500² = 250,000` utterly dwarfs `2² = 4` and `10² = 100`. Over **99.9%** of the "distance"
comes from `sqft` alone. The model is effectively **blind to bedrooms and age** — even though,
in our data, bedrooms is the *strongest* driver of price. That's the trap.
""")

# --------------------------------------------------------------- step 5 -----
md(r"""
## Step 5 — Normalize: rescale every column to 0-1

**Min-max normalization** rewrites each value as `(value − min) / (max − min)`, so the smallest
value in a column becomes 0 and the largest becomes 1. Let's see the same houses after scaling.
""")

code(r'''
# ---- Teach the scaler what "smallest" and "largest" mean --------------------------
# .fit() looks at the real data and remembers each column's min and max.
# (For this illustration we fit on all the houses. In Step 7, where we actually train
#  a model, we will be stricter about that -- see the golden rule there.)
demo_scaler = MinMaxScaler().fit(homes[["bedrooms", "sqft", "age_years"]])

# ---- Put our two example houses into a small table --------------------------------
rows = pd.DataFrame([house_A, house_B], index=["house_A", "house_B"])

# .transform() applies the (value - min) / (max - min) formula to every value.
# We wrap the result back into a DataFrame so it prints with proper column names.
scaled = pd.DataFrame(demo_scaler.transform(rows), index=rows.index,
                      columns=["bedrooms", "sqft", "age_years"]).round(2)

print("RAW values:\n", rows, "\n")
print("SCALED to 0-1:\n", scaled)
''')

# --------------------------------------------------------------- step 6 -----
md("## Step 6 — Re-do the distance (SCALED)")

code(r'''
# ---- The same subtraction, but on the 0-1 versions ---------------------------------
sd = scaled.loc["house_B"] - scaled.loc["house_A"]   # .loc[name] picks a row by its label
print("Scaled differences:  bedrooms {:.2f}, sqft {:.2f}, age {:.2f}".format(
      sd["bedrooms"], sd["sqft"], sd["age_years"]))

# ---- Square them and see who contributes what --------------------------------------
sq = sd**2            # squares every value at once
total_s = sq.sum()    # add them all up

for f in ["bedrooms", "sqft", "age_years"]:
    print("  {:<9} contributes {:.1%} of the scaled distance".format(f, sq[f] / total_s))
''')

md(r"""
Now all three features have a real say. `bedrooms` — the feature that actually decides
the price — finally counts instead of being buried under `sqft`'s big raw numbers.

So far this is arithmetic on two invented houses. From here on we stop hand-waving and
**make actual price predictions on real houses**, then measure how far off they are.
""")

# --------------------------------------------------------------- step 7 -----
md(r"""
## Step 7 — Set up the experiment: 800 houses to learn from, 200 to be tested on

Before we can say a model is "good" or "bad", we need something to grade it against. The rule
is simple and it is the same rule used everywhere in machine learning:

- **Split the 1,000 clean houses into 800 and 200.**
- The model is only allowed to *learn* from the **800** (the *training set*).
- We then ask it to price the **200** it has never seen (the *test set*), and compare each
  prediction with that house's real price.

Grading a model on houses it memorised would be like marking your own homework — it would look
brilliant and tell us nothing. The 200 held-back houses are the honest exam.

We then build **the same KNN model twice**: once on the raw columns, once on the scaled
columns. Everything else about the two is identical, right down to which 200 houses are held
back. From here on, all we do is examine those two models.

> **Golden rule of scaling:** fit the scaler on the **training** data only, then apply that same
> scaler to the test data. If we fitted it on all 1,000 houses, the scaler would have peeked at
> the exam paper — the test houses would have influenced the min and max — and our score would
> be a lie.
""")

code(r'''
# ---- Inputs and answer ------------------------------------------------------------
X = homes[["bedrooms", "sqft", "age_years"]]   # the FEATURES: what the model gets to see
y = homes["price"]                             # the LABEL: the thing we are predicting

# ---- Hold back 20% of the houses for the exam --------------------------------------
# test_size=0.2 means 20% of 1,000 = 200 houses are held back; the other 800 are for
# learning. random_state=1 fixes WHICH houses are held back, so everyone in the room
# gets exactly the same split and exactly the same numbers.
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=1)

print("Houses the model may learn from (training set):", len(X_tr))
print("Houses held back for the exam   (test set)    :", len(X_te))

# ---- Model 1: trained on the RAW columns -------------------------------------------
# n_neighbors=5 -> to price a house, find the 5 most similar houses and average them.
knn_raw = KNeighborsRegressor(n_neighbors=5).fit(X_tr, y_tr)

# ---- Model 2: the SAME model, trained on SCALED columns ------------------------------
# The golden rule in code: .fit() the scaler on the TRAINING data only...
scaler = MinMaxScaler().fit(X_tr)
X_tr_s = scaler.transform(X_tr)   # ...then apply that scaling to the training houses...
X_te_s = scaler.transform(X_te)   # ...and the SAME scaling to the test houses.

knn_scaled = KNeighborsRegressor(n_neighbors=5).fit(X_tr_s, y_tr)

print("\nTwo models built. Identical settings, identical houses.")
print("The ONLY difference: model 2 saw the columns on a common 0-1 ruler.")
''')

# --------------------------------------------------------------- step 8 -----
md(r"""
## Step 8 — Predict one real house, both ways

Averages of 200 houses are easy to nod along to and hard to feel. So before we grade anything,
let's watch **one** house go through both models and look at *which houses each model decided
were "similar"*. This is where the whole lab clicks.

We pick a house out of the 200 held-back ones, ask each model for a price, and then — because
KNN has nothing to hide — print the actual five neighbours each model averaged to get there.
""")

code(r'''
# ---- Pick one house out of the 200 held back -----------------------------------------
# Position 198 in the test set. Any house would do; this one shows the effect clearly.
# .iloc[[198]] takes row number 198 and keeps it as a one-row TABLE (the double brackets),
# because the model expects a table, not a single row.
example_pos  = 198
example_X    = X_te.iloc[[example_pos]]
example_true = y_te.iloc[example_pos]

print("THE HOUSE WE ARE PRICING")
print(example_X.to_string(index=False))
print("Its real selling price: ${:,.0f}".format(example_true))

# ---- Ask both models for a price -------------------------------------------------------
pred_raw_one    = knn_raw.predict(example_X)[0]
pred_scaled_one = knn_scaled.predict(scaler.transform(example_X))[0]

# ---- A small helper so we can print each model's five neighbours ------------------------
# .kneighbors() hands back the row numbers of the k training houses it judged closest.
def show_neighbours(title, neighbour_rows, prediction):
    table = X_tr.iloc[neighbour_rows].copy()   # the 5 neighbour houses...
    table["price"] = y_tr.iloc[neighbour_rows] # ...with the prices it averaged
    print("\n" + title)
    print(table.to_string(index=False))
    print("  -> average of those 5 prices = PREDICTION ${:,.0f}".format(prediction))
    print("  -> the real price was          ${:,.0f}   (off by ${:,.0f})".format(
          example_true, abs(prediction - example_true)))

_, rows_raw    = knn_raw.kneighbors(example_X)
_, rows_scaled = knn_scaled.kneighbors(scaler.transform(example_X))

show_neighbours("WITHOUT SCALING, the 5 houses it called 'most similar':",
                rows_raw[0], pred_raw_one)
show_neighbours("WITH SCALING, the 5 houses it called 'most similar':",
                rows_scaled[0], pred_scaled_one)
''')

md(r"""
**Read the two tables side by side — this is the point of the entire lab.**

The unscaled model chose five houses whose **square footage** is within a few feet of our
house's. Look at their **bedroom** counts: they are the wrong size of house entirely. It priced
a 4-bedroom home by averaging five 3-bedroom homes, purely because the floor areas matched —
exactly as Step 4 predicted, since sqft was ~99.96% of the distance.

The scaled model chose five houses that match on **all three** features, and its price lands
close.

Nothing about the model changed. It picked **different neighbours**, because "similar" was
measured with a fairer ruler. That is what normalization buys you — and it is why the error
falls in the next two steps.
""")

# --------------------------------------------------------------- step 9 -----
md(r"""
## Step 9 — Grade the unscaled model on all 200 test houses

One house could be luck. Now we make a prediction for **every one of the 200** held-back
houses, and summarise how far off we were.

**How the error is measured — read this once, carefully.** We have 200 predictions and 200 real
prices, so we have 200 errors in dollars. We report them two ways:

- **MAE** (mean absolute error) — exactly what it sounds like: take the size of each of the 200
  errors and average them. "On a typical house we were $X out."
- **RMSE** (root mean squared error) — **not** a plain average. It *squares* each of the 200
  errors, averages the squares, then takes the square root to get back into dollars. Squaring
  makes a $60,000 miss count far more than four $15,000 misses, so **RMSE is always the larger
  of the two**, and it rises fast when a model gets a few houses badly wrong.

RMSE is the number quoted on the slide, because for a price model the occasional catastrophic
miss is exactly what we care about. Both are in dollars, and for both, **lower is better**.
""")

code(r'''
# ---- One prediction for each of the 200 test houses ------------------------------------
pred_raw = knn_raw.predict(X_te)

# ---- Turn 200 errors into one number, two different ways --------------------------------
mae_raw = mean_absolute_error(y_te, pred_raw)          # average size of the misses

# mean_squared_error averages the SQUARED errors; ** 0.5 is a square root, which brings
# the number back into dollars. That two-step is what makes it "root mean squared".
rmse_raw = mean_squared_error(y_te, pred_raw) ** 0.5

print("Predictions made:", len(pred_raw))
print("UNSCALED KNN  MAE  (plain average miss) : ${:,.0f}".format(mae_raw))
print("UNSCALED KNN  RMSE (big misses weighted): ${:,.0f}".format(rmse_raw))
print("\nFor scale, the average house here costs ${:,.0f},".format(y.mean()))
print("so an RMSE of ${:,.0f} is about {:.0%} of a typical house price.".format(
      rmse_raw, rmse_raw / y.mean()))
''')

# -------------------------------------------------------------- step 10 -----
md(r"""
## Step 10 — The same model **with** scaling, on the same 200 houses

Same 800 training houses, same 200 test houses, same `n_neighbors=5`, same random split.
The columns are on a 0-1 ruler. That is the only difference.
""")

code(r'''
# ---- Predict the same 200 houses, using the scaled model --------------------------------
pred_scaled = knn_scaled.predict(X_te_s)

mae_scaled  = mean_absolute_error(y_te, pred_scaled)
rmse_scaled = mean_squared_error(y_te, pred_scaled) ** 0.5

print("                        UNSCALED        SCALED")
print("MAE  (plain average) : ${:>9,.0f}    ${:>9,.0f}".format(mae_raw, mae_scaled))
print("RMSE (slide figure)  : ${:>9,.0f}    ${:>9,.0f}".format(rmse_raw, rmse_scaled))
print("\nScaling cut the typical error by {:.0%} -- and NOTHING else changed.".format(
      1 - rmse_scaled / rmse_raw))

# ---- Two more ways of saying the same thing ----------------------------------------------
# 1) On how many of the 200 houses was the scaled model the closer of the two?
closer = (abs(pred_scaled - y_te) < abs(pred_raw - y_te)).mean()
print("\nThe scaled model was the closer of the two on {:.1%} of the 200 test houses.".format(closer))

# 2) WHY it is closer: the 5 neighbours it averages are a much more consistent set of houses.
#    .std() measures spread -- how much the five prices disagree with each other. If the five
#    "similar" houses disagree wildly about price, the average of them is a shaky prediction.
def neighbour_price_spread(model, features):
    _, rows = model.kneighbors(features)        # the 5 chosen neighbours for every test house
    return y_tr.values[rows].std(axis=1).mean() # spread within each set, averaged over all 200

print("Average disagreement among the 5 chosen neighbours' prices:")
print("   unscaled: ${:,.0f}".format(neighbour_price_spread(knn_raw, X_te)))
print("   scaled  : ${:,.0f}".format(neighbour_price_spread(knn_scaled, X_te_s)))
''')

md(r"""
**What you should see:** about **$27,600** unscaled against about **$16,300** scaled — roughly a
**41% cut in typical error**. Same model, same houses, same split. The *only* difference is
which ruler the columns were measured on.

The last figure is the mechanism in one line: unscaled, the five "similar" houses disagree with
each other by about **$23,000** on price — because they were never really similar, they merely
shared a floor area. Scaled, that disagreement roughly halves. **A prediction is only as steady
as the neighbours it averages.**
""")

# -------------------------------------------------------------- step 11 -----
md(r"""
## Step 11 — See it: two pictures

The left chart is the headline number. The right pair is more honest about what a "prediction"
actually is: every one of the 200 test houses is a dot — its true price along the bottom, our
predicted price up the side. **The dashed line is perfection**, where predicted equals true. The
closer the cloud hugs that line, the better the model.
""")

code(r'''
# ---- Picture 1: the two error bars ----------------------------------------------------
fig, ax = plt.subplots(figsize=(5, 4))

# .bar() takes the labels for the bars and their heights.
bars = ax.bar(["Unscaled", "Scaled"], [rmse_raw, rmse_scaled],
              color=["#C0392B", "#1E5199"])

ax.set_ylabel("Test RMSE  (typical $ error)")
ax.set_title("Same KNN model - scaling is the only change")

# ---- Print the actual dollar figure on top of each bar --------------------------------
# zip() walks through both lists together, one bar and one value at a time.
for b, v in zip(bars, [rmse_raw, rmse_scaled]):
    ax.text(b.get_x() + b.get_width()/2, v, "${:,.0f}".format(v),
            ha="center", va="bottom")

plt.tight_layout()
plt.show()


# ---- Picture 2: every prediction against its true price --------------------------------
# One panel per model, sharing the same axes so they can be compared fairly.
fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), sharex=True, sharey=True)

lo, hi = y_te.min(), y_te.max()     # the range of real prices, for the perfection line

for ax, preds, name, rmse, colour in [
        (axes[0], pred_raw,    "UNSCALED", rmse_raw,    "#C0392B"),
        (axes[1], pred_scaled, "SCALED",   rmse_scaled, "#1E5199")]:
    # Each dot is one test house: true price across, our prediction up.
    ax.scatter(y_te, preds, s=14, alpha=0.55, color=colour, edgecolor="none")
    # The dashed 45-degree line: where a perfect prediction would land.
    ax.plot([lo, hi], [lo, hi], "k--", linewidth=1, label="perfect prediction")
    ax.set_title("{}  -  RMSE ${:,.0f}".format(name, rmse))
    ax.set_xlabel("True price ($)")
    ax.legend(loc="upper left", fontsize=8)

axes[0].set_ylabel("Predicted price ($)")
plt.tight_layout()
plt.show()
''')

md(r"""
On the left the cloud is wide and woolly — plenty of houses are priced $50,000 or more away from
what they really sold for, in both directions, because the unscaled model grouped them by floor
area alone. On the right the same 200 dots pull in tight around the dashed line.

Same model. Same houses. Different ruler.
""")

# ------------------------------------------------------------- wrap-up ------
md(r"""
## Wrap-up

- The house data was already clean, yet an **unscaled** distance model still did badly —
  because `sqft`'s big raw numbers drowned out the features that actually set the price.
- The mechanism is concrete, not magic: unscaled, KNN **chose the wrong "similar" houses**
  (Step 8), so it averaged the wrong prices.
- **Normalization** (min-max to 0-1) put every column on the same ruler, and the *same* model's
  error dropped sharply — about **41%** on the 200 held-back houses.
- **RMSE** is the typical dollars we were off across the test set, with big misses weighted
  more heavily than small ones. Lower is better; it is not a percentage and it is not a grade.
- **This is why neural networks need scaled inputs too** — the same "big-number features
  dominate" effect shows up there. We'll see a neural net next (§2.8.4).
- **Rule of thumb:** always fit your scaler on training data only, then reuse it on test/live
  data.
""")

# ------------------------------------------------------------------ write ---
nb = {
    "cells": cells,
    "metadata": {
        "colab": {"provenance": []},
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 0,
}

with open(OUT, "w") as fh:
    json.dump(nb, fh, indent=1)
    fh.write("\n")

print("Wrote {} — {} cells ({} code, {} markdown).".format(
    OUT, len(cells),
    sum(1 for c in cells if c["cell_type"] == "code"),
    sum(1 for c in cells if c["cell_type"] == "markdown")))
