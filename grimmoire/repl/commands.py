"""Command handlers for the Grimmoire REPL."""
import json
import time
import webbrowser
import sys
from typing import Optional, Callable, List, Dict
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from ..db.manager import DatabaseManager
from ..search.engine import SearchEngine, SearchType, SearchResult
from ..search.pubmed import PubMedClient
from ..search.web_provider import list_providers, get_provider
from ..scraper.sources import SourceRegistry
from ..scraper.base import ScraperProgress
from ..jobs.runner import JobRunner, JobContext, JobStatus
from ..jobs.journal import Journal

# Import crawlers to register them
from ..scraper.crawlers import naeb

# Strip Rich markup for plain text output
import re
def strip_rich_markup(text: str) -> str:
    """Remove Rich markup tags from text."""
    return re.sub(r'\[/?[^\]]+\]', '', text)


def magic_print(text: str, delay: float = 0.018):
    """Print text letter by letter with magical effect."""
    clean_text = strip_rich_markup(text)
    for char in clean_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write('\n')
    sys.stdout.flush()


def magic_print_block(text: str, line_delay: float = 0.012, char_delay: float = 0.008):
    """Print a block of text with magical effect, line by line."""
    clean_text = strip_rich_markup(text)
    for line in clean_text.split('\n'):
        for char in line:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(char_delay)
        sys.stdout.write('\n')
        sys.stdout.flush()
        time.sleep(line_delay)


@dataclass
class CommandResult:
    success: bool
    message: str = ""
    data: any = None


class CommandHandler:
    """Handles all REPL commands."""
    
    def __init__(self, db: DatabaseManager, console: Console):
        self.db = db
        self.console = console
        self.search_engine = SearchEngine(db)
        self.pubmed = PubMedClient()
        self.job_runner = JobRunner(db)
        self.journal = Journal(db)
        self._last_results: List[SearchResult] = []  # Store last search results
    
    def cmd_search(self, args: List[str]) -> CommandResult:
        """Search for entries. Usage: search <type> <query> [--web]
        
        Use --web or -w to force include online database search.
        Without flag, web search is used as fallback when no local results.
        """
        if len(args) < 2:
            return CommandResult(False, "Usage: search <type> <query> [--web]\nTypes: plant, ingredient, ailment, recipe, all")
        
        type_map = {
            'plant': SearchType.PLANT, 'plants': SearchType.PLANT,
            'ingredient': SearchType.INGREDIENT, 'ingredients': SearchType.INGREDIENT, 'compound': SearchType.INGREDIENT,
            'ailment': SearchType.AILMENT, 'ailments': SearchType.AILMENT, 'disease': SearchType.AILMENT,
            'recipe': SearchType.RECIPE, 'recipes': SearchType.RECIPE, 'formula': SearchType.RECIPE,
            'all': SearchType.ALL,
        }
        
        # Parse --web flag
        force_web = '--web' in args or '-w' in args
        args = [a for a in args if a not in ('--web', '-w')]
        
        search_type = type_map.get(args[0].lower(), SearchType.ALL)
        query = ' '.join(args[1:])
        
        with self.console.status(f"[bold green]Searching for '{query}'...") if force_web else self.console.status(""):
            results, suggestion = self.search_engine.search(query, search_type, include_web=force_web if force_web else None)
        
        if suggestion:
            magic_print(f"🔮 Did you mean: {suggestion}?")
        
        if not results:
            magic_print("No results found in the grimmoire...")
            return CommandResult(True, "No results", [])
        
        # Check if any results came from web
        has_web_results = any(r.source != 'local' for r in results)
        self._display_results(results, show_source=has_web_results)
        
        local_count = sum(1 for r in results if r.source == 'local')
        web_count = len(results) - local_count
        if web_count > 0:
            return CommandResult(True, f"Found {local_count} local + {web_count} online results", results)
        return CommandResult(True, f"Found {len(results)} results", results)
    
    def cmd_pubmed(self, args: List[str]) -> CommandResult:
        """Search PubMed for research. Usage: pubmed <query>"""
        if not args:
            return CommandResult(False, "Usage: pubmed <query>")
        
        query = ' '.join(args)
        
        with self.console.status(f"[bold green]Searching PubMed for '{query}'..."):
            try:
                results = self.pubmed.search_herbs(query, max_results=10)
            except Exception as e:
                return CommandResult(False, f"PubMed search failed: {e}")
        
        if not results:
            magic_print("No PubMed scrolls found...")
            return CommandResult(True, "No results", [])
        
        self._display_pubmed_results(results)
        return CommandResult(True, f"Found {len(results)} articles", results)
    
    def cmd_find(self, args: List[str]) -> CommandResult:
        """Quick search across all types. Usage: find <query>"""
        if not args:
            return CommandResult(False, "Usage: find <query>")
        return self.cmd_search(['all'] + args)
    
    def cmd_websearch(self, args: List[str]) -> CommandResult:
        """Search online databases. Usage: websearch <query> [--provider <name>]
        
        Searches multiple online traditional medicine databases:
        - COCONUT: 695K natural products
        - LOTUS: 750K structure-organism pairs (via Wikidata)
        - ChEMBL: 2.4M compounds with bioactivity
        - ClinicalTrials.gov: Clinical trials
        - NAEB: Native American Ethnobotany
        - HERB 2.0: TCM herbs and ingredients
        - TCMSP: TCM Systems Pharmacology
        - OSADHI: Indian medicinal phytochemicals
        - IMPPAT: Indian Medicinal Plants
        - MSK: Memorial Sloan Kettering herbs
        - Dr. Duke's: Phytochemical database
        """
        if not args:
            # List available providers
            providers = list_providers()
            magic_print("✨ Available web search providers:")
            for name in providers:
                provider = get_provider(name)
                magic_print(f"  • {name} - {provider.name}")
            return CommandResult(True, "Listed providers", providers)
        
        # Parse arguments
        provider_filter = None
        query_parts = []
        i = 0
        while i < len(args):
            if args[i] in ('--provider', '-p') and i + 1 < len(args):
                provider_filter = [args[i + 1]]
                i += 2
            else:
                query_parts.append(args[i])
                i += 1
        
        if not query_parts:
            return CommandResult(False, "Usage: searchtheuniverse <query> [--provider <name>]")
        
        query = ' '.join(query_parts)
        
        magic_print(f"🔮 Scrying the universe for '{query}'...")
        try:
            results = self.search_engine.search_web_only(query, SearchType.ALL, 20, provider_filter)
        except Exception as e:
            return CommandResult(False, f"Web search failed: {e}")
        
        if not results:
            magic_print("The universe reveals nothing...")
            return CommandResult(True, "No results", [])
        
        self._display_results(results, show_source=True)
        return CommandResult(True, f"Found {len(results)} results from online sources", results)
    
    def cmd_read(self, args: List[str]) -> CommandResult:
        """Read/view a search result in the grimmoire with pager. Usage: read <#>
        
        Shows detailed information about a result from the last search.
        Uses a pager for comfortable reading (like less/man).
        """
        if not args:
            return CommandResult(False, "Usage: read <#>\nDisplays details of a result from the last search")
        
        if not self._last_results:
            return CommandResult(False, "No recent search results. Run a search first.")
        
        try:
            idx = int(args[0]) - 1  # Convert to 0-based index
        except (ValueError, IndexError):
            return CommandResult(False, "Please provide a valid result number")
        
        if idx < 0 or idx >= len(self._last_results):
            return CommandResult(False, f"Result #{idx + 1} not found. Results are numbered 1-{len(self._last_results)}")
        
        result = self._last_results[idx]
        name = result.data.get('name', 'Unknown')
        
        # Build plain text content for pager
        lines = []
        lines.append("=" * 70)
        lines.append(f"  ✨ {name}")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Type: {result.type}")
        lines.append(f"Source: {result.source}")
        lines.append("")
        
        # Show ALL data from the result
        for key, value in result.data.items():
            if key == 'name':
                continue  # Already shown
            
            # Format the key nicely
            display_key = key.replace('_', ' ').title()
            
            if isinstance(value, list):
                if value:
                    lines.append(f"{display_key}:")
                    for item in value:
                        lines.append(f"  • {item}")
            elif isinstance(value, dict):
                lines.append(f"{display_key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            elif value:
                # Wrap long text
                str_value = str(value)
                if len(str_value) > 70:
                    lines.append(f"{display_key}:")
                    # Word wrap
                    words = str_value.split()
                    current_line = "  "
                    for word in words:
                        if len(current_line) + len(word) + 1 > 70:
                            lines.append(current_line)
                            current_line = "  " + word
                        else:
                            current_line += " " + word if current_line != "  " else word
                    if current_line.strip():
                        lines.append(current_line)
                else:
                    lines.append(f"{display_key}: {str_value}")
        
        lines.append("")
        if result.url:
            lines.append(f"URL: {result.url}")
            lines.append("")
            lines.append("💡 Use 'open " + str(idx + 1) + "' to open in browser")
        
        lines.append("")
        lines.append("─" * 70)
        
        content = "\n".join(lines)
        
        # Display with magical typing effect
        magic_print_block(content)
        
        return CommandResult(True, f"Displayed result #{idx + 1}", result)
    
    def cmd_open(self, args: List[str]) -> CommandResult:
        """Open a search result in browser. Usage: open <#>
        
        Opens the URL in your default web browser.
        """
        if not args:
            return CommandResult(False, "Usage: open <#>\nOpens a result from the last search in your browser")
        
        if not self._last_results:
            return CommandResult(False, "No recent search results. Run a search first.")
        
        try:
            idx = int(args[0]) - 1  # Convert to 0-based index
        except (ValueError, IndexError):
            return CommandResult(False, "Please provide a valid result number")
        
        if idx < 0 or idx >= len(self._last_results):
            return CommandResult(False, f"Result #{idx + 1} not found. Results are numbered 1-{len(self._last_results)}")
        
        result = self._last_results[idx]
        
        if not result.url:
            return CommandResult(False, f"No URL available for result #{idx + 1}. Use 'read {idx + 1}' to view details.")
        
        webbrowser.open(result.url)
        magic_print(f"✓ Portal opened: {result.data.get('name', 'Unknown')}")
        
        return CommandResult(True, f"Opened result #{idx + 1} in browser", result)
    
    def cmd_sources(self, args: List[str]) -> CommandResult:
        """Manage data sources. Usage: sources [list|add|enable|disable] [args...]"""
        if not args:
            args = ['list']
        
        action = args[0].lower()
        
        if action == 'list':
            sources = self.db.get_sources()
            self._display_sources(sources)
            return CommandResult(True, f"{len(sources)} sources", sources)
        elif action == 'add':
            if len(args) < 3:
                return CommandResult(False, "Usage: sources add <name> <url>")
            source_id = self.db.add_source(args[1], args[2])
            return CommandResult(True, f"Added source '{args[1]}' (ID: {source_id})")
        elif action == 'enable':
            if len(args) < 2:
                return CommandResult(False, "Usage: sources enable <id>")
            try:
                self.db.enable_source(int(args[1]))
                return CommandResult(True, f"Enabled source {args[1]}")
            except ValueError:
                return CommandResult(False, "Invalid source ID")
        elif action in ('disable', 'exclude'):
            if len(args) < 2:
                return CommandResult(False, "Usage: sources disable <id>")
            try:
                self.db.disable_source(int(args[1]))
                return CommandResult(True, f"Disabled source {args[1]}")
            except ValueError:
                return CommandResult(False, "Invalid source ID")
        else:
            return CommandResult(False, f"Unknown action: {action}")
    
    def cmd_scrape(self, args: List[str], timeout: float = 30.0) -> CommandResult:
        """Scrape data from a source. Usage: scrape <source_name> [--background]"""
        if not args:
            available = SourceRegistry.list_sources()
            magic_print("📜 Available gathering rituals:")
            for name in available:
                magic_print(f"  • {name}")
            return CommandResult(True, "Listed scrapers")
        
        source_name = args[0]
        background = '--background' in args or '-b' in args
        
        if not SourceRegistry.has_scraper(source_name):
            return CommandResult(False, f"No scraper available for '{source_name}'")
        
        job_id = self.db.create_job('scrape', {'source': source_name})
        
        def scrape_job(ctx: JobContext):
            scraper = SourceRegistry.get_scraper(source_name, ctx.db)
            def progress_callback(item, progress: ScraperProgress):
                ctx.progress_callback(progress.to_dict(), progress.processed_items)
                if ctx.should_stop():
                    scraper.request_stop()
            return scraper.run(callback=progress_callback)
        
        if background:
            self.job_runner.run_job(job_id, scrape_job, async_mode=True)
            return CommandResult(True, f"Started background scrape job {job_id}")
        else:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                         BarColumn(), TaskProgressColumn(), console=self.console) as progress:
                task = progress.add_task(f"Scraping {source_name}...", total=None)
                start_time = time.time()
                
                def display_progress(ctx: JobContext):
                    scraper = SourceRegistry.get_scraper(source_name, ctx.db)
                    def callback(item, prog: ScraperProgress):
                        progress.update(task, completed=prog.processed_items, total=prog.total_items or None,
                                       description=f"Scraping {source_name}: {prog.processed_items} items")
                        ctx.progress_callback(prog.to_dict(), prog.processed_items)
                        if time.time() - start_time > timeout:
                            scraper.request_stop()
                        if ctx.should_stop():
                            scraper.request_stop()
                    return scraper.run(callback=callback)
                
                self.job_runner.run_job(job_id, display_progress)
            
            job = self.db.get_job(job_id)
            self.search_engine.refresh_dictionary()
            return CommandResult(True, f"Scraped {job['results_count']} items from {source_name}")
    
    def cmd_jobs(self, args: List[str]) -> CommandResult:
        """Manage background jobs. Usage: jobs [list|status|resume|stop] [job_id]"""
        if not args:
            args = ['list']
        
        action = args[0].lower()
        
        if action == 'list':
            jobs = self.db.get_jobs()
            self._display_jobs(jobs)
            return CommandResult(True, f"{len(jobs)} jobs")
        elif action == 'status':
            if len(args) < 2:
                return CommandResult(False, "Usage: jobs status <job_id>")
            try:
                job_id = int(args[1])
                job = self.db.get_job(job_id)
                if not job:
                    return CommandResult(False, f"Job {job_id} not found")
                summary = self.journal.summarize_job(job_id)
                self._display_job_status(job, summary)
                return CommandResult(True, f"Job {job_id} status", summary)
            except ValueError:
                return CommandResult(False, "Invalid job ID")
        elif action == 'resume':
            if len(args) < 2:
                return CommandResult(False, "Usage: jobs resume <job_id>")
            try:
                return self._resume_job(int(args[1]))
            except ValueError:
                return CommandResult(False, "Invalid job ID")
        elif action == 'stop':
            self.job_runner.request_stop()
            return CommandResult(True, "Stop requested for current job")
        else:
            return CommandResult(False, f"Unknown action: {action}")
    
    def _resume_job(self, job_id: int) -> CommandResult:
        job = self.db.get_job(job_id)
        if not job:
            return CommandResult(False, f"Job {job_id} not found")
        if job['status'] != JobStatus.PAUSED:
            return CommandResult(False, f"Job {job_id} is not paused (status: {job['status']})")
        
        query = json.loads(job['query']) if job['query'] else {}
        source_name = query.get('source')
        if not source_name:
            return CommandResult(False, "Cannot determine source for job")
        
        def resume_scrape(ctx: JobContext, saved_progress: dict):
            scraper = SourceRegistry.get_scraper(source_name, ctx.db)
            resume_from = ScraperProgress.from_dict(saved_progress)
            def callback(item, prog: ScraperProgress):
                ctx.progress_callback(prog.to_dict(), prog.processed_items)
                if ctx.should_stop():
                    scraper.request_stop()
            return scraper.run(resume_from=resume_from, callback=callback)
        
        magic_print(f"🔄 Resuming ritual {job_id}...")
        self.job_runner.resume_job(job_id, resume_scrape, async_mode=True)
        return CommandResult(True, f"Resumed job {job_id}")
    
    def cmd_db(self, args: List[str]) -> CommandResult:
        """Database utilities. Usage: db [stats|export|path]"""
        if not args:
            args = ['stats']
        
        action = args[0].lower()
        
        if action == 'stats':
            stats = self.db.get_stats()
            self._display_stats(stats)
            return CommandResult(True, "Database stats", stats)
        elif action == 'path':
            magic_print(f"📖 Grimmoire location: {self.db.db_path}")
            return CommandResult(True, str(self.db.db_path))
        else:
            return CommandResult(False, f"Unknown action: {action}")
    
    def _display_results(self, results: List[SearchResult], show_source: bool = False):
        # Store results for later reference (e.g., opening URLs)
        self._last_results = results
        
        # Magic reveal of title
        magic_print("✨ Revealing ancient wisdom...", delay=0.02)
        
        table = Table(title="Search Results", show_header=True)
        table.add_column("#", style="bold yellow", width=3)
        table.add_column("Type", style="cyan", width=12)
        table.add_column("Name", style="green")
        if show_source:
            table.add_column("Source", style="magenta", width=15)
        table.add_column("Details", style="dim")
        
        for idx, result in enumerate(results[:20], 1):
            name = result.data.get('name', 'Unknown')
            details = ""
            if result.type == 'plant':
                details = result.data.get('scientific_name', '') or result.data.get('family', '') or result.data.get('latin_name', '')
            elif result.type == 'ingredient':
                details = result.data.get('molecular_formula', '') or result.data.get('pubchem_cid', '') or result.data.get('smiles', '')[:30] if result.data.get('smiles') else ''
            elif result.type == 'ailment':
                details = result.data.get('category', '') or result.data.get('status', '')
            elif result.type == 'recipe':
                details = result.data.get('tradition', '') or result.data.get('tribe', '')
            elif result.type == 'clinical_trial':
                details = result.data.get('status', '') or result.data.get('nct_id', '')
            elif result.type == 'ethnobotany':
                details = result.data.get('tribe', '') or result.data.get('category', '')
            
            # Add URL as clickable link if present
            if result.url:
                name = f"[link={result.url}]{name}[/link]"
            
            if show_source:
                table.add_row(str(idx), result.type, name, result.source, details or "")
            else:
                table.add_row(str(idx), result.type, name, details or "")
        
        self.console.print(table)
        if len(results) > 20:
            magic_print(f"... and {len(results) - 20} more results")
        
        # Show hint about opening results
        if any(r.url for r in results[:20]):
            magic_print("💡 Use 'read <#>' to view details, 'open <#>' to open in browser")
    
    def _display_pubmed_results(self, results: List[Dict]):
        for i, article in enumerate(results, 1):
            title = article.get('title', 'No title')
            authors = ', '.join(article.get('authors', [])[:3])
            if len(article.get('authors', [])) > 3:
                authors += ' et al.'
            source = article.get('source', '')
            pubdate = article.get('pubdate', '')
            pmid = article.get('pmid', '')
            
            panel = Panel(
                f"[bold]{title}[/bold]\n\n[dim]{authors}[/dim]\n{source} ({pubdate})\n[link=https://pubmed.ncbi.nlm.nih.gov/{pmid}]PMID: {pmid}[/link]",
                title=f"[{i}]", border_style="blue"
            )
            self.console.print(panel)
    
    def _display_sources(self, sources: List[Dict]):
        table = Table(title="Data Sources", show_header=True)
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Name", style="green")
        table.add_column("Type", width=8)
        table.add_column("Status", width=10)
        table.add_column("Last Scraped", width=20)
        
        for source in sources:
            status = "[green]Enabled[/green]" if source['enabled'] else "[red]Disabled[/red]"
            table.add_row(str(source['id']), source['name'], source['source_type'], status, source.get('last_scraped') or "Never")
        self.console.print(table)
    
    def _display_jobs(self, jobs: List[Dict]):
        table = Table(title="Jobs", show_header=True)
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Type", width=10)
        table.add_column("Status", width=12)
        table.add_column("Results", width=8)
        table.add_column("Created", width=20)
        
        status_colors = {'pending': 'yellow', 'running': 'blue', 'paused': 'magenta', 'completed': 'green', 'failed': 'red'}
        
        for job in jobs[:20]:
            status = job['status']
            color = status_colors.get(status, 'white')
            table.add_row(str(job['id']), job['job_type'], f"[{color}]{status}[/{color}]",
                         str(job['results_count'] or 0), job['created_at'][:19] if job['created_at'] else "")
        self.console.print(table)
    
    def _display_job_status(self, job: Dict, summary: Dict):
        status_colors = {'pending': 'yellow', 'running': 'blue', 'paused': 'magenta', 'completed': 'green', 'failed': 'red'}
        status = job['status']
        color = status_colors.get(status, 'white')
        
        content = f"""[bold]Job ID:[/bold] {job['id']}
[bold]Type:[/bold] {job['job_type']}
[bold]Status:[/bold] [{color}]{status}[/{color}]
[bold]Results:[/bold] {job['results_count'] or 0}
[bold]Duration:[/bold] {summary.get('duration', 'N/A')}
[bold]Interrupts:[/bold] {summary.get('interrupts', 0)}
[bold]Resumes:[/bold] {summary.get('resumes', 0)}"""
        
        if summary.get('errors'):
            content += f"\n[bold red]Errors:[/bold red]\n"
            for error in summary['errors'][:5]:
                content += f"  • {error}\n"
        
        self.console.print(Panel(content, title="Job Status", border_style=color))
    
    def _display_stats(self, stats: Dict):
        table = Table(title="Database Statistics", show_header=True)
        table.add_column("Entity", style="cyan")
        table.add_column("Count", style="green", justify="right")
        for entity, count in stats.items():
            table.add_row(entity.title(), str(count))
        self.console.print(table)
