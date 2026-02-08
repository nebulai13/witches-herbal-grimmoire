"""Main REPL interface for Grimmoire - Witchy Edition."""
import sys
import shlex
import random
from typing import Optional, List
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.style import Style
from rich.theme import Theme
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion

from ..db.manager import DatabaseManager
from ..db.schema import get_db_path
from .commands import CommandHandler, CommandResult


# Witchy color theme
WITCHY_THEME = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red",
    "success": "green",
    "herb": "green",
    "potion": "magenta",
    "spell": "cyan",
    "moon": "bright_white",
    "cauldron": "dark_orange",
})

BANNER = """
[magenta]
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀
        ⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀
        ⠀⢀⣾⣿⣿⣿⣿⣿[green]🌿[/green]⣿⣿⣿⣿⣿⣿[green]🌿[/green]⣿⣿⣿⣿⣿⣷⡀⠀
        ⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀
        ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
        ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
        ⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃
        ⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀
        ⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀
        ⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀
        ⠀⠀⠀[bright_white]☽[/bright_white]⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀[bright_white]☾[/bright_white]⠀⠀⠀
[/magenta]
[bold green]╔══════════════════════════════════════════════════════════════════╗[/bold green]
[bold green]║[/bold green]                                                                  [bold green]║[/bold green]
[bold green]║[/bold green]   [magenta]✧･ﾟ: *✧･ﾟ:*[/magenta]  [bold bright_white]THE WITCH'S GRIMMOIRE[/bold bright_white]  [magenta]*:･ﾟ✧*:･ﾟ✧[/magenta]   [bold green]║[/bold green]
[bold green]║[/bold green]                                                                  [bold green]║[/bold green]
[bold green]║[/bold green]      [dim]~ Herbal Wisdom & Traditional Medicine Database ~[/dim]       [bold green]║[/bold green]
[bold green]║[/bold green]                                                                  [bold green]║[/bold green]
[bold green]╚══════════════════════════════════════════════════════════════════╝[/bold green]
"""

WITCHY_TIPS = [
    "🌙 Tip: Brew your database with [green]scrape \"NAEB Datasette\"[/green]",
    "🔮 Tip: Divine PubMed secrets with [green]pubmed <query>[/green]",
    "🌿 Tip: Search for herbs with [green]search plant <name>[/green]",
    "⚗️ Tip: Find potions with [green]search recipe <ingredient>[/green]",
    "🕯️ Tip: Discover ailment cures with [green]search ailment <condition>[/green]",
    "☽ Tip: Your spell history is preserved across sessions",
    "✨ Tip: Misspelled incantations are auto-corrected",
]

FAREWELL_MESSAGES = [
    "May the moon guide your path! 🌙",
    "Blessed be, dear herbalist! ✨",
    "Until the stars align again! ⭐",
    "The cauldron awaits your return! 🔮",
    "Merry meet, merry part, merry meet again! 🌿",
]

HELP_TEXT = """
## ✨ Mystical Commands ✨

### 🌿 Herbal Search
- `search plant <query>` - Seek herbs in the grimmoire
- `search ingredient <query>` - Divine active compounds
- `search ailment <query>` - Find cures for maladies
- `search recipe <query>` - Discover ancient preparations
- `find <query>` - Search all mystical knowledge
- `pubmed <query>` - Consult the modern scrolls

### 📚 Sources of Wisdom
- `sources list` - View all knowledge sources
- `sources add <name> <url>` - Add a new source of wisdom
- `sources enable <id>` - Awaken a dormant source
- `sources disable <id>` - Silence a source

### 🔮 Scrying & Gathering
- `scrape` - List available gathering rituals
- `scrape <source>` - Gather knowledge (30s timeout)
- `scrape <source> -b` - Gather in the background

### ⚗️ Background Rituals
- `jobs list` - View all ongoing rituals
- `jobs status <id>` - Divine a ritual's progress
- `jobs resume <id>` - Resume an interrupted ritual
- `jobs stop` - Halt the current ritual

### 📖 Grimmoire Management
- `db stats` - Count entries in your grimmoire
- `db path` - Reveal the grimmoire's location

### 🕯️ Other
- `help` - Summon this guidance
- `quit` / `exit` - Close the grimmoire

## 💫 Mystical Tips
- Spell corrections are automatic - fear not typos!
- Long rituals can be interrupted with Ctrl+C and resumed later
- The grimmoire remembers your search history
"""


class GrimmoireCompleter(Completer):
    """Custom completer with witchy flair."""
    
    def __init__(self, handler: CommandHandler):
        self.handler = handler
        self.commands = ['search', 'find', 'pubmed', 'sources', 'scrape', 'jobs', 'db', 'help', 'quit', 'exit']
        self.search_types = ['plant', 'ingredient', 'ailment', 'recipe', 'all']
        self.sources_actions = ['list', 'add', 'enable', 'disable']
        self.jobs_actions = ['list', 'status', 'resume', 'stop']
        self.db_actions = ['stats', 'path']
    
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        words = text.split()
        
        if not words:
            for cmd in self.commands:
                yield Completion(cmd, start_position=0)
        elif len(words) == 1 and not text.endswith(' '):
            word = words[0].lower()
            for cmd in self.commands:
                if cmd.startswith(word):
                    yield Completion(cmd, start_position=-len(word))
        elif words[0].lower() == 'search':
            if len(words) == 1 or (len(words) == 2 and not text.endswith(' ')):
                prefix = words[1].lower() if len(words) > 1 else ''
                for stype in self.search_types:
                    if stype.startswith(prefix):
                        yield Completion(stype, start_position=-len(prefix))
            else:
                partial = words[-1] if not text.endswith(' ') else ''
                suggestions = self.handler.search_engine.autocomplete(partial)
                for suggestion in suggestions:
                    yield Completion(suggestion, start_position=-len(partial))
        elif words[0].lower() == 'sources':
            if len(words) == 1 or (len(words) == 2 and not text.endswith(' ')):
                prefix = words[1].lower() if len(words) > 1 else ''
                for action in self.sources_actions:
                    if action.startswith(prefix):
                        yield Completion(action, start_position=-len(prefix))
        elif words[0].lower() == 'jobs':
            if len(words) == 1 or (len(words) == 2 and not text.endswith(' ')):
                prefix = words[1].lower() if len(words) > 1 else ''
                for action in self.jobs_actions:
                    if action.startswith(prefix):
                        yield Completion(action, start_position=-len(prefix))
        elif words[0].lower() == 'db':
            if len(words) == 1 or (len(words) == 2 and not text.endswith(' ')):
                prefix = words[1].lower() if len(words) > 1 else ''
                for action in self.db_actions:
                    if action.startswith(prefix):
                        yield Completion(action, start_position=-len(prefix))
        elif words[0].lower() == 'scrape':
            if len(words) == 1 or (len(words) == 2 and not text.endswith(' ')):
                prefix = words[1] if len(words) > 1 else ''
                from ..scraper.sources import SourceRegistry
                for source in SourceRegistry.list_sources():
                    if source.lower().startswith(prefix.lower()):
                        yield Completion(source, start_position=-len(prefix))


class GrimmoireREPL:
    """Main REPL interface with witchy aesthetics."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.console = Console(theme=WITCHY_THEME)
        self.db = DatabaseManager(db_path)
        self.handler = CommandHandler(self.db, self.console)
        
        history_path = get_db_path().parent / "spell_history.txt"
        self.session = PromptSession(
            history=FileHistory(str(history_path)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=GrimmoireCompleter(self.handler)
        )
    
    def _get_prompt(self) -> str:
        """Get a witchy prompt with moon phase indicator."""
        moons = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘']
        import time
        moon = moons[int(time.time() / 3600) % 8]  # Changes hourly
        return f"\n{moon} [bold magenta]grimmoire[/bold magenta] [green]⌁[/green] "
    
    def run(self):
        """Run the REPL main loop."""
        self.console.print(BANNER)
        
        # Show quick stats with witchy flair
        stats = self.db.get_stats()
        total = sum(stats.get(k, 0) for k in ['plants', 'ingredients', 'ailments', 'recipes'])
        
        if total > 0:
            self.console.print(f"[dim]📖 Your grimmoire contains {total} entries of arcane knowledge[/dim]")
        else:
            self.console.print("[dim]📖 Your grimmoire is empty. Gather wisdom with [green]scrape \"NAEB Datasette\"[/green][/dim]")
        
        # Random witchy tip
        self.console.print(f"\n[dim]{random.choice(WITCHY_TIPS)}[/dim]\n")
        
        while True:
            try:
                # Get witchy prompt
                prompt_text = self._get_prompt()
                self.console.print(prompt_text, end="")
                line = self.session.prompt("")
                line = line.strip()
                
                if not line:
                    continue
                
                try:
                    parts = shlex.split(line)
                except ValueError as e:
                    self.console.print(f"[danger]✗ Spell malformed: {e}[/danger]")
                    continue
                
                command = parts[0].lower()
                args = parts[1:]
                
                result = self._handle_command(command, args)
                
                if result is None:
                    break
                
                if not result.success and result.message:
                    self.console.print(f"[danger]✗ {result.message}[/danger]")
            
            except KeyboardInterrupt:
                self.handler.job_runner.request_stop()
                self.console.print("\n[warning]⚡ Ritual interrupted. Use 'quit' to close the grimmoire.[/warning]")
                continue
            
            except EOFError:
                break
        
        farewell = random.choice(FAREWELL_MESSAGES)
        self.console.print(f"\n[bold magenta]✨ {farewell}[/bold magenta]\n")
        self.db.close()
    
    def _handle_command(self, command: str, args: List[str]) -> Optional[CommandResult]:
        """Handle a single command. Returns None to exit."""
        
        if command in ('quit', 'exit', 'q'):
            return None
        
        elif command == 'help':
            self.console.print(Markdown(HELP_TEXT))
            return CommandResult(True)
        
        elif command == 'search':
            return self.handler.cmd_search(args)
        
        elif command == 'find':
            return self.handler.cmd_find(args)
        
        elif command == 'pubmed':
            return self.handler.cmd_pubmed(args)
        
        elif command == 'sources':
            return self.handler.cmd_sources(args)
        
        elif command == 'scrape':
            return self.handler.cmd_scrape(args)
        
        elif command == 'jobs':
            return self.handler.cmd_jobs(args)
        
        elif command == 'db':
            return self.handler.cmd_db(args)
        
        else:
            return CommandResult(False, f"Unknown incantation: '{command}'. Whisper 'help' for guidance.")
