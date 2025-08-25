# streamlit_app.py
import math
from functools import lru_cache
from itertools import combinations as it_combinations
import streamlit as st
import time

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
            if 0 <= total_rem <= bounds[0]:
                yield (total_rem,)
            return
        b0 = bounds[0]
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
        b0 = bounds[0]
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
        slot_req = [0]*slots
        for _, s in must_include:
            slot_req[s] += 1
        feasible = all(slot_req[i] <= counts[i] for i in range(slots))
        if not feasible:
            continue
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
    page_title="✨ Combinatorics Engine Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Fixed CSS with proper scrolling
SCROLLABLE_PROFESSIONAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --accent: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    --success: linear-gradient(135deg, #81ff8a 0%, #6dd5ed 100%);
    --warning: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    --danger: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
    --dark: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    --light: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    --glass: rgba(255, 255, 255, 0.08);
    --glass-border: rgba(255, 255, 255, 0.2);
    --shadow-soft: 0 10px 40px -10px rgba(0, 0, 0, 0.1);
    --shadow-hard: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    --shadow-glow: 0 0 30px rgba(102, 126, 234, 0.3);
    --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    --border-radius: 16px;
    --transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* Global resets and base styles - FIXED for scrolling */
html, body {
    height: auto !important;
    min-height: 100vh;
    overflow-x: hidden;
    overflow-y: auto !important;
}

.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    font-family: var(--font-primary);
    position: relative;
}

/* Fixed background animation - doesn't interfere with scrolling */
.stApp::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 20%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
    pointer-events: none;
    z-index: -2;
    animation: backgroundShift 20s ease-in-out infinite;
}

@keyframes backgroundShift {
    0%, 100% { 
        background: 
            radial-gradient(circle at 20% 20%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
    }
    33% { 
        background: 
            radial-gradient(circle at 80% 30%, rgba(120, 119, 198, 0.4) 0%, transparent 50%),
            radial-gradient(circle at 20% 70%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 60% 60%, rgba(120, 219, 255, 0.3) 0%, transparent 50%);
    }
    66% { 
        background: 
            radial-gradient(circle at 40% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 70% 20%, rgba(255, 119, 198, 0.4) 0%, transparent 50%),
            radial-gradient(circle at 30% 50%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
    }
}

/* Enhanced typography */
h1, h2, h3, h4, h5, h6 {
    background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin-bottom: 1rem;
    animation: textGlow 2s ease-in-out infinite alternate;
}

@keyframes textGlow {
    0% { filter: drop-shadow(0 0 5px rgba(255, 255, 255, 0.3)); }
    100% { filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.6)); }
}

/* Glass morphism container - FIXED overflow */
.block-container {
    background: var(--glass);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-soft);
    padding: 2rem;
    margin: 2rem auto;
    max-width: none;
    animation: containerFloat 6s ease-in-out infinite;
    position: relative;
    overflow: visible !important;
}

.block-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    animation: shimmer 3s ease-in-out infinite;
    pointer-events: none;
}

@keyframes containerFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-5px); }
}

@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

/* Enhanced tabs */
[data-testid="stTabs"] {
    background: var(--glass);
    backdrop-filter: blur(15px);
    border-radius: var(--border-radius);
    padding: 0.5rem;
    box-shadow: var(--shadow-soft);
    margin-bottom: 2rem;
    border: 1px solid var(--glass-border);
}

[data-testid="stTabs"] [role="tablist"] {
    gap: 0.5rem;
}

[data-testid="stTabs"] button {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 12px !important;
    color: rgba(255, 255, 255, 0.7) !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    transition: var(--transition-bounce) !important;
    position: relative !important;
    overflow: hidden !important;
    font-size: 0.95rem !important;
}

[data-testid="stTabs"] button::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--primary);
    opacity: 0;
    transition: var(--transition);
    border-radius: 12px;
    z-index: -1;
}

[data-testid="stTabs"] button:hover {
    color: white !important;
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: var(--shadow-glow) !important;
}

[data-testid="stTabs"] button:hover::before {
    opacity: 0.8;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: white !important;
    background: var(--primary) !important;
    transform: translateY(-3px) scale(1.05) !important;
    box-shadow: var(--shadow-glow) !important;
}

[data-testid="stTabs"] button[aria-selected="true"]::before {
    opacity: 1;
}

/* Ultra-enhanced buttons */
.stButton > button {
    background: var(--primary) !important;
    border: none !important;
    border-radius: var(--border-radius) !important;
    color: white !important;
    font-weight: 700 !important;
    padding: 16px 32px !important;
    transition: var(--transition-bounce) !important;
    box-shadow: var(--shadow-soft) !important;
    position: relative !important;
    overflow: hidden !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    font-size: 0.9rem !important;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
    transition: var(--transition);
    border-radius: 50%;
    transform: translate(-50%, -50%);
}

.stButton > button:hover {
    transform: translateY(-4px) scale(1.05) !important;
    box-shadow: var(--shadow-hard) !important;
    background: var(--secondary) !important;
}

.stButton > button:hover::before {
    width: 300px;
    height: 300px;
}

.stButton > button:active {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: var(--shadow-soft) !important;
}

/* Enhanced metrics */
[data-testid="stMetric"] {
    background: var(--glass) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--border-radius) !important;
    padding: 2rem !important;
    box-shadow: var(--shadow-soft) !important;
    transition: var(--transition-bounce) !important;
    position: relative !important;
    overflow: hidden !important;
    text-align: center !important;
    animation: metricPulse 3s ease-in-out infinite !important;
}

[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--accent);
    opacity: 0;
    transition: var(--transition);
    border-radius: var(--border-radius);
    z-index: -1;
}

@keyframes metricPulse {
    0%, 100% { box-shadow: var(--shadow-soft), 0 0 0 0 rgba(102, 126, 234, 0.4); }
    50% { box-shadow: var(--shadow-hard), 0 0 0 10px rgba(102, 126, 234, 0); }
}

[data-testid="stMetric"]:hover {
    transform: translateY(-8px) scale(1.03) !important;
    box-shadow: var(--shadow-hard) !important;
}

[data-testid="stMetric"]:hover::before {
    opacity: 0.1;
}

[data-testid="stMetric"] label {
    color: rgba(255, 255, 255, 0.8) !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 1rem !important;
}

[data-testid="stMetric"] [data-testid="metric-container"] > div {
    color: white !important;
    font-size: 3rem !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    animation: numberCount 1s ease-out !important;
}

@keyframes numberCount {
    0% { transform: scale(0.5) rotate(-5deg); opacity: 0; }
    100% { transform: scale(1) rotate(0deg); opacity: 1; }
}

/* Enhanced input fields */
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: white !important;
    padding: 12px 16px !important;
    font-weight: 500 !important;
    transition: var(--transition) !important;
    backdrop-filter: blur(10px) !important;
}

.stNumberInput > div > div > input:focus,
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > select:focus {
    border-color: rgba(102, 126, 234, 0.8) !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    transform: translateY(-2px) !important;
}

/* Enhanced labels */
.stNumberInput > label,
.stTextInput > label,
.stTextArea > label,
.stSelectbox > label {
    color: rgba(255, 255, 255, 0.9) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 0.5rem !important;
}

/* Code blocks */
.stCode {
    background: rgba(0, 0, 0, 0.3) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px) !important;
    font-family: var(--font-mono) !important;
    animation: codeSlideIn 0.5s ease-out !important;
}

@keyframes codeSlideIn {
    0% { transform: translateX(-20px); opacity: 0; }
    100% { transform: translateX(0); opacity: 1; }
}

/* Columns enhancement */
.stColumn {
    padding: 1rem !important;
}

.stColumn > div {
    background: var(--glass);
    border-radius: 12px;
    border: 1px solid var(--glass-border);
    padding: 1.5rem;
    backdrop-filter: blur(15px);
    transition: var(--transition);
    height: 100%;
}

.stColumn > div:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-soft);
}

/* LaTeX styling */
.katex {
    color: rgba(255, 255, 255, 0.9) !important;
    font-size: 1.2rem !important;
    background: var(--glass) !important;
    padding: 1rem !important;
    border-radius: 12px !important;
    border: 1px solid var(--glass-border) !important;
    backdrop-filter: blur(10px) !important;
    text-align: center !important;
    animation: formulaGlow 2s ease-in-out infinite alternate !important;
}

@keyframes formulaGlow {
    0% { box-shadow: 0 0 10px rgba(102, 126, 234, 0.3); }
    100% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.6); }
}

/* Error and warning states */
.stAlert {
    border-radius: 12px !important;
    border: none !important;
    backdrop-filter: blur(15px) !important;
    animation: alertSlideIn 0.5s ease-out !important;
}

@keyframes alertSlideIn {
    0% { transform: translateY(-20px); opacity: 0; }
    100% { transform: translateY(0); opacity: 1; }
}

.stAlert[data-baseweb-tag="alert"][kind="error"] {
    background: var(--danger) !important;
}

.stAlert[data-baseweb-tag="alert"][kind="success"] {
    background: var(--success) !important;
}

/* Loading animation */
.stSpinner {
    animation: spinnerGlow 1.5s ease-in-out infinite !important;
}

@keyframes spinnerGlow {
    0%, 100% { filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.5)); }
    50% { filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.8)); }
}

/* FIXED: Scrollbar styling */
::-webkit-scrollbar {
    width: 12px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 6px;
}

::-webkit-scrollbar-thumb {
    background: var(--primary);
    border-radius: 6px;
    transition: var(--transition);
    border: 2px solid transparent;
    background-clip: content-box;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--secondary);
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
}

/* Responsive design */
@media (max-width: 768px) {
    .block-container {
        margin: 1rem;
        padding: 1rem;
    }
    
    h1 {
        font-size: 2rem !important;
    }
    
    [data-testid="stMetric"] [data-testid="metric-container"] > div {
        font-size: 2rem !important;
    }
}

/* FIXED: Final entrance animation - doesn't affect scrolling */
.main {
    animation: pageEnter 1s ease-out;
}

@keyframes pageEnter {
    0% { 
        opacity: 0; 
        transform: translateY(30px) scale(0.95);
        filter: blur(5px);
    }
    100% { 
        opacity: 1; 
        transform: translateY(0) scale(1);
        filter: blur(0px);
    }
}
</style>
"""

st.markdown(SCROLLABLE_PROFESSIONAL_CSS, unsafe_allow_html=True)

# Animated title with typing effect
title_placeholder = st.empty()
title_text = "✨ Combinatorics Engine Pro"
for i in range(len(title_text) + 1):
    title_placeholder.title(title_text[:i] + "█")
    time.sleep(0.05)  # Reduced delay
title_placeholder.title(title_text)

# Animated subtitle
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <p style='font-size: 1.5rem; color: rgba(255, 255, 255, 0.8); font-weight: 300; animation: fadeInUp 1s ease-out 0.5s both;'>
        Advanced Mathematical Computing Platform
    </p>
    <div style='width: 100px; height: 4px; background: linear-gradient(90deg, #667eea, #764ba2); margin: 1rem auto; border-radius: 2px; animation: expandWidth 1s ease-out 1s both;'></div>
</div>

<style>
@keyframes fadeInUp {
    0% { opacity: 0; transform: translateY(30px); }
    100% { opacity: 1; transform: translateY(0); }
}

@keyframes expandWidth {
    0% { width: 0; }
    100% { width: 100px; }
}
</style>
""", unsafe_allow_html=True)

# Enhanced tabs with icons
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Permutations & Combinations",
    "🔄 Inclusion–Exclusion",
    "👥 Team Constraints",
    "🚫 Forbidden Adjacency",
    "📅 Smart Scheduling"
])

with tab1:
    st.markdown("### 🎯 Basic Combinatorics Calculator")
    
    colA, colB = st.columns([3, 2])
    
    with colA:
        with st.container():
            st.markdown("**Configuration**")
            mode = st.selectbox(
                "Calculation Mode", 
                ["🔢 Permutation (nPr)", "🎲 Combination (nCr)"],
                help="Choose between permutations (order matters) or combinations (order doesn't matter)"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                n = st.number_input("Total items (n)", min_value=0, value=10, step=1, help="Total number of items to choose from")
            with col2:
                r = st.number_input("Items to select (r)", min_value=0, value=3, step=1, help="Number of items to select")
            
            run = st.button("🚀 Calculate", type="primary")
    
    with colB:
        st.markdown("**Formula Reference**")
        if mode.startswith("🔢"):
            st.latex(r"P(n,r) = \frac{n!}{(n-r)!}")
            st.markdown("*Permutations: Order matters*")
        else:
            st.latex(r"C(n,r) = \frac{n!}{r!(n-r)!}")
            st.markdown("*Combinations: Order doesn't matter*")
    
    if run:
        if r > n:
            st.error("❌ Error: r cannot exceed n")
        else:
            with st.spinner("🔄 Computing..."):
                time.sleep(0.5)  # Small delay for effect
                res = nPr(n, r) if mode.startswith("🔢") else nCr(n, r)
                
            col1, col2, col3 = st.columns(3)
            with col2:
                st.metric("🎯 Result", f"{res:,}")
            
            st.markdown("---")
            st.markdown("**📊 Calculation Details**")
            st.code({
                "mode": "permutation" if mode.startswith("🔢") else "combination", 
                "n": n, 
                "r": r, 
                "result": res,
                "formula": f"{n}P{r}" if mode.startswith("🔢") else f"{n}C{r}"
            }, language="json")

with tab2:
    st.markdown("### 🔄 Inclusion-Exclusion Principle")
    st.markdown("*Calculate the size of union of multiple sets*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Set Sizes**")
        sets_raw = st.text_area(
            "Define your sets (JSON format)",
            value='{"A":20,"B":25,"C":18}',
            height=120,
            help="Define the size of each individual set"
        )
    
    with col2:
        st.markdown("**🔗 Intersections**")
        inters_raw = st.text_area(
            "Set intersections (JSON format)",
            value='{"A,B":8,"A,C":5,"B,C":6,"A,B,C":3}',
            height=120,
            help="Define the sizes of intersections between sets"
        )
    
    if st.button("🧮 Calculate Union Size", type="primary"):
        try:
            with st.spinner("🔄 Processing sets..."):
                import json
                time.sleep(0.3)
                
                set_sizes = json.loads(sets_raw or "{}")
                inters_dict = json.loads(inters_raw or "{}")
                
                intersections = {}
                for k, v in inters_dict.items():
                    key = tuple(sorted(k.split(",")))
                    intersections[key] = int(v)
                
                res = inclusion_exclusion(set_sizes, intersections)
            
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.metric("🎯 Union |A ∪ B ∪ ...|", f"{res:,}")
            
            st.markdown("---")
            st.markdown("**📊 Detailed Analysis**")
            st.code({
                "set_sizes": set_sizes,
                "intersections": inters_dict,
                "union_size": res,
                "principle": "Inclusion-Exclusion"
            }, language="json")
            
        except Exception as e:
            st.error(f"❌ Parse error: {e}")

with tab3:
    st.markdown("### 👥 Advanced Team Constraints")
    st.markdown("*Solve complex selection problems with group requirements*")
    
    # Input section
    col1, col2 = st.columns([2, 1])
    with col1:
        gs = st.text_input(
            "🏢 Group sizes (comma-separated)",
            "6,5,4",
            help="Size of each group to select from"
        )
    with col2:
        r_val = st.number_input("🎯 Total selections", min_value=0, value=5, step=1)
    
    # Constraint options
    st.markdown("**🎛️ Constraint Types**")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        mins_str = st.text_input(
            "🔽 Minimum from each group",
            "2,1,0",
            help="Minimum selections required from each group"
        )
        run_min = st.button("📊 Compute Minimums", type="primary")
    
    with c2:
        exacts_str = st.text_input(
            "🎯 Exact from each group",
            "",
            help="Exact selections required from each group"
        )
        run_exact = st.button("🎲 Compute Exacts")
    
    with c3:
        maxs_str = st.text_input(
            "🔼 Maximum from each group",
            "",
            help="Maximum selections allowed from each group"
        )
        run_max = st.button("📈 Compute At-most", type="secondary")

    def parse_int_list(s):
        s = s.strip()
        if not s: return []
        return [int(x.strip()) for x in s.split(",") if x.strip()]

    try:
        group_sizes = parse_int_list(gs)
    except:
        group_sizes = []

    if run_min and group_sizes:
        try:
            with st.spinner("🔄 Calculating minimum constraints..."):
                time.sleep(0.4)
                mins = parse_int_list(mins_str)
                if mins and len(mins) != len(group_sizes):
                    st.error("❌ Minimums length must match group sizes")
                else:
                    res = count_with_min_requirements(group_sizes, mins or [0]*len(group_sizes), r_val)
                    
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        st.metric("🎯 Valid Combinations", f"{res:,}")
                    
                    st.code({
                        "group_sizes": group_sizes,
                        "minimums": mins or [0]*len(group_sizes),
                        "total_selections": r_val,
                        "result": res,
                        "constraint_type": "minimum"
                    }, language="json")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    if run_exact and group_sizes:
        try:
            with st.spinner("🔄 Calculating exact constraints..."):
                time.sleep(0.4)
                exacts = parse_int_list(exacts_str)
                if len(exacts) != len(group_sizes):
                    st.error("❌ Exacts length must match group sizes")
                else:
                    res = count_with_exact_requirements(group_sizes, exacts)
                    
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        st.metric("🎯 Valid Combinations", f"{res:,}")
                    
                    st.code({
                        "group_sizes": group_sizes,
                        "exact_requirements": exacts,
                        "result": res,
                        "constraint_type": "exact"
                    }, language="json")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    if run_max and group_sizes:
        try:
            with st.spinner("🔄 Calculating maximum constraints..."):
                time.sleep(0.4)
                maxs = parse_int_list(maxs_str)
                if len(maxs) != len(group_sizes):
                    st.error("❌ At-most length must match group sizes")
                else:
                    res = count_with_at_most(group_sizes, maxs, r_val)
                    
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        st.metric("🎯 Valid Combinations", f"{res:,}")
                    
                    st.code({
                        "group_sizes": group_sizes,
                        "maximums": maxs,
                        "total_selections": r_val,
                        "result": res,
                        "constraint_type": "maximum"
                    }, language="json")
        except Exception as e:
            st.error(f"❌ Error: {e}")

with tab4:
    st.markdown("### 🚫 Forbidden Adjacency Analysis")
    st.markdown("*Count arrangements avoiding specific adjacency patterns*")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("**⚙️ Configuration**")
        n_f = st.number_input("🔢 Total items (0 to n-1)", min_value=0, value=6, step=1)
        r_f = st.number_input("📝 Arrangement length", min_value=0, value=4, step=1)
        pairs_str = st.text_input(
            '🚫 Forbidden pairs (format: "a-b,c-d")',
            "1-2,2-3",
            help="Items that cannot be adjacent in arrangements"
        )
    
    with col2:
        st.markdown("**📋 Example**")
        st.info("""
        **Items**: 0, 1, 2, 3, 4, 5  
        **Length**: 4  
        **Forbidden**: 1-2, 2-3  
        
        ✅ Valid: [0,1,3,4]  
        ❌ Invalid: [1,2,0,3] (1-2 adjacent)
        """)
    
    if st.button("🔍 Analyze Arrangements", type="primary"):
        try:
            with st.spinner("🔄 Computing valid arrangements..."):
                time.sleep(0.5)
                pairs = []
                pairs_str = pairs_str.strip()
                if pairs_str:
                    for p in pairs_str.split(","):
                        a, b = p.split("-")
                        pairs.append((int(a), int(b)))
                
                if r_f > n_f:
                    st.error("❌ Arrangement length cannot exceed total items")
                else:
                    res = arrangements_with_forbidden(n_f, r_f, pairs)
                    
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        st.metric("🎯 Valid Arrangements", f"{res:,}")
                    
                    # Calculate percentage if total arrangements > 0
                    total_arrangements = nPr(n_f, r_f) if r_f <= n_f else 0
                    if total_arrangements > 0:
                        percentage = (res / total_arrangements) * 100
                        st.markdown(f"**📊 {percentage:.1f}% of all possible arrangements are valid**")
                    
                    st.markdown("---")
                    st.code({
                        "total_items": n_f,
                        "arrangement_length": r_f,
                        "forbidden_pairs": pairs,
                        "valid_arrangements": res,
                        "total_possible": total_arrangements,
                        "success_rate": f"{percentage:.2f}%" if total_arrangements > 0 else "N/A"
                    }, language="json")
        except Exception as e:
            st.error(f"❌ Error: {e}")

with tab5:
    st.markdown("### 📅 Smart Scheduling System")
    st.markdown("*Optimize resource allocation with capacity constraints*")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ppl = st.text_input(
            "👥 People/Resources",
            "Alice,Bob,Charlie,David,Eve",
            help="Comma-separated list of people or resources"
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            slots = st.number_input("🕐 Available slots", min_value=1, value=3, step=1)
        with col_b:
            cap = st.number_input("👤 Max per slot", min_value=1, value=2, step=1)
    
    with col2:
        st.markdown("**🔧 Advanced Options**")
        must = st.text_input(
            '📌 Fixed assignments',
            "Alice:0,Charlie:1",
            help='Format: "name:slot,name:slot"'
        )
    
    st.markdown("**📊 Visual Representation**")
    people_list = [x.strip() for x in ppl.split(",") if x.strip()]
    
    # Create a visual representation of slots
    slot_cols = st.columns(int(slots))
    for i in range(int(slots)):
        with slot_cols[i]:
            st.markdown(f"**🕐 Slot {i}**")
            st.markdown(f"Capacity: {cap} people")
    
    if st.button("🚀 Generate Schedules", type="primary"):
        try:
            with st.spinner("🔄 Optimizing schedules..."):
                time.sleep(0.6)
                people = people_list
                must_include = []
                
                if must.strip():
                    for m in must.split(","):
                        if ":" in m:
                            name, s = m.split(":")
                            must_include.append((name.strip(), int(s.strip())))
                
                res = schedule_slots_count(people, int(slots), int(cap), must_include)
                
                col1, col2, col3 = st.columns([1,2,1])
                with col2:
                    st.metric("🎯 Possible Schedules", f"{res:,}")
                
                # Additional insights
                st.markdown("---")
                st.markdown("**🔍 Schedule Analysis**")
                
                total_capacity = int(slots) * int(cap)
                utilization = (len(people) / total_capacity) * 100 if total_capacity > 0 else 0
                
                insight_cols = st.columns(3)
                with insight_cols[0]:
                    st.metric("👥 Total People", len(people))
                with insight_cols[1]:
                    st.metric("🏢 Total Capacity", total_capacity)
                with insight_cols[2]:
                    st.metric("📊 Utilization", f"{utilization:.1f}%")
                
                st.code({
                    "people": people,
                    "slots": int(slots),
                    "max_per_slot": int(cap),
                    "fixed_assignments": must_include,
                    "possible_schedules": res,
                    "utilization_rate": f"{utilization:.2f}%"
                }, language="json")
                
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Enhanced footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; color: rgba(255, 255, 255, 0.6);'>
    <p style='font-size: 0.9rem; margin-bottom: 1rem;'>
        ✨ <strong>Pro Tip:</strong> Start with small parameters—combinatorial numbers grow exponentially!
    </p>
    <div style='display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;'>
        <span>🎯 Professional Grade</span>
        <span>⚡ High Performance</span>
        <span>🔒 Reliable Results</span>
        <span>🎨 Beautiful UI</span>
    </div>
</div>
""", unsafe_allow_html=True)
