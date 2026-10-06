/**
 * Guest IP Assignment Module
 * Handles guest IP assignment and release operations
 */

(function() {
    'use strict';
    
    // Module state
    let modal = null;
    let form = null;
    let confirmButton = null;
    let spinner = null;
    let formErrors = null;
    let guestNameInput = null;
    let guestIPAddressInput = null;
    
    /**
     * Initialize the guest IP assignment module
     */
    function initGuestIPAssignment() {
        // Get modal elements
        modal = document.getElementById('guestAssignmentModal');
        form = document.getElementById('guestAssignmentForm');
        confirmButton = document.getElementById('confirmAssignButton');
        spinner = confirmButton ? confirmButton.querySelector('.spinner-border') : null;
        formErrors = document.getElementById('assignFormErrors');
        guestNameInput = document.getElementById('guestName');
        guestIPAddressInput = document.getElementById('guestIPAddress');
        
        if (!modal || !form || !confirmButton) {
            console.error('Guest IP assignment modal elements not found');
            return;
        }
        
        // Set up event listener for the top "Assign Guest IP" button
        const assignGuestIPButton = document.getElementById('assignGuestIPButton');
        if (assignGuestIPButton) {
            assignGuestIPButton.addEventListener('click', showAssignmentModal);
        }
        
        // Set up event listeners for release buttons (delegate to handle dynamic content)
        document.addEventListener('click', handleReleaseButtonClick);
        
        // Set up confirm button
        confirmButton.addEventListener('click', handleConfirmAssignment);
        
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
        if (guestNameInput) {
            guestNameInput.addEventListener('input', () => clearFieldError(guestNameInput));
        }
        if (guestIPAddressInput) {
            guestIPAddressInput.addEventListener('input', () => clearFieldError(guestIPAddressInput));
        }
        
        // Handle Enter key in inputs
        if (guestNameInput) {
            guestNameInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleConfirmAssignment();
                }
            });
        }
        if (guestIPAddressInput) {
            guestIPAddressInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    guestNameInput.focus();
                }
            });
        }
    }
    
    /**
     * Handle clicks on release buttons
     */
    function handleReleaseButtonClick(e) {
        if (e.target.classList.contains('release-guest-btn')) {
            e.preventDefault();
            const ipId = e.target.getAttribute('data-ip-id');
            const ipAddress = e.target.getAttribute('data-ip-address');
            const guestName = e.target.getAttribute('data-guest-name');
            handleReleaseGuest(ipId, ipAddress, guestName);
        }
    }
    
    /**
     * Show the assignment modal
     */
    function showAssignmentModal() {
        if (modal) {
            // Reset form
            form.reset();
            clearAllErrors();
            
            // Show modal
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
            
            // Focus on IP address input
            if (guestIPAddressInput) {
                setTimeout(() => guestIPAddressInput.focus(), 100);
            }
        }
    }
    
    /**
     * Hide the modal
     */
    function hideModal() {
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }
    
    /**
     * Validate IP address format
     */
    function validateIPAddress() {
        const ipAddress = guestIPAddressInput.value.trim();
        
        if (!ipAddress) {
            showFieldError('guestIPAddress', 'IP address is required');
            return false;
        }
        
        // Basic IP address format validation
        const ipPattern = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
        if (!ipPattern.test(ipAddress)) {
            showFieldError('guestIPAddress', 'Invalid IP address format (e.g., 192.168.1.100)');
            return false;
        }
        
        // Check each octet is 0-255
        const octets = ipAddress.split('.');
        for (let i = 0; i < 4; i++) {
            const octet = parseInt(octets[i]);
            if (octet < 0 || octet > 255) {
                showFieldError('guestIPAddress', 'IP address octets must be between 0 and 255');
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Validate guest name input
     */
    function validateGuestName() {
        const guestName = guestNameInput.value.trim();
        
        if (!guestName) {
            showFieldError('guestName', 'Guest name is required');
            return false;
        }
        
        if (guestName.length > 150) {
            showFieldError('guestName', 'Guest name must be 150 characters or less');
            return false;
        }
        
        return true;
    }
    
    /**
     * Handle confirm assignment button click
     */
    function handleConfirmAssignment() {
        // Clear previous errors
        clearAllErrors();
        
        // Validate inputs
        const isIPValid = validateIPAddress();
        const isNameValid = validateGuestName();
        
        if (!isIPValid || !isNameValid) {
            return;
        }
        
        // Get form data
        const ipAddress = guestIPAddressInput.value.trim();
        const guestName = guestNameInput.value.trim();
        
        // Show loading indicator
        showLoading();
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Send AJAX request
        fetch('/assets/guest-ip/assign/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams({
                ip_address: ipAddress,
                guest_name: guestName
            })
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
            
            if (result.ok && result.data.success) {
                handleAssignSuccess(result.data);
            } else {
                handleAssignError(result.data);
            }
        })
        .catch(error => {
            hideLoading();
            handleAssignError({
                error: 'Network error. Please try again.'
            });
        });
    }
    
    /**
     * Handle successful assignment
     */
    function handleAssignSuccess(data) {
        // Show success message
        showSuccessMessage(data.message || 'IP assigned to guest successfully');
        
        // Close modal
        hideModal();
        
        // Reload page to show updated IP status
        setTimeout(() => {
            window.location.reload();
        }, 500);
    }
    
    /**
     * Handle assignment error
     */
    function handleAssignError(data) {
        if (data.error) {
            showGeneralError(data.error);
        } else {
            showGeneralError('An unexpected error occurred. Please try again.');
        }
    }
    
    /**
     * Handle guest IP release
     */
    function handleReleaseGuest(ipId, ipAddress, guestName) {
        // Show confirmation dialog
        const confirmed = confirm(`Release IP ${ipAddress} from guest ${guestName}?`);
        
        if (!confirmed) {
            return;
        }
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Send AJAX request
        fetch('/assets/guest-ip/release/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams({
                ip_id: ipId
            })
        })
        .then(response => {
            return response.json().then(data => ({
                status: response.status,
                ok: response.ok,
                data: data
            }));
        })
        .then(result => {
            if (result.ok && result.data.success) {
                handleReleaseSuccess(result.data);
            } else {
                handleReleaseError(result.data);
            }
        })
        .catch(error => {
            handleReleaseError({
                error: 'Network error. Please try again.'
            });
        });
    }
    
    /**
     * Handle successful release
     */
    function handleReleaseSuccess(data) {
        // Show success message
        showSuccessMessage(data.message || 'IP released successfully');
        
        // Reload page to show updated IP status
        setTimeout(() => {
            window.location.reload();
        }, 500);
    }
    
    /**
     * Handle release error
     */
    function handleReleaseError(data) {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('An unexpected error occurred. Please try again.');
        }
    }
    
    /**
     * Show loading indicator
     */
    function showLoading() {
        if (spinner) {
            spinner.style.display = 'inline-block';
        }
        if (confirmButton) {
            confirmButton.disabled = true;
        }
    }
    
    /**
     * Hide loading indicator
     */
    function hideLoading() {
        if (spinner) {
            spinner.style.display = 'none';
        }
        if (confirmButton) {
            confirmButton.disabled = false;
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
        if (guestNameInput) {
            clearFieldError(guestNameInput);
        }
        if (guestIPAddressInput) {
            clearFieldError(guestIPAddressInput);
        }
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
        document.addEventListener('DOMContentLoaded', initGuestIPAssignment);
    } else {
        initGuestIPAssignment();
    }
})();
