import json
import os
from datetime import datetime
from typing import List, Dict
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class TaskManager:
    def __init__(self):
        self.tasks_file = os.path.join(config.DATA_DIR, "tasks.json")
        self.tasks = self.load_tasks()
    
    def load_tasks(self) -> List[Dict]:
        """Load tasks from file"""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_tasks(self):
        """Save tasks to file"""
        try:
            with open(self.tasks_file, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def add_task(self, text: str, priority: str = "Normal") -> Dict:
        """Add a new task"""
        task = {
            'id': len(self.tasks) + 1,
            'text': text,
            'priority': priority,
            'completed': False,
            'created_at': datetime.now().isoformat()
        }
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def complete_task(self, task_id: int) -> bool:
        """Mark task as completed"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                self.save_tasks()
                return True
        return False
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        self.tasks = [t for t in self.tasks if t['id'] != task_id]
        self.save_tasks()
        return True
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks"""
        return [t for t in self.tasks if not t['completed']]
    
    def get_completed_tasks(self) -> List[Dict]:
        """Get all completed tasks"""
        return [t for t in self.tasks if t['completed']]
