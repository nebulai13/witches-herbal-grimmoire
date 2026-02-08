"""Background job runner with journaling support."""
import json
import signal
import threading
import time
from datetime import datetime
from typing import Callable, Optional, Any, List, Dict
from dataclasses import dataclass
from enum import Enum

from ..db.manager import DatabaseManager
from ..scraper.base import ScraperProgress


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class JobContext:
    """Context passed to job functions."""
    job_id: int
    db: DatabaseManager
    progress_callback: Callable
    should_stop: Callable[[], bool]


class JobRunner:
    """Runs long-running jobs in background with journaling."""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.current_job_id: Optional[int] = None
        self.stop_requested = False
        self._lock = threading.Lock()
        self._running_thread: Optional[threading.Thread] = None
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        def handler(signum, frame):
            self.request_stop()
        try:
            signal.signal(signal.SIGINT, handler)
            signal.signal(signal.SIGTERM, handler)
        except ValueError:
            pass
    
    def request_stop(self):
        with self._lock:
            self.stop_requested = True
            if self.current_job_id:
                self.db.journal_event('interrupt_requested', {'reason': 'user_interrupt'}, self.current_job_id)
    
    def should_stop(self) -> bool:
        with self._lock:
            return self.stop_requested
    
    def _update_progress(self, job_id: int, progress: dict, results_count: int = None):
        self.db.update_job_progress(job_id, progress, results_count)
        self.db.journal_event('progress', progress, job_id)
    
    def run_job(self, job_id: int, job_func: Callable[[JobContext], Any], async_mode: bool = False) -> Optional[Any]:
        if async_mode:
            thread = threading.Thread(target=self._run_job_internal, args=(job_id, job_func), daemon=True)
            thread.start()
            self._running_thread = thread
            return None
        else:
            return self._run_job_internal(job_id, job_func)
    
    def _run_job_internal(self, job_id: int, job_func: Callable[[JobContext], Any]) -> Any:
        with self._lock:
            self.current_job_id = job_id
            self.stop_requested = False
        
        self.db.update_job_status(job_id, JobStatus.RUNNING)
        self.db.journal_event('start', {'timestamp': datetime.now().isoformat()}, job_id)
        
        context = JobContext(
            job_id=job_id,
            db=self.db,
            progress_callback=lambda p, c=None: self._update_progress(job_id, p, c),
            should_stop=self.should_stop
        )
        
        result = None
        try:
            result = job_func(context)
            if self.should_stop():
                self.db.update_job_status(job_id, JobStatus.PAUSED)
                self.db.journal_event('paused', {'reason': 'interrupt', 'timestamp': datetime.now().isoformat()}, job_id)
            else:
                self.db.update_job_status(job_id, JobStatus.COMPLETED)
                self.db.journal_event('complete', {'timestamp': datetime.now().isoformat()}, job_id)
        except Exception as e:
            self.db.update_job_status(job_id, JobStatus.FAILED, str(e))
            self.db.journal_event('error', {'error': str(e), 'timestamp': datetime.now().isoformat()}, job_id)
        finally:
            with self._lock:
                self.current_job_id = None
        
        return result
    
    def resume_job(self, job_id: int, job_func: Callable[[JobContext, dict], Any], async_mode: bool = False) -> Optional[Any]:
        job = self.db.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        if job['status'] not in (JobStatus.PAUSED, JobStatus.PENDING):
            raise ValueError(f"Job {job_id} cannot be resumed (status: {job['status']})")
        
        progress = json.loads(job['progress']) if job['progress'] else {}
        self.db.journal_event('resume', {'from_progress': progress, 'timestamp': datetime.now().isoformat()}, job_id)
        
        def wrapped_func(ctx: JobContext):
            return job_func(ctx, progress)
        
        return self.run_job(job_id, wrapped_func, async_mode)
    
    def wait_for_completion(self, timeout: float = None) -> bool:
        if self._running_thread:
            self._running_thread.join(timeout)
            return not self._running_thread.is_alive()
        return True
    
    def get_resumable_jobs(self) -> List[Dict]:
        return self.db.get_jobs(JobStatus.PAUSED)
