"""
CSV handling functionality for Animagine Prompt Node
"""

import pandas as pd
import logging
from typing import Optional, List, Dict
import os

logger = logging.getLogger('AnimaginePrompt')

class CSVHandler:
    """
    Handles loading and processing of CSV files containing character data
    """
    
    REQUIRED_COLUMNS = ['GENDER', 'CHARACTER', 'COPYRIGHT']  # Notar las mayúsculas
    
    def __init__(self):
        self.current_data = None
        self.cache = {}
    
    def validate_csv_structure(self, filepath: str) -> bool:
        """
        Validates if the CSV file has the required structure
        """
        try:
            if not os.path.exists(filepath):
                logger.error(f"CSV file not found: {filepath}")
                return False
                
            df = pd.read_csv(filepath)
            logger.info(f"CSV columns found: {df.columns.tolist()}")
            
            missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
            if missing_columns:
                logger.error(f"Missing required columns: {missing_columns}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating CSV structure: {str(e)}")
            return False
    
    def load_csv(self, filepath: str) -> Optional[pd.DataFrame]:
        """
        Loads CSV file with basic caching
        """
        try:
            if filepath in self.cache:
                return self.cache[filepath]
            
            if not self.validate_csv_structure(filepath):
                logger.error(f"Invalid CSV structure in file: {filepath}")
                return None
            
            df = pd.read_csv(filepath)
            self.cache[filepath] = df
            self.current_data = df
            return df
            
        except Exception as e:
            logger.error(f"Error loading CSV file: {str(e)}")
            return None
    
    def get_entry(self, index: int) -> Optional[Dict[str, str]]:
        """
        Gets a specific entry from the loaded CSV
        """
        try:
            if self.current_data is None:
                return None
            
            if index >= len(self.current_data):
                logger.error(f"Index {index} out of bounds for CSV with {len(self.current_data)} entries")
                return None
                
            row = self.current_data.iloc[index]
            return {
                'gender': row['GENDER'],
                'character': row['CHARACTER'],
                'copyright': row['COPYRIGHT']
            }
        except Exception as e:
            logger.error(f"Error getting CSV entry: {str(e)}")
            return None