// Main JavaScript for Threat-Aware Training Recommender

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeFormValidation();
    initializeFileUpload();
    initializeTextareaEnhancements();
    initializeTooltips();
    initializeProgressiveEnhancement();
    initializeAccessibility();
});

/**
 * Form Validation Enhancement
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const fileInput = form.querySelector('input[type="file"]');
            const urlsInput = form.querySelector('#urls');
            const textInput = form.querySelector('#news_text');
            
            // Check if file is provided
            if (!fileInput || !fileInput.files.length) {
                e.preventDefault();
                showAlert('Please select an Excel file to upload.', 'danger');
                fileInput?.focus();
                return;
            }
            
            // Check if at least one news source is provided
            const hasUrls = urlsInput && urlsInput.value.trim();
            const hasText = textInput && textInput.value.trim();
            
            if (!hasUrls && !hasText) {
                e.preventDefault();
                showAlert('Please provide at least one news source (URLs or direct text).', 'warning');
                urlsInput?.focus();
                return;
            }
            
            // Validate file type
            const file = fileInput.files[0];
            const allowedTypes = ['.xlsx', '.xls'];
            const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
            
            if (!allowedTypes.includes(fileExtension)) {
                e.preventDefault();
                showAlert('Please upload a valid Excel file (.xlsx or .xls)', 'danger');
                fileInput.focus();
                return;
            }
            
            // Validate file size (10MB limit)
            const maxSize = 10 * 1024 * 1024; // 10MB in bytes
            if (file.size > maxSize) {
                e.preventDefault();
                showAlert('File size must be less than 10MB. Please choose a smaller file.', 'danger');
                fileInput.focus();
                return;
            }
            
            // Show processing state
            showProcessingState(form);
        });
    });
}

/**
 * File Upload Enhancements
 */
function initializeFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        // Create custom file upload display
        const wrapper = document.createElement('div');
        wrapper.className = 'file-upload-wrapper';
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        
        // Add file info display
        const fileInfo = document.createElement('div');
        fileInfo.className = 'file-info mt-2 text-muted small';
        wrapper.appendChild(fileInfo);
        
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const fileSize = formatFileSize(file.size);
                const fileName = file.name;
                fileInfo.innerHTML = `
                    <i class="fas fa-file-excel text-success me-2"></i>
                    <strong>${fileName}</strong> (${fileSize})
                `;
                fileInfo.classList.add('text-success');
                
                // Validate file in real-time
                validateFile(file, fileInfo);
            } else {
                fileInfo.innerHTML = '';
                fileInfo.classList.remove('text-success', 'text-danger');
            }
        });
        
        // Drag and drop functionality
        wrapper.addEventListener('dragover', function(e) {
            e.preventDefault();
            wrapper.classList.add('dragover');
        });
        
        wrapper.addEventListener('dragleave', function() {
            wrapper.classList.remove('dragover');
        });
        
        wrapper.addEventListener('drop', function(e) {
            e.preventDefault();
            wrapper.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                input.dispatchEvent(new Event('change'));
            }
        });
    });
}

/**
 * Textarea Enhancements
 */
function initializeTextareaEnhancements() {
    const textareas = document.querySelectorAll('textarea');
    
    textareas.forEach(textarea => {
        // Add character counter for news text
        if (textarea.id === 'news_text') {
            addCharacterCounter(textarea);
        }
        
        // Add URL validation for URLs textarea
        if (textarea.id === 'urls') {
            addURLValidation(textarea);
        }
        
        // Auto-resize functionality
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight + 2) + 'px';
        });
        
        // Focus enhancement
        textarea.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        textarea.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
}

/**
 * Initialize Tooltips
 */
function initializeTooltips() {
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Progressive Enhancement Features
 */
function initializeProgressiveEnhancement() {
    // Add loading states to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        if (button.type === 'submit') {
            button.addEventListener('click', function() {
                // Add slight delay to show loading state
                setTimeout(() => {
                    if (this.form && this.form.checkValidity()) {
                        this.disabled = true;
                        this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                    }
                }, 100);
            });
        }
    });
    
    // Add smooth scroll for internal links
    const internalLinks = document.querySelectorAll('a[href^="#"]');
    internalLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

/**
 * Accessibility Enhancements
 */
function initializeAccessibility() {
    // Add ARIA labels to form elements
    const formElements = document.querySelectorAll('input, textarea, select');
    formElements.forEach(element => {
        if (!element.getAttribute('aria-label') && !element.getAttribute('aria-labelledby')) {
            const label = element.closest('.mb-3, .mb-4')?.querySelector('label');
            if (label) {
                const labelId = label.id || `label-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
                label.id = labelId;
                element.setAttribute('aria-labelledby', labelId);
            }
        }
    });
    
    // Add keyboard navigation for accordions
    const accordionButtons = document.querySelectorAll('.accordion-button');
    accordionButtons.forEach(button => {
        button.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
}

/**
 * Utility Functions
 */

function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert.auto-alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show auto-alert`;
    alert.setAttribute('role', 'alert');
    
    const icon = getAlertIcon(type);
    alert.innerHTML = `
        ${icon}
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert at top of main content
    const container = document.querySelector('main .container, main');
    if (container) {
        container.insertBefore(alert, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 150);
            }
        }, 5000);
    }
    
    // Scroll to alert
    alert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function getAlertIcon(type) {
    const icons = {
        'success': '<i class="fas fa-check-circle me-2"></i>',
        'danger': '<i class="fas fa-exclamation-triangle me-2"></i>',
        'warning': '<i class="fas fa-exclamation-circle me-2"></i>',
        'info': '<i class="fas fa-info-circle me-2"></i>'
    };
    return icons[type] || icons['info'];
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function validateFile(file, infoElement) {
    const allowedTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'];
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    let isValid = true;
    let errors = [];
    
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls)$/i)) {
        errors.push('Invalid file type. Please upload an Excel file (.xlsx or .xls)');
        isValid = false;
    }
    
    if (file.size > maxSize) {
        errors.push('File size exceeds 10MB limit');
        isValid = false;
    }
    
    if (!isValid) {
        infoElement.classList.remove('text-success');
        infoElement.classList.add('text-danger');
        infoElement.innerHTML = `
            <i class="fas fa-exclamation-triangle text-danger me-2"></i>
            ${errors.join(', ')}
        `;
    }
    
    return isValid;
}

function addCharacterCounter(textarea) {
    const counter = document.createElement('div');
    counter.className = 'character-counter text-muted small mt-1';
    textarea.parentNode.appendChild(counter);
    
    function updateCounter() {
        const length = textarea.value.length;
        const maxLength = 10000; // Reasonable limit for news text
        counter.textContent = `${length.toLocaleString()} characters`;
        
        if (length > maxLength * 0.9) {
            counter.classList.add('text-warning');
        } else {
            counter.classList.remove('text-warning');
        }
        
        if (length > maxLength) {
            counter.classList.add('text-danger');
            counter.textContent += ` (exceeds recommended limit of ${maxLength.toLocaleString()})`;
        } else {
            counter.classList.remove('text-danger');
        }
    }
    
    textarea.addEventListener('input', updateCounter);
    updateCounter(); // Initial count
}

function addURLValidation(textarea) {
    const validator = document.createElement('div');
    validator.className = 'url-validator mt-2';
    textarea.parentNode.appendChild(validator);
    
    textarea.addEventListener('input', debounce(function() {
        validateURLs(this.value, validator);
    }, 500));
}

function validateURLs(text, validatorElement) {
    if (!text.trim()) {
        validatorElement.innerHTML = '';
        return;
    }
    
    const urls = text.split('\n').map(url => url.trim()).filter(url => url);
    const urlPattern = /^https?:\/\/.+\..+/i;
    
    let validCount = 0;
    let invalidUrls = [];
    
    urls.forEach(url => {
        if (urlPattern.test(url)) {
            validCount++;
        } else {
            invalidUrls.push(url);
        }
    });
    
    if (invalidUrls.length === 0) {
        validatorElement.innerHTML = `
            <small class="text-success">
                <i class="fas fa-check-circle me-1"></i>
                ${validCount} valid URL${validCount !== 1 ? 's' : ''} found
            </small>
        `;
    } else {
        validatorElement.innerHTML = `
            <small class="text-warning">
                <i class="fas fa-exclamation-triangle me-1"></i>
                ${validCount} valid, ${invalidUrls.length} invalid URL${invalidUrls.length !== 1 ? 's' : ''}
            </small>
        `;
    }
}

function showProcessingState(form) {
    // Disable all form elements
    const formElements = form.querySelectorAll('input, textarea, button');
    formElements.forEach(element => {
        element.disabled = true;
    });
    
    // Show processing message
    const processingDiv = document.createElement('div');
    processingDiv.className = 'processing-overlay text-center p-4 bg-light border rounded mt-3';
    processingDiv.innerHTML = `
        <div class="spinner-border text-primary mb-3" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <h6>Processing your request...</h6>
        <p class="text-muted mb-0">This may take a few minutes depending on the amount of data.</p>
    `;
    
    form.appendChild(processingDiv);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for testing or external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatFileSize,
        validateFile,
        showAlert,
        debounce
    };
}