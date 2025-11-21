"""
XML Validator Module
Handles extraction and validation of XML files from zip archives.
"""
import zipfile
import os
import tempfile
import shutil
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class XMLValidator:
    """Class to handle XML file extraction and validation from zip files."""
    
    def __init__(self, zip_path: str, extract_to: Optional[str] = None):
        """
        Initialize XML Validator.
        
        Args:
            zip_path: Path to the zip file
            extract_to: Optional directory to extract to. If None, uses temp directory.
        """
        self.zip_path = zip_path
        self.extract_to = extract_to
        self.extracted_files = []
        self.extract_folder = None
        
    def validate_zip(self) -> Tuple[bool, str]:
        """
        Validate that the zip file exists and is readable.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not os.path.exists(self.zip_path):
            return False, f"Zip file '{self.zip_path}' not found."
        
        if not zipfile.is_zipfile(self.zip_path):
            return False, f"'{self.zip_path}' is not a valid zip file."
        
        return True, ""
    
    def extract_zip(self) -> Tuple[bool, str, List[str]]:
        """
        Extract the zip file and list all files.
        
        Returns:
            Tuple of (success, message, list_of_files)
        """
        is_valid, error = self.validate_zip()
        if not is_valid:
            return False, error, []
        
        try:
            # Create extraction directory
            if self.extract_to:
                self.extract_folder = self.extract_to
                os.makedirs(self.extract_folder, exist_ok=True)
            else:
                # Use temp directory
                self.extract_folder = tempfile.mkdtemp(prefix='xmlvalidator_')
            
            # Extract zip file
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.extract_folder)
                self.extracted_files = zip_ref.namelist()
            
            return True, f"Files extracted to: '{self.extract_folder}'", self.extracted_files
            
        except zipfile.BadZipFile:
            return False, "Invalid or corrupted zip file.", []
        except Exception as e:
            return False, f"Error extracting zip file: {str(e)}", []
    
    def find_xml_files(self) -> List[str]:
        """
        Find all XML files in the extracted directory.
        
        Returns:
            List of XML file paths
        """
        if not self.extract_folder or not os.path.exists(self.extract_folder):
            return []
        
        xml_files = []
        for root, dirs, files in os.walk(self.extract_folder):
            for file in files:
                if file.lower().endswith('.xml'):
                    xml_files.append(os.path.join(root, file))
        
        return xml_files
    
    def read_xml_file(self, xml_filename: str) -> Tuple[bool, str, Optional[str]]:
        """
        Read and return the contents of a specific XML file.
        
        Args:
            xml_filename: Name of the XML file to read (can be just filename or relative path)
        
        Returns:
            Tuple of (success, message, content)
        """
        if not self.extract_folder:
            return False, "No extraction folder. Please extract zip file first.", None
        
        # Try to find the file
        target_path = None
        
        # First, try direct path
        direct_path = os.path.join(self.extract_folder, xml_filename)
        if os.path.exists(direct_path):
            target_path = direct_path
        else:
            # Search in extracted files
            for root, dirs, files in os.walk(self.extract_folder):
                for file in files:
                    if file == xml_filename or file.endswith(xml_filename):
                        target_path = os.path.join(root, file)
                        break
                if target_path:
                    break
        
        if not target_path or not os.path.exists(target_path):
            return False, f"File '{xml_filename}' not found in extracted folder.", None
        
        try:
            with open(target_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return True, f"Successfully read '{xml_filename}'", content
        except Exception as e:
            return False, f"Error reading file: {str(e)}", None
    
    def cleanup(self):
        """Clean up extracted files if using temp directory."""
        if self.extract_folder and self.extract_to is None:
            try:
                if os.path.exists(self.extract_folder):
                    shutil.rmtree(self.extract_folder)
            except Exception as e:
                print(f"Warning: Could not cleanup temp directory: {str(e)}")
    
    def process_zip(self, target_xml: Optional[str] = None) -> Dict:
        """
        Complete workflow: validate, extract, and optionally read a specific XML file.
        
        Args:
            target_xml: Optional XML filename to read after extraction
        
        Returns:
            Dictionary with results
        """
        result = {
            'success': False,
            'message': '',
            'extracted_files': [],
            'xml_files': [],
            'xml_content': None,
            'xml_filename': target_xml
        }
        
        # Extract zip
        success, message, files = self.extract_zip()
        result['extracted_files'] = files
        result['message'] = message
        
        if not success:
            result['message'] = message
            return result
        
        # Find all XML files
        result['xml_files'] = self.find_xml_files()
        
        # Read target XML if specified
        if target_xml:
            success, msg, content = self.read_xml_file(target_xml)
            result['xml_content'] = content
            if not success:
                result['message'] += f" | {msg}"
            else:
                result['success'] = True
        else:
            result['success'] = True
        
        return result


def validate_zip_file(zip_path: str, target_xml: Optional[str] = None) -> Dict:
    """
    Convenience function to validate and process a zip file.
    
    Args:
        zip_path: Path to zip file
        target_xml: Optional XML filename to read
    
    Returns:
        Dictionary with results
    """
    validator = XMLValidator(zip_path)
    try:
        return validator.process_zip(target_xml)
    finally:
        validator.cleanup()
