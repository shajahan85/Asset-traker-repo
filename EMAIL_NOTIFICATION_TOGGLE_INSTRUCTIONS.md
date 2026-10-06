# Email Notification Toggle - Implementation Guide

## Overview
A checkbox has been added to asset forms to allow users to enable/disable email notifications on a per-save basis.

---

## Form Changes

### Form Field Added
In `assets/forms/asset_forms.py`, the following field was added to `AssetForm`:

```python
send_notification = forms.BooleanField(
    required=False,
    initial=True,  # Checked by default
    label='Send Email Notification',
    help_text='Uncheck to prevent email notification for this save',
    widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input',
        'id': 'id_send_notification'
    })
)
```

### Template Updated
In `assets/templates/assets/asset_form.html`, the checkbox is displayed before the submit button:

```html
<!-- Email Notification Control -->
<div class="form-group">
    <div class="form-check">
        {{ form.send_notification }}
        <label class="form-check-label" for="id_send_notification">
            {{ form.send_notification.label }}
        </label>
        <div class="help-text">{{ form.send_notification.help_text }}</div>
    </div>
</div>
```

---

## Notification Service Changes

### Updated Method Signature
The `_send_email` method now accepts a `skip_notification` parameter:

```python
@staticmethod
def _send_email(subject, message, skip_notification=False):
    """
    Internal method to send email.
    
    Args:
        subject: Email subject
        message: Email message body
        skip_notification: If True, skip sending email
    """
    # Check if notification should be skipped
    if skip_notification:
        return
    
    try:
        # ... email sending code ...
```

### All Notification Methods Updated
All notification methods now accept `skip_notification` parameter:

- `send_asset_created_notification(asset, user, skip_notification=False)`
- `send_asset_updated_notification(asset, user, changes=None, skip_notification=False)`
- `send_asset_freed_notification(asset, user, skip_notification=False)` *(needs to be updated)*
- `send_asset_scrapped_notification(asset, user, skip_notification=False)` *(needs to be updated)*
- `send_asset_reassigned_notification(asset, user, skip_notification=False)` *(needs to be updated)*

---

## View Integration Required

### In Asset Create/Update Views

When saving an asset, check the checkbox value and pass it to the notification service:

```python
def asset_create(request):
    # ... view code ...
    
    if form.is_valid():
        asset = form.save()
        
        # Get checkbox value (True if checked, False if unchecked)
        skip_notification = not form.cleaned_data.get('send_notification', True)
        
        # Send notification only if checkbox is checked
        NotificationService.send_asset_created_notification(
            asset=asset,
            user=request.user,
            skip_notification=skip_notification
        )
        
        # ... rest of code ...
```

```python
def asset_update(request, pk):
    # ... view code ...
    
    if form.is_valid():
        asset = form.save()
        
        # Get checkbox value (True if checked, False if unchecked)
        skip_notification = not form.cleaned_data.get('send_notification', True)
        
        # Send notification only if checkbox is checked
        NotificationService.send_asset_updated_notification(
            asset=asset,
            user=request.user,
            skip_notification=skip_notification
        )
        
        # ... rest of code ...
```

---

## Example View Implementations

### Class-Based View Example

```python
from assets.services.notification_service import NotificationService

class AssetUpdateView(UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = 'assets/asset_form.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Get checkbox value
        skip_notification = not form.cleaned_data.get('send_notification', True)
        
        # Send notification
        NotificationService.send_asset_updated_notification(
            asset=self.object,
            user=self.request.user,
            skip_notification=skip_notification
        )
        
        return response
```

### Function-Based View Example

```python
from assets.services.notification_service import NotificationService
from assets.forms.asset_forms import AssetForm

def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            asset = form.save()
            
            # Get checkbox value
            skip_notification = not form.cleaned_data.get('send_notification', True)
            
            # Send notification if checkbox is checked
            NotificationService.send_asset_updated_notification(
                asset=asset,
                user=request.user,
                skip_notification=skip_notification
            )
            
            messages.success(request, 'Asset updated successfully!')
            return redirect('asset_detail', pk=asset.pk)
    else:
        form = AssetForm(instance=asset)
    
    return render(request, 'assets/asset_form.html', {'form': form})
```

---

## User Experience

### Checkbox Behavior:
- **Checked by default** - Normal email sending behavior
- **User unchecks** - Email notification is skipped for that save
- **Helpful text** - "Uncheck to prevent email notification for this save"

### Use Cases:
1. **Bulk Updates** - Uncheck when updating multiple assets to avoid spam
2. **Employee Code Updates** - Uncheck when only updating employee codes
3. **Minor Changes** - Uncheck for changes that don't need notifications
4. **Testing** - Uncheck during testing to avoid sending emails

---

## TODO: Complete the Integration

### Remaining Tasks:

1. **Update other notification methods** (freed, scrapped, reassigned) to accept `skip_notification` parameter

2. **Update all views that call notification methods** to:
   - Check the `send_notification` checkbox value
   - Pass `skip_notification` parameter

3. **Add checkbox to other forms** that trigger notifications:
   - Freed system form
   - Asset reassignment form
   - Asset scrap form

4. **Test the implementation:**
   - Create asset with checkbox checked → Email sent
   - Create asset with checkbox unchecked → No email
   - Update asset with checkbox checked → Email sent
   - Update asset with checkbox unchecked → No email

---

## Quick Reference

### Form Field Name:
`send_notification`

### Logic:
```python
skip_notification = not form.cleaned_data.get('send_notification', True)
```

### Notification Call:
```python
NotificationService.send_asset_updated_notification(
    asset, 
    user, 
    skip_notification=skip_notification
)
```

---

## Benefits

1. **User Control** - Users decide when emails are sent
2. **Prevents Spam** - No emails during bulk updates
3. **Flexible** - Can enable/disable per-save
4. **Default Safe** - Checked by default maintains current behavior
5. **Easy to Use** - Simple checkbox, no complex configuration

---

## Notes

- Checkbox is **checked by default** to maintain current email behavior
- Checkbox value is **not saved to database** (form field only)
- **Each save operation** has its own checkbox state
- Works with all notification types (created, updated, freed, etc.)

