"""
Configuration settings for DocuVision OCR application.

This module contains all configurable parameters for the OCR engine,
image processing, and application behavior.
"""

import os
from typing import Dict, Any

# OCR Engine Configuration
OCR_CONFIG: Dict[str, Any] = {
    # Tesseract language (can be 'eng', 'fra', 'deu', etc.)
    'language': 'eng',
    
    # Page Segmentation Mode (PSM)
    # 6: Uniform block of text (default)
    # 8: Single word
    # 13: Raw line. Treat the image as a single text line
    'page_segmentation_mode': 6,
    
    # OCR Engine Mode (OEM)
    # 3: Default, based on what is available
    # 1: Neural nets LSTM engine only
    # 2: Legacy engine only
    'ocr_engine_mode': 3,
    
    # Minimum confidence threshold for text detection (0-100)
    'confidence_threshold': 30,
    
    # Custom Tesseract configuration
    'custom_config': '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?;: '
}

# Image Processing Configuration
IMAGE_CONFIG: Dict[str, Any] = {
    # Maximum dimensions for image resizing (to improve processing speed)
    'max_width': 2000,
    'max_height': 2000,
    
    # Gaussian blur kernel size for noise reduction
    'gaussian_blur_kernel': (5, 5),
    
    # Threshold type: 'binary', 'adaptive', or 'otsu'
    'threshold_type': 'adaptive',
    
    # Binary threshold value (used when threshold_type is 'binary')
    'binary_threshold': 150,
    
    # Adaptive threshold parameters
    'adaptive_threshold_max_value': 255,
    'adaptive_threshold_block_size': 11,
    'adaptive_threshold_c': 2,
    
    # Morphological operations
    'enable_morphology': True,
    'morphology_kernel_size': (3, 3),
    'morphology_iterations': 1,
    
    # Deskewing
    'enable_deskew': True,
    'deskew_angle_threshold': 0.5,
}

# File Handling Configuration
FILE_CONFIG: Dict[str, Any] = {
    # Supported file extensions
    'supported_image_formats': ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'],
    'supported_document_formats': ['.pdf'],
    
    # Maximum file size in MB
    'max_file_size_mb': 10,
    
    # Temporary file settings
    'temp_dir': 'temp',
    'cleanup_temp_files': True,
}

# Streamlit App Configuration
APP_CONFIG: Dict[str, Any] = {
    # Page configuration
    'page_title': 'DocuVision - OCR Text Extractor',
    'page_icon': '📄',
    'layout': 'centered',
    'initial_sidebar_state': 'expanded',
    
    # UI settings
    'max_upload_size': 10,  # MB
    'show_preprocessing_options': True,
    'show_confidence_scores': True,
    'enable_batch_processing': False,
    
    # Performance settings
    'cache_ttl': 3600,  # Cache TTL in seconds
    'enable_caching': True,
}

# Logging Configuration
LOGGING_CONFIG: Dict[str, Any] = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': 'docuvision.log',
    'max_log_size_mb': 10,
    'backup_count': 5,
}

# Environment-specific overrides
def load_environment_config():
    """Load configuration overrides from environment variables."""
    
    # OCR Configuration overrides
    if os.getenv('TESSERACT_CMD'):
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_CMD')
    
    if os.getenv('OCR_LANGUAGE'):
        OCR_CONFIG['language'] = os.getenv('OCR_LANGUAGE')
    
    if os.getenv('OCR_CONFIDENCE_THRESHOLD'):
        OCR_CONFIG['confidence_threshold'] = int(os.getenv('OCR_CONFIDENCE_THRESHOLD'))
    
    # File Configuration overrides
    if os.getenv('MAX_FILE_SIZE_MB'):
        FILE_CONFIG['max_file_size_mb'] = int(os.getenv('MAX_FILE_SIZE_MB'))
        APP_CONFIG['max_upload_size'] = int(os.getenv('MAX_FILE_SIZE_MB'))
    
    # App Configuration overrides
    if os.getenv('STREAMLIT_THEME'):
        APP_CONFIG['theme'] = os.getenv('STREAMLIT_THEME')

# Load environment-specific configuration on import
load_environment_config()