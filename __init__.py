"""Animagine Prompt Node for ComfyUI
A node designed to help structure prompts according to specific guidelines
"""
import os
import logging
from .animagine_node import AnimaginePromptNode
from .wildcards_node import MultilineTextInput, TextFileLoader, MultiWildcardLoader
from .api_routes import define_routes

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AnimaginePrompt')

# Base directory of the node
NODE_DIR = os.path.dirname(os.path.realpath(__file__))
SAMPLE_DATA_DIR = os.path.join(NODE_DIR, "sample_data")

# Ensure the sample_data directory exists
if not os.path.exists(SAMPLE_DATA_DIR):
    os.makedirs(SAMPLE_DATA_DIR)

# Node class mappings for registration
NODE_CLASS_MAPPINGS = {
    "AnimaginePrompt": AnimaginePromptNode,
    "MultilineTextInput": MultilineTextInput,
    "TextFileLoader": TextFileLoader,
    "MultiWildcardLoader": MultiWildcardLoader
}

# Display name mappings for nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "AnimaginePrompt": "Animagine Prompt",
    "MultilineTextInput": "Multiline Text Input",
    "TextFileLoader": "Wildcards Text File Loader",
    "MultiWildcardLoader": "Multi-Wildcard Loader"
}

# Web directory configuration for JavaScript extensions
WEB_DIRECTORY = "./web"

# Register API routes directly
define_routes()
logger.info("[Animagine Prompt] API routes initialized")

__version__ = "1.6.0"
