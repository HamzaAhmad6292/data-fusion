"""
Data Description Service

This service automatically crawls the data directory, identifies all supported
dataset files, generates semantic descriptions for each using LLM,
and consolidates everything into a single master metadata file.
"""

import os
import json
import sys
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "app"))

from app.description_generator import DescriptionGenerator
from app.processors.factory import ProcessorFactory

# UI and Logging imports
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
    from rich.logging import RichHandler
    from rich.theme import Theme
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Custom Theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "bold magenta",
})

# Setup Logging
if RICH_AVAILABLE:
    console = Console(theme=custom_theme)
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console)]
    )
else:
    console = None
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("description_service")

class DescriptionService:
    """Service to generate and consolidate descriptions for all available data."""

    def __init__(
        self, 
        data_dir: str = "data", 
        output_file: str = "data/consolidated_descriptions.json"
    ):
        """
        Initialize the service.
        
        Args:
            data_dir: Directory containing data files
            output_file: Path to save the consolidated JSON
        """
        self.data_root = project_root / data_dir
        self.output_path = project_root / output_file
        
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.generator = DescriptionGenerator()
        self.supported_extensions = ProcessorFactory.get_supported_types()
        
    def log_banner(self):
        """Display a beautiful banner."""
        if not RICH_AVAILABLE:
            print("=== DATA DESCRIPTION SERVICE ===")
            return

        banner = Panel(
            """[bold highlight]LEGAL FUSION[/bold highlight]
[info]Data Ingestion & Documentation Engine[/info]

[white]Synthesizing intelligence from heterogeneous legal data sources.[/white]""",
            box=box.DOUBLE,
            border_style="highlight",
            subtitle="[success]v1.0[/success]",
            subtitle_align="right"
        )
        console.print(banner)

    def find_all_files(self) -> List[Path]:
        """Find all supported files in the data directory recursively."""
        all_files = []
        for ext in self.supported_extensions:
            # Recursive search for each extension
            all_files.extend(self.data_root.rglob(f"*{ext}"))
        
        # Filter: Exclude hidden files, temp files, and results files
        filtered_files = [
            f for f in all_files 
            if not f.name.startswith('.') 
            and not f.name.endswith('_descriptions.json')
            and "consolidated" not in f.name
            and "checkpoint" not in str(f).lower()
        ]
        
        # Remove duplicates (Path objects handle this well but just in case)
        return sorted(list(set(filtered_files)))

    def run(self, force: bool = False, limit: Optional[int] = None):
        """
        Run the description generation process.
        
        Args:
            force: If True, re-generate even if output exists.
            limit: Maximum number of files to process.
        """
        self.log_banner()
        
        if not self.data_root.exists():
            logger.error(f"Data root directory not found: {self.data_root}")
            return

        data_files = self.find_all_files()
        
        if not data_files:
            logger.warning(f"No supported data files found in {self.data_root}")
            return

        if limit:
            data_files = data_files[:limit]
            logger.info(f"Limit applied: processing only first [highlight]{limit}[/highlight] files.")

        logger.info(f"Discovered [highlight]{len(data_files)}[/highlight] data files for analysis.")
        
        consolidated_results = []
        stats = {"success": 0, "failed": 0, "total": len(data_files)}
        start_time = time.time()

        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=40),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=console,
                transient=False
            ) as progress:
                main_task = progress.add_task("[info]Analyzing Datasets...", total=len(data_files))
                
                for file_path in data_files:
                    rel_path = file_path.relative_to(project_root)
                    progress.update(main_task, description=f"[info]Processing [bold]{file_path.name}[/bold]")
                    
                    try:
                        # Generate description
                        result = self.generator.generate(file_path)
                        
                        # Add metadata about location
                        result["relative_path"] = str(rel_path)
                        result["processed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        
                        consolidated_results.append(result)
                        stats["success"] += 1
                        logger.info(f"[success]DONE[/success] {file_path.name}")
                        
                    except Exception as e:
                        stats["failed"] += 1
                        logger.error(f"Failed to process {file_path.name}: {str(e)}")
                    
                    progress.advance(main_task)
                    if file_path.suffix.lower() not in ['.txt', '.text']:
                        time.sleep(2)
        else:
            # Fallback for non-rich
            for i, file_path in enumerate(data_files):
                logger.info(f"[{i+1}/{len(data_files)}] Processing {file_path.name}...")
                try:
                    result = self.generator.generate(file_path)
                    consolidated_results.append(result)
                    stats["success"] += 1
                except Exception as e:
                    stats["failed"] += 1
                    logger.error(f"Error: {e}")
                
                if file_path.suffix.lower() not in ['.txt', '.text']:
                    time.sleep(2)

        # Final Consolidation and Save
        duration = time.time() - start_time
        self._save_results(consolidated_results, stats, duration)

    def _save_results(self, results: List[Dict], stats: Dict, duration: float):
        """Save results to file and display summary."""
        output_data = {
            "metadata": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_files": stats["total"],
                "success_count": stats["success"],
                "failure_count": stats["failed"],
                "duration_seconds": round(duration, 2)
            },
            "datasets": results
        }
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
            
        if RICH_AVAILABLE:
            # Summary Table
            table = Table(
                title="[bold highlight]Generation Summary[/bold highlight]",
                box=box.ROUNDED,
                header_style="bold cyan",
                border_style="highlight"
            )
            
            table.add_column("Filename", style="white")
            table.add_column("Type", style="dim")
            table.add_column("Columns", justify="right", style="magenta")
            table.add_column("Status", justify="center")

            for res in results:
                ext = Path(res['file_path']).suffix
                table.add_row(
                    res['filename'],
                    ext,
                    str(len(res.get('columns', []))),
                    "[success]✔ SUCCESS[/success]"
                )
            
            console.print("\n")
            console.print(table)
            
            # Final Status Panel
            summary_panel = Panel(
                f"""[bold]Process Completed in {duration:.2f} seconds[/bold]
[success]Successfully Processed:[/success] {stats['success']}
[error]Failed:[/error] {stats['failed']}
[highlight]Master File:[/highlight] {self.output_path}""",
                title="[bold]Status Report[/bold]",
                border_style="success" if stats["failed"] == 0 else "warning"
            )
            console.print(summary_panel)
        else:
            logger.info(f"Finished. Results saved to {self.output_path}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Description Service")
    parser.add_argument("--data-dir", default="data", help="Directory containing data files")
    parser.add_argument("--output", default="data/consolidated_descriptions.json", help="Output file path")
    parser.add_argument("--limit", type=int, help="Limit number of files to process")
    
    args = parser.parse_args()
    
    service = DescriptionService(data_dir=args.data_dir, output_file=args.output)
    service.run(limit=args.limit)
