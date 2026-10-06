/**
 * VM Creation Module
 * Handles quick VM creation from the Free IP page
 */

(function() {
    'use strict';
    
    // Module state
    let modal = null;
    let form = null;
    let submitButton = null;
    let spinner = null;
    let formErrors = null;
    
    /**
     * Initialize the VM creation modal
     */
    function initVMCreationModal() {
        // Get DOM elements
        const addVMButton = document.getElementById('addVMButton');
        modal = document.getElementById('vmCreationModal');
        form = document.getElementById('vmCreationForm');
        submitButton = document.getElementById('createVMButton');
        spinner = submitButton ? submitButton.querySelector('.spinner-border') : null;
        formErrors = document.getElementById('formErrors');
        
        if (!addVMButton || !modal || !form || !submitButton) {
            console.error('VM creation modal elements not found');
            return;
        }
        
        // Set up event listeners
        addVMButton.addEventListener('click', showModal);
        submitButton.addEventListener('click', handleSubmit);
        
        // Set up cancel buttons
        const cancelButtons = modal.querySelectorAll('.modal-close, .btn-cancel');
        cancelButtons.forEach(button => {
            button.addEventListener('click', hideModal);
        });
        
        // Close modal when clicking outside
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                hideModal();
            }
        });
        
        // Set up input validation
        const vmIPInput = document.getElementById('vmIP');
        const baseMachineIPInput = document.getElementById('baseMachineIP');
        
        if (vmIPInput) {
            vmIPInput.addEventListener('input', () => clearFieldError(vmIPInput));
        }
        
        if (baseMachineIPInput) {
            baseMachineIPInput.addEventListener('input', () => clearFieldError(baseMachineIPInput));
        }
    }
    
    /**
     * Show the VM creation modal
     */
    function showModal() {
        if (modal) {
            // Reset form
            form.reset();
            clearAllErrors();
            
            // Show modal
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }
    
    /**
     * Hide the VM creation modal
     */
    function hideModal() {
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }
    
    /**
     * Validate IPv4 address format
     */
    function validateIPv4(ip) {
        const ipv4Pattern = /^(\d{1,3}\.){3}\d{1,3}$/;
        if (!ipv4Pattern.test(ip)) {
            return false;
        }
        
        // Check each octet is 0-255
        const octets = ip.split('.');
        for (let octet of octets) {
            const num = parseInt(octet, 10);
            if (num < 0 || num > 255) {
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Validate form inputs
     */
    function validateForm() {
        let isValid = true;
        
        const vmIP = document.getElementById('vmIP').value.trim();
        const baseMachineIP = document.getElementById('baseMachineIP').value.trim();
        
        // Validate VM IP
        if (!vmIP) {
            showFieldError('vmIP', 'VM IP address is required');
            isValid = false;
        } else if (!validateIPv4(vmIP)) {
            showFieldError('vmIP', 'Please enter a valid IPv4 address');
            isValid = false;
        }
        
        // Validate Base Machine IP
        if (!baseMachineIP) {
            showFieldError('baseMachineIP', 'Base Machine IP address is required');
            isValid = false;
        } else if (!validateIPv4(baseMachineIP)) {
            showFieldError('baseMachineIP', 'Please enter a valid IPv4 address');
            isValid = false;
        }
        
        return isValid;
    }
    
    /**
     * Handle form submission
     */
    function handleSubmit(e) {
        e.preventDefault();
        
        // Clear previous errors
        clearAllErrors();
        
        // Validate form
        if (!validateForm()) {
            return;
        }
        
        // Collect form data
        const formData = new FormData();
        formData.append('vm_ip', document.getElementById('vmIP').value.trim());
        formData.append('base_machine_ip', document.getElementById('baseMachineIP').value.trim());
        formData.append('vm_name', document.getElementById('vmName').value.trim());
        
        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        formData.append('csrfmiddlewaretoken', csrfToken);
        
        // Show loading indicator
        showLoading();
        
        // Submit via AJAX
        submitVMForm(formData);
    }
    
    /**
     * Submit VM form via AJAX
     */
    function submitVMForm(formData) {
        fetch('/assets/vms/quick-create/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => {
            return response.json().then(data => ({
                status: response.status,
                ok: response.ok,
                data: data
            }));
        })
        .then(result => {
            hideLoading();
            
            if (result.ok) {
                handleSuccess(result.data);
            } else {
                handleError(result.data);
            }
        })
        .catch(error => {
            hideLoading();
            handleError({
                error: 'Network error. Please try again.',
                field_errors: {}
            });
        });
    }
    
    /**
     * Handle successful VM creation
     */
    function handleSuccess(data) {
        // Show success message
        showSuccessMessage(data.message || 'VM created successfully');
        
        // Close modal
        hideModal();
        
        // Refresh page to show new VM
        setTimeout(() => {
            window.location.reload();
        }, 500);
    }
    
    /**
     * Handle error response
     */
    function handleError(data) {
        // Show general error message
        if (data.error) {
            showGeneralError(data.error);
        }
        
        // Show field-specific errors
        if (data.field_errors) {
            for (let field in data.field_errors) {
                const errors = data.field_errors[field];
                if (errors && errors.length > 0) {
                    showFieldError(field, errors[0]);
                }
            }
        }
    }
    
    /**
     * Show loading indicator
     */
    function showLoading() {
        if (spinner) {
            spinner.style.display = 'inline-block';
        }
        if (submitButton) {
            submitButton.disabled = true;
        }
    }
    
    /**
     * Hide loading indicator
     */
    function hideLoading() {
        if (spinner) {
            spinner.style.display = 'none';
        }
        if (submitButton) {
            submitButton.disabled = false;
        }
    }
    
    /**
     * Show general error message
     */
    function showGeneralError(message) {
        if (formErrors) {
            formErrors.textContent = message;
            formErrors.style.display = 'block';
        }
    }
    
    /**
     * Show field-specific error
     */
    function showFieldError(fieldName, message) {
        const input = document.getElementById(fieldName);
        if (input) {
            input.classList.add('error');
            const feedback = input.nextElementSibling;
            if (feedback && feedback.classList.contains('error-message')) {
                feedback.textContent = message;
                feedback.style.display = 'block';
            }
        }
    }
    
    /**
     * Clear field error
     */
    function clearFieldError(input) {
        if (input) {
            input.classList.remove('error');
            const feedback = input.nextElementSibling;
            if (feedback && feedback.classList.contains('error-message')) {
                feedback.textContent = '';
                feedback.style.display = 'none';
            }
        }
    }
    
    /**
     * Clear all errors
     */
    function clearAllErrors() {
        // Clear general error
        if (formErrors) {
            formErrors.textContent = '';
            formErrors.style.display = 'none';
        }
        
        // Clear field errors
        const inputs = form.querySelectorAll('.form-control');
        inputs.forEach(input => clearFieldError(input));
    }
    
    /**
     * Show success message
     */
    function showSuccessMessage(message) {
        // Create a temporary alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-success';
        alert.style.position = 'fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.style.padding = '15px 20px';
        alert.style.backgroundColor = '#d4edda';
        alert.style.color = '#155724';
        alert.style.border = '1px solid #c3e6cb';
        alert.style.borderRadius = '4px';
        alert.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
        alert.textContent = message;
        document.body.appendChild(alert);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            alert.remove();
        }, 3000);
    }
    
    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVMCreationModal);
    } else {
        initVMCreationModal();
    }
})();
