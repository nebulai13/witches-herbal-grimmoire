# Grimmoire User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Searching](#searching)
3. [Data Sources](#data-sources)
4. [Scraping Data](#scraping-data)
5. [Background Jobs](#background-jobs)
6. [Database Management](#database-management)
7. [Tips & Tricks](#tips--tricks)

---

## Getting Started

### Installation

```bash
# Quick install
./install.sh

# Or development mode
./install.sh dev

# Or manually with pip
pip install -e .
```

### Starting the REPL

```bash
grimmoire
# or
python -m grimmoire.main
```

You'll see:
```
╔═══════════════════════════════════════════════════════════════╗
║   🌿  GRIMMOIRE  🌿                                           ║
║   Traditional Medicine & Ingredients Search                   ║
╚═══════════════════════════════════════════════════════════════╝

Database is empty. Run 'scrape NAEB Datasette' to get started.

🌿 grimmoire>
```

### First Steps

1. **Populate the database** with data from NAEB (Native American Ethnobotany):
   ```
   scrape "NAEB Datasette"
   ```

2. **Search for plants**:
   ```
   search plant sage
   ```

3. **Search PubMed** for research:
   ```
   pubmed "sage antimicrobial"
   ```

---

## Searching

### Search Types

| Type | Description | Example |
|------|-------------|---------|
| `plant` | Medicinal plants | `search plant echinacea` |
| `ingredient` | Compounds, chemicals | `search ingredient curcumin` |
| `ailment` | Diseases, conditions | `search ailment headache` |
| `recipe` | Formulations, preparations | `search recipe tea` |
| `all` | Search everything | `search all lavender` |

### Quick Search

Use `find` for a quick search across all types:
```
find chamomile
```

### PubMed Search

Search medical literature:
```
pubmed turmeric
pubmed "diabetes treatment herbs"
pubmed "Salvia officinalis"
```

### Spell Correction

Grimmoire automatically corrects misspellings:
```
🌿 grimmoire> search plant chamomil
Did you mean: chamomile?
```

The correction uses fuzzy matching from your local database vocabulary.

### Search Examples

```bash
# Find all plants in the mint family
search plant mint

# Find compounds with anti-inflammatory properties
search ingredient anti-inflammatory

# Find traditional remedies for sleep
search ailment sleep

# Quick search for any mention of ginger
find ginger

# Research articles on elderberry
pubmed elderberry immune
```

---

## Data Sources

### Viewing Sources

```
sources list
```

Output:
```
                              Data Sources                              
┏━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID   ┃ Name           ┃ Type     ┃ Status     ┃ Last Scraped         ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ 1    │ NAEB Datasette │ api      │ Enabled    │ 2024-01-15 10:30:00  │
│ 2    │ PubChem        │ api      │ Enabled    │ Never                │
│ 3    │ PubMed         │ api      │ Enabled    │ Never                │
...
```

### Built-in Sources

| Source | Type | Description |
|--------|------|-------------|
| NAEB Datasette | API | Native American Ethnobotany (45K+ uses) |
| PubChem | API | Chemical compound properties |
| PubMed | API | Medical research literature |
| COCONUT | API | 695K+ natural products |
| Dr. Duke's | Scrape | USDA phytochemical database |
| HERB 2.0 | Scrape | TCM clinical trials & herbs |
| TCMBank | Bulk | TCM ingredients & targets |
| OSADHI | Scrape | Indian medicinal plants |
| IMPPAT | Scrape | Indian phytochemistry |
| MSK Herbs | Scrape | Memorial Sloan Kettering herb info |

### Adding a Source

```
sources add "My Database" "https://example.com/api"
```

### Enabling/Disabling Sources

```bash
# Disable a source (exclude from searches)
sources disable 5

# Re-enable a source
sources enable 5
```

---

## Scraping Data

### List Available Scrapers

```
scrape
```

Output:
```
Available scrapers:
  • NAEB Datasette
  • PubChem
```

### Running a Scrape

```bash
# Scrape NAEB (Native American Ethnobotany)
scrape "NAEB Datasette"

# Scrape PubChem compound data
scrape PubChem
```

Progress is displayed:
```
Scraping NAEB Datasette: 2500 items ━━━━━━━━━━━━━━━━━━━ 55%
```

### Background Scraping

For long-running scrapes, use background mode:
```
scrape "NAEB Datasette" -b
```

Output:
```
Started background scrape job 1
```

### Interrupting a Scrape

Press `Ctrl+C` to interrupt. The job is paused and can be resumed:
```
^C
Interrupted. Use 'quit' to exit.
```

---

## Background Jobs

### List Jobs

```
jobs list
```

Output:
```
                              Jobs                              
┏━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ ID   ┃ Type     ┃ Status     ┃ Results  ┃ Created             ┃
┡━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ 1    │ scrape   │ paused     │ 2500     │ 2024-01-15 10:30:00 │
│ 2    │ scrape   │ completed  │ 4521     │ 2024-01-14 15:20:00 │
└──────┴──────────┴────────────┴──────────┴─────────────────────┘
```

### Job Status

```
jobs status 1
```

Shows detailed status with journal entries:
```
╭─────────────── Job Status ───────────────╮
│ Job ID: 1                                │
│ Type: scrape                             │
│ Status: paused                           │
│ Results: 2500                            │
│ Duration: 0:05:30                        │
│ Interrupts: 1                            │
│ Resumes: 0                               │
╰──────────────────────────────────────────╯
```

### Resume a Job

```
jobs resume 1
```

The job continues from where it left off.

### Stop Current Job

```
jobs stop
```

---

## Database Management

### Database Statistics

```
db stats
```

Output:
```
  Database Statistics  
┏━━━━━━━━━━━━━┳━━━━━━━┓
┃ Entity      ┃ Count ┃
┡━━━━━━━━━━━━━╇━━━━━━━┩
│ Plants      │  4521 │
│ Ingredients │   125 │
│ Ailments    │  8932 │
│ Recipes     │     0 │
│ Sources     │    10 │
│ Jobs        │     2 │
└─────────────┴───────┘
```

### Database Location

```
db path
```

Output:
```
Database path: /Users/you/.grimmoire/grimmoire.db
```

### Database Schema

The SQLite database includes:

- **plants**: name, scientific_name, family, common_names, taxonomy_id
- **ingredients**: name, synonyms, pubchem_cid, inchi_key, smiles, molecular_formula
- **ailments**: name, synonyms, icd10_code, mesh_id, category
- **recipes**: name, tradition, description, preparation, dosage
- **sources**: name, url, type, priority, enabled, last_scraped
- **jobs**: type, status, progress, results_count
- **journal**: event_type, event_data, timestamps

Full-text search (FTS5) is enabled on all main tables.

---

## Tips & Tricks

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Autocomplete commands and search terms |
| `↑/↓` | Navigate command history |
| `Ctrl+C` | Interrupt current operation |
| `Ctrl+D` | Exit REPL |

### Autocomplete

Press `Tab` for suggestions:
```
🌿 grimmoire> search pl[TAB]
plant
🌿 grimmoire> search plant cham[TAB]
chamomile
```

### Command History

Your command history is saved to `~/.grimmoire/history.txt`.

### Using with Scripts

Pipe commands to Grimmoire:
```bash
echo "search plant sage" | python -m grimmoire.main
```

### Combining Searches

Search locally first, then expand to PubMed:
```
search plant turmeric
pubmed "turmeric Curcuma longa"
```

### Backup Your Database

```bash
cp ~/.grimmoire/grimmoire.db ~/.grimmoire/grimmoire.db.backup
```

---

## Troubleshooting

### "No results found"

1. Check if database is populated: `db stats`
2. If empty, run a scrape: `scrape "NAEB Datasette"`
3. Try broader search terms
4. Check for spelling suggestions

### Scrape Interrupted

Use `jobs list` to find paused jobs, then `jobs resume <id>`.

### Slow Searches

The first search after startup builds the spell-check dictionary. Subsequent searches are faster.

### PubMed Rate Limiting

PubMed allows 3 requests/second without an API key. For heavy use, get a free NCBI API key and set:
```python
pubmed = PubMedClient(api_key="your_key")
```
