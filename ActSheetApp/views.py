from django.shortcuts import render
from django.views.decorators.cache import cache_control
from .models import admin_tb,branch_tb,shift_tb,zone_tb,window_zone_tb,team_leader_tb,agent_tb,client_tb,job_tb,staff_tb,task_tb,customer_tb,staff_attendance_tb,task_request_tb,time_period_tb,complaint_ticket_tb,delay_task_request_tb,agent_checkin_checkout_tb,message_tb
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime
import random
import string
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
import json
from django.http import JsonResponse
from django.db.models import Count
from django.db.models import Sum, IntegerField
from django.db.models import F
from django.db.models.functions import Cast
import numpy as np
from channels.db import database_sync_to_async
from django.contrib.sessions.models import Session
from django.utils import timezone
from .forms import imgForm, imgForm1
import csv
# Create your views here.


# Create your views here.

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def adminLogin(request):
    if  request.method=='POST':
        email       = request.POST['email']
        password    = request.POST['password']
        var         = admin_tb.objects.all().filter(email=email,password=password)

        if request.session.has_key('agentId'):
            del request.session['agentId']
        if request.session.has_key('teamLeadertId'):
            del request.session['teamLeadertId']

        if var:
            for x in var:
                request.session['adminId']=x.id
            return redirect('admin-dashboard')
        else:
            return render(request,'admin/login.html',{'msg':"Invalid username or password"})
    else:
        if  request.session.has_key('adminId'):
            return redirect('admin-dashboard')
        else:
            return render(request,'admin/login.html')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def adminDashboard(request):
    if request.session.has_key('adminId'):

        active_clients      = client_tb.objects.all().filter(status='Active').count()
        pending_clients     = client_tb.objects.all().filter(status='Pending').count()
        complete_clients    = client_tb.objects.all().filter(status='Complete').count()

        clients             = [{'active_clients' : active_clients,'pending_clients' : pending_clients,'complete_clients' : complete_clients}]

        active_jobs         = job_tb.objects.all().filter(status='Active').count()
        pending_jobs        = job_tb.objects.all().filter(status='Pending').count()
        complete_jobs       = job_tb.objects.all().filter(status='Complete').count()

        jobs                = [{'active_jobs' : active_jobs,'pending_jobs' : pending_jobs,'complete_jobs' : complete_jobs}]

        pending_task        = task_tb.objects.all().filter(status='Pending')

        sessions    = Session.objects.filter(expire_date__gte=timezone.now())
        agent_list  = []
        tl_list     = []
    
        for session in sessions:
            data        = session.get_decoded()
            agent_id    = data.get('agentId')
            tl_id       = data.get('teamLeadertId')

            if agent_id != None:
                agent_list.append(agent_id)
            if tl_id != None:
                tl_list.append(tl_id)

        online_agent    = len(agent_list)
        online_tl       = len(tl_list)

        count_of_online_user = [{'online_agent' : online_agent,'online_tl' :online_tl}]
        
        return render(request,'admin/dashboard.html',{'clients' : clients ,'jobs':jobs,'pending_task' : pending_task,'count_of_online_user' : count_of_online_user})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listBranch(request):
    if request.session.has_key('adminId'):
        branch_list = branch_tb.objects.all()
        return render(request,'admin/list_branch.html',{'branch_list' : branch_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewBranch(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            name            = request.POST['name']
            getclient_id    = request.POST['client_id']
            client_id       = client_tb.objects.get(id=getclient_id)
            image_file      = imgForm(request.POST,request.FILES)
            image_file1     = imgForm1(request.POST,request.FILES)
            now             = datetime.now()
            image           = None
            image1          = None

            if image_file.is_valid():
                image       = image_file.cleaned_data['image']
            if image_file1.is_valid():
                image1      = image_file1.cleaned_data['image1']

            a               = branch_tb(name=name,client_id=client_id,layout=image,document=image1,created_at=now,updated_at=now)
            a.save()
            messages.success(request, 'Successfully added.')
            return redirect('list-branch')
        else:
            client_list = client_tb.objects.all()
            return render(request,'admin/add_branch.html',{'client_list' : client_list})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateBranch(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            branch_id           = request.GET['id']
            name                = request.POST['name']
            getclient_id        = request.POST['client_id']
            client_id           = branch_tb.objects.get(id=getclient_id)
            now                 = datetime.now()
            image_file          = imgForm(request.POST,request.FILES)
            image_file1         = imgForm1(request.POST,request.FILES)

            branch_tb.objects.all().filter(id=branch_id).update(name=name,client_id=client_id,updated_at=now)

            if image_file.is_valid():
                image           = image_file.cleaned_data['image']
                mymodel         = branch_tb.objects.get(id=branch_id)
                mymodel.layout  = image
                mymodel.save()
            if image_file1.is_valid():
                image1          = image_file1.cleaned_data['image1']
                mymodel         = branch_tb.objects.get(id=branch_id)
                mymodel.document= image1
                mymodel.save()

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-branch')
        else:
            branch_id   = request.GET['id']
            branch_data = branch_tb.objects.all().filter(id=branch_id)
            client_list = client_tb.objects.all()
            return render(request,'admin/edit_branch.html',{'branch_data' : branch_data,'client_list' : client_list})
    else:
        return redirect('admin-login')





@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteBranch(request):
    if request.session.has_key('adminId'):
        branch_id   = request.GET['id']
        fromReg     = branch_tb.objects.all().filter(id=branch_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-branch')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-branch')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listAllShift(request):
    if request.session.has_key('adminId'):
        shift_list  = shift_tb.objects.all()
        return render(request,'admin/list_all_shift.html',{'shift_list' : shift_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewShift(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            from_time   = request.POST['from']
            to_time     = request.POST['to']
            now         = datetime.now()
            a           = shift_tb(from_time=from_time,to_time=to_time,created_at=now,updated_at=now)
            a.save()
            messages.success(request, 'Successfully added.')
            return redirect('list-shift')
        else:
            return render(request,'admin/add_shift.html')
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateShift(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            shift_id    = request.GET['id']
            from_time   = request.POST['from']
            to_time     = request.POST['to']
            now         = datetime.now()

            shift_tb.objects.all().filter(id=shift_id).update(from_time=from_time,to_time=to_time,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-shift')
        else:
            shift_id    = request.GET['id']
            shift_data  = shift_tb.objects.all().filter(id=shift_id)
            return render(request,'admin/edit_shift.html',{'shift_data' : shift_data})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteShift(request):
    if request.session.has_key('adminId'):
        shift_id    = request.GET['id']
        fromReg     = shift_tb.objects.all().filter(id=shift_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-shift')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-shift')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listAllZones(request):
    if request.session.has_key('adminId'):
        zone_list   = zone_tb.objects.all()
        return render(request,'admin/list_zones.html',{'zone_list' : zone_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewZone(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            zone            = request.POST['zone']
            getbranch_id    = request.POST['branch_id']
            branch_id       = branch_tb.objects.get(id=getbranch_id)
            now             = datetime.now()
            branch_data     = branch_tb.objects.all().filter(id=branch_id.id).get()
            client_id       = client_tb.objects.get(id=branch_data.client_id.id)

            a               = zone_tb(zone=zone,client_id=client_id,created_at=now,updated_at=now,branch_id=branch_id)
            a.save()
            messages.success(request, 'Successfully added.')
            return redirect('list-zones')
        else:
            branch_list=branch_tb.objects.all()
            return render(request,'admin/add_zone.html',{'branch_list' : branch_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateZone(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            zone_id         = request.GET['id']
            zone            = request.POST['zone']
            now             = datetime.now()
            getbranch_id    = request.POST['branch_id']
            branch_id       = branch_tb.objects.get(id=getbranch_id)
            branch_data     = branch_tb.objects.all().filter(id=branch_id.id).get()
            client_id       = client_tb.objects.get(id=branch_data.client_id.id)

            zone_tb.objects.all().filter(id=zone_id).update(zone=zone,client_id=client_id,updated_at=now,branch_id=branch_id)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-zones')
        else:
            zone_id         = request.GET['id']
            zone_data       = zone_tb.objects.all().filter(id=zone_id)
            branch_list     = branch_tb.objects.all()
            return render(request,'admin/edit_zone.html',{'zone_data' : zone_data,'branch_list' : branch_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteZone(request):
    if request.session.has_key('adminId'):
        zone_id     = request.GET['id']
        fromReg     = zone_tb.objects.all().filter(id=zone_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-zones')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-zones')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listAllWindowZones(request):
    if request.session.has_key('adminId'):
        zone_list   = window_zone_tb.objects.all()
        return render(request,'admin/list_window_zones.html',{'zone_list' : zone_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewWindowZone(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            zone            = request.POST['zone']
            getbranch_id    = request.POST['branch_id']
            branch_id       = branch_tb.objects.get(id=getbranch_id)
            now             = datetime.now()
            branch_data     = branch_tb.objects.all().filter(id=branch_id.id).get()
            client_id       = client_tb.objects.get(id=branch_data.client_id.id)

            a               = window_zone_tb(zone=zone,client_id=client_id,created_at=now,updated_at=now,branch_id=branch_id)
            a.save()
            messages.success(request, 'Successfully added.')
            return redirect('list-window-zones')
        else:
            branch_list     = branch_tb.objects.all()
            return render(request,'admin/add_window_zone.html',{'branch_list' : branch_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateWindowZone(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            zone_id         = request.GET['id']
            zone            = request.POST['zone']
            now             = datetime.now()
            getbranch_id    = request.POST['branch_id']
            branch_id       = branch_tb.objects.get(id=getbranch_id)
            branch_data     = branch_tb.objects.all().filter(id=branch_id.id).get()
            client_id       = client_tb.objects.get(id=branch_data.client_id.id)

            window_zone_tb.objects.all().filter(id=zone_id).update(zone=zone,client_id=client_id,updated_at=now,branch_id=branch_id)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-zones')
        else:
            zone_id         = request.GET['id']
            zone_data       = window_zone_tb.objects.all().filter(id=zone_id)
            branch_list     = branch_tb.objects.all()
            return render(request,'admin/edit_window_zone.html',{'zone_data' : zone_data,'branch_list' : branch_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteWindowZone(request):
    if request.session.has_key('adminId'):
        zone_id             = request.GET['id']
        fromReg             = window_zone_tb.objects.all().filter(id=zone_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-zones')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-zones')
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listTeamLeader(request):
    if request.session.has_key('adminId'):
        team_leader_list    = team_leader_tb.objects.all()
        return render(request,'admin/list_team_leader.html',{'team_leader_list' : team_leader_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewTeamLeader(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            name            = request.POST['name']
            email           = request.POST['email']
            phone           = request.POST['phone']

            get_tl          = team_leader_tb.objects.all().filter(email=email)

            if get_tl:
                messages.error(request, 'Email already exist')
                return redirect('add-team-leader')
            else:
                # Auto generated password
                lettersLw       = string.ascii_lowercase
                lettersUp       = string.ascii_uppercase
                digits          = '1234567890'
                password        = ''.join(random.choice(digits + lettersLw + lettersUp) for i in range(10))
            
                # password hashchecked
                hash_password   = make_password(password)

                now             = datetime.now()
                a               = team_leader_tb(name=name,email=email,phone=phone,password=hash_password,created_at=now,updated_at=now)
                a.save()

                sendEmail(email,'email/password.html',password)

                messages.success(request, 'Successfully added.')
                return redirect('list-team-leader')
        else:
            return render(request,'admin/add_team_leader.html')
    else:
        return redirect('admin-login')



def sendEmail(email,template,password):
    html_template   = template
    html_message    = render_to_string(html_template,  {'password': password})
    subject         = 'Welcome to ActSheet'
    email_from      = settings.EMAIL_HOST_USER
    recipient_list  = [email]
    message         = EmailMessage(subject, html_message, email_from, recipient_list)
    message.content_subtype = 'html'
    message.send()
    return


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateTeamLeader(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            team_leader_id  = request.GET['id']
            name            = request.POST['name']
            email           = request.POST['email']
            phone           = request.POST['phone']
            now             = datetime.now()

            get_tl          = team_leader_tb.objects.all().filter(email=email).exclude(id=team_leader_id)

            if get_tl:
                messages.error(request, 'Email already exist')
                return redirect('/edit-team-leader?id='+ str(team_leader_id))
            else:
                team_leader_tb.objects.all().filter(id=team_leader_id).update(name=name,email=email,phone=phone,updated_at=now)

                messages.success(request, 'Changes successfully updated.')
                return redirect('list-team-leader')
        else:
            team_leader_id  = request.GET['id']
            team_leader_data= team_leader_tb.objects.all().filter(id=team_leader_id)
            return render(request,'admin/edit_team_leader.html',{'team_leader_data' : team_leader_data})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteTeamLeader(request):
    if request.session.has_key('adminId'):
        team_leader_id  = request.GET['id']
        fromReg         = team_leader_tb.objects.all().filter(id=team_leader_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-team-leader')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-team-leader')
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listAgent(request):
    if request.session.has_key('adminId'):
        agent_list  = agent_tb.objects.all()
        return render(request,'admin/list_agent.html',{'agent_list' : agent_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewAgent(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            name                = request.POST['name']
            email               = request.POST['email']
            phone               = request.POST['phone']
            get_team_leader_id  = request.POST['team_leader_id']
            team_leader_id      = team_leader_tb.objects.get(id=get_team_leader_id)
            total_hrs           = request.POST['total_hrs']
            required_hrs        = request.POST['required_hrs']
            max_break_time      = request.POST['max_break_time']

            
            get_agent           = agent_tb.objects.all().filter(email=email)

            if get_agent:
                messages.error(request, 'Email already exist')
                return redirect('add-agent')
            else:
                # Auto generated password
                lettersLw           = string.ascii_lowercase
                lettersUp           = string.ascii_uppercase
                digits              = '1234567890'
                password            = ''.join(random.choice(digits + lettersLw + lettersUp) for i in range(10))
            
                # password hashchecked
                hash_password       = make_password(password)

                now                 = datetime.now()
                a                   = agent_tb(name=name,email=email,phone=phone,password=hash_password,team_leader_id=team_leader_id,total_hrs=total_hrs,required_hrs=required_hrs,max_break_time=max_break_time,created_at=now,updated_at=now)
                a.save()

                sendEmail(email,'email/password.html',password)

                messages.success(request, 'Successfully added.')
                return redirect('list-agent')
        else:
            team_leader_list    = team_leader_tb.objects.all()
            return render(request,'admin/add_agent.html',{'team_leader_list' : team_leader_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateAgent(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            agent_id            = request.GET['id']
            name                = request.POST['name']
            email               = request.POST['email']
            phone               = request.POST['phone']
            now                 = datetime.now()
            get_team_leader_id  = request.POST['team_leader_id']
            team_leader_id      = team_leader_tb.objects.get(id=get_team_leader_id)
            total_hrs           = request.POST['total_hrs']
            required_hrs        = request.POST['required_hrs']
            max_break_time      = request.POST['max_break_time']

            get_agent           = agent_tb.objects.all().filter(email=email).exclude(id=agent_id)

            if get_agent:
                messages.error(request, 'Email already exist')
                return redirect('/edit-agent?id='+ str(agent_id))
            else:
                agent_tb.objects.all().filter(id=agent_id).update(name=name,email=email,phone=phone,team_leader_id=team_leader_id,total_hrs=total_hrs,required_hrs=required_hrs,max_break_time=max_break_time,updated_at=now)

                messages.success(request, 'Changes successfully updated.')
                return redirect('list-agent')
        else:
            agent_id            = request.GET['id']
            agent_data          = agent_tb.objects.all().filter(id=agent_id)
            team_leader_list    = team_leader_tb.objects.all()
            return render(request,'admin/edit_agent.html',{'team_leader_list' : team_leader_list,'agent_data' : agent_data})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteAgent(request):
    if request.session.has_key('adminId'):
        team_leader_id  = request.GET['id']
        fromReg         = agent_tb.objects.all().filter(id=team_leader_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-agent')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-agent')
    else:
        return redirect('admin-login')





@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listClient(request):
    if request.session.has_key('adminId'):
        client_list  = client_tb.objects.all()
        return render(request,'admin/list_client.html',{'client_list' : client_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewClient(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            name                = request.POST['name']
            email               = request.POST['email']
            phone               = request.POST['phone']
            business            = request.POST['business']

            get_client          = client_tb.objects.all().filter(email=email)

            if get_client:
                messages.error(request, 'Email already exist')
                return redirect('add-client')
            else:
                # Auto generated password
                lettersLw           = string.ascii_lowercase
                lettersUp           = string.ascii_uppercase
                digits              = '1234567890'
                password            = ''.join(random.choice(digits + lettersLw + lettersUp) for i in range(10))
            
                # password hashchecked
                hash_password       = make_password(password)

                now                 = datetime.now()
                a                   = client_tb(name=name,email=email,phone=phone,password=hash_password,business=business,created_at=now,updated_at=now)
                a.save()

                latest_id           = client_tb.objects.latest('id')
                client_id           = 'CLI' + str(latest_id.id)

                client_tb.objects.all().filter(id=latest_id.id).update(client_id=client_id,updated_at=now)

                sendEmail(email,'email/password.html',password)

                messages.success(request, 'Successfully added.')
                return redirect('list-client')
        else:
            return render(request,'admin/add_client.html')
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateClient(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            client_id       = request.GET['id']
            name            = request.POST['name']
            email           = request.POST['email']
            phone           = request.POST['phone']
            business        = request.POST['business']
            now             = datetime.now()

            get_client      = client_tb.objects.all().filter(email=email).exclude(id=client_id)

            if get_client:
                messages.error(request, 'Email already exist')
                return redirect('/edit-client?id='+ str(client_id))
            else:
                client_tb.objects.all().filter(id=client_id).update(name=name,email=email,phone=phone,business=business,updated_at=now)

                messages.success(request, 'Changes successfully updated.')
                return redirect('list-client')
        else:
            client_id       = request.GET['id']
            client_data     = client_tb.objects.all().filter(id=client_id)
            return render(request,'admin/edit_client_data.html',{'client_data' : client_data})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteClient(request):
    if request.session.has_key('adminId'):
        client_id       = request.GET['id']
        fromReg         = client_tb.objects.all().filter(id=client_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-client')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-client')
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listJob(request):
    if request.session.has_key('adminId'):
        job_list  = job_tb.objects.all()
        return render(request,'admin/list_job.html',{'job_list' : job_list})
    elif request.session.has_key('teamLeadertId'):
        if request.session.has_key('client_id'):
            team_leader_id      = request.session['teamLeadertId']
            client_id           = request.session['client_id']

            job_list            = job_tb.objects.all().filter(team_leader_id=team_leader_id,client_id=client_id)
            return render(request,'admin/list_job.html',{'job_list' : job_list})
        else:
            messages.error(request, 'Please select client')
            return redirect('team-leader-dashboard')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewJob(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            title               = request.POST['title']
            description         = request.POST['description']
            start_date          = request.POST['start_date']
            end_date            = request.POST['end_date']
            actual_start_date   = request.POST['actual_start_date']
            actual_end_date     = request.POST['actual_end_date']
            get_team_leader_id  = request.POST['team_leader_id']
            team_leader_id      = team_leader_tb.objects.get(id=get_team_leader_id)
            getbranch_id        = request.POST['branch_id']
            branch_id           = branch_tb.objects.get(id=getbranch_id)
            getclient_id        = request.POST['client_id']
            client_id           = client_tb.objects.get(id=getclient_id)
            now                 = datetime.now()

            a                   = job_tb(title=title,description=description,start_date=start_date,end_date=end_date,actual_start_date=actual_start_date,actual_end_date=actual_end_date,branch_id=branch_id,team_leader_id=team_leader_id,client_id=client_id,created_at=now,updated_at=now)
            a.save()

            latest_id           = job_tb.objects.latest('id')
            job_id              = 'JOB' + str(latest_id.id)

            job_tb.objects.all().filter(id=latest_id.id).update(job_id=job_id,updated_at=now)
           
            messages.success(request, 'Successfully added.')
            return redirect('list-jobs')
        else:
            branch_list         = branch_tb.objects.all()
            team_leader_list    = team_leader_tb.objects.all()
            client_list         = client_tb.objects.all()
            return render(request,'admin/add_job.html',{'branch_list' : branch_list,'team_leader_list' : team_leader_list,'client_list' : client_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateJob(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            job_id              = request.GET['id']
            title               = request.POST['title']
            description         = request.POST['description']
            start_date          = request.POST['start_date']
            end_date            = request.POST['end_date']
            actual_start_date   = request.POST['actual_start_date']
            actual_end_date     = request.POST['actual_end_date']
            get_team_leader_id  = request.POST['team_leader_id']
            team_leader_id      = team_leader_tb.objects.get(id=get_team_leader_id)
            getbranch_id        = request.POST['branch_id']
            branch_id           = branch_tb.objects.get(id=getbranch_id)
            getclient_id        = request.POST['client_id']
            client_id           = client_tb.objects.get(id=getclient_id)
            now                 = datetime.now()

            job_tb.objects.all().filter(id=job_id).update(title=title,description=description,start_date=start_date,end_date=end_date,actual_start_date=actual_start_date,actual_end_date=actual_end_date,branch_id=branch_id,team_leader_id=team_leader_id,client_id=client_id,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-jobs')
        else:
            job_id              = request.GET['id']
            job_data            = job_tb.objects.all().filter(id=job_id)
            branch_list         = branch_tb.objects.all()
            team_leader_list    = team_leader_tb.objects.all()
            client_list         = client_tb.objects.all()
            
            return render(request,'admin/edit_job_data.html',{'branch_list' : branch_list,'team_leader_list' : team_leader_list,'client_list' : client_list,'job_data' : job_data})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteJob(request):
    if request.session.has_key('adminId'):
        job_id          = request.GET['id']
        fromReg         = job_tb.objects.all().filter(id=job_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-jobs')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-jobs')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listStaff(request):
    if request.session.has_key('adminId'):
        staff_list  = staff_tb.objects.all()
        return render(request,'admin/list_staff.html',{'staff_list' : staff_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addStaff(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            name                = request.POST['name']
            email               = request.POST['email']
            phone               = request.POST['phone']
            designation         = request.POST['designation']
            total_hrs           = request.POST['total_hrs']
            required_hrs        = request.POST['required_hrs']
            max_break_time      = request.POST['max_break_time']
            get_shift_id        = request.POST['shift_id']
            shift_id            = shift_tb.objects.get(id=get_shift_id)
            getbranch_id        = request.POST['branch_id']
            branch_id           = branch_tb.objects.get(id=getbranch_id)
            getclient_id        = request.POST['client_id']
            client_id           = client_tb.objects.get(id=getclient_id)
            image_file          = imgForm(request.POST,request.FILES) 
            
            image               = None

            now                 = datetime.now()

            get_staff           = staff_tb.objects.all().filter(email=email)

            if get_staff:
                messages.error(request, 'Email already exist')
                return redirect('add-staff')
            else:
                if image_file.is_valid():
                    image=image_file.cleaned_data['image']

                a               = staff_tb(name=name,email=email,phone=phone,designation=designation,total_hrs=total_hrs,required_hrs=required_hrs,max_break_time=max_break_time,branch_id=branch_id,shift_id=shift_id,client_id=client_id,image=image,created_at=now,updated_at=now)
                a.save()
           
            messages.success(request, 'Successfully added.')
            return redirect('list-staff')
        else:
            branch_list         = branch_tb.objects.all()
            shift_list          = shift_tb.objects.all()
            client_list         = client_tb.objects.all()

            return render(request,'admin/add_staff.html',{'branch_list' : branch_list,'shift_list' : shift_list,'client_list' : client_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateStaff(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            staff_id            = request.GET['id']
            name                = request.POST['name']
            email               = request.POST['email']
            phone               = request.POST['phone']
            designation         = request.POST['designation']
            total_hrs           = request.POST['total_hrs']
            required_hrs        = request.POST['required_hrs']
            max_break_time      = request.POST['max_break_time']
            get_shift_id        = request.POST['shift_id']
            shift_id            = shift_tb.objects.get(id=get_shift_id)
            getbranch_id        = request.POST['branch_id']
            branch_id           = branch_tb.objects.get(id=getbranch_id)
            getclient_id        = request.POST['client_id']
            client_id           = client_tb.objects.get(id=getclient_id)
            image_file          = imgForm(request.POST,request.FILES)

            now                 = datetime.now()
            
            get_staff           = staff_tb.objects.all().filter(email=email).exclude(id=staff_id)

            if get_staff:
                messages.error(request, 'Email already exist')
                return redirect('/edit-staff?id='+ str(staff_id))
            else:
                update_data     = staff_tb.objects.all().filter(id=staff_id).update(name=name,email=email,phone=phone,designation=designation,total_hrs=total_hrs,required_hrs=required_hrs,max_break_time=max_break_time,branch_id=branch_id,shift_id=shift_id,client_id=client_id,updated_at=now)
                if image_file.is_valid():
                    image       = image_file.cleaned_data['image']
                  
                    mymodel = staff_tb.objects.get(id=staff_id)
                    mymodel.image = image
                    mymodel.save()

                messages.success(request, 'Changes successfully updated.')
                return redirect('list-staff')
        else:
            staff_id            = request.GET['id']
            staff_data          = staff_tb.objects.all().filter(id=staff_id)
            branch_list         = branch_tb.objects.all()
            shift_list          = shift_tb.objects.all()
            client_list         = client_tb.objects.all()
            
            return render(request,'admin/edit_staff_data.html',{'branch_list' : branch_list,'shift_list' : shift_list,'client_list' : client_list,'staff_data' : staff_data})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteStaff(request):
    if request.session.has_key('adminId'):
        job_id          = request.GET['id']
        fromReg         = staff_tb.objects.all().filter(id=job_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-staff')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-staff')
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listTask(request):
    if request.session.has_key('adminId'):
        task_list           = task_tb.objects.all()

        now             = datetime.now()

        date1_year  = int(now.strftime("%y"))
        date1_month = int(now.strftime("%m"))
        date1_date  = int(now.strftime("%d"))
        
        all_task        = []
        for task in task_list:
            end_date    = task.end_date
            date2_year  = int(end_date.strftime("%y"))
            date2_month = int(end_date.strftime("%m"))
            date2_date  = int(end_date.strftime("%d"))
            
            d1          = datetime(date1_year,date1_month,date1_date)
            d2          = datetime(date2_year,date2_month,date2_date)

            taskarray                       = {}
            taskarray['id']                 = task.id
            taskarray['task_id']            = task.task_id
            taskarray['title']              = task.title
            taskarray['client_id']          = task.client_id.client_id
            taskarray['job_id']             = task.job_id.title
            taskarray['start_date']         = task.start_date
            taskarray['end_date']           = task.end_date
            taskarray['status']             = task.status
            taskarray['have_request']       = task.have_request
            taskarray['have_delay_request'] = task.have_delay_request
            taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending') else False
            all_task.append(taskarray)

        return render(request,'admin/list_task.html',{'task_list' : all_task})

    elif request.session.has_key('agentId'):
        if request.session.has_key('client_id'):
            agent_id        = request.session['agentId']
            client_id       = request.session['client_id']
            task_list       = task_tb.objects.all().filter(agent_id=agent_id,client_id=client_id)

            now             = datetime.now()

            date1_year  = int(now.strftime("%y"))
            date1_month = int(now.strftime("%m"))
            date1_date  = int(now.strftime("%d"))
            
            all_task        = []
            for task in task_list:
                end_date    = task.end_date
                date2_year  = int(end_date.strftime("%y"))
                date2_month = int(end_date.strftime("%m"))
                date2_date  = int(end_date.strftime("%d"))
                
                d1          = datetime(date1_year,date1_month,date1_date)
                d2          = datetime(date2_year,date2_month,date2_date)

                taskarray                       = {}
                taskarray['id']                 = task.id
                taskarray['task_id']            = task.task_id
                taskarray['title']              = task.title
                taskarray['client_id']          = task.client_id.client_id
                taskarray['job_id']             = task.job_id.title
                taskarray['start_date']         = task.start_date
                taskarray['end_date']           = task.end_date
                taskarray['status']             = task.status
                taskarray['have_request']       = task.have_request
                taskarray['have_delay_request'] = task.have_delay_request
                taskarray['is_expired']     = True if (d2 < d1 and task.status == 'Pending') else False
                all_task.append(taskarray)

            return render(request,'admin/list_task.html',{'task_list' : all_task})
        else:
            messages.error(request, 'Please select client')
            return redirect('agent-dashboard')

    elif request.session.has_key('teamLeadertId'):
        if request.session.has_key('client_id'):
            team_leader_id  = request.session['teamLeadertId']
            client_id       = request.session['client_id']
            task_list       = task_tb.objects.all().filter(team_leader_id=team_leader_id,client_id=client_id)
            
            now             = datetime.now()

            date1_year  = int(now.strftime("%y"))
            date1_month = int(now.strftime("%m"))
            date1_date  = int(now.strftime("%d"))
            
            all_task        = []
            for task in task_list:
                end_date    = task.end_date
                date2_year  = int(end_date.strftime("%y"))
                date2_month = int(end_date.strftime("%m"))
                date2_date  = int(end_date.strftime("%d"))
                
                d1          = datetime(date1_year,date1_month,date1_date)
                d2          = datetime(date2_year,date2_month,date2_date)

                taskarray                       = {}
                taskarray['id']                 = task.id
                taskarray['task_id']            = task.task_id
                taskarray['title']              = task.title
                taskarray['client_id']          = task.client_id.client_id
                taskarray['job_id']             = task.job_id.title
                taskarray['start_date']         = task.start_date
                taskarray['end_date']           = task.end_date
                taskarray['status']             = task.status
                taskarray['have_request']       = task.have_request
                taskarray['have_delay_request'] = task.have_delay_request
                taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending') else False
                all_task.append(taskarray)
            
            return render(request,'admin/list_task.html',{'task_list' : all_task})
        else:
            messages.error(request, 'Please select client')
            return redirect('team-leader-dashboard')

    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewTask(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            title               = request.POST['title']
            description         = request.POST['description']
            start_date          = request.POST['start_date']
            end_date            = request.POST['end_date']
            start_time          = request.POST['start_time']
            end_time            = request.POST['end_time']
            get_job_id          = request.POST['job_id']
            job_id              = job_tb.objects.get(id=get_job_id)
            get_team_leader_id  = request.POST['team_leader_id']
            team_leader_id      = team_leader_tb.objects.get(id=get_team_leader_id)
            get_agent_id        = request.POST['agent_id']
            agent_id            = agent_tb.objects.get(id=get_agent_id)
            required_hrs        = request.POST['required_hrs']
            now                 = datetime.now()

            client_id           = job_tb.objects.all().filter(id=job_id.id).get()
            a                   = task_tb(title=title,description=description,start_date=start_date,end_date=end_date,start_time=start_time,end_time=end_time,job_id=job_id,team_leader_id=team_leader_id,agent_id=agent_id,required_hrs=required_hrs,client_id=client_id.client_id,created_at=now,updated_at=now)
            a.save()

            latest_id           = task_tb.objects.latest('id')
            task_id             = 'TASK' + str(latest_id.id)

            task_tb.objects.all().filter(id=latest_id.id).update(task_id=task_id,updated_at=now)
           
            messages.success(request, 'Successfully added.')
            return redirect('list-task')
        else:
            job_list            = job_tb.objects.all()
            agent_list          = agent_tb.objects.all()
            team_leader_list    = team_leader_tb.objects.all()
            return render(request,'admin/add_task.html',{'job_list' : job_list,'agent_list' : agent_list,'team_leader_list':team_leader_list})
    else:
        return redirect('admin-login')





@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateTask(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            task_id             = request.GET['id']
            title               = request.POST['title']
            description         = request.POST['description']
            start_date          = request.POST['start_date']
            end_date            = request.POST['end_date']
            start_time          = request.POST['start_time']
            end_time            = request.POST['end_time']
            get_job_id          = request.POST['job_id']
            job_id              = job_tb.objects.get(id=get_job_id)
            get_team_leader_id  = request.POST['team_leader_id']
            team_leader_id      = team_leader_tb.objects.get(id=get_team_leader_id)
            get_agent_id        = request.POST['agent_id']
            agent_id            = agent_tb.objects.get(id=get_agent_id)
            required_hrs        = request.POST['required_hrs']
            now                 = datetime.now()

            task_tb.objects.all().filter(id=task_id).update(title=title,description=description,start_date=start_date,end_date=end_date,start_time=start_time,end_time=end_time,job_id=job_id,team_leader_id=team_leader_id,agent_id=agent_id,required_hrs=required_hrs,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-task')
        else:
            task_id             = request.GET['id']
            task_data           = task_tb.objects.all().filter(id=task_id)
            job_list            = job_tb.objects.all()
            agent_list          = agent_tb.objects.all()
            team_leader_list    = team_leader_tb.objects.all()
            
            return render(request,'admin/edit_task_data.html',{'job_list' : job_list,'agent_list' : agent_list,'team_leader_list' : team_leader_list,'task_data' : task_data})
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def viewTask(request):
    if request.session.has_key('agentId'):
        task_id             = request.GET['id']
        task_data           = task_tb.objects.all().filter(id=task_id)
        job_list            = job_tb.objects.all()
        agent_list          = agent_tb.objects.all()
        team_leader_list    = team_leader_tb.objects.all()
        
        return render(request,'user/view_task_data.html',{'job_list' : job_list,'agent_list' : agent_list,'team_leader_list' : team_leader_list,'task_data' : task_data})
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteTask(request):
    if request.session.has_key('adminId'):
        task_id         = request.GET['id']
        fromReg         = task_tb.objects.all().filter(id=task_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-task')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-task')
    else:
        return redirect('admin-login')





# Cancel assigned task
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def revokeTask(request):
    if request.session.has_key('adminId'):
        task_id         = request.GET['id']
        gettask_id      = task_tb.objects.all().filter(id=task_id).values()
        now             = datetime.now()
       
        task_tb.objects.all().filter(id=task_id).update(team_leader_id=None,agent_id=None,updated_at=now)
        
        messages.success(request, gettask_id[0]['task_id']+' ' + 'Cancelled Successfully .')
        return redirect('list-task')
        
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listCustomer(request):
    if request.session.has_key('adminId'):
        customer_list   = customer_tb.objects.all()
        task_id         = request.GET['id']

        return render(request,'admin/list_customer.html',{'customer_list' : customer_list,'task_id' : task_id})

    elif request.session.has_key('teamLeadertId'):
        team_leader_id  = request.session['teamLeadertId']
        customer_list   = customer_tb.objects.all().filter(team_leader_id=team_leader_id)
        task_id         = request.GET['id']
        task_data       = task_tb.objects.all().filter(id=task_id).get()
        
        return render(request,'admin/list_customer.html',{'customer_list' : customer_list,'task_id' : task_id,'submit_tl': task_data.submit_tl})

    elif request.session.has_key('agentId'):
        agent_id        = request.session['agentId']
        customer_list   = customer_tb.objects.all().filter(agent_id=agent_id)
        task_id         = request.GET['id']
        task_data       = task_tb.objects.all().filter(id=task_id).get()

        now             = datetime.now()

        date1_year      = int(now.strftime("%y"))
        date1_month     = int(now.strftime("%m"))
        date1_date      = int(now.strftime("%d"))

        end_date        = task_data.end_date
        date2_year      = int(end_date.strftime("%y"))
        date2_month     = int(end_date.strftime("%m"))
        date2_date      = int(end_date.strftime("%d"))
        
        d1              = datetime(date1_year,date1_month,date1_date)
        d2              = datetime(date2_year,date2_month,date2_date)

        is_expired      = True if d2 < d1 and task_data.status == 'Pending' else False 
        
        return render(request,'admin/list_customer.html',{'customer_list' : customer_list,'task_id' : task_id,'submit_tl': task_data.submit_tl,'is_expired' : is_expired})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewCustomer(request):
    if request.session.has_key('adminId') or request.session.has_key('agentId'):
        if request.method=="POST":
            date                        = request.POST['date']
            opening_time                = request.POST['opening_time']
            closing_time                = request.POST['closing_time']
            customer_id                 = request.POST['customer_id']
            customer_entry_time         = request.POST['customer_entry_time']
            customer_exit_time          = request.POST['customer_exit_time']
            dwell_time                  = request.POST['dwell_time']
            
            is_single                   = request.POST.get('single','')

            single                      = is_single == 'single' and True or False
            group                       = is_single == 'group' and True or False

            sex                         = request.POST.get('sex','')
            male                        = sex == 'is_male' and True or False
            female                      = sex == 'is_female' and True or False


            get_zone_ids                = request.POST.getlist('zone_ids[]')
            zone_ids                    = ','.join(get_zone_ids)
            get_window_zone_ids         = request.POST.getlist('window_zone_ids[]')
            window_zone_ids             = ','.join(get_window_zone_ids)
            get_staff_ids               = request.POST.getlist('staff_ids[]')
            staff_ids                   = ','.join(get_staff_ids)       
            repeat_customer             = request.POST.get('repeat_customer', False)
            repeat_customer_id          = None if not request.POST['repeat_customer_id'] else request.POST['repeat_customer_id']
            repeat_customer_visit_date  = None if not request.POST['repeat_customer_visit_date'] else request.POST['repeat_customer_visit_date']
            tray                        = request.POST.get('tray', False)
            refreshment                 = request.POST.get('refreshment', False)
            gloves                      = request.POST.get('gloves', False)
            backup_stock                = request.POST.get('backup_stock', False)
            business_card               = request.POST.get('business_card', False)
            body_language               = request.POST.get('body_language', False)
            full_uniform                = request.POST.get('full_uniform', False)
            conversion_status           = request.POST.get('conversion_status', False)
            conversion_percentage       = None if not request.POST['conversion_percentage'] else request.POST['conversion_percentage']
            converted_count             = None if not request.POST['converted_count'] else request.POST['converted_count']
            get_conversion_to           = request.POST.get('conversion_to')
            conversion_to               = None if get_conversion_to == None else staff_tb.objects.get(id=get_conversion_to)
            invoice_time                = request.POST['invoice_time']
            reason_for_no_conversion    = request.POST['reason_for_no_conversion']
            remark                      = request.POST['remark']           
            get_task_id                 = request.POST['task_id']
            task_id                     = task_tb.objects.get(id=get_task_id)
            button                      = request.POST['button']
            no_of_male                  = request.POST['no_of_male']
            no_of_female                = request.POST['no_of_female']
            get_time_period             = request.POST['time_period_id']
            time_period_id              = time_period_tb.objects.get(id=get_time_period)

            submit_tl                   = button == 'submit_tl' and True or False

            agent_id                    = task_id.agent_id
            job_id                      = task_id.job_id
            get_job_data                = job_tb.objects.get(id=job_id.id)
            branch_id                   = get_job_data.branch_id
            client_id                   = task_id.client_id
            team_leader_id              = task_id.team_leader_id

            now                         = datetime.now()

            a                           = customer_tb(date=date,opening_time=opening_time,closing_time=closing_time,customer_id=customer_id,customer_entry_time=customer_entry_time,customer_exit_time=customer_exit_time,dwell_time=dwell_time,single=single,group=group,male=male,female=female,zone_ids=zone_ids,window_zone_ids=window_zone_ids,staff_ids=staff_ids,repeat_customer=repeat_customer,repeat_customer_id=repeat_customer_id,repeat_customer_visit_date=repeat_customer_visit_date,tray=tray,refreshment=refreshment,gloves=gloves,backup_stock=backup_stock,business_card=business_card,body_language=body_language,full_uniform=full_uniform,conversion_status=conversion_status,conversion_percentage=conversion_percentage,conversion_to=conversion_to,converted_count=converted_count,invoice_time=invoice_time,reason_for_no_conversion=reason_for_no_conversion,remark=remark,task_id=task_id,agent_id=agent_id,submit_tl=submit_tl,job_id=job_id,branch_id=branch_id,no_of_male=no_of_male,no_of_female=no_of_female,client_id=client_id,time_period_id=time_period_id,team_leader_id=team_leader_id,created_at=now,updated_at=now)
            a.save()
           
            messages.success(request, 'Successfully added.')
            return redirect('/list-customer?id='+ str(task_id.id))
        else:
            zone_list                   = zone_tb.objects.all()
            window_zone_list            = window_zone_tb.objects.all()
            staff_list                  = staff_tb.objects.all()
            time_period                 = time_period_tb.objects.all()
            task_id                     = request.GET['id']
            return render(request,'admin/add_customer.html',{'zone_list' : zone_list,'window_zone_list' : window_zone_list,'staff_list':staff_list,'task_id' :task_id,'time_period':time_period})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateCustomer(request):
    if request.session.has_key('adminId') or request.session.has_key('agentId'):
        if request.method=="POST":
            get_customer_id             = request.POST['id']
            date                        = request.POST['date']
            opening_time                = request.POST['opening_time']
            closing_time                = request.POST['closing_time']
            customer_id                 = request.POST['customer_id']
            customer_entry_time         = request.POST['customer_entry_time']
            customer_exit_time          = request.POST['customer_exit_time']
            dwell_time                  = request.POST['dwell_time']
            
            is_single                   = request.POST.get('single','')
            single                      = is_single == 'single' and True or False
            group                       = is_single == 'group' and True or False

            sex                         = request.POST.get('sex','')
            male                        = sex == 'is_male' and True or False
            female                      = sex == 'is_female' and True or False

            get_zone_ids                = request.POST.getlist('zone_ids[]')
            zone_ids                    = ','.join(get_zone_ids)
            get_window_zone_ids         = request.POST.getlist('window_zone_ids[]')
            window_zone_ids             = ','.join(get_window_zone_ids)
            get_staff_ids               = request.POST.getlist('staff_ids[]')
            staff_ids                   = ','.join(get_staff_ids)       
            repeat_customer             = request.POST.get('repeat_customer', False)
            repeat_customer_id          = None if not request.POST['repeat_customer_id'] else request.POST['repeat_customer_id']
            repeat_customer_visit_date  = None if not request.POST['repeat_customer_visit_date'] else request.POST['repeat_customer_visit_date']
            tray                        = request.POST.get('tray', False)
            refreshment                 = request.POST.get('refreshment', False)
            gloves                      = request.POST.get('gloves', False)
            backup_stock                = request.POST.get('backup_stock', False)
            business_card               = request.POST.get('business_card', False)
            body_language               = request.POST.get('body_language', False)
            full_uniform                = request.POST.get('full_uniform', False)
            conversion_status           = request.POST.get('conversion_status', False)
            conversion_percentage       = None if not request.POST['conversion_percentage'] else request.POST['conversion_percentage']
            converted_count             = None if not request.POST['converted_count'] else request.POST['converted_count']
            get_conversion_to           = request.POST.get('conversion_to')
            conversion_to               = None if get_conversion_to == None else staff_tb.objects.get(id=get_conversion_to)
            invoice_time                = request.POST['invoice_time']
            reason_for_no_conversion    = request.POST['reason_for_no_conversion']
            remark                      = request.POST['remark']           
            get_task_id                 = request.POST['task_id']
            task_id                     = task_tb.objects.get(id=get_task_id)
            button                      = request.POST['button']
            no_of_male                  = request.POST['no_of_male']
            no_of_female                = request.POST['no_of_female']
            submit_tl                   = button == 'submit_tl' and True or False
            get_time_period             = request.POST['time_period_id']
            time_period_id              = time_period_tb.objects.get(id=get_time_period)

            agent_id                    = task_id.agent_id
            job_id                      = task_id.job_id
            get_job_data                = job_tb.objects.get(id=job_id.id)
            branch_id                   = get_job_data.branch_id
            client_id                   = task_id.client_id
            team_leader_id              = task_id.team_leader_id

            now                         = datetime.now()

            customer_tb.objects.all().filter(id=get_customer_id).update(date=date,opening_time=opening_time,closing_time=closing_time,customer_id=customer_id,customer_entry_time=customer_entry_time,customer_exit_time=customer_exit_time,dwell_time=dwell_time,single=single,group=group,male=male,female=female,zone_ids=zone_ids,window_zone_ids=window_zone_ids,staff_ids=staff_ids,repeat_customer=repeat_customer,repeat_customer_id=repeat_customer_id,repeat_customer_visit_date=repeat_customer_visit_date,tray=tray,refreshment=refreshment,gloves=gloves,backup_stock=backup_stock,business_card=business_card,body_language=body_language,full_uniform=full_uniform,conversion_status=conversion_status,conversion_percentage=conversion_percentage,conversion_to=conversion_to,converted_count=converted_count,invoice_time=invoice_time,reason_for_no_conversion=reason_for_no_conversion,remark=remark,task_id=task_id,agent_id=agent_id,submit_tl=submit_tl,job_id=job_id,branch_id=branch_id,no_of_male=no_of_male,no_of_female=no_of_female,client_id=client_id,time_period_id=time_period_id,team_leader_id=team_leader_id,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('/list-customer?id='+ str(task_id.id))
        else:
            customer_id         = request.GET['id']
            customer_data       = customer_tb.objects.all().filter(id=customer_id).get()
            zone_list           = zone_tb.objects.all()
            window_zone_list    = window_zone_tb.objects.all()
            staff_list          = staff_tb.objects.all()
            time_period         = time_period_tb.objects.all()

            task_id             = customer_data.task_id_id
            
            return render(request,'admin/edit_customer_data.html',{'zone_list' : zone_list,'window_zone_list' : window_zone_list,'staff_list':staff_list,'task_id' :task_id,'customer_data' : customer_data,'time_period':time_period})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteCustomer(request):
    if request.session.has_key('adminId'):
        customer_id     = request.GET['id']
        fromReg         = customer_tb.objects.all().filter(id=customer_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-task')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-task')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def taskSubmitToTeamLeader(request):
    if request.session.has_key('agentId'):
        task_id     = request.GET['id']
        now         = datetime.now()
        
        task_tb.objects.all().filter(id=task_id).update(submit_tl=True,status='Complete',updated_at=now)
        messages.success(request, 'Success.')
        return redirect('/list-customer?id='+ str(task_id))
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listStaffAttendance(request):
    if request.session.has_key('adminId'):
        staff_attendance_list       = staff_attendance_tb.objects.all()
        return render(request,'admin/list_staff_attendance.html',{'staff_attendance_list' : staff_attendance_list})
    
    elif request.session.has_key('agentId'):
        if request.session.has_key('client_id'):
            client_id               = request.session['client_id']
            staff_attendance_list   = staff_attendance_tb.objects.all().filter(client_id=client_id)
            return render(request,'admin/list_staff_attendance.html',{'staff_attendance_list' : staff_attendance_list}) 
        else:
            messages.error(request, 'Please select client')
            return redirect('agent-dashboard')  

    elif request.session.has_key('teamLeadertId'):
        if request.session.has_key('client_id'):
            client_id               = request.session['client_id']
            staff_attendance_list   = staff_attendance_tb.objects.all().filter(client_id=client_id)
            return render(request,'admin/list_staff_attendance.html',{'staff_attendance_list' : staff_attendance_list}) 
        else:
            messages.error(request, 'Please select client')
            return redirect('team-leader-dashboard')  

    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addAttendance(request):
    if request.session.has_key('adminId') or request.session.has_key('agentId') or request.session.has_key('teamLeadertId'):
        if request.method=="POST":
            get_staff_id        = request.POST['staff_id']
            staff_id            = staff_tb.objects.get(id=get_staff_id)
            date                = request.POST['date']
            in_time             = request.POST['in_time']
            out_time            = request.POST['out_time']
            break_hours         = request.POST['break_hours']
            work_hours          = request.POST['work_hours']
            over_time           = request.POST['over_time']
            under_time          = request.POST['under_time']

            client_id           = staff_tb.objects.all().filter(id=staff_id.id).get()
            
            now                 = datetime.now()

            a                   = staff_attendance_tb(staff_id=staff_id,date=date,in_time=in_time,out_time=out_time,break_hours=break_hours,work_hours=work_hours,over_time=over_time,under_time=under_time,client_id=client_id.client_id,created_at=now,updated_at=now)
            a.save()
           
            messages.success(request, 'Successfully added.')
            return redirect('list-attendance')
        else:
            staff_list          = staff_tb.objects.all()
            return render(request,'admin/add_attendance.html',{'staff_list' : staff_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteStaffAttendance(request):
    if request.session.has_key('adminId') or request.session.has_key('agentId') or request.session.has_key('teamLeadertId'):
        attendance_id   = request.GET['id']
        fromReg         = staff_attendance_tb.objects.all().filter(id=attendance_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-attendance')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-attendance')
    else:
        return redirect('admin-login')


def getStaffData(request):
    if request.session.has_key('adminId') or request.session.has_key('agentId') or request.session.has_key('teamLeadertId'):

        get_staff_id        = request.GET['staff_id']
        staff_data          = staff_tb.objects.all().filter(id=get_staff_id).values()

        time                = [{'total_work_hour': staff_data[0]['total_hrs'] , 'required_hours' : staff_data[0]['required_hrs']}]
   
        return HttpResponse(json.dumps(time), content_type="application/json")
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def getReport(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId') or request.session.has_key('clientId'):
        if request.method=="POST":
            date_from           = request.POST['date_from']
            date_to             = request.POST['date_to']
            category            = request.POST['category']
            category_type_id    = request.POST.getlist('category_type_id[]')
            selected_type       = request.POST['type']
            get_client_id       = request.POST['client_id']
            client_id           = client_tb.objects.get(id=get_client_id)
            all_clients         = []


            staff_list          = staff_tb.objects.all().filter(client_id=client_id).values()
            branch_list         = branch_tb.objects.all().filter(client_id=client_id).values()
            zone_list           = zone_tb.objects.all().filter(client_id=client_id).values()
            window_zone_list    = window_zone_tb.objects.filter(client_id=client_id).all().values()

            if request.session.has_key('adminId'):
                all_clients     = client_tb.objects.all()
            elif request.session.has_key('teamLeadertId'):
                team_leader_id  = request.session['teamLeadertId']
                get_all_jobs    = job_tb.objects.all().filter(team_leader_id=team_leader_id)
                all_clients     = []
                client_id       = 0
                for job in get_all_jobs:
                    client_data = job.client_id
                    all_clients.append(client_data)
            
            if category == 'time' or category == 'performance':
                category_type_id = ','.join(category_type_id)

            request_data        = [{'date_from' : date_from ,'date_to' : date_to ,'category' :category,'category_type_id' : category_type_id,'selected_type' : selected_type,'client_id' : get_client_id}]

            if category == 'staff':
                get_data_list       = []
                for category in category_type_id:
                    staff_name              = staff_tb.objects.all().filter(id=category).values('name')
                    list_data               = {}
                    
                    get_data                = customer_tb.objects.all().filter(date__range=(date_from, date_to),conversion_to=category).values().order_by('conversion_to')
                    list_data[staff_name[0]['name']]    = get_data
                    get_data_list.append(list_data)

                ################################################################################
                distinct_data       = customer_tb.objects.all().filter(date__range=(date_from, date_to),conversion_to__in=category_type_id).values('conversion_to').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                get_distinct_data   = []
                i                   = 0

                for x in distinct_data:
                    i               = i + 1
                    staff_name      = staff_tb.objects.all().filter(id=x['conversion_to']).values('name')
                    my_dict = {}
                    my_dict['key']              =  i
                    my_dict['staff_id']         =  x['conversion_to']
                    my_dict['name']             =  staff_name[0]['name']
                    my_dict['single']           =  x['single']
                    my_dict['group']            =  x['group']
                    my_dict['total']            =  x['single'] + x['group']
                    my_dict['male']             =  x['male']
                    my_dict['female']           =  x['female']
                    my_dict['converted_count']  =  x['converted_count']
                    my_dict['pct']              =  x['pct']
                    get_distinct_data.append(my_dict)


            elif category == 'branch':
                get_data_list       = []
                for category in category_type_id:
                    branch_name             = branch_tb.objects.all().filter(id=category).values('name')
                    list_data               = {}
                    
                    get_data                = customer_tb.objects.all().filter(date__range=(date_from, date_to),branch_id=category).values().order_by('branch_id')
                    list_data[branch_name[0]['name']]    = get_data
                    get_data_list.append(list_data)

                ################################################################################

                distinct_data   = customer_tb.objects.all().filter(date__range=(date_from, date_to),branch_id__in=category_type_id).values('branch_id').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                get_distinct_data   = []
                i                   = 0
                for x in distinct_data:
                    i               = i + 1
                    branch_name     = branch_tb.objects.all().filter(id=x['branch_id']).values('name')
                    my_dict = {}
                    my_dict['key']              =  i
                    my_dict['staff_id']         =  x['branch_id']
                    my_dict['name']             =  branch_name[0]['name']
                    my_dict['single']           =  x['single']
                    my_dict['group']            =  x['group']
                    my_dict['total']            =  x['single'] + x['group']
                    my_dict['male']             =  x['male']
                    my_dict['female']           =  x['female']
                    my_dict['converted_count']  =  x['converted_count']
                    my_dict['pct']              =  x['pct']
                    get_distinct_data.append(my_dict)
                    
            elif category == 'window_zone':
                all_data            = []
                get_data_list       = []
                for x in category_type_id:
                    zone_id         = x

                    zone                        = window_zone_tb.objects.all().filter(id=zone_id).values('zone')
                    list_data                   = {}
                    
                    get_data                    = customer_tb.objects.all().filter(date__range=(date_from, date_to)).extra(where=['FIND_IN_SET('+x+', window_zone_ids)']).values().order_by()
                    list_data[zone[0]['zone']]  = get_data
                    get_data_list.append(list_data)

                    ################################################################################

                    distinct_data   = customer_tb.objects.all().filter(date__range=(date_from, date_to)).extra(where=['FIND_IN_SET('+x+', window_zone_ids)']).values('window_zone_ids').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                    all_data.append(distinct_data)

                    getdistinct_data   = []
                    i                   = 0

                    for data in all_data:
                        for getData in data:
                            get_ids         = getData['window_zone_ids'].split(',')
                            zone_names      = []
                            zone_ids_list   = []
                            for zoneid in get_ids:
                                zone        = window_zone_tb.objects.all().filter(id=zoneid).values('zone')
                                zone_names.append(zone[0]['zone'])
                                zone_ids_list.append(zoneid)

                            i               = i + 1
                            zone            = window_zone_tb.objects.all().filter(id=zone_id).values('zone')
                            my_dict = {}
                            my_dict['key']              =  i
                            my_dict['ids']              =  ', '.join(zone_ids_list)
                            my_dict['name']             =  ', '.join(zone_names)
                            my_dict['single']           =  getData['single']
                            my_dict['group']            =  getData['group']
                            my_dict['total']            =  getData['single'] + getData['group']
                            my_dict['male']             =  getData['male']
                            my_dict['female']           =  getData['female']
                            my_dict['converted_count']  =  getData['converted_count']
                            my_dict['pct']              =  getData['pct']
                            getdistinct_data.append(my_dict)

                new_list            = []
                get_distinct_data   = []
                for getdata_new in getdistinct_data:
                    if getdata_new['ids'] not in new_list:
                        new_list.append(getdata_new['ids'])
                        get_distinct_data.append(getdata_new)

            elif category == 'zone':
                all_data            = []
                get_data_list       = []
                for x in category_type_id:
                    zone_id                     = x
                    
                    zone                        = zone_tb.objects.all().filter(id=zone_id).values('zone')
                    list_data                   = {}
                    
                    get_data                    = customer_tb.objects.all().filter(date__range=(date_from, date_to)).extra(where=['FIND_IN_SET('+x+', zone_ids)']).values().order_by()

                    list_data[zone[0]['zone']]  = get_data
                    get_data_list.append(list_data)

                    ################################################################################

                    distinct_data   = customer_tb.objects.all().filter(date__range=(date_from, date_to)).extra(where=['FIND_IN_SET('+x+', zone_ids)']).values('zone_ids').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                    all_data.append(distinct_data)

                    getdistinct_data    = []
                    i                   = 0

                    for data in all_data:
                        for getData in data:
                            get_ids         = getData['zone_ids'].split(',')
                            zone_names      = []
                            zone_ids_list   = []
                            for zoneid in get_ids:
                                zone        = zone_tb.objects.all().filter(id=zoneid).values('zone')
                                zone_names.append(zone[0]['zone'])
                                zone_ids_list.append(zoneid)

                            i               = i + 1
                            zone            = zone_tb.objects.all().filter(id=zone_id).values('zone')
                            my_dict = {}
                            my_dict['key']              =  i
                            my_dict['ids']              =  ', '.join(zone_ids_list)
                            my_dict['name']             =  ', '.join(zone_names)
                            my_dict['single']           =  getData['single']
                            my_dict['group']            =  getData['group']
                            my_dict['total']            =  getData['single'] + getData['group']
                            my_dict['male']             =  getData['male']
                            my_dict['female']           =  getData['female']
                            my_dict['converted_count']  =  getData['converted_count']
                            my_dict['pct']              =  getData['pct']
                            getdistinct_data.append(my_dict)

                new_list            = []
                get_distinct_data   = []
                for getdata_new in getdistinct_data:
                    if getdata_new['ids'] not in new_list:
                        new_list.append(getdata_new['ids'])
                        get_distinct_data.append(getdata_new)

            ###################################################################################################

            elif category == 'time':
                if category_type_id == 'branch':
                    get_branch_ids              = branch_tb.objects.all().filter(client_id=client_id)
                    get_time_periods            = time_period_tb.objects.all()

                    time_wise_data              = []
                    for branch in get_branch_ids:
                        time_data               = []
                        for time in get_time_periods:
                            get_branch_data                     = customer_tb.objects.all().filter(date__range=(date_from, date_to),client_id=client_id,branch_id=branch.id,time_period_id=time.id).values('branch_id').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                            time_list_array                     = {}

                            time_list_array['time_period']      = time.period
                            time_list_array['single']           = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single']
                            time_list_array['group']            = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['group']
                            time_list_array['total']            = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['count']
                            time_list_array['male']             = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['male']
                            time_list_array['female']           = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['female']
                            time_list_array['converted_count']  = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['converted_count']
                            time_list_array['pct']              = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['pct']

                            time_data.append(time_list_array)

                        single                  = 0
                        group                   = 0
                        total_count             = 0
                        male                    = 0
                        female                  = 0
                        converted_count         = 0
                        conversion_percentage   = 0
                        total_entry             = len(time_data)
                        for total in time_data:
                            time_period             = 'Total'
                            single                  = single + total['single']
                            group                   = group + total['group']
                            total_count             = total_count +  total['total']
                            male                    = male +  total['male']
                            female                  = female +  total['female']
                            
                            converted_count         =  converted_count + total['converted_count']
                            conversion_percentage   =  conversion_percentage + total['pct']
                            
                        total_pct                   = 0 if total_entry == 0 else round(conversion_percentage / total_entry)
                        data_total_sum              = {'time_period' : time_period,'single' : single,'group' :group,'single' :single,'group':group,'total':total_count,'male':male,'female':female,'converted_count':converted_count,'pct':total_pct}
                        time_data.append(data_total_sum)

                        branch_list_array                       = {}
                        branch_list_array[branch.name]          = time_data
                        time_wise_data.append(branch_list_array)

                elif category_type_id == 'staff':
                    get_staff_ids               = staff_tb.objects.all().filter(client_id=client_id)
                    get_time_periods            = time_period_tb.objects.all()

                    time_wise_data              = []
                    for staff in get_staff_ids:
                        time_data               = []
                        for time in get_time_periods:
                            get_staff_data                      = customer_tb.objects.all().filter(date__range=(date_from, date_to),client_id=client_id,conversion_to=staff.id,time_period_id=time.id).values('conversion_to').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                            time_list_array                     = {}

                            time_list_array['time_period']      = time.period
                            time_list_array['single']           = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['single']
                            time_list_array['group']            = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['group']
                            time_list_array['total']            = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['count']
                            time_list_array['male']             = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['male']
                            time_list_array['female']           = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['female']
                            time_list_array['converted_count']  = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['converted_count']
                            time_list_array['pct']              = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['pct']

                            time_data.append(time_list_array)

                        single                  = 0
                        group                   = 0
                        total_count             = 0
                        male                    = 0
                        female                  = 0
                        converted_count         = 0
                        conversion_percentage   = 0
                        total_entry             = len(time_data)
                        for total in time_data:
                            time_period             = 'Total'
                            single                  = single + total['single']
                            group                   = group + total['group']
                            total_count             = total_count +  total['total']
                            male                    = male +  total['male']
                            female                  = female +  total['female']
                            
                            converted_count         =  converted_count + total['converted_count']
                            conversion_percentage   =  conversion_percentage + total['pct']
                            
                        total_pct                   = 0 if total_entry == 0 else round(conversion_percentage / total_entry)
                        data_total_sum              = {'time_period' : time_period,'single' : single,'group' :group,'single' :single,'group':group,'total':total_count,'male':male,'female':female,'converted_count':converted_count,'pct':total_pct}
                        time_data.append(data_total_sum)

                        staff_list_array                        = {}
                        staff_list_array[staff.name]            = time_data
                        time_wise_data.append(staff_list_array)

                return render(request,'admin/time_wise.html',{'get_data' : time_wise_data,'request_data' : request_data,'staff_list' :staff_list,'branch_list' :branch_list,'zone_list' :zone_list,'window_zone_list':window_zone_list,'clients' :all_clients})
            
            elif category == 'performance':
                if category_type_id == 'branch':
                    get_branch_ids                          = branch_tb.objects.all().filter(client_id=client_id)

                    performance_data                        = []
                    for branch in get_branch_ids:
                        get_branch_data                     = customer_tb.objects.all().filter(date__range=(date_from, date_to),client_id=client_id).values('branch_id').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                       
                        array_data                          = {}
                        array_data['branch']                = branch.name
                        array_data['total']                 = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['count']
                        array_data['converted_count']       = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['converted_count']
                        array_data['pct']                   = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['pct']
                        
                        performance_data.append(array_data)
                        
                elif category_type_id == 'staff':

                    get_staff_ids                           = staff_tb.objects.all().filter(client_id=client_id)
                    get_time_periods                        = time_period_tb.objects.all()

                    performance_data                        = []
                    for staff in get_staff_ids:
                        get_staff_data                      = customer_tb.objects.all().filter(date__range=(date_from, date_to),client_id=client_id,conversion_to=staff.id).values('conversion_to').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                       
                        staff_name                          = staff_tb.objects.all().filter(id=staff.id).get()
                        branch_name                         = branch_tb.objects.all().filter(id=staff_name.branch_id.id).get()
                        array_data                          = {}
                        array_data['name']                  = staff_name.name
                        array_data['branch']                = branch_name.name
                        array_data['total']                 = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['count']
                        array_data['converted_count']       = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['converted_count']
                        array_data['pct']                   = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['pct']
                        performance_data.append(array_data)

                performance_data.sort(key=lambda x: x.get('pct'), reverse=True)

                total_count             = 0
                converted_count         = 0
                conversion_percentage   = 0
                total_entry             = len(performance_data)
                for total in performance_data:
                    total_count             =  total_count + total['total']
                    converted_count         =  converted_count + total['converted_count']
                    conversion_percentage   =  conversion_percentage + total['pct']
                    
                total_pct                   = 0 if total_entry == 0 else round(conversion_percentage / total_entry)
                data_total_sum              = {'total':total_count,'converted_count':converted_count,'pct':total_pct}
                   
                return render(request,'admin/performance_report.html',{'get_data' : performance_data,'data_total_sum':data_total_sum,'request_data' : request_data,'staff_list' :staff_list,'branch_list' :branch_list,'zone_list' :zone_list,'window_zone_list':window_zone_list,'clients' :all_clients})
            ############################################################################################################################################
                        
            get_distinct_data.sort(key=lambda x: x.get('pct'), reverse=True)

            if selected_type == 'consolidated':

                sum_male            = 0
                sum_female          = 0
                total_count         = 0
                sum_single          = 0
                sum_group           = 0
                sum_converted_count = 0
                total_pct           = 0
                total_entry         = len(get_distinct_data)
                
                for total in get_distinct_data:
                    sum_male                = sum_male +  total['male']
                    sum_female              = sum_female +  total['female']
                    total_count             = total_count +  total['total']
                    sum_single              = sum_single + total['single']
                    sum_group               = sum_group + total['group']
                    sum_converted_count     = sum_converted_count + total['converted_count']
                    sum_pct                 = total_pct + total['pct'] 

                total_pct                   = 0 if total_entry == 0 else sum_pct / total_entry
                data_total_sum              = {'sum_male' : sum_male,'sum_female' : sum_female,'total_count' :total_count,'sum_single' :sum_single,'sum_group': sum_group,'sum_converted_count': sum_converted_count,'total_pct':total_pct}
                
                return render(request,'admin/consolidated_report.html',{'get_data' : get_distinct_data,'length_graph' : len(get_distinct_data),'graph_data' :get_distinct_data[:9],'length' :len(get_distinct_data),'request_data' : request_data,'staff_list' :staff_list,'branch_list' :branch_list,'zone_list' :zone_list,'window_zone_list':window_zone_list,'clients' : all_clients,'data_total_sum' : data_total_sum})
            else:
                get_detailed_data_list  = []
                for get_detailed_data in get_data_list:
                    key     = list(get_detailed_data.keys())
                    values  = list(get_detailed_data.values())
                    
                    get_all_data    = []
                    for data in values[0]:
                        staff_name                      = staff_tb.objects.all().filter(id=data['conversion_to_id']).values('name')
                        get_ids                         = data['zone_ids'].split(',')
                        zone_names                      = []
                        for zoneid in get_ids:
                            zone                        = zone_tb.objects.all().filter(id=zoneid).values('zone')
                            zone_names.append(zone[0]['zone'])

                        get_win_ids                     = data['window_zone_ids'].split(',')
                        win_zone_names                  = []
                        for winzoneid in get_win_ids:
                            winzone                     = window_zone_tb.objects.all().filter(id=winzoneid).values('zone')
                            win_zone_names.append(winzone[0]['zone'])

                        my_dict = {}
                        my_dict['date']                 =  data['date']
                        my_dict['customer_entry_time']  =  data['customer_entry_time']
                        my_dict['customer_exit_time']   =  data['customer_exit_time']
                        my_dict['single']               =  (data['single'] == True and 1 or 0)
                        my_dict['group']                =  (data['group'] == True and 1 or 0)
                        my_dict['total']                =  my_dict['single'] + my_dict['group']
                        my_dict['male']                 =  (data['male'] == True and 1 or 0) + data['no_of_male']
                        my_dict['female']               =  (data['female'] == True and 1 or 0) + data['no_of_female']
                        my_dict['staff_name']           =  staff_name[0]['name']
                        my_dict['zone_ids']             =  ', '.join(zone_names)
                        my_dict['window_zone_ids']      =  ', '.join(win_zone_names)
                        my_dict['dwell_time']           =  data['dwell_time']
                        my_dict['tray']                 =  data['tray']
                        my_dict['refreshment']          =  data['refreshment']
                        my_dict['gloves']               =  data['gloves']
                        my_dict['backup_stock']         =  data['backup_stock']
                        my_dict['business_card']        =  data['business_card']
                        my_dict['full_uniform']         =  data['full_uniform']
                        my_dict['conversion_status']    =  data['conversion_status']
                        my_dict['converted_count']      =  data['converted_count']
                        my_dict['conversion_percentage']=  data['conversion_percentage']
                        get_all_data.append(my_dict)

                    male                    = 0
                    female                  = 0
                    total_count             = 0
                    single                  = 0
                    group                   = 0
                    converted_count         = 0
                    conversion_percentage   = 0
                    customer_entry_time     = 'Total'  
                    customer_exit_time      = ''
                    staff_name              = ''
                    zone_ids                = ''
                    window_zone_ids         = ''
                    dwell_time              = ''
                    tray                    = ''
                    refreshment             = ''
                    gloves                  = ''
                    backup_stock            = ''
                    business_card           = ''
                    full_uniform            = ''
                    conversion_status       = ''
                    total_entry             = len(get_all_data)

                    for total in get_all_data:
                        date                    = ''
                        single                  = single + total['single']
                        group                   = group + total['group']
                        total_count             = total_count +  total['total']
                        male                    = male +  total['male']
                        female                  = female +  total['female']
                        
                        converted_count         =  converted_count + total['converted_count']
                        conversion_percentage   =  conversion_percentage + total['conversion_percentage']
                        
                    total_pct                   = 0 if total_entry == 0 else conversion_percentage / total_entry
                    data_total_sum              = {'date' : date,'customer_entry_time' : customer_entry_time,'customer_exit_time' :customer_exit_time,'single' :single,'group':group,'total':total_count,'male':male,'female':female,'staff_name' :staff_name,'zone_ids': zone_ids,'window_zone_ids': window_zone_ids,'dwell_time':dwell_time,'tray' : tray,'refreshment' :refreshment,'gloves':gloves,'backup_stock':backup_stock,'business_card':business_card,'full_uniform' :full_uniform,'conversion_status':conversion_status,'converted_count':converted_count,'conversion_percentage':total_pct}
                    get_all_data.append(data_total_sum)

                    data_list_array             = {}
                    data_list_array[key[0]]     = get_all_data
                    get_detailed_data_list.append(data_list_array) 
              
                return render(request,'admin/detailed_report.html',{'get_data' : get_detailed_data_list,'request_data' : request_data,'staff_list' :staff_list,'branch_list' :branch_list,'zone_list' :zone_list,'window_zone_list':window_zone_list,'clients' :all_clients})
        else:
            all_clients             = []    
            if request.session.has_key('adminId'):
                all_clients          = client_tb.objects.all()

            elif request.session.has_key('teamLeadertId'):
                team_leader_id      = request.session['teamLeadertId']
                get_all_jobs        = job_tb.objects.all().filter(team_leader_id=team_leader_id)
                client_id           = 0

                for job in get_all_jobs:
                    client_data     = job.client_id
                    all_clients.append(client_data)
            
            request_data            = []
            return render(request,'admin/consolidated_report.html',{'request_data' : request_data,'clients':all_clients})

    else:
        return redirect('admin-login')



def getFilterCategory(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId') or request.session.has_key('clientId'):
        get_type        = request.GET['type']
        client_id       = request.GET['client_id']

        if get_type == 'staff':
            get_data    = staff_tb.objects.all().filter(client_id=client_id).values()
        elif get_type == 'branch':
            get_data    = branch_tb.objects.all().filter(client_id=client_id).values()
        elif get_type == 'zone':
            get_data    = zone_tb.objects.all().filter(client_id=client_id).values()
        elif get_type == 'window_zone':
            get_data    = window_zone_tb.objects.filter(client_id=client_id).all().values()

        return  JsonResponse({"models_to_return": list(get_data)})
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def adminLogout(request):
    if request.session.has_key('adminId'):
        del request.session['adminId']
        adminLogout(request)
    return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def userLogin(request):
    if  request.method=='POST':
        email       = request.POST['email']
        password    = request.POST['password']
        user        = request.POST['user']

        if request.session.has_key('adminId'):
            del request.session['adminId']
        if request.session.has_key('teamLeadertId'):
            del request.session['teamLeadertId']

        if user == 'agent':
            agent   = agent_tb.objects.all().filter(email=email)
            if agent:
                for x in agent:
                    if(check_password(password,x.password) == True):
                        request.session['agentId']=x.id
                        return redirect('agent-dashboard')
                    else:
                        return render(request,'user/login.html',{'msg':"Invalid username or password"})
            else:
                return render(request,'user/login.html',{'msg':"Invalid username or password"})
        elif user == 'team_leader':
            tl      = team_leader_tb.objects.all().filter(email=email)
            if tl:
                for x in tl:
                    if(check_password(password,x.password) == True):
                        request.session['teamLeadertId']=x.id
                        return redirect('team-leader-dashboard')
                    else:
                        return render(request,'user/login.html',{'msg':"Invalid username or password"})
            else:
                return render(request,'user/login.html',{'msg':"Invalid username or password"})
    else:
        if  request.session.has_key('agentId'):
            return redirect('agent-dashboard')
        elif request.session.has_key('teamLeadertId'):
            return redirect('team-leader-dashboard')
        else:
            return render(request,'user/login.html')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def agentDashboard(request):
    if request.session.has_key('agentId'):
        agent_id            = request.session['agentId']
        client_id           = 0

        pending_task        = task_tb.objects.all().filter(agent_id=agent_id, status='Pending')

        get_all_clients     = []
        for task in pending_task:
            client_data = task.client_id
            get_all_clients.append(client_data)

        if request.session.has_key('client_id'):
            client_id       = request.session['client_id']
            pending_task    = task_tb.objects.all().filter(agent_id=agent_id,client_id=client_id,status='Pending')  
      
        return render(request,'user/agent_dashboard.html',{'pending_task' : pending_task,'request' : request,'all_clients' : get_all_clients,'client_id' : client_id})
    else:
        return redirect('user-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def teamLeaderDashboard(request):
    if request.session.has_key('teamLeadertId'):
        team_leader_id      = request.session['teamLeadertId']

        active_task         = task_tb.objects.all().filter(team_leader_id=team_leader_id,status='Active').count()
        pending_task        = task_tb.objects.all().filter(team_leader_id=team_leader_id,status='Pending').count()
        complete_task       = task_tb.objects.all().filter(team_leader_id=team_leader_id,status='Complete').count()

        task                = [{'active_task' : active_task,'pending_task' : pending_task,'complete_task' : complete_task}]

        active_jobs         = job_tb.objects.all().filter(team_leader_id=team_leader_id,status='Active').count()
        pending_jobs        = job_tb.objects.all().filter(team_leader_id=team_leader_id,status='Pending').count()
        complete_jobs       = job_tb.objects.all().filter(team_leader_id=team_leader_id,status='Complete').count()

        jobs                = [{'active_jobs' : active_jobs,'pending_jobs' : pending_jobs,'complete_jobs' : complete_jobs}]

        pending_task        = task_tb.objects.all().filter(team_leader_id=team_leader_id,status='Pending')

        get_all_jobs        = job_tb.objects.all().filter(team_leader_id=team_leader_id)
        get_all_clients     = []
        client_id           = 0
        for job in get_all_jobs:
            client_data = job.client_id
            get_all_clients.append(client_data)

        if request.session.has_key('client_id'):
            client_id       = request.session['client_id']
            pending_task    = task_tb.objects.all().filter(team_leader_id=team_leader_id,client_id=client_id,status='Pending')  
        
        return render(request,'user/team_leader_dashboard.html',{'all_task' : task ,'jobs':jobs,'pending_task' : pending_task,'all_clients': get_all_clients,'client_id' :client_id})
    else:
        return redirect('user-login')


def storeClientIdInSession(request):
    client_id   = request.GET['client_id']

    if client_id == 'All':
        del request.session['client_id']
    else:
        request.session['client_id']=client_id

    return HttpResponse(json.dumps(True), content_type="application/json")


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def userLogout(request):
    if request.session.has_key('agentId'):
        del request.session['agentId']
        adminLogout(request)
    if request.session.has_key('teamLeadertId'):
        del request.session['teamLeadertId']
        adminLogout(request)
    return redirect('user-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def clientLogin(request):
    if  request.method=='POST':
        email       = request.POST['email']
        password    = request.POST['password']


        if request.session.has_key('adminId'):
            del request.session['adminId']
        if request.session.has_key('teamLeadertId'):
            del request.session['teamLeadertId']
        if request.session.has_key('agentId'):
            del request.session['agentId']

        
        client      = client_tb.objects.all().filter(email=email)
        if client:
            for x in client:
                if(check_password(password,x.password) == True):
                    request.session['clientId']=x.id
                    return redirect('client-dashboard')
                else:
                    return render(request,'client/login.html',{'msg':"Invalid username or password"})
        else:
            return render(request,'client/login.html',{'msg':"Invalid username or password"})
    else:
        if  request.session.has_key('clientId'):
            return redirect('client-dashboard')
        else:
            return render(request,'client/login.html')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def clientDashboard(request):
    if request.session.has_key('clientId'):
        client_id           = request.session['clientId']

        active_task         = task_tb.objects.all().filter(client_id=client_id,status='Active').count()
        pending_task        = task_tb.objects.all().filter(client_id=client_id,status='Pending').count()
        complete_task       = task_tb.objects.all().filter(client_id=client_id,status='Complete').count()

        task                = [{'active_task' : active_task,'pending_task' : pending_task,'complete_task' : complete_task}]

        active_jobs         = job_tb.objects.all().filter(client_id=client_id,status='Active').count()
        pending_jobs        = job_tb.objects.all().filter(client_id=client_id,status='Pending').count()
        complete_jobs       = job_tb.objects.all().filter(client_id=client_id,status='Complete').count()

        jobs                = [{'active_jobs' : active_jobs,'pending_jobs' : pending_jobs,'complete_jobs' : complete_jobs}]

        pending_task        = task_tb.objects.all().filter(client_id=client_id,status='Pending')
        
        return render(request,'client/client_dashboard.html',{'all_task' : task ,'jobs':jobs,'pending_task' : pending_task})
    else:
        return redirect('user-login')      



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def clientLogout(request):
    if request.session.has_key('clientId'):
        del request.session['clientId']
        adminLogout(request)
    return redirect('client-login')    



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def taskRequest(request):
    if request.session.has_key('agentId'):
        if  request.method=='POST':
            get_task_id     = request.POST['id']
            task_id         = task_tb.objects.get(id=get_task_id)
            remark          = request.POST['remark']

            team_leader_id  = task_id.team_leader_id
            agent_id        = task_id.agent_id
            now             = datetime.now()

            a               = task_request_tb(task_id=task_id,remark=remark,team_leader_id=team_leader_id,agent_id=agent_id,created_at=now,updated_at=now)
            a.save()

            task_tb.objects.all().filter(id=task_id).update(have_request=True,updated_at=now)

            messages.success(request, 'Success.')
            return redirect('list-task')
        else:
            task_id         = request.GET['id']
            return render(request,'user/request_remark.html',{'task_id' : task_id})
    else:
        return redirect('user-login')  




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def changeStatusOfTaskRequest(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        if  request.method=='POST':
            get_task_id     = request.POST['id']
            task_id         = task_tb.objects.get(id=get_task_id)
            get_status      = request.POST['status']
            status          = True if get_status == 'Approve' else False
            
            now             = datetime.now()

            task_request_tb.objects.all().filter(task_id=task_id.id).update(status=status,updated_at=now)
            task_tb.objects.all().filter(id=task_id.id).update(have_request=False,request_status=get_status,updated_at=now)

            messages.success(request, 'Success.')
            return redirect('list-task')
        else:
            task_id             = request.GET['id']
            request_data        = task_request_tb.objects.all().filter(id=task_id)
            agent_list          = agent_tb.objects.all()
            team_leader_list    = team_leader_tb.objects.all()
            return render(request,'admin/approve_task_request.html',{'task_id' : task_id ,'request_data' : request_data,'agent_list' : agent_list,'team_leader_list':team_leader_list})
    else:
        return redirect('user-login') 




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def searchTask(request):
    if  request.method=='POST':
        search_key          = request.POST['search']
        if request.session.has_key('adminId'):
            task_list       = task_tb.objects.all().filter(title__icontains=search_key)

            return render(request,'admin/list_task.html',{'task_list' : task_list,'search_key' : search_key})

        elif request.session.has_key('agentId'):
            if request.session.has_key('client_id'):
                agent_id        = request.session['agentId']
                client_id       = request.session['client_id']
                task_list       = task_tb.objects.all().filter(title__icontains=search_key,agent_id=agent_id,client_id=client_id)
                return render(request,'admin/list_task.html',{'task_list' : task_list,'search_key' :search_key})
            else:
                messages.error(request, 'Please select client')
                return redirect('agent-dashboard')

        elif request.session.has_key('teamLeadertId'):
            if request.session.has_key('client_id'):
                team_leader_id  = request.session['teamLeadertId']
                client_id       = request.session['client_id']
                task_list       = task_tb.objects.all().filter(title__icontains=search_key,team_leader_id=team_leader_id,client_id=client_id)
                return render(request,'admin/list_task.html',{'task_list' : task_list,'search_key' : search_key})
            else:
                messages.error(request, 'Please select client')
                return redirect('team-leader-dashboard')

        else:
            return redirect('admin-login')
    else:
        return redirect('list-task')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def complaintTicket(request):  
    if request.session.has_key('clientId'):
        if  request.method=='POST':
            get_client_id   = request.session['clientId']
            client_id       = client_tb.objects.get(id=get_client_id)
            remark          = request.POST['remark']
            now             = datetime.now()

            get_team_leader = task_tb.objects.filter(client_id=client_id).first()

            a               = complaint_ticket_tb(client_id=client_id,remark=remark,team_leader_id=get_team_leader.team_leader_id,created_at=now,updated_at=now)
            a.save()

            messages.success(request, 'Success.')
            return redirect('client-dashboard')
        else:
            client_id       = request.session['clientId']
            task_list       = task_tb.objects.all().filter(client_id=client_id)
            
            return render(request,'client/complaint_ticket.html',{'client_id' : client_id,'task_list' : task_list})
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listcomplaintTicket(request):  
    if request.session.has_key('adminId'):
        all_complaints      = complaint_ticket_tb.objects.all()
    if request.session.has_key('teamLeadertId'):
        team_leader_id      = request.session['teamLeadertId']
        all_complaints      = complaint_ticket_tb.objects.all().filter(team_leader_id=team_leader_id)

    return render(request,'client/lsit_complaint_ticket.html',{'all_complaints' : all_complaints})



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def editComplaintTicketStatus(request):  
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        if  request.method=='POST':
            complaint_id    = request.POST['id']
            status          = request.POST['status']
            now             = datetime.now()

            complaint_ticket_tb.objects.all().filter(id=complaint_id).update(status=status,updated_at=now)

            messages.success(request, 'Success.')
            return redirect('list-complaint-tickets')
        else:
            complaint_id    = request.GET['id']
            complaint_data  = complaint_ticket_tb.objects.all().filter(id=complaint_id)
            
            return render(request,'client/edit_complaint_ticket.html',{'complaint_data' : complaint_data})
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def delayTaskRequest(request):
    if request.session.has_key('agentId'):
        if  request.method=='POST':
            get_task_id     = request.POST['id']
            task_id         = task_tb.objects.get(id=get_task_id)
            remark          = request.POST['remark']

            team_leader_id  = task_id.team_leader_id
            agent_id        = task_id.agent_id
            client_id       = task_id.client_id
            now             = datetime.now()
            actual_end_date = task_id.end_date

            print(now)
            print(actual_end_date)

            a               = delay_task_request_tb(task_id=task_id,remark=remark,team_leader_id=team_leader_id,agent_id=agent_id,client_id=client_id,actual_end_date=actual_end_date,created_at=now,updated_at=now)
            a.save()

            task_tb.objects.all().filter(id=task_id.id).update(have_delay_request=True,updated_at=now)

            messages.success(request, 'Success.')
            return redirect('list-task')
        else:
            task_id         = request.GET['id']
            return render(request,'user/delay_request_remark.html',{'task_id' : task_id})
    else:
        return redirect('user-login')  


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def changeStatusOfDelayTaskRequest(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        if  request.method=='POST':
            get_task_id     = request.POST['id']
            task_id         = task_tb.objects.get(id=get_task_id)
            get_status      = request.POST['status']
            status          = True if get_status == 'Approve' else False
            new_end_date    = request.POST['new_end_date']
            end_date        = new_end_date if get_status == 'Approve' else task_id.end_date
            
            now             = datetime.now()

            delay_task_request_tb.objects.all().filter(task_id=task_id.id).update(status=status,new_end_date=new_end_date,updated_at=now)
            task_tb.objects.all().filter(id=task_id.id).update(end_date=end_date,have_delay_request=False,request_status=get_status,updated_at=now)

            messages.success(request, 'Success.')
            return redirect('list-task')
        else:
            task_id             = request.GET['id']
            request_data        = delay_task_request_tb.objects.all().filter(task_id=task_id)

            agent_list          = agent_tb.objects.all()
            team_leader_list    = team_leader_tb.objects.all()
            return render(request,'admin/approve_delay_task_request.html',{'task_id' : task_id ,'request_data' : request_data,'agent_list' : agent_list,'team_leader_list':team_leader_list})
    else:
        return redirect('user-login') 



def agentCheckInCheckOut(request): 
    if request.session.has_key('agentId'):
        status          = request.GET['status']
        get_agent_id    = request.session['agentId']
        agent_id        = agent_tb.objects.get(id=get_agent_id)
        date            = datetime.now()
        time            = date.strftime("%H:%M:%S")
        now             = datetime.now()

        a               = agent_checkin_checkout_tb(date=date,time=time,agent_id=agent_id,status=status,created_at=now,updated_at=now)
        a.save()

    return HttpResponse(json.dumps(True), content_type="application/json")




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listAgentAttendace(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        if  request.method=='POST':
            agent_id        = request.POST['id']
            date_from       = request.POST['date_from']
            date_to         = request.POST['date_to']

            request_data    = {'date_from' : date_from,'date_to': date_to}
            attendance_data = agent_checkin_checkout_tb.objects.all().filter(date__range=(date_from, date_to),agent_id=agent_id)
            return render(request,'admin/list_agent_attendance.html',{'attendance_data' : attendance_data,'agent_id' : agent_id,'request_data' :request_data })

        else:
            agent_id        = request.GET['id']
            attendance_data = agent_checkin_checkout_tb.objects.all().filter(agent_id=agent_id).order_by('-id')
            request_data    = {}
            return render(request,'admin/list_agent_attendance.html',{'attendance_data' : attendance_data,'agent_id' : agent_id })
    else:
        return redirect('user-login') 


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listClientMessage(request):
    if request.session.has_key('clientId'):
        client_id                   = request.session['clientId']
        get_team_leader             = task_tb.objects.all().filter(client_id=client_id).values('team_leader_id').distinct()
        get_admin                   = admin_tb.objects.all().get()

        admin_client_last_msg       = message_tb.objects.all().filter(client_id=client_id,admin_id=get_admin.id).last()
        unread_message_count        = message_tb.objects.all().filter(client_id=client_id,admin_id=get_admin.id,sender='Admin',status='Send').count()
        time                        = admin_client_last_msg.time
        print(time)
        d                           = datetime.strptime("10:00", "%H:%M")
        print(d)
        d.datetime("%Y-%m-%d %H:%M %p")
        print(time.strftime("%H:%M %p"))
        print(d)

        list_all_tl                 = [{'id':get_admin.id,'name' : 'Admin','user_role' : 'Admin','message':'' if not admin_client_last_msg.message else admin_client_last_msg.message,'unread':unread_message_count}]

        for team_leader in get_team_leader:
            tl_name                 = team_leader_tb.objects.all().filter(id=team_leader['team_leader_id']).get()
            tl_client_last_msg      = message_tb.objects.all().filter(client_id=client_id,team_leader_id=team_leader['team_leader_id']).last()
            tl_unread_message_count = message_tb.objects.all().filter(client_id=client_id,team_leader_id=team_leader['team_leader_id'],sender='Team Leader',status='Send').count()
           

            tl_array                = {}
            tl_array['id']          = tl_name.id
            tl_array['name']        = tl_name.name
            tl_array['user_role']   = 'Team Leader'
            tl_array['message']     = '' if not tl_client_last_msg else tl_client_last_msg
            tl_array['unread']      = tl_unread_message_count

            list_all_tl.append(tl_array)
      
        return render(request,'client/client_message.html',{'team_leader' : list_all_tl})
    else:
        return redirect('client-login') 