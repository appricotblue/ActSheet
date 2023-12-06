from django.urls import path,include
from ActSheetApp import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
     path('admin-login/', views.adminLogin ,name='admin-login'),
     path('admin-dashboard/', views.adminDashboard, name='admin-dashboard'),
     path('admin-logout/', views.adminLogout, name='admin-logout'),
     path('list-branch/', views.listBranch, name='list-branch'),
     path('add-branch/', views.addNewBranch, name='add-branch'),
     path('edit-branch/', views.updateBranch, name='edit-branch'),
     path('delete-branch/', views.deleteBranch, name='delete-branch'),
     path('list-shift/', views.listAllShift, name='list-shift'),
     path('add-shift/', views.addNewShift, name='add-shift'),
     path('edit-shift/', views.updateShift, name='edit-shift'),
     path('delete-shift/', views.deleteShift, name='delete-shift'),
     path('list-zones/', views.listAllZones, name='list-zones'),
     path('add-zone/', views.addNewZone, name='add-zone'),
     path('edit-zone/', views.updateZone, name='edit-zone'),
     path('delete-zone/', views.deleteZone, name='delete-zone'),
     path('list-window-zones/', views.listAllWindowZones, name='list-window-zones'),
     path('add-window-zones/', views.addNewWindowZone, name='add-window-zone'),
     path('edit-window-zone/', views.updateWindowZone, name='edit-window_zone'),
     path('delete-window-zone/', views.deleteWindowZone, name='delete-window-zone'),
     path('list-team-leader/', views.listTeamLeader, name='list-team-leader'),
     path('add-team-leader/', views.addNewTeamLeader, name='add-team-leader'),
     path('edit-team-leader/', views.updateTeamLeader, name='edit-team-leader'),
     path('delete-team-leader/', views.deleteTeamLeader, name='delete-team-leader'),
     path('list-agent/', views.listAgent, name='list-agent'),
     path('add-agent/', views.addNewAgent, name='add-agent'),
     path('edit-agent/', views.updateAgent, name='edit-agent'),
     path('delete-agent/', views.deleteAgent, name='delete-agent'),
     path('list-client/', views.listClient, name='list-client'),
     path('add-client/', views.addNewClient, name='add-client'),
     path('edit-client/', views.updateClient, name='edit-client'),
     path('delete-client/', views.deleteClient, name='delete-client'),
     path('list-jobs/', views.listJob, name='list-jobs'),
     path('add-job/', views.addNewJob, name='add-job'),
     path('edit-job/', views.updateJob, name='edit-job'),
     path('delete-job/', views.deleteJob, name='delete-job'),
     path('view-job/', views.viewJobData, name='view-job'),

     path('list-staff/', views.listStaff, name='list-staff'),
     path('add-staff/', views.addStaff, name='add-staff'),
     path('edit-staff/', views.updateStaff, name='edit-staff'),
     path('delete-staff/', views.deleteStaff, name='delete-staff'),
     path('list-task/', views.listTask, name='list-task'),
     path('add-task/', views.addNewTask, name='add-task'),
     path('edit-task/', views.updateTask, name='edit-task'),
     path('delete-task/', views.deleteTask, name='delete-task'),
     path('revoke-task/', views.revokeTask, name='revoke-task'),


     path('list-customer/', views.listCustomer, name='list-customer'),
     path('add-customer/', views.addNewCustomer, name='add-customer'),
     path('edit-customer/', views.updateCustomer, name='edit-customer'),
     path('delete-customer/', views.deleteCustomer, name='delete-customer'),
     path('add-customer-confirm/', views.addCustomerConfirmation, name='add-customer-confirm'),


     path('list-attendance/', views.listStaffAttendance, name='list-attendance'),
     path('add-attendance/', views.addAttendance, name='add-attendance'),
     path('view-attendance/', views.viewAttendance, name='view-attendance'),
     path('edit-attendance/', views.editAttendance, name='edit-attendance'),
     path('delete-attendance/', views.deleteStaffAttendance, name='delete-attendance'),
     path('search-staff-attendance/', views.searchStaffAttendance, name='search-staff-attendance'),
     path('approve-staff-attendance/', views.approveStaffAttendance, name='approve-staff-attendance'),
     path('list-approve-attendance/', views.listStaffApprovedAttendance, name='list-approve-attendance'),


     path('staff-data/', views.getStaffData, name='staff-data'),
     path('report/', views.getReport, name='report'),
     path('get-filter-category/', views.getFilterCategory, name='get-filter-category'),
     path('user-login/', views.userLogin ,name='user-login'),
     path('agent-dashboard/', views.agentDashboard, name='agent-dashboard'),
     path('view-task/', views.viewTask, name='view-task'),
     path('task-submit/', views.taskSubmitToTeamLeader, name='task-submit'),
     path('user-logout/', views.userLogout, name='user-logout'),
     path('store-clientId/', views.storeClientIdInSession, name='store-clientId'),
     path('team-leader-dashboard/', views.teamLeaderDashboard, name='team-leader-dashboard'),
     path('', views.clientLogin ,name='client-login'),
     path('client-dashboard/', views.clientDashboard, name='client-dashboard'),
     path('client-activities/', views.clientActivities, name='client-activities'),
     path('client-logout/', views.clientLogout, name='client-logout'),
     path('task-request/', views.taskRequest, name='task-request'),
     path('search-task/', views.searchTask, name='search-task'),
     path('change-request-status/', views.changeStatusOfTaskRequest, name='change-request-status'),

     path('complaint-ticket/', views.complaintTicket, name='complaint-ticket'),
     path('list-complaint-tickets/', views.listcomplaintTicket, name='list-complaint-tickets'),
     path('edit-complaint-ticket/', views.editComplaintTicketStatus, name='edit-complaint-ticket'),

     path('delay-task-request/', views.delayTaskRequest, name='delay-task-request'),
     path('change-delay-request-status/', views.changeStatusOfDelayTaskRequest, name='change-delay-request-status'),

     path('agent-attendance/', views.agentCheckInCheckOut, name='agent-attendance'),
     path('list-agent-attendance/', views.listAgentAttendace, name='list-agent-attendance'),

     path('message/', views.listClientMessage, name='client-message'),
     path('client-send-message/', views.clientSendMessage, name='client-send-message'),


     path('import/', views.importRecord, name='import'),
     path('task/', views.clientTaskList, name='task'),

     path('attendance/', views.listClientStaffAttendance, name='attendance'),
     path('search-attendance/', views.searchClientStaffAttendance, name='search-attendance'),


     path('list-task-based-job/', views.listTaskBasedJob, name='list-task-based-job'),
     path('filter-task-by-type/', views.filterTaskByType, name='filter-task-by-client'),

     path('search-job/', views.searchJob, name='search-job'),
     path('filter-job-by-client/', views.jobFilterByClient, name='filter-job-by-client'),

     path('get-client-branch/', views.getClientBranch, name='get-client-branch'),
     path('get-filter-type/', views.getComplaintTicketFilterType, name='get-filter-type'),
     path('filter-complaint-ticket/', views.filtercomplaintTicket, name='filter-complaint-ticket'),

     path('task-submitted/', views.listTaskSubmittedToTeamLeader, name='task-submitted'),
     path('task-approved/', views.approveTask, name='task-approved'),

     path('job-completed/', views.completeJob, name='job-completed'),
     path('job-completed-mail/', views.completeJobSendMail, name='job-completed-mail'),
     path('notification-seen/', views.updateNotificationSeen, name='notification-seen'),
     
     path('delay-request-history/', views.delayRequestHistory, name='delay-request-history'),
     path('edit-request-history/', views.editRequestHistory, name='edit-request-history'),

     path('list-all-staff/', views.listClientWiseStaff, name='list-client-staff'),

     path('get-branch-staff/', views.getFilterBranchStaff, name='get-branch-staff'),
     path('get-client-branch/', views.getFilterClientBranch, name='get-client-branch'),
     path('repeat-customer-ids/', views.getRepeatCustomerId, name='repeat-customer-ids'),

     path('job-wise-email-approved-task/', views.sendJobWiseMailApprovedTaskToBranch, name='job-wise-email-approved-task'),
     path('job-wise-email-approved-task-send/', views.sendJobWiseMailApprovedTask, name='job-wise-email-approved-task-send'),

     path('user-forgot-password-email/', views.userForgotPasswordEmail, name='user-forgot-password-email'),
     path('tl-forgot-password/', views.tlForgotPassword, name='tl-forgot-password'),
     path('agent-forgot-password/', views.agentForgotPassword, name='agent-forgot-password'),
     path('client-forgot-password-email/', views.clientForgotPasswordEmail, name='client-forgot-password-email'),
     path('client-forgot-password/', views.clientForgotPassword, name='client-forgot-password'),
     path('admin-forgot-password-email/', views.adminForgotPasswordEmail, name='admin-forgot-password-email'),
     path('admin-forgot-password/', views.adminForgotPassword, name='admin-forgot-password'),

     path('update-client-password/', views.updateClientPassword, name='update-client-password'),
     path('update-agent-password/', views.updateAgentPassword, name='update-agent-password'),
     path('update-tl-password/', views.updateTLPassword, name='update-tl-password'),

     path('get-task-filter-type/', views.getTaskFilterType, name='get-task-filter-type'),
     path('check-staff-email/', views.checkStaffEmail, name='check-staff-email'),
     path('check-agent-email/', views.checkAgentEmail, name='check-agent-email'),
     path('check-tl-email/', views.checkTLEmail, name='check-tl-email'),

     path('list-approved-task/', views.listApprovedTask, name='list-approved-task'),
     path('filter-list-approved-task/', views.filterApprovedTaskTaskByType, name='filter-list-approved-task'),
     path('search-list-approved-task/', views.searchApprovedTask, name='search-list-approved-task'),


]    

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)