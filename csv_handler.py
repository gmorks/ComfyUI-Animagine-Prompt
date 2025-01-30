"""
CSV handling functionality for Animagine Prompt Node
"""

import pandas as pd
from typing import Optional, Dict
import os
import time
from .logger import logger

class CSVHandler:
    """
    Handles loading and processing of CSV files containing character data
    """
    
    REQUIRED_COLUMNS = ['GENDER', 'CHARACTER', 'COPYRIGHT']
    
    def __init__(self):
        self.current_data = None
        self.cache = {}
    
    def validate_csv_structure(self, filepath: str) -> bool:
        """
        Validates if the CSV file has the required structure
        """
        try:
            if not os.path.exists(filepath):
                logger.log_error(
                    FileNotFoundError(f"CSV file not found: {filepath}"),
                    "CSV Validation",
                    {"filepath": filepath}
                )
                return False
                
            df = pd.read_csv(filepath)
            logger.log_csv_operation(
                "Validation",
                filepath,
                {"columns_found": df.columns.tolist()}
            )
            
            missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
            if missing_columns:
                logger.log_error(
                    ValueError("Missing required columns"),
                    "CSV Validation",
                    {"missing_columns": missing_columns}
                )
                return False
                
            return True
            
        except Exception as e:
            logger.log_error(e, "CSV Validation", {"filepath": filepath})
            return False
    
    def load_csv(self, filepath: str) -> Optional[pd.DataFrame]:
        """
        Loads CSV file with basic caching
        """
        try:
            start_time = time.time()
            
            if filepath in self.cache:
                logger.log_csv_operation(
                    "Cache Hit",
                    filepath,
                    {"cache_size": len(self.cache)}
                )
                return self.cache[filepath]
            
            if not self.validate_csv_structure(filepath):
                return None
            
            df = pd.read_csv(filepath)
            self.cache[filepath] = df
            self.current_data = df
            
            end_time = time.time()
            logger.log_performance(
                "CSV Load",
                start_time,
                end_time,
                {
                    "filepath": filepath,
                    "rows": len(df),
                    "cached": True
                }
            )
            
            return df
            
        except Exception as e:
            logger.log_error(e, "CSV Load", {"filepath": filepath})
            return None
    
    def get_entry(self, index: int) -> Optional[Dict[str, str]]:
        """
        Gets a specific entry from the loaded CSV
        """
        try:
            if self.current_data is None:
                logger.log_error(
                    ValueError("No CSV data loaded"),
                    "Get Entry",
                    {"index": index}
                )
                return None
            
            if index >= len(self.current_data):
                logger.log_error(
                    IndexError(f"Index {index} out of bounds"),
                    "Get Entry",
                    {
                        "index": index,
                        "max_index": len(self.current_data) - 1
                    }
                )
                return None
                
            row = self.current_data.iloc[index]
            entry = {
                'gender': row['GENDER'],
                'character': row['CHARACTER'],
                'copyright': row['COPYRIGHT']
            }
            
            logger.log_csv_operation(
                "Get Entry",
                None,
                {"index": index, "entry": entry}
            )
            
            return entry
            
        except Exception as e:
            logger.log_error(e, "Get Entry", {"index": index})
            return None