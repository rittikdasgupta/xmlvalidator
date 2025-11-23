// Main JavaScript for XML Validator

document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const fileInfo = document.getElementById('fileInfo');
    const submitBtn = document.getElementById('submitBtn');
    const loader = document.getElementById('loader');
    const resultsSection = document.getElementById('resultsSection');
    const closeResults = document.getElementById('closeResults');

    // Drag and drop functionality
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB in bytes
            
            if (file.size > MAX_FILE_SIZE) {
                showError(`File "${file.name}" is too large (${(file.size / 1024 / 1024).toFixed(2)} MB). Maximum size is 50 MB.`);
                return;
            }
            
            // Create a new FileList-like object (DataTransfer doesn't allow direct assignment)
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            updateFileInfo(file);
        }
    });

    // Browse button click handler
    const browseBtn = document.getElementById('browseBtn');
    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent triggering dropZone click
        fileInput.click();
    });

    // Click on drop zone (but not on the button) to open file dialog
    dropZone.addEventListener('click', (e) => {
        // Only trigger if click is not on the button
        if (e.target !== browseBtn && !browseBtn.contains(e.target)) {
            fileInput.click();
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            const isValid = updateFileInfo(e.target.files[0]);
            if (!isValid) {
                // File is too large, show error immediately
                showError('File size exceeds 50 MB limit. Please select a smaller file.');
            }
        }
    });

    function updateFileInfo(file) {
        const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB in bytes
        const fileSize = (file.size / 1024 / 1024).toFixed(2);
        
        if (file.size > MAX_FILE_SIZE) {
            fileInfo.textContent = `❌ File too large: ${fileSize} MB (Maximum: 50 MB)`;
            fileInfo.style.color = 'var(--error-color)';
            // Clear the file input
            fileInput.value = '';
            return false;
        } else {
            fileInfo.textContent = `Selected: ${file.name} (${fileSize} MB)`;
            fileInfo.style.color = 'var(--primary-color)';
            return true;
        }
    }

    // Form submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!fileInput.files || fileInput.files.length === 0) {
            showError('Please select a ZIP file');
            return;
        }

        const formData = new FormData(uploadForm);
        const targetXml = document.getElementById('targetXml').value.trim();

        // Show loading state
        submitBtn.disabled = true;
        loader.style.display = 'block';
        submitBtn.querySelector('.btn-text').textContent = 'Processing...';
        resultsSection.style.display = 'none';

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            // Check if response has content
            const contentType = response.headers.get('content-type');
            const text = await response.text();
            
            // If response is empty, handle it
            if (!text || text.trim().length === 0) {
                showError('Server returned an empty response. Please try again.');
                return;
            }
            
            // Try to parse JSON
            let data;
            try {
                data = JSON.parse(text);
            } catch (jsonError) {
                // If response is not valid JSON, show the raw response or a helpful error
                console.error('Invalid JSON response:', text);
                showError('Server returned an invalid response. Please try again or contact support.');
                return;
            }

            if (response.ok && data.success) {
                showResults(data);
            } else {
                showError(data.error || data.message || 'An error occurred while processing the file');
            }
        } catch (error) {
            // Handle network errors, timeouts, etc.
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                showError('Network error: Could not connect to server. Please check your connection and try again.');
            } else {
                showError('Network error: ' + error.message);
            }
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            loader.style.display = 'none';
            submitBtn.querySelector('.btn-text').textContent = 'Validate & Extract';
        }
    });

    function showResults(data) {
        const statusMessage = document.getElementById('statusMessage');
        // const extractedFilesList = document.getElementById('extractedFilesList');
        const xmlFilesList = document.getElementById('xmlFilesList');
        const xmlContentSection = document.getElementById('xmlContentSection');
        const xmlContent = document.getElementById('xmlContent');

        // Status message
        statusMessage.className = 'status-message success';
        statusMessage.textContent = '✓ ' + (data.message || 'File processed successfully');

        // Extracted files
        // if (data.extracted_files && data.extracted_files.length > 0) {
        //     extractedFilesList.innerHTML = data.extracted_files.map(file => 
        //         `<div class="file-item">${escapeHtml(file)}</div>`
        //     ).join('');
        //     document.getElementById('extractedFilesSection').style.display = 'block';
        // } else {
        //     document.getElementById('extractedFilesSection').style.display = 'none';
        // }

        // XML files with timestamps
        if (data.xml_files && data.xml_files.length > 0) {
            xmlFilesList.innerHTML = data.xml_files.map(file => {
                const timestamp = data.xml_timestamps && data.xml_timestamps[file] 
                    ? `<span class="file-timestamp">${escapeHtml(data.xml_timestamps[file])}</span>` 
                    : '<span class="file-timestamp">Unknown</span>';
                return `<div class="file-item">
                    <span class="file-name">${escapeHtml(file)}</span>
                    ${timestamp}
                </div>`;
            }).join('');
            document.getElementById('xmlFilesSection').style.display = 'block';
        } else {
            document.getElementById('xmlFilesSection').style.display = 'none';
        }

        // XML content
        if (data.xml_content) {
            xmlContent.textContent = data.xml_content;
            
            // Display XML filename if available
            const xmlFilenameDisplay = document.getElementById('xmlFilenameDisplay');
            if (data.xml_filename) {
                xmlFilenameDisplay.textContent = ` File: ${escapeHtml(data.xml_filename)}`;
                xmlFilenameDisplay.style.display = 'block';
            } else {
                xmlFilenameDisplay.style.display = 'none';
            }
            
            xmlContentSection.style.display = 'block';
        } else {
            xmlContentSection.style.display = 'none';
        }

        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function showError(message) {
        const statusMessage = document.getElementById('statusMessage');
        statusMessage.className = 'status-message error';
        statusMessage.textContent = '✗ ' + message;
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Close results
    closeResults.addEventListener('click', () => {
        resultsSection.style.display = 'none';
    });
});

