"""Views for branch management."""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from assets.models import Branch
from assets.forms.branch_form import BranchForm
from assets.permissions import AdminRequiredMixin


class BranchListView(LoginRequiredMixin, ListView):
    """Display list of all branches."""
    model = Branch
    template_name = 'assets/branch_list.html'
    context_object_name = 'branches'
    login_url = '/login/'
    
    def get_queryset(self):
        """Return all branches ordered by name."""
        return Branch.objects.all().order_by('name')


class BranchCreateView(AdminRequiredMixin, CreateView):
    """Handle branch creation (admin only)."""
    model = Branch
    form_class = BranchForm
    template_name = 'assets/branch_form.html'
    success_url = reverse_lazy('branch_list')
    
    def form_valid(self, form):
        """Save the branch and display success message."""
        response = super().form_valid(form)
        messages.success(self.request, f'Branch "{self.object.name}" created successfully.')
        return response
    
    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class BranchUpdateView(AdminRequiredMixin, UpdateView):
    """Handle branch updates (admin only)."""
    model = Branch
    form_class = BranchForm
    template_name = 'assets/branch_form.html'
    success_url = reverse_lazy('branch_list')
    pk_url_kwarg = 'pk'
    
    def form_valid(self, form):
        """Save the branch and display success message."""
        response = super().form_valid(form)
        messages.success(self.request, f'Branch "{self.object.name}" updated successfully.')
        return response
    
    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class BranchDeleteView(AdminRequiredMixin, DeleteView):
    """Handle branch deletion (admin only)."""
    model = Branch
    template_name = 'assets/branch_confirm_delete.html'
    success_url = reverse_lazy('branch_list')
    pk_url_kwarg = 'pk'
    
    def delete(self, request, *args, **kwargs):
        """Delete the branch and display success message."""
        branch = self.get_object()
        branch_name = branch.name
        
        # Check if branch has assets
        if branch.assets.exists():
            messages.error(
                request,
                f'Cannot delete branch "{branch_name}" because it has {branch.assets.count()} assets assigned to it. '
                'Please reassign the assets to another branch first.'
            )
            return redirect('branch_list')
        
        messages.success(request, f'Branch "{branch_name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)
