# Traditional & Natural Medicine Super-Database: Source List

> **Purpose:** Extended source list for building a searchable super-database aggregating herbal, traditional, and natural medicine knowledge from all major world traditions.  
> **Generated:** 2026-02-08  
> **Legend:** 🟢 = Open API | 🔵 = Downloadable Data | 🟡 = Web Scraping Required | 🔴 = Subscription/Restricted

---

## 1. MEGA-AGGREGATORS (Start Here — Best ROI)

### 🟢🔵 COCONUT 2.0 — Collection of Open Natural Products
- **URL:** https://coconut.naturalproducts.net
- **Scope:** 695,133 unique natural product structures aggregated from 53+ open databases
- **Access:** REST API (Kotlin-based), bulk download (SDF, CSV), SPARQL
- **API Docs:** https://coconut.naturalproducts.net/documentation
- **License:** Open access
- **Aggregates:** KNApSAcK, CMAUP, NPAtlas, FooDB, NuBBEDB, TCM@Taiwan, AfroDB, SANCDB, NANPDB, StreptomeDB, and 40+ more
- **Key Fields:** Structure (SMILES, InChI), organism source, geographic origin, computed properties (ADMET), NP classification
- **Paper:** DOI: 10.1093/nar/gkae1063 (Nucleic Acids Res, 2025)
- **Priority:** ⭐⭐⭐⭐⭐ — Best single starting point, already aggregates dozens of smaller DBs

### 🟢🔵 LOTUS — Natural Products Occurrence Database
- **URL:** https://lotus.naturalproducts.net / https://lotus.nprod.net
- **Scope:** 750,000+ structure-organism pairs, 250,000+ compounds, 40,000+ taxa
- **Access:** Wikidata SPARQL endpoint, bulk download, REST API
- **Wikidata Integration:** All data mirrored to Wikidata for community curation
- **SPARQL Endpoint:** https://query.wikidata.org (query LOTUS data via Wikidata)
- **License:** CC0 (public domain via Wikidata)
- **Paper:** eLife 2022;11:e70780
- **Priority:** ⭐⭐⭐⭐⭐ — Open, FAIR-compliant, Wikidata-backed, community-curated

### 🟢🔵 PubChem (Natural Products Subset)
- **URL:** https://pubchem.ncbi.nlm.nih.gov
- **Scope:** 110M+ compounds total; filter for natural products via classification
- **API:** PUG-REST (HTTP/REST), PUG-SOAP, PUG-View, PubChemRDF
- **API Base:** `https://pubchem.ncbi.nlm.nih.gov/rest/pug/`
- **Docs:** https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
- **Python:** `pip install pubchempy` or direct requests
- **Rate Limit:** 5 requests/second, no API key needed
- **Example:**
  ```
  GET https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/curcumin/property/MolecularFormula,MolecularWeight,IsomericSMILES/JSON
  ```
- **License:** Public domain
- **Priority:** ⭐⭐⭐⭐⭐ — Foundational chemistry layer for cross-referencing

---

## 2. TRADITIONAL CHINESE MEDICINE (TCM)

### 🟢🔵 HERB 2.0 — High-throughput Experiment & Reference-guided Database
- **URL:** http://herb.ac.cn
- **Scope:** 8,558 clinical trials, 8,032 meta-analyses, 7,263 herbs, 49,258 ingredients, 12,933 targets
- **Access:** Web search interface, downloadable datasets
- **Paper:** DOI: 10.1093/nar/gkae1038 (Nucleic Acids Res, 2025)
- **Key Features:** Links herbs → ingredients → targets → diseases with clinical trial evidence
- **Priority:** ⭐⭐⭐⭐⭐

### 🔵 TCMSP — TCM Systems Pharmacology Database
- **URL:** https://tcmsp-e.com
- **Scope:** 499 herbs, 29,384 ingredients, 3,311 targets, 837 diseases
- **Access:** Web search, network downloads (XGMML format for Cytoscape)
- **License:** Open Database License (ODbL)
- **Key Fields:** OB (oral bioavailability), DL (drug-likeness), BBB, Caco-2, ALogP
- **Paper:** J Cheminformatics 2014;6(1):13
- **Priority:** ⭐⭐⭐⭐

### 🔵 TCMBank — Largest Downloadable TCM Database
- **URL:** https://tcmbank.cn
- **Scope:** 9,192 herbs, 61,966 ingredients, 15,179 targets, 32,529 diseases
- **Access:** Bulk download (free, non-commercial), web search
- **Key Features:** 3D structures in mol2, cross-refs to DrugBank/PubChem/MeSH, deep learning DDI predictions
- **Paper:** Signal Transduction and Targeted Therapy, 2023
- **Priority:** ⭐⭐⭐⭐⭐

### 🔵 ETCM v2.0 — Encyclopedia of Traditional Chinese Medicine
- **URL:** http://www.tcmip.cn/ETCM2/front/#/
- **Scope:** 48,442 TCM formulas, 9,872 Chinese patent drugs, 2,079 medicinal materials, 38,298 ingredients
- **Access:** Web interface, network visualization tool
- **Paper:** Acta Pharmaceutica Sinica B, 2023
- **Priority:** ⭐⭐⭐⭐

### 🔵 LTM-TCM — Linking Traditional & Modern Medicine
- **URL:** http://cloud.tasly.com/#/tcm/home
- **Scope:** 1,928 symptoms, 48,126 prescriptions, 9,122 plants, 34,967 ingredients, 13,109 targets
- **Access:** Web (Chinese + English), data available upon request
- **Key Features:** 41,025 manually collected clinical records, 213 ancient Chinese medical books
- **Paper:** Pharmacological Research, 2022
- **Priority:** ⭐⭐⭐⭐

### 🔵 TCMID 2.0 — TCM Integrative Database
- **URL:** http://www.megabionet.org/tcmid/ and https://www.bidd.group/TCMID/
- **Scope:** 47,000 prescriptions, 8,159 herbs, 25,210 compounds, 17,521 targets
- **Access:** Web search, linked to DrugBank/OMIM/PubChem
- **License:** CC BY-NC 3.0
- **Priority:** ⭐⭐⭐

### 🔵 TCM Database@Taiwan
- **URL:** http://tcm.cmu.edu.tw
- **Scope:** 61,000+ compounds from 453 TCM herbs (largest 3D structure collection for TCM)
- **Access:** Free download for virtual screening (mol2 format)
- **Priority:** ⭐⭐⭐

### 🔵 YaTCM — Yet Another TCM Database
- **URL:** http://cadd.pharmacy.nankai.edu.cn/yatcm/home
- **Scope:** Herbs, ingredients, targets, pathways, diseases
- **Access:** Web toolkit with similarity search, pathway analysis, network pharmacology
- **Priority:** ⭐⭐⭐

### 🟡 SymMap — Symptom Mapping for TCM
- **URL:** http://www.symmap.org
- **Scope:** Maps TCM symptoms → herbs → ingredients → modern disease targets
- **Access:** Web interface
- **Priority:** ⭐⭐⭐

---

## 3. AYURVEDA / INDIAN TRADITIONAL MEDICINE (AYUSH)

### 🔵 OSADHI — Online Structural & Analytics Database for Herbs of India
- **URL:** https://neist.res.in/osadhi/index.html
- **Scope:** 22,314 phytochemicals from Indian medicinal plants
- **Access:** Web search, downloadable data
- **Key Fields:** 2D structures, physicochemical properties, drug-likeness scores, ADMET predictions, NP classification
- **Key Features:** Cross-cultural study across all Indian states/UTs, machine learning classification by therapeutic use
- **Priority:** ⭐⭐⭐⭐⭐

### 🔵 IMPPAT 2.0 — Indian Medicinal Plants, Phytochemistry & Therapeutics
- **URL:** https://cb.imsc.res.in/imppat/
- **Scope:** 4,010 Indian medicinal plants, 17,967 phytochemicals, 1,095 therapeutic uses, 1,133 traditional formulations
- **Access:** Web search, downloadable datasets
- **Key Features:** Manually curated, comparative analysis with other chemical libraries
- **Priority:** ⭐⭐⭐⭐⭐

### 🔵 Ayurvedic Pharmacopoeia of India (API)
- **URL:** https://www.ayurveda.hu/api/API-Vol-1.pdf (Volume 1)
- **All Volumes:** https://dravyagunatvpm.wordpress.com/e-ayupharmacopoeia-of-india/
- **Scope:** Official monographs for Ayurvedic medicinal plants (Rasa, Guna, Virya, Vipaka, Karma, formulations, therapeutic uses)
- **Access:** PDF download (all volumes freely available)
- **Priority:** ⭐⭐⭐⭐ — Official government reference, ideal for OCR/parsing into structured data

### 🔴 TKDL — Traditional Knowledge Digital Library
- **URL:** https://www.tkdl.res.in
- **Scope:** Ayurveda, Unani, Siddha, Sowa-Rigpa formulations (representative database)
- **Access:** Restricted — only patent offices under TKDL Access Agreement
- **Note:** Can be used as reference for what categories/formulations exist; actual data requires formal access
- **Priority:** ⭐⭐ (access barrier)

### 🔵 AYUSH Research Guidelines & Databases
- **URL:** https://www.ayushcoe.in/database.php
- **Scope:** Network pharmacology resources, herb-drug interaction data for AYUSH systems
- **Access:** Web reference, compilable datasets in Excel
- **Priority:** ⭐⭐⭐

### 🔵 Kaggle — Indian Medicine Data
- **URL:** https://www.kaggle.com/datasets/mohneesh7/indian-medicine-data
- **Scope:** Allopathic + Ayurvedic medicines in India
- **Access:** CSV/JSON download
- **Priority:** ⭐⭐

### 🔵 GitHub — Indian Medicine Dataset
- **URL:** https://github.com/junioralive/Indian-Medicine-Dataset
- **Scope:** Indian medicines organized by brand with composition data
- **Access:** JSON/CSV, MongoDB API example included
- **Priority:** ⭐⭐

---

## 4. NATIVE AMERICAN / FIRST NATIONS ETHNOBOTANY

### 🟢🔵 NAEB — Native American Ethnobotany Database (Moerman)
- **Official:** http://naeb.brit.org (BRIT — Botanical Research Institute of Texas)
- **Open Mirror with API:** https://naeb.louispotok.com (Datasette-powered, full SQL query + download)
- **Scope:** 45,000+ uses of 4,000+ plant species by 291 Native American tribes, from 200+ sources
- **Access (mirror):** Full SQL queries via Datasette, bulk download, JSON API
- **Tables:** `uses`, `species`, `tribes`, `use_categories`, `use_subcategories`, `sources`
- **Bibliography:** Full BibTeX available for download
- **Original Author:** Daniel Moerman (book: "Native American Ethnobotany")
- **Priority:** ⭐⭐⭐⭐⭐ — The definitive resource, and the Datasette mirror is perfectly API-ready

### 🟡 Prairie Ethnobotany Database (U. Kansas)
- **URL:** https://nativeplants.ku.edu/ethnobotany-database
- **Scope:** 1,600+ unique species, 338 tribes, focused on Great Plains
- **Access:** Web search interface
- **Priority:** ⭐⭐⭐

### 🟡 Great Lakes Anishinaabe Ethnobotany
- **URL:** Via Cedar Tree Institute / NMU Center for Native American Studies
- **Scope:** Video interviews, personal stories, cultural teachings for Upper Great Lakes plants
- **Access:** Web browsing
- **Priority:** ⭐⭐ (qualitative/cultural, less structured)

### 🟡 USDA PLANTS Database
- **URL:** https://plants.usda.gov
- **Scope:** All vascular plants, mosses, lichens of US territories (includes ethnobotanical notes)
- **Access:** Web search, some download capability
- **Priority:** ⭐⭐⭐ — Useful for taxonomic cross-referencing

---

## 5. GENERAL PHYTOCHEMISTRY & ETHNOBOTANY

### 🟢🔵 Dr. Duke's Phytochemical & Ethnobotanical Databases (USDA)
- **URL:** https://phytochem.nal.usda.gov/
- **Scope:** Phytochemicals, bioactivities, and ethnobotanical uses — searchable by plant or chemical
- **Access:** Web search, results downloadable as PDF/spreadsheet
- **Key Features:** Links plants → chemicals → bioactivities, multiple search modes
- **Priority:** ⭐⭐⭐⭐⭐ — Classic USDA resource, highly structured

### 🔵 KNApSAcK — Comprehensive Species-Metabolite Relations
- **URL:** http://www.knapsackfamily.com/knapsack_core/top.php
- **Scope:** 50,000+ structures, 100,000+ structure-organism pairs
- **Access:** Web search, some download capability
- **Key Features:** First major public resource of referenced structure-organism NP pairs
- **Priority:** ⭐⭐⭐⭐

### 🔵 CMAUP 2.0 — Collective Molecular Activities of Useful Plants
- **URL:** http://www.bidd.group/CMAUP/
- **Scope:** 5,645 plants from 153 countries, multi-target activity landscapes
- **Access:** Web interface, downloadable data
- **Key Fields:** Target heatmaps, gene ontologies, biological pathways, diseases
- **Paper:** Nucleic Acids Res 2019;47:D1118-D1127
- **Priority:** ⭐⭐⭐⭐

### 🔵 NPAtlas 2.0 — Natural Products Atlas (Microbial)
- **URL:** https://www.npatlas.org
- **Scope:** 33,000+ microbial natural products (bacteria, fungi)
- **Access:** Bulk download (SDF, TSV), REST API
- **API:** https://www.npatlas.org/api/v1/
- **Priority:** ⭐⭐⭐⭐

### 🔵 FooDB — Food Component Database
- **URL:** https://foodb.ca
- **Scope:** 70,926 food components (nutrients, phytochemicals) in 892 foods
- **Access:** Web search, CSV/SDF download
- **Priority:** ⭐⭐⭐

### 🟡 NAPRALERT — Natural Products Alert
- **URL:** https://napralert.org (University of Illinois at Chicago)
- **Scope:** 200,000+ primary literature sources, 900,000+ structure-organism pairs compiled over 5 decades
- **Access:** Subscription-based, some free queries
- **Priority:** ⭐⭐⭐ (access barrier but massive scope)

### 🟢 ChEMBL
- **URL:** https://www.ebi.ac.uk/chembl/
- **API:** REST API at https://www.ebi.ac.uk/chembl/api/data/
- **Scope:** 2.4M+ compounds, 15M+ bioactivities (includes many NPs)
- **Access:** Open, REST API, bulk download (PostgreSQL dump, SDF)
- **Python:** `pip install chembl_webresource_client`
- **Priority:** ⭐⭐⭐⭐ — Essential for bioactivity data cross-referencing

### 🟢 ChEBI — Chemical Entities of Biological Interest
- **URL:** https://www.ebi.ac.uk/chebi/
- **API:** REST + SPARQL
- **Scope:** Curated chemical ontology with NP annotations
- **Priority:** ⭐⭐⭐

---

## 6. AFRICAN TRADITIONAL MEDICINE

### 🔵 SANCDB — South African Natural Compounds Database
- **URL:** https://sancdb.rubi.ru.ac.za
- **Scope:** 1,000+ compounds from South African biodiversity
- **Access:** Web search, SDF download
- **Priority:** ⭐⭐⭐⭐

### 🔵 NANPDB — Northern African Natural Products Database
- **URL:** Part of COCONUT aggregation
- **Scope:** Natural products from Northern African sources
- **Access:** Via COCONUT bulk download
- **Priority:** ⭐⭐⭐

### 🔵 AfroDB — African Medicinal Plants Database
- **URL:** Part of COCONUT aggregation
- **Scope:** Compounds from African medicinal plants
- **Access:** Via COCONUT bulk download
- **Priority:** ⭐⭐⭐

### 🟡 TRAMED III (South Africa)
- **URL:** Developed by MRC + University of Cape Town
- **Scope:** Research compilation on South African traditional medicine
- **Access:** Web interface (may be intermittent)
- **Priority:** ⭐⭐

---

## 7. CLINICAL EVIDENCE & SAFETY DATABASES

### 🟢 PubMed / MEDLINE (NCBI)
- **URL:** https://pubmed.ncbi.nlm.nih.gov
- **API:** E-utilities (Entrez)
- **Base URL:** `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
- **Key Endpoints:** `esearch.fcgi` (search), `efetch.fcgi` (retrieve), `elink.fcgi` (cross-ref)
- **MeSH Terms for herbs:** "Plants, Medicinal", "Herbal Medicine", "Drugs, Chinese Herbal", "Medicine, Ayurvedic", "Medicine, African Traditional"
- **Rate Limit:** 3/sec without API key, 10/sec with (free key from NCBI)
- **Priority:** ⭐⭐⭐⭐⭐ — Essential for clinical evidence layer

### 🟢 ClinicalTrials.gov
- **URL:** https://clinicaltrials.gov
- **API:** REST API v2: `https://clinicaltrials.gov/api/v2/studies`
- **Docs:** https://clinicaltrials.gov/data-api/api
- **Scope:** Search for trials involving herbs, TCM formulas, Ayurvedic treatments
- **Priority:** ⭐⭐⭐⭐

### 🔴 NatMed Pro (formerly Natural Medicines Comprehensive Database)
- **URL:** https://naturalmedicines.therapeuticresearch.com
- **Scope:** Evidence-based monographs on dietary supplements, NPs, CAM therapies
- **Access:** Subscription only (institutional or individual)
- **Key Features:** Effectiveness ratings, safety ratings, drug interactions, dosing
- **Priority:** ⭐⭐⭐ (authoritative but paywalled)

### 🟡 Memorial Sloan Kettering — About Herbs
- **URL:** https://www.mskcc.org/cancer-care/diagnosis-treatment/symptom-management/integrative-medicine/herbs
- **Scope:** 250+ herbs/supplements with mechanism, adverse effects, interactions
- **Access:** Free web, structured enough for scraping
- **Priority:** ⭐⭐⭐⭐

### 🟡 MedlinePlus — Drugs, Herbs & Supplements
- **URL:** https://medlineplus.gov/druginfo/herb_All.html
- **API:** MedlinePlus Connect API (limited)
- **Scope:** Consumer-level herb/supplement information from NIH
- **Priority:** ⭐⭐⭐

---

## 8. NATURAL REMEDIES OF NON-PLANT ORIGIN

### Clay, Mineral & Apitherapy Sources

These are less database-oriented — more literature-based:

- **Medicinal Clays:** Search PubMed for "medicinal clay", "kaolin therapeutic", "bentonite medicinal", "pelotherapy"
- **Apitherapy (bee products):** Search for "propolis", "royal jelly", "bee venom therapy" in PubChem/PubMed
- **Peloid/Mud therapy:** European Spa Research (ESPA) publications
- **Mineral waters:** WHO "Guidelines for drinking-water quality" + European pharmacopoeia monographs

### 🔵 ZINC Database — Natural Products Subset
- **URL:** https://zinc.docking.org
- **Scope:** 80,000+ NP entries (purchasable), 230M+ total compounds
- **Access:** Bulk download (SDF, SMILES), REST API
- **Priority:** ⭐⭐⭐ (for structural searching of mineral/non-plant compounds too)

---

## 9. BOTANICAL / TAXONOMIC REFERENCE DATABASES

### 🟢 GBIF — Global Biodiversity Information Facility
- **URL:** https://www.gbif.org
- **API:** REST API at https://api.gbif.org/v1/
- **Scope:** Occurrence records for all species globally — cross-reference medicinal plant distributions
- **Priority:** ⭐⭐⭐⭐

### 🟢 NCBI Taxonomy
- **URL:** https://www.ncbi.nlm.nih.gov/taxonomy
- **API:** E-utilities
- **Scope:** Standardized taxonomic identifiers — essential for organism normalization
- **Priority:** ⭐⭐⭐⭐⭐

### 🟡 The Plant List / World Flora Online
- **URL:** http://www.worldfloraonline.org
- **Scope:** Accepted plant names and synonyms — crucial for name disambiguation
- **Access:** Bulk download available
- **Priority:** ⭐⭐⭐⭐

### 🟢 Wikidata
- **URL:** https://www.wikidata.org
- **API:** REST API + SPARQL endpoint (https://query.wikidata.org)
- **Scope:** Structured data for plants, compounds, diseases — LOTUS data lives here
- **Priority:** ⭐⭐⭐⭐⭐ — Central knowledge graph for linking everything

---

## 10. DATASETS ON GITHUB / KAGGLE

| Source | URL | Format | Scope |
|--------|-----|--------|-------|
| COCONUT dumps | https://coconut.naturalproducts.net/download | SDF, CSV | 695K NPs |
| LOTUS on Zenodo | https://zenodo.org/communities/lotus | TSV | 750K pairs |
| TCMBank download | https://tcmbank.cn/download | Various | 62K ingredients |
| Indian Medicine Dataset | github.com/junioralive/Indian-Medicine-Dataset | JSON, CSV | Indian meds |
| Indian Medicine (Kaggle) | kaggle.com/datasets/mohneesh7/indian-medicine-data | CSV | Ayurvedic/Allopathic |
| NAEB mirror (Datasette) | naeb.louispotok.com | SQLite, JSON API | 45K ethnobotanical uses |
| PubChem API wrapper | github.com/XavierJiezou/python-pubchem-api | Python | Crawling tool |

---

## 11. ARCHITECTURE RECOMMENDATIONS

### Suggested Data Model (Core Entities)

```
PLANT/ORGANISM ──→ COMPOUND/INGREDIENT ──→ TARGET/PROTEIN ──→ DISEASE/CONDITION
     │                    │                       │                    │
     └── Taxonomy         └── Structure           └── Pathway          └── ICD-10/MeSH
     └── Geography        └── Properties          └── Gene Ontology    └── TCM Symptom
     └── Tradition        └── Bioactivity         └── Mechanism        └── Ayurveda Dosha
```

### Recommended Crawl/Ingest Priority

1. **COCONUT 2.0** — bulk download, covers 53 sub-databases in one shot
2. **LOTUS/Wikidata** — SPARQL for structure-organism pairs
3. **PubChem** — REST API for compound details + bioactivities
4. **NAEB Datasette** — JSON API for ethnobotanical uses
5. **HERB 2.0 + TCMBank** — TCM-specific clinical evidence
6. **OSADHI + IMPPAT** — Ayurvedic phytochemistry
7. **Dr. Duke's** — Ethnobotanical use-activity links
8. **ChEMBL** — Bioactivity data for cross-referencing
9. **PubMed** — Clinical evidence abstracts
10. **ClinicalTrials.gov** — Ongoing/completed trial data

### Key Identifiers for Linking

| Entity | Standard ID |
|--------|------------|
| Compounds | InChIKey, PubChem CID, SMILES |
| Organisms | NCBI Taxonomy ID, GBIF ID |
| Diseases | MeSH, ICD-10, DO (Disease Ontology) |
| Targets/Proteins | UniProt ID, Gene Symbol |
| Literature | PubMed ID (PMID), DOI |

### Tech Stack Suggestions

- **Ingestion:** Python (requests, BeautifulSoup, RDKit for chemistry)
- **Storage:** PostgreSQL + ChemicalStructure extension (RDKit cartridge) or MongoDB for flexible schema
- **Search:** Elasticsearch for text, RDKit for substructure/similarity search
- **API:** FastAPI or Flask for your own REST endpoints
- **Normalization:** Use InChIKey as the universal compound key; NCBI TaxID for organisms

---

## 12. ADDITIONAL NICHE SOURCES

| Database | Tradition | URL | Notes |
|----------|-----------|-----|-------|
| HerbMed Pro | Western Herbal | herbmed.org | Fee-based, 207 herbs |
| CABI (Herbs & Spices) | Global | cabi.org | Subscription DB |
| Seaweed Metabolite DB | Marine | In COCONUT | Seaweed compounds |
| StreptomeDB | Microbial | In COCONUT | Streptomyces NPs |
| SuperNatural 3 | Global NPs | In COCONUT | Purchasable NPs |
| NuBBEDB | Brazilian | In COCONUT | Brazilian biodiversity |
| BIOFACQUIM | Mexican | In COCONUT | Mexican NPs |
| TIPdb | Taiwanese | In COCONUT | Taiwanese NPs |
| InPACdb | Indian | In COCONUT | Indian anti-cancer NPs |
| Carotenoids DB | Carotenoids | In COCONUT | Specialized |
| HIT (Herbal Ingredients' Targets) | TCM | lifecenter.sgst.cn/hit/ | 586 ingredients, 1301 targets |
| TCMAnalyzer | TCM | tcmanalyzer.com | Scaffold-activity analysis |
| NPASS | NPs | In COCONUT | Activity & species source |
| Exposome-Explorer | Diet/Environment | In COCONUT | Dietary biomarkers |
| European Pharmacopoeia | European Herbal | edqm.eu | Official monographs (paid) |
| German Commission E | German Herbal | Via AHCC | Historical monographs |
| WHO Monographs on Medicinal Plants | Global | WHO publications | PDF volumes (scrapeable) |
| Kampo (Japanese) | Japanese TCM | Various academic DBs | Search PubMed for "Kampo database" |
| Jamu (Indonesian) | Indonesian TM | Various | Limited digital presence |
| Unani Medicine | Greco-Arabic | Via TKDL/AYUSH | Part of Indian AYUSH system |
| Siddha Medicine | South Indian | Via TKDL/AYUSH | Tamil tradition |

---

## 13. USEFUL TOOLS & LIBRARIES

| Tool | Purpose | URL |
|------|---------|-----|
| RDKit | Cheminformatics (SMILES, InChI, fingerprints) | rdkit.org |
| pubchempy | Python PubChem API wrapper | pypi.org/project/PubChemPy |
| chembl_webresource_client | Python ChEMBL API | pypi.org/project/chembl-webresource-client |
| Biopython Entrez | PubMed/NCBI API wrapper | biopython.org |
| Datasette | Instant JSON API from SQLite | datasette.io |
| Cytoscape | Network visualization | cytoscape.org |
| Open Babel | Chemical format conversion | openbabel.org |

---

*This document is a living reference. Many databases update annually. Always check for the latest version before bulk ingestion.*
