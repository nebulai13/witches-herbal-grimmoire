# 🌙 The Witch's Grimmoire 🌙

```
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀
        ⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀
        ⠀⢀⣾⣿⣿⣿⣿⣿ 🌿 ⣿⣿⣿⣿⣿🌿⣿⣿⣿⣿⣿⣷⡀⠀
        ⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀
        ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
        ⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃
        ⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀
        ⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀
        ⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀
        ⠀⠀⠀ ☽ ⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇ ☾ ⠀⠀⠀
```

> *✧･ﾟ: *✧･ﾟ:* A mystical terminal companion for exploring herbal wisdom *:･ﾟ✧*:･ﾟ✧*

A witchy terminal-based REPL for searching traditional medicine databases, brewing knowledge from ancient herbalism and folk remedies. **Now with automatic web search fallback** — when your local grimmoire has no answers, we consult the vast online archives!

## ✨ Quick Summoning

```bash
# Cast the installation spell
./install.sh

# Open the grimmoire
grimmoire

# Or invoke directly (for the impatient witch)
pip install -e .
python -m grimmoire.main
```

## 🔮 Mystical Features

- **🌿 Multi-source Scrying**: Divine knowledge from local databases, PubMed scrolls, and 11+ online sources
- **🌐 Automatic Web Fallback**: No local results? We search online archives automatically!
- **✨ Spell Correction**: Typos are transmuted automatically via fuzzy matching
- **📖 Entity Divination**: Seek plants, ingredients, ailments, and recipes
- **🕸️ Knowledge Gathering**: Scrape wisdom from NAEB, PubChem, and arcane sources
- **⚗️ Background Rituals**: Run long searches in the shadows with journaling
- **🌙 Interrupt Recovery**: Pause and resume rituals with state preservation
- **📚 Source Curation**: Add, enable, or silence sources of wisdom

## 🌙 Installation Rituals

### Quick Summoning (Recommended)

```bash
./install.sh
```

This conjures an isolated realm in `~/.grimmoire/` and grants you the `grimmoire` incantation.

### Apprentice Mode (Development)

```bash
./install.sh dev
# or
pip install -e .
```

### Banishment

```bash
./install.sh uninstall
```

## 📜 Mystical Commands

Start the grimmoire:
```bash
grimmoire
```

### First Ritual (Gathering Wisdom)

```
🌕 grimmoire ⌁ scrape "NAEB Datasette"    # Gather ethnobotany lore (~4500 entries)
🌕 grimmoire ⌁ db stats                    # Count your collected wisdom
```

### Basic Incantations

```bash
# Seek in the grimmoire (auto-searches web if no local results)
search plant chamomile          # Find herbs
search ingredient curcumin      # Find compounds
search ailment headache         # Find cures
find lavender                   # Search all knowledge

# Force include web results
search plant turmeric --web     # Search local + online

# Search online sources directly
websearch curcumin              # Search all online databases
websearch quercetin --provider chembl   # Search specific provider

# Consult modern scrolls
pubmed turmeric
pubmed "diabetes herbal treatment"

# Manage sources of wisdom
sources list
sources disable 5               # Silence a source

# Gather new knowledge (for offline use)
scrape                          # List gathering rituals
scrape "NAEB Datasette"         # Perform ritual
scrape PubChem -b               # Background ritual

# Background rituals
jobs list
jobs resume 1                   # Resume interrupted ritual

# Grimmoire utilities
db stats
db path
```

## 🌐 Online Sources of Wisdom

The grimmoire can consult these online archives:

| Provider | Coverage | Specialty |
|----------|----------|-----------|
| **COCONUT** | 695K compounds | Natural products aggregator |
| **LOTUS** | 750K pairs | Wikidata structure-organism links |
| **ChEMBL** | 2.4M compounds | Bioactivity data |
| **ClinicalTrials.gov** | Clinical trials | Modern research |
| **NAEB** | 45K+ uses | Native American ethnobotany |
| **HERB 2.0** | 7K herbs | TCM clinical evidence |
| **TCMSP** | 29K ingredients | TCM Systems Pharmacology |
| **OSADHI** | 22K compounds | Indian phytochemicals |
| **IMPPAT** | 18K compounds | Indian medicinal plants |
| **MSK** | 250+ herbs | Safety & interactions |
| **Dr. Duke's** | Extensive | USDA phytochemistry |

## 📚 Scrolls of Knowledge

- [User Guide](docs/USER_GUIDE.md) - Complete ritual instructions
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Architecture and extending the magic
- [API Reference](docs/API_REFERENCE.md) - Full spell documentation

## ⚗️ Architecture

```
grimmoire/
├── main.py              # Portal to the grimmoire
├── db/                  # SQLite with FTS5 (the memory)
├── search/              # Scrying + spell correction + PubMed + web providers
│   ├── engine.py        # Local + web fallback search
│   ├── web_provider.py  # 11 online source providers
│   └── pubmed.py        # PubMed E-utilities client
├── scraper/             # Knowledge gatherers (offline)
├── jobs/                # Background rituals with journaling
└── repl/                # The mystical interface
```

## 🕯️ A Session with the Grimmoire

```
╔══════════════════════════════════════════════════════════════════╗
║   ✧･ﾟ: *✧･ﾟ:*  THE WITCH'S GRIMMOIRE  *:･ﾟ✧*:･ﾟ✧                ║
║         ~ Herbal Wisdom & Traditional Medicine Database ~        ║
╚══════════════════════════════════════════════════════════════════╝

📖 Your grimmoire is empty. Gather wisdom with scrape "NAEB Datasette"

🌙 Tip: Search online databases with websearch <query>

🌕 grimmoire ⌁ search plant ashwagandha
Searching online databases...
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Type       ┃ Name               ┃ Source      ┃ Details          ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ plant      │ Ashwagandha        │ IMPPAT      │ Withania somn... │
│ compound   │ Withanolide A      │ COCONUT     │ C28H38O6         │
│ compound   │ Withaferin A       │ ChEMBL      │ CHEMBL65531      │
└────────────┴────────────────────┴─────────────┴──────────────────┘
Found 0 local + 12 online results

🌖 grimmoire ⌁ websearch curcumin --provider chembl
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Type       ┃ Name               ┃ Source      ┃ Details          ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ ingredient │ Curcumin           │ ChEMBL      │ C21H20O6         │
│ ingredient │ Demethoxycurcumin  │ ChEMBL      │ C20H18O5         │
└────────────┴────────────────────┴─────────────┴──────────────────┘

🌗 grimmoire ⌁ quit
✨ May the moon guide your path! 🌙
```

## 🔮 License

MIT - Share the magic freely

---

*"By root and leaf, by moon and sun, may healing wisdom flow to one."* 🌙
# test
