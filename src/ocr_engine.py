"""
OCR Engine Module

This module provides the core OCR functionality using Tesseract OCR.
It handles text extraction from preprocessed images with configurable parameters.
"""

import logging
import pytesseract
import numpy as np
from PIL import Image
from typing import Dict, List, Tuple, Optional, Any
import cv2
import platform
import os

from config.settings import OCR_CONFIG

# For Windows, set the Tesseract path if not in the system's PATH
if platform.system() == "Windows":
    # The user needs to update this path to their Tesseract installation
    pytesseract.pytesseract.tesseract_cmd = r"C:\Users\nikhi\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCREngine:
    """
    OCR Engine class for extracting text from images using Tesseract OCR.
    
    This class provides methods for text extraction with various configuration
    options and confidence scoring.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the OCR Engine.
        
        Args:
            config (Dict[str, Any], optional): Custom OCR configuration.
                                             Defaults to OCR_CONFIG from settings.
        """
        self.config = config or OCR_CONFIG.copy()
        self._validate_tesseract_installation()
        logger.info("OCR Engine initialized successfully")
    
    def _validate_tesseract_installation(self) -> None:
        """
        Validate that Tesseract OCR is properly installed and accessible.
        
        Raises:
            RuntimeError: If Tesseract is not found or not properly configured.
        """
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version detected: {version}")
        except Exception as e:
            error_msg = (
                "Tesseract OCR is not properly installed or configured. "
                "Please install Tesseract and ensure it's in your PATH. "
                f"Error: {str(e)}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def extract_text(self, image: np.ndarray, **kwargs) -> str:
        """
        Extract text from a preprocessed image.
        
        Args:
            image (np.ndarray): Preprocessed image as numpy array
            **kwargs: Additional OCR configuration parameters
        
        Returns:
            str: Extracted text from the image
        
        Raises:
            ValueError: If image is invalid or empty
            RuntimeError: If OCR processing fails
        """
        if image is None or image.size == 0:
            raise ValueError("Invalid or empty image provided")
        
        try:
            # Merge custom parameters with default config
            ocr_config = self.config.copy()
            ocr_config.update(kwargs)
            
            # Convert numpy array to PIL Image if necessary
            if isinstance(image, np.ndarray):
                # Ensure image is in correct format for PIL
                if len(image.shape) == 3:
                    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                else:
                    image_pil = Image.fromarray(image)
            else:
                image_pil = image
            
            # Build Tesseract configuration string
            tesseract_config = self._build_tesseract_config(ocr_config)
            
            # Extract text using Tesseract
            extracted_text = pytesseract.image_to_string(
                image_pil,
                lang=ocr_config.get('language', 'eng'),
                config=tesseract_config
            )
            
            # Clean and validate extracted text
            cleaned_text = self._clean_extracted_text(extracted_text)
            
            logger.info(f"Successfully extracted {len(cleaned_text)} characters")
            return cleaned_text
            
        except Exception as e:
            error_msg = f"OCR text extraction failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def extract_text_with_confidence(self, image: np.ndarray, **kwargs) -> Tuple[str, List[Dict]]:
        """
        Extract text with confidence scores for each detected word.
        
        Args:
            image (np.ndarray): Preprocessed image as numpy array
            **kwargs: Additional OCR configuration parameters
        
        Returns:
            Tuple[str, List[Dict]]: Extracted text and list of word confidence data
        """
        if image is None or image.size == 0:
            raise ValueError("Invalid or empty image provided")
        
        try:
            # Merge custom parameters with default config
            ocr_config = self.config.copy()
            ocr_config.update(kwargs)
            
            # Convert numpy array to PIL Image if necessary
            if isinstance(image, np.ndarray):
                if len(image.shape) == 3:
                    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                else:
                    image_pil = Image.fromarray(image)
            else:
                image_pil = image
            
            # Build Tesseract configuration string
            tesseract_config = self._build_tesseract_config(ocr_config)
            
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(
                image_pil,
                lang=ocr_config.get('language', 'eng'),
                config=tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Process OCR data to extract text and confidence scores
            text_parts = []
            word_confidences = []
            confidence_threshold = ocr_config.get('confidence_threshold', 30)
            
            for i, word in enumerate(ocr_data['text']):
                confidence = int(ocr_data['conf'][i])
                
                if word.strip() and confidence >= confidence_threshold:
                    text_parts.append(word)
                    word_confidences.append({
                        'word': word,
                        'confidence': confidence,
                        'bbox': {
                            'x': ocr_data['left'][i],
                            'y': ocr_data['top'][i],
                            'width': ocr_data['width'][i],
                            'height': ocr_data['height'][i]
                        }
                    })
            
            extracted_text = ' '.join(text_parts)
            cleaned_text = self._clean_extracted_text(extracted_text)
            
            logger.info(f"Extracted text with {len(word_confidences)} confident words")
            return cleaned_text, word_confidences
            
        except Exception as e:
            error_msg = f"OCR text extraction with confidence failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of languages supported by the installed Tesseract.
        
        Returns:
            List[str]: List of supported language codes
        """
        try:
            languages = pytesseract.get_languages(config='')
            logger.info(f"Found {len(languages)} supported languages")
            return languages
        except Exception as e:
            logger.warning(f"Could not retrieve supported languages: {str(e)}")
            return ['eng']  # Default fallback
    
    def _build_tesseract_config(self, config: Dict[str, Any]) -> str:
        """
        Build Tesseract configuration string from config dictionary.
        
        Args:
            config (Dict[str, Any]): OCR configuration parameters
        
        Returns:
            str: Tesseract configuration string
        """
        config_parts = []
        
        # Page Segmentation Mode
        if 'page_segmentation_mode' in config:
            config_parts.append(f"--psm {config['page_segmentation_mode']}")
        
        # OCR Engine Mode
        if 'ocr_engine_mode' in config:
            config_parts.append(f"--oem {config['ocr_engine_mode']}")
        
        # Custom configuration
        if 'custom_config' in config:
            config_parts.append(config['custom_config'])
        
        return ' '.join(config_parts)
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text (str): Raw extracted text
        
        Returns:
            str: Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        cleaned = ' '.join(text.split())
        
        # Remove common OCR artifacts
        cleaned = cleaned.replace('|', 'I')  # Common misrecognition
        cleaned = cleaned.replace('0', 'O')  # In text context, 0 might be O
        
        # Fix common spacing issues
        cleaned = cleaned.replace(' .', '.')
        cleaned = cleaned.replace(' ,', ',')
        cleaned = cleaned.replace(' !', '!')
        cleaned = cleaned.replace(' ?', '?')
        cleaned = cleaned.replace(' ;', ';')
        cleaned = cleaned.replace(' :', ':')
        
        return cleaned.strip()
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Update OCR configuration parameters.
        
        Args:
            new_config (Dict[str, Any]): New configuration parameters to merge
        """
        self.config.update(new_config)
        logger.info("OCR configuration updated")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current OCR configuration.
        
        Returns:
            Dict[str, Any]: Current OCR configuration
        """
        return self.config.copy()


# Utility functions for OCR operations
def quick_ocr(image_path: str, language: str = 'eng') -> str:
    """
    Quick OCR function for simple text extraction.
    
    Args:
        image_path (str): Path to the image file
        language (str): Language code for OCR (default: 'eng')
    
    Returns:
        str: Extracted text
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=language)
        return text.strip()
    except Exception as e:
        logger.error(f"Quick OCR failed: {str(e)}")
        return ""


def batch_ocr(image_paths: List[str], language: str = 'eng') -> List[Tuple[str, str]]:
    """
    Perform OCR on multiple images.
    
    Args:
        image_paths (List[str]): List of image file paths
        language (str): Language code for OCR (default: 'eng')
    
    Returns:
        List[Tuple[str, str]]: List of (image_path, extracted_text) tuples
    """
    results = []
    ocr_engine = OCREngine()
    
    for image_path in image_paths:
        try:
            image = cv2.imread(image_path)
            if image is not None:
                text = ocr_engine.extract_text(image, language=language)
                results.append((image_path, text))
            else:
                logger.warning(f"Could not load image: {image_path}")
                results.append((image_path, ""))
        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {str(e)}")
            results.append((image_path, ""))
    
    return results