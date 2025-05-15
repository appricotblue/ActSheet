from .models import admin_tb,branch_tb,shift_tb,zone_tb,window_zone_tb,team_leader_tb,agent_tb,client_tb,job_tb,staff_tb,task_tb,customer_tb,staff_attendance_tb,task_request_tb,time_period_tb,complaint_ticket_tb,agent_checkin_checkout_tb


def getDataCountAllTemplate(request):  
    complaint_data          = []
    checkin_data            = None
    if request.session.has_key('adminId'):
        complaint_data      = complaint_ticket_tb.objects.all().filter(status="Pending")
        return {'complaint_data' : len(complaint_data),'checkin_data' : checkin_data}
    elif request.session.has_key('teamLeadertId'):
        get_team_leader_id  = request.session['teamLeadertId']
        team_leader_id      = team_leader_tb.objects.get(id=get_team_leader_id)

        complaint_data      = complaint_ticket_tb.objects.all().filter(status="Pending",team_leader_id=team_leader_id)
        
        return {'complaint_data' : len(complaint_data),'checkin_data' : checkin_data}
    elif request.session.has_key('agentId'):
        agent_id            = request.session['agentId']
        get_checkin_data    = agent_checkin_checkout_tb.objects.filter(agent_id=agent_id).last()
        checkin_data        = get_checkin_data.status

        return {'complaint_data' : len(complaint_data),'checkin_data' : checkin_data}
    else:
        return {'complaint_data' : len(complaint_data),'checkin_data' : checkin_data}
    