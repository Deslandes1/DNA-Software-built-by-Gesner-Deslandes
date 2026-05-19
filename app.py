import streamlit as st
import pandas as pd
import numpy as np
import base64
from datetime import datetime
import hashlib
import random

st.set_page_config(
    page_title="DNA Software – Gesner Deslandes",
    page_icon="🧬",
    layout="centered"
)

# ---------- CSS with DNA helix animation ----------
st.markdown(
    """
    <style>
    @keyframes helix {
        0% { transform: rotateY(0deg); }
        100% { transform: rotateY(360deg); }
    }
    .dna-helix {
        animation: helix 3s linear infinite;
        font-size: 100px;
        text-align: center;
        margin-bottom: 20px;
        display: inline-block;
    }
    .stApp {
        background: linear-gradient(135deg, #0b2b40, #1e6f5c);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a2a33, #145c4a);
    }
    .stButton button {
        background-color: #ff9a3c !important;
        color: white !important;
        border-radius: 30px !important;
        font-weight: bold !important;
    }
    .stButton button:hover {
        background-color: #ff6f00 !important;
        transform: scale(1.02);
    }
    h1, h2, h3, h4, p, div, span, label {
        color: #ffffff !important;
    }
    .report-box {
        background: rgba(0,0,0,0.55);
        padding: 1rem;
        border-radius: 20px;
        margin-top: 1rem;
        border-left: 5px solid #ff9a3c;
    }
    .success-text {
        color: #a5ffb2 !important;
        font-weight: bold;
    }
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

# Reference populations for ancestry (simplified)
LOCI = ["D3S1358", "vWA", "FGA", "TH01", "TPOX", "CSF1PO", "D5S818", "D7S820", "D8S1179", "D13S317", "D16S539", "D18S51", "D21S11"]

REF_POP = {
    "European": {
        "D3S1358": {"freq": {"14":0.2,"15":0.3,"16":0.25,"17":0.15,"18":0.1}},
        "vWA": {"freq": {"16":0.1,"17":0.3,"18":0.35,"19":0.2,"20":0.05}},
        "FGA": {"freq": {"21":0.15,"22":0.25,"23":0.3,"24":0.2,"25":0.1}},
        "TH01": {"freq": {"6":0.1,"7":0.2,"8":0.3,"9":0.3,"9.3":0.1}},
        "TPOX": {"freq": {"8":0.5,"9":0.3,"10":0.15,"11":0.05}}
    },
    "African": {
        "D3S1358": {"freq": {"15":0.3,"16":0.35,"17":0.2,"18":0.1,"19":0.05}},
        "vWA": {"freq": {"16":0.2,"17":0.3,"18":0.25,"19":0.15,"20":0.1}},
        "FGA": {"freq": {"20":0.1,"21":0.2,"22":0.3,"23":0.25,"24":0.15}},
        "TH01": {"freq": {"6":0.2,"7":0.3,"8":0.2,"9":0.2,"10":0.1}},
        "TPOX": {"freq": {"8":0.2,"9":0.4,"10":0.3,"11":0.1}}
    },
    "Asian": {
        "D3S1358": {"freq": {"14":0.3,"15":0.4,"16":0.2,"17":0.08,"18":0.02}},
        "vWA": {"freq": {"16":0.15,"17":0.4,"18":0.3,"19":0.1,"20":0.05}},
        "FGA": {"freq": {"21":0.2,"22":0.35,"23":0.25,"24":0.15,"25":0.05}},
        "TH01": {"freq": {"7":0.15,"8":0.3,"9":0.4,"9.3":0.1,"10":0.05}},
        "TPOX": {"freq": {"8":0.4,"9":0.4,"10":0.15,"11":0.05}}
    }
}

# ---------- Helper functions ----------
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
        locus = row['Locus']
        a1 = int(row['Allele1'])
        a2 = int(row['Allele2'])
        markers[locus] = sorted([a1, a2])
    return markers

def compute_paternity_index(child_markers, alleged_father_markers):
    matches = 0
    for locus in LOCI:
        child_alleles = child_markers[locus]
        father_alleles = alleged_father_markers[locus]
        if any(a in father_alleles for a in child_alleles):
            matches += 1
    return matches / len(LOCI), matches

def compute_sibling_index(profile1, profile2):
    shared = 0
    total_alleles = 0
    for locus in LOCI:
        a1_set = set(profile1[locus])
        a2_set = set(profile2[locus])
        shared += len(a1_set & a2_set)
        total_alleles += 2
    return shared / total_alleles, shared

def are_identical_twins(profile1, profile2):
    for locus in LOCI:
        if profile1[locus] != profile2[locus]:
            return False, 0
    return True, 100.0

def compute_ancestry(profile, populations):
    scores = {}
    for pop, freq_dict in populations.items():
        log_lik = 0.0
        for locus in LOCI:
            if locus not in freq_dict:
                continue
            allele_freqs = freq_dict[locus]["freq"]
            a1, a2 = profile[locus]
            p1 = allele_freqs.get(str(a1), 0.001)
            p2 = allele_freqs.get(str(a2), 0.001)
            prob = p1**2 if a1 == a2 else 2 * p1 * p2
            log_lik += np.log(prob)
        scores[pop] = log_lik
    exp_scores = np.exp(list(scores.values()))
    probs = exp_scores / exp_scores.sum()
    return {pop: probs[i] for i, pop in enumerate(scores.keys())}

def display_markers_table(markers):
    return pd.DataFrame([(locus, markers[locus][0], markers[locus][1]) for locus in LOCI if locus in markers],
                        columns=["Locus", "Allele 1", "Allele 2"])

# ---------- Login ----------
def login():
    st.markdown('<div style="text-align:center;"><div class="dna-helix">🧬</div></div>', unsafe_allow_html=True)
    st.title("DNA Forensic Software")
    st.markdown("**Paternity · Modernity (Ancestry) · Twins · Siblings**")
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
    st.title("🧬 DNA Identification Suite")
    st.markdown("**Analyse blood, saliva, hair, or sweat samples**")
    st.markdown("---")

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2866/2866864.png", width=80)
        st.markdown(f"**Stored profiles:** {len(st.session_state.profiles)}")
        if st.session_state.profiles:
            for name in st.session_state.profiles:
                st.write(f"• {name}")
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.profiles = {}
            st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["📝 Register", "🔬 Relationship", "🌍 Ancestry", "📊 Reports"])

    # Register tab
    with tab1:
        st.subheader("Register a DNA profile")
        name = st.text_input("Name / ID")
        sample_type = st.selectbox("Sample type", ["Blood", "Saliva", "Hair", "Sweat"])
        data_source = st.radio("Input method", ["Auto-generate (demo)", "Upload CSV", "Manual"], horizontal=True)

        markers = None
        if data_source == "Auto-generate (demo)" and name:
            markers = generate_random_markers(name)
            st.success("Auto‑generated 13 STR loci.")
        elif data_source == "Upload CSV" and name:
            uploaded = st.file_uploader("CSV: Locus,Allele1,Allele2", type=["csv"])
            if uploaded:
                markers = parse_markers_from_csv(uploaded)
                st.success("CSV loaded.")
        elif data_source == "Manual" and name:
            markers = {}
            cols = st.columns(4)
            for i, locus in enumerate(LOCI):
                with cols[i % 4]:
                    a1 = st.number_input(f"{locus} a1", min_value=5, max_value=30, value=16, key=f"{locus}_a1")
                    a2 = st.number_input(f"{locus} a2", min_value=5, max_value=30, value=18, key=f"{locus}_a2")
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

    # Relationship tab
    with tab2:
        st.subheader("Paternity, Siblings & Twins")
        if len(st.session_state.profiles) < 2:
            st.info("Need at least two profiles.")
        else:
            profiles = list(st.session_state.profiles.keys())
            test = st.radio("Test type", ["Paternity", "Siblings", "Twins"])
            if test == "Paternity":
                child = st.selectbox("Child", profiles)
                father = st.selectbox("Alleged father", [p for p in profiles if p != child])
                if st.button("Run Paternity Test"):
                    child_m = st.session_state.profiles[child]["markers"]
                    father_m = st.session_state.profiles[father]["markers"]
                    prob, matches = compute_paternity_index(child_m, father_m)
                    st.session_state.last_result = {"test":"Paternity","child":child,"father":father,"probability":prob,"matches":matches}
                    st.metric("Paternity probability", f"{prob:.1%}")
                    st.metric("Loci matched", f"{matches}/{len(LOCI)}")
                    if prob >= 0.9: st.success("✅ Father confirmed")
                    elif prob >= 0.7: st.warning("⚠️ Inconclusive")
                    else: st.error("❌ Excluded")
            elif test == "Siblings":
                a = st.selectbox("Person A", profiles)
                b = st.selectbox("Person B", [p for p in profiles if p != a])
                if st.button("Compute Sibling index"):
                    m1 = st.session_state.profiles[a]["markers"]
                    m2 = st.session_state.profiles[b]["markers"]
                    sim, shared = compute_sibling_index(m1, m2)
                    st.session_state.last_result = {"test":"Siblings","ind1":a,"ind2":b,"similarity":sim}
                    st.metric("Allele sharing", f"{sim:.1%}")
                    if sim > 0.45: st.success("✅ Likely full siblings")
                    elif sim > 0.25: st.warning("⚠️ Possible half‑siblings")
                    else: st.error("❌ Unlikely siblings")
            elif test == "Twins":
                t1 = st.selectbox("Twin A", profiles)
                t2 = st.selectbox("Twin B", [p for p in profiles if p != t1])
                if st.button("Analyse twin type"):
                    m1 = st.session_state.profiles[t1]["markers"]
                    m2 = st.session_state.profiles[t2]["markers"]
                    identical, _ = are_identical_twins(m1, m2)
                    sim, _ = compute_sibling_index(m1, m2) if not identical else (1.0,0)
                    st.session_state.last_result = {"test":"Twins","twin1":t1,"twin2":t2,"identical":identical,"similarity":sim}
                    if identical: st.success("🧬 Identical twins (monozygotic)")
                    else: st.info(f"Fraternal twins (dizygotic) – sharing {sim:.1%}")

    # Ancestry tab
    with tab3:
        if st.session_state.profiles:
            selected = st.selectbox("Individual for ancestry", list(st.session_state.profiles.keys()))
            if st.button("Estimate ancestry"):
                markers = st.session_state.profiles[selected]["markers"]
                probs = compute_ancestry(markers, REF_POP)
                st.session_state.last_result = {"test":"Ancestry","individual":selected,"probabilities":probs}
                for pop, prob in probs.items():
                    st.progress(prob, text=f"{pop}: {prob:.1%}")
        else:
            st.info("No profiles yet.")

    # Reports tab
    with tab4:
        if st.session_state.last_result:
            res = st.session_state.last_result
            report = f"DNA Report – {res['test']}\n"
            if res['test'] == "Paternity":
                report += f"Child: {res['child']}, Father: {res['father']}\nProbability: {res['probability']:.1%}\nLoci matches: {res['matches']}/{len(LOCI)}"
            elif res['test'] == "Siblings":
                report += f"{res['ind1']} & {res['ind2']}\nAllele sharing: {res['similarity']:.1%}"
            elif res['test'] == "Twins":
                report += f"{res['twin1']} & {res['twin2']}\nIdentical: {'Yes' if res['identical'] else 'No (fraternal)'}\nSimilarity: {res['similarity']:.1%}"
            elif res['test'] == "Ancestry":
                report += f"{res['individual']}\n" + "\n".join([f"{k}: {v:.1%}" for k,v in res['probabilities'].items()])
            st.download_button("📄 Download report (TXT)", report, file_name=f"dna_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        else:
            st.info("No analysis yet.")

# ---------- Run ----------
if not st.session_state.authenticated:
    login()
else:
    main_app()
