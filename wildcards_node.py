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
    CATEGORY = "Animagine-Prompt"
    
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
    CATEGORY = "Animagine-Prompt"
    
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


class MultiWildcardLoader:
    """
    A node that loads multiple wildcard files and concatenates their selected lines.
    Supports template mode with placeholder syntax like {filename.txt}.
    Uses line_index system like TextFileLoader for consistent selection.
    """
    CATEGORY = "Animagine-Prompt"
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mode": (["slots", "template"], {
                    "default": "slots",
                    "tooltip": "Slots: Use individual wildcard slots. Template: Use template with {filename.txt} placeholders"
                }),
                "template_text": ("STRING", {
                    "multiline": True,
                    "default": "{expressions.txt} {poses.txt} wearing {clothing.txt} in a {scenarios.txt}",
                    "placeholder": "Template with {filename.txt} placeholders"
                }),
                "separator": ("STRING", {
                    "default": ", ",
                    "placeholder": "Separator between wildcards (slots mode only)"
                }),
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2**32 - 1,
                    "display": "number",
                    "tooltip": "Seed for random selection (-1 for time-based seed)"
                })
            },
            "optional": {
                # Wildcard slot 1
                "wildcard_1_path": ("STRING", {
                    "default": "",
                    "placeholder": "Path to first wildcard file"
                }),
                "wildcard_1_enabled": ("BOOLEAN", {
                    "default": True,
                    "label": "Enable Wildcard 1"
                }),
                "wildcard_1_line_index": ("INT", {
                    "default": -1,
                    "min": -1,
                    "display": "number",
                    "tooltip": "Line index for wildcard 1 (-1 for random)"
                }),
                
                # Wildcard slot 2
                "wildcard_2_path": ("STRING", {
                    "default": "",
                    "placeholder": "Path to second wildcard file"
                }),
                "wildcard_2_enabled": ("BOOLEAN", {
                    "default": True,
                    "label": "Enable Wildcard 2"
                }),
                "wildcard_2_line_index": ("INT", {
                    "default": -1,
                    "min": -1,
                    "display": "number",
                    "tooltip": "Line index for wildcard 2 (-1 for random)"
                }),
                
                # Wildcard slot 3
                "wildcard_3_path": ("STRING", {
                    "default": "",
                    "placeholder": "Path to third wildcard file"
                }),
                "wildcard_3_enabled": ("BOOLEAN", {
                    "default": True,
                    "label": "Enable Wildcard 3"
                }),
                "wildcard_3_line_index": ("INT", {
                    "default": -1,
                    "min": -1,
                    "display": "number",
                    "tooltip": "Line index for wildcard 3 (-1 for random)"
                }),
                
                # Wildcard slot 4
                "wildcard_4_path": ("STRING", {
                    "default": "",
                    "placeholder": "Path to fourth wildcard file"
                }),
                "wildcard_4_enabled": ("BOOLEAN", {
                    "default": True,
                    "label": "Enable Wildcard 4"
                }),
                "wildcard_4_line_index": ("INT", {
                    "default": -1,
                    "min": -1,
                    "display": "number",
                    "tooltip": "Line index for wildcard 4 (-1 for random)"
                }),
                
                # Wildcard slot 5
                "wildcard_5_path": ("STRING", {
                    "default": "",
                    "placeholder": "Path to fifth wildcard file"
                }),
                "wildcard_5_enabled": ("BOOLEAN", {
                    "default": True,
                    "label": "Enable Wildcard 5"
                }),
                "wildcard_5_line_index": ("INT", {
                    "default": -1,
                    "min": -1,
                    "display": "number",
                    "tooltip": "Line index for wildcard 5 (-1 for random)"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("combined_text", "preview_text")
    FUNCTION = "load_multiple_wildcards"
    
    @classmethod
    def IS_CHANGED(s, mode, template_text, separator, seed, **kwargs):
        """
        This method tells ComfyUI when the node output should be recalculated.
        It helps with real-time preview by making the output update when parameters change.
        """
        # Create a hash of all input parameters to detect changes
        import hashlib
        
        # Combine all parameters into a string
        params_str = f"{mode}_{template_text}_{separator}_{seed}"
        
        # Add wildcard parameters
        for i in range(1, 6):
            path = kwargs.get(f"wildcard_{i}_path", "")
            enabled = kwargs.get(f"wildcard_{i}_enabled", True)
            line_index = kwargs.get(f"wildcard_{i}_line_index", -1)
            params_str += f"_{path}_{enabled}_{line_index}"
        
        # Return hash of parameters - when this changes, ComfyUI will recalculate
        return hashlib.md5(params_str.encode()).hexdigest()
    
    def _resolve_file_path(self, file_path):
        """
        Resolve file path, trying relative to project directory first, then absolute.
        
        Args:
            file_path (str): The file path to resolve
            
        Returns:
            str: Resolved absolute path or original path if not found
        """
        if not file_path or not file_path.strip():
            return None
            
        file_path = file_path.strip()
        
        # If already absolute and exists, return as-is
        if os.path.isabs(file_path) and os.path.isfile(file_path):
            return file_path
            
        # Try relative to current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        relative_path = os.path.join(script_dir, file_path)
        if os.path.isfile(relative_path):
            return relative_path
            
        # Try relative to example_files directory
        example_files_path = os.path.join(script_dir, "example_files", file_path)
        if os.path.isfile(example_files_path):
            return example_files_path
            
        # Return original path (will cause error in load_text_line if not found)
        return file_path
    
    def _load_wildcard_line(self, file_path, line_index, seed):
        """
        Load a line from a wildcard file using the TextFileLoader logic.
        
        Args:
            file_path (str): Path to the wildcard file
            line_index (int): Index of line to select (-1 for random)
            seed (int): Seed for random selection
            
        Returns:
            str: Selected line or error message
        """
        try:
            resolved_path = self._resolve_file_path(file_path)
            if not resolved_path:
                return f"Error: Empty file path"
                
            # Normalize path
            resolved_path = os.path.normpath(resolved_path)
            
            # Check if file exists
            if not os.path.isfile(resolved_path):
                return f"Error: File not found at {resolved_path}"
            
            # Get file modification time
            file_mod_time = os.path.getmtime(resolved_path)
            
            # Use cache if available and file hasn't been modified
            cache_key = resolved_path
            if cache_key in text_file_cache and text_file_cache[cache_key]["mod_time"] == file_mod_time:
                lines = text_file_cache[cache_key]["lines"]
            else:
                # Read file and store in cache
                with open(resolved_path, 'r', encoding='utf-8') as f:
                    lines = [line.rstrip() for line in f if line.strip()]
                text_file_cache[cache_key] = {
                    "lines": lines,
                    "mod_time": file_mod_time
                }
            
            # Check if file is empty
            if not lines:
                return f"Error: File {os.path.basename(resolved_path)} is empty"
            
            # Select line
            if line_index == -1:
                # Set up random seed for consistent but different choices
                current_time = time.time()
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
                    return f"Error: Line index {line_index} out of range (0-{len(lines)-1}) for {os.path.basename(resolved_path)}"
                selected_line = lines[line_index]
            
            return selected_line
            
        except Exception as e:
            return f"Error loading {os.path.basename(file_path) if file_path else 'file'}: {str(e)}"
    
    def load_multiple_wildcards(self, mode, template_text, separator, seed, **kwargs):
        """
        Load multiple wildcard files and combine their content.
        
        Args:
            mode (str): "slots" or "template" mode
            template_text (str): Template text with {filename.txt} placeholders
            separator (str): Separator between wildcards (slots mode only)
            seed (int): Seed for random selection
            **kwargs: Wildcard paths, enabled flags, and line indices
            
        Returns:
            tuple: Contains the combined text and preview text
        """
        try:
            # Use current time as unique identifier for this execution
            node_instance_id = id(self)
            current_time = time.time()
            last_execution_time[node_instance_id] = current_time
            
            if mode == "template":
                return self._process_template_mode(template_text, seed)
            else:
                return self._process_slots_mode(separator, seed, **kwargs)
                
        except Exception as e:
            error_msg = f"Multi-Wildcard Error: {str(e)}"
            return (error_msg, error_msg)
    
    def _process_template_mode(self, template_text, seed):
        """
        Process template mode by finding {filename.txt} placeholders and replacing them.
        
        Args:
            template_text (str): Template with placeholders
            seed (int): Seed for random selection
            
        Returns:
            tuple: Processed template text and preview text
        """
        import re
        
        # Find all {filename.txt} patterns
        placeholder_pattern = r'\{([^}]+)\}'
        placeholders = re.findall(placeholder_pattern, template_text)
        
        if not placeholders:
            return (template_text, template_text)
        
        result_text = template_text
        
        # Process each placeholder
        for i, filename in enumerate(placeholders):
            # Calculate seed for this wildcard (offset by position)
            if seed == -1:
                wildcard_seed = -1
            else:
                wildcard_seed = seed + i
                
            # Load wildcard line (always random selection in template mode)
            selected_line = self._load_wildcard_line(filename, -1, wildcard_seed)
            
            # Replace the first occurrence of this placeholder
            placeholder = '{' + filename + '}'
            result_text = result_text.replace(placeholder, selected_line, 1)
        
        return (result_text, result_text)
    
    def _process_slots_mode(self, separator, seed, **kwargs):
        """
        Process slots mode by loading enabled wildcards and joining with separator.
        
        Args:
            separator (str): Separator between wildcards
            seed (int): Seed for random selection
            **kwargs: Wildcard configuration
            
        Returns:
            tuple: Combined wildcard text and preview text
        """
        selected_lines = []
        
        # Process each wildcard slot
        for i in range(1, 6):  # 5 slots
            path_key = f"wildcard_{i}_path"
            enabled_key = f"wildcard_{i}_enabled"
            line_index_key = f"wildcard_{i}_line_index"
            
            # Get values with defaults
            file_path = kwargs.get(path_key, "")
            enabled = kwargs.get(enabled_key, True)
            line_index = kwargs.get(line_index_key, -1)
            
            # Skip if not enabled or no path
            if not enabled or not file_path or not file_path.strip():
                continue
            
            # Calculate seed for this wildcard (offset by position)
            if seed == -1:
                wildcard_seed = -1
            else:
                wildcard_seed = seed + i
            
            # Load wildcard line
            selected_line = self._load_wildcard_line(file_path, line_index, wildcard_seed)
            
            # Only add if not an error message
            if not selected_line.startswith("Error:"):
                selected_lines.append(selected_line)
            else:
                # Include error in output for debugging
                selected_lines.append(selected_line)
        
        # Combine with separator
        if not selected_lines:
            no_wildcards_msg = "No wildcards loaded"
            return (no_wildcards_msg, no_wildcards_msg)
        
        combined_text = separator.join(selected_lines)
        return (combined_text, combined_text)


# Node class mappings for ComfyUI registration
NODE_CLASS_MAPPINGS = {
    "MultilineTextInput": MultilineTextInput,
    "TextFileLoader": TextFileLoader,
    "MultiWildcardLoader": MultiWildcardLoader
}

# Display names for better UI presentation
NODE_DISPLAY_NAME_MAPPINGS = {
    "MultilineTextInput": "Multiline Text Input",
    "TextFileLoader": "Wildcards Text File Loader",
    "MultiWildcardLoader": "Multi-Wildcard Loader"
}