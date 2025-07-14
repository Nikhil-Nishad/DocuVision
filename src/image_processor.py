"""
Image Processing Module

This module provides comprehensive image preprocessing capabilities
to enhance OCR accuracy through various computer vision techniques.
"""

import logging
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import Tuple, Optional, Dict, Any
import math

from config.settings import IMAGE_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Image processor class for preprocessing images to improve OCR accuracy.
    
    This class provides various image enhancement techniques including
    noise reduction, contrast enhancement, deskewing, and thresholding.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Image Processor.
        
        Args:
            config (Dict[str, Any], optional): Custom image processing configuration.
                                             Defaults to IMAGE_CONFIG from settings.
        """
        self.config = config or IMAGE_CONFIG.copy()
        logger.info("Image Processor initialized successfully")
    
    def preprocess_image(self, image_input, enhancement_level: str = 'medium') -> np.ndarray:
        """
        Main preprocessing pipeline for OCR optimization.
        
        Args:
            image_input: Input image (file path, PIL Image, or numpy array)
            enhancement_level (str): Level of enhancement ('light', 'medium', 'heavy')
        
        Returns:
            np.ndarray: Preprocessed image ready for OCR
        
        Raises:
            ValueError: If image input is invalid
            RuntimeError: If preprocessing fails
        """
        try:
            # Load and validate image
            image = self._load_image(image_input)
            
            if image is None or image.size == 0:
                raise ValueError("Invalid or empty image provided")
            
            logger.info(f"Processing image with shape: {image.shape}")
            
            # Apply preprocessing pipeline based on enhancement level
            if enhancement_level == 'light':
                processed_image = self._light_preprocessing(image)
            elif enhancement_level == 'medium':
                processed_image = self._medium_preprocessing(image)
            elif enhancement_level == 'heavy':
                processed_image = self._heavy_preprocessing(image)
            else:
                raise ValueError(f"Invalid enhancement level: {enhancement_level}")
            
            logger.info("Image preprocessing completed successfully")
            return processed_image
            
        except Exception as e:
            error_msg = f"Image preprocessing failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _load_image(self, image_input) -> np.ndarray:
        """
        Load image from various input types.
        
        Args:
            image_input: Input image (file path, PIL Image, or numpy array)
        
        Returns:
            np.ndarray: Loaded image as numpy array
        """
        if isinstance(image_input, str):
            # Load from file path
            image = cv2.imread(image_input)
            if image is None:
                raise ValueError(f"Could not load image from path: {image_input}")
        elif isinstance(image_input, Image.Image):
            # Convert PIL Image to numpy array
            image = np.array(image_input)
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        elif isinstance(image_input, np.ndarray):
            # Use numpy array directly
            image = image_input.copy()
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")
        
        return image
    
    def _light_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """
        Light preprocessing pipeline for clean images.
        
        Args:
            image (np.ndarray): Input image
        
        Returns:
            np.ndarray: Lightly processed image
        """
        # Resize if too large
        image = self._resize_image(image)
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply simple thresholding
        processed = self._apply_threshold(gray)
        
        return processed
    
    def _medium_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """
        Medium preprocessing pipeline for typical documents.
        
        Args:
            image (np.ndarray): Input image
        
        Returns:
            np.ndarray: Medium processed image
        """
        # Resize if too large
        image = self._resize_image(image)
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Noise reduction
        denoised = self._reduce_noise(gray)
        
        # Enhance contrast
        enhanced = self._enhance_contrast(denoised)
        
        # Apply thresholding
        thresholded = self._apply_threshold(enhanced)
        
        # Morphological operations
        if self.config.get('enable_morphology', True):
            processed = self._apply_morphology(thresholded)
        else:
            processed = thresholded
        
        return processed
    
    def _heavy_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """
        Heavy preprocessing pipeline for challenging images.
        
        Args:
            image (np.ndarray): Input image
        
        Returns:
            np.ndarray: Heavily processed image
        """
        # Resize if too large
        image = self._resize_image(image)
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Deskew if enabled
        if self.config.get('enable_deskew', True):
            deskewed = self._deskew_image(gray)
        else:
            deskewed = gray
        
        # Advanced noise reduction
        denoised = self._advanced_noise_reduction(deskewed)
        
        # Enhance contrast aggressively
        enhanced = self._enhance_contrast(denoised, factor=1.5)
        
        # Apply adaptive thresholding
        thresholded = self._apply_threshold(enhanced, method='adaptive')
        
        # Morphological operations
        if self.config.get('enable_morphology', True):
            processed = self._apply_morphology(thresholded)
        else:
            processed = thresholded
        
        # Final cleanup
        cleaned = self._final_cleanup(processed)
        
        return cleaned
    
    def _resize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Resize image if it exceeds maximum dimensions.
        
        Args:
            image (np.ndarray): Input image
        
        Returns:
            np.ndarray: Resized image
        """
        height, width = image.shape[:2]
        max_width = self.config.get('max_width', 2000)
        max_height = self.config.get('max_height', 2000)
        
        if width > max_width or height > max_height:
            # Calculate scaling factor
            scale_w = max_width / width
            scale_h = max_height / height
            scale = min(scale_w, scale_h)
            
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            return resized
        
        return image
    
    def _reduce_noise(self, image: np.ndarray) -> np.ndarray:
        """
        Apply noise reduction using Gaussian blur.
        
        Args:
            image (np.ndarray): Input grayscale image
        
        Returns:
            np.ndarray: Denoised image
        """
        kernel_size = self.config.get('gaussian_blur_kernel', (5, 5))
        return cv2.GaussianBlur(image, kernel_size, 0)
    
    def _advanced_noise_reduction(self, image: np.ndarray) -> np.ndarray:
        """
        Apply advanced noise reduction techniques.
        
        Args:
            image (np.ndarray): Input grayscale image
        
        Returns:
            np.ndarray: Denoised image
        """
        # Apply Non-local Means Denoising
        denoised = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
        
        # Apply bilateral filter for edge preservation
        bilateral = cv2.bilateralFilter(denoised, 9, 75, 75)
        
        return bilateral
    
    def _enhance_contrast(self, image: np.ndarray, factor: float = 1.2) -> np.ndarray:
        """
        Enhance image contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization).
        
        Args:
            image (np.ndarray): Input grayscale image
            factor (float): Enhancement factor
        
        Returns:
            np.ndarray: Contrast enhanced image
        """
        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0 * factor, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        
        return enhanced
    
    def _apply_threshold(self, image: np.ndarray, method: Optional[str] = None) -> np.ndarray:
        """
        Apply thresholding to create binary image.
        
        Args:
            image (np.ndarray): Input grayscale image
            method (str, optional): Thresholding method ('binary', 'adaptive', 'otsu')
        
        Returns:
            np.ndarray: Binary thresholded image
        """
        threshold_type = method or self.config.get('threshold_type', 'adaptive')
        
        if threshold_type == 'binary':
            threshold_value = self.config.get('binary_threshold', 150)
            _, thresholded = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)
        
        elif threshold_type == 'adaptive':
            max_value = self.config.get('adaptive_threshold_max_value', 255)
            block_size = self.config.get('adaptive_threshold_block_size', 11)
            c_value = self.config.get('adaptive_threshold_c', 2)
            
            thresholded = cv2.adaptiveThreshold(
                image, max_value, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, block_size, c_value
            )
        
        elif threshold_type == 'otsu':
            _, thresholded = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        else:
            raise ValueError(f"Invalid threshold type: {threshold_type}")
        
        return thresholded
    
    def _apply_morphology(self, image: np.ndarray) -> np.ndarray:
        """
        Apply morphological operations to clean up the binary image.
        
        Args:
            image (np.ndarray): Input binary image
        
        Returns:
            np.ndarray: Morphologically processed image
        """
        kernel_size = self.config.get('morphology_kernel_size', (3, 3))
        iterations = self.config.get('morphology_iterations', 1)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
        
        # Apply opening (erosion followed by dilation) to remove noise
        opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=iterations)
        
        # Apply closing (dilation followed by erosion) to fill gaps
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        
        return closed
    
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Detect and correct skew in the image.
        
        Args:
            image (np.ndarray): Input grayscale image
        
        Returns:
            np.ndarray: Deskewed image
        """
        try:
            # Find edges
            edges = cv2.Canny(image, 50, 150, apertureSize=3)
            
            # Find lines using Hough transform
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                angles = []
                for rho, theta in lines[:, 0]:
                    angle = theta * 180 / np.pi
                    # Convert to angle from horizontal
                    if angle > 90:
                        angle = angle - 180
                    angles.append(angle)
                
                # Calculate median angle
                if angles:
                    median_angle = np.median(angles)
                    angle_threshold = self.config.get('deskew_angle_threshold', 0.5)
                    
                    if abs(median_angle) > angle_threshold:
                        # Rotate image to correct skew
                        height, width = image.shape
                        center = (width // 2, height // 2)
                        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                        deskewed = cv2.warpAffine(image, rotation_matrix, (width, height),
                                                flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                        logger.info(f"Deskewed image by {median_angle:.2f} degrees")
                        return deskewed
            
            return image
            
        except Exception as e:
            logger.warning(f"Deskewing failed: {str(e)}")
            return image
    
    def _final_cleanup(self, image: np.ndarray) -> np.ndarray:
        """
        Apply final cleanup operations to the processed image.
        
        Args:
            image (np.ndarray): Input binary image
        
        Returns:
            np.ndarray: Final cleaned image
        """
        # Remove small noise components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=8)
        
        # Calculate minimum component size (0.1% of image area)
        min_size = int(0.001 * image.shape[0] * image.shape[1])
        
        # Create mask for components larger than minimum size
        mask = np.zeros_like(image)
        for i in range(1, num_labels):  # Skip background (label 0)
            if stats[i, cv2.CC_STAT_AREA] >= min_size:
                mask[labels == i] = 255
        
        return mask
    
    def get_image_stats(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Get statistical information about the image.
        
        Args:
            image (np.ndarray): Input image
        
        Returns:
            Dict[str, Any]: Image statistics
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        stats = {
            'shape': image.shape,
            'dtype': str(image.dtype),
            'mean_intensity': float(np.mean(gray)),
            'std_intensity': float(np.std(gray)),
            'min_intensity': int(np.min(gray)),
            'max_intensity': int(np.max(gray)),
            'is_binary': len(np.unique(gray)) <= 2
        }
        
        return stats
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Update image processing configuration parameters.
        
        Args:
            new_config (Dict[str, Any]): New configuration parameters to merge
        """
        self.config.update(new_config)
        logger.info("Image processing configuration updated")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current image processing configuration.
        
        Returns:
            Dict[str, Any]: Current image processing configuration
        """
        return self.config.copy()


# Utility functions for common image operations
def quick_preprocess(image_path: str) -> np.ndarray:
    """
    Quick preprocessing function for simple use cases.
    
    Args:
        image_path (str): Path to the image file
    
    Returns:
        np.ndarray: Preprocessed image
    """
    processor = ImageProcessor()
    return processor.preprocess_image(image_path, enhancement_level='medium')


def compare_preprocessing_methods(image_path: str) -> Dict[str, np.ndarray]:
    """
    Compare different preprocessing methods on the same image.
    
    Args:
        image_path (str): Path to the image file
    
    Returns:
        Dict[str, np.ndarray]: Dictionary with different preprocessing results
    """
    processor = ImageProcessor()
    
    results = {
        'original': processor._load_image(image_path),
        'light': processor.preprocess_image(image_path, enhancement_level='light'),
        'medium': processor.preprocess_image(image_path, enhancement_level='medium'),
        'heavy': processor.preprocess_image(image_path, enhancement_level='heavy')
    }
    
    return results