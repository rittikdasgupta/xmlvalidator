import zipfile
import os

# Step 1: Ask for zip file name
zip_filename = 'C:\Balthazaar\RDD_80.005.09390_001.zip'

# Step 2: Check if zip file exists
if not os.path.exists('C:\Balthazaar\RDD_80.005.09390_001.zip'):
    print(f"File '{C:\Balthazaar\RDD_80.005.09390_001.zip}' not found.")
else:
    # Step 3: Open and extract the zip file
    with zipfile.ZipFile("C:\Balthazaar\RDD_80.005.09390_001.zip", 'r') as zip_ref:
        extract_folder = zip_filename.replace('.zip', '')
        zip_ref.extractall(extract_folder)
        print(f"✅ Files extracted to folder: '{extract_folder}'")

        # Step 4: List all files inside the zip
        print("\n📄 Extracted files:")
        extracted_files = zip_ref.namelist()
        for f in extracted_files:
            print(f)

        # Step 5: Ask for file to read (we'll use 'hello.txt' as per your input)
        target_file = 'STORE3500.xml'
        target_path = os.path.join(extract_folder, target_file)

        # Step 6: Read and print file contents
        if os.path.exists(target_path):
            print("\n📜 Contents of 'STORE3500.xml':\n")
            with open(target_path, 'r', encoding='utf-8') as file:
                content = file.read()
                print(content)
        else:
            print(f"❌ File '{target_file}' not found in extracted folder.")