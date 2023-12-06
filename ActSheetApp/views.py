from django.shortcuts import render
from django.views.decorators.cache import cache_control
from .models import admin_tb,branch_tb,shift_tb,zone_tb,window_zone_tb,team_leader_tb,agent_tb,client_tb,job_tb,staff_tb,task_tb,customer_tb,staff_attendance_tb,task_request_tb,time_period_tb,complaint_ticket_tb,delay_task_request_tb,agent_checkin_checkout_tb,message_tb,notification_tb,staff_attendance_break_tb
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime, timedelta
import random
import string
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse, HttpResponseRedirect
import json
from django.http import JsonResponse
from django.db.models import Count
from django.db.models import Sum, IntegerField, Max
from django.db.models import F
from django.db.models.functions import Cast
import numpy as np
from channels.db import database_sync_to_async
from django.contrib.sessions.models import Session
from django.utils import timezone
from .forms import imgForm, imgForm1, csvUpload
import csv
import operator
import itertools
import calendar
import time
import math
from django.http import Http404 
import pytz
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
                request.session['logged_user_name'] = 'Admin'
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
        complete_clients    = client_tb.objects.all().filter(status='Completed').count()

        clients             = [{'active_clients' : active_clients,'pending_clients' : pending_clients,'complete_clients' : complete_clients}]

        active_jobs         = job_tb.objects.all().filter(status='On Going').count()
        pending_jobs        = job_tb.objects.all().filter(status='Pending').count()
        complete_jobs       = job_tb.objects.all().filter(status='Completed').count()

        jobs                = [{'active_jobs' : active_jobs,'pending_jobs' : pending_jobs,'complete_jobs' : complete_jobs}]

        pending_task        = task_tb.objects.all().filter(status='Pending')

   
        sessions    = Session.objects.filter(expire_date__gte=datetime.now(pytz.timezone('Asia/Dubai')))
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
        if request.method=="POST":
            search_key  = request.POST['search']
            branch_list = branch_tb.objects.all().filter(name__icontains=search_key)

            return render(request,'admin/list_branch.html',{'branch_list' : branch_list,'search_key':search_key})
        else:
            branch_list = branch_tb.objects.all().order_by('-id')
            return render(request,'admin/list_branch.html',{'branch_list' : branch_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewBranch(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            name            = request.POST['name']
            email           = request.POST['email']
            cc              = request.POST['cc']
            getclient_id    = request.POST['client_id']
            client_id       = client_tb.objects.get(id=getclient_id)
            image_file      = imgForm(request.POST,request.FILES)
            image_file1     = imgForm1(request.POST,request.FILES)
            now             = datetime.now(pytz.timezone('Asia/Dubai'))
            image           = None
            image1          = None

            get_branch     = branch_tb.objects.all().filter(email=email)

            if get_branch:
                messages.error(request, 'Email already exist')
                return redirect('add-branch')
            else:
                if image_file.is_valid():
                    image       = image_file.cleaned_data['image']
                if image_file1.is_valid():
                    image1      = image_file1.cleaned_data['image1']

                a               = branch_tb(name=name,email=email,client_id=client_id,layout=image,document=image1,cc=cc,created_at=now,updated_at=now)
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
            email               = request.POST['email']
            cc                  = request.POST['cc']
            getclient_id        = request.POST['client_id']
            client_id           = client_tb.objects.get(id=getclient_id)
            now                 = datetime.now(pytz.timezone('Asia/Dubai'))
            image_file          = imgForm(request.POST,request.FILES)
            image_file1         = imgForm1(request.POST,request.FILES)

            get_branch          = branch_tb.objects.all().filter(email=email).exclude(id=branch_id)

            if get_branch:
                messages.error(request, 'Email already exist')
                return redirect('/edit-branch?id='+ str(branch_id))
            else:
                branch_tb.objects.all().filter(id=branch_id).update(name=name,email=email,client_id=client_id,cc=cc,updated_at=now)

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
        shift_list  = shift_tb.objects.all().order_by('-id')
        return render(request,'admin/list_all_shift.html',{'shift_list' : shift_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewShift(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            from_time   = request.POST['from']
            to_time     = request.POST['to']
            now         = datetime.now(pytz.timezone('Asia/Dubai'))
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
            now         = datetime.now(pytz.timezone('Asia/Dubai'))

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
        if request.method=="POST":
            search_key  = request.POST['search']
            zone_list   = zone_tb.objects.all().filter(zone__icontains=search_key)

            return render(request,'admin/list_zones.html',{'zone_list' : zone_list,'search_key':search_key})
        else:
            zone_list   = zone_tb.objects.all().order_by('-id')
            return render(request,'admin/list_zones.html',{'zone_list' : zone_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewZone(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            zone_list       = request.POST.getlist('zone[]')
            
            getbranch_id    = request.POST.getlist('branch_id[]')
            
            for zone in zone_list:
                for branch in getbranch_id: 
                    branch_id       = branch_tb.objects.get(id=branch)
                    now             = datetime.now(pytz.timezone('Asia/Dubai'))
                    
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
            now             = datetime.now(pytz.timezone('Asia/Dubai'))
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
        if request.method=="POST":
            search_key  = request.POST['search']
            zone_list   = window_zone_tb.objects.all().filter(zone__icontains=search_key)

            return render(request,'admin/list_window_zones.html',{'zone_list' : zone_list,'search_key':search_key})
        else:
            zone_list   = window_zone_tb.objects.all().order_by('-id')
            return render(request,'admin/list_window_zones.html',{'zone_list' : zone_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewWindowZone(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            zone_list       = request.POST.getlist('zone[]')

            getbranch_id    = request.POST.getlist('branch_id[]')
            for zone in zone_list:
                for branch in getbranch_id: 
                    branch_id       = branch_tb.objects.get(id=branch)
                    
                    now             = datetime.now(pytz.timezone('Asia/Dubai'))
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
            now             = datetime.now(pytz.timezone('Asia/Dubai'))
            getbranch_id    = request.POST['branch_id']
            branch_id       = branch_tb.objects.get(id=getbranch_id)
            branch_data     = branch_tb.objects.all().filter(id=branch_id.id).get()
            client_id       = client_tb.objects.get(id=branch_data.client_id.id)

            window_zone_tb.objects.all().filter(id=zone_id).update(zone=zone,client_id=client_id,updated_at=now,branch_id=branch_id)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-window-zones')
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
            return redirect('list-window-zones')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-window-zones')
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listTeamLeader(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            search_key          = request.POST['search']
            team_leader_list    = team_leader_tb.objects.all().filter(name__icontains=search_key)

            return render(request,'admin/list_team_leader.html',{'team_leader_list' : team_leader_list,'search_key':search_key})
        else:
            team_leader_list    = team_leader_tb.objects.all().order_by('-id')
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
            auto_password   = request.POST.get('auto_password')
            password        = request.POST.get('password')

            get_tl          = team_leader_tb.objects.all().filter(email=email)

            if get_tl:
                messages.error(request, 'Email already exist')
                return redirect('add-team-leader')
            else:
                # Auto generated password
                if auto_password:
                    lettersLw       = string.ascii_lowercase
                    lettersUp       = string.ascii_uppercase
                    digits          = '1234567890'
                    password        = ''.join(random.choice(digits + lettersLw + lettersUp) for i in range(10))
                    sendEmail(email,'email/password.html',password)
                else:
                    password        = password

                # password hashchecked
                hash_password   = make_password(password)

                now             = datetime.now(pytz.timezone('Asia/Dubai'))
                a               = team_leader_tb(name=name,email=email,phone=phone,password=hash_password,created_at=now,updated_at=now)
                a.save()

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


def completeJobSendEmail(email,template,list_data):
    html_template   = template
    html_message    = render_to_string(html_template,  {'list_data': list_data})
    subject         = 'Welcome to ActSheet'
    email_from      = settings.EMAIL_HOST_USER
    recipient_list  = [email]
    message         = EmailMessage(subject, html_message, email_from, recipient_list)
    message.content_subtype = 'html'
    message.send()
    return




def branchWiseSendEmail(email,template,list_data,cc_list):
    html_template   = template
    html_message    = render_to_string(html_template,  {'list_data': list_data})
    subject         = 'Welcome to ActSheet'
    email_from      = settings.EMAIL_HOST_USER
    recipient_list  = [email]
    message         = EmailMessage(subject, html_message, email_from, recipient_list,[r for r in cc_list])
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
            now             = datetime.now(pytz.timezone('Asia/Dubai'))

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
        if request.method=="POST":
            search_key  = request.POST['search']
            agent_list  = agent_tb.objects.all().filter(name__icontains=search_key)

            return render(request,'admin/list_agent.html',{'agent_list' : agent_list,'search_key':search_key})
        else:
            agent_list  = agent_tb.objects.all().order_by('-id')
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
            auto_password       = request.POST.get('auto_password')
            password            = request.POST.get('password')

            
            get_agent           = agent_tb.objects.all().filter(email=email)

            if get_agent:
                messages.error(request, 'Email already exist')
                return redirect('add-agent')
            else:
                # Auto generated password
                if auto_password:
                    lettersLw           = string.ascii_lowercase
                    lettersUp           = string.ascii_uppercase
                    digits              = '1234567890'
                    password            = ''.join(random.choice(digits + lettersLw + lettersUp) for i in range(10))
                    sendEmail(email,'email/password.html',password)
                else:
                    password            = password

                # password hashchecked
                hash_password       = make_password(password)

                now                 = datetime.now(pytz.timezone('Asia/Dubai'))
                a                   = agent_tb(name=name,email=email,phone=phone,password=hash_password,team_leader_id=team_leader_id,total_hrs=total_hrs,required_hrs=required_hrs,max_break_time=max_break_time,created_at=now,updated_at=now)
                a.save()

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
            now                 = datetime.now(pytz.timezone('Asia/Dubai'))
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
        if request.method=="POST":
            search_key  = request.POST['search']
            client_list = client_tb.objects.all().filter(name__icontains=search_key)

            return render(request,'admin/list_client.html',{'client_list' : client_list,'search_key':search_key})
        else:
            client_list = client_tb.objects.all().order_by('-id')
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
            business            = request.POST['business']
            auto_password       = request.POST.get('auto_password')
            password            = request.POST.get('password')
            image_file          = imgForm(request.POST,request.FILES)
            image               = None

            get_client          = client_tb.objects.all().filter(email=email)

            if get_client:
                messages.error(request, 'Email already exist')
                return redirect('add-client')
            else:
                # Auto generated password
                if auto_password:
                    lettersLw           = string.ascii_lowercase
                    lettersUp           = string.ascii_uppercase
                    digits              = '1234567890'
                    password            = ''.join(random.choice(digits + lettersLw + lettersUp) for i in range(10))
                    sendEmail(email,'email/password.html',password)
                else:
                    password            = password

                # password hashchecked
                hash_password           = make_password(password)

                now                     = datetime.now(pytz.timezone('Asia/Dubai'))

                if image_file.is_valid():
                    image               = image_file.cleaned_data['image']

                a                       = client_tb(name=name,email=email,phone=phone,password=hash_password,business=business,logo=image,created_at=now,updated_at=now)
                a.save()

                latest_id               = client_tb.objects.latest('id')
                client_id               = 'CLI' + str(latest_id.id)

                client_tb.objects.all().filter(id=latest_id.id).update(client_id=client_id,updated_at=now)

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
            status          = request.POST['status']
            image_file      = imgForm(request.POST,request.FILES)
            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            get_client      = client_tb.objects.all().filter(email=email).exclude(id=client_id)

            if get_client:
                messages.error(request, 'Email already exist')
                return redirect('/edit-client?id='+ str(client_id))
            else:
                if image_file.is_valid():
                    image           = image_file.cleaned_data['image']
                    mymodel         = client_tb.objects.get(id=client_id)
                    mymodel.logo    = image
                    mymodel.save()

                client_tb.objects.all().filter(id=client_id).update(name=name,email=email,phone=phone,business=business,status=status,updated_at=now)

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
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        if request.session.has_key('adminId'):
            job_list        = job_tb.objects.all().order_by('-id')
            client_list     = client_tb.objects.all()

        elif request.session.has_key('teamLeadertId'):
            if request.session.has_key('client_id'):
                team_leader_id      = request.session['teamLeadertId']
                client_id           = request.session['client_id']

                get_all_clients     = job_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
                client_list         = []

                for get_client_id in get_all_clients:
                    client_array= client_tb.objects.all().filter(id=get_client_id['client_id']).get()
                    client_list.append(client_array)

                job_list            = job_tb.objects.all().filter(team_leader_id=team_leader_id,client_id=client_id).order_by('-id')
            else:
                messages.error(request, 'Please select client')
                return redirect('team-leader-dashboard')

        all_jobs        = []
        for job in job_list:
            get_all_task_under_job          = task_tb.objects.all().filter(job_id=job.id).values()
            get_all_task_status_approved    = task_tb.objects.all().filter(job_id=job.id,status="Approved").values()

            complete_job                    = False
            if(get_all_task_under_job):
                if(len(get_all_task_under_job) == len(get_all_task_status_approved)):
                    complete_job            = True


            job_array                       = {}
            job_array['id']                 = job.id
            job_array['job_id']             = job.job_id
            job_array['client_id']          = job.client_id
            job_array['title']              = job.title
            job_array['team_leader_id']     = job.team_leader_id
            job_array['start_date']         = job.start_date
            job_array['end_date']           = job.end_date
            job_array['status']             = job.status
            job_array['complete_job']       = complete_job
            all_jobs.append(job_array)

        return render(request,'admin/list_job.html',{'job_list' : all_jobs,'client_list':client_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def searchJob(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        search_key          = request.POST['search']
        if request.session.has_key('adminId'):
            job_list        = job_tb.objects.all().filter(title__icontains=search_key)
            client_list     = client_tb.objects.all()

        elif request.session.has_key('teamLeadertId'):
            if request.session.has_key('client_id'):
                team_leader_id      = request.session['teamLeadertId']
                client_id           = request.session['client_id']

                get_all_clients     = job_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
                client_list         = []
                for get_client_id in get_all_clients:
                    client_array= client_tb.objects.all().filter(id=get_client_id['client_id']).get()
                    client_list.append(client_array)

                job_list            = job_tb.objects.all().filter(title__icontains=search_key,team_leader_id=team_leader_id,client_id=client_id)

            else:
                messages.error(request, 'Please select client')
                return redirect('team-leader-dashboard')
            
        all_jobs        = []
        for job in job_list:
            get_all_task_under_job          = task_tb.objects.all().filter(job_id=job.id).values()
            get_all_task_status_approved    = task_tb.objects.all().filter(job_id=job.id,status="Approved").values()

            complete_job                    = False
            if(get_all_task_under_job):
                if(len(get_all_task_under_job) == len(get_all_task_status_approved)):
                    complete_job            = True


            job_array                       = {}
            job_array['id']                 = job.id
            job_array['job_id']             = job.job_id
            job_array['client_id']          = job.client_id
            job_array['title']              = job.title
            job_array['team_leader_id']     = job.team_leader_id
            job_array['start_date']         = job.start_date
            job_array['end_date']           = job.end_date
            job_array['status']             = job.status
            job_array['complete_job']       = complete_job
            all_jobs.append(job_array)

        return render(request,'admin/list_job.html',{'job_list' : all_jobs,'client_list':client_list,'search_key':search_key})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def jobFilterByClient(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        client_id           = request.POST['client_id']
        date_from           = request.POST['date_from']
        date_to             = request.POST['date_to']
        
        if request.session.has_key('adminId'):
            job_list        = job_tb.objects.all().filter(start_date__range=(date_from, date_to),client_id=client_id)
            client_list     = client_tb.objects.all()

        elif request.session.has_key('teamLeadertId'):
            if request.session.has_key('client_id'):
                team_leader_id      = request.session['teamLeadertId']

                get_all_clients     = job_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
                client_list         = []
                for get_client_id in get_all_clients:
                    client_array= client_tb.objects.all().filter(id=get_client_id['client_id']).get()
                    client_list.append(client_array)

                job_list            = job_tb.objects.all().filter(start_date__range=(date_from, date_to),team_leader_id=team_leader_id,client_id=client_id)

            else:
                messages.error(request, 'Please select client')
                return redirect('team-leader-dashboard')


        all_jobs        = []
        for job in job_list:
            get_all_task_under_job          = task_tb.objects.all().filter(job_id=job.id).values()
            get_all_task_status_approved    = task_tb.objects.all().filter(job_id=job.id,status="Approved").values()

            complete_job                    = False
            if(get_all_task_under_job):
                if(len(get_all_task_under_job) == len(get_all_task_status_approved)):
                    complete_job            = True


            job_array                       = {}
            job_array['id']                 = job.id
            job_array['job_id']             = job.job_id
            job_array['client_id']          = job.client_id
            job_array['title']              = job.title
            job_array['team_leader_id']     = job.team_leader_id
            job_array['start_date']         = job.start_date
            job_array['end_date']           = job.end_date
            job_array['status']             = job.status
            job_array['complete_job']       = complete_job
            all_jobs.append(job_array)

        return render(request,'admin/list_job.html',{'job_list' : all_jobs,'client_list':client_list,'date_from':date_from,'date_to':date_to,'client_id':client_id})      
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
            get_team_leader_id  = request.POST['team_leader_id']
            team_leader_id      = team_leader_tb.objects.get(id=get_team_leader_id)
            getclient_id        = request.POST['client_id']
            client_id           = client_tb.objects.get(id=getclient_id)
            now                 = datetime.now(pytz.timezone('Asia/Dubai'))

            a                   = job_tb(title=title,description=description,start_date=start_date,end_date=end_date,team_leader_id=team_leader_id,client_id=client_id,created_at=now,updated_at=now)
            a.save()

            latest_id           = job_tb.objects.latest('id')
            job_id              = 'JOB' + str(latest_id.id)

            job_tb.objects.all().filter(id=latest_id.id).update(job_id=job_id,updated_at=now)
           
            messages.success(request, 'Successfully added.')
            return redirect('list-jobs')
        else:
            team_leader_list    = team_leader_tb.objects.all()
            client_list         = client_tb.objects.all()
            return render(request,'admin/add_job.html',{'team_leader_list' : team_leader_list,'client_list' : client_list})
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
            get_team_leader_id  = request.POST['team_leader_id']
            team_leader_id      = team_leader_tb.objects.get(id=get_team_leader_id)
            getclient_id        = request.POST['client_id']
            client_id           = client_tb.objects.get(id=getclient_id)
            now                 = datetime.now(pytz.timezone('Asia/Dubai'))

            job_tb.objects.all().filter(id=job_id).update(title=title,description=description,start_date=start_date,end_date=end_date,team_leader_id=team_leader_id,client_id=client_id,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-jobs')
        else:
            job_id              = request.GET['id']
            job_data            = job_tb.objects.all().filter(id=job_id)
            team_leader_list    = team_leader_tb.objects.all()
            client_list         = client_tb.objects.all()
            
            return render(request,'admin/edit_job_data.html',{'team_leader_list' : team_leader_list,'client_list' : client_list,'job_data' : job_data})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def viewJobData(request):
    if request.session.has_key('teamLeadertId'):
        job_id              = request.GET['id']
        job_data            = job_tb.objects.all().filter(id=job_id)
        team_leader_list    = team_leader_tb.objects.all()
        client_list         = client_tb.objects.all()
        
        return render(request,'admin/view_job_data.html',{'team_leader_list' : team_leader_list,'client_list' : client_list,'job_data' : job_data})    
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
        if request.method=="POST":
            search_key  = request.POST['search']
            staff_list  = staff_tb.objects.all().filter(name__icontains=search_key)

            return render(request,'admin/list_staff.html',{'staff_list' : staff_list,'search_key':search_key})
        else:
            staff_list  = staff_tb.objects.all().order_by('-id')
            return render(request,'admin/list_staff.html',{'staff_list' : staff_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addStaff(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            name                = request.POST['name'].capitalize()
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

            now                 = datetime.now(pytz.timezone('Asia/Dubai'))

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
            name                = request.POST['name'].capitalize()
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

           
            now                 = datetime.now(pytz.timezone('Asia/Dubai'))
            
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

            for staff in staff_data:
                branch_list     = branch_tb.objects.all().filter(client_id=staff.client_id)

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
        task_list           = task_tb.objects.all().exclude(status='Approved').order_by('-id')
        client_list         = client_tb.objects.all()

        now                 = datetime.now(pytz.timezone('Asia/Dubai'))

        date1_year          = int(now.strftime("%y"))
        date1_month         = int(now.strftime("%m"))
        date1_date          = int(now.strftime("%d"))
        
        all_task    = []
        for task in task_list:
            submitted_date      = None

            if task.status == 'Submitted' or task.status == 'Approved':
                submitted_date  = customer_tb.objects.all().filter(task_id=task.id).aggregate(Max('created_at'))
                
            end_date    = task.end_date
            date2_year  = int(end_date.strftime("%y"))
            date2_month = int(end_date.strftime("%m"))
            date2_date  = int(end_date.strftime("%d"))
            
            d1          = datetime(date1_year,date1_month,date1_date)
            d2          = datetime(date2_year,date2_month,date2_date)

            start_time  = task.start_time
            end_time    = task.start_time
            now_time    = now.strftime("%H:%m")

            taskarray                       = {}
            taskarray['id']                 = task.id
            taskarray['task_id']            = task.task_id
            taskarray['title']              = task.title
            taskarray['client_id']          = task.client_id
            taskarray['branch_id']          = task.branch_id
            taskarray['job_id']             = task.job_id
            taskarray['start_date']         = task.start_date
            taskarray['end_date']           = task.end_date
            taskarray['end_time']           = task.end_time
            taskarray['status']             = task.status
            taskarray['have_request']       = task.have_request
            taskarray['have_delay_request'] = task.have_delay_request
            taskarray['approved_time']      = task.approved_time
            taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
            taskarray['submitted_date']     = None if not submitted_date else submitted_date['created_at__max']
            taskarray['time_out']           = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False

            all_task.append(taskarray)

        return render(request,'admin/list_task.html',{'task_list' : all_task,'client_list':client_list})

    elif request.session.has_key('agentId'):
        if request.session.has_key('client_id'):
            agent_id        = request.session['agentId']
            client_id       = request.session['client_id']
            task_list       = task_tb.objects.all().filter(agent_id=agent_id,client_id=client_id).exclude(status='Approved').order_by('-id')

            get_all_clients = task_tb.objects.all().filter(agent_id=agent_id).values('client_id').distinct()
            client_list     = []
            for client_id in get_all_clients:
                client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                client_list.append(client_array)

            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            date1_year  = int(now.strftime("%y"))
            date1_month = int(now.strftime("%m"))
            date1_date  = int(now.strftime("%d"))
            
            all_task        = []
            for task in task_list:
                submitted_date      = None

                if task.status == 'Submitted' or task.status == 'Approved':
                    submitted_date  = customer_tb.objects.all().filter(task_id=task.id).aggregate(Max('created_at'))

                end_date    = task.end_date
                date2_year  = int(end_date.strftime("%y"))
                date2_month = int(end_date.strftime("%m"))
                date2_date  = int(end_date.strftime("%d"))
                
                d1          = datetime(date1_year,date1_month,date1_date)
                d2          = datetime(date2_year,date2_month,date2_date)

                start_time  = task.start_time
                end_time    = task.start_time
                now_time    = now.strftime("%H:%m")

                taskarray                       = {}
                taskarray['id']                 = task.id
                taskarray['task_id']            = task.task_id
                taskarray['title']              = task.title
                taskarray['client_id']          = task.client_id
                taskarray['branch_id']          = task.branch_id
                taskarray['job_id']             = task.job_id
                taskarray['start_date']         = task.start_date
                taskarray['end_date']           = task.end_date
                taskarray['end_time']           = task.end_time
                taskarray['status']             = task.status
                taskarray['have_request']       = task.have_request
                taskarray['have_delay_request'] = task.have_delay_request
                taskarray['approved_time']      = task.approved_time
                taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
                taskarray['submitted_date']     = None if not submitted_date else submitted_date['created_at__max']
                taskarray['time_out']           = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False    
                all_task.append(taskarray)

            return render(request,'admin/list_task.html',{'task_list' : all_task,'client_list': client_list})
        else:
            messages.error(request, 'Please select client')
            return redirect('agent-dashboard')

    elif request.session.has_key('teamLeadertId'):
        if request.session.has_key('client_id'):
            team_leader_id  = request.session['teamLeadertId']
            client_id       = request.session['client_id']
            task_list       = task_tb.objects.all().filter(team_leader_id=team_leader_id,client_id=client_id).exclude(status='Approved').order_by('-id')
            
            get_all_clients = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
            client_list     = []
            for client_id in get_all_clients:
                client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                client_list.append(client_array)

            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            date1_year  = int(now.strftime("%y"))
            date1_month = int(now.strftime("%m"))
            date1_date  = int(now.strftime("%d"))
            
            all_task        = []
            for task in task_list:
                submitted_date      = None

                if task.status == 'Submitted' or task.status == 'Approved':
                    submitted_date  = customer_tb.objects.all().filter(task_id=task.id).aggregate(Max('created_at'))

                end_date    = task.end_date
                date2_year  = int(end_date.strftime("%y"))
                date2_month = int(end_date.strftime("%m"))
                date2_date  = int(end_date.strftime("%d"))
                
                d1          = datetime(date1_year,date1_month,date1_date)
                d2          = datetime(date2_year,date2_month,date2_date)

                start_time  = task.start_time
                end_time    = task.start_time
                now_time    = now.strftime("%H:%m")

                taskarray                       = {}
                taskarray['id']                 = task.id
                taskarray['task_id']            = task.task_id
                taskarray['title']              = task.title
                taskarray['client_id']          = task.client_id
                taskarray['branch_id']          = task.branch_id
                taskarray['job_id']             = task.job_id
                taskarray['start_date']         = task.start_date
                taskarray['end_date']           = task.end_date
                taskarray['end_time']           = task.end_time
                taskarray['status']             = task.status
                taskarray['have_request']       = task.have_request
                taskarray['have_delay_request'] = task.have_delay_request
                taskarray['approved_time']      = task.approved_time
                taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
                taskarray['submitted_date']     = None if not submitted_date else submitted_date['created_at__max']
                taskarray['time_out']           = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False    
                all_task.append(taskarray)
            
            return render(request,'admin/list_task.html',{'task_list' : all_task,'client_list': client_list})
        else:
            messages.error(request, 'Please select client')
            return redirect('team-leader-dashboard')

    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listApprovedTask(request):
    if request.session.has_key('adminId'):
        task_list           = task_tb.objects.all().filter(status='Approved').order_by('-id')
        client_list         = client_tb.objects.all()

        now                 = datetime.now(pytz.timezone('Asia/Dubai'))

        date1_year          = int(now.strftime("%y"))
        date1_month         = int(now.strftime("%m"))
        date1_date          = int(now.strftime("%d"))
        
        all_task    = []
        for task in task_list:
            submitted_date      = None

            if task.status == 'Submitted' or task.status == 'Approved':
                submitted_date  = customer_tb.objects.all().filter(task_id=task.id).aggregate(Max('created_at'))
                
            end_date    = task.end_date
            date2_year  = int(end_date.strftime("%y"))
            date2_month = int(end_date.strftime("%m"))
            date2_date  = int(end_date.strftime("%d"))
            
            d1          = datetime(date1_year,date1_month,date1_date)
            d2          = datetime(date2_year,date2_month,date2_date)

            start_time  = task.start_time
            end_time    = task.start_time
            now_time    = now.strftime("%H:%m")

            taskarray                       = {}
            taskarray['id']                 = task.id
            taskarray['task_id']            = task.task_id
            taskarray['title']              = task.title
            taskarray['client_id']          = task.client_id
            taskarray['branch_id']          = task.branch_id
            taskarray['job_id']             = task.job_id
            taskarray['start_date']         = task.start_date
            taskarray['end_date']           = task.end_date
            taskarray['end_time']           = task.end_time
            taskarray['status']             = task.status
            taskarray['have_request']       = task.have_request
            taskarray['have_delay_request'] = task.have_delay_request
            taskarray['approved_time']      = task.approved_time
            taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
            taskarray['submitted_date']     = None if not submitted_date else submitted_date['created_at__max']
            taskarray['time_out']           = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False

            all_task.append(taskarray)

        return render(request,'admin/list_approved_task.html',{'task_list' : all_task,'client_list':client_list})

    elif request.session.has_key('agentId'):
        if request.session.has_key('client_id'):
            agent_id        = request.session['agentId']
            client_id       = request.session['client_id']
            task_list       = task_tb.objects.all().filter(agent_id=agent_id,client_id=client_id,status='Approved').order_by('-id')

            get_all_clients = task_tb.objects.all().filter(agent_id=agent_id).values('client_id').distinct()
            client_list     = []
            for client_id in get_all_clients:
                client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                client_list.append(client_array)

            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            date1_year  = int(now.strftime("%y"))
            date1_month = int(now.strftime("%m"))
            date1_date  = int(now.strftime("%d"))
            
            all_task        = []
            for task in task_list:
                submitted_date      = None

                if task.status == 'Submitted' or task.status == 'Approved':
                    submitted_date  = customer_tb.objects.all().filter(task_id=task.id).aggregate(Max('created_at'))

                end_date    = task.end_date
                date2_year  = int(end_date.strftime("%y"))
                date2_month = int(end_date.strftime("%m"))
                date2_date  = int(end_date.strftime("%d"))
                
                d1          = datetime(date1_year,date1_month,date1_date)
                d2          = datetime(date2_year,date2_month,date2_date)

                start_time  = task.start_time
                end_time    = task.start_time
                now_time    = now.strftime("%H:%m")

                taskarray                       = {}
                taskarray['id']                 = task.id
                taskarray['task_id']            = task.task_id
                taskarray['title']              = task.title
                taskarray['client_id']          = task.client_id
                taskarray['branch_id']          = task.branch_id
                taskarray['job_id']             = task.job_id
                taskarray['start_date']         = task.start_date
                taskarray['end_date']           = task.end_date
                taskarray['end_time']           = task.end_time
                taskarray['status']             = task.status
                taskarray['have_request']       = task.have_request
                taskarray['have_delay_request'] = task.have_delay_request
                taskarray['approved_time']      = task.approved_time
                taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
                taskarray['submitted_date']     = None if not submitted_date else submitted_date['created_at__max']
                taskarray['time_out']           = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False    
                all_task.append(taskarray)

            return render(request,'admin/list_approved_task.html',{'task_list' : all_task,'client_list': client_list})
        else:
            messages.error(request, 'Please select client')
            return redirect('agent-dashboard')

    elif request.session.has_key('teamLeadertId'):
        if request.session.has_key('client_id'):
            team_leader_id  = request.session['teamLeadertId']
            client_id       = request.session['client_id']
            task_list       = task_tb.objects.all().filter(team_leader_id=team_leader_id,client_id=client_id,status='Approved').order_by('-id')
            
            get_all_clients = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
            client_list     = []
            for client_id in get_all_clients:
                client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                client_list.append(client_array)

            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            date1_year  = int(now.strftime("%y"))
            date1_month = int(now.strftime("%m"))
            date1_date  = int(now.strftime("%d"))
            
            all_task        = []
            for task in task_list:
                submitted_date      = None

                if task.status == 'Submitted' or task.status == 'Approved':
                    submitted_date  = customer_tb.objects.all().filter(task_id=task.id).aggregate(Max('created_at'))

                end_date    = task.end_date
                date2_year  = int(end_date.strftime("%y"))
                date2_month = int(end_date.strftime("%m"))
                date2_date  = int(end_date.strftime("%d"))
                
                d1          = datetime(date1_year,date1_month,date1_date)
                d2          = datetime(date2_year,date2_month,date2_date)

                start_time  = task.start_time
                end_time    = task.start_time
                now_time    = now.strftime("%H:%m")

                taskarray                       = {}
                taskarray['id']                 = task.id
                taskarray['task_id']            = task.task_id
                taskarray['title']              = task.title
                taskarray['client_id']          = task.client_id
                taskarray['branch_id']          = task.branch_id
                taskarray['job_id']             = task.job_id
                taskarray['start_date']         = task.start_date
                taskarray['end_date']           = task.end_date
                taskarray['end_time']           = task.end_time
                taskarray['status']             = task.status
                taskarray['have_request']       = task.have_request
                taskarray['have_delay_request'] = task.have_delay_request
                taskarray['approved_time']      = task.approved_time
                taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
                taskarray['submitted_date']     = None if not submitted_date else submitted_date['created_at__max']
                taskarray['time_out']           = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False    
                all_task.append(taskarray)
            
            return render(request,'admin/list_approved_task.html',{'task_list' : all_task,'client_list': client_list})
        else:
            messages.error(request, 'Please select client')
            return redirect('team-leader-dashboard')

    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def searchTask(request):
    if  request.method=='POST':
        search_key          = request.POST['search']
        if request.session.has_key('adminId'):
            task_list       = task_tb.objects.all().filter(title__icontains=search_key).exclude(status='Approved').order_by('-id')
            client_list     = client_tb.objects.all()

            now                 = datetime.now(pytz.timezone('Asia/Dubai'))

            date1_year          = int(now.strftime("%y"))
            date1_month         = int(now.strftime("%m"))
            date1_date          = int(now.strftime("%d"))
            
            all_task    = []
            for task in task_list:
                submitted_date      = None

                if task.status == 'Submitted' or task.status == 'Approved':
                    submitted_date  = customer_tb.objects.all().filter(task_id=task.id).aggregate(Max('created_at'))
                    
                end_date    = task.end_date
                date2_year  = int(end_date.strftime("%y"))
                date2_month = int(end_date.strftime("%m"))
                date2_date  = int(end_date.strftime("%d"))
                
                d1          = datetime(date1_year,date1_month,date1_date)
                d2          = datetime(date2_year,date2_month,date2_date)

                start_time  = task.start_time
                end_time    = task.start_time
                now_time    = now.strftime("%H:%m")

                taskarray                       = {}
                taskarray['id']                 = task.id
                taskarray['task_id']            = task.task_id
                taskarray['title']              = task.title
                taskarray['client_id']          = task.client_id
                taskarray['branch_id']          = task.branch_id
                taskarray['job_id']             = task.job_id
                taskarray['start_date']         = task.start_date
                taskarray['end_date']           = task.end_date
                taskarray['end_time']           = task.end_time
                taskarray['status']             = task.status
                taskarray['have_request']       = task.have_request
                taskarray['have_delay_request'] = task.have_delay_request
                taskarray['approved_time']      = task.approved_time
                taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
                taskarray['submitted_date']     = None if not submitted_date else submitted_date['created_at__max']
                taskarray['time_out']           = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False

                all_task.append(taskarray)

            return render(request,'admin/list_task.html',{'task_list' : all_task,'search_key' : search_key,'client_list' :client_list})

        elif request.session.has_key('agentId'):
            if request.session.has_key('client_id'):
                agent_id        = request.session['agentId']
                client_id       = request.session['client_id']
                task_list       = task_tb.objects.all().filter(title__icontains=search_key,agent_id=agent_id,client_id=client_id).exclude(status='Approved').order_by('-id')
                
                get_all_clients = task_tb.objects.all().filter(agent_id=agent_id).values('client_id').distinct()
                client_list     = []
                for client_id in get_all_clients:
                    client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                    client_list.append(client_array)

                now                 = datetime.now(pytz.timezone('Asia/Dubai'))

                date1_year          = int(now.strftime("%y"))
                date1_month         = int(now.strftime("%m"))
                date1_date          = int(now.strftime("%d"))
                
                all_task    = []
                for task in task_list:
                    submitted_date      = None

                    if task.status == 'Submitted' or task.status == 'Approved':
                        submitted_date  = customer_tb.objects.all().filter(task_id=task.id).aggregate(Max('created_at'))
                        
                    end_date    = task.end_date
                    date2_year  = int(end_date.strftime("%y"))
                    date2_month = int(end_date.strftime("%m"))
                    date2_date  = int(end_date.strftime("%d"))
                    
                    d1          = datetime(date1_year,date1_month,date1_date)
                    d2          = datetime(date2_year,date2_month,date2_date)

                    start_time  = task.start_time
                    end_time    = task.start_time
                    now_time    = now.strftime("%H:%m")

                    taskarray                       = {}
                    taskarray['id']                 = task.id
                    taskarray['task_id']            = task.task_id
                    taskarray['title']              = task.title
                    taskarray['client_id']          = task.client_id
                    taskarray['branch_id']          = task.branch_id
                    taskarray['job_id']             = task.job_id
                    taskarray['start_date']         = task.start_date
                    taskarray['end_date']           = task.end_date
                    taskarray['end_time']           = task.end_time
                    taskarray['status']             = task.status
                    taskarray['have_request']       = task.have_request
                    taskarray['have_delay_request'] = task.have_delay_request
                    taskarray['approved_time']      = task.approved_time
                    taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
                    taskarray['submitted_date']     = None if not submitted_date else submitted_date['created_at__max']
                    taskarray['time_out']           = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False

                    all_task.append(taskarray)  

                return render(request,'admin/list_task.html',{'task_list' : all_task,'search_key' :search_key,'client_list':client_list})
            else:
                messages.error(request, 'Please select client')
                return redirect('agent-dashboard')

        elif request.session.has_key('teamLeadertId'):
            if request.session.has_key('client_id'):
                team_leader_id  = request.session['teamLeadertId']
                client_id       = request.session['client_id']
                task_list       = task_tb.objects.all().filter(title__icontains=search_key,team_leader_id=team_leader_id,client_id=client_id).exclude(status='Approved').order_by('-id')
                
                get_all_clients = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
                client_list     = []
                for client_id in get_all_clients:
                    client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                    client_list.append(client_array)

                now                 = datetime.now(pytz.timezone('Asia/Dubai'))

                date1_year          = int(now.strftime("%y"))
                date1_month         = int(now.strftime("%m"))
                date1_date          = int(now.strftime("%d"))
                
                all_task    = []
                for task in task_list:
                    submitted_date      = None

                    if task.status == 'Submitted' or task.status == 'Approved':
                        submitted_date  = customer_tb.objects.all().filter(task_id=task.id).aggregate(Max('created_at'))
                        
                    end_date    = task.end_date
                    date2_year  = int(end_date.strftime("%y"))
                    date2_month = int(end_date.strftime("%m"))
                    date2_date  = int(end_date.strftime("%d"))
                    
                    d1          = datetime(date1_year,date1_month,date1_date)
                    d2          = datetime(date2_year,date2_month,date2_date)

                    start_time  = task.start_time
                    end_time    = task.start_time
                    now_time    = now.strftime("%H:%m")

                    taskarray                       = {}
                    taskarray['id']                 = task.id
                    taskarray['task_id']            = task.task_id
                    taskarray['title']              = task.title
                    taskarray['client_id']          = task.client_id
                    taskarray['branch_id']          = task.branch_id
                    taskarray['job_id']             = task.job_id
                    taskarray['start_date']         = task.start_date
                    taskarray['end_date']           = task.end_date
                    taskarray['end_time']           = task.end_time
                    taskarray['status']             = task.status
                    taskarray['have_request']       = task.have_request
                    taskarray['have_delay_request'] = task.have_delay_request
                    taskarray['approved_time']      = task.approved_time
                    taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
                    taskarray['submitted_date']     = None if not submitted_date else submitted_date['created_at__max']
                    taskarray['time_out']           = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False

                    all_task.append(taskarray)

                return render(request,'admin/list_task.html',{'task_list' : all_task,'search_key' : search_key,'client_list':client_list})
            else:
                messages.error(request, 'Please select client')
                return redirect('team-leader-dashboard')

        else:
            return redirect('admin-login')
    else:
        return redirect('list-task')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def searchApprovedTask(request):
    if  request.method=='POST':
        search_key          = request.POST['search']
        if request.session.has_key('adminId'):
            task_list       = task_tb.objects.all().filter(title__icontains=search_key,status='Approved').order_by('-id')
            client_list     = client_tb.objects.all()

            now                 = datetime.now(pytz.timezone('Asia/Dubai'))

            date1_year          = int(now.strftime("%y"))
            date1_month         = int(now.strftime("%m"))
            date1_date          = int(now.strftime("%d"))
            
            all_task    = []
            for task in task_list:
                submitted_date      = None

                if task.status == 'Submitted' or task.status == 'Approved':
                    submitted_date  = customer_tb.objects.all().filter(task_id=task.id).aggregate(Max('created_at'))
                    
                end_date    = task.end_date
                date2_year  = int(end_date.strftime("%y"))
                date2_month = int(end_date.strftime("%m"))
                date2_date  = int(end_date.strftime("%d"))
                
                d1          = datetime(date1_year,date1_month,date1_date)
                d2          = datetime(date2_year,date2_month,date2_date)

                start_time  = task.start_time
                end_time    = task.start_time
                now_time    = now.strftime("%H:%m")

                taskarray                       = {}
                taskarray['id']                 = task.id
                taskarray['task_id']            = task.task_id
                taskarray['title']              = task.title
                taskarray['client_id']          = task.client_id
                taskarray['branch_id']          = task.branch_id
                taskarray['job_id']             = task.job_id
                taskarray['start_date']         = task.start_date
                taskarray['end_date']           = task.end_date
                taskarray['end_time']           = task.end_time
                taskarray['status']             = task.status
                taskarray['have_request']       = task.have_request
                taskarray['have_delay_request'] = task.have_delay_request
                taskarray['approved_time']      = task.approved_time
                taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
                taskarray['submitted_date']     = None if not submitted_date else submitted_date['created_at__max']
                taskarray['time_out']           = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False

                all_task.append(taskarray)

            return render(request,'admin/list_approved_task.html',{'task_list' : all_task,'search_key' : search_key,'client_list' :client_list})

        elif request.session.has_key('agentId'):
            if request.session.has_key('client_id'):
                agent_id        = request.session['agentId']
                client_id       = request.session['client_id']
                task_list       = task_tb.objects.all().filter(title__icontains=search_key,agent_id=agent_id,client_id=client_id,status='Approved').order_by('-id')
                
                get_all_clients = task_tb.objects.all().filter(agent_id=agent_id).values('client_id').distinct()
                client_list     = []
                for client_id in get_all_clients:
                    client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                    client_list.append(client_array)

                now                 = datetime.now(pytz.timezone('Asia/Dubai'))

                date1_year          = int(now.strftime("%y"))
                date1_month         = int(now.strftime("%m"))
                date1_date          = int(now.strftime("%d"))
                
                all_task    = []
                for task in task_list:
                    submitted_date      = None

                    if task.status == 'Submitted' or task.status == 'Approved':
                        submitted_date  = customer_tb.objects.all().filter(task_id=task.id).aggregate(Max('created_at'))
                        
                    end_date    = task.end_date
                    date2_year  = int(end_date.strftime("%y"))
                    date2_month = int(end_date.strftime("%m"))
                    date2_date  = int(end_date.strftime("%d"))
                    
                    d1          = datetime(date1_year,date1_month,date1_date)
                    d2          = datetime(date2_year,date2_month,date2_date)

                    start_time  = task.start_time
                    end_time    = task.start_time
                    now_time    = now.strftime("%H:%m")

                    taskarray                       = {}
                    taskarray['id']                 = task.id
                    taskarray['task_id']            = task.task_id
                    taskarray['title']              = task.title
                    taskarray['client_id']          = task.client_id
                    taskarray['branch_id']          = task.branch_id
                    taskarray['job_id']             = task.job_id
                    taskarray['start_date']         = task.start_date
                    taskarray['end_date']           = task.end_date
                    taskarray['end_time']           = task.end_time
                    taskarray['status']             = task.status
                    taskarray['have_request']       = task.have_request
                    taskarray['have_delay_request'] = task.have_delay_request
                    taskarray['approved_time']      = task.approved_time
                    taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
                    taskarray['submitted_date']     = None if not submitted_date else submitted_date['created_at__max']
                    taskarray['time_out']           = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False

                    all_task.append(taskarray)  

                return render(request,'admin/list_approved_task.html',{'task_list' : all_task,'search_key' :search_key,'client_list':client_list})
            else:
                messages.error(request, 'Please select client')
                return redirect('agent-dashboard')

        elif request.session.has_key('teamLeadertId'):
            if request.session.has_key('client_id'):
                team_leader_id  = request.session['teamLeadertId']
                client_id       = request.session['client_id']
                task_list       = task_tb.objects.all().filter(title__icontains=search_key,team_leader_id=team_leader_id,client_id=client_id,status='Approved').order_by('-id')
                
                get_all_clients = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
                client_list     = []
                for client_id in get_all_clients:
                    client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                    client_list.append(client_array)

                now                 = datetime.now(pytz.timezone('Asia/Dubai'))

                date1_year          = int(now.strftime("%y"))
                date1_month         = int(now.strftime("%m"))
                date1_date          = int(now.strftime("%d"))
                
                all_task    = []
                for task in task_list:
                    submitted_date      = None

                    if task.status == 'Submitted' or task.status == 'Approved':
                        submitted_date  = customer_tb.objects.all().filter(task_id=task.id).aggregate(Max('created_at'))
                        
                    end_date    = task.end_date
                    date2_year  = int(end_date.strftime("%y"))
                    date2_month = int(end_date.strftime("%m"))
                    date2_date  = int(end_date.strftime("%d"))
                    
                    d1          = datetime(date1_year,date1_month,date1_date)
                    d2          = datetime(date2_year,date2_month,date2_date)

                    start_time  = task.start_time
                    end_time    = task.start_time
                    now_time    = now.strftime("%H:%m")

                    taskarray                       = {}
                    taskarray['id']                 = task.id
                    taskarray['task_id']            = task.task_id
                    taskarray['title']              = task.title
                    taskarray['client_id']          = task.client_id
                    taskarray['branch_id']          = task.branch_id
                    taskarray['job_id']             = task.job_id
                    taskarray['start_date']         = task.start_date
                    taskarray['end_date']           = task.end_date
                    taskarray['end_time']           = task.end_time
                    taskarray['status']             = task.status
                    taskarray['have_request']       = task.have_request
                    taskarray['have_delay_request'] = task.have_delay_request
                    taskarray['approved_time']      = task.approved_time
                    taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
                    taskarray['submitted_date']     = None if not submitted_date else submitted_date['created_at__max']
                    taskarray['time_out']           = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False

                    all_task.append(taskarray)

                return render(request,'admin/list_approved_task.html',{'task_list' : all_task,'search_key' : search_key,'client_list':client_list})
            else:
                messages.error(request, 'Please select client')
                return redirect('team-leader-dashboard')

        else:
            return redirect('admin-login')
    else:
        return redirect('list-task')





@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listTaskBasedJob(request):
    if request.session.has_key('adminId'):
        job_id          = request.GET['id']
        task_list       = task_tb.objects.all().filter(job_id=job_id).order_by('-id')
        client_list     = client_tb.objects.all()

        now             = datetime.now(pytz.timezone('Asia/Dubai'))

        date1_year  = int(now.strftime("%y"))
        date1_month = int(now.strftime("%m"))
        date1_date  = int(now.strftime("%d"))
        
        all_task        = []
        email_send      = False
        for task in task_list:
            if task.status == 'Approved':
                email_send  = True
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
            taskarray['client_id']          = task.client_id
            taskarray['branch_id']          = task.branch_id
            taskarray['job_id']             = task.job_id
            taskarray['start_date']         = task.start_date
            taskarray['end_date']           = task.end_date
            taskarray['status']             = task.status
            taskarray['have_request']       = task.have_request
            taskarray['have_delay_request'] = task.have_delay_request
            taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
            all_task.append(taskarray)

        return render(request,'admin/list_task.html',{'task_list' : all_task,'client_list':client_list,'email_send':email_send,'job_id':job_id})

    elif request.session.has_key('teamLeadertId'):
        if request.session.has_key('client_id'):
            job_id          = request.GET['id']
            team_leader_id  = request.session['teamLeadertId']
            client_id       = request.session['client_id']
            task_list       = task_tb.objects.all().filter(team_leader_id=team_leader_id,client_id=client_id,job_id=job_id).order_by('-id')
            
            get_all_clients = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
            client_list     = []
            for client_id in get_all_clients:
                client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                client_list.append(client_array)

            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            date1_year  = int(now.strftime("%y"))
            date1_month = int(now.strftime("%m"))
            date1_date  = int(now.strftime("%d"))
            
            all_task        = []
            email_send      = False
            for task in task_list:
                if task.status == 'Approved':
                    email_send  = True

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
                taskarray['client_id']          = task.client_id
                taskarray['branch_id']          = task.branch_id
                taskarray['job_id']             = task.job_id
                taskarray['start_date']         = task.start_date
                taskarray['end_date']           = task.end_date
                taskarray['status']             = task.status
                taskarray['have_request']       = task.have_request
                taskarray['have_delay_request'] = task.have_delay_request
                taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
                all_task.append(taskarray)
            
            return render(request,'admin/list_task.html',{'task_list' : all_task,'client_list':client_list,'email_send':email_send,'job_id':job_id})
        else:
            messages.error(request, 'Please select client')
            return redirect('team-leader-dashboard')

    else:
        return redirect('admin-login')






@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def filterTaskByType(request):
    if  request.method=='POST':
        date_from       = request.POST.get('date_from')
        date_to         = request.POST.get('date_to')
        get_type        = request.POST['type']
        get_id          = request.POST.getlist('get_id[]')

        if request.session.has_key('adminId'): 
            if get_type == 'client':
                if date_from and date_to:
                    task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),client_id__in=get_id).exclude(status='Approved').order_by('-id')
                else:
                    task_list       = task_tb.objects.all().filter(client_id__in=get_id).exclude(status='Approved').order_by('-id')

                get_all_clients = task_tb.objects.all().values('client_id').distinct()

                get_list        = []
                for client_id in get_all_clients:
                    client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                    get_list.append(client_array)

            if get_type == 'agent':
                if date_from and date_to:
                    task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),agent_id__in=get_id).exclude(status='Approved').order_by('-id')
                else:
                    task_list       = task_tb.objects.all().filter(agent_id__in=get_id).exclude(status='Approved').order_by('-id')
                    
                get_all_agents  = task_tb.objects.all().values('agent_id').distinct()

                get_list        = []
                for agent_id in get_all_agents:
                    agent_array = agent_tb.objects.all().filter(id=agent_id['agent_id']).get()
                    get_list.append(agent_array)
            
            if get_type == 'branch':
                if date_from and date_to:
                    task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),branch_id__in=get_id).exclude(status='Approved').order_by('-id')
                else:
                    task_list       = task_tb.objects.all().filter(branch_id__in=get_id).exclude(status='Approved').order_by('-id')

                get_all_branch  = task_tb.objects.all().values('branch_id').distinct()

                get_list        = []
                for branch_id in get_all_branch:
                    branch_array= branch_tb.objects.all().filter(id=branch_id['branch_id']).get()
                    get_list.append(branch_array)
            

        elif request.session.has_key('agentId'):
            if request.session.has_key('client_id'):
                agent_id            = request.session['agentId']
                if get_type == 'client':
                    if date_from and date_to:
                        task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),agent_id=agent_id,client_id__in=get_id).exclude(status='Approved').order_by('-id')
                    else:
                        task_list       = task_tb.objects.all().filter(agent_id=agent_id,client_id__in=get_id).exclude(status='Approved').order_by('-id')

                    get_all_clients = task_tb.objects.all().filter(agent_id=agent_id).values('client_id').distinct()
                    get_list        = []
                    for client_id in get_all_clients:
                        client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                        get_list.append(client_array)

                if get_type == 'branch':
                    if date_from and date_to:
                        task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),agent_id=agent_id,branch_id__in=get_id).exclude(status='Approved').order_by('-id')
                    else:
                        task_list       = task_tb.objects.all().filter(agent_id=agent_id,branch_id__in=get_id).exclude(status='Approved').order_by('-id')

                    get_all_branch  = task_tb.objects.all().filter(agent_id=agent_id).values('branch_id').distinct()

                    get_list        = []
                    for branch_id in get_all_branch:
                        branch_array= branch_tb.objects.all().filter(id=branch_id['branch_id']).get()
                        get_list.append(branch_array)
            else:
                messages.error(request, 'Please select client')
                return redirect('agent-dashboard')

        elif request.session.has_key('teamLeadertId'):
            if request.session.has_key('client_id'):
                team_leader_id  = request.session['teamLeadertId']

                if get_type == 'client':
                    if date_from and date_to:
                        task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),team_leader_id=team_leader_id,client_id__in=get_id).exclude(status='Approved').order_by('-id')
                    else:
                        task_list       = task_tb.objects.all().filter(team_leader_id=team_leader_id,client_id__in=get_id).exclude(status='Approved').order_by('-id')

                    get_all_clients = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()

                    get_list        = []
                    for client_id in get_all_clients:
                        client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                        get_list.append(client_array)

                if get_type == 'agent':
                    if date_from and date_to:
                        task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),team_leader_id=team_leader_id,agent_id__in=get_id).exclude(status='Approved').order_by('-id')
                    else:
                        task_list       = task_tb.objects.all().filter(team_leader_id=team_leader_id,agent_id__in=get_id).exclude(status='Approved').order_by('-id')

                    get_all_agents  = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('agent_id').distinct()

                    get_list        = []
                    for agent_id in get_all_agents:
                        agent_array = agent_tb.objects.all().filter(id=agent_id['agent_id']).get()
                        get_list.append(agent_array)

                if get_type == 'branch':
                    if date_from and date_to:
                        task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),team_leader_id=team_leader_id,branch_id__in=get_id).exclude(status='Approved').order_by('-id')
                    else:
                        task_list       = task_tb.objects.all().filter(team_leader_id=team_leader_id,branch_id__in=get_id).exclude(status='Approved').order_by('-id')

                    get_all_branch  = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('branch_id').distinct()

                    get_list        = []
                    for branch_id in get_all_branch:
                        branch_array= branch_tb.objects.all().filter(id=branch_id['branch_id']).get()
                        get_list.append(branch_array)
                
            else:
                messages.error(request, 'Please select client')
                return redirect('team-leader-dashboard')
        else:
            return redirect('admin-login')

        
        now                 = datetime.now(pytz.timezone('Asia/Dubai'))

        date1_year          = int(now.strftime("%y"))
        date1_month         = int(now.strftime("%m"))
        date1_date          = int(now.strftime("%d"))
        
        all_task    = []
        for task in task_list:
            submitted_date      = None

            if task.status == 'Submitted' or task.status == 'Approved':
                submitted_date  = customer_tb.objects.all().filter(task_id=task.id).aggregate(Max('created_at'))
                
            end_date    = task.end_date
            date2_year  = int(end_date.strftime("%y"))
            date2_month = int(end_date.strftime("%m"))
            date2_date  = int(end_date.strftime("%d"))
            
            d1          = datetime(date1_year,date1_month,date1_date)
            d2          = datetime(date2_year,date2_month,date2_date)

            start_time  = task.start_time
            end_time    = task.start_time
            now_time    = now.strftime("%H:%m")

            taskarray                       = {}
            taskarray['id']                 = task.id
            taskarray['task_id']            = task.task_id
            taskarray['title']              = task.title
            taskarray['client_id']          = task.client_id
            taskarray['branch_id']          = task.branch_id
            taskarray['job_id']             = task.job_id
            taskarray['start_date']         = task.start_date
            taskarray['end_date']           = task.end_date
            taskarray['end_time']           = task.end_time
            taskarray['status']             = task.status
            taskarray['have_request']       = task.have_request
            taskarray['have_delay_request'] = task.have_delay_request
            taskarray['approved_time']      = task.approved_time
            taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
            taskarray['submitted_date']     = None if not submitted_date else submitted_date['created_at__max']
            taskarray['time_out']           = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False

            all_task.append(taskarray)
        
        return render(request,'admin/list_task.html',{'task_list' : all_task,'get_id':get_id,'get_type':get_type,'get_list':get_list,'date_from' :date_from, 'date_to':date_to})

    else:
        return redirect('list-task')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def filterApprovedTaskTaskByType(request):
    if  request.method=='POST':
        date_from       = request.POST.get('date_from')
        date_to         = request.POST.get('date_to')
        get_type        = request.POST['type']
        get_id          = request.POST.getlist('get_id[]')

        if request.session.has_key('adminId'): 
            if get_type == 'client':
                if date_from and date_to:
                    task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),client_id__in=get_id,status='Approved').order_by('-id')
                else:
                    task_list       = task_tb.objects.all().filter(client_id__in=get_id,status='Approved').order_by('-id')

                get_all_clients = task_tb.objects.all().values('client_id').distinct()

                get_list        = []
                for client_id in get_all_clients:
                    client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                    get_list.append(client_array)

            if get_type == 'agent':
                if date_from and date_to:
                    task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),agent_id__in=get_id,status='Approved').order_by('-id')
                else:
                    task_list       = task_tb.objects.all().filter(agent_id__in=get_id,status='Approved').order_by('-id')
                    
                get_all_agents  = task_tb.objects.all().values('agent_id').distinct()

                get_list        = []
                for agent_id in get_all_agents:
                    agent_array = agent_tb.objects.all().filter(id=agent_id['agent_id']).get()
                    get_list.append(agent_array)
            
            if get_type == 'branch':
                if date_from and date_to:
                    task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),branch_id__in=get_id,status='Approved').order_by('-id')
                else:
                    task_list       = task_tb.objects.all().filter(branch_id__in=get_id,status='Approved').order_by('-id')

                get_all_branch  = task_tb.objects.all().values('branch_id').distinct()

                get_list        = []
                for branch_id in get_all_branch:
                    branch_array= branch_tb.objects.all().filter(id=branch_id['branch_id']).get()
                    get_list.append(branch_array)
            

        elif request.session.has_key('agentId'):
            if request.session.has_key('client_id'):
                agent_id            = request.session['agentId']
                if get_type == 'client':
                    if date_from and date_to:
                        task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),agent_id=agent_id,client_id__in=get_id,status='Approved').order_by('-id')
                    else:
                        task_list       = task_tb.objects.all().filter(agent_id=agent_id,client_id__in=get_id,status='Approved').order_by('-id')

                    get_all_clients = task_tb.objects.all().filter(agent_id=agent_id).values('client_id').distinct()
                    get_list        = []
                    for client_id in get_all_clients:
                        client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                        get_list.append(client_array)

                if get_type == 'branch':
                    if date_from and date_to:
                        task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),agent_id=agent_id,branch_id__in=get_id,status='Approved').order_by('-id')
                    else:
                        task_list       = task_tb.objects.all().filter(agent_id=agent_id,branch_id__in=get_id,status='Approved').order_by('-id')

                    get_all_branch  = task_tb.objects.all().filter(agent_id=agent_id).values('branch_id').distinct()

                    get_list        = []
                    for branch_id in get_all_branch:
                        branch_array= branch_tb.objects.all().filter(id=branch_id['branch_id']).get()
                        get_list.append(branch_array)
            else:
                messages.error(request, 'Please select client')
                return redirect('agent-dashboard')

        elif request.session.has_key('teamLeadertId'):
            if request.session.has_key('client_id'):
                team_leader_id  = request.session['teamLeadertId']

                if get_type == 'client':
                    if date_from and date_to:
                        task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),team_leader_id=team_leader_id,client_id__in=get_id,status='Approved').order_by('-id')
                    else:
                        task_list       = task_tb.objects.all().filter(team_leader_id=team_leader_id,client_id__in=get_id,status='Approved').order_by('-id')

                    get_all_clients = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()

                    get_list        = []
                    for client_id in get_all_clients:
                        client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                        get_list.append(client_array)

                if get_type == 'agent':
                    if date_from and date_to:
                        task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),team_leader_id=team_leader_id,agent_id__in=get_id,status='Approved').order_by('-id')
                    else:
                        task_list       = task_tb.objects.all().filter(team_leader_id=team_leader_id,agent_id__in=get_id,status='Approved').order_by('-id')

                    get_all_agents  = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('agent_id').distinct()

                    get_list        = []
                    for agent_id in get_all_agents:
                        agent_array = agent_tb.objects.all().filter(id=agent_id['agent_id']).get()
                        get_list.append(agent_array)

                if get_type == 'branch':
                    if date_from and date_to:
                        task_list       = task_tb.objects.all().filter(start_date__range=(date_from, date_to),team_leader_id=team_leader_id,branch_id__in=get_id,status='Approved').order_by('-id')
                    else:
                        task_list       = task_tb.objects.all().filter(team_leader_id=team_leader_id,branch_id__in=get_id,status='Approved').order_by('-id')

                    get_all_branch  = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('branch_id').distinct()

                    get_list        = []
                    for branch_id in get_all_branch:
                        branch_array= branch_tb.objects.all().filter(id=branch_id['branch_id']).get()
                        get_list.append(branch_array)
                
            else:
                messages.error(request, 'Please select client')
                return redirect('team-leader-dashboard')
        else:
            return redirect('admin-login')

        
        now                 = datetime.now(pytz.timezone('Asia/Dubai'))

        date1_year          = int(now.strftime("%y"))
        date1_month         = int(now.strftime("%m"))
        date1_date          = int(now.strftime("%d"))
        
        all_task    = []
        for task in task_list:
            submitted_date      = None

            if task.status == 'Submitted' or task.status == 'Approved':
                submitted_date  = customer_tb.objects.all().filter(task_id=task.id).aggregate(Max('created_at'))
                
            end_date    = task.end_date
            date2_year  = int(end_date.strftime("%y"))
            date2_month = int(end_date.strftime("%m"))
            date2_date  = int(end_date.strftime("%d"))
            
            d1          = datetime(date1_year,date1_month,date1_date)
            d2          = datetime(date2_year,date2_month,date2_date)

            start_time  = task.start_time
            end_time    = task.start_time
            now_time    = now.strftime("%H:%m")

            taskarray                       = {}
            taskarray['id']                 = task.id
            taskarray['task_id']            = task.task_id
            taskarray['title']              = task.title
            taskarray['client_id']          = task.client_id
            taskarray['branch_id']          = task.branch_id
            taskarray['job_id']             = task.job_id
            taskarray['start_date']         = task.start_date
            taskarray['end_date']           = task.end_date
            taskarray['end_time']           = task.end_time
            taskarray['status']             = task.status
            taskarray['have_request']       = task.have_request
            taskarray['have_delay_request'] = task.have_delay_request
            taskarray['approved_time']      = task.approved_time
            taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
            taskarray['submitted_date']     = None if not submitted_date else submitted_date['created_at__max']
            taskarray['time_out']           = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False

            all_task.append(taskarray)
        
        return render(request,'admin/list_approved_task.html',{'task_list' : all_task,'get_id':get_id,'get_type':get_type,'get_list':get_list,'date_from' :date_from, 'date_to':date_to})

    else:
        return redirect('list-task')





@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listTaskSubmittedToTeamLeader(request):
    if request.session.has_key('adminId'):
        task_list       = task_tb.objects.all().filter(status='Submitted').order_by('-id')
        client_list     = client_tb.objects.all()

        now             = datetime.now(pytz.timezone('Asia/Dubai'))

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
            taskarray['client_id']          = task.client_id
            taskarray['branch_id']          = task.branch_id
            taskarray['job_id']             = task.job_id
            taskarray['start_date']         = task.start_date
            taskarray['end_date']           = task.end_date
            taskarray['status']             = task.status
            taskarray['have_request']       = task.have_request
            taskarray['have_delay_request'] = task.have_delay_request
            taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
            all_task.append(taskarray)

        return render(request,'admin/list_task.html',{'task_list' : all_task,'client_list':client_list,'submit':'submit'})

    elif request.session.has_key('teamLeadertId'):
        if request.session.has_key('client_id'):
            team_leader_id  = request.session['teamLeadertId']
            client_id       = request.session['client_id']
            task_list       = task_tb.objects.all().filter(team_leader_id=team_leader_id,client_id=client_id,status='Submitted').order_by('-id')
            
            get_all_clients = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
            client_list     = []
            for client_id in get_all_clients:
                client_array= client_tb.objects.all().filter(id=client_id['client_id']).get()
                client_list.append(client_array)

            now             = datetime.now(pytz.timezone('Asia/Dubai'))

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
                taskarray['client_id']          = task.client_id
                taskarray['branch_id']          = task.branch_id
                taskarray['job_id']             = task.job_id
                taskarray['start_date']         = task.start_date
                taskarray['end_date']           = task.end_date
                taskarray['status']             = task.status
                taskarray['have_request']       = task.have_request
                taskarray['have_delay_request'] = task.have_delay_request
                taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
                all_task.append(taskarray)
            
            return render(request,'admin/list_task.html',{'task_list' : all_task,'client_list':client_list,'submit':'submit'})
        else:
            messages.error(request, 'Please select client')
            return redirect('team-leader-dashboard')

    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewTask(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
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
            getbranch_id        = request.POST['branch_id']
            branch_id           = branch_tb.objects.get(id=getbranch_id)
            get_agent_id        = request.POST['agent_id']
            agent_id            = agent_tb.objects.get(id=get_agent_id)
            required_hrs        = request.POST['required_hrs']
            now                 = datetime.now(pytz.timezone('Asia/Dubai'))

            client_id           = job_tb.objects.all().filter(id=job_id.id).get()
            a                   = task_tb(title=title,description=description,start_date=start_date,end_date=end_date,start_time=start_time,end_time=end_time,job_id=job_id,branch_id=branch_id,team_leader_id=team_leader_id,agent_id=agent_id,required_hrs=required_hrs,client_id=client_id.client_id,created_at=now,updated_at=now)
            a.save()

            latest_id           = task_tb.objects.latest('id')
            task_id             = 'TASK' + str(latest_id.id)

            task_tb.objects.all().filter(id=latest_id.id).update(task_id=task_id,updated_at=now)
            job_tb.objects.all().filter(id=job_id.id).update(status='On Going',updated_at=now)
           
            messages.success(request, 'Successfully added.')
            return redirect('list-task')
        else:
            if request.session.has_key('adminId'):
                job_list            = job_tb.objects.all()
                agent_list          = agent_tb.objects.all()
                team_leader_list    = team_leader_tb.objects.all()
                branch_list         = branch_tb.objects.all()
            if request.session.has_key('teamLeadertId'):
                team_leader_id      = request.session['teamLeadertId']
                client_id           = request.session['client_id']
                job_list            = job_tb.objects.all().filter(team_leader_id=team_leader_id,client_id=client_id)
                agent_list          = agent_tb.objects.all().filter(team_leader_id=team_leader_id)
                team_leader_list    = team_leader_tb.objects.all().filter(id=team_leader_id)
                branch_list         = branch_tb.objects.all().filter(client_id=client_id)
            return render(request,'admin/add_task.html',{'branch_list' : branch_list,'job_list' : job_list,'agent_list' : agent_list,'team_leader_list':team_leader_list})
    else:
        return redirect('admin-login')





@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateTask(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
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
            getbranch_id        = request.POST['branch_id']
            branch_id           = branch_tb.objects.get(id=getbranch_id)
            required_hrs        = request.POST['required_hrs']
            now                 = datetime.now(pytz.timezone('Asia/Dubai'))

            task_tb.objects.all().filter(id=task_id).update(title=title,description=description,start_date=start_date,end_date=end_date,start_time=start_time,end_time=end_time,job_id=job_id,branch_id=branch_id,team_leader_id=team_leader_id,agent_id=agent_id,required_hrs=required_hrs,updated_at=now)

            job_tb.objects.all().filter(id=job_id.id).update(status='On Going',updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-task')
        else:
            task_id             = request.GET['id']
            task_data           = task_tb.objects.all().filter(id=task_id)
            if request.session.has_key('adminId'):
                job_list            = job_tb.objects.all()
                agent_list          = agent_tb.objects.all()
                team_leader_list    = team_leader_tb.objects.all()
                branch_list         = branch_tb.objects.all()
            if request.session.has_key('teamLeadertId'):
                team_leader_id      = request.session['teamLeadertId']
                client_id           = request.session['client_id']
                job_list            = job_tb.objects.all().filter(team_leader_id=team_leader_id,client_id=client_id)
                agent_list          = agent_tb.objects.all().filter(team_leader_id=team_leader_id)
                team_leader_list    = team_leader_tb.objects.all().filter(id=team_leader_id)
                branch_list         = branch_tb.objects.all().filter(client_id=client_id)
            
            return render(request,'admin/edit_task_data.html',{'branch_list' : branch_list,'job_list' : job_list,'agent_list' : agent_list,'team_leader_list' : team_leader_list,'task_data' : task_data})
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
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
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
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        if request.session.has_key('adminId'):
            task_id         = request.GET['id']
            gettask_id      = task_tb.objects.all().filter(id=task_id).values()
            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            task_tb.objects.all().filter(id=task_id).update(team_leader_id=None,agent_id=None,status='Pending',updated_at=now)
        
        elif request.session.has_key('teamLeadertId'):
            task_id         = request.GET['id']
            gettask_id      = task_tb.objects.all().filter(id=task_id).values()
            now             = datetime.now(pytz.timezone('Asia/Dubai'))
            task_tb.objects.all().filter(id=task_id).update(agent_id=None,status='Pending',updated_at=now)

        messages.success(request, gettask_id[0]['task_id']+' ' + 'Cancelled Successfully .')
        return redirect('list-task')  
    else:
        return redirect('admin-login')



# approve assigned task
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def approveTask(request):
    if request.session.has_key('adminId') or  request.session.has_key('teamLeadertId'):
        task_id         = request.GET['id']
        gettask_id      = task_tb.objects.all().filter(id=task_id).values()
        now             = datetime.now(pytz.timezone('Asia/Dubai'))
        approved_time   = now
       
        task_tb.objects.all().filter(id=task_id).update(status='Approved',approved_time=approved_time,updated_at=now)
        customer_tb.objects.all().filter(task_id=task_id).update(status='Completed',updated_at=now)
        
        messages.success(request, gettask_id[0]['task_id']+' ' + 'approved Successfully .')
        return redirect('list-task')
        
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listCustomer(request):
    if request.session.has_key('adminId'):
        task_id         = request.GET['id']
        customer_list   = customer_tb.objects.all().filter(task_id=task_id).order_by('-id')

    elif request.session.has_key('teamLeadertId'):
        team_leader_id  = request.session['teamLeadertId']
        task_id         = request.GET['id']
        customer_list   = customer_tb.objects.all().filter(team_leader_id=team_leader_id,task_id=task_id).order_by('-id')
        
    elif request.session.has_key('agentId'):
        agent_id        = request.session['agentId']
        task_id         = request.GET['id']
        customer_list   = customer_tb.objects.all().filter(agent_id=agent_id,task_id=task_id).order_by('-id')

    else:
        return redirect('admin-login')

    task_data       = task_tb.objects.all().filter(id=task_id).get()

    now             = datetime.now(pytz.timezone('Asia/Dubai'))

    date1_year      = int(now.strftime("%y"))
    date1_month     = int(now.strftime("%m"))
    date1_date      = int(now.strftime("%d"))

    end_date        = task_data.end_date
    date2_year      = int(end_date.strftime("%y"))
    date2_month     = int(end_date.strftime("%m"))
    date2_date      = int(end_date.strftime("%d"))

    start_time      = task_data.start_time
    end_time        = task_data.start_time
    now_time        = now.strftime("%H:%m")

    
    d1              = datetime(date1_year,date1_month,date1_date)
    d2              = datetime(date2_year,date2_month,date2_date)

    is_expired      = True if d2 < d1 and task_data.status == 'Pending' else False 
    time_out        = True if now_time >= start_time and now_time <= end_time and task.status == 'Pending' else False
    customer_data   = []
    for customer in customer_list:
        staff_list  = customer.staff_ids.split(',')
        
        get_staff   = []
        for staff_data in staff_list:
            if staff_data:
                getdata = staff_tb.objects.all().filter(id=staff_data).get()
                get_staff.append(getdata.name)

        attend_staffs   = ','.join(get_staff)

        customer_data.append({
            'id'                    : customer.id,
            'date'                  : customer.date,
            'customer_id'           : customer.customer_id,
            'customer_entry_time'   : customer.customer_entry_time,
            'customer_exit_time'    : customer.customer_exit_time,
            'dwell_time'            : customer.dwell_time,
            'conversion_to'         : customer.conversion_to,
            'conversion_status'     : customer.conversion_status,
            'repeat_customer'       : customer.repeat_customer,
            'attend_staffs'         : attend_staffs,
            'submit_tl'             : customer.submit_tl,
        })
    return render(request,'admin/list_customer.html',{'customer_list' : customer_data,'task_id' : task_id,'submit_tl': task_data.submit_tl,'is_expired' : is_expired,'time_out':time_out})
    




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewCustomer(request):
    if request.session.has_key('adminId') or request.session.has_key('agentId') or request.session.has_key('teamLeadertId'):
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
            repeat_customer_id          = None if not request.POST.get('repeat_customer_id') else request.POST.get('repeat_customer_id')
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
            no_of_male                  = 0 if not request.POST['no_of_male'] else request.POST['no_of_male']
            no_of_female                = 0 if not request.POST['no_of_female'] else request.POST['no_of_male']
            # get_time_period             = request.POST['time_period_id']
            # time_period_id              = time_period_tb.objects.get(id=get_time_period)

            submit_tl                   = button == 'submit_tl' and True or False

            agent_id                    = task_id.agent_id
            job_id                      = task_id.job_id
            get_job_data                = job_tb.objects.get(id=job_id.id)
            branch_id                   = task_id.branch_id
            client_id                   = task_id.client_id
            team_leader_id              = task_id.team_leader_id

            now                         = datetime.now(pytz.timezone('Asia/Dubai'))


            if '09:00' <= customer_entry_time < '10:00':
                get_time_period         = 1
            elif '10:00' <= customer_entry_time < '12:00':
                get_time_period         = 2
            elif '12:00' <= customer_entry_time < '14:00':
                get_time_period         = 3
            elif '14:00' <= customer_entry_time < '16:00':
                get_time_period         = 4
            elif '16:00' <= customer_entry_time < '18:00':
                get_time_period         = 5
            elif '18:00' <= customer_entry_time < '20:00':
                get_time_period         = 6
            elif '20:00' <= customer_entry_time < '22:00':
                get_time_period         = 7
            elif '22:00' <= customer_entry_time < '24:00':
                get_time_period         = 8
            elif '24:00' <= customer_entry_time < '02:00':
                get_time_period         = 9

            time_period_id              = time_period_tb.objects.get(id=get_time_period)

            a                           = customer_tb(date=date,opening_time=opening_time,closing_time=closing_time,customer_id=customer_id,customer_entry_time=customer_entry_time,customer_exit_time=customer_exit_time,dwell_time=dwell_time,single=single,group=group,male=male,female=female,zone_ids=zone_ids,window_zone_ids=window_zone_ids,staff_ids=staff_ids,repeat_customer=repeat_customer,repeat_customer_id=repeat_customer_id,repeat_customer_visit_date=repeat_customer_visit_date,tray=tray,refreshment=refreshment,gloves=gloves,backup_stock=backup_stock,business_card=business_card,body_language=body_language,full_uniform=full_uniform,conversion_status=conversion_status,conversion_percentage=conversion_percentage,conversion_to=conversion_to,converted_count=converted_count,invoice_time=invoice_time,reason_for_no_conversion=reason_for_no_conversion,remark=remark,task_id=task_id,agent_id=agent_id,submit_tl=submit_tl,job_id=job_id,branch_id=branch_id,no_of_male=no_of_male,no_of_female=no_of_female,client_id=client_id,time_period_id=time_period_id,team_leader_id=team_leader_id,created_at=now,updated_at=now)
            a.save()
           
            task_tb.objects.all().filter(id=task_id.id).update(status='On Going',updated_at=now)
            client_tb.objects.all().filter(id=task_id.client_id.id).update(status='Active',updated_at=now)
            get_customer                = customer_tb.objects.all().filter(task_id=task_id.id).values()

            if(len(get_customer) == 1):
                job_tb.objects.all().filter(id=job_id.id).update(actual_start_date=now,updated_at=now)

            latest_id                   = customer_tb.objects.latest('id')

            messages.success(request, 'Successfully added.')
            return redirect('/list-customer?id='+ str(task_id.id))
        else:
            task_id                     = request.GET['id']
            gettask_id                  = task_tb.objects.get(id=task_id)
            get_branch_image            = gettask_id.branch_id.layout
            client_id                   = gettask_id.client_id.id
            branch_id                   = gettask_id.branch_id.id

            zone_list                   = zone_tb.objects.all().filter(branch_id=branch_id)
            window_zone_list            = window_zone_tb.objects.all().filter(branch_id=branch_id)
            staff_list                  = staff_tb.objects.all().filter(client_id=client_id)#need all client staff
            time_period                 = time_period_tb.objects.all()

            latest_id                   = 0 if not customer_tb.objects.all() else customer_tb.objects.latest('id')
            next_customer_id            = (0 if latest_id == 0 else int(latest_id.id)) + int(1)
            
            return render(request,'admin/add_customer.html',{'zone_list' : zone_list,'window_zone_list' : window_zone_list,'staff_list':staff_list,'task_id' :task_id,'time_period':time_period,'get_branch_image':get_branch_image,'client_id':client_id,'next_customer_id':next_customer_id,'branch_id':branch_id})
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addCustomerConfirmation(request):
    if request.session.has_key('adminId') or request.session.has_key('agentId') or request.session.has_key('teamLeadertId'):
        if request.method=="POST":
            get_task_id         = request.POST['task_id']
            opening_time        = request.POST['opening_time']
            closing_time        = request.POST['closing_time']
            now                 = datetime.now(pytz.timezone('Asia/Dubai'))

            get_last_entry      = customer_tb.objects.all().filter(task_id=get_task_id).latest('id')
            date                = get_last_entry.date                    

            customer_tb.objects.all().filter(date=date).update(opening_time=opening_time,closing_time=closing_time,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('/list-customer?id='+ str(get_task_id))

        else:
            get_task_id         = request.GET['task_id']
            get_last_entry      = customer_tb.objects.all().filter(task_id=get_task_id).latest('id')
            return render(request,'admin/customer_add_confirm.html',{'task_id':get_task_id,'get_customer_data':get_last_entry})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateCustomer(request):
    if request.session.has_key('adminId') or request.session.has_key('agentId') or request.session.has_key('teamLeadertId'):
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
            repeat_customer_id          = None if not request.POST.get('repeat_customer_id') else request.POST.get('repeat_customer_id')
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
            no_of_male                  = 0 if not request.POST['no_of_male'] else request.POST['no_of_male']
            no_of_female                = 0 if not request.POST['no_of_female'] else request.POST['no_of_female']
            submit_tl                   = button == 'submit_tl' and True or False
            # get_time_period             = request.POST['time_period_id']
            # time_period_id              = time_period_tb.objects.get(id=get_time_period)

            agent_id                    = task_id.agent_id
            job_id                      = task_id.job_id
            get_job_data                = job_tb.objects.get(id=job_id.id)
            branch_id                   = task_id.branch_id
            client_id                   = task_id.client_id
            team_leader_id              = task_id.team_leader_id

            now                         = datetime.now(pytz.timezone('Asia/Dubai'))


            if '09:00' <= customer_entry_time < '10:00':
                get_time_period         = 1
            elif '10:00' <= customer_entry_time < '12:00':
                get_time_period         = 2
            elif '12:00' <= customer_entry_time < '14:00':
                get_time_period         = 3
            elif '14:00' <= customer_entry_time < '16:00':
                get_time_period         = 4
            elif '16:00' <= customer_entry_time < '18:00':
                get_time_period         = 5
            elif '18:00' <= customer_entry_time < '20:00':
                get_time_period         = 6
            elif '20:00' <= customer_entry_time < '22:00':
                get_time_period         = 7
            elif '22:00' <= customer_entry_time < '24:00':
                get_time_period         = 8
            elif '24:00' <= customer_entry_time < '02:00':
                get_time_period         = 9


            time_period_id              = time_period_tb.objects.get(id=get_time_period)

            task_tb.objects.all().filter(id=task_id.id).update(status='On Going',updated_at=now)

            customer_tb.objects.all().filter(id=get_customer_id).update(date=date,opening_time=opening_time,closing_time=closing_time,customer_id=customer_id,customer_entry_time=customer_entry_time,customer_exit_time=customer_exit_time,dwell_time=dwell_time,single=single,group=group,male=male,female=female,zone_ids=zone_ids,window_zone_ids=window_zone_ids,staff_ids=staff_ids,repeat_customer=repeat_customer,repeat_customer_id=repeat_customer_id,repeat_customer_visit_date=repeat_customer_visit_date,tray=tray,refreshment=refreshment,gloves=gloves,backup_stock=backup_stock,business_card=business_card,body_language=body_language,full_uniform=full_uniform,conversion_status=conversion_status,conversion_percentage=conversion_percentage,conversion_to=conversion_to,converted_count=converted_count,invoice_time=invoice_time,reason_for_no_conversion=reason_for_no_conversion,remark=remark,task_id=task_id,agent_id=agent_id,submit_tl=submit_tl,job_id=job_id,branch_id=branch_id,no_of_male=no_of_male,no_of_female=no_of_female,client_id=client_id,time_period_id=time_period_id,team_leader_id=team_leader_id,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('/list-customer?id='+ str(task_id.id))
        else:
            customer_id         = request.GET['id']
            customer_data       = customer_tb.objects.all().filter(id=customer_id).get()

            gettask_id          = task_tb.objects.get(id=customer_data.task_id.id)
            client_id           = gettask_id.client_id.id
            branch_id           = gettask_id.branch_id.id

            zone_list           = zone_tb.objects.all().filter(branch_id=branch_id)
            window_zone_list    = window_zone_tb.objects.all().filter(branch_id=branch_id)
            staff_list          = staff_tb.objects.all().filter(client_id=client_id) #need all client staff
            time_period         = time_period_tb.objects.all()

            task_id             = customer_data.task_id_id
            zone_ids            = customer_data.zone_ids.split(',')
            win_ids             = customer_data.window_zone_ids.split(',')
            staff_ids           = customer_data.staff_ids.split(',')

            
            all_zones           = []
            for z_list in zone_list:
                zone_array              = {}
                zone_array['id']        = z_list.id
                zone_array['zone']      = z_list.zone
                zone_array['branch_id'] = z_list.branch_id
                
                if  str(z_list.id) in zone_ids:
                    zone_array['selected']  = 'selected'
                else:
                    zone_array['selected']  = ''
                all_zones.append(zone_array)


            all_winzones           = []
            for w_list in window_zone_list:
                win_zone_array              = {}
                win_zone_array['id']        = w_list.id
                win_zone_array['zone']      = w_list.zone
                win_zone_array['branch_id'] = w_list.branch_id
                
                if  str(w_list.id) in win_ids:
                    win_zone_array['selected']  = 'selected'
                else:
                    win_zone_array['selected']  = ''
                all_winzones.append(win_zone_array)


            all_staff               = []
            for s_list in staff_list:
                staff_array                 = {}
                staff_array['id']           = s_list.id
                staff_array['name']         = s_list.name
                staff_array['branch_id']    = s_list.branch_id
                
                if  str(s_list.id) in staff_ids:
                    staff_array['selected']  = 'selected'
                else:
                    staff_array['selected']  = ''
                all_staff.append(staff_array)

            
            opening_time        = datetime.strptime(customer_data.opening_time, '%H:%M').time()
            closing_time        = datetime.strptime(customer_data.closing_time, '%H:%M').time()

            repeat_customer_ids = customer_tb.objects.all().filter(date=customer_data.repeat_customer_visit_date,branch_id=branch_id).values('id')
           
            return render(request,'admin/edit_customer_data.html',{'zone_list' : all_zones,'window_zone_list' : all_winzones,'staff_list':all_staff,'task_id' :task_id,'customer_data' : customer_data,'time_period':time_period,'zone_ids':zone_ids,'opening_time':opening_time,'closing_time':closing_time,'repeat_customer_ids':repeat_customer_ids,'branch_id':branch_id})
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
        task_id         = request.GET['id']
        now             = datetime.now(pytz.timezone('Asia/Dubai'))
        
        task_tb.objects.all().filter(id=task_id).update(submit_tl=True,status='Submitted',updated_at=now)
        customer_tb.objects.all().filter(task_id=task_id).update(submit_tl=True,status='Submitted',updated_at=now)

        # messages.success(request, 'Success.')
        return redirect('/add-customer-confirm/?task_id='+ str(task_id))
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listStaffAttendance(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            client_id               = request.POST['client_id']
            date_from               = request.POST['date_from']
            date_to                 = request.POST['date_to']
            branch_id               = request.POST['branch_id']
            staff_id                = request.POST['staff_id']
            client_list             = client_tb.objects.all()
            branch                  = branch_tb.objects.all().filter(client_id=client_id)
            staff_list              = staff_tb.objects.all().filter(branch_id=branch_id)

            staff_attendance_list   = staff_attendance_tb.objects.all().filter(date__range=(date_from, date_to),client_id=client_id,staff_id=staff_id,approve=False)
            return render(request,'admin/list_staff_attendance.html',{'staff_attendance_list' : staff_attendance_list,'client_list':client_list,'client_id':client_id,'date_from':date_from,'date_to':date_to,'branch_id':branch_id,'staff_id':staff_id,'branch':branch,'staff_list':staff_list})
        else:
            staff_attendance_list   = staff_attendance_tb.objects.all().filter(approve=False).order_by('-id')
            client_list             = client_tb.objects.all()
            return render(request,'admin/list_staff_attendance.html',{'staff_attendance_list' : staff_attendance_list,'client_list':client_list})
    elif request.session.has_key('agentId'):
        if request.session.has_key('client_id'):
            client_id               = request.session['client_id']
            agent_id                = request.session['agentId']
            staff_attendance_list   = staff_attendance_tb.objects.all().filter(agent_id=agent_id,approve=False).order_by('-id')
            return render(request,'admin/list_staff_attendance.html',{'staff_attendance_list' : staff_attendance_list}) 
        else:
            messages.error(request, 'Please select client')
            return redirect('agent-dashboard')  

    elif request.session.has_key('teamLeadertId'):
        if request.session.has_key('client_id'):
            client_id               = request.session['client_id']
            staff_attendance_list   = staff_attendance_tb.objects.all().filter(client_id=client_id,approve=False).order_by('-id')
            return render(request,'admin/list_staff_attendance.html',{'staff_attendance_list' : staff_attendance_list}) 
        else:
            messages.error(request, 'Please select client')
            return redirect('team-leader-dashboard')  

    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listStaffApprovedAttendance(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            client_id               = request.POST['client_id']
            date_from               = request.POST['date_from']
            date_to                 = request.POST['date_to']
            branch_id               = request.POST['branch_id']
            staff_id                = request.POST['staff_id']
            client_list             = client_tb.objects.all()
            branch                  = branch_tb.objects.all().filter(client_id=client_id)
            staff_list              = staff_tb.objects.all().filter(branch_id=branch_id)

            staff_attendance_list   = staff_attendance_tb.objects.all().filter(date__range=(date_from, date_to),client_id=client_id,staff_id=staff_id,approve=True)
            return render(request,'admin/list_staff_approve_attendance.html',{'staff_attendance_list' : staff_attendance_list,'client_list':client_list,'client_id':client_id,'date_from':date_from,'date_to':date_to,'branch_id':branch_id,'staff_id':staff_id,'branch':branch,'staff_list':staff_list})
        else:
            staff_attendance_list   = staff_attendance_tb.objects.all().filter(approve=True).order_by('-id')
            client_list             = client_tb.objects.all()
            return render(request,'admin/list_staff_approve_attendance.html',{'staff_attendance_list' : staff_attendance_list,'client_list':client_list})
    elif request.session.has_key('agentId'):
        if request.session.has_key('client_id'):
            client_id               = request.session['client_id']
            agent_id                = request.session['agentId']
            staff_attendance_list   = staff_attendance_tb.objects.all().filter(agent_id=agent_id,approve=True).order_by('-id')
            return render(request,'admin/list_staff_approve_attendance.html',{'staff_attendance_list' : staff_attendance_list}) 
        else:
            messages.error(request, 'Please select client')
            return redirect('agent-dashboard')  

    elif request.session.has_key('teamLeadertId'):
        if request.session.has_key('client_id'):
            client_id               = request.session['client_id']
            staff_attendance_list   = staff_attendance_tb.objects.all().filter(client_id=client_id,approve=True).order_by('-id')
            return render(request,'admin/list_staff_approve_attendance.html',{'staff_attendance_list' : staff_attendance_list}) 
        else:
            messages.error(request, 'Please select client')
            return redirect('team-leader-dashboard')  

    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def searchStaffAttendance(request):
    if request.method=="POST":
        search_key                  = request.POST['search']

        staff_list                  = staff_tb.objects.all().filter(name__icontains=search_key)
        client_list                 = client_tb.objects.all()
        staff_attendance_list       = []
        for staff in staff_list:
            if request.session.has_key('adminId'):
                get_attendance_list = staff_attendance_tb.objects.all().filter(staff_id=staff.id).order_by('-id')
            elif request.session.has_key('agentId'):
                client_id           = request.session['client_id']
                agent_id            = request.session['agentId']
                get_attendance_list = staff_attendance_tb.objects.all().filter(staff_id=staff.id,agent_id=agent_id).order_by('-id')
            elif request.session.has_key('teamLeadertId'):
                client_id           = request.session['client_id']
                get_attendance_list = staff_attendance_tb.objects.all().filter(staff_id=staff.id,client_id=client_id).order_by('-id')


            for attendace in get_attendance_list:
                staff_attendance_list.append({
                    'id'                : attendace.id,
                    'date'              : attendace.date,
                    'client_id'         : attendace.client_id,
                    'staff_id'          : attendace.staff_id,
                    'in_time'           : attendace.in_time,
                    'out_time'          : attendace.out_time,
                    'official_break'    : attendace.official_break,
                    'un_official_break' : attendace.un_official_break,
                    'break_hours'       : attendace.break_hours,
                    'work_hours'        : attendace.work_hours,
                    'over_time'         : attendace.over_time,
                    'under_time'        : attendace.under_time,
                    'submit'            : attendace.submit
                })

        return render(request,'admin/list_staff_attendance.html',{'staff_attendance_list' : staff_attendance_list,'client_list':client_list,'search_key':search_key})
    else:
        return redirect('list-attendance')






@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addAttendance(request):
    if request.session.has_key('adminId') or request.session.has_key('agentId') or request.session.has_key('teamLeadertId'):
        if request.method=="POST":
            get_staff_id        = request.POST['staff_id']
            staff_id            = staff_tb.objects.get(id=get_staff_id)
            date                = request.POST['date']
            out_date            = request.POST['out_date']
            in_time             = request.POST['in_time']
            out_time            = request.POST['out_time']
            break_hours         = request.POST['break_hours']
            work_hours          = request.POST['work_hours']
            over_time           = request.POST['over_time']
            under_time          = request.POST['under_time']
            epoch_work_hours    = request.POST['epoch_work_hours']
            epoch_org_work_hours= request.POST['epoch_org_work_hours']
            epoch_over_time     = request.POST['epoch_over_time']
            epoch_under_time    = request.POST['epoch_under_time']
            num                 = request.POST['break_num']
            submit              = True if request.POST['button'] == 'submit' else False
            agent_id            = None
            if request.session.has_key('agentId'):
                get_agent_id    = request.session['agentId'] # attendance added agent id need
                agent_id        = agent_tb.objects.get(id=get_agent_id)

            client_id           = staff_tb.objects.all().filter(id=staff_id.id).get()
            
            now                 = datetime.now(pytz.timezone('Asia/Dubai'))

            a                   = staff_attendance_tb(staff_id=staff_id,date=date,out_date=out_date,in_time=in_time,out_time=out_time,break_hours=break_hours,work_hours=work_hours,over_time=over_time,under_time=under_time,client_id=client_id.client_id,epoch_work_hours=epoch_work_hours,epoch_org_work_hours=epoch_org_work_hours,epoch_over_time=epoch_over_time,epoch_under_time=epoch_under_time,submit=submit,agent_id=agent_id,created_at=now,updated_at=now)
            a.save()

            latest_id           = staff_attendance_tb.objects.latest('id')

            for x in range(int(num)):
                if request.POST.get('short_break['+str(x+1)+'][out_date]'):
                    break_out_date  = request.POST.get('short_break['+str(x+1)+'][out_date]')
                    break_out_time  = request.POST['short_break['+str(x+1)+'][out_time]']
                    break_in_date   = request.POST.get('short_break['+str(x+1)+'][in_date]')
                    break_in_time   = request.POST['short_break['+str(x+1)+'][in_time]']
                    break_type      = request.POST['short_break['+str(x+1)+'][type]']
                    remark          = request.POST['short_break['+str(x+1)+'][remark]']
                    break_diff      = request.POST['short_break['+str(x+1)+'][break_diff]']
                    
                    break_save      = staff_attendance_break_tb(attendance_id=latest_id,out_date=break_out_date,out_time=break_out_time,in_date=break_in_date,in_time=break_in_time,break_type=break_type,remark=remark,break_diff=break_diff,created_at=now,updated_at=now)
                    break_save.save()


            get_staff_break         = staff_attendance_break_tb.objects.all().filter(attendance_id=latest_id)
                
            official_break_sum      = 0
            un_official_break_sum   = 0

            for break_data in get_staff_break:
                if break_data.break_type == 'Official':
                    if(break_data.break_diff.isnumeric() == True):
                        official_break_sum  = official_break_sum + int(break_data.break_diff)
                elif break_data.break_type == 'Un Official':
                    if(break_data.break_diff.isnumeric() == True):
                        un_official_break_sum  = un_official_break_sum + int(break_data.break_diff)

            offdiffSeconds      = official_break_sum/1000
            HH                  = math.floor(offdiffSeconds/3600)
            MM                  = math.floor((offdiffSeconds%3600)/60)
            official_time       = str((("0" + str(HH)) if (HH < 10) else HH)) + ":" + str(("0" + str(MM)) if (MM < 10) else MM)
            
            
            un_official_time    = time.strftime('%H:%M', time.localtime(un_official_break_sum))
            unoffdiffSeconds    = un_official_break_sum/1000
            UHH                 = math.floor(unoffdiffSeconds/3600)
            UMM                 = math.floor((unoffdiffSeconds%3600)/60)
            un_official_time    = str((("0" + str(UHH)) if (UHH < 10) else UHH)) + ":" + str(("0" + str(UMM)) if (UMM < 10) else UMM)
               
            staff_attendance_tb.objects.all().filter(id=latest_id.id).update(official_break=official_time,un_official_break=un_official_time,updated_at=now)
           
            messages.success(request, 'Successfully added.')
            return redirect('list-attendance')
        else:
            if request.session.has_key('adminId'):
                staff_list      = staff_tb.objects.all()
            if request.session.has_key('agentId') or request.session.has_key('teamLeadertId'):
                client_id       = request.session['client_id']
                staff_list      = staff_tb.objects.all().filter(client_id=client_id)

            return render(request,'admin/add_attendance.html',{'staff_list' : staff_list})
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def viewAttendance(request):
    if request.session.has_key('adminId') or request.session.has_key('agentId') or request.session.has_key('teamLeadertId') or request.session.has_key('clientId'):
        attendance_id       = request.GET['id']
        staff_list          = staff_tb.objects.all()
        attendace_data      = staff_attendance_tb.objects.all().filter(id=attendance_id)
        attendace_break     = staff_attendance_break_tb.objects.all().filter(attendance_id=attendance_id)

        list_break          = []
        key                 = 0
        for break_times in attendace_break:
            key                         = key+1
            break_array                 = {}
            break_array['key']          = key
            break_array['out_date']     = break_times.out_date
            break_array['out_time']     = break_times.out_time
            break_array['in_date']      = break_times.in_date
            break_array['in_time']      = break_times.in_time
            break_array['break_type']   = break_times.break_type
            break_array['remark']       = break_times.remark

            list_break.append(break_array)
        return render(request,'admin/view_attendance.html',{'staff_list' : staff_list,'attendace_data':attendace_data,'attendace_break':attendace_break})
    else:
        return redirect('admin-login')





@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def editAttendance(request):
    if request.session.has_key('adminId') or request.session.has_key('agentId') or request.session.has_key('teamLeadertId') or request.session.has_key('clientId'):
        if request.method=="POST":
            staff_attendace_id  = request.POST['staff_attendace_id']
            attendance_id       = staff_attendance_tb.objects.get(id=staff_attendace_id)
            get_staff_id        = request.POST['staff_id']
            staff_id            = staff_tb.objects.get(id=get_staff_id)
            date                = request.POST['date']
            out_date            = request.POST['out_date']
            in_time             = request.POST['in_time']
            out_time            = request.POST['out_time']
            break_hours         = request.POST['break_hours']
            work_hours          = request.POST['work_hours']
            over_time           = request.POST['over_time']
            under_time          = request.POST['under_time']
            epoch_work_hours    = request.POST['epoch_work_hours']
            epoch_org_work_hours= request.POST['epoch_org_work_hours']
            epoch_over_time     = request.POST['epoch_over_time']
            epoch_under_time    = request.POST['epoch_under_time']
            num                 = request.POST['break_num']
            submit              = True if request.POST['button'] == 'submit' else False

            client_id           = staff_tb.objects.all().filter(id=staff_id.id).get()
            
            now                 = datetime.now(pytz.timezone('Asia/Dubai'))

            staff_attendance_tb.objects.all().filter(id=staff_attendace_id).update(staff_id=staff_id,date=date,out_date=out_date,in_time=in_time,out_time=out_time,break_hours=break_hours,work_hours=work_hours,over_time=over_time,under_time=under_time,client_id=client_id.client_id,epoch_work_hours=epoch_work_hours,epoch_org_work_hours=epoch_org_work_hours,epoch_over_time=epoch_over_time,epoch_under_time=epoch_under_time,submit=submit,updated_at=now)

            latest_id           = attendance_id
            
            fromReg             = staff_attendance_break_tb.objects.all().filter(attendance_id=latest_id)
            fromReg.delete()

            for x in range(int(num)):
                if request.POST.get('short_break['+str(x+1)+'][out_date]'):
                    break_id        = request.POST.get('short_break['+str(x+1)+'][break_id]')
                    break_out_date  = request.POST.get('short_break['+str(x+1)+'][out_date]')
                    break_out_time  = request.POST.get('short_break['+str(x+1)+'][out_time]')
                    break_in_date   = request.POST.get('short_break['+str(x+1)+'][in_date]')
                    break_in_time   = request.POST.get('short_break['+str(x+1)+'][in_time]')
                    break_type      = request.POST.get('short_break['+str(x+1)+'][type]')
                    remark          = request.POST.get('short_break['+str(x+1)+'][remark]')
                    break_diff      = request.POST.get('short_break['+str(x+1)+'][break_diff]')
                    
                    
                    break_save      = staff_attendance_break_tb(attendance_id=latest_id,out_date=break_out_date,out_time=break_out_time,in_date=break_in_date,in_time=break_in_time,break_type=break_type,remark=remark,break_diff=break_diff,created_at=now,updated_at=now)
                    break_save.save()


            get_staff_break         = staff_attendance_break_tb.objects.all().filter(attendance_id=latest_id)
                
            official_break_sum      = 0
            un_official_break_sum   = 0

            for break_data in get_staff_break:
                if break_data.break_type == 'Official':
                    if(break_data.break_diff.isnumeric() == True):
                        official_break_sum  = official_break_sum + int(break_data.break_diff)
                elif break_data.break_type == 'Un Official':
                    if(break_data.break_diff.isnumeric() == True):
                        un_official_break_sum  = un_official_break_sum + int(break_data.break_diff)

            offdiffSeconds      = official_break_sum/1000
            HH                  = math.floor(offdiffSeconds/3600)
            MM                  = math.floor((offdiffSeconds%3600)/60)
            official_time       = str((("0" + str(HH)) if (HH < 10) else HH)) + ":" + str(("0" + str(MM)) if (MM < 10) else MM)
            
            
            un_official_time    = time.strftime('%H:%M', time.localtime(un_official_break_sum))
            unoffdiffSeconds    = un_official_break_sum/1000
            UHH                 = math.floor(unoffdiffSeconds/3600)
            UMM                 = math.floor((unoffdiffSeconds%3600)/60)
            un_official_time    = str((("0" + str(UHH)) if (UHH < 10) else UHH)) + ":" + str(("0" + str(UMM)) if (UMM < 10) else UMM)
               
            staff_attendance_tb.objects.all().filter(id=latest_id.id).update(official_break=official_time,un_official_break=un_official_time,updated_at=now)
           

            messages.success(request, 'Successfully updated.')
            return redirect('list-attendance')
        else:
            attendance_id       = request.GET['id']
            staff_list          = staff_tb.objects.all()
            attendace_data      = staff_attendance_tb.objects.all().filter(id=attendance_id)
            attendace_break     = staff_attendance_break_tb.objects.all().filter(attendance_id=attendance_id)
            
            for staff in attendace_data:
                staff_data      = staff_tb.objects.all().filter(id=staff.staff_id.id).get()

            staff_total_work_hour       = int(staff_data.total_hrs) * 60000 * 60
            staff_required_work_hour    = int(staff_data.required_hrs) * 60000 * 60

            list_break          = []
            key                 = 0
            for break_times in attendace_break:
                key                         = key+1
                break_array                 = {}
                break_array['key']          = key
                break_array['id']           = break_times.id
                break_array['out_date']     = break_times.out_date
                break_array['out_time']     = break_times.out_time
                break_array['in_date']      = break_times.in_date
                break_array['in_time']      = break_times.in_time
                break_array['break_type']   = break_times.break_type
                break_array['remark']       = break_times.remark
                break_array['break_diff']   = break_times.break_diff
                break_array['remove']       = True
                if(len(attendace_break) == key):
                    break_array['remove']   = False

                list_break.append(break_array)
            count_break = 1 if len(attendace_break) == 0 else len(attendace_break)
            actual_break= len(attendace_break)
            
            return render(request,'admin/edit_attendance.html',{'staff_list' : staff_list,'attendace_data':attendace_data,'attendace_break':list_break,'count_break':count_break,'staff_total_work_hour':staff_total_work_hour,'staff_required_work_hour':staff_required_work_hour,'actual_break':actual_break})
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
            all_type            = request.POST['all_type']


            #############################################################################################
            staff_list                  = staff_tb.objects.all().filter(client_id=client_id).values()
            branch_list                 = branch_tb.objects.all().filter(client_id=client_id).values()
            get_zone_list               = zone_tb.objects.all().filter(client_id=client_id).values()
            zone_list                   = []
            for data in get_zone_list:
                branch                  = branch_tb.objects.all().filter(id=data['branch_id_id']).get()
                zone_array              = {}
                zone_array['id']        = data['id']
                zone_array['zone']      = data['zone']
                zone_array['branch']    = branch.name
                zone_list.append(zone_array)

            get_window_zone_list        = window_zone_tb.objects.filter(client_id=client_id).all().values()
            window_zone_list            = []
            for data in get_window_zone_list:
                branch                  = branch_tb.objects.all().filter(id=data['branch_id_id']).get()
                zone_array              = {}
                zone_array['id']        = data['id']
                zone_array['zone']      = data['zone']
                zone_array['branch']    = branch.name
                window_zone_list.append(zone_array)
            #####################################################################################################

            if request.session.has_key('adminId'):
                all_clients     = client_tb.objects.all()
            elif request.session.has_key('teamLeadertId'):
                team_leader_id  = request.session['teamLeadertId']
                get_all_jobs    = job_tb.objects.all().filter(team_leader_id=team_leader_id)
                all_clients     = []
                for job in get_all_jobs:
                    client_data = job.client_id
                    all_clients.append(client_data)
            
            #############################################################################################################
            if category == 'time' or category == 'performance':
                category_type_id = ','.join(category_type_id)
            
            ###################################################################################################################

            request_data        = [{'date_from' : date_from ,'date_to' : date_to ,'category' :category,'category_type_id' : category_type_id,'selected_type' : selected_type,'client_id' : get_client_id,'all_type' : all_type}]

            ###################################################################################################################

            if category == 'staff':
                if all_type == 'All':
                    category_type_id    = staff_tb.objects.all().filter(client_id=client_id).values_list('id',flat=True)
                
                get_data_list           = []
                for category in category_type_id:
                    staff_name              = staff_tb.objects.all().filter(id=category).values('name')
                    list_data               = {}
                    
                    get_data                = customer_tb.objects.all().filter(date__range=(date_from, date_to),conversion_to=category,status="Completed").values().order_by('conversion_to')
                    list_data[staff_name[0]['name']]    = get_data
                    get_data_list.append(list_data)

                ################################################################################
                distinct_data       = customer_tb.objects.all().filter(date__range=(date_from, date_to),conversion_to__in=category_type_id,status="Completed").values('conversion_to').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).annotate(repeat_customer=(Sum(Cast('repeat_customer', IntegerField())))).order_by().distinct()
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
                    my_dict['repeat_cust_count']=  x['repeat_customer']
                    my_dict['repeat_customer']  =  round(0 if not x['repeat_customer'] else x['repeat_customer'] / (x['single'] + x['group'])* 100)
                    my_dict['pct']              =  round(0 if not x['converted_count'] else x['converted_count']/ (x['single'] + x['group'])* 100)
                    get_distinct_data.append(my_dict)


            elif category == 'branch':
                if all_type == 'All':
                    category_type_id        = branch_tb.objects.all().filter(client_id=client_id).values_list('id',flat=True)

                get_data_list       = []
                for category in category_type_id:
                    branch_name             = branch_tb.objects.all().filter(id=category).values('name')
                    list_data               = {}
                    
                    get_data                = customer_tb.objects.all().filter(date__range=(date_from, date_to),branch_id=category,status="Completed").values().order_by('branch_id')
                    list_data[branch_name[0]['name']]    = get_data
                    get_data_list.append(list_data)

                ################################################################################

                distinct_data   = customer_tb.objects.all().filter(date__range=(date_from, date_to),branch_id__in=category_type_id,status="Completed").values('branch_id').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).annotate(repeat_customer=(Sum(Cast('repeat_customer', IntegerField())))).order_by().distinct()
                
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
                    my_dict['repeat_cust_count']=  x['repeat_customer']
                    my_dict['repeat_customer']  =  round(0 if not x['repeat_customer'] else x['repeat_customer'] / (x['single'] + x['group'])* 100)
                    my_dict['pct']              =  round(0 if not x['converted_count'] else x['converted_count'] / (x['single'] + x['group'])* 100)
                    get_distinct_data.append(my_dict)
                    
            elif category == 'window_zone':
                if all_type == 'All':
                    category_type_id            = window_zone_tb.objects.all().filter(client_id=client_id).values_list('id',flat=True)

                all_data            = []
                get_data_list       = []
                for x in category_type_id:
                    zone_id         = x

                    zone                        = window_zone_tb.objects.all().filter(id=zone_id).values('zone')
                    list_data                   = {}
                    
                    # get_data                    = customer_tb.objects.all().filter(date__range=(date_from, date_to),status="Completed").extra(where=['FIND_IN_SET('+str(x)+', window_zone_ids)']).values().order_by()
                    
                    get_data                    = customer_tb.objects.all().filter(date__range=(date_from, date_to),status="Completed",window_zone_ids__contains=str(x)).values().order_by()

                    list_data[zone[0]['zone']]  = get_data
                    get_data_list.append(list_data)

                    ################################################################################
                
                get_distinct_data       = []
                i                       = 0
                filter_keys             = []

                for get_detailed_data in get_data_list:
                    key     = list(get_detailed_data.keys())
                    values  = list(get_detailed_data.values())
                    
                    get_all_data        = []
                    
                    i                   = i + 1
                    filter_keys.append(str(key[0]))
                    
                    if values[0]:
                        for data in values[0]:
                            staff_name                      = staff_tb.objects.all().filter(id=data['conversion_to_id']).values('name')
                            get_ids                         = data['zone_ids'].split(',')
                            zone_names                      = []
                            for zoneid in get_ids:
                                if zoneid:
                                    
                                    zone                    = zone_tb.objects.all().filter(id=zoneid).values('zone')
                                    zone_names.append(zone[0]['zone'])

                            get_win_ids                     = data['window_zone_ids'].split(',')
                            win_zone_names                  = []
                            for winzoneid in get_win_ids:
                                if winzoneid:
                                    winzone                     = window_zone_tb.objects.all().filter(id=winzoneid).values('zone')
                                    win_zone_names.append(winzone[0]['zone'])

                            my_dict = {}
                            my_dict['key']                  =   i
                            my_dict['name']                 =   key[0]
                            my_dict['single']               =  (data['single'] == True and 1 or 0)
                            my_dict['group']                =  (data['group'] == True and 1 or 0)
                            my_dict['total']                =  my_dict['single'] + my_dict['group']
                            my_dict['male']                 =  (data['male'] == True and 1 or 0) + (0 if not data['no_of_male'] else data['no_of_male'])
                            my_dict['female']               =  (data['female'] == True and 1 or 0) + (0 if not data['no_of_female'] else data['no_of_female'])
                            my_dict['repeat_customer']      =  (data['repeat_customer'] == True and 1 or 0)
                            my_dict['conversion_status']    =  data['conversion_status']
                            my_dict['converted_count']      =  data['converted_count']
                            my_dict['conversion_percentage']=  data['conversion_percentage']
                            get_all_data.append(my_dict)
                        
                        # get_distinct_data.sort(key=lambda x: x.get('date'), reverse=False)
                        male                    = 0
                        female                  = 0
                        total_count             = 0
                        single                  = 0
                        group                   = 0
                        converted_count         = 0
                        conversion_percentage   = 0
                        repeat_customer         = 0
                        
                        for total in get_all_data:
                            single                  = single + total['single']
                            
                            group                   = group + total['group']
                            total_count             = total_count +  total['total']
                            repeat_customer         = repeat_customer +  total['repeat_customer']
                            male                    = male +  total['male']
                            female                  = female +  total['female']
                            
                            converted_count         =  converted_count + (0 if not total['converted_count'] else total['converted_count']) 
                            conversion_percentage   =  conversion_percentage + (0 if not total['conversion_percentage'] else total['conversion_percentage'])

                        
                        total_pct                   = 0 if total_count == 0 else round((converted_count / total_count) * 100)
                        total_repeat_pct            = 0 if total_count == 0 else round((repeat_customer / total_count) * 100)
                        data_total_sum              = {'key':total['key'],'name': total['name'] ,'single' :single,'group':group,'total':total_count,'male':male,'female':female,'converted_count':converted_count,'pct':total_pct,'repeat_customer':total_repeat_pct,'repeat_cust_count':repeat_customer}
                        get_distinct_data.append(data_total_sum)

            elif category == 'zone':  
                if all_type == 'All':
                    category_type_id            = zone_tb.objects.all().filter(client_id=client_id).values_list('id',flat=True)

                all_data            = []
                get_data_list       = []
                for x in category_type_id:
                    zone_id         = x

                    zone                        = zone_tb.objects.all().filter(id=zone_id).values('zone')
                    list_data                   = {}
                    
                    get_data                    = customer_tb.objects.all().filter(date__range=(date_from, date_to),status="Completed",zone_ids__contains=str(x)).values().order_by()

                    list_data[zone[0]['zone']]  = get_data
                    get_data_list.append(list_data)

                    ################################################################################
                
                get_distinct_data       = []
                i                       = 0
                filter_keys             = []

                for get_detailed_data in get_data_list:
                    key     = list(get_detailed_data.keys())
                    values  = list(get_detailed_data.values())
                    
                    get_all_data        = []
                    
                    i                   = i + 1
                    filter_keys.append(str(key[0]))
                    
                    if values[0]:
                        for data in values[0]:
                            staff_name                      = staff_tb.objects.all().filter(id=data['conversion_to_id']).values('name')
                            get_ids                         = data['zone_ids'].split(',')
                            zone_names                      = []
                            for zoneid in get_ids:
                                if zoneid:
                                    
                                    zone                    = zone_tb.objects.all().filter(id=zoneid).values('zone')
                                    zone_names.append(zone[0]['zone'])

                            get_win_ids                     = data['window_zone_ids'].split(',')
                            win_zone_names                  = []
                            for winzoneid in get_win_ids:
                                if winzoneid:
                                    winzone                 = window_zone_tb.objects.all().filter(id=winzoneid).values('zone')
                                    win_zone_names.append(winzone[0]['zone'])

                            my_dict = {}
                            my_dict['key']                  =   i
                            my_dict['name']                 =   key[0]
                            my_dict['single']               =  (data['single'] == True and 1 or 0)
                            my_dict['group']                =  (data['group'] == True and 1 or 0)
                            my_dict['total']                =  my_dict['single'] + my_dict['group']
                            my_dict['male']                 =  (data['male'] == True and 1 or 0) + (0 if not data['no_of_male'] else data['no_of_male'])
                            my_dict['female']               =  (data['female'] == True and 1 or 0) + (0 if not data['no_of_female'] else data['no_of_female'])
                            my_dict['repeat_customer']      =  (data['repeat_customer'] == True and 1 or 0)
                            my_dict['conversion_status']    =  data['conversion_status']
                            my_dict['converted_count']      =  data['converted_count']
                            my_dict['conversion_percentage']=  data['conversion_percentage']
                            get_all_data.append(my_dict)
                        
                            
                        # get_distinct_data.sort(key=lambda x: x.get('date'), reverse=False)
                        male                    = 0
                        female                  = 0
                        total_count             = 0
                        single                  = 0
                        group                   = 0
                        converted_count         = 0
                        conversion_percentage   = 0
                        repeat_customer         = 0
                        
                        for total in get_all_data:
                            single                  = single + total['single']
                            
                            group                   = group + total['group']
                            total_count             = total_count +  total['total']
                            repeat_customer         = repeat_customer +  total['repeat_customer']
                            male                    = male +  total['male']
                            female                  = female +  total['female']
                            
                            converted_count         =  converted_count + (0 if not total['converted_count'] else total['converted_count']) 
                            conversion_percentage   =  conversion_percentage + (0 if not total['conversion_percentage'] else total['conversion_percentage'])
                        total_pct                   = 0 if total_count == 0 else round((converted_count / total_count) * 100)
                        total_repeat_pct            = 0 if total_count == 0 else round((repeat_customer / total_count) * 100)
                        
                        data_total_sum              = {'key':total['key'],'name': total['name'] ,'single' :single,'group':group,'total':total_count,'male':male,'female':female,'converted_count':converted_count,'pct':total_pct,'repeat_customer':total_repeat_pct,'repeat_cust_count':repeat_customer}
                        get_distinct_data.append(data_total_sum)

            ###################################################################################################

            elif category == 'time_wise_branch':
                if all_type == 'All':
                    category_type_id        = branch_tb.objects.all().filter(client_id=client_id).values_list('id',flat=True)

                get_time_periods            = time_period_tb.objects.all()

                time_wise_data              = []
                filter_keys                 = []
                i                           = 0   
                for branch in category_type_id:
                    branch_data             = branch_tb.objects.all().filter(id=branch).get()

                    filter_keys.append(branch_data.name)
                    i                       = i + 1
                    time_data               = []
                    for time in get_time_periods:
                        get_branch_data                     = customer_tb.objects.all().filter(date__range=(date_from, date_to),branch_id=branch_data.id,time_period_id=time.id,status="Completed").values('branch_id').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                        time_list_array                     = {}

                        time_list_array['time_period']      = time.period
                        time_list_array['single']           = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single']
                        time_list_array['group']            = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['group']
                        time_list_array['total']            = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single'] + get_branch_data[0]['group']
                        time_list_array['male']             = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['male']
                        time_list_array['female']           = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['female']
                        time_list_array['converted_count']  = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['converted_count']
                        pct         = 0
                        if(len(get_branch_data) != 0):
                            converted_count = 0 if (len(get_branch_data) == 0) else (0 if not get_branch_data[0]['converted_count'] else get_branch_data[0]['converted_count'])
                            total_count     = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single'] + get_branch_data[0]['group']
                            
                            if(total_count != 0):
                                pct         = round(converted_count / total_count * 100)
                            else:
                                pct         = 0
                        time_list_array['pct']   = pct

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
                        
                        converted_count         =  converted_count + (0 if not total['converted_count'] else total['converted_count'])
                        conversion_percentage   =  conversion_percentage + total['pct']
                        
                    total_pct                   = 0 if total_count == 0 else round(converted_count / total_count * 100)
                    data_total_sum              = {'time_period' : time_period,'single' : single,'group' :group,'single' :single,'group':group,'total':total_count,'male':male,'female':female,'converted_count':converted_count,'pct':total_pct,'total_rw':True}
                    time_data.append(data_total_sum)

                    branch_list_array                       = {}
                    branch_list_array[branch_data.name,i]   = time_data
                    time_wise_data.append(branch_list_array)
                
                table_num   = []
                for x in range(len(filter_keys)):
                    table_num.append('tbl'+str(x+1))

                return render(request,'admin/time_wise.html',{'get_data' : time_wise_data,'request_data' : request_data,'staff_list' :staff_list,'branch_list' :branch_list,'zone_list' :zone_list,'window_zone_list':window_zone_list,'clients' :all_clients,'filter_keys':filter_keys,'table_num':table_num})

            elif category == 'time_wise_staff':
                if all_type == 'All':
                    category_type_id        = staff_tb.objects.all().filter(client_id=client_id).values_list('id',flat=True)

                get_time_periods            = time_period_tb.objects.all()

                time_wise_data              = []
                filter_keys                 = []
                i                           = 0   
                for staff in category_type_id:
                    staff_data              = staff_tb.objects.all().filter(id=staff).get()
                    i                       = i + 1
                    filter_keys.append(staff_data.name)
                    time_data               = []
                    for time in get_time_periods:
                        get_staff_data                      = customer_tb.objects.all().filter(date__range=(date_from, date_to),client_id=client_id,conversion_to=staff_data.id,time_period_id=time.id,status="Completed").values('conversion_to').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                        time_list_array                     = {}

                        time_list_array['time_period']      = time.period
                        time_list_array['single']           = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['single']
                        time_list_array['group']            = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['group']
                        time_list_array['total']            = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['single'] + get_staff_data[0]['group']
                        time_list_array['male']             = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['male']
                        time_list_array['female']           = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['female']
                        time_list_array['converted_count']  = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['converted_count']
                        pct                                 = 0
                        if(len(get_staff_data) != 0):
                            converted_count = 0 if (len(get_staff_data) == 0) else (0 if not get_staff_data[0]['converted_count'] else get_staff_data[0]['converted_count'])
                            total_count     = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['single'] + get_staff_data[0]['group']
                            
                            if(total_count != 0):
                                pct         = round(converted_count / total_count * 100)

                        time_list_array['pct']   = pct

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
                        male                    = male +  (0 if not total['male'] else total['male'])
                        female                  = female +  (0 if not total['female'] else total['female'])
                        
                        
                        converted_count         =  converted_count + (0 if not total['converted_count'] else total['converted_count'])
                        conversion_percentage   =  conversion_percentage + total['pct']
                    
                    total_pct                   = 0 if total_count == 0 else round(converted_count / total_count * 100)
                    data_total_sum              = {'time_period' : time_period,'single' : single,'group' :group,'single' :single,'group':group,'total':total_count,'male':male,'female':female,'converted_count':converted_count,'pct':total_pct,'total_rw':True}
                    
                    time_data.append(data_total_sum)

                    staff_list_array                        = {}
                    staff_list_array[staff_data.name,i]     = time_data
                    time_wise_data.append(staff_list_array)

                table_num   = []
                for x in range(len(filter_keys)):
                    table_num.append('tbl'+str(x+1))

                return render(request,'admin/time_wise.html',{'get_data' : time_wise_data,'request_data' : request_data,'staff_list' :staff_list,'branch_list' :branch_list,'zone_list' :zone_list,'window_zone_list':window_zone_list,'clients' :all_clients,'filter_keys':filter_keys,'table_num':table_num})
            
            elif category == 'performance_wise_branch':
                if all_type == 'All':
                    category_type_id                    = branch_tb.objects.all().filter(client_id=client_id).values_list('id',flat=True)

                performance_data                        = []
                for branch in category_type_id:
                    pct                                 = 0
                    converted_count                     = 0
                    total_count                         = 0
                    branch_data                         = branch_tb.objects.all().filter(id=branch).get()
                    get_branch_data                     = customer_tb.objects.all().filter(date__range=(date_from, date_to),branch_id=branch_data.id,status="Completed").values('branch_id').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                    
                    array_data                          = {}
                    array_data['branch']                = branch_data.name
                    array_data['single']                = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single']
                    array_data['group']                 = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['group']
                    array_data['total']                 = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single'] + get_branch_data[0]['group']
                    array_data['converted_count']       = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['converted_count']
                    
                    pct         = 0
                    if(len(get_branch_data) != 0):
                        converted_count = 0 if (len(get_branch_data) == 0) else (0 if not get_branch_data[0]['converted_count'] else get_branch_data[0]['converted_count'])
                        total_count     = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single'] + get_branch_data[0]['group']
                        
                        if(total_count != 0):
                            pct         = round(converted_count / total_count * 100)
                        else:
                            pct         = 0
                    array_data['pct']   = pct
                    
                    performance_data.append(array_data)
                
                performance_data.sort(key=lambda x: x.get('pct'), reverse=True)

                total_count             = 0
                converted_count         = 0
                conversion_percentage   = 0
                total_entry             = len(performance_data)
                total_pct               = 0
                for total in performance_data:
                    total_count             =  total_count + total['total']
                    converted_count         =  converted_count + (0 if not total['converted_count'] else total['converted_count'])
                    conversion_percentage   =  conversion_percentage + total['pct']
                    
                total_pct                   = 0 if total_count == 0 else round(converted_count / total_count * 100)
                data_total_sum              = {'total':total_count,'converted_count':converted_count,'pct':total_pct}
                
                return render(request,'admin/performance_report.html',{'get_data' : performance_data,'data_total_sum':data_total_sum,'request_data' : request_data,'staff_list' :staff_list,'branch_list' :branch_list,'zone_list' :zone_list,'window_zone_list':window_zone_list,'clients' :all_clients})
                    
            elif category == 'performance_wise_staff':
                if all_type == 'All':
                    category_type_id                    = staff_tb.objects.all().filter(client_id=client_id).values_list('id',flat=True)

                get_time_periods                        = time_period_tb.objects.all()

                performance_data                        = []
                for staff in category_type_id:
                    staff_data                          = staff_tb.objects.all().filter(id=staff).get()
                    get_staff_data                      = customer_tb.objects.all().filter(date__range=(date_from, date_to),conversion_to=staff_data.id,status="Completed").values('conversion_to').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                    
                    staff_name                          = staff_data.name
                    branch_name                         = branch_tb.objects.all().filter(id=staff_data.branch_id.id).get()
                    array_data                          = {}
                    array_data['name']                  = staff_data.name
                    array_data['branch']                = branch_name.name
                    array_data['single']                = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['single']
                    array_data['group']                 = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['group']
                    array_data['total']                 = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['single'] + get_staff_data[0]['group']
                    array_data['converted_count']       = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['converted_count']

                    pct         = 0
                    if(len(get_staff_data) != 0):
                        converted_count = 0 if (len(get_staff_data) == 0) else (0 if not get_staff_data[0]['converted_count'] else get_staff_data[0]['converted_count'])
                        total_count     = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['single'] + get_staff_data[0]['group']
                        
                        if(total_count != 0):
                            pct         = round(converted_count / total_count * 100)
                        else:
                            pct         = 0
                    array_data['pct']   = pct
                    performance_data.append(array_data)

                performance_data.sort(key=lambda x: x.get('pct'), reverse=True)

                total_count             = 0
                converted_count         = 0
                conversion_percentage   = 0
                total_entry             = len(performance_data)
                for total in performance_data:
                    total_count             =  total_count + total['total']
                    converted_count         =  converted_count + (0 if not total['converted_count'] else total['converted_count'])
                    conversion_percentage   =  conversion_percentage + total['pct']
                    
                total_pct                   = 0 if total_count == 0 else round(converted_count / total_count * 100)
                data_total_sum              = {'total':total_count,'converted_count':converted_count,'pct':total_pct}
                
                return render(request,'admin/performance_report.html',{'get_data' : performance_data,'data_total_sum':data_total_sum,'request_data' : request_data,'staff_list' :staff_list,'branch_list' :branch_list,'zone_list' :zone_list,'window_zone_list':window_zone_list,'clients' :all_clients})
            ############################################################################################################################################
            #################--- staff attendance report -- #################
            if category == 'staff_attendance':
                if all_type == 'All':
                    category_type_id        = staff_tb.objects.all().filter(client_id=client_id).values_list('id',flat=True)

                staff_attendance_list       = staff_attendance_tb.objects.all().filter(date__range=(date_from, date_to),client_id=client_id,staff_id__in=category_type_id,submit=True,approve=True)
                    

                ################################################################################
                get_detailed_data_list  = []
                i_key                   = 0
                for data in staff_attendance_list:
                    i_key               = i_key + 1
                    staff_name                      = staff_tb.objects.all().filter(id=data.staff_id.id).values('name')

                    my_dict = {}
                    my_dict['id']                   =  data.id
                    my_dict['date']                 =  data.date
                    my_dict['name']                 =  staff_name[0]['name']
                    my_dict['in_time']              =  data.in_time
                    my_dict['out_time']             =  data.out_time
                    my_dict['official_break']       =  data.official_break
                    my_dict['un_official_break']    =  data.un_official_break
                    my_dict['break_hours']          =  data.break_hours
                    my_dict['work_hours']           =  data.work_hours
                    my_dict['over_time']            =  data.over_time
                    my_dict['under_time']           =  data.under_time
                    get_detailed_data_list.append(my_dict)

                
                d = sorted(get_detailed_data_list, key=operator.itemgetter("name"))
                outputList=[]
                for i,g in itertools.groupby(d, key=operator.itemgetter("name")):
                    data_arra   = {}
                    data_arra[i]= list(g)
                    outputList.append(data_arra)


                
                
                get_detailed_data_list  = []
                data_total_sum          = {}
                for attendace in outputList:
                    key     = list(attendace.keys())
                    values  = list(attendace.values())

                    get_all_data    = []
                    for data in values[0]:
                        my_dict = {}
                        my_dict['id']                   =  data['id']
                        my_dict['date']                 =  data['date']
                        my_dict['name']                 =  data['name']
                        my_dict['in_time']              =  data['in_time']
                        my_dict['out_time']             =  data['out_time']
                        my_dict['official_break']       =  data['official_break']
                        my_dict['un_official_break']    =  data['un_official_break']
                        my_dict['break_hours']          =  data['break_hours']
                        my_dict['work_hours']           =  data['work_hours']
                        my_dict['over_time']            =  data['over_time']
                        my_dict['under_time']           =  data['under_time']
                        get_all_data.append(my_dict)
                    
                    get_all_data.sort(key=lambda x: x.get('date'), reverse=False)


                    mysum           = timedelta()
                    work_hours      = timedelta()
                    over_time       = timedelta()
                    under_time      = timedelta()
                    off_br_hours    = timedelta()
                    un_off_br_hours = timedelta()
                    for total in get_all_data:
                        (h, m) = total['break_hours'].split(':')
                        d = timedelta(hours=int(h), minutes=int(m))
                        mysum = d + mysum

                        if total['official_break']:
                            (obh, obm) = total['official_break'].split(':')
                            obd = timedelta(hours=int(obh), minutes=int(obm))
                            off_br_hours = obd + off_br_hours

                        if total['un_official_break']:
                            (ubh, ubm) = total['un_official_break'].split(':')
                            ubd = timedelta(hours=int(ubh), minutes=int(ubm))
                            un_off_br_hours = ubd + un_off_br_hours

                        (wh, wm) = total['work_hours'].split(':')
                        wd = timedelta(hours=int(wh), minutes=int(wm))
                        work_hours = wd + work_hours

                        if total['over_time'] != '0':
                            (oh, om) = total['over_time'].split(':')
                            od = timedelta(hours=int(oh), minutes=int(om))
                            over_time = od + over_time
                        if total['under_time'] != '0':
                            (uh, um) = total['under_time'].split(':')
                            ud = timedelta(hours=int(uh), minutes=int(um))
                            under_time = ud + under_time
                        
                    data_total_sum              = {'date' : '','name' : 'Total','in_time' :'','out_time' :'','official_break':off_br_hours,'un_official_break':un_off_br_hours,'break_hours':mysum,'work_hours':work_hours,'over_time':over_time,'under_time':under_time,'total_rw':True}
                    get_all_data.append(data_total_sum)

                    data_list_array             = {}
                    data_list_array[key[0],i_key]   = get_all_data
                    
                    get_detailed_data_list.append(data_list_array) 
                
                return render(request,'admin/staff_attendance_report.html',{'staff_attendance_list' : get_detailed_data_list,'data_total_sum':data_total_sum,'request_data' : request_data,'staff_list' :staff_list,'branch_list' :branch_list,'zone_list' :zone_list,'window_zone_list':window_zone_list,'clients' :all_clients})
            ####################################################################################################################################################           
            get_distinct_data.sort(key=lambda x: x.get('pct'), reverse=True)
            
            if selected_type == 'consolidated':

                sum_male            = 0
                sum_female          = 0
                total_count         = 0
                sum_single          = 0
                sum_group           = 0
                sum_converted_count = 0
                sum_repeat_cus_count= 0
                
                total_entry         = len(get_distinct_data)
                 
                i                       = 0
                get_distinct_data_list  = []

                for total in get_distinct_data:
                    i                   = i+1
                    total_pct           = 0
                    get_distinct_data_list.append({
                        'key'               : i,
                        'name'              : total['name'] ,
                        'single'            : total['single'],
                        'group'             : total['group'],
                        'total'             : total['total'],
                        'male'              : total['male'],
                        'female'            : total['female'],
                        'converted_count'   : total['converted_count'],
                        'repeat_customer'   : total['repeat_customer'],
                        'repeat_cust_count' : total['repeat_cust_count'],
                        'pct'               : total['pct']
                    })
                    
                    sum_male                = sum_male +  (0 if not total['male'] else total['male'])
                    sum_female              = sum_female +  (0 if not total['female'] else total['female'])
                    total_count             = total_count +  total['total']
                    sum_single              = sum_single + (0 if not total['single'] else total['single'])
                    sum_group               = sum_group + (0 if not total['group'] else total['group'])
                    sum_converted_count     = sum_converted_count + (0 if not total['converted_count'] else total['converted_count'])
                    sum_repeat_cus_count    = sum_repeat_cus_count + (0 if not total['repeat_cust_count'] else total['repeat_cust_count'])
                    # sum_pct                 = round(sum_converted_count / total_count * 100 )
               
                repeat_customer_pct         = round(sum_repeat_cus_count / total_count * 100 )
                total_pct                   = 0 if total_count == 0 else round(sum_converted_count / total_count * 100)
                data_total_sum              = {'sum_male' : sum_male,'sum_female' : sum_female,'total_count' :total_count,'sum_single' :sum_single,'sum_group': sum_group,'sum_converted_count': sum_converted_count,'total_pct':total_pct,'repeat_customer_pct':repeat_customer_pct}
                
                
                return render(request,'admin/consolidated_report.html',{'get_data' : get_distinct_data_list,'length_graph' : len(get_distinct_data),'graph_data' :get_distinct_data[:9],'length' :len(get_distinct_data),'request_data' : request_data,'staff_list' :staff_list,'branch_list' :branch_list,'zone_list' :zone_list,'window_zone_list':window_zone_list,'clients' : all_clients,'data_total_sum' : data_total_sum})
            else:
                get_detailed_data_list  = []
                i                       = 0
                filter_keys             = []

                for get_detailed_data in get_data_list:
                    key     = list(get_detailed_data.keys())
                    values  = list(get_detailed_data.values())
                    
                    get_all_data    = []
                    
                    i               = i + 1
                    filter_keys.append(str(key[0]))
                    
                    for data in values[0]:
                        staff_name                      = staff_tb.objects.all().filter(id=data['conversion_to_id']).values('name')
                        get_ids                         = data['zone_ids'].split(',')
                        zone_names                      = []
                        for zoneid in get_ids:
                            if zoneid:
                                
                                zone                        = zone_tb.objects.all().filter(id=zoneid).values('zone')
                                zone_names.append(zone[0]['zone'])

                        get_win_ids                     = data['window_zone_ids'].split(',')
                        win_zone_names                  = []
                        for winzoneid in get_win_ids:
                            if winzoneid:
                                winzone                     = window_zone_tb.objects.all().filter(id=winzoneid).values('zone')
                                win_zone_names.append(winzone[0]['zone'])

                        my_dict = {}
                        my_dict['date']                 =  data['date']
                        my_dict['customer_entry_time']  =  data['customer_entry_time']
                        my_dict['customer_exit_time']   =  data['customer_exit_time']
                        my_dict['single']               =  (data['single'] == True and 1 or 0)
                        my_dict['group']                =  (data['group'] == True and 1 or 0)
                        my_dict['total']                =  my_dict['single'] + my_dict['group']
                        my_dict['male']                 =  (data['male'] == True and 1 or 0) + (0 if not data['no_of_male'] else data['no_of_male'])
                        my_dict['female']               =  (data['female'] == True and 1 or 0) + (0 if not data['no_of_female'] else data['no_of_female'])
                        my_dict['staff_name']           =  '' if not staff_name else staff_name[0]['name']
                        
                        n = 5  # number of strings to join before adding a dot
                        win_zone_names                  = " ".join(".".join(win_zone_names[i:i+n]) for i in range(0, len(win_zone_names), n))
                        zone_names                      = " ".join(".".join(zone_names[i:i+n]) for i in range(0, len(zone_names), n))

                        my_dict['zone_ids']             =  zone_names
                        my_dict['window_zone_ids']      =  win_zone_names
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
                    
                    get_all_data.sort(key=lambda x: x.get('date'), reverse=False)

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
                    date                    = ''
                    
                    for total in get_all_data:
                        date                    = ''
                        single                  = single + total['single']
                        group                   = group + total['group']
                        total_count             = total_count +  total['total']
                        male                    = male +  total['male']
                        female                  = female +  total['female']
                        
                        converted_count         =  converted_count + (0 if not total['converted_count'] else total['converted_count']) 
                        conversion_percentage   =  conversion_percentage + (0 if not total['conversion_percentage'] else total['conversion_percentage'])
                        
                    total_pct                   = 0 if total_count == 0 else round((converted_count / total_count) * 100)
                    data_total_sum              = {'date' : date,'customer_entry_time' : customer_entry_time,'customer_exit_time' :customer_exit_time,'single' :single,'group':group,'total':total_count,'male':male,'female':female,'staff_name' :staff_name,'zone_ids': zone_ids,'window_zone_ids': window_zone_ids,'dwell_time':dwell_time,'tray' : tray,'refreshment' :refreshment,'gloves':gloves,'backup_stock':backup_stock,'business_card':business_card,'full_uniform' :full_uniform,'conversion_status':conversion_status,'converted_count':converted_count,'conversion_percentage':total_pct,'total_rw':True}
                    get_all_data.append(data_total_sum)

                    data_list_array             = {}
                        
                    data_list_array[key[0],i]   = get_all_data
                    get_detailed_data_list.append(data_list_array) 

                # filter_keys = ','.join(filter_keys)
                
                table_num   = []
                for x in range(len(filter_keys)):
                    table_num.append('tbl'+str(x+1))
                
                return render(request,'admin/detailed_report.html',{'get_data' : get_detailed_data_list,'request_data' : request_data,'staff_list' :staff_list,'branch_list' :branch_list,'zone_list' :zone_list,'window_zone_list':window_zone_list,'clients' :all_clients,'filter_keys':filter_keys,'table_num':table_num})
        else:
            all_clients             = []    
            if request.session.has_key('adminId'):
                all_clients          = client_tb.objects.all()

            elif request.session.has_key('teamLeadertId'):
                team_leader_id      = request.session['teamLeadertId']
                get_all_jobs        = job_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
                client_id           = 0

                for get_client_id in get_all_jobs:
                    client_array= client_tb.objects.all().filter(id=get_client_id['client_id']).get()
                    all_clients.append(client_array)
            
            request_data            = []
            return render(request,'admin/consolidated_report.html',{'request_data' : request_data,'clients':all_clients})

    else:
        return redirect('admin-login')



def getFilterCategory(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId') or request.session.has_key('clientId'):
        get_type        = request.GET['type']
        client_id       = request.GET['client_id']

        if get_type == 'staff' or get_type == 'time_wise_staff' or get_type == 'performance_wise_staff' or get_type == 'staff_attendance':
            get_data                    = staff_tb.objects.all().filter(client_id=client_id).values()
        elif get_type == 'branch' or get_type == 'time_wise_branch' or get_type == 'performance_wise_branch':
            get_data                    = branch_tb.objects.all().filter(client_id=client_id).values()
        elif get_type == 'zone':
            zone_get_data               = zone_tb.objects.all().filter(client_id=client_id).values()
            get_data                    = []
            for data in zone_get_data:
                branch                  = branch_tb.objects.all().filter(id=data['branch_id_id']).get()
                zone_array              = {}
                zone_array['id']        = data['id']
                zone_array['zone']      = data['zone']
                zone_array['branch']    = branch.name
                get_data.append(zone_array)
        elif get_type == 'window_zone':
            zone_get_data               = window_zone_tb.objects.filter(client_id=client_id).all().values()
            get_data                    = []
            for data in zone_get_data:
                branch                  = branch_tb.objects.all().filter(id=data['branch_id_id']).get()
                zone_array              = {}
                zone_array['id']        = data['id']
                zone_array['zone']      = data['zone']
                zone_array['branch']    = branch.name
                get_data.append(zone_array)

        return  JsonResponse({"models_to_return": list(get_data)})
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def adminLogout(request):
    if request.session.has_key('adminId'):
        del request.session['adminId']
        if request.session.has_key('clientId'):
            del request.session['client_id']
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
                        request.session['logged_user_name'] = x.name
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
                        request.session['logged_user_name'] = x.name
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
        
        agent_all_task      = task_tb.objects.all().filter(agent_id=agent_id).values('client_id').distinct()

        get_all_clients     = []
        for task in agent_all_task:
            client_data = client_tb.objects.get(id=task['client_id'])
            get_all_clients.append(client_data)

        if request.session.has_key('client_id'):
            client_id       = request.session['client_id']
            pending_task    = task_tb.objects.all().filter(agent_id=agent_id,client_id=client_id,status='Pending')  
        
        return render(request,'user/agent_dashboard.html',{'pending_task' : pending_task,'all_clients' : get_all_clients,'client_id' : client_id})
    else:
        return redirect('user-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def teamLeaderDashboard(request):
    if request.session.has_key('teamLeadertId'):
        team_leader_id      = request.session['teamLeadertId']

        active_task         = task_tb.objects.all().filter(team_leader_id=team_leader_id,status='Active').count()
        pending_task        = task_tb.objects.all().filter(team_leader_id=team_leader_id,status='Pending').count()
        complete_task       = task_tb.objects.all().filter(team_leader_id=team_leader_id,status='Completed').count()

        task                = [{'active_task' : active_task,'pending_task' : pending_task,'complete_task' : complete_task}]

        active_jobs         = job_tb.objects.all().filter(team_leader_id=team_leader_id,status='On Going').count()
        pending_jobs        = job_tb.objects.all().filter(team_leader_id=team_leader_id,status='Pending').count()
        complete_jobs       = job_tb.objects.all().filter(team_leader_id=team_leader_id,status='Completed').count()

        jobs                = [{'active_jobs' : active_jobs,'pending_jobs' : pending_jobs,'complete_jobs' : complete_jobs}]

        pending_task        = task_tb.objects.all().filter(team_leader_id=team_leader_id,status='Pending')

        pending_jobs        = job_tb.objects.all().filter(team_leader_id=team_leader_id,status='Pending')


        get_all_jobs        = job_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
        get_all_clients     = []
        client_id           = 0
        for job in get_all_jobs:
            client_data = client_tb.objects.get(id=job['client_id'])
            get_all_clients.append(client_data)

        if request.session.has_key('client_id'):
            client_id       = request.session['client_id']
            pending_task    = task_tb.objects.all().filter(team_leader_id=team_leader_id,client_id=client_id,status='Pending')  
        
        return render(request,'user/team_leader_dashboard.html',{'all_task' : task ,'jobs':jobs,'pending_task' : pending_task,'pending_jobs':pending_jobs,'all_clients': get_all_clients,'client_id' :client_id})
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
        if request.session.has_key('clientId'):
            del request.session['client_id']
        userLogout(request)
    if request.session.has_key('teamLeadertId'):
        if request.session.has_key('clientId'):
            del request.session['client_id']
        del request.session['teamLeadertId']
        userLogout(request)
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
                    request.session['logged_user_name']=x.name
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
def clientActivities(request):
    if request.session.has_key('clientId'):
        client_id           = request.session['clientId']

        active_task         = task_tb.objects.all().filter(client_id=client_id,status='Active').count()
        pending_task        = task_tb.objects.all().filter(client_id=client_id,status='Pending').count()
        complete_task       = task_tb.objects.all().filter(client_id=client_id,status='Completed').count()

        task                = [{'active_task' : active_task,'pending_task' : pending_task,'complete_task' : complete_task}]

        active_jobs         = job_tb.objects.all().filter(client_id=client_id,status='On Going').count()
        pending_jobs        = job_tb.objects.all().filter(client_id=client_id,status='Pending').count()
        complete_jobs       = job_tb.objects.all().filter(client_id=client_id,status='Completed').count()

        jobs                = [{'active_jobs' : active_jobs,'pending_jobs' : pending_jobs,'complete_jobs' : complete_jobs}]

        pending_task        = task_tb.objects.all().filter(client_id=client_id,status='Pending')
        
        return render(request,'client/client_activities.html',{'all_task' : task ,'jobs':jobs,'pending_task' : pending_task})
    else:
        return redirect('user-login')      



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def clientDashboard(request):
    if request.session.has_key('clientId'):
        if  request.method=='POST':
            from_date           = request.POST['date_from']
            to_date             = request.POST['date_to']

            client_id           = request.session['clientId']

            get_branch_ids      = branch_tb.objects.all().filter(client_id=client_id)
            number_of_persons   = customer_tb.objects.all().filter(date__range=(from_date, to_date),client_id=client_id).values('client_id').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).distinct()
            
            performance_data                        = []
            key                                     = 0
            for branch in get_branch_ids:
                key                                 = key + 1
                get_branch_data                     = customer_tb.objects.all().filter(date__range=(from_date, to_date),client_id=client_id,branch_id=branch.id).values('branch_id').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()

                array_data                          = {}
                array_data['key']                   = key
                array_data['branch']                = branch.name
                array_data['total']                 = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['count']
                array_data['male']                  = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['male']
                array_data['female']                = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['female']
                array_data['converted_count']       = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['converted_count']
                array_data['pct']                   = 0 if (len(get_branch_data) == 0) else round(get_branch_data[0]['converted_count'] / (get_branch_data[0]['single'] + get_branch_data[0]['group'])* 100)
                
                performance_data.append(array_data)

            get_staff_ids                           = staff_tb.objects.all().filter(client_id=client_id)
            staff_performance_data                  = []
            key                                     = 0
            for staff in get_staff_ids:
                key                                 = key + 1
                get_staff_data                      = customer_tb.objects.all().filter(date__range=(from_date, to_date),client_id=client_id,conversion_to=staff.id).values('conversion_to').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                
                staff_name                          = staff_tb.objects.all().filter(id=staff.id).get()
                branch_name                         = branch_tb.objects.all().filter(id=staff_name.branch_id.id).get()
                staffarray_data                     = {}
                staffarray_data['key']              = key
                staffarray_data['name']             = staff_name.name
                staffarray_data['branch']           = branch_name.name
                staffarray_data['total']            = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['count']
                staffarray_data['converted_count']  = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['converted_count']
                staffarray_data['pct']              = 0 if (len(get_staff_data) == 0) else round(get_staff_data[0]['converted_count'] / (get_staff_data[0]['single'] + get_staff_data[0]['group'])* 100)
                staff_performance_data.append(staffarray_data)

        else:
            from_date           = datetime.now(pytz.timezone('Asia/Dubai')) - timedelta(30)
            to_date             = datetime.now(pytz.timezone('Asia/Dubai'))

            client_id           = request.session['clientId']

            get_branch_ids      = branch_tb.objects.all().filter(client_id=client_id)
            number_of_persons   = customer_tb.objects.all().filter(date__lte=datetime.today(), date__gt=datetime.today()-timedelta(days=30),client_id=client_id).values('client_id').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).distinct()
            
            performance_data                        = []
            key                                     = 0
            for branch in get_branch_ids:
                key                                 = key + 1
                get_branch_data                     = customer_tb.objects.all().filter(date__lte=datetime.today(), date__gt=datetime.today()-timedelta(days=30),client_id=client_id,branch_id=branch.id).values('branch_id').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                
                array_data                          = {}
                array_data['key']                   = key
                array_data['branch']                = branch.name
                array_data['total']                 = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['count']
                array_data['male']                  = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['male']
                array_data['female']                = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['female']
                array_data['converted_count']       = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['converted_count']
                
                converted_count                     = 0 if not array_data['converted_count'] else array_data['converted_count'] 
                array_data['pct']                   = 0 if (len(get_branch_data) == 0) else round(converted_count / (get_branch_data[0]['single'] + get_branch_data[0]['group'])* 100)
                
                performance_data.append(array_data)

            get_staff_ids                           = staff_tb.objects.all().filter(client_id=client_id)
            staff_performance_data                  = []
            key                                     = 0
            for staff in get_staff_ids:
                key                                 = key + 1
                get_staff_data                      = customer_tb.objects.all().filter(date__lte=datetime.today(), date__gt=datetime.today()-timedelta(days=30),client_id=client_id,conversion_to=staff.id).values('conversion_to').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                
                staff_name                          = staff_tb.objects.all().filter(id=staff.id).get()
                branch_name                         = branch_tb.objects.all().filter(id=staff_name.branch_id.id).get()
                staffarray_data                     = {}
                staffarray_data['key']              = key
                staffarray_data['name']             = staff_name.name
                staffarray_data['branch']           = branch_name.name
                staffarray_data['total']            = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['count']
                staffarray_data['converted_count']  = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['converted_count']
                staffarray_data['pct']              = 0 if (len(get_staff_data) == 0) else round(0 if not get_staff_data[0]['converted_count'] else get_staff_data[0]['converted_count'] / (get_staff_data[0]['single'] + get_staff_data[0]['group'])* 100)
                staff_performance_data.append(staffarray_data)

            from_date   = from_date.strftime("%Y-%m-%d")
            to_date     = to_date.strftime("%Y-%m-%d")
        
        staff_performance_data.sort(key=lambda x: x.get('pct'), reverse=True)
        staff_performance_data = staff_performance_data[:20]
        
        return render(request,'client/client_dashboard.html',{'performance_data' : performance_data,'number_of_persons':number_of_persons,'from_date':from_date,'to_date':to_date,'length':len(performance_data),'staff_performance_data':staff_performance_data,'length_graph': len(staff_performance_data)})
    else:
        return redirect('user-login')   



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def clientLogout(request):
    if request.session.has_key('clientId'):
        del request.session['clientId']
        if request.session.has_key('clientId'):
            del request.session['client_id']
        clientLogout(request)
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
            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            a               = task_request_tb(task_id=task_id,remark=remark,team_leader_id=team_leader_id,agent_id=agent_id,created_at=now,updated_at=now)
            a.save()
            

            task_tb.objects.all().filter(id=task_id.id).update(have_request=True,updated_at=now)

            ###########################################################################################
            message             = 'Have new request for edit task'
            getadmin_id         = admin_tb.objects.all().get()
            admin_id            = admin_tb.objects.get(id=getadmin_id.id)
           
            send_notification   = notification_tb(admin_id=admin_id,team_leader_id=team_leader_id,message=message,created_at=now,updated_at=now)
            send_notification.save()


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
            submit_tl       = False if status == True else True #for edit request need to set submit tl false
            task_status     = 'Pending' if status == True else task_id.status
            status_remark   = request.POST['status_remark']

            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            task_request_tb.objects.all().filter(task_id=task_id.id).update(status=status,status_remark=status_remark,updated_at=now)
            task_tb.objects.all().filter(id=task_id.id).update(have_request=False,request_status=get_status,submit_tl=submit_tl,status=task_status,updated_at=now)

            if get_status == 'Approve':
                customer_tb.objects.all().filter(task_id=task_id.id,status="Submitted").update(submit_tl=False,updated_at=now)

            messages.success(request, 'Success.')
            return redirect('list-task')
        else:
            task_id             = request.GET['id']
            request_data        = task_request_tb.objects.all().filter(task_id=task_id)
            agent_list          = agent_tb.objects.all()
            team_leader_list    = team_leader_tb.objects.all()
            
            return render(request,'admin/approve_task_request.html',{'task_id' : task_id ,'request_data' : request_data,'agent_list' : agent_list,'team_leader_list':team_leader_list})
    else:
        return redirect('user-login') 




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def complaintTicket(request):  
    if request.session.has_key('clientId'):
        if  request.method=='POST':
            get_client_id   = request.session['clientId']
            client_id       = client_tb.objects.get(id=get_client_id)
            remark          = request.POST['remark']
            get_task_id     = request.POST['id']
            task_id         = task_tb.objects.get(id=get_task_id)
            agent_id        = task_id.agent_id
            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            get_team_leader = task_tb.objects.filter(client_id=client_id).first()

            a               = complaint_ticket_tb(client_id=client_id,remark=remark,team_leader_id=get_team_leader.team_leader_id,task_id=task_id,agent_id=agent_id,created_at=now,updated_at=now)
            a.save()

            message             = 'Client raise complaint ticket'
            getadmin_id         = admin_tb.objects.all().get()
            admin_id            = admin_tb.objects.get(id=getadmin_id.id)

            send_notification   = notification_tb(admin_id=admin_id,message=message,team_leader_id=get_team_leader.team_leader_id,created_at=now,updated_at=now)
            send_notification.save()

            messages.success(request, 'Success.')
            return redirect('task')
        else:
            client_id       = request.session['clientId']
            task_list       = task_tb.objects.all().filter(client_id=client_id)
            task_id         = request.GET['id']

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
    if request.session.has_key('clientId'):
        client_id      = request.session['clientId']
        all_complaints = complaint_ticket_tb.objects.all().filter(client_id=client_id)

    return render(request,'client/lsit_complaint_ticket.html',{'all_complaints' : all_complaints})



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def editComplaintTicketStatus(request):  
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        if  request.method=='POST':
            complaint_id    = request.POST['id']
            status          = request.POST['status']
            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            complaint_ticket_tb.objects.all().filter(id=complaint_id).update(status=status,updated_at=now)

            if request.session.has_key('teamLeadertId'):
                message             = 'Team Leader '+status+' client complaint ticket' 
                getadmin_id         = admin_tb.objects.all().get()
                admin_id            = admin_tb.objects.get(id=getadmin_id.id)

                send_notification   = notification_tb(admin_id=admin_id,message=message,created_at=now,updated_at=now)
                send_notification.save()

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
            now             = datetime.now(pytz.timezone('Asia/Dubai'))
            actual_end_date = task_id.end_date

            a               = delay_task_request_tb(task_id=task_id,remark=remark,team_leader_id=team_leader_id,agent_id=agent_id,client_id=client_id,actual_end_date=actual_end_date,created_at=now,updated_at=now)
            a.save()

            task_tb.objects.all().filter(id=task_id.id).update(have_delay_request=True,updated_at=now)

            ###########################################################################################
            message             = 'Have new request for late task submission'
            getadmin_id         = admin_tb.objects.all().get()
            admin_id            = admin_tb.objects.get(id=getadmin_id.id)
           
            send_notification   = notification_tb(admin_id=admin_id,team_leader_id=team_leader_id,message=message,created_at=now,updated_at=now)
            send_notification.save()

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
            new_end_time    = request.POST['new_end_time']
            end_date        = new_end_date if get_status == 'Approve' else task_id.end_date
            end_time        = new_end_time if get_status == 'Approve' else task_id.end_time
            status_remark   = request.POST['status_remark']
            
            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            delay_task_request_tb.objects.all().filter(task_id=task_id.id).update(status=status,new_end_date=new_end_date,status_remark=status_remark,updated_at=now)
            task_tb.objects.all().filter(id=task_id.id).update(end_date=end_date,end_time=end_time,have_delay_request=False,request_status=get_status,updated_at=now)


            get_data            = delay_task_request_tb.objects.all().filter(task_id=task_id.id).first()
            agent_id            = get_data.agent_id
            team_leader_id      = get_data.team_leader_id

            message             = 'Admin '+get_status+' the request'
           
            send_notification   = notification_tb(message=message,agent_id=agent_id,team_leader_id=team_leader_id,created_at=now,updated_at=now)
            send_notification.save()

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
        date            = datetime.now(pytz.timezone('Asia/Dubai'))
        time            = date.strftime("%H:%M:%S")
        now             = datetime.now(pytz.timezone('Asia/Dubai'))

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
        time                        = '' if not admin_client_last_msg else admin_client_last_msg.time
        key                         = 1

        list_all_tl                 = [{'key':key,'id':get_admin.id,'name' : 'Admin','user_role' : 'Admin','message':'' if not admin_client_last_msg else admin_client_last_msg.message,'unread':unread_message_count,'time' : time}]

        for team_leader in get_team_leader:
            key                     = key + 1
            tl_name                 = team_leader_tb.objects.all().filter(id=team_leader['team_leader_id']).get()
            tl_client_last_msg      = message_tb.objects.all().filter(client_id=client_id,team_leader_id=team_leader['team_leader_id']).last()
            tl_unread_message_count = message_tb.objects.all().filter(client_id=client_id,team_leader_id=team_leader['team_leader_id'],sender='Team Leader',status='Send').count()
            time                    = '' if not tl_client_last_msg else tl_client_last_msg.time

            tl_array                = {}
            tl_array['key']         = key
            tl_array['id']          = tl_name.id
            tl_array['name']        = tl_name.name
            tl_array['user_role']   = 'Team Leader'
            tl_array['message']     = '' if not tl_client_last_msg else tl_client_last_msg.message
            tl_array['unread']      = tl_unread_message_count
            tl_array['time']        = time

            list_all_tl.append(tl_array)

        list_all_tl.sort(key=lambda x: x.get('time'), reverse=True)
        #############################################################################################
        request_data            = dict(request.GET.items())
        sender_id               = None if not request_data else request.GET['id']
        role                    = None if not request_data else request.GET['role']

        if request_data:
            if role == 'Team Leader':
                get_messages    = message_tb.objects.all().filter(client_id=client_id,team_leader_id=sender_id)
                message_tb.objects.all().filter(client_id=client_id,team_leader_id=sender_id).exclude(sender='Client').update(status='Read')

            elif role == 'Admin':
                get_messages    = message_tb.objects.all().filter(client_id=client_id,admin_id=sender_id)
                message_tb.objects.all().filter(client_id=client_id,admin_id=sender_id).exclude(sender='Client').update(status='Read')
        else:
            get_messages        = [] 

        all_msg                 = []
        for msg in get_messages:
            msg_type                = 'receiver'
            clientname              = client_tb.objects.all().filter(id=client_id).get()
            name                    = clientname.name
            if msg.sender != 'Client':
                msg_type            = 'sender'
                if msg.sender == 'Team Leader':
                    name            = msg.team_leader_id.name
                elif msg.sender == 'Admin':
                    name            = 'Admin'

            msg_array               = {}
            msg_array['message']    = msg.message
            msg_array['msg_type']   = msg_type
            msg_array['name']       = name
            msg_array['time']       = msg.time
            all_msg.append(msg_array)

        return render(request,'client/client_message.html',{'team_leader' : list_all_tl,'sender_id':sender_id,'role':role,'get_messages':all_msg})
    
    elif request.session.has_key('adminId'):
        admin_id                    = request.session['adminId']
        get_team_leader             = team_leader_tb.objects.all()
        get_agent                   = agent_tb.objects.all()
        get_client                  = client_tb.objects.all()

        list_all_tl                 = []
        key                         = 0
        for team_leader in get_team_leader:
            key                     = key + 1
            tl_client_last_msg      = message_tb.objects.all().filter(admin_id=admin_id,team_leader_id=team_leader.id).last()
            tl_unread_message_count = message_tb.objects.all().filter(admin_id=admin_id,team_leader_id=team_leader.id,sender='Team Leader',status='Send').count()
            time                    = '' if not tl_client_last_msg else tl_client_last_msg.time

            tl_array                = {}
            tl_array['key']         = key
            tl_array['id']          = team_leader.id
            tl_array['name']        = team_leader.name
            tl_array['user_role']   = 'Team Leader'
            tl_array['message']     = '' if not tl_client_last_msg else tl_client_last_msg.message
            tl_array['unread']      = tl_unread_message_count
            tl_array['time']        = time

            list_all_tl.append(tl_array)

        for client in get_client:
            key                     = key + 1
            tl_client_last_msg      = message_tb.objects.all().filter(admin_id=admin_id,client_id=client.id).last()
            tl_unread_message_count = message_tb.objects.all().filter(admin_id=admin_id,client_id=client.id,sender='Client',status='Send').count()
            time                    = '' if not tl_client_last_msg else tl_client_last_msg.time

            tl_array                = {}
            tl_array['key']         = key
            tl_array['id']          = client.id
            tl_array['name']        = client.name
            tl_array['user_role']   = 'Client'
            tl_array['message']     = '' if not tl_client_last_msg else tl_client_last_msg.message
            tl_array['unread']      = tl_unread_message_count
            tl_array['time']        = time

            list_all_tl.append(tl_array)

        for agent in get_agent:
            key                     = key + 1
            tl_client_last_msg      = message_tb.objects.all().filter(admin_id=admin_id,agent_id=agent.id).last()
            tl_unread_message_count = message_tb.objects.all().filter(admin_id=admin_id,agent_id=agent.id,sender='Agent',status='Send').count()
            time                    = '' if not tl_client_last_msg else tl_client_last_msg.time

            tl_array                = {}
            tl_array['key']         = key
            tl_array['id']          = agent.id
            tl_array['name']        = agent.name
            tl_array['user_role']   = 'Agent'
            tl_array['message']     = '' if not tl_client_last_msg else tl_client_last_msg.message
            tl_array['unread']      = tl_unread_message_count
            tl_array['time']        = time

            list_all_tl.append(tl_array)

        list_all_tl.sort(key=lambda x: x.get('time'), reverse=True)
        #############################################################################################
        request_data            = dict(request.GET.items())
        sender_id               = None if not request_data else request.GET['id']
        role                    = None if not request_data else request.GET['role']

        if request_data:
            if role == 'Team Leader':
                get_messages    = message_tb.objects.all().filter(admin_id=admin_id,team_leader_id=sender_id)
                message_tb.objects.all().filter(admin_id=admin_id,team_leader_id=sender_id).exclude(sender='Admin').update(status='Read')

            elif role == 'Client':
                get_messages    = message_tb.objects.all().filter(admin_id=admin_id,client_id=sender_id)
                message_tb.objects.all().filter(admin_id=admin_id,client_id=sender_id).exclude(sender='Admin').update(status='Read')
            
            elif role == 'Agent':
                get_messages    = message_tb.objects.all().filter(admin_id=admin_id,agent_id=sender_id)
                message_tb.objects.all().filter(admin_id=admin_id,agent_id=sender_id).exclude(sender='Admin').update(status='Read')
        else:
            get_messages        = [] 

        all_msg                 = []
        for msg in get_messages:
            msg_type                = 'receiver'
            
            name                    = 'Admin'
            if msg.sender != 'Admin':
                msg_type            = 'sender'
                if msg.sender == 'Team Leader':
                    name            = msg.team_leader_id.name
                elif msg.sender == 'Client':
                    name            = msg.client_id.name
                elif msg.sender == 'Agent':
                    name            = msg.agent_id.name

            msg_array               = {}
            msg_array['message']    = msg.message
            msg_array['msg_type']   = msg_type
            msg_array['name']       = name
            msg_array['time']       = msg.time
            all_msg.append(msg_array)

        return render(request,'client/client_message.html',{'team_leader' : list_all_tl,'sender_id':sender_id,'role':role,'get_messages':all_msg})
    
    if request.session.has_key('teamLeadertId'):
        team_leader_id              = request.session['teamLeadertId']
        get_client                  = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
        get_admin                   = admin_tb.objects.all().get()
        get_agent                   = agent_tb.objects.all().filter(team_leader_id=team_leader_id)

        admin_client_last_msg       = message_tb.objects.all().filter(team_leader_id=team_leader_id,admin_id=get_admin.id).last()
        unread_message_count        = message_tb.objects.all().filter(team_leader_id=team_leader_id,admin_id=get_admin.id,sender='Admin',status='Send').count()
        time                        = '' if not admin_client_last_msg else admin_client_last_msg.time
        key                         = 1
        list_all_tl                 = [{'key':key,'id':get_admin.id,'name' : 'Admin','user_role' : 'Admin','message':'' if not admin_client_last_msg else admin_client_last_msg.message,'unread':unread_message_count,'time' : time}]

        for client in get_client:
            key                     = key + 1
            tl_name                 = client_tb.objects.all().filter(id=client['client_id']).get()
            tl_client_last_msg      = message_tb.objects.all().filter(client_id=client['client_id'],team_leader_id=team_leader_id).last()
            tl_unread_message_count = message_tb.objects.all().filter(client_id=client['client_id'],team_leader_id=team_leader_id,sender='Client',status='Send').count()
            time                    = '' if not tl_client_last_msg else tl_client_last_msg.time

            tl_array                = {}
            tl_array['key']         = key
            tl_array['id']          = tl_name.id
            tl_array['name']        = tl_name.name
            tl_array['user_role']   = 'Client'
            tl_array['message']     = '' if not tl_client_last_msg else tl_client_last_msg.message
            tl_array['unread']      = tl_unread_message_count
            tl_array['time']        = time

            list_all_tl.append(tl_array)
        
        for agent in get_agent:
            key                     = key + 1
            tl_client_last_msg      = message_tb.objects.all().filter(team_leader_id=team_leader_id,agent_id=agent.id).last()
            tl_unread_message_count = message_tb.objects.all().filter(team_leader_id=team_leader_id,agent_id=agent.id,sender='Agent',status='Send').count()
            time                    = '' if not tl_client_last_msg else tl_client_last_msg.time

            tl_array                = {}
            tl_array['key']         = key
            tl_array['id']          = agent.id
            tl_array['name']        = agent.name
            tl_array['user_role']   = 'Agent'
            tl_array['message']     = '' if not tl_client_last_msg else tl_client_last_msg.message
            tl_array['unread']      = tl_unread_message_count
            tl_array['time']        = time

            list_all_tl.append(tl_array)

        list_all_tl.sort(key=lambda x: x.get('time'), reverse=True)
        #############################################################################################
        request_data            = dict(request.GET.items())
        sender_id               = None if not request_data else request.GET['id']
        role                    = None if not request_data else request.GET['role']

        if request_data:
            if role == 'Client':
                get_messages    = message_tb.objects.all().filter(client_id=sender_id,team_leader_id=team_leader_id)
                message_tb.objects.all().filter(client_id=sender_id,team_leader_id=team_leader_id).exclude(sender='Team Leader').update(status='Read')

            elif role == 'Admin':
                get_messages    = message_tb.objects.all().filter(team_leader_id=team_leader_id,admin_id=sender_id)
                message_tb.objects.all().filter(team_leader_id=team_leader_id,admin_id=sender_id).exclude(sender='Team Leader').update(status='Read')
            
            elif role == 'Agent':
                get_messages    = message_tb.objects.all().filter(team_leader_id=team_leader_id,agent_id=sender_id)
                message_tb.objects.all().filter(team_leader_id=team_leader_id,agent_id=sender_id).exclude(sender='Team Leader').update(status='Read')
        else:
            get_messages        = [] 

        all_msg                 = []
        for msg in get_messages:
            msg_type                = 'receiver'
            team_leader_name        = team_leader_tb.objects.all().filter(id=team_leader_id).get()
            name                    = team_leader_name.name
            if msg.sender != 'Team Leader':
                msg_type            = 'sender'
                if msg.sender == 'Client':
                    name            = msg.client_id.name
                elif msg.sender == 'Admin':
                    name            = 'Admin'
                elif msg.sender == 'Agent':
                    name            = msg.agent_id.name

            msg_array               = {}
            msg_array['message']    = msg.message
            msg_array['msg_type']   = msg_type
            msg_array['name']       = name
            msg_array['time']       = msg.time
            all_msg.append(msg_array)

        return render(request,'client/client_message.html',{'team_leader' : list_all_tl,'sender_id':sender_id,'role':role,'get_messages':all_msg})
    
    if request.session.has_key('agentId'):
        agent_id                    = request.session['agentId']
        get_agent                   = agent_tb.objects.all().filter(id=agent_id).get()
        get_admin                   = admin_tb.objects.all().get()

        admin_client_last_msg       = message_tb.objects.all().filter(agent_id=agent_id,admin_id=get_admin.id).last()
        unread_message_count        = message_tb.objects.all().filter(agent_id=agent_id,admin_id=get_admin.id,sender='Admin',status='Send').count()
        time                        = '' if not admin_client_last_msg else admin_client_last_msg.time
        key                         = 1
        list_all_tl                 = [{'key':key,'id':get_admin.id,'name' : 'Admin','user_role' : 'Admin','message':'' if not admin_client_last_msg else admin_client_last_msg.message,'unread':unread_message_count,'time' : time}]

        tl_name                     = team_leader_tb.objects.all().filter(id=get_agent.team_leader_id.id).get()
        tl_client_last_msg          = message_tb.objects.all().filter(agent_id=agent_id,team_leader_id=get_agent.team_leader_id).last()
        tl_unread_message_count     = message_tb.objects.all().filter(agent_id=agent_id,team_leader_id=get_agent.team_leader_id,sender='Team Leader',status='Send').count()
        time                        = '' if not tl_client_last_msg else tl_client_last_msg.time

        get_all_tl                  = {'key':key,'id':tl_name.id,'name' : tl_name.name,'user_role' : 'Team Leader','message':'' if not admin_client_last_msg else admin_client_last_msg.message,'unread':unread_message_count,'time' : time}
        list_all_tl.append(get_all_tl)
        

        list_all_tl.sort(key=lambda x: x.get('time'), reverse=True)
        #############################################################################################
        request_data            = dict(request.GET.items())
        sender_id               = None if not request_data else request.GET['id']
        role                    = None if not request_data else request.GET['role']

        if request_data:
            if role == 'Team Leader':
                get_messages    = message_tb.objects.all().filter(agent_id=agent_id,team_leader_id=sender_id)
                message_tb.objects.all().filter(agent_id=agent_id,team_leader_id=sender_id).exclude(sender='Client').update(status='Read')

            elif role == 'Admin':
                get_messages    = message_tb.objects.all().filter(agent_id=agent_id,admin_id=sender_id)
                message_tb.objects.all().filter(agent_id=agent_id,admin_id=sender_id).exclude(sender='Client').update(status='Read')
        else:
            get_messages        = [] 

        all_msg                 = []
        for msg in get_messages:
            msg_type                = 'receiver'
            agentname               = agent_tb.objects.all().filter(id=agent_id).get()
            name                    = agentname.name
            if msg.sender != 'Agent':
                msg_type            = 'sender'
                if msg.sender == 'Team Leader':
                    name            = msg.team_leader_id.name
                elif msg.sender == 'Admin':
                    name            = 'Admin'

            msg_array               = {}
            msg_array['message']    = msg.message
            msg_array['msg_type']   = msg_type
            msg_array['name']       = name
            msg_array['time']       = msg.time
            all_msg.append(msg_array)

        return render(request,'client/client_message.html',{'team_leader' : list_all_tl,'sender_id':sender_id,'role':role,'get_messages':all_msg})
    
    else:
        return redirect('client-login') 




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def clientSendMessage(request):
    if request.session.has_key('clientId'):
        if  request.method=='POST':
            getclient_id    = request.session['clientId']
            client_id       = client_tb.objects.get(id=getclient_id)
            sender_id       = request.POST['sender_id']
            role            = request.POST['role']
            message         = request.POST['message']
            now             = datetime.now(pytz.timezone('Asia/Dubai'))
            time            = now.strftime("%H:%M")
            status          = 'Send'

            if role == 'Team Leader':
                team_leader_id  = team_leader_tb.objects.get(id=sender_id)
                a               = message_tb(date=now,time=time,message=message,client_id=client_id,team_leader_id=team_leader_id,status=status,sender='Client',receiver='Team Leader',created_at=now,updated_at=now)
                a.save()
            elif role == 'Admin':
                admin_id        = admin_tb.objects.get(id=sender_id)
                a               = message_tb(date=now,time=time,message=message,client_id=client_id,admin_id=admin_id,status=status,sender='Client',receiver='Admin',created_at=now,updated_at=now)
                a.save()

            return redirect('/message?id='+str(sender_id)+'&&role='+role)


    if request.session.has_key('adminId'):
        if  request.method=='POST':
            getadmin_id     = request.session['adminId']
            admin_id        = admin_tb.objects.get(id=getadmin_id)
            sender_id       = request.POST['sender_id']
            role            = request.POST['role']
            message         = request.POST['message']
            now             = datetime.now(pytz.timezone('Asia/Dubai'))
            time            = now.strftime("%H:%M")
            status          = 'Send'

            if role == 'Team Leader':
                team_leader_id  = team_leader_tb.objects.get(id=sender_id)
                a               = message_tb(date=now,time=time,message=message,admin_id=admin_id,team_leader_id=team_leader_id,status=status,sender='Admin',receiver='Team Leader',created_at=now,updated_at=now)
                a.save()
            elif role == 'Client':
                client_id       = client_tb.objects.get(id=sender_id)
                a               = message_tb(date=now,time=time,message=message,client_id=client_id,admin_id=admin_id,status=status,sender='Admin',receiver='Client',created_at=now,updated_at=now)
                a.save()
            elif role == 'Agent':
                agent_id        = agent_tb.objects.get(id=sender_id)
                a               = message_tb(date=now,time=time,message=message,agent_id=agent_id,admin_id=admin_id,status=status,sender='Admin',receiver='Agent',created_at=now,updated_at=now)
                a.save()

            return redirect('/message?id='+str(sender_id)+'&&role='+role)

    if request.session.has_key('teamLeadertId'):
        if  request.method=='POST':
            getteam_leader_id       = request.session['teamLeadertId']
            team_leader_id          = team_leader_tb.objects.get(id=getteam_leader_id)
            sender_id               = request.POST['sender_id']
            role                    = request.POST['role']
            message                 = request.POST['message']
            now                     = datetime.now(pytz.timezone('Asia/Dubai'))
            time                    = now.strftime("%H:%M")
            status                  = 'Send'

            if role == 'Admin':
                admin_id        = admin_tb.objects.get(id=sender_id)
                a               = message_tb(date=now,time=time,message=message,admin_id=admin_id,team_leader_id=team_leader_id,status=status,sender='Team Leader',receiver='Admin',created_at=now,updated_at=now)
                a.save()
            elif role == 'Client':
                client_id       = client_tb.objects.get(id=sender_id)
                a               = message_tb(date=now,time=time,message=message,client_id=client_id,team_leader_id=team_leader_id,status=status,sender='Team Leader',receiver='Client',created_at=now,updated_at=now)
                a.save()
            elif role == 'Agent':
                agent_id        = agent_tb.objects.get(id=sender_id)
                a               = message_tb(date=now,time=time,message=message,agent_id=agent_id,team_leader_id=team_leader_id,status=status,sender='Team Leader',receiver='Agent',created_at=now,updated_at=now)
                a.save()

            return redirect('/message?id='+str(sender_id)+'&&role='+role)

    if request.session.has_key('agentId'):
        if  request.method=='POST':
            getagent_id     = request.session['agentId']
            agent_id        = agent_tb.objects.get(id=getagent_id)
            sender_id       = request.POST['sender_id']
            role            = request.POST['role']
            message         = request.POST['message']
            now             = datetime.now(pytz.timezone('Asia/Dubai'))
            time            = now.strftime("%H:%M")
            status          = 'Send'

            if role == 'Team Leader':
                team_leader_id  = team_leader_tb.objects.get(id=sender_id)
                a               = message_tb(date=now,time=time,message=message,agent_id=agent_id,team_leader_id=team_leader_id,status=status,sender='Agent',receiver='Team Leader',created_at=now,updated_at=now)
                a.save()
            elif role == 'Admin':
                admin_id        = admin_tb.objects.get(id=sender_id)
                a               = message_tb(date=now,time=time,message=message,agent_id=agent_id,admin_id=admin_id,status=status,sender='Agent',receiver='Admin',created_at=now,updated_at=now)
                a.save()

            return redirect('/message?id='+str(sender_id)+'&&role='+role)
    else:
        return redirect('client-login') 





@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def importRecord(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        if  request.method=='POST':
            # try:
            gettask_id  = request.POST['task_id']
            task_id     = task_tb.objects.get(id=gettask_id)

            csv_file    = request.FILES["csv_file"]
            csv_form    = csvUpload(request.POST,request.FILES)
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request,'File is not CSV type')
                return redirect('/import?id='+str(gettask_id))
            #if file is too large, return
            if csv_file.multiple_chunks():
                messages.error(request,"Uploaded file is too big (%.2f MB)." % (csv_file.size/(1000*1000),))
                return redirect('/import?id='+str(gettask_id))

            file_data   = csv_file.read().decode("utf-8")       
            
            lines       = file_data.split("\n")
            #loop over the lines and save them in db. If error , store as string and then display
            customer_data   = []
            for line in lines:
                if line:
                    fields                                  = line.split(",")
                    if fields[0]:
                        data_dict                               = {}

                        data_dict["store"]                      = fields[0]
                        data_dict["date"]                       = fields[1]
                        data_dict["customer_id"]                = fields[2]
                        data_dict["staff_name"]                 = fields[3]
                        data_dict["repeat_customer"]            = fields[4]
                        data_dict["repeat_customer_id"]         = fields[5]
                        data_dict["repeat_customer_visit_date"] = fields[6]
                        data_dict["opening_time"]               = fields[7]
                        data_dict["closing_time"]               = fields[8]
                        data_dict["customer_entry_time"]        = fields[9]
                        data_dict["customer_exit_time"]         = fields[10]
                        data_dict["dwell_time"]                 = fields[11]
                        data_dict["single"]                     = fields[12]
                        data_dict["group"]                      = fields[13]
                        data_dict["total_count"]                = fields[14]
                        data_dict["male"]                       = fields[15]
                        data_dict["female"]                     = fields[16]
                        data_dict["zone"]                       = fields[17]
                        data_dict["window_zone"]                = fields[18]
                        data_dict["tray"]                       = fields[19]
                        data_dict["refreshment"]                = fields[20]
                        data_dict["gloves"]                     = fields[21]
                        data_dict["backup_stock"]               = fields[22]
                        data_dict["business_card"]              = fields[23]
                        data_dict["body_language"]              = fields[24]
                        data_dict["full_uniform"]               = fields[25]
                        data_dict["conversion_status"]          = fields[26]
                        data_dict["invoice_time"]               = fields[27]
                        data_dict["conversion_percentage"]      = fields[28]
                        data_dict["remark"]                     = fields[29]

                
                        customer_data.append(data_dict)
            
            customer_data.pop(0)
            for customer in customer_data:
                
                date                        = customer['date']
                opening_time                = customer['opening_time']
                closing_time                = customer['closing_time']
                customer_id                 = customer['customer_id']
                customer_entry_time         = customer['customer_entry_time']
                customer_exit_time          = customer['customer_exit_time']
                dwell_time                  = customer['dwell_time']

                repeat_customer             = False if customer['repeat_customer'] == '0' else True
                repeat_customer_id          = None if customer['repeat_customer_id'] == '0' else customer['repeat_customer_id']

                
                repeat_customer_visit_date  = None if customer['repeat_customer_visit_date'] == '0' else customer['repeat_customer_visit_date']

                single                      = False if customer['single'] == '0' else True
                group                       = False if customer['group'] == '0' else True

                male                        = True if customer['single'] != '0' and customer['male'] != '0' else False
                female                      = True if customer['single'] != '0' and customer['female'] != '0' else False

                store_id                    = branch_tb.objects.all().filter(name=customer['store']).get()

                get_ids                     = customer['zone'].split('.')
                zone_names                  = []
                for zoneid in get_ids:
                    zone                    = zone_tb.objects.all().filter(zone=zoneid,branch_id=store_id.id).values('id')
                    if zone:
                        zone_names.append(str(zone[0]['id']))

                zone_ids                    = ','.join(zone_names)

                get_win_ids                 = customer['window_zone'].split('.')
                win_zone_names              = []
                for winzoneid in get_win_ids:
                    winzone                 = window_zone_tb.objects.all().filter(zone=winzoneid,branch_id=store_id.id).values('id')
                    if winzone:
                        win_zone_names.append(str(winzone[0]['id']))

                window_zone_ids             = ','.join(win_zone_names)

                tray                        = True if customer['tray'] == 'YES' else False
                refreshment                 = True if customer['refreshment'] == 'YES' else False
                gloves                      = True if customer['gloves'] == 'YES' else False
                backup_stock                = True if customer['backup_stock'] == 'YES' else False
                business_card               = True if customer['business_card'] == 'YES' else False
                full_uniform                = True if customer['full_uniform'] == 'YES' else False
                body_language               = True if customer['body_language'] == 'YES' else False
                conversion_status           = True if customer['conversion_status'] == '1' else False

                conversion_percentage       = customer['conversion_percentage'].replace("%","")
                conversion_percentage       = False if conversion_percentage == '0' else conversion_percentage
                converted_count             = 1 if conversion_status == True else 0

                
                invoice_time                = customer['invoice_time']
                no_of_male                  = customer['male'] if customer['group'] != '0' else None
                no_of_female                = customer['female'] if customer['group'] != '0' else None
                remark                      = customer['remark']  

                get_staff_name              = customer['staff_name'].split('.')

                get_conversion_to           = get_staff_name[0].capitalize()
                

                get_staff_id                = staff_tb.objects.all().filter(name=get_conversion_to,branch_id=store_id.id).get()
                conversion_to               = None if get_conversion_to == None else staff_tb.objects.get(id=get_staff_id.id)
                
                staff_names                 = []
                for staffId in get_staff_name:
                    staff                   = staffId.capitalize()
                    getstaff                = staff_tb.objects.all().filter(name=staff).values('id')
                    if getstaff:
                        staff_names.append(str(getstaff[0]['id']))

                all_staff_ids               = ','.join(staff_names)

                agent_id                    = task_id.agent_id
                job_id                      = task_id.job_id
                get_job_data                = job_tb.objects.get(id=job_id.id)
                branch_id                   = task_id.branch_id
                client_id                   = task_id.client_id
                team_leader_id              = task_id.team_leader_id
                reason_for_no_conversion    = None

                now                         = datetime.now(pytz.timezone('Asia/Dubai'))


                if '9:00' <= customer_entry_time < '10:00':
                    time_period_id          = 1
                elif '10:00' <= customer_entry_time < '12:00':
                    time_period_id          = 2
                elif '12:00' <= customer_entry_time < '14:00':
                    time_period_id          = 3
                elif '14:00' <= customer_entry_time < '16:00':
                    time_period_id          = 4
                elif '16:00' <= customer_entry_time < '18:00':
                    time_period_id          = 5
                elif '18:00' <= customer_entry_time < '20:00':
                    time_period_id          = 6
                elif '20:00' <= customer_entry_time < '22:00':
                    time_period_id          = 7
                elif '22:00' <= customer_entry_time < '24:00':
                    time_period_id          = 8
                elif '24:00' <= customer_entry_time < '02:00':
                    time_period_id          = 9

                time_period_id              = time_period_tb.objects.get(id=time_period_id)

                get_customer                = customer_tb.objects.all().filter(task_id=task_id.id).values()

                if(len(get_customer) == 1):
                    job_tb.objects.all().filter(id=job_id.id).update(actual_start_date=now,updated_at=now)
              
                a                           = customer_tb(date=date,opening_time=opening_time,closing_time=closing_time,customer_id=customer_id,customer_entry_time=customer_entry_time,customer_exit_time=customer_exit_time,dwell_time=dwell_time,single=single,group=group,male=male,female=female,zone_ids=zone_ids,window_zone_ids=window_zone_ids,staff_ids=all_staff_ids,repeat_customer=repeat_customer,repeat_customer_id=repeat_customer_id,repeat_customer_visit_date=repeat_customer_visit_date,tray=tray,refreshment=refreshment,gloves=gloves,backup_stock=backup_stock,business_card=business_card,body_language=body_language,full_uniform=full_uniform,conversion_status=conversion_status,conversion_percentage=conversion_percentage,conversion_to=conversion_to,converted_count=converted_count,invoice_time=invoice_time,reason_for_no_conversion=reason_for_no_conversion,remark=remark,task_id=task_id,agent_id=agent_id,job_id=job_id,branch_id=branch_id,no_of_male=no_of_male,no_of_female=no_of_female,client_id=client_id,time_period_id=time_period_id,team_leader_id=team_leader_id,created_at=now,updated_at=now)
                a.save()

            # except Exception as e:
            #     logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
            #     messages.error(request,"Unable to upload file. "+repr(e))

            messages.success(request, 'Success')
            return redirect('/list-customer?id='+ str(task_id.id))
        else:
            task_id     = request.GET['id']
            return render(request,'admin/import_record.html',{'task_id':task_id})
    else:
        return redirect('admin-login') 



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def clientTaskList(request):      
    if request.session.has_key('clientId'):
        client_id       = request.session['clientId']
        task_list       = task_tb.objects.all().filter(client_id=client_id)

        now             = datetime.now(pytz.timezone('Asia/Dubai'))

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
            taskarray['is_expired']         = True if (d2 < d1 and task.status == 'Pending' or d2 < d1 and task.status == 'On Going') else False
            all_task.append(taskarray)

        return render(request,'client/task_list.html',{'task_list':all_task})
    else:
        return redirect('client-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listClientStaffAttendance(request):
    if request.session.has_key('clientId'):
        if  request.method=='POST':
            client_id               = request.session['clientId']
            date_from               = request.POST['date_from']
            date_to                 = request.POST['date_to']
            branch_id               = request.POST['branch_id']
            staff_id                = request.POST['staff_id']
            branch                  = branch_tb.objects.all().filter(client_id=client_id)
            staff_list              = staff_tb.objects.all().filter(branch_id=branch_id)

            staff_attendance_list   = staff_attendance_tb.objects.all().filter(date__range=(date_from, date_to),client_id=client_id,staff_id=staff_id,submit=True,approve=True)
        else:   
            date_from               = None 
            date_to                 = None
            client_id               = request.session['clientId']
            branch_id               = None
            staff_id                = None
            staff_list              = []

            branch                  = branch_tb.objects.all().filter(client_id=client_id)
            staff_attendance_list   = staff_attendance_tb.objects.all().filter(client_id=client_id,submit=True,approve=True)

        get_detailed_data_list  = []
        
        for data in staff_attendance_list:
           
            staff_name                      = staff_tb.objects.all().filter(id=data.staff_id.id).values('name')

            my_dict = {}
            my_dict['id']                   =  data.id
            my_dict['date']                 =  data.date
            my_dict['name']                 =  staff_name[0]['name']
            my_dict['in_time']              =  data.in_time
            my_dict['out_time']             =  data.out_time
            my_dict['official_break']       =  data.official_break
            my_dict['un_official_break']    =  data.un_official_break
            my_dict['break_hours']          =  data.break_hours
            my_dict['work_hours']           =  data.work_hours
            my_dict['over_time']            =  data.over_time
            my_dict['under_time']           =  data.under_time
            get_detailed_data_list.append(my_dict)

        
        d = sorted(get_detailed_data_list, key=operator.itemgetter("name"))
        outputList=[]
        for i,g in itertools.groupby(d, key=operator.itemgetter("name")):
            data_arra   = {}
            data_arra[i]= list(g)
            outputList.append(data_arra)


        
        
        get_detailed_data_list  = []
        data_total_sum          = {}
        for attendace in outputList:
            key     = list(attendace.keys())
            values  = list(attendace.values())

            get_all_data    = []
            for data in values[0]:
                my_dict = {}
                my_dict['id']                   =  data['id']
                my_dict['date']                 =  data['date']
                my_dict['name']                 =  data['name']
                my_dict['in_time']              =  data['in_time']
                my_dict['out_time']             =  data['out_time']
                my_dict['official_break']       =  data['official_break']
                my_dict['un_official_break']    =  data['un_official_break']
                my_dict['break_hours']          =  data['break_hours']
                my_dict['work_hours']           =  data['work_hours']
                my_dict['over_time']            =  data['over_time']
                my_dict['under_time']           =  data['under_time']
                get_all_data.append(my_dict)
            
            get_all_data.sort(key=lambda x: x.get('date'), reverse=False)


            mysum           = timedelta()
            work_hours      = timedelta()
            over_time       = timedelta()
            under_time      = timedelta()
            off_br_hours    = timedelta()
            un_off_br_hours = timedelta()
            for total in get_all_data:
                (h, m) = total['break_hours'].split(':')
                d = timedelta(hours=int(h), minutes=int(m))
                mysum = d + mysum

                if total['official_break']:
                    (obh, obm) = total['official_break'].split(':')
                    obd = timedelta(hours=int(obh), minutes=int(obm))
                    off_br_hours = obd + off_br_hours

                if total['un_official_break']:
                    (ubh, ubm) = total['un_official_break'].split(':')
                    ubd = timedelta(hours=int(ubh), minutes=int(ubm))
                    un_off_br_hours = ubd + un_off_br_hours

                (wh, wm) = total['work_hours'].split(':')
                wd = timedelta(hours=int(wh), minutes=int(wm))
                work_hours = wd + work_hours

                if total['over_time'] != '0':
                    (oh, om) = total['over_time'].split(':')
                    od = timedelta(hours=int(oh), minutes=int(om))
                    over_time = od + over_time
                if total['under_time'] != '0':
                    (uh, um) = total['under_time'].split(':')
                    ud = timedelta(hours=int(uh), minutes=int(um))
                    under_time = ud + under_time
                
            data_total_sum              = {'date' : '','name' : 'Total','in_time' :'','out_time' :'','official_break':off_br_hours,'un_official_break':un_off_br_hours,'break_hours':mysum,'work_hours':work_hours,'over_time':over_time,'under_time':under_time}
            get_all_data.append(data_total_sum)

            data_list_array             = {}
            data_list_array[key[0]]     = get_all_data
            get_detailed_data_list.append(data_list_array) 

        
        return render(request,'client/list_staff_attendance.html',{'staff_attendance_list' : get_detailed_data_list,'date_from':date_from,'date_to':date_to,'branch':branch,'branch_id':branch_id,'staff_id':staff_id,'staff_list':staff_list})  
    else:
        return redirect('user-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def searchClientStaffAttendance(request):
    if request.session.has_key('clientId'):
        if  request.method=='POST':
            client_id               = request.session['clientId']
            search_key              = request.POST['search']
            branch                  = branch_tb.objects.all().filter(client_id=client_id)

            staff_list              = staff_tb.objects.all().filter(name__icontains=search_key,client_id=client_id)

            staff_attendance_list   = []
            for staff in staff_list:

                get_attendance_list = staff_attendance_tb.objects.all().filter(staff_id=staff.id,client_id=client_id,submit=True,approve=True).order_by('-id')

                for attendace in get_attendance_list:
                    staff_attendance_list.append({
                        'id'                : attendace.id,
                        'date'              : attendace.date,
                        'client_id'         : attendace.client_id,
                        'staff_id'          : attendace.staff_id,
                        'in_time'           : attendace.in_time,
                        'out_time'          : attendace.out_time,
                        'official_break'    : attendace.official_break,
                        'un_official_break' : attendace.un_official_break,
                        'break_hours'       : attendace.break_hours,
                        'work_hours'        : attendace.work_hours,
                        'over_time'         : attendace.over_time,
                        'under_time'        : attendace.under_time,
                        'submit'            : attendace.submit
                    })


            get_detailed_data_list  = []
            print(staff_attendance_list)
            for data in staff_attendance_list:
                staff_name                      = staff_tb.objects.all().filter(id=data['staff_id'].id).values('name')

                my_dict = {}
                my_dict['id']                   =  data['id']
                my_dict['date']                 =  data['date']
                my_dict['name']                 =  staff_name[0]['name']
                my_dict['in_time']              =  data['in_time']
                my_dict['out_time']             =  data['out_time']
                my_dict['official_break']       =  data['official_break']
                my_dict['un_official_break']    =  data['un_official_break']
                my_dict['break_hours']          =  data['break_hours']
                my_dict['work_hours']           =  data['work_hours']
                my_dict['over_time']            =  data['over_time']
                my_dict['under_time']           =  data['under_time']
                get_detailed_data_list.append(my_dict)

            
            d = sorted(get_detailed_data_list, key=operator.itemgetter("name"))
            outputList=[]
            for i,g in itertools.groupby(d, key=operator.itemgetter("name")):
                data_arra   = {}
                data_arra[i]= list(g)
                outputList.append(data_arra)


            
            
            get_detailed_data_list  = []
            for attendace in outputList:
                key     = list(attendace.keys())
                values  = list(attendace.values())

                get_all_data    = []
                for data in values[0]:
                    my_dict = {}
                    my_dict['id']                   =  data['id']
                    my_dict['date']                 =  data['date']
                    my_dict['name']                 =  data['name']
                    my_dict['in_time']              =  data['in_time']
                    my_dict['out_time']             =  data['out_time']
                    my_dict['official_break']       =  data['official_break']
                    my_dict['un_official_break']    =  data['un_official_break']
                    my_dict['break_hours']          =  data['break_hours']
                    my_dict['work_hours']           =  data['work_hours']
                    my_dict['over_time']            =  data['over_time']
                    my_dict['under_time']           =  data['under_time']
                    get_all_data.append(my_dict)
                
                get_all_data.sort(key=lambda x: x.get('date'), reverse=False)


                mysum           = timedelta()
                work_hours      = timedelta()
                over_time       = timedelta()
                under_time      = timedelta()
                off_br_hours    = timedelta()
                un_off_br_hours = timedelta()
                for total in get_all_data:
                    (h, m) = total['break_hours'].split(':')
                    d = timedelta(hours=int(h), minutes=int(m))
                    mysum = d + mysum

                    if total['official_break']:
                        (obh, obm) = total['official_break'].split(':')
                        obd = timedelta(hours=int(obh), minutes=int(obm))
                        off_br_hours = obd + off_br_hours

                    if total['un_official_break']:
                        (ubh, ubm) = total['un_official_break'].split(':')
                        ubd = timedelta(hours=int(ubh), minutes=int(ubm))
                        un_off_br_hours = ubd + un_off_br_hours

                    (wh, wm) = total['work_hours'].split(':')
                    wd = timedelta(hours=int(wh), minutes=int(wm))
                    work_hours = wd + work_hours

                    if total['over_time'] != '0':
                        (oh, om) = total['over_time'].split(':')
                        od = timedelta(hours=int(oh), minutes=int(om))
                        over_time = od + over_time
                    if total['under_time'] != '0':
                        (uh, um) = total['under_time'].split(':')
                        ud = timedelta(hours=int(uh), minutes=int(um))
                        under_time = ud + under_time
                    
                data_total_sum              = {'date' : '','name' : 'Total','in_time' :'','out_time' :'','official_break':off_br_hours,'un_official_break':un_off_br_hours,'break_hours':mysum,'work_hours':work_hours,'over_time':over_time,'under_time':under_time}
                get_all_data.append(data_total_sum)

                data_list_array             = {}
                data_list_array[key[0]]     = get_all_data
                get_detailed_data_list.append(data_list_array) 
            
            return render(request,'client/list_staff_attendance.html',{'staff_attendance_list' : get_detailed_data_list,'branch':branch,'search_key':search_key})  
        else:
            return redirect('attendance')
    else:
        return redirect('user-login')




def getClientBranch(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        
        client_id       = request.GET['client_id']

        get_data        = branch_tb.objects.all().filter(client_id=client_id).values()
        
        return  JsonResponse({"models_to_return": list(get_data)})
    else:
        return redirect('admin-login')



def getComplaintTicketFilterType(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        get_type       = request.GET['type']

        if get_type == 'client':
            if request.session.has_key('teamLeadertId'):
                team_leader_id          = request.session['teamLeadertId']
                get_all_clients         = complaint_ticket_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
            
            elif request.session.has_key('adminId'):
                get_all_clients         = complaint_ticket_tb.objects.all().values('client_id').distinct()

            get_list                    = []
            for get_client_id in get_all_clients:
                client_data             = client_tb.objects.all().filter(id=get_client_id['client_id']).get()
                client_array            = {}
                client_array['id']      = client_data.id
                client_array['name']    = client_data.name
                get_list.append(client_array)

        elif get_type == 'agent': 
            if request.session.has_key('teamLeadertId'):
                team_leader_id              = request.session['teamLeadertId']
                get_all_agent               = complaint_ticket_tb.objects.all().filter(team_leader_id=team_leader_id).values('agent_id').distinct()
            elif request.session.has_key('adminId'):
                get_all_agent               = complaint_ticket_tb.objects.all().values('agent_id').distinct()

            get_list                    = []
            for get_agent_id in get_all_agent:
                agent_data              = agent_tb.objects.all().filter(id=get_agent_id['agent_id']).get()
                agent_array             = {}
                agent_array['id']       = agent_data.id
                agent_array['name']     = agent_data.name
                get_list.append(agent_array)


        return  JsonResponse({"models_to_return": list(get_list)})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def filtercomplaintTicket(request):  
    if  request.method=='POST':
        get_type       = request.POST['type']
        get_id         = request.POST['id']

        if request.session.has_key('adminId'):
            if get_type == 'client':
                get_all_clients             = complaint_ticket_tb.objects.all().values('client_id').distinct()
                get_list                    = []
                for get_client_id in get_all_clients:
                    client_data             = client_tb.objects.all().filter(id=get_client_id['client_id']).get()
                    client_array            = {}
                    client_array['id']      = client_data.id
                    client_array['name']    = client_data.name
                    get_list.append(client_array)

                all_complaints              = complaint_ticket_tb.objects.all().filter(client_id=get_id)
                
            elif get_type == 'agent':
                get_all_agent               = complaint_ticket_tb.objects.all().values('agent_id').distinct()
                get_list                    = []
                for get_agent_id in get_all_agent:
                    agent_data              = agent_tb.objects.all().filter(id=get_agent_id['agent_id']).get()
                    agent_array             = {}
                    agent_array['id']       = agent_data.id
                    agent_array['name']     = agent_data.name
                    get_list.append(agent_array)

                all_complaints              = complaint_ticket_tb.objects.all().filter(agent_id=get_id)
        if request.session.has_key('teamLeadertId'):
            team_leader_id                  = request.session['teamLeadertId']
            if get_type == 'client':
                get_all_clients             = complaint_ticket_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
                get_list                    = []
                for get_client_id in get_all_clients:
                    client_data             = client_tb.objects.all().filter(id=get_client_id['client_id']).get()
                    client_array            = {}
                    client_array['id']      = client_data.id
                    client_array['name']    = client_data.name
                    get_list.append(client_array)

                all_complaints              = complaint_ticket_tb.objects.all().filter(team_leader_id=team_leader_id,client_id=get_id)

            elif get_type == 'agent':
                get_all_agent               = complaint_ticket_tb.objects.all().filter(team_leader_id=team_leader_id).values('agent_id').distinct()
                get_list                    = []
                for get_agent_id in get_all_agent:
                    agent_data              = agent_tb.objects.all().filter(id=get_agent_id['agent_id']).get()
                    agent_array             = {}
                    agent_array['id']       = agent_data.id
                    agent_array['name']     = agent_data.name
                    get_list.append(agent_array)

                all_complaints      = complaint_ticket_tb.objects.all().filter(team_leader_id=team_leader_id,agent_id=get_id)

    return render(request,'client/lsit_complaint_ticket.html',{'all_complaints' : all_complaints,'get_type':get_type,'get_list':get_list,'get_id':get_id})


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def completeJob(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        job_id          = request.GET['id']
      
        return render(request,'admin/complete_job_send_mail.html',{'job_id':job_id})
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def completeJobSendMail(request):
    if request.session.has_key('adminId') or  request.session.has_key('teamLeadertId'):
        job_id          = request.POST['job_id']
        date_from       = request.POST['date_from']
        date_to         = request.POST['date_to']

        getjob_id       = job_tb.objects.all().filter(id=job_id).values()
        now             = datetime.now(pytz.timezone('Asia/Dubai'))
       
        job_tb.objects.all().filter(id=job_id).update(status='Completed',actual_end_date=now,updated_at=now)
        task_tb.objects.all().filter(job_id=job_id).update(status='Completed',updated_at=now)
        

        ##########################################################################################
        client_id           = getjob_id[0]['client_id_id']
        client_email_data   = client_tb.objects.all().filter(id=client_id).get()
        email               = client_email_data.email
        logo                = client_email_data.logo
      
        get_branch_ids      = task_tb.objects.all().filter(job_id=job_id).values('branch_id').distinct()
            
        ##########################################################################################    
        key                                     = 0
        converted_count                         = 0
        total_count                             = 0
        pct                                     = 0
        performance_data                        = []
        for branch in get_branch_ids:
            get_branch_data                     = customer_tb.objects.all().filter(date__range=(date_from, date_to),branch_id=branch['branch_id'],job_id=job_id,status="Completed").values('branch_id').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
            branch_data                         = branch_tb.objects.all().filter(id=branch['branch_id']).get()
            
            array_data                          = {}
            array_data['branch']                = branch_data.name
            array_data['total']                 = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single'] + get_branch_data[0]['group']
            array_data['converted_count']       = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['converted_count']

            if(len(get_branch_data) != 0):
                converted_count = 0 if (len(get_branch_data) == 0) else (0 if not get_branch_data[0]['converted_count'] else get_branch_data[0]['converted_count'])
                total_count     = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single'] + get_branch_data[0]['group']
                
                if(total_count != 0):
                    pct         = round(converted_count / total_count * 100)
                else:
                    pct         = 0
            array_data['pct']   = pct
            
            performance_data.append(array_data)

        performance_data.sort(key=lambda x: x.get('pct'), reverse=True)

        total_count             = 0
        converted_count         = 0
        conversion_percentage   = 0
        total_entry             = len(performance_data)
        for total in performance_data:
            total_count             =  total_count + total['total']
            converted_count         =  converted_count + (0 if not total['converted_count'] else total['converted_count'])
            conversion_percentage   =  conversion_percentage + total['pct']
            
        total_pct                   = 0 if total_count == 0 else round(converted_count / total_count * 100)
        data_total_sum              = {'branch':'Total','total':total_count,'converted_count':converted_count,'pct':total_pct}
        performance_data.append(data_total_sum)
        
        ##########################################################################################
        get_time_periods            = time_period_tb.objects.all()

        time_wise_data              = []
        filter_keys                 = []
        i                           = 0   
        for branch in get_branch_ids:
            branch_data             = branch_tb.objects.all().filter(id=branch['branch_id']).get()

            filter_keys.append(branch_data.name)
            i                       = i + 1
            time_data               = []
            for time in get_time_periods:
                get_branch_data                     = customer_tb.objects.all().filter(date__range=(date_from, date_to),branch_id=branch_data.id,time_period_id=time.id,status="Completed",job_id=job_id).values('branch_id').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                time_list_array                     = {}

                time_list_array['time_period']      = time.period
                time_list_array['single']           = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single']
                time_list_array['group']            = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['group']
                time_list_array['total']            = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single'] + get_branch_data[0]['group']
                time_list_array['male']             = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['male']
                time_list_array['female']           = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['female']
                time_list_array['converted_count']  = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['converted_count']
                
                if(len(get_branch_data) != 0):
                    converted_count = 0 if (len(get_branch_data) == 0) else (0 if not get_branch_data[0]['converted_count'] else get_branch_data[0]['converted_count'])
                    total_count     = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single'] + get_branch_data[0]['group']
                    
                    if(total_count != 0):
                        pct         = round(converted_count / total_count * 100)
                    else:
                        pct         = 0
                time_list_array['pct']   = pct

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
                
                converted_count         =  converted_count + (0 if not total['converted_count'] else total['converted_count'])
                conversion_percentage   =  conversion_percentage + total['pct']
                
            total_pct                   = 0 if total_count == 0 else round(converted_count / total_count * 100)
            data_total_sum              = {'time_period' : time_period,'single' : single,'group' :group,'single' :single,'group':group,'total':total_count,'male':male,'female':female,'converted_count':converted_count,'pct':total_pct,'total_rw':True}
            time_data.append(data_total_sum)

            branch_list_array                       = {}
            branch_list_array[branch_data.name,i]   = time_data
            time_wise_data.append(branch_list_array)
        
        ##########################################################################################
        # split_actual_start_date = [] if not getjob_id[0]['actual_start_date'] else getjob_id[0]['actual_start_date'].split(' ')
        # split_actual_end_date   = [] if not getjob_id[0]['actual_end_date'] else getjob_id[0]['actual_end_date'].split(' ')
        
        # job_actual_start_date   = '' if not split_actual_start_date else datetime.strptime(split_actual_start_date[0], "%Y-%m-%d").strftime("%b %d, %Y")
        # job_actual_end_date     = '' if not split_actual_end_date else datetime.strptime(split_actual_end_date[0], "%Y-%m-%d").strftime("%b %d, %Y")
        
        job_actual_start_date   = datetime.strptime(date_from, "%Y-%m-%d").strftime("%b %d, %Y")
        job_actual_end_date     = datetime.strptime(date_to, "%Y-%m-%d").strftime("%b %d, %Y")

        url                     = request.build_absolute_uri('/')

        ##########################################################################################
        list_data               = {'logo' : logo,'performance_data' : performance_data ,'time_wise_data':time_wise_data,'job_actual_start_date':job_actual_start_date,'job_actual_end_date':job_actual_end_date,'url':url}
        

        completeJobSendEmail(email,'email/complete_job.html',list_data)
        messages.success(request, getjob_id[0]['job_id']+' ' + 'Completed Successfully .')
        return redirect('list-jobs')      
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateNotificationSeen(request):
    if request.session.has_key('adminId'):
        admin_id        = request.session['adminId']
        now             = datetime.now(pytz.timezone('Asia/Dubai'))
        notification_tb.objects.all().filter(admin_id=admin_id).update(admin_seen=True,updated_at=now)

    elif request.session.has_key('teamLeadertId'):
        team_leader_id  = request.session['teamLeadertId']
        now             = datetime.now(pytz.timezone('Asia/Dubai'))
        notification_tb.objects.all().filter(team_leader_id=team_leader_id).update(team_leader_seen=True,updated_at=now)
    
    elif request.session.has_key('agentId'):
        agent_id        = request.session['agentId']
        now             = datetime.now(pytz.timezone('Asia/Dubai'))
        notification_tb.objects.all().filter(agent_id=agent_id).update(agent_seen=True,updated_at=now)
    
    elif request.session.has_key('clientId'):
        client_id       = request.session['clientId']
        now             = datetime.now(pytz.timezone('Asia/Dubai'))
        notification_tb.objects.all().filter(client_id=client_id).update(client_seen=True,updated_at=now)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def delayRequestHistory(request):  
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId') or request.session.has_key('agentId'):
        if  request.method=='POST':
            get_type       = request.POST['type']
            get_id         = request.POST['id']

            if request.session.has_key('adminId'):
                if get_type == 'agent':
                    get_all_data                = delay_task_request_tb.objects.all().filter(agent_id=get_id).order_by('-id')

                    get_all_agent               = delay_task_request_tb.objects.all().values('agent_id').distinct()
                    get_list                    = []
                    for get_agent_id in get_all_agent:
                        agent_data              = agent_tb.objects.all().filter(id=get_agent_id['agent_id']).get()
                        agent_array             = {}
                        agent_array['id']       = agent_data.id
                        agent_array['name']     = agent_data.name
                        get_list.append(agent_array)

            elif request.session.has_key('teamLeadertId'):
                if get_type == 'agent':
                    team_leader_id              = request.session['teamLeadertId']
                    get_all_data                = delay_task_request_tb.objects.all().filter(team_leader_id=team_leader_id,agent_id=get_id).order_by('-id')

                    get_all_agent               = delay_task_request_tb.objects.all().filter(team_leader_id=team_leader_id).values('agent_id').distinct()
                    get_list                    = []
                    for get_agent_id in get_all_agent:
                        agent_data              = agent_tb.objects.all().filter(id=get_agent_id['agent_id']).get()
                        agent_array             = {}
                        agent_array['id']       = agent_data.id
                        agent_array['name']     = agent_data.name
                        get_list.append(agent_array)
        else:
            get_type       = None
            get_id         = None

            if request.session.has_key('adminId'):
                get_all_data                = delay_task_request_tb.objects.all().order_by('-id')
                
                get_all_agent               = delay_task_request_tb.objects.all().values('agent_id').distinct()
                get_list                    = []
                for get_agent_id in get_all_agent:
                    agent_data              = agent_tb.objects.all().filter(id=get_agent_id['agent_id']).get()
                    agent_array             = {}
                    agent_array['id']       = agent_data.id
                    agent_array['name']     = agent_data.name
                    get_list.append(agent_array)

            elif request.session.has_key('teamLeadertId'):
                team_leader_id              = request.session['teamLeadertId']
                get_all_data                = delay_task_request_tb.objects.all().filter(team_leader_id=team_leader_id).order_by('-id')

                get_all_agent               = delay_task_request_tb.objects.all().filter(team_leader_id=team_leader_id).values('agent_id').distinct()
                get_list                    = []
                for get_agent_id in get_all_agent:
                    agent_data              = agent_tb.objects.all().filter(id=get_agent_id['agent_id']).get()
                    agent_array             = {}
                    agent_array['id']       = agent_data.id
                    agent_array['name']     = agent_data.name
                    get_list.append(agent_array)

            elif request.session.has_key('agentId'):
                get_list        = []
                agent_id        = request.session['agentId']
                get_all_data    = delay_task_request_tb.objects.all().filter(agent_id=agent_id).order_by('-id')

        return render(request,'admin/delay_request_history.html',{'get_all_data' : get_all_data,'get_list':get_list,'get_type':get_type,'get_id':get_id})
    else:
        return redirect('user-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def editRequestHistory(request):  
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId') or request.session.has_key('agentId'):
        if  request.method=='POST':
            get_type       = request.POST['type']
            get_id         = request.POST['id']

            if request.session.has_key('adminId'):
                if get_type == 'agent':
                    get_all_data                = task_request_tb.objects.all().filter(agent_id=get_id).order_by('-id')

                    get_all_agent               = task_request_tb.objects.all().values('agent_id').distinct()
                    get_list                    = []
                    for get_agent_id in get_all_agent:
                        agent_data              = agent_tb.objects.all().filter(id=get_agent_id['agent_id']).get()
                        agent_array             = {}
                        agent_array['id']       = agent_data.id
                        agent_array['name']     = agent_data.name
                        get_list.append(agent_array)

            elif request.session.has_key('teamLeadertId'):
                if get_type == 'agent':
                    team_leader_id              = request.session['teamLeadertId']
                    get_all_data                = task_request_tb.objects.all().filter(team_leader_id=team_leader_id,agent_id=get_id).order_by('-id')

                    get_all_agent               = task_request_tb.objects.all().filter(team_leader_id=team_leader_id).values('agent_id').distinct()
                    get_list                    = []
                    for get_agent_id in get_all_agent:
                        agent_data              = agent_tb.objects.all().filter(id=get_agent_id['agent_id']).get()
                        agent_array             = {}
                        agent_array['id']       = agent_data.id
                        agent_array['name']     = agent_data.name
                        get_list.append(agent_array)
        else:
            get_type       = None
            get_id         = None

            if request.session.has_key('adminId'):
                get_all_data                = task_request_tb.objects.all().order_by('-id')
                
                get_all_agent               = task_request_tb.objects.all().values('agent_id').distinct()
                get_list                    = []
                for get_agent_id in get_all_agent:
                    agent_data              = agent_tb.objects.all().filter(id=get_agent_id['agent_id']).get()
                    agent_array             = {}
                    agent_array['id']       = agent_data.id
                    agent_array['name']     = agent_data.name
                    get_list.append(agent_array)

            elif request.session.has_key('teamLeadertId'):
                team_leader_id              = request.session['teamLeadertId']
                get_all_data                = task_request_tb.objects.all().filter(team_leader_id=team_leader_id).order_by('-id')

                get_all_agent               = task_request_tb.objects.all().filter(team_leader_id=team_leader_id).values('agent_id').distinct()
                get_list                    = []
                for get_agent_id in get_all_agent:
                    agent_data              = agent_tb.objects.all().filter(id=get_agent_id['agent_id']).get()
                    agent_array             = {}
                    agent_array['id']       = agent_data.id
                    agent_array['name']     = agent_data.name
                    get_list.append(agent_array)

            elif request.session.has_key('agentId'):
                get_list        = []
                agent_id        = request.session['agentId']
                get_all_data    = task_request_tb.objects.all().filter(agent_id=agent_id).order_by('-id')

        return render(request,'admin/edit_request_history.html',{'get_all_data' : get_all_data,'get_list':get_list,'get_type':get_type,'get_id':get_id})
    else:
        return redirect('user-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listClientWiseStaff(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId') or request.session.has_key('agentId'):
        task_id                     = request.GET['id']
        gettask_id                  = task_tb.objects.get(id=task_id)
        get_branch_image            = gettask_id.branch_id.layout
        client_id                   = gettask_id.client_id.id

        staff_list  = staff_tb.objects.all().filter(client_id=client_id)
        return render(request,'client/list_staff.html',{'staff_list' : staff_list,'task_id':task_id})
    else:
        return redirect('admin-login')



def getFilterBranchStaff(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId') or request.session.has_key('clientId'):
        branch_id   = request.GET['branch_id']

        get_data    = staff_tb.objects.all().filter(branch_id=branch_id).values()

        return  JsonResponse({"models_to_return": list(get_data)})
    else:
        return redirect('admin-login')


def getFilterClientBranch(request):
    if request.session.has_key('adminId'):
        client_id   = request.GET['client_id']

        get_data    = branch_tb.objects.all().filter(client_id=client_id).values()

        return  JsonResponse({"models_to_return": list(get_data)})
    else:
        return redirect('admin-login')




def getRepeatCustomerId(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId') or request.session.has_key('agentId'):
        date            = request.GET['date']
        branch_id       = request.GET['branch_id']

        # time_str        = '00:00:00'
        # datetime_str    = f'{date} {time_str}'
        # date_obj        = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

        # # add UTC timezone to datetime object
        # date_obj_utc    = date_obj.replace(tzinfo=timezone.utc)
        # # convert datetime object to string with timezone offset
        # date_str_utc    = date_obj_utc.strftime('%Y-%m-%d %H:%M:%S%z')

        
        get_data        = customer_tb.objects.all().filter(date__exact=date,branch_id=branch_id).values('id')
        
        return  JsonResponse({"models_to_return": list(get_data)})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def sendJobWiseMailApprovedTaskToBranch(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        job_id          = request.GET['job_id']
        get_job_data    = job_tb.objects.all().filter(id=job_id).get()
        get_client_data = client_tb.objects.all().filter(id=get_job_data.client_id.id).get()
        get_branch_ids  = task_tb.objects.all().filter(job_id=job_id,status='Approved').values('branch_id').distinct()
        branch_list     = []
        for branch in get_branch_ids: 
            get_branch  = branch_tb.objects.all().filter(id=branch['branch_id']).get()
            branch_list.append(get_branch)
      
        return render(request,'admin/send_branch_wise_email_confirm.html',{'client_data' : get_client_data,'branch_list':branch_list,'job_id':job_id})
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def sendJobWiseMailApprovedTask(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId'):
        job_id                      = request.POST['job_id']
        date_from                   = request.POST['date_from']
        date_to                     = request.POST['date_to']
        get_branch_ids              = request.POST.getlist('branch_id[]')

        # get_max_date                = task_tb.objects.all().filter(job_id=job_id,status='Approved').latest('updated_at')
        # get_min_date                = task_tb.objects.all().filter(job_id=job_id,status='Approved').order_by('updated_at')[0]
        # date_from                   = get_max_date.updated_at
        # date_to                     = get_min_date.updated_at
       
        job_actual_start_date       = datetime.strptime(date_from, "%Y-%m-%d").strftime("%b %d, %Y")
        job_actual_end_date         = datetime.strptime(date_to, "%Y-%m-%d").strftime("%b %d, %Y")
        

        
        # get_branch_ids              = task_tb.objects.all().filter(job_id=job_id,status='Approved').values('branch_id').distinct()

        #######################################################################################################################
        getjob_id           = job_tb.objects.all().filter(id=job_id).values()
        client_id           = getjob_id[0]['client_id_id']
        client_email_data   = client_tb.objects.all().filter(id=client_id).get()
        logo                = client_email_data.logo

        ###################### Time Wise ###############################################################################
        get_time_periods            = time_period_tb.objects.all()

        time_wise_data              = []
        for branch in get_branch_ids:
            branch_data             = branch_tb.objects.all().filter(id=branch).get()

            time_data               = []

            for time in get_time_periods:
                get_branch_data     = customer_tb.objects.all().filter(date__range=(date_from, date_to),branch_id=branch,time_period_id=time.id,status="Completed",job_id=job_id).values('branch_id').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                time_list_array                     = {}

                time_list_array['time_period']      = time.period
                time_list_array['single']           = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single']
                time_list_array['group']            = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['group']
                time_list_array['total']            = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single'] + get_branch_data[0]['group']
                time_list_array['male']             = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['male']
                time_list_array['female']           = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['female']
                time_list_array['converted_count']  = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['converted_count']
                
                if(len(get_branch_data) != 0):
                    converted_count = 0 if (len(get_branch_data) == 0) else (0 if not get_branch_data[0]['converted_count'] else get_branch_data[0]['converted_count'])
                    total_count     = 0 if (len(get_branch_data) == 0) else get_branch_data[0]['single'] + get_branch_data[0]['group']
                    
                    if(total_count != 0):
                        pct         = round(converted_count / total_count * 100)
                    else:
                        pct         = 0
                time_list_array['pct']   = pct

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
                
                converted_count         =  converted_count + (0 if not total['converted_count'] else total['converted_count'])
                conversion_percentage   =  conversion_percentage + total['pct']
                
            total_pct                   = 0 if total_count == 0 else round(converted_count / total_count * 100)
            data_total_sum              = {'time_period' : time_period,'single' : single,'group' :group,'single' :single,'group':group,'total':total_count,'male':male,'female':female,'converted_count':converted_count,'pct':total_pct,'total_rw':True}
            time_data.append(data_total_sum)
            
            ################################################################################################################
            ################## StaffWise ############################################################
            get_staff_ids                           = staff_tb.objects.all().filter(branch_id=branch)
            get_time_periods                        = time_period_tb.objects.all()

            performance_data                        = []
            attendance_report                       = []
            for staff in get_staff_ids:
                get_staff_data                      = customer_tb.objects.all().filter(date__range=(date_from, date_to),conversion_to=staff.id,status="Completed",job_id=job_id).values('conversion_to').annotate(count=Count('conversion_to')).annotate(converted_count=Sum('converted_count')).annotate(pct=Sum('conversion_percentage') / Count('conversion_to')).annotate(male=(Sum(Cast('male', IntegerField()))) + (Sum('no_of_male'))).annotate(female=(Sum(Cast('female', IntegerField()))) + (Sum('no_of_female'))).annotate(single=Sum(Cast('single', IntegerField()))).annotate(group=Sum(Cast('group', IntegerField()))).order_by().distinct()
                
                staff_name                          = staff_tb.objects.all().filter(id=staff.id).get()
                branch_name                         = branch_tb.objects.all().filter(id=staff_name.branch_id.id).get()
                array_data                          = {}
                array_data['name']                  = staff_name.name
                array_data['single']                = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['single']
                array_data['group']                 = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['group']
                array_data['total']                 = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['single'] + get_staff_data[0]['group']
                array_data['converted_count']       = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['converted_count']
                
                if(len(get_staff_data) != 0):
                    converted_count = 0 if (len(get_staff_data) == 0) else (0 if not get_staff_data[0]['converted_count'] else get_staff_data[0]['converted_count'])
                    total_count     = 0 if (len(get_staff_data) == 0) else get_staff_data[0]['single'] + get_staff_data[0]['group']
                    
                    if(total_count != 0):
                        pct         = round(converted_count / total_count * 100)
                    else:
                        pct         = 0
                array_data['pct']   = pct
                performance_data.append(array_data)

                ########################################### attendance ################################################
                staff_attendance_list               = staff_attendance_tb.objects.all().filter(date__range=(date_from, date_to),staff_id=staff.id,submit=True,approve=True)
                get_detailed_data_list              = []
            
                if staff_attendance_list:
                    for data in staff_attendance_list:
                        my_dict = {}
                        my_dict['date']                 =  data.date
                        my_dict['name']                 =  staff.name
                        my_dict['in_time']              =  data.in_time
                        my_dict['out_time']             =  data.out_time
                        my_dict['break_hours']          =  data.break_hours
                        my_dict['work_hours']           =  data.work_hours
                        my_dict['over_time']            =  data.over_time
                        my_dict['under_time']           =  data.under_time
                        get_detailed_data_list.append(my_dict)
                else:
                    not_my_dict = {}
                    not_my_dict['date']                 =  ''
                    not_my_dict['name']                 =  staff.name
                    not_my_dict['in_time']              =  '00:00'
                    not_my_dict['out_time']             =  '00:00'
                    not_my_dict['break_hours']          =  '00:00'
                    not_my_dict['work_hours']           =  '00:00'
                    not_my_dict['over_time']            =  '00:00'
                    not_my_dict['under_time']           =  '00:00'
                    get_detailed_data_list.append(not_my_dict)

                
                d = sorted(get_detailed_data_list, key=operator.itemgetter("name"))
                outputList=[]
                for i,g in itertools.groupby(d, key=operator.itemgetter("name")):
                    data_arra   = {}
                    data_arra[i]= list(g)
                    outputList.append(data_arra)

                
       
                get_detailed_data_list  = []
                for attendace in outputList:
                    key     = list(attendace.keys())
                    values  = list(attendace.values())

                    get_all_data    = []
                    for data in values[0]:
                        my_dict = {}
                        my_dict['date']                 =  data['date']
                        my_dict['name']                 =  data['name']
                        my_dict['in_time']              =  data['in_time']
                        my_dict['out_time']             =  data['out_time']
                        my_dict['break_hours']          =  data['break_hours']
                        my_dict['work_hours']           =  data['work_hours']
                        my_dict['over_time']            =  data['over_time']
                        my_dict['under_time']           =  data['under_time']
                        get_all_data.append(my_dict)
                    
                    get_all_data.sort(key=lambda x: x.get('date'), reverse=False)


                    mysum       = timedelta()
                    work_hours  = timedelta()
                    over_time   = timedelta()
                    under_time  = timedelta()
                    for total in get_all_data:
                        (h, m) = total['break_hours'].split(':')
                        d = timedelta(hours=int(h), minutes=int(m))
                        mysum = d + mysum

                        (wh, wm) = total['work_hours'].split(':')
                        wd = timedelta(hours=int(wh), minutes=int(wm))
                        work_hours = wd + work_hours

                        if total['over_time'] != '0':
                            (oh, om) = total['over_time'].split(':')
                            od = timedelta(hours=int(oh), minutes=int(om))
                            over_time = od + over_time
                        if total['under_time'] != '0':
                            (uh, um) = total['under_time'].split(':')
                            ud = timedelta(hours=int(uh), minutes=int(um))
                            under_time = ud + under_time
                        
                    data_total_sum              = {'name' : key[0],'in_time' :'','out_time' :'','break_hours':mysum,'work_hours':work_hours,'over_time':over_time,'under_time':under_time}
                    get_all_data.append(data_total_sum)

                    # data_list_array             = {}
                    # data_list_array             = data_total_sum
                    get_detailed_data_list.append(data_total_sum) 

                    if get_detailed_data_list:
                        attendance_report.append(data_total_sum)
            
                ########################################################################################
            ########### Performance ############################
            performance_data.sort(key=lambda x: x.get('pct'), reverse=True)

            total_count             = 0
            converted_count         = 0
            conversion_percentage   = 0
            total_entry             = len(performance_data)
            for total in performance_data:
                total_count             =  total_count + total['total']
                converted_count         =  converted_count + (0 if not total['converted_count'] else total['converted_count'])
                conversion_percentage   =  conversion_percentage + total['pct']
                
            total_pct                   = 0 if total_count == 0 else round(converted_count / total_count * 100)
            data_total_sum              = {'name':'Total','total':total_count,'converted_count':converted_count,'pct':total_pct}
            performance_data.append(data_total_sum)


       
            ##########################################################################################
            url                         = request.build_absolute_uri('/')
            branch_name                 = branch_data.name
            email                       = branch_data.email
            list_data                   = {'performance_data' : performance_data ,'time_data':time_data,'attendance_report':attendance_report,'branch_name':branch_name,'url':url,'job_actual_start_date':job_actual_start_date,'job_actual_end_date':job_actual_end_date,'logo':logo}
           
            
            # return render(request,'email/branchwise_job.html',{'list_data' : list_data})
            # sendemail
            cc_list                     = branch_data.cc.split(',')
            
            branchWiseSendEmail(email,'email/branchwise_job.html',list_data,cc_list)
            messages.success(request, 'Mail Send Successfully')  
        
        return redirect('/list-task-based-job?id='+ str(job_id))
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def userForgotPasswordEmail(request):
    if  request.method=='POST':
        email       = request.POST['email']
        user        = request.POST['user']
        now         = datetime.now(pytz.timezone('Asia/Dubai'))
        digits      = '1234567890'
        pin         = ''.join(random.choice(digits) for i in range(4))

        if user == 'agent':
            if agent_tb.objects.all().filter(email=email).exists():
                agent   = agent_tb.objects.all().filter(email=email).get()
                agent_tb.objects.all().filter(id=agent.id).update(pin=pin,updated_at=now)

                url     = request.build_absolute_uri('/agent-forgot-password/?pin='+str(pin))
            else:
                messages.error(request, 'User not found')
                return redirect('user-forgot-password-email')

        elif user == 'team_leader':
            if team_leader_tb.objects.all().filter(email=email).exists():
                tl      = team_leader_tb.objects.all().filter(email=email).get()
                team_leader_tb.objects.all().filter(id=tl.id).update(pin=pin,updated_at=now)

                url     = request.build_absolute_uri('/tl-forgot-password/?pin='+str(pin))
            else:
                messages.error(request, 'User not found')
                return redirect('user-forgot-password-email')

        sendEmailRestPassword(email,'email/forgot_password.html',url)
        messages.success(request, 'Email send successfully.')
        return redirect('user-forgot-password-email')
    else:
        return render(request,'user/forgot_password_email.html')




def sendEmailRestPassword(email,template,url):
    html_template   = template
    html_message    = render_to_string(html_template,  {'url': url})
    subject         = 'Welcome to Actsheet'
    email_from      = settings.EMAIL_HOST_USER
    recipient_list  = [email]
    message         = EmailMessage(subject, html_message, email_from, recipient_list)
    message.content_subtype = 'html'
    message.send()
    return



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def tlForgotPassword(request):
    if 'pin' in request.GET:
        if request.method=="POST":
            pin             = request.POST['user_id']
            password        = request.POST['confirm_password']
            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            hash_password   = make_password(password)
            
            team_leader_tb.objects.all().filter(pin=pin).update(password=hash_password,pin=None,updated_at=now)

            messages.success(request, 'Password successfully updated.')
            return redirect('user-login')
        else:
            user_id     = request.GET['pin']
            return render(request,'user/tl_forgot_password.html',{'user_id' : user_id})
    else:
        raise Http404



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def agentForgotPassword(request):
    if 'pin' in request.GET:
        if request.method=="POST":
            pin             = request.POST['user_id']
            password        = request.POST['confirm_password']
            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            hash_password   = make_password(password)
            
            agent_tb.objects.all().filter(pin=pin).update(password=hash_password,pin=None,updated_at=now)

            messages.success(request, 'Password successfully updated.')
            return redirect('user-login')
        else:
            pin             = request.GET['pin']
            return render(request,'user/agent_forgot_password.html',{'user_id' : pin})
    else:
        raise Http404




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def clientForgotPasswordEmail(request):
    if  request.method=='POST':
        email       = request.POST['email']

        if client_tb.objects.all().filter(email=email).exists():
            client  = client_tb.objects.all().filter(email=email).get()
            now     = datetime.now(pytz.timezone('Asia/Dubai'))

            digits  = '1234567890'
            pin     = ''.join(random.choice(digits) for i in range(4))

            client_tb.objects.all().filter(id=client.id).update(pin=pin,updated_at=now)

            url     = request.build_absolute_uri('/client-forgot-password/?pin='+str(pin))
        else:
            messages.error(request, 'User not found')
            return redirect('client-forgot-password-email')

        sendEmailRestPassword(email,'email/forgot_password.html',url)
        messages.success(request, 'Email send successfully.')
        return redirect('client-forgot-password-email')
    else:
        return render(request,'client/forgot_password_email.html')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def clientForgotPassword(request):
    if 'pin' in request.GET:
        if request.method=="POST":
            pin             = request.POST['user_id']
            password        = request.POST['confirm_password']
            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            hash_password   = make_password(password)
            
            client_tb.objects.all().filter(pin=pin).update(password=hash_password,pin=None,updated_at=now)

            messages.success(request, 'Password successfully updated.')
            return redirect('client-login')
        else:
            user_id     = request.GET['pin']
            return render(request,'client/forgot_password.html',{'user_id' : user_id})
    else:
        raise Http404



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def adminForgotPasswordEmail(request):
    if  request.method=='POST':
        email       = request.POST['email']

        if admin_tb.objects.all().filter(email=email).exists():
            admin   = admin_tb.objects.all().filter(email=email).get()
            now     = datetime.now(pytz.timezone('Asia/Dubai'))

            digits  = '1234567890'
            pin     = ''.join(random.choice(digits) for i in range(4))

            admin_tb.objects.all().filter(id=admin.id).update(pin=pin,updated_at=now)

            url     = request.build_absolute_uri('/admin-forgot-password/?pin='+str(pin))
        else:
            messages.error(request, 'User not found')
            return redirect('admin-forgot-password-email')

        
        sendEmailRestPassword(email,'email/forgot_password.html',url)
        messages.success(request, 'Email send successfully.')
        return redirect('admin-forgot-password-email')
    else:
        return render(request,'admin/forgot_password_email.html')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def adminForgotPassword(request):
    if 'pin' in request.GET:
        if request.method=="POST":
            pin             = request.POST['user_id']
            password        = request.POST['confirm_password']
            now             = datetime.now(pytz.timezone('Asia/Dubai'))

            # hash_password   = make_password(password)
            admin_tb.objects.all().filter(pin=pin).update(password=password,pin=None,updated_at=now)

            messages.success(request, 'Password successfully updated.')
            return redirect('admin-login')
        else:
            pin             = request.GET['pin']
            return render(request,'admin/forgot_password.html',{'user_id' : pin})
    else:
        raise Http404



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateClientPassword(request):
    if request.session.has_key('adminId'):
        client_id       = request.GET['id']
        password        = request.POST['new_password']
        now             = datetime.now(pytz.timezone('Asia/Dubai'))

        # password hashchecked
        hash_password   = make_password(password)
        client_tb.objects.all().filter(id=client_id).update(password=hash_password,updated_at=now)

        messages.success(request, 'Password update successfully')
        return redirect('/edit-client?id='+ str(client_id))
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateAgentPassword(request):
    if request.session.has_key('adminId'):
        agent_id        = request.GET['id']
        password        = request.POST['new_password']
        now             = datetime.now(pytz.timezone('Asia/Dubai'))

        # password hashchecked
        hash_password   = make_password(password)
        agent_tb.objects.all().filter(id=agent_id).update(password=hash_password,updated_at=now)

        messages.success(request, 'Password update successfully')
        return redirect('/edit-agent?id='+ str(agent_id))
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateTLPassword(request):
    if request.session.has_key('adminId'):
        tl_id           = request.GET['id']
        password        = request.POST['new_password']
        now             = datetime.now(pytz.timezone('Asia/Dubai'))

        # password hashchecked
        hash_password   = make_password(password)
        team_leader_tb.objects.all().filter(id=tl_id).update(password=hash_password,updated_at=now)

        messages.success(request, 'Password update successfully')
        return redirect('/edit-team-leader?id='+ str(tl_id))
    else:
        return redirect('admin-login')




def getTaskFilterType(request):
    if request.session.has_key('adminId') or request.session.has_key('teamLeadertId') or request.session.has_key('agentId'):
        get_type       = request.GET['type']
       

        if get_type == 'client':
            if request.session.has_key('teamLeadertId'):
                team_leader_id          = request.session['teamLeadertId']
                get_all_clients         = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('client_id').distinct()
            elif request.session.has_key('agentId'):
                agent_id                = request.session['agentId']
                get_all_clients         = task_tb.objects.all().filter(agent_id=agent_id).values('client_id').distinct()
            elif request.session.has_key('adminId'):
                get_all_clients         = task_tb.objects.all().values('client_id').distinct()

            get_list                    = []
            for get_client_id in get_all_clients:
                client_data             = client_tb.objects.all().filter(id=get_client_id['client_id']).get()
                client_array            = {}
                client_array['id']      = client_data.id
                client_array['name']    = client_data.client_id
                get_list.append(client_array)

        elif get_type == 'agent': 
            if request.session.has_key('teamLeadertId'):
                team_leader_id              = request.session['teamLeadertId']
                get_all_agent               = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('agent_id').distinct()
            elif request.session.has_key('adminId'):
                get_all_agent               = task_tb.objects.all().values('agent_id').distinct()

            get_list                    = []
            for get_agent_id in get_all_agent:
                agent_data              = agent_tb.objects.all().filter(id=get_agent_id['agent_id']).get()
                agent_array             = {}
                agent_array['id']       = agent_data.id
                agent_array['name']     = agent_data.name
                get_list.append(agent_array)

        elif get_type == 'branch': 
            if request.session.has_key('teamLeadertId'):
                team_leader_id          = request.session['teamLeadertId']
                get_all_branch          = task_tb.objects.all().filter(team_leader_id=team_leader_id).values('branch_id').distinct()
            elif request.session.has_key('agentId'):
                agent_id                = request.session['agentId']
                get_all_branch          = task_tb.objects.all().filter(agent_id=agent_id).values('branch_id').distinct()
            elif request.session.has_key('adminId'):
                get_all_branch          = task_tb.objects.all().values('branch_id').distinct()

            get_list                    = []
            for get_branch_id in get_all_branch:
                branch_data             = branch_tb.objects.all().filter(id=get_branch_id['branch_id']).get()
                branch_array            = {}
                branch_array['id']      = branch_data.id
                branch_array['name']    = branch_data.name
                get_list.append(branch_array)


        return  JsonResponse({"models_to_return": list(get_list)})
    else:
        return redirect('admin-login')


def checkStaffEmail(request):
    email       = request.GET['email']
    get_id      = request.GET.get('id')
    email_exist = False
    
    if get_id:
        get_staff   = staff_tb.objects.all().filter(email=email).exclude(id=get_id)
        if get_staff:
            email_exist = True
    else:
        get_staff   = staff_tb.objects.all().filter(email=email)
        if get_staff:
            email_exist = True

    return HttpResponse(json.dumps(email_exist), content_type="application/json")


def checkAgentEmail(request):
    email       = request.GET['email']
    get_id      = request.GET.get('id')
    email_exist = False
    
    if get_id:
        get_agent   = agent_tb.objects.all().filter(email=email).exclude(id=get_id)
        if get_agent:
            email_exist = True
    else:
        get_agent   = agent_tb.objects.all().filter(email=email)
        if get_agent:
            email_exist = True

    return HttpResponse(json.dumps(email_exist), content_type="application/json")



def checkTLEmail(request):
    email       = request.GET['email']
    get_id      = request.GET.get('id')
    email_exist = False
    
    if get_id:
        get_tl  = team_leader_tb.objects.all().filter(email=email).exclude(id=get_id)
        if get_tl:
            email_exist = True
    else:
        get_tl  = team_leader_tb.objects.all().filter(email=email)
        if get_tl:
            email_exist = True

    return HttpResponse(json.dumps(email_exist), content_type="application/json")



# approve staff attendance
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def approveStaffAttendance(request):
    if request.session.has_key('adminId') or  request.session.has_key('teamLeadertId'):
        attendace_id    = request.GET['id']
        now             = datetime.now(pytz.timezone('Asia/Dubai'))
        approved_time   = now
       
        staff_attendance_tb.objects.all().filter(id=attendace_id).update(approve=True,approved_time=approved_time,updated_at=now)
        
        messages.success(request, 'Successfully Approved.')
        return redirect('list-attendance')
        
    else:
        return redirect('admin-login')