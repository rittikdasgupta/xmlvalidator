"""
Script to create a test ZIP file of approximately 50MB with XML files inside.
"""
import zipfile
import os
import tempfile
import xml.etree.ElementTree as ET
import random
import string

def create_large_xml_file(filepath, target_size_mb=10):
    """
    Create an XML file of approximately target_size_mb MB.
    
    Args:
        filepath: Path where to save the XML file
        target_size_mb: Target size in MB
    """
    target_size_bytes = target_size_mb * 1024 * 1024
    
    # Create XML structure
    root = ET.Element("test_data")
    root.set("version", "1.0")
    
    # Add metadata
    metadata = ET.SubElement(root, "metadata")
    ET.SubElement(metadata, "created_by").text = "XML Validator Test Generator"
    ET.SubElement(metadata, "purpose").text = "Testing 50MB file size limit"
    
    # Create data section with repetitive content to reach target size
    data_section = ET.SubElement(root, "data")
    
    # Each entry is about 500 bytes, so we need approximately target_size_bytes / 500 entries
    bytes_written = 0
    entry_count = 0
    
    # Write in chunks to avoid memory issues
    chunk_size = 1000  # Number of entries per chunk
    
    while bytes_written < target_size_bytes:
        for i in range(chunk_size):
            entry = ET.SubElement(data_section, "entry")
            entry.set("id", f"entry_{entry_count:08d}")
            
            # Use more varied content to reduce compression ratio
            import random
            import string
            
            ET.SubElement(entry, "name").text = f"Test Entry {entry_count} - {''.join(random.choices(string.ascii_letters + string.digits, k=50))}"
            ET.SubElement(entry, "description").text = f"This is test entry {entry_count} with unique identifier {entry_count * 12345} used for testing the 50MB file size limit. Random data: {''.join(random.choices(string.ascii_letters + string.digits, k=100))}"
            ET.SubElement(entry, "value").text = f"Value_{entry_count}_{entry_count * 7}_{entry_count * 13}_" + ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=300))
            ET.SubElement(entry, "timestamp").text = f"2024-{(entry_count % 12) + 1:02d}-{(entry_count % 28) + 1:02d}T{(entry_count % 24):02d}:{(entry_count % 60):02d}:{(entry_count % 60):02d}+00:00"
            ET.SubElement(entry, "category").text = f"category_{entry_count % 10}"
            ET.SubElement(entry, "status").text = random.choice(["active", "inactive", "pending", "completed", "failed"])
            
            # Add nested elements with varied content
            details = ET.SubElement(entry, "details")
            ET.SubElement(details, "field1").text = ''.join(random.choices(string.ascii_letters + string.digits, k=100))
            ET.SubElement(details, "field2").text = ''.join(random.choices(string.ascii_letters + string.digits, k=100))
            ET.SubElement(details, "field3").text = ''.join(random.choices(string.ascii_letters + string.digits, k=100))
            ET.SubElement(details, "field4").text = ''.join(random.choices(string.ascii_letters + string.digits, k=100))
            ET.SubElement(details, "random_data").text = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=200))
            
            entry_count += 1
        
        # Write to file periodically to check size
        tree = ET.ElementTree(root)
        tree.write(filepath, encoding='utf-8', xml_declaration=True)
        bytes_written = os.path.getsize(filepath)
        
        if bytes_written >= target_size_bytes:
            break
    
    print(f"Created XML file: {filepath} ({bytes_written / 1024 / 1024:.2f} MB, {entry_count} entries)")


def create_test_zip(output_path="test_50mb.zip", target_size_mb=50):
    """
    Create a ZIP file of approximately target_size_mb MB with XML files.
    
    Args:
        output_path: Path for the output ZIP file
        target_size_mb: Target size in MB
    """
    print(f"Creating test ZIP file of approximately {target_size_mb}MB...")
    
    # Remove existing file if it exists
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"Removed existing file: {output_path}")
    
    # Create temporary directory for XML files
    temp_dir = tempfile.mkdtemp(prefix='xml_test_')
    
    try:
        xml_files = []
        total_size = 0
        target_size_bytes = target_size_mb * 1024 * 1024
        
        # Create multiple XML files to reach target size
        # With less repetitive content, compression will be less effective (~60-70% compression)
        # Target: ~50MB compressed, so we need ~70-80MB uncompressed
        # Check if we want a file just under the limit
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == '--under-limit':
            file_sizes = [22, 22, 18, 13]  # MB per file (uncompressed) - just under limit
        else:
            file_sizes = [25, 25, 20, 15]  # MB per file (uncompressed) - over limit
        
        for i, size_mb in enumerate(file_sizes):
            xml_path = os.path.join(temp_dir, f"test_data_{i+1}.xml")
            create_large_xml_file(xml_path, size_mb)
            xml_files.append(xml_path)
            total_size += os.path.getsize(xml_path)
        
        print(f"\nTotal uncompressed size: {total_size / 1024 / 1024:.2f} MB")
        print(f"Creating ZIP file...")
        
        # Create ZIP file
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for xml_file in xml_files:
                zipf.write(xml_file, os.path.basename(xml_file))
                print(f"  Added: {os.path.basename(xml_file)}")
        
        # Check final ZIP size
        zip_size = os.path.getsize(output_path)
        zip_size_mb = zip_size / 1024 / 1024
        
        print(f"\n✓ ZIP file created: {output_path}")
        print(f"  Final size: {zip_size_mb:.2f} MB ({zip_size:,} bytes)")
        
        if zip_size_mb >= target_size_mb * 0.95:  # Within 5% of target
            print(f"  ✓ File size is close to target ({target_size_mb}MB)")
        else:
            print(f"  ⚠ File size is smaller than target. You may need to adjust file_sizes array.")
        
        # List contents
        with zipfile.ZipFile(output_path, 'r') as zipf:
            print(f"\nZIP file contents:")
            for info in zipf.infolist():
                print(f"  - {info.filename} ({info.file_size / 1024 / 1024:.2f} MB uncompressed)")
        
    finally:
        # Cleanup temp directory
        import shutil
        shutil.rmtree(temp_dir)
        print(f"\nCleaned up temporary files.")


if __name__ == '__main__':
    import sys
    
    # Check if user wants a file just under 50MB (for testing acceptance)
    if len(sys.argv) > 1 and sys.argv[1] == '--under-limit':
        output_file = "test_49mb.zip"
        # Create a file just under 50MB
        file_sizes = [24, 24, 19, 14]  # Slightly smaller
        print("Creating test ZIP file just under 50MB limit...")
    else:
        output_file = "test_50mb.zip"
        print("Creating test ZIP file over 50MB limit (for rejection testing)...")
    
    create_test_zip(output_file, target_size_mb=50)
    print(f"\n✅ Test ZIP file ready: {output_file}")

