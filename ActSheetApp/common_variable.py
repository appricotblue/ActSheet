from .models import admin_tb,branch_tb,shift_tb,zone_tb,window_zone_tb,team_leader_tb,agent_tb,client_tb,job_tb,staff_tb,task_tb,customer_tb,staff_attendance_tb,task_request_tb,time_period_tb,complaint_ticket_tb,agent_checkin_checkout_tb,message_tb,notification_tb


def getDataCountAllTemplate(request):  
    complaint_data          = []
    checkin_data            = None
    unread_message          = 0
    get_notification        = []
    notification_count      = 0
    name                    = None
    if request.session.has_key('adminId'):
        adminId             = request.session['adminId']
        complaint_data      = complaint_ticket_tb.objects.all().filter(status="Pending")
        unread_message      = message_tb.objects.all().filter(admin_id=adminId,status='Send').exclude(sender='Admin').count()
        get_notification    = notification_tb.objects.all().filter(admin_id=adminId,admin_seen=False)
        notification_count  = len(get_notification)
        name                = 'Admin'

        return {'complaint_data' : len(complaint_data),'checkin_data' : checkin_data,'unread_message':unread_message,'get_notification':get_notification,'notification_count':notification_count,'name':name}
    elif request.session.has_key('teamLeadertId'):
        get_team_leader_id  = request.session['teamLeadertId']
        team_leader_id      = team_leader_tb.objects.get(id=get_team_leader_id)
        complaint_data      = complaint_ticket_tb.objects.all().filter(status="Pending",team_leader_id=team_leader_id)
        unread_message      = message_tb.objects.all().filter(team_leader_id=team_leader_id,status='Send').exclude(sender='Team Leader').count()
        get_notification    = notification_tb.objects.all().filter(team_leader_id=team_leader_id,team_leader_seen=False)
        notification_count  = len(get_notification)
        name                = team_leader_id.name

        return {'complaint_data' : len(complaint_data),'checkin_data' : checkin_data,'unread_message':unread_message,'get_notification':get_notification,'notification_count':notification_count,'name':name}
    elif request.session.has_key('agentId'):
        agent_id            = request.session['agentId']
        get_checkin_data    = agent_checkin_checkout_tb.objects.filter(agent_id=agent_id).last()
        checkin_data        = None if not get_checkin_data else get_checkin_data.status
        get_notification    = notification_tb.objects.all().filter(agent_id=agent_id,agent_seen=False)
        unread_message      = message_tb.objects.all().filter(agent_id=agent_id,status='Send').exclude(sender='Agent').count()
        notification_count  = len(get_notification)

        agent_data          = agent_tb.objects.get(id=agent_id)
        name                = agent_data.name

        return {'complaint_data' : len(complaint_data),'checkin_data' : checkin_data,'unread_message':unread_message,'get_notification':get_notification,'notification_count':notification_count,'name':name}
    elif request.session.has_key('clientId'):
        client_id           = request.session['clientId']
        unread_message      = message_tb.objects.all().filter(client_id=client_id,status='Send').exclude(sender='Client').count()
        get_notification    = notification_tb.objects.all().filter(client_id=client_id,client_seen=False)
        notification_count  = len(get_notification)

        client_data         = client_tb.objects.get(id=client_id)
        name                = client_data.name

        return {'complaint_data' : len(complaint_data),'checkin_data' : checkin_data,'unread_message': unread_message,'get_notification':get_notification,'notification_count':notification_count,'name':name}
    else:
        return {'complaint_data' : len(complaint_data),'checkin_data' : checkin_data,'unread_message':unread_message,'get_notification':get_notification,'notification_count':notification_count,'name':name}
    