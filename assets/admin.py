from django.contrib import admin
from .models import OperatingSystem, Team, IPRange, HyperVVM, TestingDevice, Accessory


@admin.register(OperatingSystem)
class OperatingSystemAdmin(admin.ModelAdmin):
    """Admin configuration for OperatingSystem model."""
    list_display = ['name', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    ordering = ['name']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin configuration for Team model with hierarchy support and branch filtering."""
    list_display = ['get_hierarchy_display', 'branch', 'parent', 'sub_team_count', 'created_at']
    list_filter = ['branch', 'parent', 'created_at']
    search_fields = ['name', 'branch__name', 'parent__name']
    readonly_fields = ['created_at', 'sub_team_count']
    ordering = ['branch__name', 'parent__name', 'name']
    
    fieldsets = (
        ('Team Information', {
            'fields': ('name', 'branch', 'parent')
        }),
        ('Metadata', {
            'fields': ('created_at', 'sub_team_count'),
            'classes': ('collapse',)
        }),
    )
    
    def get_hierarchy_display(self, obj):
        """Display team name with hierarchy indication."""
        return obj.get_hierarchy_display()
    get_hierarchy_display.short_description = 'Team Name'
    
    def sub_team_count(self, obj):
        """Display count of sub-teams."""
        return obj.sub_teams.count()
    sub_team_count.short_description = 'Sub-Teams'
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related('branch', 'parent').prefetch_related('sub_teams')
    
    def delete_model(self, request, obj):
        """Override delete to log cascade information."""
        sub_teams = list(obj.sub_teams.all())
        if sub_teams:
            from django.contrib import messages
            sub_team_names = ', '.join([st.name for st in sub_teams])
            messages.warning(
                request,
                f"Deleting parent team '{obj.name}' will also delete {len(sub_teams)} sub-team(s): {sub_team_names}"
            )
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Override bulk delete to log cascade information."""
        from django.contrib import messages
        total_sub_teams = 0
        for obj in queryset:
            total_sub_teams += obj.sub_teams.count()
        
        if total_sub_teams > 0:
            messages.warning(
                request,
                f"Deleting these teams will also delete {total_sub_teams} sub-team(s) due to cascade behavior."
            )
        super().delete_queryset(request, queryset)


@admin.register(IPRange)
class IPRangeAdmin(admin.ModelAdmin):
    """Admin configuration for IPRange model."""
    list_display = ['range_pattern', 'network_prefix', 'created_at']
    search_fields = ['range_pattern', 'network_prefix']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    ordering = ['range_pattern']


@admin.register(HyperVVM)
class HyperVVMAdmin(admin.ModelAdmin):
    """Admin configuration for HyperVVM model."""
    list_display = ['name', 'host_machine', 'get_display_ip', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'host_machine']
    search_fields = ['name', 'host_machine__asset_tag', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('VM Information', {
            'fields': ('name', 'host_machine', 'ip_address', 'manual_ip', 'is_active')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related(
            'host_machine',
            'host_machine__ip_address',
            'ip_address'
        )


@admin.register(TestingDevice)
class TestingDeviceAdmin(admin.ModelAdmin):
    """Admin configuration for TestingDevice model."""
    list_display = ['device_name', 'assigned_user', 'get_ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['device_name', 'assigned_user']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['device_name']
    
    fieldsets = (
        ('Device Information', {
            'fields': ('device_name', 'assigned_user', 'ip_address', 'manual_ip')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related('ip_address')



@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    """Admin configuration for Accessory model."""
    list_display = ['accessory_name', 'asset', 'quantity', 'provided_date']
    list_filter = ['provided_date', 'created_at']
    search_fields = ['accessory_name', 'accessory_details', 'asset__asset_tag', 'asset__assigned_to']
    readonly_fields = ['provided_date', 'created_at', 'updated_at']
    ordering = ['-provided_date']
    
    fieldsets = (
        ('Accessory Information', {
            'fields': ('asset', 'accessory_name', 'accessory_details', 'quantity')
        }),
        ('Metadata', {
            'fields': ('provided_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related('asset')
