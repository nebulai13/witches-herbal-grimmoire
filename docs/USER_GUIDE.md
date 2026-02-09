# Grimmoire User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Searching](#searching)
3. [Web Search](#web-search)
4. [Data Sources](#data-sources)
5. [Scraping Data](#scraping-data)
6. [Background Jobs](#background-jobs)
7. [Database Management](#database-management)
8. [Tips & Tricks](#tips--tricks)

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

1. **Search online** (works immediately, no setup needed):
   ```
   websearch curcumin
   ```

2. **Or populate the database** with data from NAEB (Native American Ethnobotany):
   ```
   scrape "NAEB Datasette"
   ```

3. **Search for plants** (searches local, falls back to web if empty):
   ```
   search plant sage
   ```

4. **Search PubMed** for research:
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

### Web Fallback

When local search returns no results, Grimmoire **automatically searches online databases**:
```
🌿 grimmoire> search plant ashwagandha
Searching online databases...
Found 0 local + 8 online results
```

### Force Web Search

Add `--web` to always include online results:
```
search plant turmeric --web
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

# Force include online results
search ingredient quercetin --web
```

---

## Web Search

### Direct Web Search

Use `websearch` to search online databases directly (bypasses local DB):

```bash
# Search all online providers
websearch curcumin

# Search a specific provider
websearch quercetin --provider chembl
websearch ashwagandha --provider imppat
```

### List Available Providers

```
websearch
```

Output:
```
Available web search providers:
  • coconut - COCONUT
  • lotus - LOTUS
  • chembl - ChEMBL
  • clinicaltrials - ClinicalTrials.gov
  • naeb - NAEB
  • herb2 - HERB 2.0
  • tcmsp - TCMSP
  • osadhi - OSADHI
  • imppat - IMPPAT
  • msk - MSK About Herbs
  • dukes - Dr. Duke's
```

### Online Providers Reference

| Provider | Coverage | Best For |
|----------|----------|----------|
| **coconut** | 695K compounds | Natural products, structures |
| **lotus** | 750K structure-organism pairs | Wikidata-linked compound data |
| **chembl** | 2.4M compounds | Bioactivity, drug-likeness |
| **clinicaltrials** | Ongoing trials | Clinical evidence |
| **naeb** | 45K+ uses | Native American ethnobotany |
| **herb2** | 7K herbs, 49K ingredients | TCM with clinical trials |
| **tcmsp** | 499 herbs, 29K ingredients | TCM pharmacology |
| **osadhi** | 22K phytochemicals | Indian medicinal plants |
| **imppat** | 4K plants, 18K compounds | Ayurvedic medicine |
| **msk** | 250+ herbs | Safety, interactions, oncology |
| **dukes** | Extensive | USDA phytochemistry |

### Web Search Examples

```bash
# Find natural products containing a compound
websearch berberine

# Find TCM herbs for a condition
websearch "liver" --provider herb2

# Find clinical trials for a plant
websearch "turmeric" --provider clinicaltrials

# Find Ayurvedic information
websearch "ashwagandha" --provider imppat

# Check herb safety/interactions
websearch "St. John's Wort" --provider msk
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

1. **Web search is automatic** — if local DB is empty, we search online automatically
2. Try `websearch <query>` to search online databases directly
3. Check if database is populated: `db stats`
4. If you want local data, run a scrape: `scrape "NAEB Datasette"`
5. Try broader search terms
6. Check for spelling suggestions

### Web Search Not Working

1. Check your internet connection
2. Some providers may be temporarily unavailable
3. Try a different provider: `websearch <query> --provider coconut`
4. Rate limits may apply — wait a moment and retry

### Scrape Interrupted

Use `jobs list` to find paused jobs, then `jobs resume <id>`.

### Slow Searches

The first search after startup builds the spell-check dictionary. Subsequent searches are faster.

### Web vs Local Search

| Scenario | Behavior |
|----------|----------|
| Local DB has results | Returns local results only |
| Local DB empty | Automatically searches online |
| `--web` flag used | Returns local + online results |
| `websearch` command | Searches only online sources |

### PubMed Rate Limiting

PubMed allows 3 requests/second without an API key. For heavy use, get a free NCBI API key and set:
```python
pubmed = PubMedClient(api_key="your_key")
```

### Online Provider Rate Limits

| Provider | Rate Limit |
|----------|------------|
| PubChem | 5 req/sec |
| PubMed | 3-10 req/sec |
| ChEMBL | 3 req/sec |
| COCONUT | 2 req/sec |
| Others | 1 req/sec |

The grimmoire automatically respects these limits.
