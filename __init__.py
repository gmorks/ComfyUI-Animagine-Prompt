"""
Animagine Prompt Node for ComfyUI
A node designed to help structure prompts according to specific guidelines
"""

import os
import logging
from .animagine_node import AnimaginePromptNode

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AnimaginePrompt')

# Directorio base del nodo
NODE_DIR = os.path.dirname(os.path.realpath(__file__))
SAMPLE_DATA_DIR = os.path.join(NODE_DIR, "sample_data")

# Asegurarse de que existe el directorio de sample_data
if not os.path.exists(SAMPLE_DATA_DIR):
    os.makedirs(SAMPLE_DATA_DIR)

# Mapping para el registro del nodo
NODE_CLASS_MAPPINGS = {
    "AnimaginePrompt": AnimaginePromptNode
}

# Mapping para el nombre de visualización
NODE_DISPLAY_NAME_MAPPINGS = {
    "AnimaginePrompt": "Animagine Prompt"
}

__version__ = "1.0.0"