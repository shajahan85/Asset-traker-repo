from django.urls import path
from django.views.generic import TemplateView
from .views import (
    AssetListView, AssetCreateView, AssetDetailView, AssetUpdateView, AssetFreeView, 
    FreeSystemsView, AssetScrapView, ScrappedItemsView, FreeIPsView, 
    WarrantyView, AssetImportView, AssetImportResultsView, AssetExportActiveView, 
    AssetExportFreedView, AssetExportScrappedView, FreeIPsExportView, GetSubTeamsView,
    OperatingSystemListView, AddOperatingSystemView, EditOperatingSystemView, DeleteOperatingSystemView,
    FreedSystemCreateView, FreedSystemEditView, FreedSystemDeleteView, AssetReassignView,
    NetworkDeviceListView, NetworkDeviceCreateView, NetworkDeviceUpdateView, NetworkDeviceDeleteView,
    NetworkDeviceExportView,
    TestingDeviceListView, TestingDeviceCreateView, TestingDeviceUpdateView, TestingDeviceDeleteView,
    TestingDeviceExportView,
    HyperVVMListView, HyperVVMCreateView, HyperVVMUpdateView, HyperVVMDetailView, HyperVVMDeleteView,
    HyperVVMExportView,
    QuickVMCreateView, ScrappedSystemCreateView, DeleteAttachmentView,
    AssetHistoryView, AssetHistoryExportView,
    GetParentTeamsByBranchView, GetSubTeamsByParentAndBranchView,
    TeamManagementView, TeamCreateView, TeamUpdateView, TeamDeleteView, GetTeamsByBranchView,
    GuestIPAssignView, GuestIPReleaseView,
    MarkIPOccupiedView, ReleaseOccupiedIPView,
    EmployeeSearchView, EmployeeAssetsExportView, ChangeAssetTagView
)
from .views_asset_ip import (
    AddSecondaryIPView, RemoveSecondaryIPView, SetPrimaryIPView
)
from .views_branch import (
    BranchListView, BranchCreateView, BranchUpdateView, BranchDeleteView
)
from .views_server_controller import (
    ServerControllerListView, ServerControllerEditView, ServerControllerFreeView,
    ServerControllerReassignView, ServerControllerScrapView, server_controller_export
)

urlpatterns = [
    path('', AssetListView.as_view(), name='asset_list'),
    path('employee-search/', EmployeeSearchView.as_view(), name='employee_search'),
    path('employee-assets-export/', EmployeeAssetsExportView.as_view(), name='employee_assets_export'),
    path('create/', AssetCreateView.as_view(), name='asset_create'),
    path('<int:pk>/', AssetDetailView.as_view(), name='asset_detail'),
    path('<int:pk>/edit/', AssetUpdateView.as_view(), name='asset_update'),
    path('<int:pk>/change-tag/', ChangeAssetTagView.as_view(), name='change_asset_tag'),
    path('<int:pk>/free/', AssetFreeView.as_view(), name='asset_free'),
    path('<int:pk>/reassign/', AssetReassignView.as_view(), name='asset_reassign'),
    path('<int:pk>/add-secondary-ip/', AddSecondaryIPView.as_view(), name='add_secondary_ip'),
    path('ip/<int:pk>/remove/', RemoveSecondaryIPView.as_view(), name='remove_secondary_ip'),
    path('ip/<int:pk>/set-primary/', SetPrimaryIPView.as_view(), name='set_primary_ip'),
    path('attachments/<int:pk>/delete/', DeleteAttachmentView.as_view(), name='delete_attachment'),
    path('freed/', FreeSystemsView.as_view(), name='freed_systems'),
    path('freed/create/', FreedSystemCreateView.as_view(), name='freed_system_create'),
    path('freed/<int:pk>/edit/', FreedSystemEditView.as_view(), name='freed_system_edit'),
    path('freed/<int:pk>/delete/', FreedSystemDeleteView.as_view(), name='freed_system_delete'),
    path('<int:pk>/scrap/', AssetScrapView.as_view(), name='asset_scrap'),
    path('scrapped/', ScrappedItemsView.as_view(), name='scrapped_items'),
    path('scrapped/create/', ScrappedSystemCreateView.as_view(), name='scrapped_system_create'),
    path('ips/free/', FreeIPsView.as_view(), name='free_ips'),
    path('guest-ip/assign/', GuestIPAssignView.as_view(), name='guest_ip_assign'),
    path('guest-ip/release/', GuestIPReleaseView.as_view(), name='guest_ip_release'),
    path('ip/mark-occupied/', MarkIPOccupiedView.as_view(), name='mark_ip_occupied'),
    path('ip/release-occupied/', ReleaseOccupiedIPView.as_view(), name='release_occupied_ip'),
    path('warranty/', WarrantyView.as_view(), name='warranty'),
    
    # Branch management
    path('branches/', BranchListView.as_view(), name='branch_list'),
    path('branches/create/', BranchCreateView.as_view(), name='branch_create'),
    path('branches/<int:pk>/edit/', BranchUpdateView.as_view(), name='branch_update'),
    path('branches/<int:pk>/delete/', BranchDeleteView.as_view(), name='branch_delete'),
    
    # Team management
    path('teams/', TeamManagementView.as_view(), name='team_management'),
    path('teams/create/', TeamCreateView.as_view(), name='team_create'),
    path('teams/<int:pk>/edit/', TeamUpdateView.as_view(), name='team_update'),
    path('teams/<int:pk>/delete/', TeamDeleteView.as_view(), name='team_delete'),
    path('api/teams-by-branch/<int:branch_id>/', GetTeamsByBranchView.as_view(), name='get_teams_by_branch'),
    
    path('import/', AssetImportView.as_view(), name='asset_import'),
    path('import/results/', AssetImportResultsView.as_view(), name='asset_import_results'),
    path('export/active/', AssetExportActiveView.as_view(), name='export_active_assets'),
    path('export/freed/', AssetExportFreedView.as_view(), name='export_freed_assets'),
    path('export/scrapped/', AssetExportScrappedView.as_view(), name='export_scrapped_assets'),
    path('ips/export/free/', FreeIPsExportView.as_view(), name='export_free_ips'),
    path('api/get-sub-teams/', GetSubTeamsView.as_view(), name='get_sub_teams'),
    path('api/get-parent-teams-by-branch/', GetParentTeamsByBranchView.as_view(), name='get_parent_teams_by_branch'),
    path('api/get-sub-teams-by-parent-and-branch/', GetSubTeamsByParentAndBranchView.as_view(), name='get_sub_teams_by_parent_and_branch'),
    path('operating-systems/', OperatingSystemListView.as_view(), name='operating_systems'),
    path('operating-systems/add/', AddOperatingSystemView.as_view(), name='add_operating_system'),
    path('operating-systems/<int:pk>/edit/', EditOperatingSystemView.as_view(), name='edit_operating_system'),
    path('operating-systems/<int:pk>/delete/', DeleteOperatingSystemView.as_view(), name='delete_operating_system'),
    path('network-devices/', NetworkDeviceListView.as_view(), name='network_device_list'),
    path('network-devices/create/', NetworkDeviceCreateView.as_view(), name='network_device_create'),
    path('network-devices/<int:pk>/edit/', NetworkDeviceUpdateView.as_view(), name='network_device_update'),
    path('network-devices/<int:pk>/delete/', NetworkDeviceDeleteView.as_view(), name='network_device_delete'),
    path('network-devices/export/', NetworkDeviceExportView.as_view(), name='export_network_devices'),
    path('testing-devices/', TestingDeviceListView.as_view(), name='testing_device_list'),
    path('testing-devices/create/', TestingDeviceCreateView.as_view(), name='testing_device_create'),
    path('testing-devices/<int:pk>/edit/', TestingDeviceUpdateView.as_view(), name='testing_device_update'),
    path('testing-devices/<int:pk>/delete/', TestingDeviceDeleteView.as_view(), name='testing_device_delete'),
    path('testing-devices/export/', TestingDeviceExportView.as_view(), name='export_testing_devices'),
    path('vms/', HyperVVMListView.as_view(), name='hyperv_vm_list'),
    path('vms/create/', HyperVVMCreateView.as_view(), name='hyperv_vm_create'),
    path('vms/quick-create/', QuickVMCreateView.as_view(), name='quick_vm_create'),
    path('vms/<int:pk>/', HyperVVMDetailView.as_view(), name='hyperv_vm_detail'),
    path('vms/<int:pk>/edit/', HyperVVMUpdateView.as_view(), name='hyperv_vm_update'),
    path('vms/<int:pk>/delete/', HyperVVMDeleteView.as_view(), name='hyperv_vm_delete'),
    path('vms/export/', HyperVVMExportView.as_view(), name='export_hyperv_vms'),
    
    # Server Controller Management
    path('server-controllers/', ServerControllerListView.as_view(), name='server_controller_list'),
    path('server-controllers/<int:pk>/edit/', ServerControllerEditView.as_view(), name='server_controller_edit'),
    path('server-controllers/<int:pk>/free/', ServerControllerFreeView.as_view(), name='server_controller_free'),
    path('server-controllers/<int:pk>/reassign/', ServerControllerReassignView.as_view(), name='server_controller_reassign'),
    path('server-controllers/<int:pk>/scrap/', ServerControllerScrapView.as_view(), name='server_controller_scrap'),
    path('server-controllers/export/', server_controller_export, name='server_controller_export'),
    
    path('test-reassign/', TemplateView.as_view(template_name='assets/test_reassign.html'), name='test_reassign'),
    # Asset History Routes
    path('asset/<int:pk>/history/', AssetHistoryView.as_view(), name='asset_history'),
    path('asset/<int:pk>/history/export/', AssetHistoryExportView.as_view(), name='asset_history_export'),
]
