#!/usr/bin/env python3
"""
🌙 The Witch's Grimmoire 🌙
Traditional Medicine & Herbal Wisdom Database

A mystical terminal companion for exploring the ancient knowledge
of medicinal plants, remedies, and traditional healing arts.
"""
import argparse
import sys
from pathlib import Path

from grimmoire.repl.interface import GrimmoireREPL
from grimmoire.db.schema import get_db_path


def main():
    parser = argparse.ArgumentParser(
        description="🌿 The Witch's Grimmoire - Traditional Medicine Search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
✨ Examples:
  grimmoire                    Open the grimmoire
  grimmoire --db custom.db     Use a custom grimmoire
  
🔮 Inside the grimmoire:
  search plant chamomile       Seek herbs
  pubmed "healing herbs"       Consult modern scrolls
  scrape "NAEB Datasette"      Gather ancient wisdom
  help                         Summon guidance
"""
    )
    
    parser.add_argument(
        '--db', 
        type=Path,
        help='Path to grimmoire database (default: ~/.grimmoire/grimmoire.db)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='🌙 The Witch\'s Grimmoire v0.1.0'
    )
    
    args = parser.parse_args()
    
    try:
        repl = GrimmoireREPL(db_path=args.db)
        repl.run()
    except KeyboardInterrupt:
        print("\n✨ The grimmoire closes...")
        sys.exit(0)
    except Exception as e:
        print(f"🔥 A hex upon us: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
