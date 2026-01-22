"""
Agent Runner Module
Handles running the pydantic_ai agent on markdown files with proper logging and widget output.
"""

import asyncio
import json
import logging
import pathlib
from datetime import datetime
from typing import List, Optional, Callable
from dataclasses import dataclass, field

import ipywidgets as widgets
from IPython.display import display, clear_output

from pydantic_ai import Agent


@dataclass
class AgentRunResult:
    """Result from processing a single markdown file."""
    md_path: str
    json_path: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
    total_params: int = 0
    missing_count: int = 0
    missing_fields: List[str] = field(default_factory=list)


@dataclass
class AgentRunSummary:
    """Summary of the entire agent run."""
    total_files: int = 0
    successful: int = 0
    failed: int = 0
    avg_missing_fields: float = 0.0
    results: List[AgentRunResult] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


class AgentRunnerLogger:
    """Handles logging to both file and memory for display."""
    
    def __init__(self, log_dir: pathlib.Path, run_id: str):
        self.log_dir = log_dir
        self.run_id = run_id
        self.log_file = log_dir / f"agent_run_{run_id}.log"
        self.messages: List[str] = []
        
        # Set up file logger
        self.logger = logging.getLogger(f"agent_runner_{run_id}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers = []  # Clear any existing handlers
        
        # File handler
        fh = logging.FileHandler(self.log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
        self.logger.addHandler(fh)
        
    def info(self, msg: str):
        self.logger.info(msg)
        self.messages.append(f"[INFO] {msg}")
        
    def warning(self, msg: str):
        self.logger.warning(msg)
        self.messages.append(f"[WARN] {msg}")
        
    def error(self, msg: str):
        self.logger.error(msg)
        self.messages.append(f"[ERROR] {msg}")
        
    def debug(self, msg: str):
        self.logger.debug(msg)
        
    def get_recent_messages(self, n: int = 10) -> List[str]:
        return self.messages[-n:]


class AgentRunnerWidget:
    """Widget for displaying agent run progress and results."""
    
    def __init__(self):
        # Progress components
        self.progress_bar = widgets.IntProgress(
            value=0, min=0, max=100,
            description='Progress:',
            bar_style='info',
            style={'bar_color': '#3498db', 'description_width': '80px'},
            layout=widgets.Layout(width='100%')
        )
        
        self.status_label = widgets.HTML(
            value='<b>Status:</b> Initializing...',
            layout=widgets.Layout(margin='5px 0')
        )
        
        self.current_file_label = widgets.HTML(
            value='<i>Waiting to start...</i>',
            layout=widgets.Layout(margin='5px 0')
        )
        
        self.stats_html = widgets.HTML(
            value='',
            layout=widgets.Layout(margin='10px 0')
        )
        
        self.log_output = widgets.Output(
            layout=widgets.Layout(
                height='150px',
                overflow='auto',
                border='1px solid #ddd',
                padding='5px'
            )
        )
        
        # Summary components (shown at the end)
        self.summary_html = widgets.HTML(value='')
        
        # Main container
        self.container = widgets.VBox([
            widgets.HTML('<h3>🤖 Agent Processing</h3>'),
            self.status_label,
            self.progress_bar,
            self.current_file_label,
            self.stats_html,
            widgets.HTML('<b>Recent Log Messages:</b>'),
            self.log_output,
            self.summary_html
        ], layout=widgets.Layout(padding='10px', border='1px solid #ccc', border_radius='5px'))
        
    def display(self):
        display(self.container)
        
    def update_progress(self, current: int, total: int, current_file: str = ""):
        self.progress_bar.max = total
        self.progress_bar.value = current
        percent = (current / total * 100) if total > 0 else 0
        self.progress_bar.description = f'{percent:.1f}%'
        
        if current_file:
            filename = pathlib.Path(current_file).name
            self.current_file_label.value = f'<i>Processing: {filename}</i>'
            
    def update_status(self, status: str, style: str = "info"):
        colors = {
            "info": "#3498db",
            "success": "#27ae60", 
            "warning": "#f39c12",
            "error": "#e74c3c"
        }
        color = colors.get(style, "#3498db")
        self.status_label.value = f'<b style="color:{color}">Status:</b> {status}'
        
        # Update progress bar style
        bar_styles = {"info": "info", "success": "success", "warning": "warning", "error": "danger"}
        self.progress_bar.bar_style = bar_styles.get(style, "info")
        
    def update_stats(self, successful: int, failed: int, total: int):
        self.stats_html.value = f'''
        <div style="display:flex; gap:20px; font-size:14px;">
            <span>✅ <b>Successful:</b> {successful}</span>
            <span>❌ <b>Failed:</b> {failed}</span>
            <span>📄 <b>Total:</b> {total}</span>
        </div>
        '''
        
    def update_log(self, messages: List[str]):
        with self.log_output:
            clear_output(wait=True)
            for msg in messages:
                if "[ERROR]" in msg:
                    print(f"\033[91m{msg}\033[0m")
                elif "[WARN]" in msg:
                    print(f"\033[93m{msg}\033[0m")
                else:
                    print(msg)
                    
    def show_summary(self, summary: AgentRunSummary, log_file_path: pathlib.Path):
        duration = summary.duration_seconds
        minutes = int(duration // 60)
        seconds = duration % 60
        
        success_rate = (summary.successful / summary.total_files * 100) if summary.total_files > 0 else 0
        
        self.summary_html.value = f'''
        <div style="background:#f8f9fa; padding:15px; border-radius:5px; margin-top:10px;">
            <h4 style="margin-top:0;">📊 Processing Summary</h4>
            <table style="width:100%; border-collapse:collapse;">
                <tr><td><b>Total Files:</b></td><td>{summary.total_files}</td></tr>
                <tr><td><b>Successful:</b></td><td style="color:#27ae60;">{summary.successful}</td></tr>
                <tr><td><b>Failed:</b></td><td style="color:#e74c3c;">{summary.failed}</td></tr>
                <tr><td><b>Success Rate:</b></td><td>{success_rate:.1f}%</td></tr>
                <tr><td><b>Avg Missing Fields:</b></td><td>{summary.avg_missing_fields:.1f}</td></tr>
                <tr><td><b>Duration:</b></td><td>{minutes}m {seconds:.1f}s</td></tr>
                <tr><td><b>Log File:</b></td><td><code>{log_file_path}</code></td></tr>
            </table>
        </div>
        '''


async def run_agent_on_markdown(
    md_path: str,
    agent: Agent,
    semaphore: asyncio.Semaphore,
    logger: AgentRunnerLogger
) -> dict:
    """Run the agent on a single markdown file."""
    async with semaphore:
        logger.debug(f"Starting processing: {md_path}")
        md_text = pathlib.Path(md_path).read_text(encoding="utf-8")
        response = await agent.run(md_text, model_settings={"temperature": 0})
        logger.debug(f"Completed processing: {md_path}")
        return response.output


async def process_markdown_files(
    md_paths: List[str],
    agent: Agent,
    json_output_dir: pathlib.Path,
    schema: dict,
    log_dir: pathlib.Path,
    concurrency: int = 3,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> AgentRunSummary:
    """
    Process multiple markdown files with the agent.
    
    Args:
        md_paths: List of markdown file paths to process
        agent: The pydantic_ai Agent instance
        json_output_dir: Directory to save JSON outputs
        schema: The JSON schema for validation
        log_dir: Directory for log files
        concurrency: Number of concurrent agent calls
        progress_callback: Optional callback(current, total, current_file) for progress updates
        
    Returns:
        AgentRunSummary with results
    """
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = AgentRunnerLogger(log_dir, run_id)
    
    summary = AgentRunSummary(
        total_files=len(md_paths),
        start_time=datetime.now()
    )
    
    logger.info(f"Starting agent run with {len(md_paths)} files, concurrency={concurrency}")
    
    semaphore = asyncio.Semaphore(concurrency)
    
    # Create tasks
    tasks = []
    for md_path in md_paths:
        task = asyncio.create_task(run_agent_on_markdown(md_path, agent, semaphore, logger))
        tasks.append((md_path, task))
    
    # Process results as they complete
    schema_props = schema.get("properties", {})
    total_params = len(schema_props)
    
    for i, (md_path, task) in enumerate(tasks):
        result = AgentRunResult(md_path=md_path, total_params=total_params)
        
        try:
            output = await task
            
            if isinstance(output, Exception):
                raise output
                
            # Save to JSON
            stem = pathlib.Path(md_path).stem
            json_path = json_output_dir / f"{stem}.json"
            
            # Load existing JSON with meta
            with json_path.open("r", encoding="utf-8") as f:
                existing = json.load(f)
            
            # Add agent field
            existing["agent"] = output
            
            # Save back
            json_str = json.dumps(existing, indent=2, ensure_ascii=False)
            json_path.write_text(json_str, encoding="utf-8")
            
            # Calculate missing fields
            missing_fields = [k for k in output if k not in schema_props or output[k] is None]
            
            result.success = True
            result.json_path = str(json_path)
            result.missing_count = len(missing_fields)
            result.missing_fields = missing_fields
            
            summary.successful += 1
            logger.info(f"✓ {stem}: {len(missing_fields)} missing fields")
            
        except Exception as e:
            result.success = False
            result.error = str(e)
            summary.failed += 1
            logger.error(f"✗ {pathlib.Path(md_path).stem}: {e}")
            
        summary.results.append(result)
        
        # Progress callback
        if progress_callback:
            progress_callback(i + 1, len(md_paths), md_path)
    
    summary.end_time = datetime.now()
    
    # Calculate average missing fields
    successful_results = [r for r in summary.results if r.success]
    if successful_results:
        summary.avg_missing_fields = sum(r.missing_count for r in successful_results) / len(successful_results)
    
    logger.info(f"Agent run completed: {summary.successful} successful, {summary.failed} failed")
    logger.info(f"Average missing fields: {summary.avg_missing_fields:.1f}")
    logger.info(f"Duration: {summary.duration_seconds:.1f} seconds")
    
    return summary, logger


async def run_agent_with_widget(
    md_paths: List[str],
    agent: Agent,
    json_output_dir: pathlib.Path,
    schema: dict,
    log_dir: pathlib.Path,
    concurrency: int = 3
) -> AgentRunSummary:
    """
    Run the agent processing with a nice widget display.
    
    Args:
        md_paths: List of markdown file paths to process
        agent: The pydantic_ai Agent instance
        json_output_dir: Directory to save JSON outputs
        schema: The JSON schema for validation
        log_dir: Directory for log files
        concurrency: Number of concurrent agent calls
        
    Returns:
        AgentRunSummary with results
    """
    widget = AgentRunnerWidget()
    widget.display()
    
    widget.update_status("Starting agent processing...", "info")
    widget.update_stats(0, 0, len(md_paths))
    
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = AgentRunnerLogger(log_dir, run_id)
    
    summary = AgentRunSummary(
        total_files=len(md_paths),
        start_time=datetime.now()
    )
    
    logger.info(f"Starting agent run with {len(md_paths)} files, concurrency={concurrency}")
    
    semaphore = asyncio.Semaphore(concurrency)
    schema_props = schema.get("properties", {})
    total_params = len(schema_props)
    
    # Process files one batch at a time for better UI updates
    for i, md_path in enumerate(md_paths):
        result = AgentRunResult(md_path=md_path, total_params=total_params)
        
        widget.update_progress(i, len(md_paths), md_path)
        widget.update_status(f"Processing file {i+1} of {len(md_paths)}...", "info")
        
        try:
            output = await run_agent_on_markdown(md_path, agent, semaphore, logger)
            
            if isinstance(output, Exception):
                raise output
                
            # Save to JSON
            stem = pathlib.Path(md_path).stem
            json_path = json_output_dir / f"{stem}.json"
            
            with json_path.open("r", encoding="utf-8") as f:
                existing = json.load(f)
            
            existing["agent"] = output
            json_str = json.dumps(existing, indent=2, ensure_ascii=False)
            json_path.write_text(json_str, encoding="utf-8")
            
            missing_fields = [k for k in output if k not in schema_props or output[k] is None]
            
            result.success = True
            result.json_path = str(json_path)
            result.missing_count = len(missing_fields)
            result.missing_fields = missing_fields
            
            summary.successful += 1
            logger.info(f"✓ {stem}: {len(missing_fields)} missing fields")
            
        except Exception as e:
            result.success = False
            result.error = str(e)
            summary.failed += 1
            logger.error(f"✗ {pathlib.Path(md_path).stem}: {e}")
            
        summary.results.append(result)
        
        # Update widget
        widget.update_stats(summary.successful, summary.failed, len(md_paths))
        widget.update_log(logger.get_recent_messages(8))
    
    summary.end_time = datetime.now()
    
    # Calculate average missing fields
    successful_results = [r for r in summary.results if r.success]
    if successful_results:
        summary.avg_missing_fields = sum(r.missing_count for r in successful_results) / len(successful_results)
    
    logger.info(f"Agent run completed: {summary.successful} successful, {summary.failed} failed")
    logger.info(f"Duration: {summary.duration_seconds:.1f} seconds")
    
    # Final UI updates
    widget.update_progress(len(md_paths), len(md_paths))
    
    if summary.failed == 0:
        widget.update_status("✅ Processing completed successfully!", "success")
    elif summary.successful > 0:
        widget.update_status(f"⚠️ Processing completed with {summary.failed} errors", "warning")
    else:
        widget.update_status("❌ Processing failed", "error")
        
    widget.update_log(logger.get_recent_messages(8))
    widget.show_summary(summary, logger.log_file)
    
    return summary
