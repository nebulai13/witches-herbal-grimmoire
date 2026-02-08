"""Journal management for tracking job history and recovery."""
import json
from typing import Optional, Dict, List
from datetime import datetime

from ..db.manager import DatabaseManager


class Journal:
    """Manages journaling for job execution and recovery."""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def log(self, event_type: str, data: dict = None, job_id: int = None):
        self.db.journal_event(event_type, data or {}, job_id)
    
    def get_last_checkpoint(self, job_id: int) -> Optional[Dict]:
        events = self.db.get_journal(job_id, limit=50)
        for event in events:
            if event['event_type'] == 'progress':
                try:
                    return json.loads(event['event_data'])
                except (json.JSONDecodeError, TypeError):
                    pass
        return None
    
    def get_recovery_point(self, job_id: int) -> Optional[Dict]:
        events = self.db.get_journal(job_id, limit=100)
        for event in events:
            if event['event_type'] in ('progress', 'paused', 'resume'):
                try:
                    data = json.loads(event['event_data'])
                    if 'from_progress' in data:
                        return data['from_progress']
                    return data
                except (json.JSONDecodeError, TypeError):
                    pass
        return None
    
    def get_job_timeline(self, job_id: int) -> List[Dict]:
        events = self.db.get_journal(job_id, limit=1000)
        timeline = []
        for event in reversed(events):
            try:
                data = json.loads(event['event_data']) if event['event_data'] else {}
            except (json.JSONDecodeError, TypeError):
                data = {}
            timeline.append({'time': event['created_at'], 'event': event['event_type'], 'data': data})
        return timeline
    
    def summarize_job(self, job_id: int) -> Dict:
        events = self.db.get_journal(job_id)
        job = self.db.get_job(job_id)
        
        summary = {
            'job_id': job_id,
            'status': job['status'] if job else 'unknown',
            'total_events': len(events),
            'errors': [],
            'interrupts': 0,
            'resumes': 0,
            'duration': None
        }
        
        start_time = None
        end_time = None
        
        for event in events:
            event_type = event['event_type']
            try:
                data = json.loads(event['event_data']) if event['event_data'] else {}
            except (json.JSONDecodeError, TypeError):
                data = {}
            
            if event_type == 'start' and not start_time:
                start_time = event['created_at']
            elif event_type in ('complete', 'error', 'paused'):
                end_time = event['created_at']
            elif event_type == 'error':
                summary['errors'].append(data.get('error', 'Unknown error'))
            elif event_type == 'interrupt_requested':
                summary['interrupts'] += 1
            elif event_type == 'resume':
                summary['resumes'] += 1
        
        if start_time and end_time:
            try:
                start = datetime.fromisoformat(start_time)
                end = datetime.fromisoformat(end_time)
                summary['duration'] = str(end - start)
            except ValueError:
                pass
        
        return summary
    
    def clear_old_entries(self, days: int = 30):
        cutoff = datetime.now().isoformat()
        self.db.conn.execute("""
            DELETE FROM journal WHERE created_at < datetime(?, '-' || ? || ' days')
        """, (cutoff, days))
        self.db.conn.commit()
