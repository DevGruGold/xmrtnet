# Autonomous Feedback Receiver - Adjusts priorities based on conversation learning
# This integrates with your existing xmrtnet autonomous system

import json
import os
from datetime import datetime
from typing import Dict, Any

class AutonomousFeedbackReceiver:
    """Receives feedback from conversations and adjusts autonomous priorities"""
    
    def __init__(self):
        self.current_priorities = {
            "analytics": 1.0,
            "development": 1.0,
            "marketing": 1.0,
            "mining": 1.0,
            "browser": 1.0,
            "social_media": 1.0
        }
        self.feedback_history = []
        self.task_queue = []
    
    def process_conversation_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Process feedback from conversation system and adjust priorities"""
        
        try:
            adjustments = feedback_data.get('adjustments', {})
            
            # Apply priority changes
            priority_changes = adjustments.get('priority_changes', {})
            for category, change in priority_changes.items():
                if category in self.current_priorities:
                    adjustment = change.get('weight_adjustment', 0)
                    self.current_priorities[category] += adjustment
                    
                    # Keep priorities within reasonable bounds
                    self.current_priorities[category] = max(0.1, min(2.0, self.current_priorities[category]))
                    
                    print(f"🎯 Adjusted {category} priority to {self.current_priorities[category]:.2f}")
            
            # Add new tasks to queue
            new_tasks = adjustments.get('new_tasks', [])
            for task in new_tasks:
                self.task_queue.append({
                    "task": task['task'],
                    "category": task['category'],
                    "priority": task['priority'],
                    "source": task['source'],
                    "added_at": datetime.now().isoformat()
                })
                
                print(f"📋 Added task: {task['task'][:50]}...")
            
            # Add focus areas
            focus_areas = adjustments.get('focus_areas', [])
            for area in focus_areas:
                category = area['category']
                if category in self.current_priorities:
                    boost = 0.3 if area['priority'] == 'high' else 0.1
                    self.current_priorities[category] += boost
                    self.current_priorities[category] = min(2.0, self.current_priorities[category])
                    
                    print(f"🔍 Boosted {category} focus by {boost}")
            
            # Record feedback
            self.feedback_history.append({
                "timestamp": datetime.now().isoformat(),
                "feedback_data": feedback_data,
                "priorities_after": self.current_priorities.copy()
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing feedback: {e}")
            return False
    
    def get_next_cycle_priorities(self) -> Dict[str, float]:
        """Get adjusted priorities for the next autonomous cycle"""
        return self.current_priorities.copy()
    
    def get_priority_adjusted_tasks(self) -> list:
        """Get tasks sorted by priority and category weight"""
        
        # Sort tasks by priority and category weight
        def task_score(task):
            priority_scores = {"high": 3, "medium": 2, "low": 1}
            base_score = priority_scores.get(task['priority'], 1)
            category_weight = self.current_priorities.get(task['category'], 1.0)
            return base_score * category_weight
        
        sorted_tasks = sorted(self.task_queue, key=task_score, reverse=True)
        return sorted_tasks[:10]  # Return top 10 priority tasks
    
    def generate_autonomous_cycle_config(self) -> Dict[str, Any]:
        """Generate configuration for the next autonomous cycle"""
        
        config = {
            "cycle_timestamp": datetime.now().isoformat(),
            "category_priorities": self.current_priorities,
            "priority_tasks": self.get_priority_adjusted_tasks(),
            "focus_adjustments": {
                "high_priority_categories": [
                    cat for cat, priority in self.current_priorities.items() 
                    if priority > 1.3
                ],
                "standard_categories": [
                    cat for cat, priority in self.current_priorities.items() 
                    if 0.8 <= priority <= 1.3
                ],
                "low_priority_categories": [
                    cat for cat, priority in self.current_priorities.items() 
                    if priority < 0.8
                ]
            }
        }
        
        return config

# Initialize the receiver
feedback_receiver = AutonomousFeedbackReceiver()

# Example integration function
def integrate_with_autonomous_cycle():
    """Example of how to integrate with existing autonomous cycle"""
    
    # Get current priorities
    priorities = feedback_receiver.get_next_cycle_priorities()
    
    print("🔄 AUTONOMOUS CYCLE PRIORITY ADJUSTMENTS")
    print("=" * 50)
    
    for category, priority in priorities.items():
        status = "🔥 HIGH" if priority > 1.3 else "⚡ NORMAL" if priority >= 0.8 else "💤 LOW"
        print(f"   {category.title()}: {priority:.2f} {status}")
    
    # Get priority tasks
    tasks = feedback_receiver.get_priority_adjusted_tasks()
    
    if tasks:
        print(f"\n📋 PRIORITY TASKS FROM USER FEEDBACK:")
        for i, task in enumerate(tasks[:5], 1):
            print(f"   {i}. [{task['category'].upper()}] {task['task'][:60]}...")
    
    return priorities, tasks

if __name__ == "__main__":
    # Test the receiver
    integrate_with_autonomous_cycle()
