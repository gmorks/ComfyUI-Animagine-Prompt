"""
Main node implementation for Animagine Prompt
"""

import os
from typing import Tuple, Dict, Any, List, Optional
import logging
from .csv_handler import CSVHandler

logger = logging.getLogger('AnimaginePrompt')

class AnimaginePromptNode:
    """
    A ComfyUI node that helps structure prompts according to specific guidelines
    """
    
    # Definición de tags predefinidas
    QUALITY_TAGS_GOOD = ["masterpiece", "best quality"]
    QUALITY_TAGS_BAD = ["low quality", "worst quality"]
    SCORE_TAGS_GOOD = ["high score", "great score", "good score"]
    SCORE_TAGS_BAD = ["average score", "bad score", "low score"]
    RATING_TAGS = ["safe", "sensitive", "nsfw", "explicit"]
    
    # Tags negativas por defecto según las guidelines
    DEFAULT_NEGATIVE_TAGS = [
        "low quality", "worst quality", "blurry", "bad anatomy",
        "bad hands", "text", "error", "missing fingers",
        "extra digit", "fewer digits", "cropped", "jpeg artifacts",
        "signature", "watermark", "username", "artist name"
    ]

    def __init__(self):
        self.csv_handler = CSVHandler()
        self.last_csv_path = None
        
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "positive_prompt": ("STRING", {"multiline": True}),
                "negative_prompt": ("STRING", {"multiline": True}),
                # Good tags controls
                "use_good_tags": ("BOOLEAN", {"default": True}),
                "quality_good": (cls.QUALITY_TAGS_GOOD,),
                "score_good": (cls.SCORE_TAGS_GOOD,),
                # Bad tags controls
                "use_bad_tags": ("BOOLEAN", {"default": False}),
                "quality_bad": (cls.QUALITY_TAGS_BAD,),
                "score_bad": (cls.SCORE_TAGS_BAD,),
                # Year control
                "use_year": ("BOOLEAN", {"default": False}),
                "year": ("INT", {"default": 2024}),
                # Rating control
                "use_rating": ("BOOLEAN", {"default": False}),
                "rating": (cls.RATING_TAGS,),
                # CSV control
                "use_csv": ("BOOLEAN", {"default": False}),
                "csv_path": ("STRING", {"default": ""}),
                "csv_index": ("INT", {"default": 0, "min": 0, "max": 9999})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("final_positive_prompt", "final_negative_prompt")
    FUNCTION = "generate_prompt"
    CATEGORY = "prompt"

    def _build_good_tags(self, quality_good: str, score_good: str) -> str:
        """Construye la sección de tags positivas"""
        tags = []
        if quality_good:
            tags.append(quality_good)
        if score_good:
            tags.append(score_good)
        return ", ".join(tags)

    def _build_bad_tags(self, quality_bad: str, score_bad: str) -> str:
        """Construye la sección de tags negativas"""
        tags = []
        if quality_bad:
            tags.append(quality_bad)
        if score_bad:
            tags.append(score_bad)
        return ", ".join(tags)

    def _get_csv_entry(self, csv_path: str, index: int) -> Optional[str]:
        """Obtiene y formatea una entrada del CSV"""
        if self.last_csv_path != csv_path:
            self.csv_handler.load_csv(csv_path)
            self.last_csv_path = csv_path
            
        entry = self.csv_handler.get_entry(index)
        if entry:
            return f"{entry['gender']}, {entry['character']}, {entry['copyright']}"
        return None

    def generate_prompt(
        self,
        positive_prompt: str,
        negative_prompt: str,
        use_good_tags: bool,
        quality_good: str,
        score_good: str,
        use_bad_tags: bool,
        quality_bad: str,
        score_bad: str,
        use_year: bool,
        year: int,
        use_rating: bool,
        rating: str,
        use_csv: bool,
        csv_path: str,
        csv_index: int
    ) -> Tuple[str, str]:
        """
        Genera los prompts finales basados en los parámetros proporcionados
        """
        try:
            # Lista para construir el prompt positivo
            positive_parts = []
            
            # Agregar tags positivas si están activadas
            if use_good_tags:
                good_tags = self._build_good_tags(quality_good, score_good)
                if good_tags:
                    positive_parts.append(good_tags)
            
            # Agregar bad tags al prompt positivo si están activadas
            if use_bad_tags:
                bad_tags = self._build_bad_tags(quality_bad, score_bad)
                if bad_tags:
                    positive_parts.append(bad_tags)
            
            # Agregar entrada del CSV si está activado
            if use_csv and csv_path:
                csv_entry = self._get_csv_entry(csv_path, csv_index)
                if csv_entry:
                    positive_parts.append(csv_entry)

            # Agregar el prompt base del usuario
            if positive_prompt:
                positive_parts.append(positive_prompt)
            
            # Agregar year tag si está activado
            if use_year:
                positive_parts.append(f"year {year}")
            
            # Agregar rating si está activado
            if use_rating:
                positive_parts.append(rating)
            
            # Construir el prompt negativo
            negative_parts = []
            
            # Agregar tags negativas por defecto
            negative_parts.extend(self.DEFAULT_NEGATIVE_TAGS)
            
            # Agregar el prompt negativo del usuario
            if negative_prompt:
                negative_parts.append(negative_prompt)
            
            # Unir todas las partes
            final_positive = ", ".join(part for part in positive_parts if part)
            final_negative = ", ".join(part for part in negative_parts if part)
            
            return final_positive, final_negative
            
        except Exception as e:
            logger.error(f"Error generating prompt: {str(e)}")
            raise e