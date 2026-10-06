# Additional IP Toggle Bugfix Requirements Document

## Introduction

The "Additional IP Addresses" section in the asset form allows users to add multiple supplementary IP addresses (WiFi, Mobile, VPN, etc.) with custom labels. Each additional IP entry has radio buttons to toggle between "Managed IP" (dropdown selection) and "Manual IP" (text input). Currently, this toggle is not working - the form fields remain visible/hidden regardless of which radio button is selected. The primary IP address toggle works correctly, so the issue is isolated to the additional IP formset entries.

This impacts users who need to switch between managed and manual IP entry modes when configuring additional IP addresses for assets.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN a user clicks the "Managed IP" radio button in an additional IP formset entry THEN the system does not show the managed IP dropdown or hide the manual IP input field

1.2 WHEN a user clicks the "Manual IP" radio button in an additional IP formset entry THEN the system does not show the manual IP input field or hide the managed IP dropdown

1.3 WHEN a new additional IP form is dynamically added via the "Add Additional IP" button THEN the IP type toggle functionality is not initialized for that new form

1.4 WHEN the page loads with existing additional IP entries THEN the IP type toggles do not respond to radio button clicks

### Expected Behavior (Correct)

2.1 WHEN a user clicks the "Managed IP" radio button in an additional IP formset entry THEN the system SHALL display the managed IP dropdown field and hide the manual IP input field

2.2 WHEN a user clicks the "Manual IP" radio button in an additional IP formset entry THEN the system SHALL display the manual IP input field and hide the managed IP dropdown field

2.3 WHEN a new additional IP form is dynamically added via the "Add Additional IP" button THEN the system SHALL initialize the IP type toggle functionality for that new form so that radio button selections immediately toggle field visibility

2.4 WHEN the page loads with existing additional IP entries THEN the system SHALL initialize IP type toggles for all existing forms and set the correct initial visibility state based on the selected radio button

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a user interacts with the primary IP address toggle (the working one at the top of the form) THEN the system SHALL CONTINUE TO correctly toggle between managed IP dropdown and manual IP input

3.2 WHEN a user adds or removes additional IP forms using the "Add Additional IP" and "Remove" buttons THEN the system SHALL CONTINUE TO correctly manage the formset (adding new forms, marking forms for deletion, re-indexing)

3.3 WHEN a user clicks radio buttons for other fields in the form (e.g., system type, if any) THEN the system SHALL CONTINUE TO function correctly without interference from the IP toggle fix

3.4 WHEN the form is submitted with additional IPs THEN the system SHALL CONTINUE TO correctly save managed and manual IP addresses as before
