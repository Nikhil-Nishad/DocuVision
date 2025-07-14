"""
DocuVision: OCR-Powered Text Extractor

This is the main Streamlit application for DocuVision, a tool to extract
text from images and PDF documents using Tesseract OCR.
"""

import streamlit as st
from PIL import Image
import numpy as np
import os

from src.ocr_engine import OCREngine
from src.image_processor import ImageProcessor
from src.file_handler import FileHandler
from src.utils import (
    display_header,
    display_footer,
    setup_logger,
    show_processing_error,
)

# Initialize logger
logger = setup_logger()

# --- Main Application Logic ---

def main():
    """
    Main function to run the Streamlit application.
    """
    display_header()

    # --- Initialize Components ---
    try:
        file_handler = FileHandler()
        image_processor = ImageProcessor()
        ocr_engine = OCREngine()
    except Exception as e:
        logger.critical(f"Failed to initialize components: {e}", exc_info=True)
        st.error(f"Application failed to start: {e}")
        st.stop()

    # --- Sidebar ---
    with st.sidebar:
        st.header("⚙️ Options")
        
        enhancement_level = st.select_slider(
            "Image Enhancement Level",
            options=['light', 'medium', 'heavy'],
            value='medium',
            help="Adjust the level of image preprocessing for better OCR. 'Heavy' may take longer."
        )

        st.info("Upload a `.png`, `.jpg`, `.jpeg`, or `.pdf` file to get started.")
        
        display_footer()

    # --- File Uploader ---
    uploaded_file = st.file_uploader(
        "Upload your document",
        type=['png', 'jpg', 'jpeg', 'pdf']
    )

    if uploaded_file:
        # --- File Processing ---
        is_valid, message = file_handler.validate_file(uploaded_file)
        if not is_valid:
            st.error(message)
            st.stop()

        if st.button("🔍 Extract Text"):
            with st.spinner("Processing your document... This may take a moment."):
                try:
                    # Process the uploaded file to get a list of images
                    images = file_handler.process_uploaded_file(uploaded_file)
                    
                    if not images:
                        st.warning("Could not extract any images from the uploaded file.")
                        st.stop()

                    total_text = ""
                    for i, image_np in enumerate(images):
                        st.subheader(f"📄 Page {i + 1}")
                        
                        # Display the original (or converted) image
                        st.image(image_np, caption=f"Original - Page {i + 1}", use_column_width=True)
                        
                        # Preprocess the image
                        processed_image = image_processor.preprocess_image(image_np, enhancement_level)
                        
                        # Extract text
                        extracted_text = ocr_engine.extract_text(processed_image)
                        
                        # Display results
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(processed_image, caption=f"Processed - Page {i + 1}", use_column_width=True)
                        with col2:
                            st.text_area("Extracted Text", extracted_text, height=300)
                        
                        total_text += f"--- Page {i + 1} ---\n{extracted_text}\n\n"

                    # --- Download Options ---
                    if total_text:
                        st.subheader("💾 Download Extracted Text")
                        
                        base_filename = os.path.splitext(uploaded_file.name)[0]
                        
                        # TXT Download
                        txt_path = file_handler.save_text_to_file(total_text, base_filename, 'txt')
                        if txt_path:
                            with open(txt_path, "rb") as f:
                                st.download_button(
                                    label="Download as .txt",
                                    data=f,
                                    file_name=f"{base_filename}.txt",
                                    mime="text/plain"
                                )
                        
                        # DOCX Download
                        docx_path = file_handler.save_text_to_file(total_text, base_filename, 'docx')
                        if docx_path:
                            with open(docx_path, "rb") as f:
                                st.download_button(
                                    label="Download as .docx",
                                    data=f,
                                    file_name=f"{base_filename}.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )

                except Exception as e:
                    show_processing_error(e, logger)

if __name__ == "__main__":
    main() 