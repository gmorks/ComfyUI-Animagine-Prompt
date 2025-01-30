"""
Main node implementation for Animagine Prompt
"""

import os
import time
from typing import Tuple, Dict, Any, List, Optional
from .csv_handler import CSVHandler
from .logger import logger
from .state_manager import state_manager

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
        # Load last state or use defaults
        self.current_state = state_manager.get_state()
        if not self.current_state:
            state_manager.reset_state()
            self.current_state = state_manager.get_state()
        logger.logger.info("AnimaginePromptNode initialized with saved state")
        
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        # Get defaults from state manager or use class defaults
        state = state_manager.get_state()
        return {
            "required": {
                "positive_prompt": ("STRING", {"multiline": True}),
                "negative_prompt": ("STRING", {"multiline": True}),
                # Good tags controls
                "use_good_tags": ("BOOLEAN", {"default": state.get("use_good_tags", True)}),
                "quality_good": (cls.QUALITY_TAGS_GOOD,),
                "score_good": (cls.SCORE_TAGS_GOOD,),
                # Bad tags controls
                "use_bad_tags": ("BOOLEAN", {"default": state.get("use_bad_tags", False)}),
                "quality_bad": (cls.QUALITY_TAGS_BAD,),
                "score_bad": (cls.SCORE_TAGS_BAD,),
                # Year control
                "use_year": ("BOOLEAN", {"default": state.get("use_year", False)}),
                "year": ("INT", {"default": state.get("year", 2024)}),
                # Rating control
                "use_rating": ("BOOLEAN", {"default": state.get("use_rating", False)}),
                "rating": (cls.RATING_TAGS,),
                # CSV control
                "use_csv": ("BOOLEAN", {"default": state.get("use_csv", False)}),
                "csv_path": ("STRING", {"default": state.get("csv_path", "")}),
                "csv_index": ("INT", {"default": state.get("csv_index", 0), "min": 0, "max": 9999})
            }
        }

    def _get_csv_entry(self, csv_path: str, index: int) -> Optional[str]:
        """Obtiene y formatea una entrada del CSV"""
        start_time = time.time()
        
        if self.last_csv_path != csv_path:
            logger.logger.info(f"Loading new CSV file: {csv_path}")
            df = self.csv_handler.load_csv(csv_path)
            if df is not None:
                state_manager.add_csv_to_history(csv_path, len(df))
            self.last_csv_path = csv_path
    
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
            
        result = ", ".join(tags)
        logger.logger.debug(f"Built good tags: {result}")
        return result

    def _build_bad_tags(self, quality_bad: str, score_bad: str) -> str:
        """Construye la sección de tags negativas"""
        tags = []
        if quality_bad:
            tags.append(quality_bad)
        if score_bad:
            tags.append(score_bad)
            
        result = ", ".join(tags)
        logger.logger.debug(f"Built bad tags: {result}")
        return result

    def _get_csv_entry(self, csv_path: str, index: int) -> Optional[str]:
        """Obtiene y formatea una entrada del CSV"""
        start_time = time.time()
        
        if self.last_csv_path != csv_path:
            logger.logger.info(f"Loading new CSV file: {csv_path}")
            self.csv_handler.load_csv(csv_path)
            self.last_csv_path = csv_path
            
        entry = self.csv_handler.get_entry(index)
        
        end_time = time.time()
        logger.log_performance(
            "CSV Entry Retrieval",
            start_time,
            end_time,
            {"path": csv_path, "index": index}
        )
        
        if entry:
            formatted_entry = f"{entry['gender']}, {entry['character']}, {entry['copyright']}"
            logger.logger.debug(f"Formatted CSV entry: {formatted_entry}")
            return formatted_entry
            
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
        start_time = time.time()
        
        try:
            # Update state with current values
            state_manager.update_state({
                "use_good_tags": use_good_tags,
                "use_bad_tags": use_bad_tags,
                "use_year": use_year,
                "year": year,
                "use_rating": use_rating,
                "rating": rating,
                "use_csv": use_csv,
                "csv_path": csv_path,
                "csv_index": csv_index
            })
            
            # Lista para construir el prompt positivo
            positive_parts = []
            
            # Agregar tags positivas si están activadas
            if use_good_tags:
                good_tags = self._build_good_tags(quality_good, score_good)
                if good_tags:
                    positive_parts.append(good_tags)
                    logger.logger.debug(f"Added good tags: {good_tags}")
            
            # Agregar bad tags al prompt positivo si están activadas
            if use_bad_tags:
                bad_tags = self._build_bad_tags(quality_bad, score_bad)
                if bad_tags:
                    positive_parts.append(bad_tags)
                    logger.logger.debug(f"Added bad tags: {bad_tags}")
            
            # Agregar entrada del CSV si está activado
            if use_csv and csv_path:
                csv_entry = self._get_csv_entry(csv_path, csv_index)
                if csv_entry:
                    positive_parts.append(csv_entry)
                    logger.logger.debug(f"Added CSV entry: {csv_entry}")

            # Agregar el prompt base del usuario
            if positive_prompt:
                positive_parts.append(positive_prompt)
                logger.logger.debug(f"Added base positive prompt: {positive_prompt}")
            
            # Agregar year tag si está activado
            if use_year:
                year_tag = f"year {year}"
                positive_parts.append(year_tag)
                logger.logger.debug(f"Added year tag: {year_tag}")
            
            # Agregar rating si está activado
            if use_rating:
                positive_parts.append(rating)
                logger.logger.debug(f"Added rating: {rating}")
            
            # Construir el prompt negativo
            negative_parts = []
            
            # Agregar tags negativas por defecto
            negative_parts.extend(self.DEFAULT_NEGATIVE_TAGS)
            logger.logger.debug("Added default negative tags")
            
            # Agregar el prompt negativo del usuario
            if negative_prompt:
                negative_parts.append(negative_prompt)
                logger.logger.debug(f"Added user negative prompt: {negative_prompt}")
            
            # Unir todas las partes
            final_positive = ", ".join(part for part in positive_parts if part)
            final_negative = ", ".join(part for part in negative_parts if part)
            
            end_time = time.time()
            logger.log_performance(
                "Prompt Generation",
                start_time,
                end_time,
                {
                    "positive_parts": len(positive_parts),
                    "negative_parts": len(negative_parts)
                }
            )
            
            logger.logger.info("Prompt generation completed successfully")
            return final_positive, final_negative
            
        except Exception as e:
            logger.log_error(
                e,
                "Prompt Generation",
                {
                    "positive_prompt": positive_prompt,
                    "negative_prompt": negative_prompt,
                    "use_csv": use_csv,
                    "csv_path": csv_path
                }
            )
            raise e