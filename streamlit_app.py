# streamlit_app.py
import math
from functools import lru_cache
from itertools import combinations as it_combinations

import streamlit as st

# ---------- Combinatorics core ----------
def nPr(n: int, r: int) -> int:
    if r < 0 or r > n: return 0
    return math.factorial(n) // math.factorial(n - r)

def nCr(n: int, r: int) -> int:
    if r < 0 or r > n: return 0
    return math.factorial(n) // (math.factorial(r) * math.factorial(n - r))

def multiset_permutations_count(counts: dict) -> int:
    total = sum(counts.values())
    denom = 1
    for c in counts.values():
        denom *= math.factorial(c)
    return math.factorial(total) // denom

def inclusion_exclusion(set_sizes: dict, intersections: dict) -> int:
    """
    set_sizes: {'A':a, 'B':b, ...}
    intersections: keys as tuples sorted, e.g. ('A','B'): x, ('A','B','C'): y
    """
    labels = list(set(set_sizes.keys()))
    total = 0

    def inter_size(lbls_tuple):
        key = tuple(sorted(lbls_tuple))
        return intersections.get(key, 0)

    for r in range(1, len(labels)+1):
        sign = 1 if r % 2 == 1 else -1
        for subset in it_combinations(labels, r):
            if r == 1:
                total += sign * set_sizes[subset[0]]
            else:
                total += sign * inter_size(subset)
    return total

def count_with_min_requirements(group_sizes, mins, r):
    m = len(group_sizes)
    if len(mins) != m: raise ValueError("mins length must match group_sizes")
    if sum(mins) > r: return 0
    remaining = r - sum(mins)

    def bounded_compositions(total_rem, bounds):
        if len(bounds) == 1:
            if 0 <= total_rem <= bounds:
                yield (total_rem,)
            return
        b0 = bounds
        for x0 in range(0, min(b0, total_rem) + 1):
            for rest in bounded_compositions(total_rem - x0, bounds[1:]):
                yield (x0,) + rest

    bounds = [group_sizes[i] - mins[i] for i in range(m)]
    total = 0
    for extra in bounded_compositions(remaining, bounds):
        picks = [mins[i] + extra[i] for i in range(m)]
        ways = 1
        for g, e in zip(group_sizes, picks):
            ways *= nCr(g, e)
        total += ways
    return total

def count_with_exact_requirements(group_sizes, exacts):
    if len(group_sizes) != len(exacts): raise ValueError("exacts length mismatch")
    ways = 1
    for g, e in zip(group_sizes, exacts):
        if e < 0 or e > g: return 0
        ways *= nCr(g, e)
    return ways

def count_with_at_most(group_sizes, maxs, r):
    if len(group_sizes) != len(maxs): raise ValueError("maxs length mismatch")
    def bounded_compositions(total_rem, bounds):
        if len(bounds) == 1:
            if 0 <= total_rem <= bounds[0]:
                yield (total_rem,)
            return
        b0 = bounds
        for x0 in range(0, min(b0, total_rem) + 1):
            for rest in bounded_compositions(total_rem - x0, bounds[1:]):
                yield (x0,) + rest
    caps = [min(g, m) for g, m in zip(group_sizes, maxs)]
    total = 0
    for picks in bounded_compositions(r, caps):
        ways = 1
        for g, e in zip(group_sizes, picks):
            ways *= nCr(g, e)
        total += ways
    return total

def arrangements_with_forbidden(n, r, forbidden_pairs):
    from functools import lru_cache
    all_items = tuple(range(n))
    fset = set(tuple(p) for p in forbidden_pairs)

    @lru_cache(maxsize=None)
    def dp(mask, last):
        used_count = mask.bit_count()
        if used_count == r:
            return 1
        total = 0
        for x in all_items:
            bit = 1 << x
            if mask & bit: 
                continue
            if last != -1 and (last, x) in fset:
                continue
            total += dp(mask | bit, x)
        return total

    return dp(0, -1)

def schedule_slots_count(people, slots, max_per_slot, must_include=None):
    n = len(people)
    if must_include is None:
        must_include = []
    # Count distributions of n distinct people across slots with capacity, via multinomial over bounded compositions
    def bounded_compositions(total, parts, cap):
        if parts == 1:
            if 0 <= total <= cap:
                yield (total,)
            return
        for x in range(0, min(total, cap) + 1):
            for rest in bounded_compositions(total - x, parts - 1, cap):
                yield (x,) + rest

    total_count = 0
    for counts in bounded_compositions(n, slots, max_per_slot):
        # handle must_include as fixed placements
        slot_req = [0]*slots
        for _, s in must_include:
            slot_req[s] += 1
        feasible = all(slot_req[i] <= counts[i] for i in range(slots))
        if not feasible:
            continue
        # remaining people to assign after fixing must_include
        m = len(must_include)
        remaining_people = n - m
        remaining_counts = [counts[i] - slot_req[i] for i in range(slots)]
        denom = 1
        for c in remaining_counts:
            denom *= math.factorial(c)
        ways_assign = math.factorial(remaining_people) // denom
        total_count += ways_assign
    return total_count

# ---------- UI helpers ----------
st.set_page_config(
    page_title="Counting Strategies Simulator",
    page_icon="∑",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DARK_CSS = """
<style>
:root {
  --bg: #0b0f14; --panel: #111726; --text: #e6eef7; --muted: #9fb3c8;
  --border: #1f2a3a; --primary: #6ea8fe;
}
html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(1200px 800px at 20% 0%, #162033 0%, var(--bg) 40%), var(--bg) !important;
}
h1, h2, h3, p, label, span, div { color: var(--text); }
.block-container { padding-top: 1.2rem; }
.kpi {
  border: 1px solid var(--border); border-radius: 12px; padding: 10px 12px;
  background: rgba(0,0,0,0.25);
}
pre.code {
  background: rgba(0,0,0,0.22);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px;
  color: var(--text);
  white-space: pre-wrap;
}
hr { border: none; border-top: 1px solid var(--border); margin: 8px 0 12px 0; }
.small { color: var(--muted); font-size: 0.9rem; }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

st.title("Counting Strategies Simulator")
st.caption("Dark UI • Combinatorics engine • Real-world constraints")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Permutations/Combinations",
    "Inclusion–Exclusion",
    "Team Constraints",
    "Forbidden Adjacency",
    "Scheduling"
])

with tab1:
    colA, colB = st.columns([1,1])
    with colA:
        mode = st.selectbox("Mode", ["Permutation (nPr)", "Combination (nCr)"])
        n = st.number_input("n", min_value=0, value=10, step=1)
        r = st.number_input("r", min_value=0, value=3, step=1)
        run = st.button("Compute", type="primary")
    with colB:
        st.write("Formula")
        if mode.startswith("Perm"):
            st.latex(r"{}P_r = \frac{n!}{(n-r)!}")
        else:
            st.latex(r"{}C_r = \frac{n!}{r!(n-r)!}")
    if run:
        if r > n:
            st.error("r cannot exceed n")
        else:
            res = nPr(n, r) if mode.startswith("Perm") else nCr(n, r)
            st.metric("Result", f"{res:,}")
            st.markdown("Details")
            st.code({"mode": "perm" if mode.startswith("Perm") else "comb", "n": n, "r": r, "result": res}, language="json")

with tab2:
    st.write("Enter set sizes and intersections (keys like A,B or A,B,C).")
    col1, col2 = st.columns(2)
    sets_raw = col1.text_area("Set sizes (JSON)", value='{"A":20,"B":25,"C":18}', height=120)
    inters_raw = col2.text_area("Intersections (JSON)", value='{"A,B":8,"A,C":5,"B,C":6,"A,B,C":3}', height=120)
    if st.button("Compute union size", type="primary"):
        try:
            import json
            set_sizes = json.loads(sets_raw or "{}")
            inters_dict = json.loads(inters_raw or "{}")
            # Convert "A,B" to tuple("A","B")
            intersections = {}
            for k, v in inters_dict.items():
                key = tuple(sorted(k.split(",")))
                intersections[key] = int(v)
            res = inclusion_exclusion(set_sizes, intersections)
            st.metric("Union |A ∪ B ∪ ...|", f"{res:,}")
            st.markdown("Details")
            st.code({"set_sizes": set_sizes, "intersections": inters_dict, "result": res}, language="json")
        except Exception as e:
            st.error(f"Parse error: {e}")

with tab3:
    st.write("Compute combinations with group constraints.")
    gs = st.text_input("Group sizes (comma-separated)", "6,5,4")
    r_val = st.number_input("Total r", min_value=0, value=5, step=1)
    c1, c2, c3 = st.columns(3)
    mins_str = c1.text_input("Minimums (optional)", "2,1,0")
    exacts_str = c2.text_input("Exacts (optional)", "")
    maxs_str = c3.text_input("At most (optional)", "")
    colL, colR = st.columns(2)
    run_min = colL.button("Compute Minimums", type="primary")
    run_exact = colR.button("Compute Exacts")
    run_max = st.button("Compute At-most", type="secondary")

    def parse_int_list(s):
        s = s.strip()
        if not s: return []
        return [int(x.strip()) for x in s.split(",") if x.strip()]

    try:
        group_sizes = parse_int_list(gs)
    except:
        group_sizes = []
    if run_min:
        try:
            mins = parse_int_list(mins_str)
            if mins and len(mins) != len(group_sizes):
                st.error("Minimums length must match group sizes")
            else:
                res = count_with_min_requirements(group_sizes, mins or [0]*len(group_sizes), r_val)
                st.metric("Result", f"{res:,}")
                st.code({"group_sizes": group_sizes, "mins": mins or [0]*len(group_sizes), "r": r_val, "result": res}, language="json")
        except Exception as e:
            st.error(str(e))
    if run_exact:
        try:
            exacts = parse_int_list(exacts_str)
            if len(exacts) != len(group_sizes):
                st.error("Exacts length must match group sizes")
            else:
                res = count_with_exact_requirements(group_sizes, exacts)
                st.metric("Result", f"{res:,}")
                st.code({"group_sizes": group_sizes, "exacts": exacts, "result": res}, language="json")
        except Exception as e:
            st.error(str(e))
    if run_max:
        try:
            maxs = parse_int_list(maxs_str)
            if len(maxs) != len(group_sizes):
                st.error("At-most length must match group sizes")
            else:
                res = count_with_at_most(group_sizes, maxs, r_val)
                st.metric("Result", f"{res:,}")
                st.code({"group_sizes": group_sizes, "maxs": maxs, "r": r_val, "result": res}, language="json")
        except Exception as e:
            st.error(str(e))

with tab4:
    st.write("Count r-permutations of n items avoiding forbidden adjacencies.")
    n_f = st.number_input("n (items 0..n-1)", min_value=0, value=6, step=1)
    r_f = st.number_input("r", min_value=0, value=4, step=1)
    pairs_str = st.text_input('Forbidden pairs "a-b,a-b"', "1-2,2-3")
    if st.button("Compute forbidden permutations", type="primary"):
        try:
            pairs = []
            pairs_str = pairs_str.strip()
            if pairs_str:
                for p in pairs_str.split(","):
                    a, b = p.split("-")
                    pairs.append((int(a), int(b)))
            if r_f > n_f:
                st.error("r cannot exceed n")
            else:
                res = arrangements_with_forbidden(n_f, r_f, pairs)
                st.metric("Result", f"{res:,}")
                st.code({"n": n_f, "r": r_f, "forbidden_pairs": pairs, "result": res}, language="json")
        except Exception as e:
            st.error(str(e))

with tab5:
    st.write("Capacity-bounded slot assignments with optional fixed placements (name:slot).")
    ppl = st.text_input("People (comma-separated)", "A,B,C,D,E")
    slots = st.number_input("Slots", min_value=1, value=3, step=1)
    cap = st.number_input("Max per slot", min_value=1, value=2, step=1)
    must = st.text_input('Must include "name:slot,name:slot"', "A:0,C:1")
    if st.button("Compute schedules", type="primary"):
        people = [x.strip() for x in ppl.split(",") if x.strip()]
        must_include = []
        try:
            if must.strip():
                for m in must.split(","):
                    name, s = m.split(":")
                    must_include.append((name.strip(), int(s.strip())))
            res = schedule_slots_count(people, int(slots), int(cap), must_include)
            st.metric("Result", f"{res:,}")
            st.code({"people": people, "slots": int(slots), "max_per_slot": int(cap), "must_include": must_include, "result": res}, language="json")
        except Exception as e:
            st.error(str(e))

st.markdown("<hr/>", unsafe_allow_html=True)
st.caption("Tip: Use small parameters first—counts can grow very large quickly.")
