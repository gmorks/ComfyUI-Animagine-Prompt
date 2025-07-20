"""
logger.py - Logging system for ComfyUI Animagine Prompt Node
"""

import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any

# Get the directory where this module is located
NODE_DIR = os.path.dirname(os.path.realpath(__file__))

class AnimagineLogger:
    """
    Custom logger for the Animagine Prompt Node with enhanced debugging capabilities
    """
    
    def __init__(self, log_dir: str = "logs"):
        # Use absolute path relative to the node directory
        self.log_dir = os.path.join(NODE_DIR, log_dir)
        self.logger = None
        self.setup_logger()
        
    def setup_logger(self) -> None:
        """
        Initialize the logger with both file and console handlers
        """
        # Create logs directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        # Create logger
        self.logger = logging.getLogger('AnimaginePrompt')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers if any
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # File handler - detailed logging
        log_file = os.path.join(
            self.log_dir,
            f"animagine_prompt_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler - important messages only
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def log_prompt_generation(
        self,
        positive_prompt: str,
        negative_prompt: str,
        params: Dict[str, Any]
    ) -> None:
        """
        Log prompt generation details
        """
        self.logger.debug("=== Prompt Generation Started ===")
        self.logger.debug(f"Parameters used: {params}")
        self.logger.debug(f"Base positive prompt: {positive_prompt}")
        self.logger.debug(f"Base negative prompt: {negative_prompt}")
    
    def log_csv_operation(
        self,
        operation: str,
        filepath: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log CSV-related operations
        """
        self.logger.debug(f"=== CSV Operation: {operation} ===")
        if filepath:
            self.logger.debug(f"File: {filepath}")
        if details:
            self.logger.debug(f"Details: {details}")
    
    def log_error(
        self,
        error: Exception,
        context: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log errors with context and details
        """
        self.logger.error(f"=== Error in {context} ===")
        self.logger.error(f"Error type: {type(error).__name__}")
        self.logger.error(f"Error message: {str(error)}")
        if details:
            self.logger.error(f"Additional details: {details}")
    
    def log_performance(
        self,
        operation: str,
        start_time: float,
        end_time: float,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log performance metrics
        """
        duration = end_time - start_time
        self.logger.debug(f"=== Performance: {operation} ===")
        self.logger.debug(f"Duration: {duration:.4f} seconds")
        if details:
            self.logger.debug(f"Details: {details}")
    
    def log_state_change(
        self,
        component: str,
        old_state: Any,
        new_state: Any
    ) -> None:
        """
        Log state changes in the node
        """
        self.logger.debug(f"=== State Change: {component} ===")
        self.logger.debug(f"Old state: {old_state}")
        self.logger.debug(f"New state: {new_state}")

# Singleton instance
logger = AnimagineLogger()