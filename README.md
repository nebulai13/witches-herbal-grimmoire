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

A witchy terminal-based REPL for searching traditional medicine databases, brewing knowledge from ancient herbalism and folk remedies.

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

- **🌿 Multi-source Scrying**: Divine knowledge from local databases and PubMed scrolls
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
# Seek in the grimmoire
search plant chamomile          # Find herbs
search ingredient curcumin      # Find compounds
search ailment headache         # Find cures
find lavender                   # Search all knowledge

# Consult modern scrolls
pubmed turmeric
pubmed "diabetes herbal treatment"

# Manage sources of wisdom
sources list
sources disable 5               # Silence a source

# Gather new knowledge
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

## 📚 Scrolls of Knowledge

- [User Guide](docs/USER_GUIDE.md) - Complete ritual instructions
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Architecture and extending the magic
- [API Reference](docs/API_REFERENCE.md) - Full spell documentation

## ⚗️ Architecture

```
grimmoire/
├── main.py              # Portal to the grimmoire
├── db/                  # SQLite with FTS5 (the memory)
├── search/              # Scrying + spell correction + PubMed
├── scraper/             # Knowledge gatherers
├── jobs/                # Background rituals with journaling
└── repl/                # The mystical interface
```

## 🌿 Sources of Ancient Wisdom

| Source | Type | Knowledge |
|--------|------|-----------|
| NAEB Datasette | API | 45K+ Native American ethnobotany uses |
| PubChem | API | Chemical compound properties |
| PubMed | API | Modern medical scrolls |
| COCONUT | API | 695K+ natural products |
| And more... | | |

## 🕯️ A Session with the Grimmoire

```
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀
        ⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀
        ⠀⢀⣾⣿⣿⣿⣿⣿ 🌿 ⣿⣿⣿⣿⣿🌿⣿⣿⣿⣿⣿⣷⡀⠀
      ☽ ⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇ ☾

╔══════════════════════════════════════════════════════════════════╗
║   ✧･ﾟ: *✧･ﾟ:*  THE WITCH'S GRIMMOIRE  *:･ﾟ✧*:･ﾟ✧                ║
║         ~ Herbal Wisdom & Traditional Medicine Database ~        ║
╚══════════════════════════════════════════════════════════════════╝

📖 Your grimmoire is empty. Gather wisdom with scrape "NAEB Datasette"

🌙 Tip: Divine PubMed secrets with pubmed <query>

🌕 grimmoire ⌁ scrape "NAEB Datasette"
🌿 Gathering from NAEB Datasette...
✓ Gathered 4521 entries of herbal wisdom

🌖 grimmoire ⌁ search plant sage
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Type     ┃ Name               ┃ Details               ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ 🌿 plant │ Sage               │ Salvia officinalis    │
│ 🌿 plant │ White Sage         │ Salvia apiana         │
└──────────┴────────────────────┴───────────────────────┘

🌗 grimmoire ⌁ pubmed "sage antimicrobial"
🔮 Consulting the modern scrolls...
[1] Antimicrobial activity of Salvia officinalis essential oil...

🌘 grimmoire ⌁ quit
✨ May the moon guide your path! 🌙
```

## 🔮 License

MIT - Share the magic freely

---

*"By root and leaf, by moon and sun, may healing wisdom flow to one."* 🌙
