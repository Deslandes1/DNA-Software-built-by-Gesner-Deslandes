import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import hashlib
import random
import math

st.set_page_config(page_title="Real DNA Software", page_icon="🧬", layout="centered")

# ---------- CSS (same as before, shortened for brevity) ----------
st.markdown(
    """
    <style>
    @keyframes helix { 0% { transform: rotateY(0deg); } 100% { transform: rotateY(360deg); } }
    .dna-helix { animation: helix 3s linear infinite; font-size: 100px; text-align: center; margin-bottom: 20px; display: inline-block; }
    .stApp { background: linear-gradient(135deg, #0b2b40, #1e6f5c); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0a2a33, #145c4a); }
    .stButton button { background-color: #ff9a3c !important; color: white !important; border-radius: 30px !important; font-weight: bold !important; }
    .stButton button:hover { background-color: #ff6f00 !important; transform: scale(1.02); }
    h1, h2, h3, h4, p, div, span, label { color: #ffffff !important; }
    .report-box { background: rgba(0,0,0,0.55); padding: 1rem; border-radius: 20px; margin-top: 1rem; border-left: 5px solid #ff9a3c; }
    .success-text { color: #a5ffb2 !important; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Session state ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "profiles" not in st.session_state:
    st.session_state.profiles = {}
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "freq_db" not in st.session_state:
    # Population frequency tables (CODIS 13 loci) – replace with your lab's validated frequencies
    st.session_state.freq_db = {
        "European": {
            "D3S1358": {"14":0.2, "15":0.3, "16":0.25, "17":0.15, "18":0.1},
            "vWA": {"16":0.1, "17":0.3, "18":0.35, "19":0.2, "20":0.05},
            "FGA": {"21":0.15, "22":0.25, "23":0.3, "24":0.2, "25":0.1},
            "TH01": {"6":0.1, "7":0.2, "8":0.3, "9":0.3, "9.3":0.1},
            "TPOX": {"8":0.5, "9":0.3, "10":0.15, "11":0.05},
            "CSF1PO": {"10":0.2, "11":0.3, "12":0.3, "13":0.15, "14":0.05},
            "D5S818": {"11":0.2, "12":0.3, "13":0.3, "14":0.15, "15":0.05},
            "D7S820": {"8":0.1, "9":0.2, "10":0.3, "11":0.25, "12":0.15},
            "D8S1179": {"12":0.2, "13":0.3, "14":0.25, "15":0.15, "16":0.1},
            "D13S317": {"11":0.2, "12":0.3, "13":0.3, "14":0.15, "15":0.05},
            "D16S539": {"11":0.2, "12":0.3, "13":0.25, "14":0.15, "15":0.1},
            "D18S51": {"13":0.1, "14":0.2, "15":0.3, "16":0.25, "17":0.15},
            "D21S11": {"28":0.2, "29":0.3, "30":0.25, "31":0.15, "32":0.1}
        },
        "African": {
            "D3S1358": {"15":0.3, "16":0.35, "17":0.2, "18":0.1, "19":0.05},
            "vWA": {"16":0.2, "17":0.3, "18":0.25, "19":0.15, "20":0.1},
            "FGA": {"20":0.1, "21":0.2, "22":0.3, "23":0.25, "24":0.15},
            "TH01": {"6":0.2, "7":0.3, "8":0.2, "9":0.2, "10":0.1},
            "TPOX": {"8":0.2, "9":0.4, "10":0.3, "11":0.1},
            "CSF1PO": {"10":0.25, "11":0.3, "12":0.25, "13":0.15, "14":0.05},
            "D5S818": {"11":0.25, "12":0.35, "13":0.25, "14":0.1, "15":0.05},
            "D7S820": {"8":0.15, "9":0.25, "10":0.35, "11":0.2, "12":0.05},
            "D8S1179": {"12":0.25, "13":0.35, "14":0.2, "15":0.15, "16":0.05},
            "D13S317": {"11":0.25, "12":0.35, "13":0.25, "14":0.1, "15":0.05},
            "D16S539": {"11":0.3, "12":0.35, "13":0.2, "14":0.1, "15":0.05},
            "D18S51": {"13":0.15, "14":0.25, "15":0.3, "16":0.2, "17":0.1},
            "D21S11": {"28":0.15, "29":0.35, "30":0.25, "31":0.15, "32":0.1}
        },
        "Asian": {
            "D3S1358": {"14":0.3, "15":0.4, "16":0.2, "17":0.08, "18":0.02},
            "vWA": {"16":0.15, "17":0.4, "18":0.3, "19":0.1, "20":0.05},
            "FGA": {"21":0.2, "22":0.35, "23":0.25, "24":0.15, "25":0.05},
            "TH01": {"7":0.15, "8":0.3, "9":0.4, "9.3":0.1, "10":0.05},
            "TPOX": {"8":0.4, "9":0.4, "10":0.15, "11":0.05},
            "CSF1PO": {"10":0.15, "11":0.35, "12":0.3, "13":0.15, "14":0.05},
            "D5S818": {"11":0.2, "12":0.4, "13":0.25, "14":0.1, "15":0.05},
            "D7S820": {"8":0.1, "9":0.3, "10":0.35, "11":0.2, "12":0.05},
            "D8S1179": {"12":0.3, "13":0.35, "14":0.2, "15":0.1, "16":0.05},
            "D13S317": {"11":0.3, "12":0.35, "13":0.2, "14":0.1, "15":0.05},
            "D16S539": {"11":0.25, "12":0.35, "13":0.25, "14":0.1, "15":0.05},
            "D18S51": {"13":0.1, "14":0.2, "15":0.35, "16":0.25, "17":0.1},
            "D21S11": {"28":0.35, "29":0.3, "30":0.2, "31":0.1, "32":0.05}
        }
    }

# ---------- Forensic functions ----------
LOCI = ["D3S1358", "vWA", "FGA", "TH01", "TPOX", "CSF1PO", "D5S818", "D7S820", "D8S1179", "D13S317", "D16S539", "D18S51", "D21S11"]

def get_allele_frequency(locus, allele, population="European"):
    freq_dict = st.session_state.freq_db.get(population, {}).get(locus, {})
    return freq_dict.get(str(allele), 0.001)

def paternity_index(child_markers, alleged_father_markers, population="European"):
    pi_locus = []
    for locus in LOCI:
        c1, c2 = child_markers[locus]
        f1, f2 = alleged_father_markers[locus]
        if f1 == f2:
            transmitted = f1
            if transmitted not in (c1, c2):
                return 0.0, -float('inf')
            p = get_allele_frequency(locus, transmitted, population)
            pi = 1.0 / p if c1 == c2 else 1.0 / (2.0 * p)
        else:
            shared = set([f1, f2]) & set([c1, c2])
            if not shared:
                return 0.0, -float('inf')
            pi = 0.0
            for a in shared:
                p = get_allele_frequency(locus, a, population)
                if c1 == c2 == a:
                    pi += 1.0 / p
                else:
                    pi += 1.0 / (2.0 * p)
        pi_locus.append(pi)
    combined_pi = np.prod(pi_locus)
    log10_pi = math.log10(combined_pi) if combined_pi > 0 else -float('inf')
    return combined_pi, log10_pi

def sibling_index(profile1, profile2, population="European"):
    lr_locus = []
    for locus in LOCI:
        g1 = set(profile1[locus])
        g2 = set(profile2[locus])
        alleles = list(g1 | g2)
        freq = {a: get_allele_frequency(locus, a, population) for a in alleles}
        def prob_genotype(g):
            a1, a2 = sorted(g)
            if a1 == a2:
                return freq[a1]**2
            else:
                return 2 * freq[a1] * freq[a2]
        p_unrelated = prob_genotype(g1) * prob_genotype(g2)
        if p_unrelated == 0:
            lr_locus.append(0.0)
            continue
        # IBD=2
        p_ibd2 = prob_genotype(g1) if g1 == g2 else 0.0
        # IBD=1
        p_ibd1 = 0.0
        for a in alleles:
            def prob_given_shared(g, a):
                if a not in g:
                    return 0.0
                if g[0] == g[1] == a:
                    return freq[a]
                else:
                    other = g[0] if g[1] == a else g[1]
                    return freq[other]
            p_ibd1 += prob_given_shared(g1, a) * prob_given_shared(g2, a)
        p_siblings = 0.25 * p_ibd2 + 0.5 * p_ibd1 + 0.25 * p_unrelated
        lr = p_siblings / p_unrelated
        lr_locus.append(lr)
    combined_lr = np.prod(lr_locus)
    log10_lr = math.log10(combined_lr) if combined_lr > 0 else -float('inf')
    return combined_lr, log10_lr

def identical_twins(profile1, profile2):
    for locus in LOCI:
        if profile1[locus] != profile2[locus]:
            return False
    return True

def ancestry_likelihood(profile, population="European"):
    log_lik = 0.0
    for locus in LOCI:
        a1, a2 = profile[locus]
        p1 = get_allele_frequency(locus, a1, population)
        p2 = get_allele_frequency(locus, a2, population)
        prob = p1**2 if a1 == a2 else 2 * p1 * p2
        log_lik += math.log(prob)
    return log_lik

def generate_random_markers(seed_name):
    random.seed(hashlib.md5(seed_name.encode()).hexdigest())
    markers = {}
    for locus in LOCI:
        a1 = random.randint(8, 20)
        a2 = random.randint(8, 20)
        markers[locus] = sorted([a1, a2])
    return markers

def parse_markers_from_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    markers = {}
    for _, row in df.iterrows():
        locus = row['Locus'].strip()
        a1 = int(row['Allele1'])
        a2 = int(row['Allele2'])
        markers[locus] = sorted([a1, a2])
    return markers

def display_markers_table(markers):
    return pd.DataFrame([(locus, markers[locus][0], markers[locus][1]) for locus in LOCI if locus in markers],
                        columns=["Locus", "Allele 1", "Allele 2"])

# ---------- Login ----------
def login():
    st.markdown('<div style="text-align:center;"><div class="dna-helix">🧬</div></div>', unsafe_allow_html=True)
    st.title("Real Forensic DNA Software")
    st.markdown("**Paternity · Siblings · Twins · Ancestry** – with likelihood ratios")
    st.markdown("Built by **Gesner Deslandes**")
    st.markdown("---")
    st.markdown("### 🔐 Access")
    password = st.text_input("Enter secure password", type="password")
    if st.button("Unlock DNA Lab"):
        if password == "20082010":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid access code.")

# ---------- Main app ----------
def main_app():
    st.title("🧬 Real‑World DNA Analysis")
    st.markdown("**Accepts real STR allele calls – computes forensic likelihood ratios**")
    st.markdown("---")

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2866/2866864.png", width=80)
        st.markdown(f"**Profiles stored:** {len(st.session_state.profiles)}")
        for name in st.session_state.profiles:
            st.write(f"• {name}")
        st.markdown("---")
        pop = st.selectbox("Population frequency database", list(st.session_state.freq_db.keys()), key="pop_selector")
        st.session_state.current_pop = pop
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.profiles = {}
            st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["📝 Register Profile", "🔬 Paternity & Kinship", "🌍 Ancestry", "📊 Reports"])

    with tab1:
        st.subheader("Register a DNA profile (real allele calls)")
        name = st.text_input("Individual ID")
        sample_type = st.selectbox("Sample type", ["Blood", "Saliva", "Hair", "Sweat", "Buccal swab"])
        data_source = st.radio("Input method", ["Auto‑generate demo", "Upload CSV (real data)", "Manual entry"], horizontal=True)
        markers = None
        if data_source == "Auto‑generate demo" and name:
            markers = generate_random_markers(name)
            st.success("Demo profile generated. Replace with real data for production.")
        elif data_source == "Upload CSV (real data)" and name:
            uploaded = st.file_uploader("CSV format: Locus,Allele1,Allele2", type=["csv"])
            if uploaded:
                markers = parse_markers_from_csv(uploaded)
                st.success("Real STR profile loaded.")
        elif data_source == "Manual entry" and name:
            markers = {}
            cols = st.columns(4)
            for i, locus in enumerate(LOCI):
                with cols[i % 4]:
                    a1 = st.number_input(f"{locus} a1", min_value=5, max_value=35, value=16, key=f"{locus}_a1")
                    a2 = st.number_input(f"{locus} a2", min_value=5, max_value=35, value=18, key=f"{locus}_a2")
                    markers[locus] = sorted([a1, a2])
        if markers and name:
            st.dataframe(display_markers_table(markers), use_container_width=True)
        if st.button("💾 Save Profile", use_container_width=True) and name and markers:
            st.session_state.profiles[name] = {
                "sample_type": sample_type,
                "markers": markers,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.success(f"Profile '{name}' saved.")

    with tab2:
        st.subheader("Forensic Relationship Tests")
        if len(st.session_state.profiles) < 2:
            st.info("Need at least two DNA profiles.")
        else:
            profiles = list(st.session_state.profiles.keys())
            test_type = st.radio("Test type", ["Paternity (Child & Alleged Father)", "Full Siblings", "Identical Twins"])
            if test_type == "Paternity (Child & Alleged Father)":
                child = st.selectbox("Child's profile", profiles)
                father = st.selectbox("Alleged father's profile", [p for p in profiles if p != child])
                if st.button("Compute Paternity Index"):
                    child_m = st.session_state.profiles[child]["markers"]
                    father_m = st.session_state.profiles[father]["markers"]
                    cpi, log10_cpi = paternity_index(child_m, father_m, st.session_state.current_pop)
                    st.session_state.last_result = {"test":"Paternity","child":child,"father":father,"CPI":cpi,"log10_CPI":log10_cpi}
                    st.metric("Combined Paternity Index (CPI)", f"{cpi:.2e}" if cpi < 1e6 else f"{cpi:.1e}")
                    st.metric("log₁₀(CPI)", f"{log10_cpi:.2f}")
                    if cpi >= 10000: st.success("✅ Paternity confirmed (CPI > 10,000)")
                    elif cpi == 0: st.error("❌ Exclusion – at least one locus mismatched")
                    else: st.warning(f"⚠️ Weak evidence (CPI = {cpi:.1f}) – more loci needed")
            elif test_type == "Full Siblings":
                ind1 = st.selectbox("Person A", profiles)
                ind2 = st.selectbox("Person B", [p for p in profiles if p != ind1])
                if st.button("Compute Sibling Kinship Index"):
                    m1 = st.session_state.profiles[ind1]["markers"]
                    m2 = st.session_state.profiles[ind2]["markers"]
                    lr, log10_lr = sibling_index(m1, m2, st.session_state.current_pop)
                    st.session_state.last_result = {"test":"Siblings","ind1":ind1,"ind2":ind2,"LR":lr,"log10_LR":log10_lr}
                    st.metric("Likelihood ratio (siblings vs unrelated)", f"{lr:.2e}")
                    st.metric("log₁₀(LR)", f"{log10_lr:.2f}")
                    if log10_lr >= 3: st.success("✅ Strong support for full siblings")
                    elif log10_lr <= -3: st.error("❌ Support for unrelated")
                    else: st.warning("⚠️ Inconclusive – test more loci")
            elif test_type == "Identical Twins":
                t1 = st.selectbox("Twin A", profiles)
                t2 = st.selectbox("Twin B", [p for p in profiles if p != t1])
                if st.button("Check for identical twins"):
                    m1 = st.session_state.profiles[t1]["markers"]
                    m2 = st.session_state.profiles[t2]["markers"]
                    identical = identical_twins(m1, m2)
                    st.session_state.last_result = {"test":"Twins","twin1":t1,"twin2":t2,"identical":identical}
                    if identical: st.success("🧬 **Identical (monozygotic) twins** – all 13 STR loci match perfectly.")
                    else: st.info("Not identical – either fraternal twins or unrelated.")

    with tab3:
        st.subheader("Ancestry Inference using Population Frequencies")
        if st.session_state.profiles:
            selected = st.selectbox("Select individual", list(st.session_state.profiles.keys()))
            if st.button("Estimate ancestry likelihoods"):
                markers = st.session_state.profiles[selected]["markers"]
                pops = list(st.session_state.freq_db.keys())
                lls = [ancestry_likelihood(markers, pop) for pop in pops]
                exp_ll = np.exp(lls - np.max(lls))
                probs = exp_ll / exp_ll.sum()
                st.session_state.last_result = {"test":"Ancestry","individual":selected,"probabilities":dict(zip(pops, probs))}
                for pop, prob in zip(pops, probs): st.progress(prob, text=f"{pop}: {prob:.1%}")
                st.caption("Based on 13 STR loci – real ancestry uses thousands of SNPs.")
        else: st.info("No profiles registered.")

    with tab4:
        st.subheader("Forensic Report")
        if st.session_state.last_result:
            res = st.session_state.last_result
            report = f"FORENSIC DNA REPORT\nDate: {datetime.now()}\nPopulation database: {st.session_state.current_pop}\n\n"
            if res['test'] == "Paternity":
                report += f"Test: Paternity\nChild: {res['child']}\nAlleged father: {res['father']}\nCPI: {res['CPI']:.2e}\nlog₁₀(CPI): {res['log10_CPI']:.2f}\n"
                report += "Conclusion: Paternity confirmed" if res['CPI'] >= 10000 else ("Exclusion" if res['CPI'] == 0 else "Inconclusive")
            elif res['test'] == "Siblings":
                report += f"Test: Full siblings\nIndividuals: {res['ind1']} and {res['ind2']}\nLR: {res['LR']:.2e}\nlog₁₀(LR): {res['log10_LR']:.2f}\n"
                report += "Conclusion: Strong support for siblings" if res['log10_LR'] >= 3 else ("Support for unrelated" if res['log10_LR'] <= -3 else "Inconclusive")
            elif res['test'] == "Twins":
                report += f"Test: Twin zygosity\nTwins: {res['twin1']} and {res['twin2']}\nVerdict: Identical twins" if res['identical'] else "Verdict: Not identical"
            elif res['test'] == "Ancestry":
                report += f"Ancestry for {res['individual']}\n" + "\n".join([f"{k}: {v:.1%}" for k,v in res['probabilities'].items()])
            st.download_button("📄 Download full report (TXT)", report, file_name=f"forensic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        else: st.info("No analysis performed yet.")

if not st.session_state.authenticated:
    login()
else:
    main_app()
