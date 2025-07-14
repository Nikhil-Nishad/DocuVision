"""
File Handler Module for DocuVision OCR Application.

This module handles file operations including upload, validation, conversion,
and temporary file management for various document formats.
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Tuple, Union, BinaryIO
import logging
from io import BytesIO

import streamlit as st
from PIL import Image
import PyPDF2
import numpy as np
from docx import Document

from config.settings import FILE_CONFIG, LOGGING_CONFIG

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format']
)
logger = logging.getLogger(__name__)


class FileHandler:
    """
    Handles file operations for the DocuVision OCR application.
    
    This class provides methods for file validation, conversion, temporary file
    management, and format handling for both images and PDF documents.
    """
    
    def __init__(self):
        """Initialize the FileHandler with configuration settings."""
        self.supported_image_formats = FILE_CONFIG['supported_image_formats']
        self.supported_document_formats = FILE_CONFIG['supported_document_formats']
        self.max_file_size_mb = FILE_CONFIG['max_file_size_mb']
        self.temp_dir = FILE_CONFIG['temp_dir']
        self.cleanup_temp_files = FILE_CONFIG['cleanup_temp_files']
        
        # Create temp directory if it doesn't exist
        self._ensure_temp_directory()
    
    def _ensure_temp_directory(self) -> None:
        """Create temporary directory if it doesn't exist."""
        try:
            Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
            logger.info(f"Temporary directory ensured: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Failed to create temp directory: {e}")
            # Fallback to system temp directory
            self.temp_dir = tempfile.gettempdir()
    
    def validate_file(self, uploaded_file) -> Tuple[bool, str]:
        """
        Validate uploaded file for format and size constraints.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            if uploaded_file is None:
                return False, "No file uploaded"
            
            # Check file size
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                return False, f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({self.max_file_size_mb}MB)"
            
            # Check file extension
            file_extension = Path(uploaded_file.name).suffix.lower()
            all_supported_formats = self.supported_image_formats + self.supported_document_formats
            
            if file_extension not in all_supported_formats:
                supported_formats_str = ", ".join(all_supported_formats)
                return False, f"Unsupported file format. Supported formats: {supported_formats_str}"
            
            # Additional validation for images
            if file_extension in self.supported_image_formats:
                try:
                    image = Image.open(uploaded_file)
                    image.verify()  # Verify that it's a valid image
                    uploaded_file.seek(0)  # Reset file pointer
                except Exception as e:
                    return False, f"Invalid image file: {str(e)}"
            
            # Additional validation for PDFs
            elif file_extension in self.supported_document_formats:
                try:
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    if len(pdf_reader.pages) == 0:
                        return False, "PDF file contains no pages"
                    uploaded_file.seek(0)  # Reset file pointer
                except Exception as e:
                    return False, f"Invalid PDF file: {str(e)}"
            
            logger.info(f"File validation successful: {uploaded_file.name}")
            return True, "File is valid"
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            return False, f"File validation failed: {str(e)}"
    
    def save_uploaded_file(self, uploaded_file) -> Optional[str]:
        """
        Save uploaded file to temporary directory.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Optional[str]: Path to saved file or None if failed
        """
        try:
            # Generate unique filename
            file_extension = Path(uploaded_file.name).suffix.lower()
            temp_filename = f"upload_{hash(uploaded_file.name)}_{uploaded_file.size}{file_extension}"
            temp_filepath = Path(self.temp_dir) / temp_filename
            
            # Save file
            with open(temp_filepath, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            logger.info(f"File saved successfully: {temp_filepath}")
            return str(temp_filepath)
            
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")
            return None
    
    def convert_pdf_to_images(self, pdf_path: str, dpi: int = 200) -> List[np.ndarray]:
        """
        Convert PDF pages to images for OCR processing.
        
        Args:
            pdf_path (str): Path to PDF file
            dpi (int): Resolution for conversion
            
        Returns:
            List[np.ndarray]: List of images as numpy arrays
        """
        images = []
        
        try:
            # Try using pdf2image if available
            try:
                from pdf2image import convert_from_path
                pil_images = convert_from_path(pdf_path, dpi=dpi)
                
                for pil_image in pil_images:
                    # Convert PIL image to numpy array
                    img_array = np.array(pil_image)
                    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                        # Convert RGB to BGR for OpenCV
                        img_array = img_array[:, :, ::-1]
                    images.append(img_array)
                
                logger.info(f"PDF converted to {len(images)} images using pdf2image")
                return images
                
            except ImportError:
                logger.warning("pdf2image not available, using fallback method")
                
            # Fallback method using PyPDF2 (limited functionality)
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    # This is a basic fallback - in practice, you'd need additional libraries
                    # for proper PDF to image conversion
                    logger.warning(f"Basic PDF processing for page {page_num + 1}")
                    
                    # Create a placeholder image for now
                    # In a real implementation, you'd use libraries like pdf2image or pymupdf
                    placeholder_image = np.ones((800, 600, 3), dtype=np.uint8) * 255
                    images.append(placeholder_image)
                
                if not images:
                    logger.error("No pages found in PDF")
                
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            st.error(f"Failed to convert PDF: {str(e)}")
            st.info("For better PDF support, install pdf2image: pip install pdf2image")
        
        return images
    
    def load_image(self, file_path: str) -> Optional[np.ndarray]:
        """
        Load image file as numpy array.
        
        Args:
            file_path (str): Path to image file
            
        Returns:
            Optional[np.ndarray]: Image as numpy array or None if failed
        """
        try:
            # Load image using PIL for better format support
            pil_image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array
            img_array = np.array(pil_image)
            
            # Convert RGB to BGR for OpenCV compatibility
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = img_array[:, :, ::-1]
            
            logger.info(f"Image loaded successfully: {file_path}")
            return img_array
            
        except Exception as e:
            logger.error(f"Failed to load image {file_path}: {e}")
            return None
    
    def process_uploaded_file(self, uploaded_file) -> List[np.ndarray]:
        """
        Process uploaded file and return list of images for OCR.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            List[np.ndarray]: List of images ready for OCR processing
        """
        images = []
        
        try:
            # Validate file first
            is_valid, error_message = self.validate_file(uploaded_file)
            if not is_valid:
                st.error(error_message)
                return images
            
            # Save uploaded file
            temp_file_path = self.save_uploaded_file(uploaded_file)
            if not temp_file_path:
                st.error("Failed to save uploaded file")
                return images
            
            file_extension = Path(uploaded_file.name).suffix.lower()
            
            # Process based on file type
            if file_extension in self.supported_image_formats:
                # Load single image
                image = self.load_image(temp_file_path)
                if image is not None:
                    images.append(image)
                else:
                    st.error("Failed to load image file")
            
            elif file_extension in self.supported_document_formats:
                # Convert PDF to images
                images = self.convert_pdf_to_images(temp_file_path)
                if not images:
                    st.error("Failed to convert PDF to images")
            
            # Cleanup temporary file if configured
            if self.cleanup_temp_files and temp_file_path:
                self._cleanup_file(temp_file_path)
            
            logger.info(f"File processing completed: {len(images)} images extracted")
            
        except Exception as e:
            logger.error(f"File processing failed: {e}")
            st.error(f"File processing failed: {str(e)}")
        
        return images
    
    def save_text_to_file(self, text: str, filename: str, format_type: str = 'txt') -> Optional[str]:
        """
        Save extracted text to a file (.txt or .docx).
        
        Args:
            text (str): The text content to save.
            filename (str): The base filename (without extension).
            format_type (str): The format to save ('txt' or 'docx').
            
        Returns:
            Optional[str]: Path to the saved file or None if failed.
        """
        try:
            output_filename = f"{filename}.{format_type}"
            output_filepath = Path(self.temp_dir) / output_filename
            
            if format_type == 'txt':
                with open(output_filepath, 'w', encoding='utf-8') as f:
                    f.write(text)
            elif format_type == 'docx':
                doc = Document()
                doc.add_paragraph(text)
                doc.save(output_filepath)
            else:
                logger.error(f"Unsupported save format: {format_type}")
                return None
            
            logger.info(f"Text saved successfully to {output_filepath}")
            return str(output_filepath)
            
        except Exception as e:
            logger.error(f"Failed to save text to file: {e}")
            return None
    
    def _cleanup_file(self, file_path: str) -> None:
        """
        Remove a file if cleanup is enabled.
        
        Args:
            file_path (str): Path to file to remove
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Temporary file cleaned up: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {e}")
    
    def cleanup_temp_directory(self) -> None:
        """Remove all files from temporary directory."""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self._ensure_temp_directory()
                logger.info("Temporary directory cleaned up")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory: {e}")
    
    def get_file_info(self, uploaded_file) -> dict:
        """
        Get information about uploaded file.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            dict: File information
        """
        try:
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            file_extension = Path(uploaded_file.name).suffix.lower()
            
            return {
                'name': uploaded_file.name,
                'size_mb': round(file_size_mb, 2),
                'extension': file_extension,
                'type': uploaded_file.type,
                'is_image': file_extension in self.supported_image_formats,
                'is_document': file_extension in self.supported_document_formats
            }
        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return {}