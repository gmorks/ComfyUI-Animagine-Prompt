"""
state_manager.py - State management for ComfyUI Animagine Prompt Node
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
from .logger import logger

class StateManager:
    """
    Manages the persistence and restoration of node states
    """
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.state_file = os.path.join(config_dir, "animagine_state.json")
        self.history_file = os.path.join(config_dir, "csv_history.json")
        self.current_state: Dict[str, Any] = {}
        self.csv_history: Dict[str, Dict[str, Any]] = {}
        self._initialize()
        
    def _initialize(self) -> None:
        """Initialize the state system"""
        # Create config directory if it doesn't exist
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
        # Load existing state if available
        self._load_state()
        self._load_csv_history()
    
    def _load_state(self) -> None:
        """Load the last saved state"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.current_state = json.load(f)
                logger.logger.debug("State loaded successfully")
        except Exception as e:
            logger.log_error(e, "State Loading")
            self.current_state = {}
    
    def _load_csv_history(self) -> None:
        """Load CSV usage history"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.csv_history = json.load(f)
                logger.logger.debug("CSV history loaded successfully")
        except Exception as e:
            logger.log_error(e, "CSV History Loading")
            self.csv_history = {}
    
    def _save_state(self) -> None:
        """Save current state to file"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_state, f, indent=2)
            logger.logger.debug("State saved successfully")
        except Exception as e:
            logger.log_error(e, "State Saving")
    
    def _save_csv_history(self) -> None:
        """Save CSV history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.csv_history, f, indent=2)
            logger.logger.debug("CSV history saved successfully")
        except Exception as e:
            logger.log_error(e, "CSV History Saving")
    
    def update_state(self, new_state: Dict[str, Any]) -> None:
        """
        Update the current state with new values
        """
        old_state = self.current_state.copy()
        self.current_state.update(new_state)
        self._save_state()
        
        logger.log_state_change(
            "Node State",
            old_state,
            self.current_state
        )
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state
        """
        return self.current_state
    
    def reset_state(self) -> None:
        """
        Reset state to default values
        """
        default_state = {
            "use_good_tags": True,
            "use_bad_tags": False,
            "use_year": False,
            "year": 2024,
            "use_rating": False,
            "rating": "safe",
            "use_csv": False,
            "csv_path": "",
            "csv_index": 0
        }
        
        old_state = self.current_state.copy()
        self.current_state = default_state
        self._save_state()
        
        logger.log_state_change(
            "State Reset",
            old_state,
            default_state
        )
    
    def add_csv_to_history(self, filepath: str, entry_count: int) -> None:
        """
        Add a CSV file to the usage history
        """
        if filepath not in self.csv_history:
            self.csv_history[filepath] = {
                "first_used": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat(),
                "use_count": 1,
                "entry_count": entry_count
            }
        else:
            self.csv_history[filepath].update({
                "last_used": datetime.now().isoformat(),
                "use_count": self.csv_history[filepath]["use_count"] + 1,
                "entry_count": entry_count
            })
        
        self._save_csv_history()
        logger.logger.debug(f"Added CSV to history: {filepath}")
    
    def get_csv_history(self, limit: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get CSV usage history, optionally limited to the most recent entries
        """
        if not limit:
            return self.csv_history
            
        # Sort by last_used date and return limited number
        sorted_history = dict(
            sorted(
                self.csv_history.items(),
                key=lambda x: x[1]["last_used"],
                reverse=True
            )[:limit]
        )
        return sorted_history
    
    def clear_csv_history(self) -> None:
        """
        Clear the CSV usage history
        """
        old_history = self.csv_history.copy()
        self.csv_history = {}
        self._save_csv_history()
        
        logger.log_state_change(
            "CSV History Clear",
            old_history,
            {}
        )

# Singleton instance
state_manager = StateManager()