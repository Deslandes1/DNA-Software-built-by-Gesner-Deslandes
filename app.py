import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import hashlib
import random
import math

st.set_page_config(page_title="DNA Forensic Software", page_icon="🧬", layout="centered")

# ---------- Translations ----------
translations = {
    "en": {
        "app_title": "DNA Forensic Software",
        "subtitle": "Paternity · Siblings · Twins · Ancestry – with likelihood ratios",
        "built_by": "Built by Gesner Deslandes",
        "access": "Access",
        "password": "Enter secure password",
        "unlock": "Unlock DNA Lab",
        "wrong_password": "Invalid access code.",
        "main_title": "Real‑World DNA Analysis",
        "main_subtitle": "Accepts real STR allele calls – computes forensic likelihood ratios",
        "sidebar_profiles": "Profiles stored:",
        "sidebar_population": "Population frequency database",
        "logout": "Logout",
        "tab_register": "📝 Register Profile",
        "tab_relationship": "🔬 Paternity & Kinship",
        "tab_ancestry": "🌍 Ancestry",
        "tab_reports": "📊 Reports",
        "register_subheader": "Register a DNA profile (real allele calls)",
        "individual_id": "Individual ID",
        "sample_type": "Sample type",
        "sample_blood": "Blood",
        "sample_saliva": "Saliva",
        "sample_hair": "Hair",
        "sample_sweat": "Sweat",
        "sample_buccal": "Buccal swab",
        "input_method": "Input method",
        "auto_demo": "Auto‑generate demo",
        "upload_csv": "Upload CSV (real data)",
        "manual_entry": "Manual entry",
        "demo_success": "Demo profile generated. Replace with real data for production.",
        "csv_prompt": "CSV format: Locus,Allele1,Allele2",
        "csv_success": "Real STR profile loaded.",
        "save_profile": "💾 Save Profile",
        "save_success": "Profile '{}' saved.",
        "need_two_profiles": "Need at least two DNA profiles.",
        "test_type": "Test type",
        "paternity_test": "Paternity (Child & Alleged Father)",
        "siblings_test": "Full Siblings",
        "twins_test": "Identical Twins",
        "child_label": "Child's profile",
        "father_label": "Alleged father's profile",
        "compute_paternity": "Compute Paternity Index",
        "cpi_metric": "Combined Paternity Index (CPI)",
        "log10_cpi": "log₁₀(CPI)",
        "paternity_confirmed": "✅ Paternity confirmed (CPI > 10,000)",
        "paternity_excluded": "❌ Exclusion – at least one locus mismatched",
        "paternity_weak": "⚠️ Weak evidence (CPI = {:.1f}) – more loci needed",
        "person_a": "Person A",
        "person_b": "Person B",
        "compute_sibling": "Compute Sibling Kinship Index",
        "lr_metric": "Likelihood ratio (siblings vs unrelated)",
        "log10_lr": "log₁₀(LR)",
        "sibling_strong": "✅ Strong support for full siblings",
        "sibling_unrelated": "❌ Support for unrelated",
        "sibling_inconclusive": "⚠️ Inconclusive – test more loci",
        "twin_a": "Twin A",
        "twin_b": "Twin B",
        "check_twins": "Check for identical twins",
        "identical_twins": "🧬 **Identical (monozygotic) twins** – all 13 STR loci match perfectly.",
        "fraternal_twins": "Not identical – either fraternal twins or unrelated.",
        "ancestry_subheader": "Ancestry Inference using Population Frequencies",
        "select_individual": "Select individual",
        "estimate_ancestry": "Estimate ancestry likelihoods",
        "ancestry_caption": "Based on 13 STR loci – real ancestry uses thousands of SNPs.",
        "no_profiles": "No profiles registered.",
        "report_subheader": "Forensic Report",
        "no_analysis": "No analysis performed yet.",
        "download_report": "📄 Download full report (TXT)",
        "report_date": "FORENSIC DNA REPORT\nDate: {}\nPopulation database: {}\n\n",
        "paternity_report": "Test: Paternity\nChild: {}\nAlleged father: {}\nCPI: {:.2e}\nlog₁₀(CPI): {:.2f}\n",
        "paternity_conclusion_confirmed": "Conclusion: Paternity confirmed",
        "paternity_conclusion_excluded": "Conclusion: Exclusion",
        "paternity_conclusion_inconclusive": "Conclusion: Inconclusive",
        "sibling_report": "Test: Full siblings\nIndividuals: {} and {}\nLR: {:.2e}\nlog₁₀(LR): {:.2f}\n",
        "sibling_conclusion_strong": "Conclusion: Strong support for siblings",
        "sibling_conclusion_unrelated": "Conclusion: Support for unrelated",
        "sibling_conclusion_inconclusive": "Conclusion: Inconclusive",
        "twins_report_identical": "Test: Twin zygosity\nTwins: {} and {}\nVerdict: Identical twins",
        "twins_report_not": "Test: Twin zygosity\nTwins: {} and {}\nVerdict: Not identical",
        "ancestry_report": "Ancestry for {}\n",
        "login_helix": "🧬",
    },
    "fr": {
        "app_title": "Logiciel ADN Forensic",
        "subtitle": "Paternité · Frères/Soeurs · Jumeaux · Ascendance – avec rapports de vraisemblance",
        "built_by": "Développé par Gesner Deslandes",
        "access": "Accès",
        "password": "Entrez le mot de passe sécurisé",
        "unlock": "Déverrouiller le labo ADN",
        "wrong_password": "Code d'accès invalide.",
        "main_title": "Analyse ADN Réelle",
        "main_subtitle": "Accepte des allèles STR réels – calcule les rapports de vraisemblance forensiques",
        "sidebar_profiles": "Profils stockés :",
        "sidebar_population": "Base de données fréquences population",
        "logout": "Déconnexion",
        "tab_register": "📝 Enregistrer un profil",
        "tab_relationship": "🔬 Paternité & Parenté",
        "tab_ancestry": "🌍 Ascendance",
        "tab_reports": "📊 Rapports",
        "register_subheader": "Enregistrer un profil ADN (allèles réels)",
        "individual_id": "ID de l'individu",
        "sample_type": "Type d'échantillon",
        "sample_blood": "Sang",
        "sample_saliva": "Salive",
        "sample_hair": "Cheveu",
        "sample_sweat": "Sueur",
        "sample_buccal": "Écouvillon buccal",
        "input_method": "Méthode de saisie",
        "auto_demo": "Génération auto (démo)",
        "upload_csv": "Importer CSV (données réelles)",
        "manual_entry": "Saisie manuelle",
        "demo_success": "Profil démo généré. Remplacez par des données réelles pour la production.",
        "csv_prompt": "Format CSV : Locus,Allele1,Allele2",
        "csv_success": "Profil STR réel chargé.",
        "save_profile": "💾 Enregistrer le profil",
        "save_success": "Profil '{}' enregistré.",
        "need_two_profiles": "Au moins deux profils ADN requis.",
        "test_type": "Type de test",
        "paternity_test": "Paternité (Enfant & Père présumé)",
        "siblings_test": "Frères/Soeurs pleins",
        "twins_test": "Jumeaux identiques",
        "child_label": "Profil de l'enfant",
        "father_label": "Profil du père présumé",
        "compute_paternity": "Calculer l'indice de paternité",
        "cpi_metric": "Indice de paternité combiné (CPI)",
        "log10_cpi": "log₁₀(CPI)",
        "paternity_confirmed": "✅ Paternité confirmée (CPI > 10 000)",
        "paternity_excluded": "❌ Exclusion – au moins un locus non concordant",
        "paternity_weak": "⚠️ Preuve faible (CPI = {:.1f}) – plus de loci nécessaires",
        "person_a": "Personne A",
        "person_b": "Personne B",
        "compute_sibling": "Calculer l'indice de parenté fraternel",
        "lr_metric": "Rapport de vraisemblance (frères vs non apparentés)",
        "log10_lr": "log₁₀(LR)",
        "sibling_strong": "✅ Forte probabilité de fratrie",
        "sibling_unrelated": "❌ Non apparentés",
        "sibling_inconclusive": "⚠️ Non concluant – testez plus de loci",
        "twin_a": "Jumeau A",
        "twin_b": "Jumeau B",
        "check_twins": "Vérifier les jumeaux identiques",
        "identical_twins": "🧬 **Jumeaux identiques (monozygotes)** – 13 loci STR parfaitement concordants.",
        "fraternal_twins": "Pas identiques – jumeaux dizygotes ou non apparentés.",
        "ancestry_subheader": "Estimation de l'ascendance via fréquences population",
        "select_individual": "Sélectionner un individu",
        "estimate_ancestry": "Estimer l'ascendance",
        "ancestry_caption": "Basé sur 13 loci STR – l'ascendance réelle utilise des milliers de SNPs.",
        "no_profiles": "Aucun profil enregistré.",
        "report_subheader": "Rapport forensique",
        "no_analysis": "Aucune analyse effectuée.",
        "download_report": "📄 Télécharger le rapport (TXT)",
        "report_date": "RAPPORT ADN FORENSIQUE\nDate : {}\nBase de données population : {}\n\n",
        "paternity_report": "Test : Paternité\nEnfant : {}\nPère présumé : {}\nCPI : {:.2e}\nlog₁₀(CPI) : {:.2f}\n",
        "paternity_conclusion_confirmed": "Conclusion : Paternité confirmée",
        "paternity_conclusion_excluded": "Conclusion : Exclusion",
        "paternity_conclusion_inconclusive": "Conclusion : Non concluant",
        "sibling_report": "Test : Frères/Soeurs pleins\nIndividus : {} et {}\nLR : {:.2e}\nlog₁₀(LR) : {:.2f}\n",
        "sibling_conclusion_strong": "Conclusion : Forte probabilité de fratrie",
        "sibling_conclusion_unrelated": "Conclusion : Non apparentés",
        "sibling_conclusion_inconclusive": "Conclusion : Non concluant",
        "twins_report_identical": "Test : Zygosité des jumeaux\nJumeaux : {} et {}\nVerdict : Jumeaux identiques",
        "twins_report_not": "Test : Zygosité des jumeaux\nJumeaux : {} et {}\nVerdict : Non identiques",
        "ancestry_report": "Ascendance de {}\n",
        "login_helix": "🧬",
    },
    "es": {
        "app_title": "Software Forense de ADN",
        "subtitle": "Paternidad · Hermanos · Gemelos · Ascendencia – con razones de verosimilitud",
        "built_by": "Creado por Gesner Deslandes",
        "access": "Acceso",
        "password": "Ingrese contraseña segura",
        "unlock": "Abrir laboratorio de ADN",
        "wrong_password": "Código de acceso inválido.",
        "main_title": "Análisis de ADN Real",
        "main_subtitle": "Acepta alelos STR reales – calcula razones de verosimilitud forenses",
        "sidebar_profiles": "Perfiles almacenados:",
        "sidebar_population": "Base de datos de frecuencias poblacionales",
        "logout": "Cerrar sesión",
        "tab_register": "📝 Registrar perfil",
        "tab_relationship": "🔬 Paternidad & Parentesco",
        "tab_ancestry": "🌍 Ascendencia",
        "tab_reports": "📊 Informes",
        "register_subheader": "Registrar un perfil de ADN (alelos reales)",
        "individual_id": "ID del individuo",
        "sample_type": "Tipo de muestra",
        "sample_blood": "Sangre",
        "sample_saliva": "Saliva",
        "sample_hair": "Cabello",
        "sample_sweat": "Sudor",
        "sample_buccal": "Hisopo bucal",
        "input_method": "Método de entrada",
        "auto_demo": "Auto‑generar demo",
        "upload_csv": "Subir CSV (datos reales)",
        "manual_entry": "Entrada manual",
        "demo_success": "Perfil demo generado. Reemplace con datos reales para producción.",
        "csv_prompt": "Formato CSV: Locus,Allele1,Allele2",
        "csv_success": "Perfil STR real cargado.",
        "save_profile": "💾 Guardar perfil",
        "save_success": "Perfil '{}' guardado.",
        "need_two_profiles": "Se necesitan al menos dos perfiles de ADN.",
        "test_type": "Tipo de prueba",
        "paternity_test": "Paternidad (Hijo & Padre supuesto)",
        "siblings_test": "Hermanos completos",
        "twins_test": "Gemelos idénticos",
        "child_label": "Perfil del hijo/a",
        "father_label": "Perfil del padre supuesto",
        "compute_paternity": "Calcular índice de paternidad",
        "cpi_metric": "Índice de paternidad combinado (CPI)",
        "log10_cpi": "log₁₀(CPI)",
        "paternity_confirmed": "✅ Paternidad confirmada (CPI > 10,000)",
        "paternity_excluded": "❌ Exclusión – al menos un locus no coincide",
        "paternity_weak": "⚠️ Evidencia débil (CPI = {:.1f}) – se necesitan más loci",
        "person_a": "Persona A",
        "person_b": "Persona B",
        "compute_sibling": "Calcular índice de parentesco entre hermanos",
        "lr_metric": "Razón de verosimilitud (hermanos vs no relacionados)",
        "log10_lr": "log₁₀(LR)",
        "sibling_strong": "✅ Fuerte apoyo para hermanos completos",
        "sibling_unrelated": "❌ Apoyo para no relacionados",
        "sibling_inconclusive": "⚠️ No concluyente – pruebe más loci",
        "twin_a": "Gemelo A",
        "twin_b": "Gemelo B",
        "check_twins": "Verificar gemelos idénticos",
        "identical_twins": "🧬 **Gemelos idénticos (monocigóticos)** – los 13 loci STR coinciden perfectamente.",
        "fraternal_twins": "No idénticos – gemelos dicigóticos o no relacionados.",
        "ancestry_subheader": "Inferencia de ascendencia usando frecuencias poblacionales",
        "select_individual": "Seleccionar individuo",
        "estimate_ancestry": "Estimar ascendencia",
        "ancestry_caption": "Basado en 13 loci STR – la ascendencia real usa miles de SNPs.",
        "no_profiles": "No hay perfiles registrados.",
        "report_subheader": "Informe Forense",
        "no_analysis": "No se ha realizado ningún análisis.",
        "download_report": "📄 Descargar informe (TXT)",
        "report_date": "INFORME FORENSE DE ADN\nFecha: {}\nBase de datos poblacional: {}\n\n",
        "paternity_report": "Prueba: Paternidad\nHijo/a: {}\nPadre supuesto: {}\nCPI: {:.2e}\nlog₁₀(CPI): {:.2f}\n",
        "paternity_conclusion_confirmed": "Conclusión: Paternidad confirmada",
        "paternity_conclusion_excluded": "Conclusión: Exclusión",
        "paternity_conclusion_inconclusive": "Conclusión: No concluyente",
        "sibling_report": "Prueba: Hermanos completos\nIndividuos: {} y {}\nLR: {:.2e}\nlog₁₀(LR): {:.2f}\n",
        "sibling_conclusion_strong": "Conclusión: Fuerte apoyo para hermanos",
        "sibling_conclusion_unrelated": "Conclusión: Apoyo para no relacionados",
        "sibling_conclusion_inconclusive": "Conclusión: No concluyente",
        "twins_report_identical": "Prueba: Zigosidad de gemelos\nGemelos: {} y {}\nVeredicto: Gemelos idénticos",
        "twins_report_not": "Prueba: Zigosidad de gemelos\nGemelos: {} y {}\nVeredicto: No idénticos",
        "ancestry_report": "Ascendencia de {}\n",
        "login_helix": "🧬",
    },
    "ht": {
        "app_title": "Lojisyèl ADN legal",
        "subtitle": "Patènite · Frè ak sè · Marasa · Zansèt – ak rapò vrejans",
        "built_by": "Konstwi pa Gesner Deslandes",
        "access": "Aksè",
        "password": "Antre modpas sekirite a",
        "unlock": "Dekole laboratwa ADN an",
        "wrong_password": "Kòd aksè pa valab.",
        "main_title": "Analiz ADN reyèl",
        "main_subtitle": "Aksepte alèl STR reyèl – kalkile rapò vrejans legal yo",
        "sidebar_profiles": "Pwofi ki estoke:",
        "sidebar_population": "Baz done frekans popilasyon an",
        "logout": "Dekonekte",
        "tab_register": "📝 Anrejistre pwofi",
        "tab_relationship": "🔬 Patènite & Fanmi",
        "tab_ancestry": "🌍 Zansèt",
        "tab_reports": "📊 Rapò",
        "register_subheader": "Anrejistre yon pwofi ADN (alèl reyèl)",
        "individual_id": "ID moun nan",
        "sample_type": "Kalite echantiyon",
        "sample_blood": "San",
        "sample_saliva": "Saliv",
        "sample_hair": "Cheve",
        "sample_sweat": "Sue",
        "sample_buccal": "Ekouvillon bikal",
        "input_method": "Metòd antre",
        "auto_demo": "Oto‑jenere demonstrasyon",
        "upload_csv": "Chaje CSV (done reyèl)",
        "manual_entry": "Antre manyèl",
        "demo_success": "Pwofi demonstrasyon jenere. Ranplase ak done reyèl pou pwodiksyon.",
        "csv_prompt": "Fòma CSV: Locus,Allele1,Allele2",
        "csv_success": "Pwofi STR reyèl chaje.",
        "save_profile": "💾 Sove pwofi a",
        "save_success": "Pwofi '{}' sove.",
        "need_two_profiles": "Bezwen omwen de pwofi ADN.",
        "test_type": "Kalite tès",
        "paternity_test": "Patènite (Pitit & Papa sipoze)",
        "siblings_test": "Frè ak sè konplè",
        "twins_test": "Marasa idantik",
        "child_label": "Pwofi pitit la",
        "father_label": "Pwofi papa sipoze a",
        "compute_paternity": "Kalkile endèks patènite",
        "cpi_metric": "Endèks patènite konbine (CPI)",
        "log10_cpi": "log₁₀(CPI)",
        "paternity_confirmed": "✅ Patènite konfime (CPI > 10,000)",
        "paternity_excluded": "❌ Eksklizyon – omwen yon locus pa matche",
        "paternity_weak": "⚠️ Prèv fèb (CPI = {:.1f}) – plis loci nesesè",
        "person_a": "Moun A",
        "person_b": "Moun B",
        "compute_sibling": "Kalkile endèks fratènite",
        "lr_metric": "Rapò vrejans (frè/sè vs pa fanmi)",
        "log10_lr": "log₁₀(LR)",
        "sibling_strong": "✅ Gwo sipò pou frè ak sè konplè",
        "sibling_unrelated": "❌ Pa fanmi",
        "sibling_inconclusive": "⚠️ Pa final – fè plis tès sou loci",
        "twin_a": "Marasa A",
        "twin_b": "Marasa B",
        "check_twins": "Tcheke si marasa idantik",
        "identical_twins": "🧬 **Marasa idantik (monozigot)** – tout 13 loci STR yo matche parfe.",
        "fraternal_twins": "Pa idantik – marasa dizigot oswa pa gen rapò.",
        "ancestry_subheader": "Enferans zansèt lè l sèvi avèk frekans popilasyon",
        "select_individual": "Chwazi moun nan",
        "estimate_ancestry": "Estime zansèt yo",
        "ancestry_caption": "Baze sou 13 loci STR – zansèt reyèl itilize dè milye de SNP.",
        "no_profiles": "Pa gen pwofi anrejistre.",
        "report_subheader": "Rapò legal",
        "no_analysis": "Pa gen okenn analiz fè.",
        "download_report": "📄 Telechaje rapò (TXT)",
        "report_date": "RAPÒ ADN LEGAL\nDat: {}\nBaz done popilasyon: {}\n\n",
        "paternity_report": "Tès: Patènite\nPitit: {}\nPapa sipoze: {}\nCPI: {:.2e}\nlog₁₀(CPI): {:.2f}\n",
        "paternity_conclusion_confirmed": "Konklizyon: Patènite konfime",
        "paternity_conclusion_excluded": "Konklizyon: Eksklizyon",
        "paternity_conclusion_inconclusive": "Konklizyon: Pa final",
        "sibling_report": "Tès: Frè ak sè konplè\nMoun: {} ak {}\nLR: {:.2e}\nlog₁₀(LR): {:.2f}\n",
        "sibling_conclusion_strong": "Konklizyon: Gwo sipò pou frè ak sè",
        "sibling_conclusion_unrelated": "Konklizyon: Pa fanmi",
        "sibling_conclusion_inconclusive": "Konklizyon: Pa final",
        "twins_report_identical": "Tès: Zigozite marasa\nMarasa: {} ak {}\nVerdik: Marasa idantik",
        "twins_report_not": "Tès: Zigozite marasa\nMarasa: {} ak {}\nVerdik: Pa idantik",
        "ancestry_report": "Zansèt pou {}\n",
        "login_helix": "🧬",
    }
}

# ---------- Session state ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "profiles" not in st.session_state:
    st.session_state.profiles = {}
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "language" not in st.session_state:
    st.session_state.language = "en"
if "freq_db" not in st.session_state:
    # Full population frequency tables (CODIS 13 loci) – European, African, Asian, Haitian, American
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
        },
        "Haitian": {
            "D3S1358": {"14":0.18, "15":0.32, "16":0.28, "17":0.14, "18":0.08},
            "vWA": {"16":0.22, "17":0.31, "18":0.27, "19":0.14, "20":0.06},
            "FGA": {"20":0.12, "21":0.22, "22":0.28, "23":0.24, "24":0.14},
            "TH01": {"6":0.18, "7":0.28, "8":0.22, "9":0.24, "9.3":0.08},
            "TPOX": {"8":0.22, "9":0.36, "10":0.28, "11":0.14},
            "CSF1PO": {"10":0.24, "11":0.32, "12":0.26, "13":0.14, "14":0.04},
            "D5S818": {"11":0.26, "12":0.34, "13":0.24, "14":0.12, "15":0.04},
            "D7S820": {"8":0.14, "9":0.24, "10":0.32, "11":0.22, "12":0.08},
            "D8S1179": {"12":0.22, "13":0.34, "14":0.26, "15":0.14, "16":0.04},
            "D13S317": {"11":0.24, "12":0.34, "13":0.26, "14":0.12, "15":0.04},
            "D16S539": {"11":0.28, "12":0.34, "13":0.22, "14":0.12, "15":0.04},
            "D18S51": {"13":0.14, "14":0.24, "15":0.30, "16":0.22, "17":0.10},
            "D21S11": {"28":0.18, "29":0.32, "30":0.26, "31":0.14, "32":0.10}
        },
        "American": {
            "D3S1358": {"14":0.22, "15":0.30, "16":0.24, "17":0.16, "18":0.08},
            "vWA": {"16":0.16, "17":0.32, "18":0.30, "19":0.18, "20":0.04},
            "FGA": {"21":0.18, "22":0.26, "23":0.28, "24":0.20, "25":0.08},
            "TH01": {"6":0.14, "7":0.24, "8":0.28, "9":0.26, "9.3":0.08},
            "TPOX": {"8":0.44, "9":0.32, "10":0.18, "11":0.06},
            "CSF1PO": {"10":0.22, "11":0.32, "12":0.28, "13":0.14, "14":0.04},
            "D5S818": {"11":0.24, "12":0.34, "13":0.26, "14":0.12, "15":0.04},
            "D7S820": {"8":0.12, "9":0.22, "10":0.32, "11":0.24, "12":0.10},
            "D8S1179": {"12":0.24, "13":0.32, "14":0.24, "15":0.14, "16":0.06},
            "D13S317": {"11":0.22, "12":0.34, "13":0.26, "14":0.14, "15":0.04},
            "D16S539": {"11":0.24, "12":0.32, "13":0.24, "14":0.14, "15":0.06},
            "D18S51": {"13":0.12, "14":0.22, "15":0.30, "16":0.24, "17":0.12},
            "D21S11": {"28":0.24, "29":0.30, "30":0.24, "31":0.14, "32":0.08}
        }
    }

def t(key, **kwargs):
    """Translation helper."""
    text = translations[st.session_state.language].get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text

# ---------- CSS (animated DNA helix) ----------
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
    st.markdown(f'<div style="text-align:center;"><div class="dna-helix">{t("login_helix")}</div></div>', unsafe_allow_html=True)
    st.title(t("app_title"))
    st.markdown(f"**{t('subtitle')}**")
    st.markdown(t("built_by"))
    st.markdown("---")
    st.markdown(f"### 🔐 {t('access')}")
    password = st.text_input(t("password"), type="password")
    if st.button(t("unlock")):
        if password == "20082010":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error(t("wrong_password"))

# ---------- Main app ----------
def main_app():
    st.title(t("main_title"))
    st.markdown(f"**{t('main_subtitle')}**")
    st.markdown("---")

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2866/2866864.png", width=80)
        # Language selector
        lang = st.selectbox("🌐 Language / Langue / Idioma / Lang", 
                            options=["en", "fr", "es", "ht"],
                            format_func=lambda x: {"en":"English", "fr":"Français", "es":"Español", "ht":"Kreyòl Ayisyen"}[x],
                            index=["en","fr","es","ht"].index(st.session_state.language))
        if lang != st.session_state.language:
            st.session_state.language = lang
            st.rerun()
        st.markdown(f"**{t('sidebar_profiles')}** {len(st.session_state.profiles)}")
        for name in st.session_state.profiles:
            st.write(f"• {name}")
        st.markdown("---")
        pop = st.selectbox(t("sidebar_population"), list(st.session_state.freq_db.keys()), key="pop_selector")
        st.session_state.current_pop = pop
        if st.button(t("logout")):
            st.session_state.authenticated = False
            st.session_state.profiles = {}
            st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs([t("tab_register"), t("tab_relationship"), t("tab_ancestry"), t("tab_reports")])

    with tab1:
        st.subheader(t("register_subheader"))
        name = st.text_input(t("individual_id"))
        sample_type = st.selectbox(t("sample_type"), 
                                   [t("sample_blood"), t("sample_saliva"), t("sample_hair"), t("sample_sweat"), t("sample_buccal")])
        data_source = st.radio(t("input_method"), [t("auto_demo"), t("upload_csv"), t("manual_entry")], horizontal=True)
        markers = None
        if data_source == t("auto_demo") and name:
            markers = generate_random_markers(name)
            st.success(t("demo_success"))
        elif data_source == t("upload_csv") and name:
            uploaded = st.file_uploader(t("csv_prompt"), type=["csv"])
            if uploaded:
                markers = parse_markers_from_csv(uploaded)
                st.success(t("csv_success"))
        elif data_source == t("manual_entry") and name:
            markers = {}
            cols = st.columns(4)
            for i, locus in enumerate(LOCI):
                with cols[i % 4]:
                    a1 = st.number_input(f"{locus} a1", min_value=5, max_value=35, value=16, key=f"{locus}_a1")
                    a2 = st.number_input(f"{locus} a2", min_value=5, max_value=35, value=18, key=f"{locus}_a2")
                    markers[locus] = sorted([a1, a2])
        if markers and name:
            st.dataframe(display_markers_table(markers), use_container_width=True)
        if st.button(t("save_profile"), use_container_width=True) and name and markers:
            st.session_state.profiles[name] = {
                "sample_type": sample_type,
                "markers": markers,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.success(t("save_success", name))

    with tab2:
        st.subheader(t("test_type"))
        if len(st.session_state.profiles) < 2:
            st.info(t("need_two_profiles"))
        else:
            profiles = list(st.session_state.profiles.keys())
            test_type = st.radio(t("test_type"), [t("paternity_test"), t("siblings_test"), t("twins_test")])
            if test_type == t("paternity_test"):
                child = st.selectbox(t("child_label"), profiles)
                father = st.selectbox(t("father_label"), [p for p in profiles if p != child])
                if st.button(t("compute_paternity")):
                    child_m = st.session_state.profiles[child]["markers"]
                    father_m = st.session_state.profiles[father]["markers"]
                    cpi, log10_cpi = paternity_index(child_m, father_m, st.session_state.current_pop)
                    st.session_state.last_result = {"test":"Paternity","child":child,"father":father,"CPI":cpi,"log10_CPI":log10_cpi}
                    st.metric(t("cpi_metric"), f"{cpi:.2e}" if cpi < 1e6 else f"{cpi:.1e}")
                    st.metric(t("log10_cpi"), f"{log10_cpi:.2f}")
                    if cpi >= 10000: st.success(t("paternity_confirmed"))
                    elif cpi == 0: st.error(t("paternity_excluded"))
                    else: st.warning(t("paternity_weak", cpi))
            elif test_type == t("siblings_test"):
                ind1 = st.selectbox(t("person_a"), profiles)
                ind2 = st.selectbox(t("person_b"), [p for p in profiles if p != ind1])
                if st.button(t("compute_sibling")):
                    m1 = st.session_state.profiles[ind1]["markers"]
                    m2 = st.session_state.profiles[ind2]["markers"]
                    lr, log10_lr = sibling_index(m1, m2, st.session_state.current_pop)
                    st.session_state.last_result = {"test":"Siblings","ind1":ind1,"ind2":ind2,"LR":lr,"log10_LR":log10_lr}
                    st.metric(t("lr_metric"), f"{lr:.2e}")
                    st.metric(t("log10_lr"), f"{log10_lr:.2f}")
                    if log10_lr >= 3: st.success(t("sibling_strong"))
                    elif log10_lr <= -3: st.error(t("sibling_unrelated"))
                    else: st.warning(t("sibling_inconclusive"))
            elif test_type == t("twins_test"):
                t1 = st.selectbox(t("twin_a"), profiles)
                t2 = st.selectbox(t("twin_b"), [p for p in profiles if p != t1])
                if st.button(t("check_twins")):
                    m1 = st.session_state.profiles[t1]["markers"]
                    m2 = st.session_state.profiles[t2]["markers"]
                    identical = identical_twins(m1, m2)
                    st.session_state.last_result = {"test":"Twins","twin1":t1,"twin2":t2,"identical":identical}
                    if identical: st.success(t("identical_twins"))
                    else: st.info(t("fraternal_twins"))

    with tab3:
        st.subheader(t("ancestry_subheader"))
        if st.session_state.profiles:
            selected = st.selectbox(t("select_individual"), list(st.session_state.profiles.keys()))
            if st.button(t("estimate_ancestry")):
                markers = st.session_state.profiles[selected]["markers"]
                pops = list(st.session_state.freq_db.keys())
                lls = [ancestry_likelihood(markers, pop) for pop in pops]
                exp_ll = np.exp(lls - np.max(lls))
                probs = exp_ll / exp_ll.sum()
                st.session_state.last_result = {"test":"Ancestry","individual":selected,"probabilities":dict(zip(pops, probs))}
                for pop, prob in zip(pops, probs): st.progress(prob, text=f"{pop}: {prob:.1%}")
                st.caption(t("ancestry_caption"))
        else: st.info(t("no_profiles"))

    with tab4:
        st.subheader(t("report_subheader"))
        if st.session_state.last_result:
            res = st.session_state.last_result
            report = t("report_date", datetime.now(), st.session_state.current_pop)
            if res['test'] == "Paternity":
                report += t("paternity_report", res['child'], res['father'], res['CPI'], res['log10_CPI'])
                if res['CPI'] >= 10000: report += t("paternity_conclusion_confirmed")
                elif res['CPI'] == 0: report += t("paternity_conclusion_excluded")
                else: report += t("paternity_conclusion_inconclusive")
            elif res['test'] == "Siblings":
                report += t("sibling_report", res['ind1'], res['ind2'], res['LR'], res['log10_LR'])
                if res['log10_LR'] >= 3: report += t("sibling_conclusion_strong")
                elif res['log10_LR'] <= -3: report += t("sibling_conclusion_unrelated")
                else: report += t("sibling_conclusion_inconclusive")
            elif res['test'] == "Twins":
                if res['identical']: report += t("twins_report_identical", res['twin1'], res['twin2'])
                else: report += t("twins_report_not", res['twin1'], res['twin2'])
            elif res['test'] == "Ancestry":
                report += t("ancestry_report", res['individual'])
                for pop, prob in res['probabilities'].items():
                    report += f"{pop}: {prob:.1%}\n"
            st.download_button(t("download_report"), report, file_name=f"forensic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        else: st.info(t("no_analysis"))

if not st.session_state.authenticated:
    login()
else:
    main_app()
