"""
XML Validator Module
Handles extraction and validation of XML files from zip archives.
"""
import zipfile
import os
import tempfile
import shutil
from datetime import datetime
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
    
    def get_xml_file_timestamps(self) -> Dict[str, str]:
        """
        Get timestamps for XML files from the zip archive.
        
        Returns:
            Dictionary mapping XML file paths to their timestamps (formatted as strings)
        """
        timestamps = {}
        
        if not os.path.exists(self.zip_path):
            return timestamps
        
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                # Get all XML files found in the extracted directory
                xml_files = self.find_xml_files()
                
                # Create a mapping of relative paths to full paths
                # We need to match zip entries to extracted XML files
                for xml_path in xml_files:
                    # Get relative path from extract folder
                    rel_path = os.path.relpath(xml_path, self.extract_folder)
                    
                    # Try to find matching entry in zip
                    # Handle both forward and backward slashes
                    zip_entry = None
                    for entry_name in zip_ref.namelist():
                        # Normalize paths for comparison
                        normalized_entry = entry_name.replace('\\', '/')
                        normalized_rel = rel_path.replace('\\', '/')
                        
                        if normalized_entry == normalized_rel or normalized_entry.endswith('/' + normalized_rel):
                            zip_entry = entry_name
                            break
                        # Also check if the entry name matches the filename
                        if os.path.basename(normalized_entry) == os.path.basename(normalized_rel):
                            zip_entry = entry_name
                            break
                    
                    if zip_entry:
                        try:
                            zip_info = zip_ref.getinfo(zip_entry)
                            # zip_info.date_time is a tuple: (year, month, day, hour, minute, second)
                            dt = datetime(*zip_info.date_time)
                            timestamps[xml_path] = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except (KeyError, ValueError, TypeError):
                            # If we can't get timestamp, use file system timestamp as fallback
                            try:
                                file_stat = os.stat(xml_path)
                                dt = datetime.fromtimestamp(file_stat.st_mtime)
                                timestamps[xml_path] = dt.strftime('%Y-%m-%d %H:%M:%S')
                            except OSError:
                                timestamps[xml_path] = 'Unknown'
                    else:
                        # If not found in zip, use file system timestamp
                        try:
                            file_stat = os.stat(xml_path)
                            dt = datetime.fromtimestamp(file_stat.st_mtime)
                            timestamps[xml_path] = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except OSError:
                            timestamps[xml_path] = 'Unknown'
        except Exception as e:
            print(f"Warning: Could not extract timestamps: {str(e)}")
        
        return timestamps
    
    def read_xml_file(self, xml_filename: str) -> Tuple[bool, str, Optional[str], Optional[str]]:
        """
        Read and return the contents of a specific XML file.
        
        Args:
            xml_filename: Name of the XML file to read (can be just filename or relative path)
        
        Returns:
            Tuple of (success, message, content, actual_filename)
        """
        if not self.extract_folder:
            return False, "No extraction folder. Please extract zip file first.", None, None
        
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
            return False, f"File '{xml_filename}' not found in extracted folder.", None, None
        
        try:
            with open(target_path, 'r', encoding='utf-8') as file:
                content = file.read()
            actual_filename = os.path.basename(target_path)
            return True, f"Successfully read '{xml_filename}'", content, actual_filename
        except Exception as e:
            return False, f"Error reading file: {str(e)}", None, None
    
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
            'xml_timestamps': {},
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
        
        # Get timestamps for XML files
        result['xml_timestamps'] = self.get_xml_file_timestamps()
        
        # Read target XML if specified, otherwise read first XML file
        if target_xml:
            success, msg, content, actual_filename = self.read_xml_file(target_xml)
            result['xml_content'] = content
            result['xml_filename'] = actual_filename if actual_filename else target_xml
            if not success:
                result['message'] += f" | {msg}"
            else:
                result['success'] = True
        else:
            # If no target XML specified, read the first XML file if available
            if result['xml_files']:
                first_xml_path = result['xml_files'][0]
                first_xml_filename = os.path.basename(first_xml_path)
                success, msg, content, actual_filename = self.read_xml_file(first_xml_filename)
                result['xml_content'] = content
                result['xml_filename'] = actual_filename if actual_filename else first_xml_filename
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
