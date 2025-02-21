import os
import random
import time
from pathlib import Path
from dynamicprompts.generators import RandomPromptGenerator

# Cache to store text lines per file
text_file_cache = {}
# Dictionary to track last execution time for each node instance
last_execution_time = {}

class MultilineTextInput:
    """
    A node that provides a multiline text input and outputs the entered text as a string.
    Now supports dynamicprompts syntax for variants and wildcards.
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
                }),
                "use_dynamic_prompts": ("BOOLEAN", {
                    "default": True,
                    "label": "Process Dynamic Prompts"
                }),
                "seed": ("INT", {
                    "default": -1, 
                    "min": -1,
                    "max": 2**32 - 1,
                    "display": "number",
                    "tooltip": "Seed for dynamic prompts generation (-1 for random)"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "output_text"
    
    def output_text(self, text, use_dynamic_prompts, seed):
        """
        Processes and returns the text, using dynamicprompts if enabled.
        
        Args:
            text (str): Input text from the multiline input
            use_dynamic_prompts (bool): Whether to process with dynamicprompts
            seed (int): Seed for random generation, -1 for random seed
            
        Returns:
            tuple: Contains the processed text as a string
        """
        if not use_dynamic_prompts:
            return (text,)
        
        try:
            # Use current time as unique identifier for this execution
            node_instance_id = id(self)
            current_time = time.time()
            last_execution_time[node_instance_id] = current_time
            
            # Set up seed
            if seed == -1:
                actual_seed = random.randint(0, 2**32 - 1)
            else:
                actual_seed = seed
                
            # Set random seed for reproducible results
            random.seed(actual_seed)
            
            # Process with dynamicprompts
            generator = RandomPromptGenerator()
            processed_text = generator.generate(text, num_images=1)[0]
            
            # Reset random seed to avoid affecting other randomness
            random.seed(None)
            
            return (processed_text,)
        except Exception as e:
            return (f"Dynamic Prompts Error: {str(e)}\nOriginal text: {text}",)


class TextFileLoader:
    """
    A node that loads a text file and returns a specific line or a random line.
    Ensures random choices are refreshed on each workflow execution.
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
                }),
                "seed": ("INT", {
                    "default": -1, 
                    "min": -1,
                    "max": 2**32 - 1,
                    "display": "number",
                    "tooltip": "Seed for random selection (-1 for time-based seed)"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("selected_line",)
    FUNCTION = "load_text_line"
    
    def load_text_line(self, file_path, line_index, seed):
        """
        Loads a text file and returns a specific line or a random line.
        Ensures new random choices on each workflow execution.
        
        Args:
            file_path (str): Path to the text file
            line_index (int): Index of the line to select, or -1 for random selection
            seed (int): Seed for random selection, -1 for time-based seed
            
        Returns:
            tuple: Contains the selected line as a string
        """
        try:
            # Use current time as unique identifier for this execution
            node_instance_id = id(self)
            current_time = time.time()
            last_execution_time[node_instance_id] = current_time
            
            # Normalize path
            file_path = os.path.normpath(file_path.strip())
            
            # Check if file exists
            if not os.path.isfile(file_path):
                return (f"Error: File not found at {file_path}",)
            
            # Get file modification time
            file_mod_time = os.path.getmtime(file_path)
            
            # Use cache if available and file hasn't been modified
            cache_key = file_path
            if cache_key in text_file_cache and text_file_cache[cache_key]["mod_time"] == file_mod_time:
                lines = text_file_cache[cache_key]["lines"]
            else:
                # Read file and store in cache
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = [line.rstrip() for line in f if line.strip()]
                text_file_cache[cache_key] = {
                    "lines": lines,
                    "mod_time": file_mod_time
                }
            
            # Check if file is empty
            if not lines:
                return ("Error: File is empty",)
            
            # Select line
            if line_index == -1:
                # Set up random seed for consistent but different choices
                if seed == -1:
                    # Time-based seed ensures different choice on each run
                    random_seed = int(current_time * 1000) % (2**32)
                else:
                    # User-provided seed for reproducible randomness
                    random_seed = seed
                    
                # Set the seed for this selection
                random.seed(random_seed)
                
                # Random selection
                selected_line = random.choice(lines)
                
                # Reset random seed to avoid affecting other randomness
                random.seed(None)
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