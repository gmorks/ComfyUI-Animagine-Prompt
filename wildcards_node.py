import os
import random
from pathlib import Path

# Cache to store text lines per file
text_file_cache = {}

class MultilineTextInput:
    """
    A node that provides a multiline text input and outputs the entered text as a string.
    """
    CATEGORY = "animagine/text"
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True, 
                    "default": "", 
                    "placeholder": "Enter your text here..."
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "output_text"
    
    def output_text(self, text):
        """
        Returns the input text as is.
        
        Args:
            text (str): Input text from the multiline input
            
        Returns:
            tuple: Contains the input text as a string
        """
        return (text,)


class TextFileLoader:
    """
    A node that loads a text file and returns a specific line or a random line.
    """
    CATEGORY = "animagine/text"
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "file_path": ("STRING", {
                    "default": "", 
                    "placeholder": "Path to text file"
                }),
                "line_index": ("INT", {
                    "default": -1, 
                    "min": -1, 
                    "display": "number",
                    "tooltip": "Index of line to select (-1 for random)"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("selected_line",)
    FUNCTION = "load_text_line"
    
    def load_text_line(self, file_path, line_index):
        """
        Loads a text file and returns a specific line or a random line.
        
        Args:
            file_path (str): Path to the text file
            line_index (int): Index of the line to select, or -1 for random selection
            
        Returns:
            tuple: Contains the selected line as a string
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IndexError: If the line index is out of range
        """
        try:
            # Normalize path
            file_path = os.path.normpath(file_path.strip())
            
            # Check if file exists
            if not os.path.isfile(file_path):
                return (f"Error: File not found at {file_path}",)
            
            # Use cache if available
            if file_path in text_file_cache:
                lines = text_file_cache[file_path]
            else:
                # Read file and store in cache
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = [line.rstrip() for line in f if line.strip()]
                text_file_cache[file_path] = lines
            
            # Check if file is empty
            if not lines:
                return ("Error: File is empty",)
            
            # Select line
            if line_index == -1:
                # Random selection
                selected_line = random.choice(lines)
            else:
                # Check if index is valid
                if line_index < 0 or line_index >= len(lines):
                    return (f"Error: Line index {line_index} out of range (0-{len(lines)-1})",)
                selected_line = lines[line_index]
            
            return (selected_line,)
            
        except Exception as e:
            return (f"Error loading file: {str(e)}",)


# Node class mappings for ComfyUI registration
NODE_CLASS_MAPPINGS = {
    "MultilineTextInput": MultilineTextInput,
    "TextFileLoader": TextFileLoader
}

# Display names for better UI presentation
NODE_DISPLAY_NAME_MAPPINGS = {
    "MultilineTextInput": "Multiline Text Input",
    "TextFileLoader": "Wildcards Text File Loader"
}