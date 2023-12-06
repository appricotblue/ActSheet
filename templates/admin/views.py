from django.shortcuts import render
from django.views.decorators.cache import cache_control
from .models import *
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime, timedelta, date, time
from .forms import imgForm, imgForm1, imgForm2, imgMultple, ImageFormSet, imgForm3, ExcelImportForm
import random
import string
from django.contrib.auth.hashers import make_password, check_password
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import base64
from PIL import Image
import io
import subprocess
from django.http import Http404 
from django.db.models import Sum, Max, Count, Min
from math import radians, cos, sin, asin, sqrt
import geopy.distance
import requests
import razorpay
import firebase_admin
from firebase_admin import credentials, messaging
from geopy.geocoders import Nominatim
from django.core.paginator import Paginator
from django.db.models.functions import Cast
from django.db.models import FloatField
import pandas as pd
from django.http import HttpResponse, HttpResponseRedirect
import json
from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone


# # -----pdf to image converter
# import base64 
# from io import BytesIO
# from pdf2image import convert_from_bytes
# import PyPDF2
# from django.core.files.storage import FileSystemStorage
# from django.core.files.base import ContentFile
# # -----pdf to image converter

# import qrcode
# from django.http import HttpResponse


# Create your views here.
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def adminTemplate(request):
    return redirect('admin-dashboard')





@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def adminLogin(request):
    if  request.method=='POST':
        email       = request.POST['email']
        password    = request.POST['password']
        user_role   = request.POST.get('user_role')

        if not user_role:
            var     = admin_tb.objects.all().filter(email=email,password=password)

            if var:
                for x in var:
                    request.session['adminId']=x.id
                return redirect('admin-dashboard')
            else:
                messages.error(request, 'Invalid username or password')
                return redirect('admin-login')
        else:
            role_id = user_roles_data_tb.objects.get(role=user_role)
            var     = user_data_tb.objects.all().filter(email=email,user_role_id=role_id.id)

            if var:
                for x in var:
                    if(check_password(password,x.password) == True):
                        request.session['userId']=x.id
                        request.session['userRole']=role_id.role
                    else:
                        messages.error(request, 'Invalid username or password')
                        return redirect('user-login')
                return redirect('user-dashboard')

            else:
                messages.error(request, 'Invalid username or password')
                return redirect('admin-login')
    else:
        if  request.session.has_key('adminId'):
            return redirect('admin-dashboard')
        else:
            user_role_list  = user_roles_data_tb.objects.all().exclude(role='Business Representative')
            return render(request,'admin/login.html',{'user_role_list':user_role_list})




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def userDashboard(request):
    if request.session.has_key('userId'):
        return render(request,'user/dashboard.html')
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def adminLogout(request):
    if request.session.has_key('adminId'):
        if request.session.has_key('adminId'):
            del request.session['adminId']
        if request.session.has_key('userId'):
            del request.session['userId']
        if request.session.has_key('userRole'):
            del request.session['userRole']
        adminLogout(request)
    return redirect('admin-login')



# @cache_control(no_cache=True,must_revalidate=True,no_store=True)
# def adminDashboard(request):
#     return render(request,'admin/dashboard.html')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def adminDashboard(request):
    if request.session.has_key('adminId'):
        if  request.method=='POST':
            from_date           = request.POST['date_from']
            to_date             = request.POST['date_to']
            latitude            = request.POST['latitude']
            longitude           = request.POST['longitude']
            location            = request.POST['location']
            
            near_by_shop        = shops_tb.objects.all()
            near_by_shop_ids    = []

            for shop in near_by_shop:
                shop_lat        = shop.latitude
                shop_long       = shop.longitude
                radius          = shop.radius

                coords_1        = (latitude, longitude)
                coords_2        = (shop_lat, shop_long)
                distance        = geopy.distance.geodesic(coords_1, coords_2).km

                if float(radius) >= float(distance):
                    near_by_shop_ids.append(shop.id)
        
        else:
            #only difference in post data and location based shops - so get data using one time

            from_date           = datetime.now() - timedelta(30)
            to_date             = datetime.now()

            from_date           = from_date.strftime("%Y-%m-%d")
            to_date             = to_date.strftime("%Y-%m-%d")

            latitude            = ""
            longitude           = ""
            location            = ""

            near_by_shop        = shops_tb.objects.all()
            near_by_shop_ids    = []

            for shop in near_by_shop:
                near_by_shop_ids.append(shop.id)


        ###########################---- Shop-----#####################################
        data_found          = False
        get_data_shop       = invoice_data_tb.objects.all().filter(created_at__range=(from_date, to_date),shop_id__in=near_by_shop_ids,status="Approve").values('shop_id').annotate(Count("shop_id")).distinct()

        shop_list           = []

        for shop in get_data_shop:
            get_shop_data   = shops_tb.objects.all().filter(id=shop['shop_id']).get()
            shop_list.append({
                'image'     : None if not get_shop_data.image else get_shop_data.image.url,
                'shop_name' : get_shop_data.name,
                'category'  : get_shop_data.category_id.name,
                'location'  : get_shop_data.location,
                'vendor'    : get_shop_data.vendor_id.name,
                'count'     : shop['shop_id__count']
            })
        shop_list.sort(key=lambda x: x.get('count'), reverse=True)
        shop_list           = shop_list[:5]

        ###########################---- Users-----#####################################
        get_data_user       = invoice_data_tb.objects.all().filter(created_at__range=(from_date, to_date),shop_id__in=near_by_shop_ids,status="Approve").values('user_id').annotate(Count("user_id")).distinct()

        users_list          = []

        for user in get_data_user:
            get_user_data   = user_data_tb.objects.all().filter(id=user['user_id']).get()
            users_list.append({
                'image'     : None if not get_user_data.profile_image else get_user_data.profile_image.url,
                'user_name' : get_user_data.name,
                "phone"     : get_user_data.phone,
                'count'     : user['user_id__count']
            })
        users_list.sort(key=lambda x: x.get('count'), reverse=True)
        users_list          = users_list[:5]

        ###########################---- Vendors-----#####################################
        get_data_vendors    = invoice_data_tb.objects.all().filter(created_at__range=(from_date, to_date),shop_id__in=near_by_shop_ids,status="Approve").values('vendor_id').annotate(Count("vendor_id")).distinct()
        
        vendors_list        = []
        key                 = 0
        for vendor in get_data_vendors:
            key             = key + 1
            get_vendor_data = vendors_tb.objects.all().filter(id=vendor['vendor_id']).get()
            vendors_list.append({
                'key'       : key,
                'name'      : get_vendor_data.name,
                "phone"     : get_vendor_data.phone,
                'count'     : vendor['vendor_id__count']
            })
        vendors_list.sort(key=lambda x: x.get('count'), reverse=True)
        vendors_list        = vendors_list[:4]
        

        request_data        = {'from_date' : from_date,'to_date':to_date,'latitude':latitude,'longitude':longitude,'location':location}

        if len(shop_list) != 0 and len(users_list) != 0 and len(vendors_list) != 0:
            data_found      = True

        respose_data        =   {
                                    'shop_list'     : shop_list,
                                    'users_list'    : users_list,
                                    'vendors_list'  : vendors_list
                                }

        return render(request,'admin/performance.html',{'request_data':request_data,'respose_data':respose_data,'data_found':data_found})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def performanceReport(request):
    if request.session.has_key('adminId'):
        if  request.method=='POST':
            from_date           = request.POST['date_from']
            to_date             = request.POST['date_to']
            latitude            = request.POST['latitude']
            longitude           = request.POST['longitude']
            location            = request.POST['location']
            
            near_by_shop        = shops_tb.objects.all()
            near_by_shop_ids    = []

            for shop in near_by_shop:
                shop_lat        = shop.latitude
                shop_long       = shop.longitude
                radius          = shop.radius

                coords_1        = (latitude, longitude)
                coords_2        = (shop_lat, shop_long)
                distance        = geopy.distance.geodesic(coords_1, coords_2).km

                if float(radius) >= float(distance):
                    near_by_shop_ids.append(shop.id)
        
        else:
            #only difference in post data and location based shops - so get data using one time

            from_date           = datetime.now() - timedelta(30)
            to_date             = datetime.now()

            from_date           = from_date.strftime("%Y-%m-%d")
            to_date             = to_date.strftime("%Y-%m-%d")

            latitude            = ""
            longitude           = ""
            location            = ""

            near_by_shop        = shops_tb.objects.all()
            near_by_shop_ids    = []

            for shop in near_by_shop:
                near_by_shop_ids.append(shop.id)


        ###########################---- Shop-----#####################################
        data_found          = False
        get_data_shop       = invoice_data_tb.objects.all().filter(created_at__range=(from_date, to_date),shop_id__in=near_by_shop_ids,status="Approve").values('shop_id').annotate(Count("shop_id")).distinct()

        shop_list           = []

        for shop in get_data_shop:
            get_shop_data   = shops_tb.objects.all().filter(id=shop['shop_id']).get()
            shop_list.append({
                'image'     : None if not get_shop_data.image else get_shop_data.image.url,
                'shop_name' : get_shop_data.name,
                'category'  : get_shop_data.category_id.name,
                'location'  : get_shop_data.location,
                'vendor'    : get_shop_data.vendor_id.name,
                'count'     : shop['shop_id__count']
            })
        shop_list.sort(key=lambda x: x.get('count'), reverse=True)
        shop_list           = shop_list[:5]

        ###########################---- Users-----#####################################
        get_data_user       = invoice_data_tb.objects.all().filter(created_at__range=(from_date, to_date),shop_id__in=near_by_shop_ids,status="Approve").values('user_id').annotate(Count("user_id")).distinct()

        users_list          = []

        for user in get_data_user:
            get_user_data   = user_data_tb.objects.all().filter(id=user['user_id']).get()
            users_list.append({
                'image'     : None if not get_user_data.profile_image else get_user_data.profile_image.url,
                'user_name' : get_user_data.name,
                "phone"     : get_user_data.phone,
                'count'     : user['user_id__count']
            })
        users_list.sort(key=lambda x: x.get('count'), reverse=True)
        users_list          = users_list[:5]

        ###########################---- Vendors-----#####################################
        get_data_vendors    = invoice_data_tb.objects.all().filter(created_at__range=(from_date, to_date),shop_id__in=near_by_shop_ids,status="Approve").values('vendor_id').annotate(Count("vendor_id")).distinct()
        
        vendors_list        = []
        key                 = 0
        for vendor in get_data_vendors:
            key             = key + 1
            get_vendor_data = vendors_tb.objects.all().filter(id=vendor['vendor_id']).get()
            vendors_list.append({
                'key'       : key,
                'name'      : get_vendor_data.name,
                "phone"     : get_vendor_data.phone,
                'count'     : vendor['vendor_id__count']
            })
        vendors_list.sort(key=lambda x: x.get('count'), reverse=True)
        vendors_list        = vendors_list[:4]
        

        request_data        = {'from_date' : from_date,'to_date':to_date,'latitude':latitude,'longitude':longitude,'location':location}

        if len(shop_list) != 0 and len(users_list) != 0 and len(vendors_list) != 0:
            data_found      = True

        respose_data        =   {
                                    'shop_list'     : shop_list,
                                    'users_list'    : users_list,
                                    'vendors_list'  : vendors_list
                                }

        return render(request,'admin/performance.html',{'request_data':request_data,'respose_data':respose_data,'data_found':data_found})
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def topUsersReport(request):
    if request.session.has_key('adminId'):
        if  request.method=='POST':
            latitude            = request.POST['latitude']
            longitude           = request.POST['longitude']
            location            = request.POST['location']
            country             = request.POST['country']
            state               = request.POST['state']
            district            = request.POST['district']
           
            get_location_array  = location.split(',')
                
            if(len(get_location_array) == 1):
                loc_type        = "Country"
                get_given_data  = country
                near_by_shop    = shops_tb.objects.all().filter(country=get_given_data)
            elif(len(get_location_array) == 2):
                loc_type        = "State"
                get_given_data  = state
                near_by_shop    = shops_tb.objects.all().filter(state=get_given_data)
            else:
                loc_type        = "City"
                get_given_data  = district
                near_by_shop    = shops_tb.objects.all().filter(city=get_given_data)

            near_by_shop_ids    = []

            for shop in near_by_shop:
                near_by_shop_ids.append(shop.id)
        
        else:
            #only difference in post data and location based shops - so get data using one time

            from_date           = datetime.now() - timedelta(30)
            to_date             = datetime.now()

            from_date           = from_date.strftime("%Y-%m-%d")
            to_date             = to_date.strftime("%Y-%m-%d")

            latitude            = ""
            longitude           = ""
            location            = ""
            country             = ""
            state               = ""
            district            = ""

            near_by_shop        = shops_tb.objects.all()
            near_by_shop_ids    = []

            for shop in near_by_shop:
                near_by_shop_ids.append(shop.id)


        ###########################---- Users-----#####################################
        get_data_user       = invoice_data_tb.objects.all().filter(shop_id__in=near_by_shop_ids,status="Approve").values('user_id').annotate(Count("user_id")).distinct()

        users_list          = []

        for user in get_data_user:
            get_user_data   = user_data_tb.objects.all().filter(id=user['user_id']).get()
            users_list.append({
                'image'     : None if not get_user_data.profile_image else get_user_data.profile_image.url,
                'user_name' : get_user_data.name,
                "phone"     : get_user_data.phone,
                "email"     : get_user_data.email,
                'count'     : user['user_id__count']
            })
        users_list.sort(key=lambda x: x.get('count'), reverse=True)

        request_data            = {'latitude':latitude,'longitude':longitude,'location':location,'country':country,'state':state,'district':district}

        #-- Pagination
        paginator               = Paginator(users_list, per_page=20)
        if request.method == 'POST':
            page_number = request.POST.get('page')
        else:
            page_number = request.GET.get('page')
        page                    = paginator.get_page(page_number)
        #-- Pagination

        return render(request,'admin/top_users.html',{'request_data':request_data,'page':page})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def topShopsReport(request):
    if request.session.has_key('adminId'):
        if  request.method=='POST':
            latitude            = request.POST['latitude']
            longitude           = request.POST['longitude']
            location            = request.POST['location']
            country             = request.POST['country']
            state               = request.POST['state']
            district            = request.POST['district']
           
            get_location_array  = location.split(',')
                
            if(len(get_location_array) == 1):
                loc_type        = "Country"
                get_given_data  = country
                near_by_shop    = shops_tb.objects.all().filter(country=get_given_data)
            elif(len(get_location_array) == 2):
                loc_type        = "State"
                get_given_data  = state
                near_by_shop    = shops_tb.objects.all().filter(state=get_given_data)
            else:
                loc_type        = "City"
                get_given_data  = district
                near_by_shop    = shops_tb.objects.all().filter(city=get_given_data)

            near_by_shop_ids    = []

            for shop in near_by_shop:
                near_by_shop_ids.append(shop.id)
        
        else:
            #only difference in post data and location based shops - so get data using one time

            from_date           = datetime.now() - timedelta(30)
            to_date             = datetime.now()

            from_date           = from_date.strftime("%Y-%m-%d")
            to_date             = to_date.strftime("%Y-%m-%d")

            latitude            = ""
            longitude           = ""
            location            = ""
            country             = ""
            state               = ""
            district            = ""

            near_by_shop        = shops_tb.objects.all()
            near_by_shop_ids    = []

            for shop in near_by_shop:
                near_by_shop_ids.append(shop.id)


        ###########################---- Shop-----#####################################
        data_found          = False
        get_data_shop       = invoice_data_tb.objects.all().filter(shop_id__in=near_by_shop_ids,status="Approve").values('shop_id').annotate(Count("shop_id")).distinct()

        shop_list           = []

        for shop in get_data_shop:
            get_shop_data   = shops_tb.objects.all().filter(id=shop['shop_id']).get()
            shop_list.append({
                'image'     : None if not get_shop_data.image else get_shop_data.image.url,
                'shop_name' : get_shop_data.name,
                'category'  : get_shop_data.category_id.name,
                'location'  : get_shop_data.location,
                'vendor'    : get_shop_data.vendor_id.name,
                'count'     : shop['shop_id__count']
            })
        shop_list.sort(key=lambda x: x.get('count'), reverse=True)

        request_data            = {'latitude':latitude,'longitude':longitude,'location':location,'country':country,'state':state,'district':district}


        #-- Pagination
        paginator               = Paginator(shop_list, per_page=20)
        if request.method == 'POST':
            page_number = request.POST.get('page')
        else:
            page_number = request.GET.get('page')
        page                    = paginator.get_page(page_number)
        #-- Pagination

        return render(request,'admin/top_shops.html',{'request_data':request_data,'page':page})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listLevels(request):
    if request.session.has_key('adminId'):
        level_list  = levels_tb.objects.all().order_by('-id')
        return render(request,'admin/list_levels.html',{'level_list' : level_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewLevel(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            name            = request.POST['name']
            level           = request.POST['level']
            percentage      = request.POST['percentage']
            now             = datetime.now()

            get_level       = levels_tb.objects.all().filter(level=level)
            if get_level:
                messages.error(request, 'Level already exist')
                return redirect('add-level')

            insert_data     = levels_tb(name=name,level=level,percentage=percentage,created_at=now,updated_at=now)
            insert_data.save()
            messages.success(request, 'Successfully added.')
            return redirect('list-levels')
        else:
            return render(request,'admin/add_level.html')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateLevel(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            level_id            = request.GET['id']
            name                = request.POST['name']
            level               = request.POST['level']
            percentage          = request.POST['percentage']
            now                 = datetime.now()

            get_level           = levels_tb.objects.all().filter(level=level).exclude(id=level_id)
            
            if get_level:
                messages.error(request, 'Level already exist')
                return redirect('/edit-level/?id='+ str(level_id))

            levels_tb.objects.all().filter(id=level_id).update(name=name,level=level,percentage=percentage,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-levels')
        else:
            level_id            = request.GET['id']
            level_data          = levels_tb.objects.all().filter(id=level_id)
            
            return render(request,'admin/edit_level.html',{'level_data' : level_data})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteLevel(request):
    if request.session.has_key('adminId'):
        level_id    = request.GET['id']
        fromReg     = levels_tb.objects.all().filter(id=level_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-levels')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-levels')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listVendors(request):
    if request.session.has_key('adminId') or request.session.has_key('userId'):
        user_id = request.GET.get('id')

        if request.session.has_key('adminId'):
            if user_id:
                vendors_list= vendors_tb.objects.filter(added_by=user_id).order_by('-id')
            else:
                vendors_list= vendors_tb.objects.all().order_by('-id')
        elif request.session.has_key('userId'):
            if user_id:
                user_id = user_id
            else:
                user_id = request.session['userId']

            vendors_list= vendors_tb.objects.all().filter(added_by=user_id).order_by('-id')

        #-- Pagination
        paginator       = Paginator(vendors_list, per_page=20)
        page_number     = request.GET.get('page')
        page            = paginator.get_page(page_number)
        #-- Pagination
        return render(request,'admin/list_vendors.html',{'page' : page})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateAdminImportVendorInvoiceStatus(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            vendor_id               = request.POST['id_vendor']
            import_invoice          = request.POST.get('import_invoice')
            now                     = datetime.now()

            import_invoice_status       = False
            if import_invoice:
                import_invoice_status   = True

            vendors_tb.objects.all().filter(id=vendor_id).update(import_invoice=import_invoice_status,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-vendor')
        else:
            return redirect('list-vendor')
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewVendor(request):
    if request.session.has_key('adminId') or request.session.has_key('userId'):
        if request.method=="POST":
            name            = request.POST['name']
            phone           = request.POST['phone']
            email           = request.POST['email']
            adar_number     = request.POST['adar_number']
            pan_number      = request.POST['pan_number']
            auto_password   = request.POST.get('auto_password')
            password        = request.POST.get('password')
            business_rep_id = request.POST.get('business_rep_id')

            image_file      = imgForm(request.POST,request.FILES)
            image_file1     = imgForm1(request.POST,request.FILES)

            now             = datetime.now()
            adar_image      = None
            pan_image       = None
            added_by        = None

            if request.session.has_key('userId'):
                added_by        = user_data_tb.objects.get(id=request.session['userId'])
            
            if business_rep_id:
                business_rep_id = user_data_tb.objects.get(id=business_rep_id)

            get_vendor          = vendors_tb.objects.all().filter(email=email)
            get_vendor_phn      = vendors_tb.objects.all().filter(phone=phone)

            if get_vendor:
                messages.error(request, 'Email already exist')
                return redirect('add-vendor')

            elif get_vendor_phn:
                messages.error(request, 'Phone number already exist')
                return redirect('add-vendor')
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

                if image_file.is_valid():
                    adar_image  = image_file.cleaned_data['image']
                if image_file1.is_valid():
                    pan_image   = image_file1.cleaned_data['image1']

                insert_data     = vendors_tb(name=name,phone=phone,email=email,password=hash_password,adar_number=adar_number,pan_number=pan_number,adar_image=adar_image,pan_image=pan_image,status="Active",added_by=added_by,business_rep_id=business_rep_id,created_at=now,updated_at=now)
                insert_data.save()
                messages.success(request, 'Successfully added.')

                return redirect('list-vendor')
        else:
            business_rep_role       = user_roles_data_tb.objects.get(role='Business Representative')
            
            if request.session.has_key('userId'):
                get_all_business_rep= user_data_tb.objects.filter(user_role_id=business_rep_role.id,assigned_to=request.session['userId'])
            else:
                get_all_business_rep= user_data_tb.objects.filter(user_role_id=business_rep_role.id)
            return render(request,'admin/add_vendor.html',{'get_all_business_rep'   : get_all_business_rep})
    else:
        return redirect('admin-login')



def sendEmail(email,template,password):
    html_template   = template
    html_message    = render_to_string(html_template,  {'password': password})
    subject         = 'Welcome to WonderApp'
    email_from      = settings.EMAIL_HOST_USER
    recipient_list  = [email]
    message         = EmailMessage(subject, html_message, email_from, recipient_list)
    message.content_subtype = 'html'
    message.send()
    return



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateVendor(request):
    if request.session.has_key('adminId') or request.session.has_key('userId'):
        if request.method=="POST":
            vendor_id       = request.GET['id']
            name            = request.POST['name']
            phone           = request.POST['phone']
            email           = request.POST['email']
            adar_number     = request.POST['adar_number']
            pan_number      = request.POST['pan_number']
            status          = request.POST['status']
            business_rep_id = request.POST.get('business_rep_id')

            image_file      = imgForm(request.POST,request.FILES)
            image_file1     = imgForm1(request.POST,request.FILES)

            now             = datetime.now()
            adar_image      = None
            pan_image       = None

            if business_rep_id:
                business_rep_id = user_data_tb.objects.get(id=business_rep_id)

            get_vendor_data = vendors_tb.objects.all().filter(id=vendor_id).get()

            get_vendor      = vendors_tb.objects.all().filter(email=email).exclude(id=vendor_id)

            get_vendor_phn  = vendors_tb.objects.all().filter(phone=phone).exclude(id=vendor_id)

            if get_vendor:
                messages.error(request, 'Email already exist')
                return redirect('/edit-vendor/?id='+ str(vendor_id))
            elif get_vendor_phn:
                messages.error(request, 'Phone number already exist')
                return redirect('/edit-vendor/?id='+ str(vendor_id))
            else:
                if image_file.is_valid():
                    image               = image_file.cleaned_data['image']
                    mymodel             = vendors_tb.objects.get(id=vendor_id)
                    mymodel.adar_image  = image
                    mymodel.save()
                if image_file1.is_valid():
                    image1              = image_file1.cleaned_data['image1']
                    mymodel             = vendors_tb.objects.get(id=vendor_id)
                    mymodel.pan_image   = image1
                    mymodel.save()

                vendors_tb.objects.all().filter(id=vendor_id).update(name=name,phone=phone,email=email,adar_number=adar_number,pan_number=pan_number,status=status,business_rep_id=business_rep_id,updated_at=now)


                #----- Notification ---- #
                #-- To vendor ---
                if get_vendor_data.status != status:
                    device_token    = get_vendor_data.device_token
                    if status == 'Pending':
                        title           = status
                        body            = 'Your account activation is pending'
                    elif status == 'Active':
                        title           = 'Congratulations'
                        body            = 'Your account is activated'
                    elif status == 'Reject':
                        title           = 'Oops..!'
                        body            = 'Your account is rejected'
                    sendNotificationToUser(device_token,title,body)

                    insert_data         = vendor_notification_tb(vendor_id=get_vendor_data,title=title,description=body,created_at=now,updated_at=now)
                    insert_data.save()
                #----------------------
                messages.success(request, 'Changes successfully updated.')
                return redirect('list-vendor')
        else:
            vendor_id           = request.GET['id']
            vendor_data         = vendors_tb.objects.all().filter(id=vendor_id)
            
            business_rep_role   = user_roles_data_tb.objects.get(role='Business Representative')

            if request.session.has_key('userId'):
                get_all_business_rep= user_data_tb.objects.filter(user_role_id=business_rep_role.id,assigned_to=request.session['userId'])
            else:
                get_all_business_rep= user_data_tb.objects.filter(user_role_id=business_rep_role.id)
            
            return render(request,'admin/edit_vendor.html',{'vendor_data' : vendor_data,'get_all_business_rep':get_all_business_rep})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateVendorPassword(request):
    if request.session.has_key('adminId') or request.session.has_key('userId'):
        vendor_id       = request.GET['id']
        password        = request.POST['new_password']
        now             = datetime.now()

        # password hashchecked
        hash_password   = make_password(password)
        vendors_tb.objects.all().filter(id=vendor_id).update(password=hash_password,updated_at=now)

        messages.success(request, 'Password update successfully')
        return redirect('/edit-vendor/?id='+ str(vendor_id))
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteVendor(request):
    if request.session.has_key('adminId') or request.session.has_key('userId'):
        vendor_id   = request.GET['id']
        fromReg     = vendors_tb.objects.all().filter(id=vendor_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-vendor')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-vendor')
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listCategory(request):
    if request.session.has_key('adminId'):
        category_list   = category_tb.objects.all().order_by('-id')

        #-- Pagination
        paginator       = Paginator(category_list, per_page=20)
        page_number     = request.GET.get('page')
        page            = paginator.get_page(page_number)
        #-- Pagination
        return render(request,'admin/list_categories.html',{'page' : page})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewCategory(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            name            = request.POST['name']
            description     = request.POST['description']
            image_file      = imgForm(request.POST,request.FILES)
            now             = datetime.now()
            image           = None

            if image_file.is_valid():
                image       = image_file.cleaned_data['image']

                insert_data = category_tb(name=name,description=description,image=image,created_at=now,updated_at=now)
                insert_data.save()
                messages.success(request, 'Successfully added.')

                return redirect('list-categories')
        else:
            return render(request,'admin/add_category.html')
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateCategory(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            category_id     = request.GET['id']
            name            = request.POST['name']
            description     = request.POST['description']
            image_file      = imgForm(request.POST,request.FILES)

            now             = datetime.now()
            image           = None

           
            if image_file.is_valid():
                image               = image_file.cleaned_data['image']
                mymodel             = category_tb.objects.get(id=category_id)
                mymodel.image       = image
                mymodel.save()

            category_tb.objects.all().filter(id=category_id).update(name=name,description=description,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-categories')
        else:
            category_id         = request.GET['id']
            category_data       = category_tb.objects.all().filter(id=category_id)
            
            return render(request,'admin/edit_category.html',{'category_data' : category_data})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteCategory(request):
    if request.session.has_key('adminId'):
        category_id = request.GET['id']
        fromReg     = category_tb.objects.all().filter(id=category_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-categories')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-categories')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listShops(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            vendor_id   = request.POST['vendor_id']
            shops_list  = shops_tb.objects.all().filter(vendor_id=vendor_id).order_by('-id')
        else:
            vendor_id   = None
            shops_list  = shops_tb.objects.all().order_by('-id')

        vendor_list     = vendors_tb.objects.all()


        #-- Pagination
        paginator       = Paginator(shops_list, per_page=20)
        if request.method == 'POST':
            page_number = request.POST.get('page')
        else:
            page_number = request.GET.get('page')
        page            = paginator.get_page(page_number)
        #-- Pagination


        return render(request,'admin/list_shops.html',{'page' : page,'vendor_list' : vendor_list,'vendor_id': vendor_id})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewShop(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            name                = request.POST['name']
            get_vendor_id       = request.POST['vendor_id']
            vendor_id           = vendors_tb.objects.get(id=get_vendor_id)
            get_category_id     = request.POST['category_id']
            category_id         = category_tb.objects.get(id=get_category_id)
            license_number      = request.POST['license_number']
            gst_number          = request.POST['gst_number']
            address             = request.POST['address']
            latitude            = request.POST['latitude']
            longitude           = request.POST['longitude']
            location            = request.POST['location']
            radius              = request.POST['radius']
            commission          = request.POST['commission']
            gst_pct             = request.POST['gst_pct']
            is_featured         = True if request.POST.get('is_featured') == 'true' else False
            wallet_amount       = request.POST.get('wallet_amount')
            image_file          = imgForm(request.POST,request.FILES)
            image_file1         = imgForm1(request.POST,request.FILES)
            image_file2         = imgForm2(request.POST,request.FILES)
            image_file3         = imgForm3(request.POST,request.FILES)
            opening_time        = request.POST.get('opening_time')
            closing_time        = request.POST.get('closing_time')
            website_url         = request.POST.get('website_url')
            phone1              = request.POST.get('phone1')
            phone2              = request.POST.get('phone2')
            now                 = datetime.now()
            image               = None
            gst_image           = None
            license_image       = None
            banner_image        = None

            business_rep_id     = vendor_id.business_rep_id
            added_by            = vendor_id.added_by

            if image_file.is_valid():
                image           = image_file.cleaned_data['image']

            if image_file1.is_valid():
                gst_image       = image_file1.cleaned_data['image1']

            if image_file2.is_valid():
                license_image   = image_file2.cleaned_data['image2']

            if image_file3.is_valid():
                banner_image    = image_file3.cleaned_data['image3']

            # geolocator          = Nominatim(user_agent="geoapiExercises")
            # getlocation         = geolocator.reverse(latitude+","+longitude)
            # getaddress          = getlocation.raw['address']
            # country             = getaddress.get('country', '')
            # state               = getaddress.get('state', '')
            # city                = getaddress.get('city', '')
            # if(not city):
            #     city            = getaddress.get('county', '')
            # pin_code            = getaddress.get('postcode', '')


            # Make the curl request
            response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng="+latitude+","+longitude+"&key=AIzaSyA6sfxAGWorlekK-rkolU152WkN5mzn76A")

            # Parse the JSON response
            location_data = json.loads(response.text)
            # Extract the country, state, and city information
            for result in location_data['results']:
                for component in result['address_components']:
                    if "country" in component['types']:
                        country     = component['long_name']
                    elif "administrative_area_level_1" in component['types']:
                        state       = component['long_name']
                    elif "administrative_area_level_3" in component['types']:
                        city        = component['long_name']
                    elif "postal_code" in component['types']:
                        pin_code    = component['long_name']


            ###------get upi
            my_string           = name.replace(" ", "")
            upi_id              = my_string+'@wonderpoints'
            get_shopupi         = shops_tb.objects.all().filter(upi_id=upi_id)
            ###------get upi

            insert_data         = shops_tb(name=name,vendor_id=vendor_id,category_id=category_id,gst_number=gst_number,address=address,latitude=latitude,longitude=longitude,location=location,radius=radius,image=image,gst_image=gst_image,license_image=license_image,banner_image=banner_image,opening_time=opening_time,closing_time=closing_time,is_featured=is_featured,commission=commission,license_number=license_number,wallet_amount=wallet_amount,gst_pct=gst_pct,country=country,state=state,city=city,pin_code=pin_code,website_url=website_url,phone1=phone1,phone2=phone2,business_rep_id=business_rep_id,added_by=added_by,created_at=now,updated_at=now)
            insert_data.save()

            ###------set upi
            latest_id           = shops_tb.objects.latest('id')
            if get_shopupi:
                upi_id          = my_string+str(latest_id.id)+'@wonderpoints'
            shops_tb.objects.all().filter(id=latest_id.id).update(upi_id=upi_id,updated_at=now)
            ###------set upi

            if image:
                insert_data     = shop_images_tb(image=image,shop_id=latest_id,is_shop_featured=True,created_at=now,updated_at=now)
                insert_data.save()

            messages.success(request, 'Successfully added.')

            return redirect('list-shops')
        else:
            vendors_list    = vendors_tb.objects.all()
            categroy_list   = category_tb.objects.all()
            return render(request,'admin/add_shop.html',{'vendors_list':vendors_list,'categroy_list':categroy_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateShop(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            shop_id             = request.GET['id']
            name                = request.POST['name']
            get_vendor_id       = request.POST['vendor_id']
            vendor_id           = vendors_tb.objects.get(id=get_vendor_id)
            get_category_id     = request.POST['category_id']
            category_id         = category_tb.objects.get(id=get_category_id)
            gst_number          = request.POST['gst_number']
            address             = request.POST['address']
            latitude            = request.POST['latitude']
            longitude           = request.POST['longitude']
            location            = request.POST['location']
            radius              = request.POST['radius']
            commission          = request.POST['commission']
            gst_pct             = request.POST['gst_pct']
            license_number      = request.POST['license_number']
            is_featured         = True if request.POST.get('is_featured') == 'true' else False
            status              = request.POST['status']
            wallet_amount       = request.POST.get('wallet_amount')
            image_file          = imgForm(request.POST,request.FILES)
            image_file1         = imgForm1(request.POST,request.FILES)
            image_file2         = imgForm2(request.POST,request.FILES)
            image_file3         = imgForm3(request.POST,request.FILES)
            opening_time        = request.POST.get('opening_time')
            closing_time        = request.POST.get('closing_time')
            website_url         = request.POST.get('website_url')
            phone1              = request.POST.get('phone1')
            phone2              = request.POST.get('phone2')
            now                 = datetime.now()

            bank_id             = bank_tb.objects.filter(shop_id=shop_id).exists()
            business_rep_id     = vendor_id.business_rep_id
            added_by            = vendor_id.added_by

            if status== 'Active' and bank_id == False:
                messages.error(request, "Can't activate ,shop did't have any ban account")
                return redirect('list-shops')

           
            if image_file.is_valid():
                image                   = image_file.cleaned_data['image']
                mymodel                 = shops_tb.objects.get(id=shop_id)
                mymodel.image           = image
                mymodel.save()

                get_shop                = shops_tb.objects.all().filter(id=shop_id).get()
                shop_images_tb.objects.all().filter(shop_id=shop_id,is_shop_featured=True).update(image=get_shop.image,updated_at=now)

            if image_file1.is_valid():
                image1                  = image_file1.cleaned_data['image1']
                mymodel                 = shops_tb.objects.get(id=shop_id)
                mymodel.gst_image       = image1
                mymodel.save()

            if image_file2.is_valid():
                image2                  = image_file2.cleaned_data['image2']
                mymodel                 = shops_tb.objects.get(id=shop_id)
                mymodel.license_image   = image2
                mymodel.save()

            if image_file3.is_valid():
                image3                  = image_file3.cleaned_data['image3']
                mymodel                 = shops_tb.objects.get(id=shop_id)
                mymodel.banner_image    = image3
                mymodel.save()

            # geolocator                  = Nominatim(user_agent="geoapiExercises")
            # getlocation                 = geolocator.reverse(latitude+","+longitude)
            # getaddress                  = getlocation.raw['address']
            # country                     = getaddress.get('country', '')
            # state                       = getaddress.get('state', '')
            # city                        = getaddress.get('city', '')
            # if(not city):
            #     city                    = getaddress.get('county', '')
            # pin_code                    = getaddress.get('postcode', '')


            # Make the curl request
            response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng="+latitude+","+longitude+"&key=AIzaSyA6sfxAGWorlekK-rkolU152WkN5mzn76A")

            # Parse the JSON response
            location_data = json.loads(response.text)
            # Extract the country, state, and city information
            for result in location_data['results']:
                for component in result['address_components']:
                    if "country" in component['types']:
                        country     = component['long_name']
                    elif "administrative_area_level_1" in component['types']:
                        state       = component['long_name']
                    elif "administrative_area_level_3" in component['types']:
                        city        = component['long_name']
                    elif "postal_code" in component['types']:
                        pin_code    = component['long_name']


            shops_tb.objects.all().filter(id=shop_id).update(name=name,vendor_id=vendor_id,category_id=category_id,gst_number=gst_number,address=address,latitude=latitude,longitude=longitude,location=location,radius=radius,commission=commission,opening_time=opening_time,closing_time=closing_time,is_featured=is_featured,status=status,license_number=license_number,wallet_amount=wallet_amount,gst_pct=gst_pct,country=country,state=state,city=city,pin_code=pin_code,website_url=website_url,phone1=phone1,phone2=phone2,business_rep_id=business_rep_id,added_by=added_by,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-shops')
        else:
            shop_id             = request.GET['id']
            shop_data           = shops_tb.objects.all().filter(id=shop_id)
            vendors_list        = vendors_tb.objects.all()
            categroy_list       = category_tb.objects.all()
            
            return render(request,'admin/edit_shop.html',{'shop_data' : shop_data,'vendors_list':vendors_list,'categroy_list':categroy_list})
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteShop(request):
    if request.session.has_key('adminId'):
        shop_id     = request.GET['id']
        fromReg     = shops_tb.objects.all().filter(id=shop_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-shops')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-shops')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listManagers(request):
    if request.session.has_key('adminId'):
        manager_list    = manager_tb.objects.all().order_by('-id')

        #-- Pagination
        paginator       = Paginator(manager_list, per_page=20)
        page_number     = request.GET.get('page')
        page            = paginator.get_page(page_number)
        #-- Pagination

        return render(request,'admin/list_manager.html',{'page' : page})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewManager(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            name                = request.POST['name']
            phone               = request.POST['phone']
            email               = request.POST['email']
            auto_password       = request.POST.get('auto_password')
            password            = request.POST.get('password')
            get_vendor_id       = request.POST['vendor_id']
            vendor_id           = vendors_tb.objects.get(id=get_vendor_id)
            get_shop_id         = request.POST['shop_id']
            shop_id             = shops_tb.objects.get(id=get_shop_id)
            now                 = datetime.now()

            get_manager         = manager_tb.objects.all().filter(email=email)
            if get_manager:
                messages.error(request, 'Email already exist')
                return redirect('add-manager')
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

                insert_data             = manager_tb(name=name,phone=phone,email=email,password=hash_password,vendor_id=vendor_id,shop_id=shop_id,created_at=now,updated_at=now)
                insert_data.save()
                messages.success(request, 'Successfully added.')

                return redirect('list-managers')
        else:
            vendors_list        = vendors_tb.objects.all()
            shop_list           = vendors_tb.objects.all()
            return render(request,'admin/add_manager.html',{'vendors_list':vendors_list,'shop_list':shop_list})
    else:
        return redirect('admin-login')

    

def getVendorShop(request):
    if request.session.has_key('adminId'):
        vendor_id   = request.GET['vendor_id']
        get_data    = shops_tb.objects.all().filter(vendor_id=vendor_id).values()

        return  JsonResponse({"models_to_return": list(get_data)})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateManager(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            manager_id      = request.GET['id']
            name            = request.POST['name']
            phone           = request.POST['phone']
            email           = request.POST['email']
            get_vendor_id   = request.POST['vendor_id']
            vendor_id       = vendors_tb.objects.get(id=get_vendor_id)
            get_shop_id     = request.POST['shop_id']
            shop_id         = shops_tb.objects.get(id=get_shop_id)
            status          = request.POST['status']

            now             = datetime.now()

            get_manager     = manager_tb.objects.all().filter(email=email).exclude(id=manager_id)

            if get_manager:
                messages.error(request, 'Email already exist')
                return redirect('/edit-manager/?id='+ str(manager_id))
            else:
                manager_tb.objects.all().filter(id=manager_id).update(name=name,phone=phone,email=email,vendor_id=vendor_id,shop_id=shop_id,status=status,updated_at=now)

                messages.success(request, 'Changes successfully updated.')
                return redirect('list-managers')
        else:
            manager_id      = request.GET['id']
            manager_data    = manager_tb.objects.all().filter(id=manager_id)
            vendors_list    = vendors_tb.objects.all()

            for manager in manager_data:
                get_shops   = shops_tb.objects.all().filter(vendor_id=manager.vendor_id.id).values()
            
            return render(request,'admin/edit_manager.html',{'manager_data' : manager_data,'get_shops':get_shops,'vendors_list':vendors_list})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateManagerPassword(request):
    if request.session.has_key('adminId'):
        manager_id      = request.GET['id']
        password        = request.POST['new_password']
        now             = datetime.now()

        # password hashchecked
        hash_password   = make_password(password)
        manager_tb.objects.all().filter(id=manager_id).update(password=hash_password,updated_at=now)

        messages.success(request, 'Password update successfully')
        return redirect('/edit-manager/?id='+ str(manager_id))
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteManager(request):
    if request.session.has_key('adminId'):
        manager_id  = request.GET['id']
        fromReg     = manager_tb.objects.all().filter(id=manager_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-managers')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-managers')
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listBank(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            vendor_id   = request.POST['vendor_id']
            bank_list   = bank_tb.objects.all().filter(vendor_id=vendor_id).order_by('-id')
        else:
            vendor_id   = None
            bank_list   = bank_tb.objects.all().order_by('-id')

        vendor_list     = vendors_tb.objects.all()

        #-- Pagination
        paginator       = Paginator(bank_list, per_page=20)
        if request.method == 'POST':
            page_number = request.POST.get('page')
        else:
            page_number = request.GET.get('page')
        page            = paginator.get_page(page_number)
        #-- Pagination

        return render(request,'admin/list_bank.html',{'page' : page,'vendor_list' : vendor_list,'vendor_id':vendor_id})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewBank(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            name                = request.POST['name']
            get_vendor_id       = request.POST['vendor_id']
            vendor_id           = vendors_tb.objects.get(id=get_vendor_id)
            get_shop_id         = request.POST['shop_id']
            shop_id             = shops_tb.objects.get(id=get_shop_id)
            account_number      = request.POST['account_number']
            account_type        = request.POST['account_type']
            ifsc_code           = request.POST['ifsc_code']
            razorpay_id         = request.POST['razorpay_id']
            image_file          = imgForm(request.POST,request.FILES)
            image               = None
            now                 = datetime.now()

            get_data            = bank_tb.objects.filter(shop_id=shop_id).exists()

            if get_data == True:
                messages.error(request, 'This shop already have bank account')
                return redirect('add-bank')

            if image_file.is_valid():
                image           = image_file.cleaned_data['image']

            insert_data         = bank_tb(name=name,vendor_id=vendor_id,shop_id=shop_id,account_number=account_number,account_type=account_type,ifsc_code=ifsc_code,razorpay_id=razorpay_id,cheque_copy=image,created_at=now,updated_at=now)
            insert_data.save()
            messages.success(request, 'Successfully added.')

            return redirect('list-bank')
        else:
            vendors_list        = vendors_tb.objects.all()
            shop_list           = shops_tb.objects.all()
            return render(request,'admin/add_bank.html',{'vendors_list':vendors_list,'shop_list':shop_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateBank(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            bank_id         = request.GET['id']
            name            = request.POST['name']
            get_vendor_id   = request.POST['vendor_id']
            vendor_id       = vendors_tb.objects.get(id=get_vendor_id)
            get_shop_id     = request.POST['shop_id']
            shop_id         = shops_tb.objects.get(id=get_shop_id)
            account_number  = request.POST['account_number']
            account_type    = request.POST['account_type']
            ifsc_code       = request.POST['ifsc_code']
            razorpay_id     = request.POST['razorpay_id']
            status          = request.POST['status']
            image_file      = imgForm(request.POST,request.FILES)

            now             = datetime.now()

            get_data        = bank_tb.objects.all().filter(shop_id=shop_id).exclude(id=bank_id)
            
            if get_data:
                messages.error(request, 'This shop already have bank account')
                return redirect('/edit-bank/?id='+ str(bank_id))

            if image_file.is_valid():
                image                   = image_file.cleaned_data['image']
                mymodel                 = bank_tb.objects.get(id=bank_id)
                mymodel.cheque_copy     = image
                mymodel.save()
            
            bank_tb.objects.all().filter(id=bank_id).update(name=name,vendor_id=vendor_id,shop_id=shop_id,account_number=account_number,account_type=account_type,ifsc_code=ifsc_code,razorpay_id=razorpay_id,status=status,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-bank')
        else:
            bank_id         = request.GET['id']
            bank_data       = bank_tb.objects.all().filter(id=bank_id)
            vendors_list    = vendors_tb.objects.all()
            shop_list       = []

            for bank in bank_data:
                shop_list   = shops_tb.objects.all().filter(vendor_id=bank.vendor_id)

            for bank in bank_data:
                get_shops   = shops_tb.objects.all().filter(vendor_id=bank.vendor_id.id).values()
            
            return render(request,'admin/edit_bank.html',{'bank_data' : bank_data,'get_shops':get_shops,'vendors_list':vendors_list,'shop_list':shop_list})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteBank(request):
    if request.session.has_key('adminId'):
        bank_id     = request.GET['id']
        fromReg     = bank_tb.objects.all().filter(id=bank_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-bank')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-bank')
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listUserBank(request):
    if request.session.has_key('adminId'):
        bank_list       = user_bank_tb.objects.all().order_by('-id')

        #-- Pagination
        paginator       = Paginator(bank_list, per_page=20)
        if request.method == 'POST':
            page_number = request.POST.get('page')
        else:
            page_number = request.GET.get('page')
        page            = paginator.get_page(page_number)
        #-- Pagination

        return render(request,'admin/list_user_bank.html',{'page' : page})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewUserBank(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            name                = request.POST['name']
            get_user_id         = request.POST['user_id']
            user_id             = user_data_tb.objects.get(id=get_user_id)
            account_number      = request.POST['account_number']
            account_type        = request.POST['account_type']
            ifsc_code           = request.POST['ifsc_code']
            razorpay_id         = request.POST['razorpay_id']
            image_file          = imgForm(request.POST,request.FILES)
            image               = None
            now                 = datetime.now()

            get_data            = user_bank_tb.objects.filter(user_id=user_id).exists()

            if get_data == True:
                messages.error(request, 'This shop already have bank account')
                return redirect('add-user-bank')

            if image_file.is_valid():
                image           = image_file.cleaned_data['image']

            insert_data         = user_bank_tb(name=name,user_id=user_id,account_number=account_number,account_type=account_type,ifsc_code=ifsc_code,razorpay_id=razorpay_id,cheque_copy=image,created_at=now,updated_at=now)
            insert_data.save()
            messages.success(request, 'Successfully added.')

            return redirect('list-user-bank')
        else:
            user_list           = user_data_tb.objects.all().exclude(user_role_id__isnull=True)

            return render(request,'admin/add_user_bank.html',{'user_list':user_list})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateUserBank(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            bank_id         = request.GET['id']
            name            = request.POST['name']
            get_user_id     = request.POST['user_id']
            user_id         = user_data_tb.objects.get(id=get_user_id)
            account_number  = request.POST['account_number']
            account_type    = request.POST['account_type']
            ifsc_code       = request.POST['ifsc_code']
            razorpay_id     = request.POST['razorpay_id']
            status          = request.POST['status']
            image_file      = imgForm(request.POST,request.FILES)
            now             = datetime.now()

            get_data        = user_bank_tb.objects.all().filter(user_id=user_id).exclude(id=bank_id)
            
            if get_data:
                messages.error(request, 'This shop already have bank account')
                return redirect('/edit-user-bank/?id='+ str(bank_id))

            if image_file.is_valid():
                image                   = image_file.cleaned_data['image']
                mymodel                 = user_bank_tb.objects.get(id=bank_id)
                mymodel.cheque_copy     = image
                mymodel.save()
            
            user_bank_tb.objects.all().filter(id=bank_id).update(name=name,user_id=user_id,account_number=account_number,account_type=account_type,ifsc_code=ifsc_code,razorpay_id=razorpay_id,status=status,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-user-bank')
        else:
            bank_id         = request.GET['id']
            bank_data       = user_bank_tb.objects.all().filter(id=bank_id)
            user_list       = user_data_tb.objects.all().exclude(user_role_id__isnull=True)

            return render(request,'admin/edit_user_bank.html',{'bank_data' : bank_data,'user_list':user_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteUserBank(request):
    if request.session.has_key('adminId'):
        bank_id     = request.GET['id']
        fromReg     = user_bank_tb.objects.all().filter(id=bank_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-user-bank')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-user-bank')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listOffers(request):
    if request.session.has_key('adminId'):
        offer_list      = offer_tb.objects.all().order_by('-id')

        #-- Pagination
        paginator       = Paginator(offer_list, per_page=20)
        page_number     = request.GET.get('page')
        page            = paginator.get_page(page_number)
        #-- Pagination

        return render(request,'admin/list_offer.html',{'page' : page})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewOffer(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            name                = request.POST['name']
            get_shop_id         = request.POST['shop_id']
            shop_id             = shops_tb.objects.get(id=get_shop_id)
            discount            = request.POST['discount']
            description         = request.POST['description']
            image_file          = imgForm(request.POST,request.FILES)
            now                 = datetime.now()
            image               = None

            if image_file.is_valid():
                image           = image_file.cleaned_data['image']

            insert_data         = offer_tb(name=name,shop_id=shop_id,discount=discount,description=description,image=image,created_at=now,updated_at=now)
            insert_data.save()
            messages.success(request, 'Successfully added.')

            return redirect('list-offer')
        else:
            shop_list           = shops_tb.objects.all()
            return render(request,'admin/add_offer.html',{'shop_list':shop_list})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateOffer(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            offer_id            = request.GET['id']
            name                = request.POST['name']
            get_shop_id         = request.POST['shop_id']
            shop_id             = shops_tb.objects.get(id=get_shop_id)
            discount            = request.POST['discount']
            description         = request.POST['description']
            status              = request.POST['status']
            image_file          = imgForm(request.POST,request.FILES)
            now                 = datetime.now()

           
            if image_file.is_valid():
                image                   = image_file.cleaned_data['image']
                mymodel                 = offer_tb.objects.get(id=offer_id)
                mymodel.image           = image
                mymodel.save()

            offer_tb.objects.all().filter(id=offer_id).update(name=name,shop_id=shop_id,discount=discount,description=description,status=status,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-offer')
        else:
            offer_id            = request.GET['id']
            offer_data          = offer_tb.objects.all().filter(id=offer_id)
            shop_list           = shops_tb.objects.all()
            
            return render(request,'admin/edit_offer.html',{'offer_data' : offer_data,'shop_list':shop_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteOffer(request):
    if request.session.has_key('adminId'):
        offer_id    = request.GET['id']
        fromReg     = offer_tb.objects.all().filter(id=offer_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-offer')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-offer')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listShopGalleryImages(request):
    if request.session.has_key('adminId'):
        images_list     = shop_images_tb.objects.all().order_by('-id')

        #-- Pagination
        paginator       = Paginator(images_list, per_page=20)
        page_number     = request.GET.get('page')
        page            = paginator.get_page(page_number)
        #-- Pagination

        return render(request,'admin/list_shop_images.html',{'page' : page})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewShopImage(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            get_shop_id         = request.POST['shop_id']
            shop_id             = shops_tb.objects.get(id=get_shop_id)
            image_file          = imgForm(request.POST,request.FILES)
            now                 = datetime.now()
            image               = None

            if image_file.is_valid():
                image           = image_file.cleaned_data['image']

            insert_data         = shop_images_tb(shop_id=shop_id,image=image,created_at=now,updated_at=now)
            insert_data.save()
            messages.success(request, 'Successfully added.')

            return redirect('list-images')
        else:
            shop_list           = shops_tb.objects.all()
            return render(request,'admin/add_shop_images.html',{'shop_list':shop_list})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateShopImage(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            image_id            = request.GET['id']
            get_shop_id         = request.POST['shop_id']
            shop_id             = shops_tb.objects.get(id=get_shop_id)
            image_file          = imgForm(request.POST,request.FILES)
            now                 = datetime.now()

            get_shop_image      = shop_images_tb.objects.all().filter(id=image_id).get()

            if get_shop_image.is_shop_featured == True and get_shop_image.shop_id.id != get_shop_id:
                messages.error(request, "Don't try to change shop, this image was used for other shop featured image")
                return redirect('list-images')
           
            if image_file.is_valid():
                image                   = image_file.cleaned_data['image']
                mymodel                 = shop_images_tb.objects.get(id=image_id)
                mymodel.image           = image
                mymodel.save()

                get_shop_image          = shop_images_tb.objects.all().filter(id=image_id).get()

                if get_shop_image.is_shop_featured == True:
                    shops_tb.objects.all().filter(id=get_shop_image.shop_id.id).update(image=get_shop_image.image,updated_at=now)

            shop_images_tb.objects.all().filter(id=image_id).update(shop_id=shop_id,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-images')
        else:
            image_id            = request.GET['id']
            image_data          = shop_images_tb.objects.all().filter(id=image_id)
            shop_list           = shops_tb.objects.all()
            
            return render(request,'admin/edit_shop_image.html',{'image_data' : image_data,'shop_list':shop_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteShopImage(request):
    if request.session.has_key('adminId'):
        image_id    = request.GET['id']
        fromReg     = shop_images_tb.objects.all().filter(id=image_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-images')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-images')
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateTermsAndConditions(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            terms_id        = request.POST['id']
            title           = request.POST['title']
            description     = request.POST['description']
            now             = datetime.now()

            if terms_id:
                terms_and_conditions_tb.objects.all().filter(id=terms_id).update(title=title,description=description,updated_at=now)
            else:
                insert_data = terms_and_conditions_tb(title=title,description=description,created_at=now,updated_at=now)
                insert_data.save()

            messages.success(request, 'Changes successfully updated.')
            return redirect('terms')
        else:
            get_data        = terms_and_conditions_tb.objects.all()
            data            = []

            if get_data:
                for x in get_data:
                    data    =   {
                                    'id'            : x.id,
                                    'title'         : x.title,
                                    'description'   : x.description,
                                } 
            
            return render(request,'admin/edit_terms.html',{'data' : data})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updatePrivacyPolicy(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            policy_id       = request.POST['id']
            title           = request.POST['title']
            description     = request.POST['description']
            now             = datetime.now()

            if policy_id:
                privacy_policy_tb.objects.all().filter(id=policy_id).update(title=title,description=description,updated_at=now)
            else:
                insert_data = privacy_policy_tb(title=title,description=description,created_at=now,updated_at=now)
                insert_data.save()

            messages.success(request, 'Changes successfully updated.')
            return redirect('policy')
        else:
            get_data        = privacy_policy_tb.objects.all()
            data            = []

            if get_data:
                for x in get_data:
                    data    =   {
                                    'id'            : x.id,
                                    'title'         : x.title,
                                    'description'   : x.description,
                                } 
            
            return render(request,'admin/edit_privacy.html',{'data' : data})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateContactUs(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            contact_id  = request.POST['id']
            email       = request.POST['email']
            mobile      = request.POST['phone']
            address     = request.POST['address']
            location    = request.POST['location']
            latitude    = request.POST['latitude']
            longitude   = request.POST['longitude']
            now         = datetime.now()

            if contact_id:
                contact_us_tb.objects.all().filter(id=contact_id).update(email=email,mobile=mobile,address=address,location=location,latitude=latitude,longitude=longitude,updated_at=now)
            else:
                insert_data = contact_us_tb(email=email,mobile=mobile,address=address,location=location,latitude=latitude,longitude=longitude,created_at=now,updated_at=now)
                insert_data.save()

            messages.success(request, 'Changes successfully updated.')
            return redirect('contacts')
        else:
            get_data        = contact_us_tb.objects.all()
            data            = []

            if get_data:
                for x in get_data:
                    data    =   {
                                    'id'        : x.id,
                                    'email'     : x.email,
                                    'mobile'    : x.mobile,
                                    'address'   : x.address,
                                    'location'  : x.location,
                                    'latitude'  : x.latitude,
                                    'longitude' : x.longitude
                                } 
            
            return render(request,'admin/edit_contact_us.html',{'data' : data})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listUserContacts(request):
    if request.session.has_key('adminId'):
        user_contact_list   = user_contacts_tb.objects.all().order_by('-id')
        return render(request,'admin/list_user_contacts.html',{'user_contact_list' : user_contact_list})
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listInvoices(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            user_id     = '' if not request.POST.get('user_id') else request.POST.get('user_id')
            search_key  = request.POST.get('search_key')
            date_from   = None if not request.POST.get('date_from') else datetime.strptime(request.POST.get('date_from'), "%Y-%m-%d")
            date_to     = None if not request.POST.get('date_to') else datetime.strptime(request.POST.get('date_to'), "%Y-%m-%d")

            if search_key and date_from and user_id:
                invoice_list= (
                                invoice_data_tb.objects.all()
                                .filter(invoice_number__icontains=search_key,invoice_date__date__gte=date_from.date(), invoice_date__date__lte=date_to.date(),user_id=user_id)
                                .exclude(invoice_date__date=date_to.date(), invoice_date__time__gt=time(23, 59, 59))
                                .order_by('-id')
                            )
            elif search_key and date_from:
                invoice_list= (
                                invoice_data_tb.objects.all()
                                .filter(invoice_number__icontains=search_key,invoice_date__date__gte=date_from.date(), invoice_date__date__lte=date_to.date())
                                .exclude(invoice_date__date=date_to.date(), invoice_date__time__gt=time(23, 59, 59))
                                .order_by('-id')
                            )
            elif user_id and date_from:
                invoice_list= (
                                invoice_data_tb.objects.all()
                                .filter(user_id=user_id,invoice_date__date__gte=date_from.date(), invoice_date__date__lte=date_to.date())
                                .exclude(invoice_date__date=date_to.date(), invoice_date__time__gt=time(23, 59, 59))
                                .order_by('-id')
                            )
            elif search_key and user_id:
                invoice_list= invoice_data_tb.objects.all().filter(invoice_number__icontains=search_key,user_id=user_id).order_by('-id')
            elif search_key:
                invoice_list= invoice_data_tb.objects.all().filter(invoice_number__icontains=search_key).order_by('-id')
            elif user_id:
                invoice_list= invoice_data_tb.objects.all().filter(user_id=user_id).order_by('-id')
            elif date_from:
                invoice_list= (
                                invoice_data_tb.objects.all()
                                .filter(invoice_date__date__gte=date_from.date(), invoice_date__date__lte=date_to.date())
                                .exclude(invoice_date__date=date_to.date(), invoice_date__time__gt=time(23, 59, 59))
                                .order_by('-id')
                            )
        else:
            search_key  = ''
            date_from   = None
            date_to     = None
            user_id     = ''

            invoice_list= invoice_data_tb.objects.all().order_by('-id')

        get_data_user               = invoice_data_tb.objects.all().values('user_id').distinct()
        all_users                   = []
        for data in get_data_user:
            wallet_transactions_tb.objects
            user_data               = user_data_tb.objects.get(id=data['user_id'])
            all_users.append(user_data)
                

        #-- Pagination
        paginator               = Paginator(invoice_list, per_page=20)
        if request.method == 'POST':
            page_number = request.POST.get('page')
        else:
            page_number = request.GET.get('page')
        page                    = paginator.get_page(page_number)
        #-- Pagination

        return render(request,'admin/list_invoice.html',{'page' : page,'search_key' :search_key,'date_from' :date_from,'date_to':date_to,'all_users':all_users,'user_id':user_id})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateInvoiceStatus(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            invoice_id      = request.POST['id']
            status          = request.POST['status']
            pre_tax_amount  = request.POST['pre_tax_amount'] 
            now             = datetime.now()

            invoice_data    = invoice_data_tb.objects.all().filter(id=invoice_id).get()

            invoice_data_tb.objects.all().filter(id=invoice_id).update(pre_tax_amount=pre_tax_amount,updated_at=now)
            if invoice_data.status != status and status == "Approve":
                response     = updateWalletAmount(invoice_id,None)

                if(response['success'] == False):
                    messages.error(request, response['message'])
                    return redirect('list-invoice')
            else:
                invoice_data_tb.objects.all().filter(id=invoice_id).update(status=status,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-invoice')
        else:
            invoice_id      = request.GET['id']
            invoice_data    = invoice_data_tb.objects.all().filter(id=invoice_id).get()
            vendors_list    = vendors_tb.objects.all()
            users_list      = user_data_tb.objects.all()
            shop_list       = shops_tb.objects.all()
           
            return render(request,'admin/edit_invoice.html',{'invoice_data' : invoice_data,'vendors_list':vendors_list,'users_list':users_list,'shop_list':shop_list})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteInvoice(request):
    if request.session.has_key('adminId'):
        invoice_id  = request.GET['id']
        fromReg     = invoice_data_tb.objects.all().filter(id=invoice_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-invoice')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-invoice')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listWalletTransactions(request):
    if request.session.has_key('adminId'):

        if request.method=="POST":
            user_id     = '' if not request.POST.get('user_id') else request.POST.get('user_id')
            date_from   = None if not request.POST.get('date_from') else datetime.strptime(request.POST.get('date_from'), "%Y-%m-%d")
            date_to     = None if not request.POST.get('date_to') else datetime.strptime(request.POST.get('date_to'), "%Y-%m-%d")
            now         = datetime.now()
            search_key  = request.POST.get('search_key')

            total_credit= ''

            if search_key and date_from and user_id:
                # get_wallet_data     = getUserWalletAmount(user_id,now)
                # total_credit        = get_wallet_data['total_balance']

                invoice_ids         = invoice_data_tb.objects.all().filter(invoice_number__icontains=search_key).values('id')
                id_list             = [obj['id'] for obj in invoice_ids]
                
                transactions_list   = (
                                        wallet_transactions_tb.objects
                                        .filter(invoice_id__in=id_list,user_id=user_id,created_at__date__gte=date_from.date(), created_at__date__lte=date_to.date())
                                        .exclude(created_at__date=date_to.date(), created_at__time__gt=time(23, 59, 59))
                                        .order_by('-id')
                                    )

            elif user_id and date_from:
                # get_wallet_data     = getUserWalletAmount(user_id,now)
                # total_credit        = get_wallet_data['total_balance']

                transactions_list   = (
                                        wallet_transactions_tb.objects
                                        .filter(user_id=user_id,created_at__date__gte=date_from.date(), created_at__date__lte=date_to.date())
                                        .exclude(created_at__date=date_to.date(), created_at__time__gt=time(23, 59, 59))
                                        .order_by('-id')
                                    )
            elif search_key and date_from:
                # get_wallet_data     = getUserWalletAmount(user_id,now)
                # total_credit        = get_wallet_data['total_balance']
                invoice_ids         = invoice_data_tb.objects.all().filter(invoice_number__icontains=search_key).values('id')
                id_list             = [obj['id'] for obj in invoice_ids]

                transactions_list   = (
                                        wallet_transactions_tb.objects
                                        .filter(invoice_id__in=id_list,created_at__date__gte=date_from.date(), created_at__date__lte=date_to.date())
                                        .exclude(created_at__date=date_to.date(), created_at__time__gt=time(23, 59, 59))
                                        .order_by('-id')
                                    )

            elif user_id and search_key:
                invoice_ids         = invoice_data_tb.objects.all().filter(invoice_number__icontains=search_key).values('id')
                id_list             = [obj['id'] for obj in invoice_ids]


                transactions_list   = wallet_transactions_tb.objects.all().filter(invoice_id__in=id_list,user_id=user_id).order_by('-id')
            elif user_id:
                get_wallet_data     = getUserWalletAmount(user_id,now)
                total_credit        = get_wallet_data['total_balance']

                transactions_list   = wallet_transactions_tb.objects.all().filter(user_id=user_id).order_by('-id')
            elif date_from:
                transactions_list   = (
                                        wallet_transactions_tb.objects
                                        .filter(created_at__date__gte=date_from.date(), created_at__date__lte=date_to.date())
                                        .exclude(created_at__date=date_to.date(), created_at__time__gt=time(23, 59, 59))
                                        .order_by('-id')
                                    )

            elif search_key:
                invoice_ids         = invoice_data_tb.objects.all().filter(invoice_number__icontains=search_key).values('id')
                id_list             = [obj['id'] for obj in invoice_ids]

                transactions_list   = wallet_transactions_tb.objects.all().filter(invoice_id__in=id_list).order_by('-id')
        else:
            user_id                 = ''
            date_from               = None
            date_to                 = None
            search_key              = ''
            total_credit            = ''

            transactions_list       = wallet_transactions_tb.objects.all().order_by('-id')

        get_data_user               = wallet_transactions_tb.objects.all().values('user_id').distinct()
        all_users                   = []
        for data in get_data_user:
            wallet_transactions_tb.objects
            user_data               = user_data_tb.objects.get(id=data['user_id'])
            all_users.append(user_data)

        
        #-- Pagination
        paginator               = Paginator(transactions_list, per_page=20)
        if request.method == 'POST':
            page_number = request.POST.get('page')
        else:
            page_number = request.GET.get('page')
        page                    = paginator.get_page(page_number)
        #-- Pagination

        return render(request,'admin/list_wallet_transactions.html',{'page' : page,'user_id':user_id,'date_from':date_from,'date_to':date_to,'all_users':all_users,'total_credit':total_credit,'search_key':search_key})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateWalletTransaction(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            transaction_id  = request.POST['id']
            status          = request.POST['status']
            expiry_date     = request.POST['expiry_date']
            now             = datetime.now()

            wallet_transactions_tb.objects.all().filter(id=transaction_id).update(status=status,expiry_date=expiry_date,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-wallet-transaction')
        else:
            transaction_id  = request.GET['id']
            transaction_data= wallet_transactions_tb.objects.all().filter(id=transaction_id).get()
            vendors_list    = vendors_tb.objects.all()
            users_list      = user_data_tb.objects.all()
            shop_list       = shops_tb.objects.all()
            invoice_list    = invoice_data_tb.objects.all()
           
            return render(request,'admin/edit_wallet_transaction.html',{'transaction_data' : transaction_data,'vendors_list':vendors_list,'users_list':users_list,'shop_list':shop_list,'invoice_list':invoice_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteWalletTransaction(request):
    if request.session.has_key('adminId'):
        transaction_id  = request.GET['id']
        fromReg         = wallet_transactions_tb.objects.all().filter(id=transaction_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-wallet-transaction')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-wallet-transaction')
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listBankTransactions(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            vendor_id   = '' if not request.POST.get('vendor_id') else request.POST.get('vendor_id')
            date_from   = None if not request.POST.get('date_from') else datetime.strptime(request.POST.get('date_from'), "%Y-%m-%d")
            date_to     = None if not request.POST.get('date_to') else datetime.strptime(request.POST.get('date_to'), "%Y-%m-%d")
            now         = datetime.now()
            search_key  = request.POST.get('search_key')
            
            if search_key and date_from and vendor_id:
                invoice_ids         = invoice_data_tb.objects.all().filter(invoice_number__icontains=search_key).values('id')
                id_list             = [obj['id'] for obj in invoice_ids]
                
                transactions_list   = (
                                        bank_transactions_tb.objects
                                        .filter(invoice_id__in=id_list,vendor_id=vendor_id,created_at__date__gte=date_from.date(), created_at__date__lte=date_to.date())
                                        .exclude(created_at__date=date_to.date(), created_at__time__gt=time(23, 59, 59))
                                        .order_by('-id')
                                    )
            elif vendor_id and date_from:
                transactions_list   = (
                                        bank_transactions_tb.objects
                                        .filter(vendor_id=vendor_id,created_at__date__gte=date_from.date(), created_at__date__lte=date_to.date())
                                        .exclude(created_at__date=date_to.date(), created_at__time__gt=time(23, 59, 59))
                                        .order_by('-id')
                                    )
            elif search_key and date_from:
                invoice_ids         = invoice_data_tb.objects.all().filter(invoice_number__icontains=search_key).values('id')
                id_list             = [obj['id'] for obj in invoice_ids]

                transactions_list   = (
                                        bank_transactions_tb.objects
                                        .filter(invoice_id__in=id_list,created_at__date__gte=date_from.date(), created_at__date__lte=date_to.date())
                                        .exclude(created_at__date=date_to.date(), created_at__time__gt=time(23, 59, 59))
                                        .order_by('-id')
                                    )
            elif search_key and vendor_id:
                invoice_ids         = invoice_data_tb.objects.all().filter(invoice_number__icontains=search_key).values('id')
                id_list             = [obj['id'] for obj in invoice_ids]

                transactions_list   = bank_transactions_tb.objects.all().filter(invoice_id__in=id_list,vendor_id=vendor_id).order_by('-id')
            elif vendor_id:
                transactions_list   = bank_transactions_tb.objects.all().filter(vendor_id=vendor_id).order_by('-id')
            elif search_key:
                invoice_ids         = invoice_data_tb.objects.all().filter(invoice_number__icontains=search_key).values('id')
                id_list             = [obj['id'] for obj in invoice_ids]

                transactions_list   = bank_transactions_tb.objects.all().filter(invoice_id__in=id_list).order_by('-id')
            elif date_from:
                transactions_list   = (
                                        bank_transactions_tb.objects
                                        .filter(created_at__date__gte=date_from.date(), created_at__date__lte=date_to.date())
                                        .exclude(created_at__date=date_to.date(), created_at__time__gt=time(23, 59, 59))
                                        .order_by('-id')
                                    )
        else:
            vendor_id               = ''
            date_from               = None
            date_to                 = None
            search_key              = ''

            transactions_list       = bank_transactions_tb.objects.all().order_by('-id')

        get_data_vendor             = bank_transactions_tb.objects.all().values('vendor_id').distinct()
        all_vendors                 = []
        for data in get_data_vendor:
            vendor_data             = vendors_tb.objects.get(id=data['vendor_id'])
            all_vendors.append(vendor_data)

        
        #-- Pagination
        paginator                   = Paginator(transactions_list, per_page=20)
        if request.method == 'POST':
            page_number = request.POST.get('page')
        else:
            page_number = request.GET.get('page')
        page                        = paginator.get_page(page_number)
        #-- Pagination

        return render(request,'admin/list_bank_transactions.html',{'page' : page,'vendor_id':vendor_id,'date_from':date_from,'date_to':date_to,'all_vendors':all_vendors,'search_key':search_key})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateBankTransaction(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            transaction_id  = request.POST['id']
            status          = request.POST['status']
            now             = datetime.now()

            bank_transactions_tb.objects.all().filter(id=transaction_id).update(transaction_status=status,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-bank-transaction')
        else:
            transaction_id  = request.GET['id']
            transaction_data= bank_transactions_tb.objects.all().filter(id=transaction_id).get()
            vendors_list    = vendors_tb.objects.all()
            bank_list       = bank_tb.objects.all()
           
            return render(request,'admin/edit_bank_transaction.html',{'transaction_data' : transaction_data,'vendors_list':vendors_list,'bank_list':bank_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteBankTransaction(request):
    if request.session.has_key('adminId'):
        transaction_id  = request.GET['id']
        fromReg         = bank_transactions_tb.objects.all().filter(id=transaction_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-bank-transactions')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-bank-transactions')
    else:
        return redirect('admin-login')



# @cache_control(no_cache=True,must_revalidate=True,no_store=True)
# def listUsers(request):
#     if request.session.has_key('adminId'):
#         if  request.method=='POST':
#             latitude            = request.POST['latitude']
#             longitude           = request.POST['longitude']
#             location            = request.POST['location']
#             country             = request.POST['country']
#             state               = request.POST['state']
#             district            = request.POST['district']
#             now                 = datetime.now()
            
#             get_users_ids       = []
#             get_users_list      = []

#             get_location_array  = location.split(',')
            
#             if(len(get_location_array) == 1):
#                 loc_type        = "Country"
#                 # get_given_data  = getCountryStateCity(latitude,longitude,loc_type)
#                 get_given_data  = country
#                 get_users_list  = user_data_tb.objects.all().filter(country=get_given_data)
#             elif(len(get_location_array) == 2):
#                 loc_type        = "State"
#                 get_given_data  = state
#                 get_users_list  = user_data_tb.objects.all().filter(state=get_given_data)
#             else:
#                 loc_type        = "City"
#                 get_given_data  = district
#                 get_users_list  = user_data_tb.objects.all().filter(city=get_given_data)

#         else:
#             latitude            = ""
#             longitude           = ""
#             location            = ""
#             country             = ""
#             state               = ""
#             district            = ""
#             now                 = datetime.now()

#             get_users_list      = user_data_tb.objects.all().order_by('-id')

#         users_list              = []

#         for user in get_users_list:
#             get_wallet_data = getUserWalletAmount(user.id,now)

#             users_list.append({
#                     'id'                : user.id,
#                     'name'              : user.name,
#                     'phone'             : user.phone,
#                     'email'             : user.email,
#                     'location'          : user.location,
#                     'profile_image'     : None if not user.profile_image else user.profile_image.url,
#                     'redeemable_points' : get_wallet_data['redeemable_points'],
#                     'status'            : user.active
#                 })

#         users_list.sort(key=lambda x: x.get('redeemable_points'), reverse=True)
#         request_data            = {'latitude':latitude,'longitude':longitude,'location':location,'country':country,'state':state,'district':district}
        
#         #-- Pagination
#         paginator               = Paginator(users_list, per_page=20)
#         if request.method == 'POST':
#             page_number = request.POST.get('page')
#         else:
#             page_number = request.GET.get('page')
#         page                    = paginator.get_page(page_number)
#         #-- Pagination

#         return render(request,'admin/list_users.html',{'page':page,'request_data':request_data})
#     else:
#         return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listUsers(request):
    if request.session.has_key('adminId') or request.session.has_key('userId'):
        if  request.method=='POST':
            user_id             = request.POST.get('user_id')
            latitude            = request.POST.get('latitude')
            longitude           = request.POST.get('longitude')
            location            = request.POST.get('location')
            country             = request.POST.get('country')
            state               = request.POST.get('state')
            district            = request.POST.get('district')
            user_role_id        = request.POST.get('user_role_id')
            now                 = datetime.now()
            
            get_users_ids       = []
            get_users_list      = []

            if location and user_id and user_role_id:
                get_location_array  = location.split(',')
                if(len(get_location_array) == 1):
                    loc_type        = "Country"
                    get_given_data  = country
                    if request.session.has_key('adminId'):
                        get_users_list  = user_data_tb.objects.all().filter(id=user_id,country=get_given_data,user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                    elif request.session.has_key('userId'):
                        get_users_list  = user_data_tb.objects.all().filter(id=user_id,country=get_given_data,added_by=request.session['userId'],user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                elif(len(get_location_array) == 2):
                    loc_type        = "State"
                    get_given_data  = state
                    if request.session.has_key('adminId'):
                        get_users_list  = user_data_tb.objects.all().filter(id=user_id,state=get_given_data,user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                    elif request.session.has_key('userId'):
                        get_users_list  = user_data_tb.objects.all().filter(id=user_id,state=get_given_data,added_by=request.session['userId'],user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                else:
                    loc_type        = "City"
                    get_given_data  = district
                    if request.session.has_key('adminId'):
                        get_users_list  = user_data_tb.objects.all().filter(id=user_id,city=get_given_data,user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                    elif request.session.has_key('userId'):
                        get_users_list  = user_data_tb.objects.all().filter(id=user_id,city=get_given_data,added_by=request.session['userId'],user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
            
            elif location and user_role_id:
                get_location_array  = location.split(',')
                if(len(get_location_array) == 1):
                    loc_type        = "Country"
                    get_given_data  = country
                    if request.session.has_key('adminId'):
                        get_users_list  = user_data_tb.objects.all().filter(country=get_given_data,user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                    elif request.session.has_key('userId'):
                        get_users_list  = user_data_tb.objects.all().filter(country=get_given_data,added_by=request.session['userId'],user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                elif(len(get_location_array) == 2):
                    loc_type        = "State"
                    get_given_data  = state
                    if request.session.has_key('adminId'):
                        get_users_list  = user_data_tb.objects.all().filter(state=get_given_data,user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                    elif request.session.has_key('userId'):
                        get_users_list  = user_data_tb.objects.all().filter(state=get_given_data,added_by=request.session['userId'],user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                else:
                    loc_type        = "City"
                    get_given_data  = district
                    if request.session.has_key('adminId'):
                        get_users_list  = user_data_tb.objects.all().filter(city=get_given_data,user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                    elif request.session.has_key('userId'):
                        get_users_list  = user_data_tb.objects.all().filter(city=get_given_data,added_by=request.session['userId'],user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')

            elif user_id and user_role_id:
                if request.session.has_key('adminId'):
                    get_users_list  = user_data_tb.objects.all().filter(id=user_id,user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                elif request.session.has_key('userId'):
                    get_users_list  = user_data_tb.objects.all().filter(id=user_id,added_by=request.session['userId'],user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                
            elif location and user_id:
                get_location_array  = location.split(',')
                if(len(get_location_array) == 1):
                    loc_type        = "Country"
                    get_given_data  = country
                    if request.session.has_key('adminId'):
                        get_users_list  = user_data_tb.objects.all().filter(id=user_id,country=get_given_data).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                    elif request.session.has_key('userId'):
                        get_users_list  = user_data_tb.objects.all().filter(id=user_id,country=get_given_data,added_by=request.session['userId']).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                elif(len(get_location_array) == 2):
                    loc_type        = "State"
                    get_given_data  = state
                    if request.session.has_key('adminId'):
                        get_users_list  = user_data_tb.objects.all().filter(id=user_id,state=get_given_data).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                    elif request.session.has_key('userId'):
                        get_users_list  = user_data_tb.objects.all().filter(id=user_id,state=get_given_data,added_by=request.session['userId']).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                else:
                    loc_type        = "City"
                    get_given_data  = district
                    if request.session.has_key('adminId'):
                        get_users_list  = user_data_tb.objects.all().filter(id=user_id,city=get_given_data).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                    elif request.session.has_key('userId'):
                        get_users_list  = user_data_tb.objects.all().filter(id=user_id,city=get_given_data,added_by=request.session['userId']).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
            elif location:
                get_location_array  = location.split(',')
                
                if(len(get_location_array) == 1):
                    loc_type        = "Country"
                    # get_given_data  = getCountryStateCity(latitude,longitude,loc_type)
                    get_given_data  = country
                    if request.session.has_key('adminId'):
                        get_users_list  = user_data_tb.objects.all().filter(country=get_given_data).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                    elif request.session.has_key('userId'):
                        get_users_list  = user_data_tb.objects.all().filter(country=get_given_data,added_by=request.session['userId']).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                elif(len(get_location_array) == 2):
                    loc_type        = "State"
                    get_given_data  = state
                    if request.session.has_key('adminId'):
                        get_users_list  = user_data_tb.objects.all().filter(state=get_given_data).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                    elif request.session.has_key('userId'):
                        get_users_list  = user_data_tb.objects.all().filter(state=get_given_data,added_by=request.session['userId']).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                else:
                    loc_type        = "City"
                    get_given_data  = district
                    if request.session.has_key('adminId'):
                        get_users_list  = user_data_tb.objects.all().filter(city=get_given_data).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                    elif request.session.has_key('userId'):
                        get_users_list  = user_data_tb.objects.all().filter(city=get_given_data,added_by=request.session['userId']).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
            elif user_id:
                if request.session.has_key('adminId'):
                    get_users_list      = user_data_tb.objects.all().filter(id=user_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                elif request.session.has_key('userId'):
                    get_users_list      = user_data_tb.objects.all().filter(id=user_id,added_by=request.session['userId']).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
            elif user_role_id:
                if request.session.has_key('adminId'):
                    get_users_list      = user_data_tb.objects.all().filter(user_role_id=user_role_id).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
                elif request.session.has_key('userId'):
                    get_users_list      = user_data_tb.objects.all().filter(user_role_id=user_role_id,added_by=request.session['userId']).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
        else:
            latitude            = ""
            longitude           = ""
            location            = ""
            country             = ""
            state               = ""
            district            = ""
            user_id             = ""
            user_role_id        = ""
            now                 = datetime.now()

            if request.session.has_key('adminId'):
                get_users_list  =  user_data_tb.objects.annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
            elif request.session.has_key('userId'):
                get_users_list  =  user_data_tb.objects.filter(added_by=request.session['userId']).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')

        users_list              = []

        #-- Pagination
        paginator               = Paginator(get_users_list, per_page=20)
        if request.method == 'POST':
            page_number = request.POST.get('page')
        else:
            page_number = request.GET.get('page')
        page                    = paginator.get_page(page_number)
        #-- Pagination

        # for user in page:
        #     # get_wallet_data = getUserWalletAmount(user.id,now)

        #     users_list.append({
        #             'id'                : user.id,
        #             'name'              : user.name,
        #             'phone'             : user.phone,
        #             'email'             : user.email,
        #             'location'          : user.location,
        #             'profile_image'     : None if not user.profile_image else user.profile_image.url,
        #             # 'redeemable_points' : get_wallet_data['redeemable_points'],
        #             'total_points'      : round(float(user.wallet_amount),2) if user.wallet_amount else '',
        #             'status'            : user.active
        #         })


        # users_list.sort(key=lambda x: x.get('redeemable_points'), reverse=True)
        request_data            = {'latitude':latitude,'longitude':longitude,'location':location,'country':country,'state':state,'district':district,'user_id':user_id,'user_role_id':user_role_id}
        all_user_roles          = user_roles_data_tb.objects.all()

        if request.session.has_key('adminId'):
            all_users           =  user_data_tb.objects.annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
        elif request.session.has_key('userId'):
            all_users           =  user_data_tb.objects.filter(added_by=request.session['userId']).annotate(wallet_amount_float=Cast('wallet_amount', FloatField())).order_by('-wallet_amount_float')
        return render(request,'admin/list_users.html',{'page':page,'request_data':request_data,'all_users':all_users,'all_user_roles':all_user_roles})
    else:
        return redirect('admin-login')




def getCountryStateCity(latitude,longitude,loc_type):
    # geolocator  = Nominatim(user_agent="geoapiExercises")
    
    # location    = geolocator.reverse(latitude+","+longitude)
    
    # address     = location.raw['address']
    # data        = ""

    # # traverse the data
    # if(loc_type == 'Country'):
    #     data = address.get('country', '')
    # elif(loc_type == 'State'):
    #     data = address.get('state', '')
    # elif(loc_type == 'City'):
    #     data    = address.get('city', '')
    #     if(not data):
    #         data= address.get('county', '')
    # elif(loc_type == 'Pin'):
    #     data    = address.get('postcode', '')

    # Make the curl request
    response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng="+latitude+","+longitude+"&key=AIzaSyA6sfxAGWorlekK-rkolU152WkN5mzn76A")

    # Parse the JSON response
    location_data = json.loads(response.text)
    # Extract the country, state, and city information
    for result in location_data['results']:
        for component in result['address_components']:
            if "country" in component['types']:
                country     = component['long_name']
            elif "administrative_area_level_1" in component['types']:
                state       = component['long_name']
            elif "administrative_area_level_3" in component['types']:
                city        = component['long_name']
            elif "postal_code" in component['types']:
                pin_code    = component['long_name']

    data        = ""

    # traverse the data
    if(loc_type == 'Country'):
        data = country
    elif(loc_type == 'State'):
        data = state
    elif(loc_type == 'City'):
        data    = city
    elif(loc_type == 'Pin'):
        data    = pin_code

    return data




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewUser(request):
    if request.session.has_key('adminId') or request.session.has_key('userId'):
        if request.method=="POST":
            name            = request.POST['name']
            phone           = request.POST['phone']
            email           = request.POST['email']
            latitude        = request.POST['latitude']
            longitude       = request.POST['longitude']
            location        = request.POST['location']
            user_role_id    = request.POST.get('user_role_id')
            user_role_id    = user_roles_data_tb.objects.get(id=user_role_id)
            password        = request.POST.get('password')
            image_file      = imgForm(request.POST,request.FILES)
            auto_password   = request.POST.get('auto_password')

            now             = datetime.now()
            profile_image   = None
            added_by        = None
            assigned_to     = None

            assigned_user_role_id   = request.POST.get('assigned_user_role_id')
            if assigned_user_role_id:
                assigned_to         = user_data_tb.objects.get(id=request.POST.get('assigned_to'))


            if request.session.has_key('userId'):
                added_by    = user_data_tb.objects.get(id=request.session['userId'])

            get_user        = user_data_tb.objects.all().filter(email=email)
            get_user_phone  = user_data_tb.objects.all().filter(phone=phone)
            if get_user:
                messages.error(request, 'Email already exist')
                return redirect('add-user')
            elif get_user_phone:
                messages.error(request, 'Phone number already exist')
                return redirect('add-user')
            else:
                if image_file.is_valid():
                    profile_image   = image_file.cleaned_data['image']


                # geolocator          = Nominatim(user_agent="geoapiExercises")
                # getlocation         = geolocator.reverse(latitude+","+longitude)
                # address             = getlocation.raw['address']
                # country             = address.get('country', '')
                # state               = address.get('state', '')
                # city                = address.get('city', '')
                # if(not city):
                #     city            = address.get('county', '')
                # pin_code            = address.get('postcode', '')


                # Make the curl request
                response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng="+latitude+","+longitude+"&key=AIzaSyA6sfxAGWorlekK-rkolU152WkN5mzn76A")

                # Parse the JSON response
                location_data = json.loads(response.text)
                # Extract the country, state, and city information
                for result in location_data['results']:
                    for component in result['address_components']:
                        if "country" in component['types']:
                            country     = component['long_name']
                        elif "administrative_area_level_1" in component['types']:
                            state       = component['long_name']
                        elif "administrative_area_level_3" in component['types']:
                            city        = component['long_name']
                        elif "postal_code" in component['types']:
                            pin_code    = component['long_name']


                if user_role_id:
                    # Auto generated password
                    if auto_password:
                        lettersLw       = string.ascii_lowercase
                        lettersUp       = string.ascii_uppercase
                        digits          = '1234567890'
                        password        = ''.join(random.choice(digits + lettersLw + lettersUp) for i in range(10))
                        sendEmail(email,'email/password.html',password)
                    else:
                        password        = password
                else:
                    password            = None


                insert_data = user_data_tb(name=name,phone=phone,email=email,profile_image=profile_image,latitude=latitude,longitude=longitude,location=location,country=country,state=state,city=city,pin_code=pin_code,active=True,user_role_id=user_role_id,password=password,added_by=added_by,assigned_to=assigned_to,created_at=now,updated_at=now)
                insert_data.save()

                latest_id       = user_data_tb.objects.latest('id')

                get_all_data    = user_data_tb.objects.count()

                if get_all_data != 1:
                    get_default_parent_id   = default_data_tb.objects.filter(title='user_default_parent_id').get()
                    default_parent_id       = get_default_parent_id.value

                    get_user_data           = user_data_tb.objects.filter(parent_id=default_parent_id).count()

                    if get_user_data < 2:
                        get_parent_id       = user_data_tb.objects.get(id=default_parent_id)
                        user_data_tb.objects.all().filter(id=latest_id.id).update(parent_id=get_parent_id,updated_at=now)
                        
                    else:
                        default_parent_id   = int(get_default_parent_id.value) + (1)
                        get_parent_id       = user_data_tb.objects.get(id=default_parent_id)
                        user_data_tb.objects.all().filter(id=latest_id.id).update(parent_id=get_parent_id,updated_at=now)
                else:
                    default_parent_id       = latest_id.id

                #update current default parent id
                default_data_tb.objects.all().filter(title='user_default_parent_id').update(value=default_parent_id,updated_at=now)

                messages.success(request, 'Successfully added.')

                return redirect('list-users')
        else:
            if request.session.has_key('userId'):
                if request.session['userRole'] == 'Admin Officer':
                    user_role_list  = user_roles_data_tb.objects.filter(role__gt='Admin Officer')
                elif request.session['userRole'] == 'Relationship Manager':
                    user_role_list  = user_roles_data_tb.objects.filter(role__gt='Relationship Manager')
                else:
                    user_role_list  = user_roles_data_tb.objects.all()
            else:
                user_role_list      = user_roles_data_tb.objects.all()
            return render(request,'admin/add_user.html',{'user_role_list' : user_role_list})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def getUsersListBasedUserRole(request):
    if request.session.has_key('adminId') or request.session.has_key('userId'):
        user_role_id    = request.GET['role_id']
        if request.session.has_key('adminId'): 
            users_list  = user_data_tb.objects.filter(user_role_id=user_role_id)
        elif request.session.has_key('userId'):
            users_list  = user_data_tb.objects.filter(user_role_id=user_role_id).exclude(id=request.session['userId'])

        get_data        = []
        for data in users_list:
            users_data_list              = {}
            users_data_list['id']        = data.id
            users_data_list['name']      = data.name
            get_data.append(users_data_list)

        return  JsonResponse({"models_to_return": list(get_data)})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateUser(request):
    if request.session.has_key('adminId') or request.session.has_key('userId'):
        if request.method=="POST":
            user_id         = request.GET['id']
            name            = request.POST.get('name')
            phone           = request.POST['phone']
            email           = request.POST['email']
            latitude        = request.POST['latitude']
            longitude       = request.POST['longitude']
            location        = request.POST['location']
            user_role_id    = request.POST.get('user_role_id')
            user_role_id    = user_roles_data_tb.objects.get(id=user_role_id)
            active          = True if request.POST.get('active') == 'true' else False
            image_file      = imgForm(request.POST,request.FILES)

            now             = datetime.now()
            adar_image      = None
            pan_image       = None

            assigned_to     = None

            assigned_user_role_id   = request.POST.get('assigned_user_role_id')
            if assigned_user_role_id:
                assigned_to         = user_data_tb.objects.get(id=request.POST.get('assigned_to'))


            get_user                = user_data_tb.objects.all().filter(email=email).exclude(id=user_id)
            get_user_phone          = user_data_tb.objects.all().filter(phone=phone).exclude(id=user_id)
            
            if get_user:
                messages.error(request, 'Email already exist')
                return redirect('/edit-user/?id='+ str(user_id))
            if get_user_phone:
                messages.error(request, 'Phone number already exist')
                return redirect('/edit-user/?id='+ str(user_id))
            else:
                if image_file.is_valid():
                    image                   = image_file.cleaned_data['image']
                    mymodel                 = user_data_tb.objects.get(id=user_id)
                    mymodel.profile_image   = image
                    mymodel.save()

                # geolocator                  = Nominatim(user_agent="geoapiExercises")
                # getlocation                 = geolocator.reverse(latitude+","+longitude)
                # address                     = getlocation.raw['address']
                # country                     = address.get('country', '')
                # state                       = address.get('state', '')
                # city                        = address.get('city', '')
                # if(not city):
                #     city                    = address.get('county', '')
                # pin_code                    = address.get('postcode', '')


                # Make the curl request
                response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng="+latitude+","+longitude+"&key=AIzaSyA6sfxAGWorlekK-rkolU152WkN5mzn76A")

                # Parse the JSON response
                location_data = json.loads(response.text)
                # Extract the country, state, and city information
                for result in location_data['results']:
                    for component in result['address_components']:
                        if "country" in component['types']:
                            country     = component['long_name']
                        elif "administrative_area_level_1" in component['types']:
                            state       = component['long_name']
                        elif "administrative_area_level_3" in component['types']:
                            city        = component['long_name']
                        elif "postal_code" in component['types']:
                            pin_code    = component['long_name']

                user_data_tb.objects.all().filter(id=user_id).update(name=name,phone=phone,email=email,active=active,latitude=latitude,longitude=longitude,location=location,country=country,state=state,city=city,pin_code=pin_code,user_role_id=user_role_id,assigned_to=assigned_to,updated_at=now)

                messages.success(request, 'Changes successfully updated.')
                return redirect('list-users')
        else:
            user_id         = request.GET['id']
            user_data       = user_data_tb.objects.all().filter(id=user_id)

            if request.session.has_key('userId'):
                if request.session['userRole'] == 'Admin Officer':
                    user_role_list  = user_roles_data_tb.objects.filter(role__gt='Admin Officer')
                elif request.session['userRole'] == 'Relationship Manager':
                    user_role_list  = user_roles_data_tb.objects.filter(role__gt='Relationship Manager')
                else:
                    user_role_list  = user_roles_data_tb.objects.all()
            else:
                user_role_list      = user_roles_data_tb.objects.all()

            list_assined_to_user_role           = []
            for user in user_data:
                get_assined_to                  = user.assigned_to
                if get_assined_to:
                    assined_to_user_role        = user.assigned_to.user_role_id 

                    # list users based on assigned user role
                    list_assined_to_user_role   = user_data_tb.objects.filter(user_role_id=assined_to_user_role.id)

            return render(request,'admin/edit_user.html',{'user_data' : user_data,'user_role_list' :user_role_list,'list_assined_to_user_role' : list_assined_to_user_role})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateUserPassword(request):
    if request.session.has_key('adminId') or request.session.has_key('userId'):
        user_id         = request.GET['id']
        password        = request.POST['new_password']
        now             = datetime.now()

        # password hashchecked
        hash_password   = make_password(password)
        user_data_tb.objects.all().filter(id=user_id).update(password=hash_password,updated_at=now)

        messages.success(request, 'Password update successfully')
        return redirect('/edit-user/?id='+ str(user_id))
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteUser(request):
    if request.session.has_key('adminId') or request.session.has_key('userId'):
        level_id    = request.GET['id']
        fromReg     = levels_tb.objects.all().filter(id=level_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-levels')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-levels')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def userResetUpdateEmailAndPin(request):
    if 'id' in request.GET:
        if request.method=="POST":
            user_id     = request.POST['id']
            user_pin    = request.POST['pin']
            now         = datetime.now()

            user_data_tb.objects.all().filter(id=user_id).update(user_pin=user_pin,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('thank-you')
        else:
            user_id     = request.GET['id']
            return render(request,'user/edit_user_pin.html',{'user_id' : user_id})
    else:
        raise Http404




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def thankYou(request):
    return render(request,'user/thank_you.html')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateRazorPayDetails(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            razor_id        = request.POST['id']
            razor_key       = request.POST['razor_key']
            razor_secret    = request.POST['razor_secret']
            now             = datetime.now()

            if razor_id:
                razor_pay_data_tb.objects.all().filter(id=razor_id).update(razor_key=razor_key,razor_secret=razor_secret,updated_at=now)
            else:
                insert_data = razor_pay_data_tb(razor_key=razor_key,razor_secret=razor_secret,created_at=now,updated_at=now)
                insert_data.save()

            messages.success(request, 'Changes successfully updated.')
            return redirect('update-razor-pay-details')
        else:
            get_data        = razor_pay_data_tb.objects.all()
            data            = {}
            if get_data:
                for x in get_data:
                    data    =   {
                                    'id'            : x.id,
                                    'razor_key'     : x.razor_key,
                                    'razor_secret'  : x.razor_secret,
                                } 
            
            return render(request,'admin/edit_razor_pay_details.html',{'data' : data})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateRazorPayxPayoutDetails(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            razor_id        = request.POST['id']
            razor_key       = request.POST['razor_key']
            razor_secret    = request.POST['razor_secret']
            account_number  = request.POST['account_number']
            now             = datetime.now()

            if razor_id:
                razor_payx_payout_data_tb.objects.all().filter(id=razor_id).update(razor_key=razor_key,razor_secret=razor_secret,account_number=account_number,updated_at=now)
            else:
                insert_data = razor_payx_payout_data_tb(razor_key=razor_key,razor_secret=razor_secret,account_number=account_number,created_at=now,updated_at=now)
                insert_data.save()

            messages.success(request, 'Changes successfully updated.')
            return redirect('update-razorpayx-payout-details')
        else:
            get_data        = razor_payx_payout_data_tb.objects.all()
            data            = {}
            if get_data:
                for x in get_data:
                    data    =   {
                                    'id'            : x.id,
                                    'razor_key'     : x.razor_key,
                                    'razor_secret'  : x.razor_secret,
                                    'account_number': x.account_number,
                                } 
            
            return render(request,'admin/payout_credentials.html',{'data' : data})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateDefaultSettings(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            get_id                  = request.POST['id']
            expiry_day              = request.POST['expiry_day']
            radius                  = request.POST['radius']
            first_month_commission  = request.POST['first_month_commission']
            field_visit_commission  = request.POST['field_visit_commission']
            now                     = datetime.now()

            if get_id:
                settings_tb.objects.all().filter(id=get_id).update(expiry_days=expiry_day,radius=radius,first_month_commission=first_month_commission,field_visit_commission=field_visit_commission,updated_at=now)
            else:
                insert_data = settings_tb(expiry_days=expiry_day,radius=radius,first_month_commission=first_month_commission,field_visit_commission=field_visit_commission,created_at=now,updated_at=now)
                insert_data.save()

            messages.success(request, 'Changes successfully updated.')
            return redirect('update-default-settings')
        else:
            get_data        = settings_tb.objects.all()
            data            = {}
            if get_data:
                for x in get_data:
                    data    =   {
                                    'id'                        : x.id,
                                    'expiry_day'                : x.expiry_days,
                                    'radius'                    : x.radius,
                                    'first_month_commission'    : x.first_month_commission,
                                    'field_visit_commission'    : x.field_visit_commission
                                } 
            
            return render(request,'admin/default_settings.html',{'data' : data})
    else:
        return redirect('admin-login')



#Bank transfer through admin panel
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def settleShopWalletAmount(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            shop_id         = request.POST['id']
            amount          = request.POST['amount']
            now             = datetime.now()

            get_shop        = shops_tb.objects.all().filter(id=shop_id).get()

            wallet_amount   = get_shop.wallet_amount

            if amount > wallet_amount:
                response    =   {
                                    "success"       : False,
                                    "message"       : "Can't transfer, amount is greater than wallet amount"
                                }

                messages.error(request, response['message'])
                return redirect('list-shops')

            get_bank_data       = bank_tb.objects.filter(shop_id=shop_id).latest('id')
            linked_account_id   = get_bank_data.razorpay_id

            get_razor_pay_data  = razor_payx_payout_data_tb.objects.latest('id')

            response            = bankTransfer(get_razor_pay_data.razor_key,get_razor_pay_data.razor_secret,get_razor_pay_data.account_number,linked_account_id,amount)
            
            if response['status_code'] == 200:
                wallet_amount   = float(wallet_amount) - float(amount)
                shops_tb.objects.all().filter(id=shop_id).update(wallet_amount=wallet_amount,updated_at=now)

                #----- Notification ---- #
                #-- To vendor ---
                device_token    = get_shop.vendor_id.device_token
                title           = 'Transferred successfully'
                body            = str(amount) +' successfully transferred to your '+get_bank_data.name+' account'
                sendNotificationToUser(device_token,title,body)

                insert_data     = vendor_notification_tb(vendor_id=get_shop.vendor_id,title=title,description=body,created_at=now,updated_at=now)
                insert_data.save()
                #----------------------

                messages.success(request, 'Settled successfully.')
            else:
                messages.error(request, response['message'])
            return redirect('list-shops')
        else:
            shop_id         = request.GET['id']
            shop_data       = shops_tb.objects.all().filter(id=shop_id).get()

            return render(request,'admin/shop_settlement.html',{'shop_data' : shop_data})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listUserCommissionData(request):
    if request.session.has_key('adminId'):
        get_user_list   = user_data_tb.objects.all().exclude(user_role_id__isnull=True)

        users_list      = []

        for user in get_user_list:
            total_amount            = user_transactions_tb.objects.all().filter(user_id=user.id).exclude(wallet_type='Shop Due Amount').aggregate(total_amount=Sum('amount'))['total_amount']
            settlement_amount       = user_transactions_tb.objects.all().filter(user_id=user.id,settled_commission=False).exclude(wallet_type='Shop Due Amount').aggregate(total_amount=Sum('amount'))['total_amount']
            earnings_amount         = float(0 if not total_amount else total_amount) - float(0 if not settlement_amount else settlement_amount)

            users_list.append({
                'id'                : user.id,
                'name'              : user.name,
                'phone'             : user.phone,
                'user_role'         : user.user_role_id.role,
                'email'             : user.email,
                'settlement_amount' : 0 if not settlement_amount else float(settlement_amount),
                'earnings_amount'   : earnings_amount
            })

       
        return render(request,'admin/list_earnings_settlements.html',{'users_list' : users_list})

    else:
        return redirect('admin-login')




#Bank transfer through admin panel
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def settleUserRoleCommissionAmount(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            user_id             = request.POST['id']
            amount              = request.POST['amount']
            now                 = datetime.now()
            user                = user_data_tb.objects.get(id=user_id)

            settlement_amount   = user_transactions_tb.objects.all().filter(user_id=user.id,settled_commission=False).exclude(wallet_type='Shop Due Amount').aggregate(total_amount=Sum('amount'))['total_amount']
            settlement_amount   = 0 if not settlement_amount else settlement_amount

            if amount > settlement_amount:
                response        =   {
                                        "success"       : False,
                                        "message"       : "Can't transfer, amount is greater than wallet amount"
                                    }

                messages.error(request, response['message'])
                return redirect('list-user-commission-data')

            get_bank_data       = user_bank_tb.objects.filter(user_id=user_id).latest('id')
            linked_account_id   = get_bank_data.razorpay_id

            get_razor_pay_data  = razor_payx_payout_data_tb.objects.latest('id')

            response            = bankTransfer(get_razor_pay_data.razor_key,get_razor_pay_data.razor_secret,get_razor_pay_data.account_number,linked_account_id,amount)
            
            if response['status_code'] == 200:
                transfer_id     =  response['transfer_id']
                user_transactions_tb.objects.all().filter(user_id=user.id).exclude(wallet_type='Shop Due Amount').update(settled_commission=True,updated_at=now)

                insert_data     = user_settlement_transactions_tb(user_id=user,amount=amount,bank_id=get_bank_data.id,razorpay_transaction_id=transfer_id,created_at=now,updated_at=now)
                insert_data.save()

                #----- Notification ---- #
                #-- To vendor ---
                device_token    = user.device_token
                title           = 'Transferred successfully'
                body            = str(amount) +' successfully transferred to your '+get_bank_data.name+' account'
                sendNotificationToUser(device_token,title,body)

                insert_data     = user_notification_tb(user_id=user,title=title,description=body,created_at=now,updated_at=now)
                insert_data.save()
                #----------------------

                messages.success(request, 'Settled successfully.')
            else:
                messages.error(request, response['message'])
            return redirect('list-user-commission-data')
        else:
            user_id             = request.GET['id']
            user_data           = user_data_tb.objects.all().filter(id=user_id).get()
            settlement_amount   = user_transactions_tb.objects.all().filter(user_id=user_data.id,settled_commission=False).exclude(wallet_type='Shop Due Amount').aggregate(total_amount=Sum('amount'))['total_amount']
            settlement_amount   = 0 if not settlement_amount else settlement_amount

            return render(request,'admin/user_settlement.html',{'user_data' : user_data,'settlement_amount':settlement_amount})
    else:
        return redirect('admin-login')




@method_decorator(csrf_exempt, name='dispatch')
def vendorDeleteShopOffers(request):
    data        = json.loads(request.body.decode("utf-8"))

    offer_id    = data.get('offer_id')

    fromReg     = offer_tb.objects.all().filter(id=offer_id)
    fromReg.delete()
    if fromReg.delete():
        response=   {
                        "success"   : True,
                        "message"   : "",
                    }
    else:
        response=   {
                        "success"   : False,
                        "message"   : "Something went to wrong",
                    }
    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def vendorShopVerifiedInvoiceList(request):
    data                = json.loads(request.body.decode("utf-8"))

    shop_id             = data.get('shop_id')
    get_shop_data       = shops_tb.objects.all().filter(id=shop_id).get()

    get_invoice_data    = invoice_data_tb.objects.all().filter(shop_id=shop_id,status='Verified').order_by('-id')

    #-- Pagination
    paginator           = Paginator(get_invoice_data, per_page=20)
    page_number         = data.get('page')
    page                = paginator.get_page(page_number)
    # Get the total number of pages
    total_pages         = paginator.num_pages
    #-- Pagination

    invoice_data        = []
    for invoice in page:
        amount_data     =   vendorAmountData(invoice.id)

        invoice_data.append({
                    'id'                : invoice.id,
                    'customer_id'       : None if not invoice.user_id else invoice.user_id.id,
                    'customer_name'     : None if not invoice.user_id else invoice.user_id.name,
                    'phone'             : None if not invoice.user_id else invoice.user_id.phone,
                    'user_id'           : invoice.vendor_id.id,
                    'vendor_phone'      : invoice.vendor_id.phone,
                    'shop_id'           : invoice.shop_id.id,
                    'shop_name'         : invoice.shop_id.name,
                    'invoice_image'     : '' if not invoice.invoice_image else invoice.invoice_image.url,
                    'invoice_number'    : invoice.invoice_number,
                    'invoice_date'      : invoice.invoice_date,
                    'pre_tax_amount'    : invoice.pre_tax_amount,
                    'invoice_amount'    : invoice.invoice_amount,
                    'remark'            : invoice.remark,
                    'status'            : invoice.status,
                    'myself'            : True if invoice.submitted_by == 'Vendor' else False,
                    'vendor_image'      : "" if not invoice.vendor_id.profile_image else invoice.vendor_id.profile_image.url,
                    "user_image"        : "" if not invoice.user_id.profile_image else invoice.user_id.profile_image.url,
                    "pay_half_amount"   : invoice.pay_half_amount,
                    "have_due_amount"   : invoice.have_due_amount,
                    'amount_data'       : amount_data
                }) 


    #--- amount data
    cal_total_amount        = 0
    total_amount            = 0
    due_amount              = 0
    half_amount             = 0
    shop_wallet_amount      = float(0 if not get_shop_data.wallet_amount else get_shop_data.wallet_amount)
    
    for invoice in get_invoice_data:
        amount_data   =   vendorAmountData(invoice.id)
    
        total_amount += amount_data['total_amount']

        if invoice['have_due_amount'] == False:
            due_amount   += amount_data['vendor_balance']
        if invoice['pay_half_amount'] == False:
            half_amount  += amount_data['commission_amount']

    # if total_amount > shop_wallet_amount:
    #     cal_total_amount    = total_amount - shop_wallet_amount

    
    vendor_name             = get_shop_data.vendor_id.name
    vendor_email            = get_shop_data.vendor_id.email

    get_razor_pay_data      = razor_pay_data_tb.objects.all().exists()

    if get_razor_pay_data == True:
        get_razor_pay_data  = razor_pay_data_tb.objects.latest('id')
    else:
        get_razor_pay_data  = {}


    shop_balance_amount     = shop_wallet_amount - float(0 if not get_shop_data.balance_amount else get_shop_data.balance_amount)
    
    # shop_balance_amount     = shop_wallet_amount

    total_amount_data       =   {
                                    "shop_id"           : shop_id,
                                    "total_amount"      : round(float(total_amount),2),
                                    "shop_wallet_amount": round(shop_wallet_amount,2),
                                    "name"              : vendor_name,
                                    "email"             : vendor_email,
                                    "razor_key"         : None if not get_razor_pay_data else get_razor_pay_data.razor_key,
                                    "razor_secret"      : None if not get_razor_pay_data else get_razor_pay_data.razor_secret,
                                    "have_bank"         : bank_tb.objects.filter(shop_id=get_shop_data.id).exists(),
                                    "due_amount"        : round(float(due_amount),2),
                                    "half_amount"       : round(float(half_amount),2),
                                    "shop_balance"      : round(float(shop_balance_amount),2),
                                } 

    #--- amount data


    response                =   {
                                    "invoice_data"      : invoice_data,
                                    "total_amount_data" : total_amount_data,
                                    "total_pages"       : total_pages
                                }

    return JsonResponse(response, status=201)


# ##--- Vendor shop credit(pay) wallet amount (all verified invoice amount add first in vendor wallet)
# @method_decorator(csrf_exempt, name='dispatch')
# def venderShopCreditWalletAmount(request):
#     data                    = json.loads(request.body.decode("utf-8"))

#     shop_id                 = data.get('shop_id')
#     total_amount            = data.get('total_amount')
#     amount                  = data.get('amount')
#     razorpay_transaction_id = data.get('razorpay_transaction_id')
#     razorpay_status         = data.get('razorpay_status')
#     payment_type            = "Online"
#     transaction_status      = "Completed"
#     entry_type              = "Credit"
#     wallet_type             = "Direct"
#     invoice_ids             = data.get('invoice_ids')
#     now                     = datetime.now()

#     get_shop_data           = shops_tb.objects.all().filter(id=shop_id).get()

#     vendor_id               = get_shop_data.vendor_id
#     bank_id                 = bank_tb.objects.filter(shop_id=shop_id).latest('id')

#     shop_amount             = float(0 if not get_shop_data.wallet_amount else get_shop_data.wallet_amount) + float(total_amount)

#     half_amount             = float(0 if not get_shop_data.half_amount else get_shop_data.half_amount) + float(amount)

#     #insert bank 
#     insert_data             = bank_transactions_tb(vendor_id=vendor_id,shop_id=get_shop_data,amount=amount,entry_type=entry_type,razorpay_transaction_id=razorpay_transaction_id,bank_id=bank_id,razorpay_status=razorpay_status,payment_type=payment_type,transaction_status=transaction_status,created_at=now,updated_at=now)
#     insert_data.save()

#     latest_id               = bank_transactions_tb.objects.latest('id')

#     #Insert shop wallet amount 
#     insert_data             = shop_wallet_transactions_tb(vendor_id=vendor_id,shop_id=get_shop_data,amount=amount,entry_type=entry_type,wallet_type=wallet_type,created_at=now,updated_at=now)
#     insert_data.save()


#     shops_tb.objects.all().filter(id=shop_id).update(wallet_amount=shop_amount,half_amount=half_amount,updated_at=now)


#     if invoice_ids:
#         for invoice in invoice_ids:
#             invoice_data_tb.objects.all().filter(id=invoice).update(pay_half_amount=True,have_due_amount=True,updated_at=now)
#     else:
#         get_invoice_data    = invoice_data_tb.objects.all().filter(shop_id=shop_id,status='Verified').update(pay_half_amount=True,have_due_amount=True,updated_at=now)


#     response                =   {
#                                     "success"   : True,
#                                     "message"   : ""
#                                 }

#     #--- capture razorpay
#     capture                 = razorpayCapture(razorpay_transaction_id,amount)
    
#     if capture != 'captured':
#         response            =   {
#                                     "success"       : False,
#                                     "message"       : "Something went to wrong"
#                                 }
#     #--- capture

#     return JsonResponse(response, status=201)


##--- Vendor shop credit(pay) wallet amount (all verified invoice amount add first in vendor wallet)
@method_decorator(csrf_exempt, name='dispatch')
def venderShopCreditWalletAmount(request):
    data                    = json.loads(request.body.decode("utf-8"))

    shop_id                 = data.get('shop_id')
    amount                  = data.get('amount')
    razorpay_transaction_id = data.get('razorpay_transaction_id')
    razorpay_status         = data.get('razorpay_status')
    payment_type            = "Online"
    transaction_status      = "Completed"
    entry_type              = "Credit"
    wallet_type             = "Direct"
    invoice_ids             = data.get('invoice_ids')
    now                     = datetime.now()

    get_shop_data           = shops_tb.objects.all().filter(id=shop_id).get()

    vendor_id               = get_shop_data.vendor_id
    bank_id                 = bank_tb.objects.filter(shop_id=shop_id).latest('id')

    shop_amount             = float(0 if not get_shop_data.wallet_amount else get_shop_data.wallet_amount) + float(amount)

    #insert bank 
    insert_data             = bank_transactions_tb(vendor_id=vendor_id,shop_id=get_shop_data,amount=amount,entry_type=entry_type,razorpay_transaction_id=razorpay_transaction_id,bank_id=bank_id,razorpay_status=razorpay_status,payment_type=payment_type,transaction_status=transaction_status,created_at=now,updated_at=now)
    insert_data.save()

    latest_id               = bank_transactions_tb.objects.latest('id')

    #Insert shop wallet amount 
    insert_data             = shop_wallet_transactions_tb(vendor_id=vendor_id,shop_id=get_shop_data,amount=amount,entry_type=entry_type,wallet_type=wallet_type,created_at=now,updated_at=now)
    insert_data.save()


    shops_tb.objects.all().filter(id=shop_id).update(wallet_amount=shop_amount,updated_at=now)


    if invoice_ids:
        for invoice in invoice_ids:
            invoice_data_tb.objects.all().filter(id=invoice).update(pay_half_amount=True,have_due_amount=True,updated_at=now)
    else:
        get_invoice_data    = invoice_data_tb.objects.all().filter(shop_id=shop_id,status='Verified').update(pay_half_amount=True,have_due_amount=True,updated_at=now)


    response                =   {
                                    "success"   : True,
                                    "message"   : ""
                                }

    #--- capture razorpay
    capture                 = razorpayCapture(razorpay_transaction_id,amount)
    
    if capture != 'captured':
        response            =   {
                                    "success"       : False,
                                    "message"       : "Something went to wrong"
                                }
    #--- capture

    return JsonResponse(response, status=201)




def razorpayCapture(payment_id,amount):
    get_razor_pay_data  = razor_pay_data_tb.objects.latest('id')
    
 
    razorpay_key_id     = get_razor_pay_data.razor_key
    razorpay_key_secret = get_razor_pay_data.razor_secret


    client              = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))

    get_payment_data    = client.payment.fetch(payment_id)

    # print('--------')
    # print(amount)
    # print(get_payment_data['amount'])

    amount              = amount * 100

    response            = client.payment.capture(payment_id, float(amount))

    return response['status']




# def gerateShopQRCOde(request):
#     # Create QR code instance
#     shop_id     = request.GET['id']
#     get_shop    = shops_tb.objects.all().filter(id=shop_id).get()
    
#     qr = qrcode.QRCode(
#         version=1,
#         box_size=7,
#         border=1
#     )

#     # Add data to the QR code
#     data = get_shop.upi_id
#     qr.add_data(data)
#     qr.make(fit=True)

#     # Create an image from the QR code
#     img = qr.make_image(fill_color='#6E57A5', back_color='white')

#     # Serve the image to the browser as a response
#     response = HttpResponse(content_type="image/png")
#     img.save(response, "PNG")
#     return response



# @cache_control(no_cache=True,must_revalidate=True,no_store=True)
# def shopQRView(request):
#     shop_id     = request.GET['id']
#     get_shop    = shops_tb.objects.all().filter(id=shop_id).get()
#     return render(request,'user/shop_qr.html',{'shop_id':shop_id,'shop_name':get_shop.name})





@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listUserAppBanner(request):
    if request.session.has_key('adminId'):
        list_all_banner = user_app_banner_tb.objects.all().order_by('order')
        all_banners     = []
        image           = None

        for banner in list_all_banner:
            if banner.shop_id:
                image   = None if not banner.shop_id.banner_image else banner.shop_id.banner_image.url
            elif banner.image:
                image   = banner.image.url

            all_banners.append({
                    'id'            : banner.id,
                    'banner'        : image,
                    'order'         : banner.order
            })

        return render(request,'admin/list_banner.html',{'all_banners' : all_banners})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addUserAppBanner(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            num         = int(request.POST['number_of_input']) + int(1)
            images      = request.FILES.getlist('image')
            now         = datetime.now()

            data_found  = False

            for x in range(int(num)):
                get_shop_id         = request.POST.get('shop_id['+str(x)+']')
                if get_shop_id:
                    shop_id         = shops_tb.objects.get(id=get_shop_id)
                    insert_data     = user_app_banner_tb(shop_id=shop_id,created_at=now,updated_at=now)
                    insert_data.save()

                    data_found      = True
            
            if images:
                for f in images:
                    myimage = user_app_banner_tb(title=f.name,created_at=now,updated_at=now)
                    myimage.image.save(f.name, f, save=True)

                    data_found      = True

            if data_found == False:
                messages.error(request, 'No image selected')
                return redirect('banner-add')

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-banner')
        else:
            shop_list       = shops_tb.objects.all().exclude(image='')
            
            return render(request,'admin/edit_banner.html',{'shop_list':shop_list})
    else:
        return redirect('admin-login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteUserAppBanner(request):
    if request.session.has_key('adminId'):
        banner_id   = request.GET['id']
        fromReg     = user_app_banner_tb.objects.all().filter(id=banner_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-banner')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-banner')
    else:
        return redirect('admin-login')




def updateUserAppBannerOrder(request):
    if request.session.has_key('adminId'):
        get_id  = request.GET['id']
        order   = request.GET['order']
        now     = datetime.now()

        user_app_banner_tb.objects.all().filter(id=get_id).update(order=order,updated_at=now)
        messages.success(request, 'Successfully Updated.')

        return  JsonResponse({'success': True})

    else:
        return redirect('admin-login')



@method_decorator(csrf_exempt, name='dispatch')
def checkVendorActive(request):
    data        = json.loads(request.body.decode("utf-8"))

    user_id     = data.get('user_id')

    user        = vendors_tb.objects.all().filter(id=user_id)
    
    if user.exists():
        for x in user:
            response    =   {
                                "is_active"     : True if x.status=="Active" else False,
                            }
    else:
        response        =   {
                                "success"    : False,
                                "message"   : "User not exist",
                            }

    return JsonResponse(response, status=201)
    



@method_decorator(csrf_exempt, name='dispatch')
def checkVendorAddInvoice(request):
    data        = json.loads(request.body.decode("utf-8"))

    user_id     = data.get('user_id')

    user        = vendors_tb.objects.all().filter(id=user_id)
    
    if user.exists():
        for x in user:
            response    =   {
                                "add_invoice"   : True if x.import_invoice==False else False,
                            }
    else:
        response        =   {
                                "success"       : False,
                                "message"       : "User not exist",
                            }

    return JsonResponse(response, status=201)


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def importShopInvoice(request):
    if request.session.has_key('adminId'):
        if  request.method=='POST':
            shop_id         = request.POST['shop_id']
            invoice_date    = request.POST['date']
            shop_data       = shops_tb.objects.get(id=shop_id)
            now             = datetime.now()

            get_invoice     = invoice_data_tb.objects.filter(shop_id=shop_id,invoice_date=invoice_date).exists()
    
            if get_invoice:
                messages.error(request, "Can't import, already uploaded")
                return redirect('list-shops')

            form            = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                file        = form.cleaned_data['file']
                df          = pd.read_excel(file)
                # convert the phone number column to a string
                df['Phone'] = df['Phone'].astype(str)

                for index, row in df.iterrows():
                    phone           = row['Phone']
                    discount        = row['Discount']
                    pre_tax_amount  = discount
                    invoice_amount  = discount
                    submitted_by    = 'Vendor'
                    status          = 'Verified'
                    created_at      = now
                    updated_at      = now
                    shop_id         = shop_data
                    vendor_id       = shop_data.vendor_id
                    is_import       = True

                    user_data       = user_data_tb.objects.filter(phone=phone).exists()

                    if not user_data:
                        user_data   = user_data_tb(phone=phone,active=True,created_at=now,updated_at=now)
                        user_data.save()

                        latest_id       = user_data_tb.objects.latest('id')

                        get_all_data    = user_data_tb.objects.count()

                        if get_all_data != 1:
                            get_default_parent_id   = default_data_tb.objects.filter(title='user_default_parent_id').get()
                            default_parent_id       = get_default_parent_id.value

                            get_user_data           = user_data_tb.objects.filter(parent_id=default_parent_id).count()

                            if get_user_data < 2:
                                get_parent_id       = user_data_tb.objects.get(id=default_parent_id)
                                user_data_tb.objects.all().filter(id=latest_id.id).update(parent_id=get_parent_id,updated_at=now)
                                
                            else:
                                default_parent_id   = int(get_default_parent_id.value) + (1)
                                get_parent_id       = user_data_tb.objects.get(id=default_parent_id)
                                user_data_tb.objects.all().filter(id=latest_id.id).update(parent_id=get_parent_id,updated_at=now)
                        else:
                            default_parent_id       = latest_id.id
                        #update current default parent id
                        default_data_tb.objects.all().filter(title='user_default_parent_id').update(value=default_parent_id,updated_at=now)
                    else:
                        user_data   = user_data_tb.objects.get(phone=phone)

                    user_id         = user_data

                    invoice_data    = invoice_data_tb(
                                        user_id         = user_id,
                                        shop_id         = shop_id,
                                        vendor_id       = vendor_id,
                                        invoice_date    = invoice_date,
                                        pre_tax_amount  = pre_tax_amount,
                                        invoice_amount  = invoice_amount,
                                        submitted_by    = submitted_by,
                                        status          = status,
                                        is_import       = is_import,
                                        created_at      = created_at,
                                        updated_at      = updated_at,
                                    )
                    invoice_data.save()

                    # Retrieve the ID of the newly created invoice record
                    invoice_id      = invoice_data.id
                    invoice_data    = invoice_data_tb.objects.get(id=invoice_id)
                    # invoice_data.invoice_number = 'Wonder' + shop_data.name + str(invoice_id)
                    invoice_data.invoice_number = str(invoice_id)
                    invoice_data.save()

            messages.success(request, 'Success.')
            return redirect('list-shops')
        else:   
            shop_id     = request.GET['id']
            shop_data   = shops_tb.objects.get(id=shop_id)

            return render(request,'admin/import_invoice.html',{'shop_id':shop_id,'shop_data':shop_data})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listUserRoles(request):
    if request.session.has_key('adminId'):
        user_roles_list = user_roles_data_tb.objects.all().order_by('-id')
        return render(request,'admin/list_user_roles.html',{'user_roles_list' : user_roles_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def addNewUserRole(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            role            = request.POST['role']
            description     = request.POST['description']
            commission      = request.POST['commission']
            now             = datetime.now()

            insert_data     = user_roles_data_tb(role=role,description=description,commission=commission,created_at=now,updated_at=now)
            insert_data.save()
            messages.success(request, 'Successfully added.')
            return redirect('list-user-roles')
        else:
            return render(request,'admin/add_user_role.html')
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateUserRole(request):
    if request.session.has_key('adminId'):
        if request.method=="POST":
            role_id         = request.GET['id']
            role            = request.POST['role']
            description     = request.POST['description']
            commission      = request.POST['commission']
            now             = datetime.now()

            user_roles_data_tb.objects.all().filter(id=role_id).update(role=role,description=description,commission=commission,updated_at=now)

            messages.success(request, 'Changes successfully updated.')
            return redirect('list-user-roles')
        else:
            role_id         = request.GET['id']
            role_data       = user_roles_data_tb.objects.all().filter(id=role_id)
            
            return render(request,'admin/edit_user_role.html',{'role_data' : role_data})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def deleteUserRole(request):
    if request.session.has_key('adminId'):
        role_id     = request.GET['id']
        fromReg     = user_roles_data_tb.objects.all().filter(id=role_id)
        fromReg.delete()
        if fromReg.delete():
            messages.success(request, 'Successfully Deleted.')
            return redirect('list-user-roles')
        else:
            messages.error(request, 'Something went to wrong')
            return redirect('list-user-roles')
    else:
        return redirect('admin-login')





@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listSupportRequest(request):
    if request.session.has_key('adminId')  or request.session.has_key('userId'):
        if request.session.has_key('adminId'):
            data_list   = vendor_support_request_tb.objects.all().order_by('-id')
        elif request.session.has_key('userId'):
            data_list   = vendor_support_request_tb.objects.filter(assigned_to=request.session['userId']).order_by('-id')
        return render(request,'admin/list_support_request.html',{'data_list' : data_list})
    else:
        return redirect('admin-login')



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def updateSupportRequest(request):
    if request.session.has_key('adminId') or request.session.has_key('userId'):
        if request.method=="POST":
            support_id              = request.GET['id']
            status                  = request.POST['status']
            assigned_user_role_id   = request.POST.get('assigned_user_role_id')
            assigned_to             = request.POST.get('assigned_to')
            status                  = request.POST['status']
            now                     = datetime.now()

            if request.session.has_key('adminId'):
                if assigned_user_role_id:
                    assigned_to     = user_data_tb.objects.get(id=assigned_to)

                vendor_support_request_tb.objects.all().filter(id=support_id).update(status=status,assigned_to=assigned_to,updated_at=now)
            elif request.session.has_key('userId'):
                vendor_support_request_tb.objects.all().filter(id=support_id).update(status=status,updated_at=now)

            messages.success(request, 'Successfully updated.')
            return redirect('list-support-request')
        else:
            support_id                      = request.GET['id']
            support_data                    = vendor_support_request_tb.objects.get(id=support_id)
            
            if request.session.has_key('userId'):
                if request.session['userRole'] == 'Admin Officer':
                    user_role_list          = user_roles_data_tb.objects.filter(role__gt='Admin Officer')
                elif request.session['userRole'] == 'Relationship Manager':
                    user_role_list          = user_roles_data_tb.objects.filter(role__gt='Relationship Manager')
                else:
                    user_role_list          = user_roles_data_tb.objects.all()
            else:
                user_role_list              = user_roles_data_tb.objects.all()

            list_assined_to_user_role       = []
            get_assined_to                  = support_data.assigned_to
            if get_assined_to:
                assined_to_user_role        = support_data.assigned_to.user_role_id 

                # list users based on assigned user role
                list_assined_to_user_role   = user_data_tb.objects.filter(user_role_id=assined_to_user_role.id)
                    
            return render(request,'admin/edit_support_data.html',{'support_data' : support_data,'user_role_list' : user_role_list, 'list_assined_to_user_role' : list_assined_to_user_role})
    else:
        return redirect('admin-login')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def listUserTransactions(request):
    if request.session.has_key('adminId'):
        transactions_list           = user_transactions_tb.objects.all().order_by('-id')

        #-- Pagination
        paginator                   = Paginator(transactions_list, per_page=20)
        if request.method == 'POST':
            page_number = request.POST.get('page')
        else:
            page_number = request.GET.get('page')
        page                        = paginator.get_page(page_number)
        #-- Pagination

        return render(request,'admin/list_user_transactions.html',{'page' : page})
    else:
        return redirect('admin-login')



###########################----- MOBILE APP API's --------##################################################################
###########################------ MOBILE Sellers --------##################################################################


@method_decorator(csrf_exempt, name='dispatch')
def vendorLogin(request):
    data        = json.loads(request.body.decode("utf-8"))

    email       = data.get('email')
    password    = data.get('password')


    vendor      = vendors_tb.objects.all().filter(email=email)

    if vendor:
        for x in vendor:
            if(check_password(password,x.password) == True):
                user_id     = x.id

                get_shop    = shops_tb.objects.all().filter(vendor_id=user_id).count()
                

                response    =   {
                                    "user_id"       : user_id,
                                    "success"       : True,
                                    "is_approved"   : True if x.status=="Active" else False,
                                    "have_shop"     : True if get_shop != 0 else False,
                                    "message"       : ""
                                }
            else:
                response    =   {
                                    "user_id"   : '',
                                    "success"   : False,
                                    "message"   : "Invalid username or password"
                                }
    else:
        response            =   {
                                    "user_id"   : '',
                                    "success"   : False,
                                    "message"   : "Invalid username or password"
                                }

    return JsonResponse(response, status=201)



def shopListAllBusinessRep(request):
    business_rep_role   = user_roles_data_tb.objects.get(role='Business Representative')
    all_business_rep    = user_data_tb.objects.filter(user_role_id=business_rep_role.id)
    list_business_rep   = []

    for shop in all_business_rep:
        list_business_rep.append({
                'id'            : shop.id,
                'shop_name'     : shop.name,
                'phone'         : shop.phone,
            })


    response            =   {
                                "list_business_rep" : list_business_rep,
                            } 
    
    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def vendorRegister(request):
    data            = json.loads(request.body.decode("utf-8"))

    name            = data.get('name')
    phone           = data.get('phone')
    email           = data.get('email')
    adar_number     = data.get('adar_number')
    pan_number      = data.get('pan_number')
    auto_password   = data.get('auto_password')
    password        = data.get('password')
    business_rep_id = data.get('business_rep_id')

    get_adar_image  = data.get('adar_image')
    get_pan_image   = data.get('pan_image')

    now             = datetime.now()
    date_time       = now.strftime("%Y%b%d%H%M%S")

    get_vendor      = vendors_tb.objects.all().filter(email=email)

    if get_vendor:
        response    =   {
                            "user_id"   : '',
                            "success"   : False,
                            "message"   : "Email already exist"
                        }
    else:
        # Auto generated password
        if auto_password == True:
            lettersLw           = string.ascii_lowercase
            lettersUp           = string.ascii_uppercase
            digits              = '1234567890'
            password            = ''.join(random.choice(digits + lettersLw + lettersUp) for i in range(10))
            sendEmail(email,'email/password.html',password)
        else:
            password            = password

        # password hashchecked
        hash_password           = make_password(password)

        adar_image              = uploadImage(get_adar_image,'adar-'+name+'-'+date_time)
        pan_image               = uploadImage(get_pan_image,'pan-'+name+'-'+date_time)

        insert_data             = vendors_tb(name=name,phone=phone,email=email,password=hash_password,adar_number=adar_number,pan_number=pan_number,adar_image=adar_image,pan_image=pan_image,status="Active",business_rep_id=business_rep_id,created_at=now,updated_at=now)
        insert_data.save()

        latest_id               = vendors_tb.objects.latest('id')
        get_shop                = shops_tb.objects.all().filter(vendor_id=latest_id.id).count()

        response                =   {
                                        "user_id"       : latest_id.id,
                                        "success"       : True,
                                        "is_approved"   : True if latest_id.status=="Active" else False,
                                        "have_shop"     : True if get_shop != 0 else False,
                                        "message"       : ""
                                    }

    return JsonResponse(response, status=201)



def uploadImage(image_string,image_name):
    image_data  = base64.b64decode(image_string)

    # open as an image
    image       = Image.open(io.BytesIO(image_data))

    # save the image to disk
    image.save('media/image/'+image_name+'.jpg', 'JPEG')

    image_path  = 'image/'+image_name+'.jpg'

    return image_path



@method_decorator(csrf_exempt, name='dispatch')
def vendorAddShop(request):
    data                = json.loads(request.body.decode("utf-8"))

    name                = data.get('name')
    get_vendor_id       = data.get('user_id')
    vendor_id           = vendors_tb.objects.get(id=get_vendor_id)
    get_category_id     = data.get('category_id')
    category_id         = category_tb.objects.get(id=get_category_id)
    gst_number          = data.get('gst_number')
    address             = data.get('address')
    latitude            = data.get('latitude')
    longitude           = data.get('longitude')
    location            = data.get('location')
    radius              = "30"
    commission          = data.get('commission')
    is_featured         = data.get('is_featured')
    gst_pct             = data.get('gst_pct')

    get_image           = data.get('image')
    get_gst_image       = data.get('gst_image')
    get_license_image   = data.get('license_image')
    get_banner_image    = data.get('banner_image')
    license_number      = data.get('license_number')

    opening_time        = data.get('opening_time')
    closing_time        = data.get('closing_time')

    website_url         = data.get('website_url')
    phone1              = data.get('phone1')
    phone2              = data.get('phone2')

    opening_time        = None if not opening_time else datetime.strptime(opening_time, '%I:%M %p')
    opening_time        = None if not opening_time else opening_time.strftime('%H:%M')
    closing_time        = None if not closing_time else datetime.strptime(closing_time, '%I:%M %p')
    closing_time        = None if not closing_time else closing_time.strftime('%H:%M')

    
    now                 = datetime.now()
    date_time           = now.strftime("%Y%b%d%H%M%S")

    if settings_tb.objects.all().exists() == True:
        get_radius      = settings_tb.objects.all().latest('id')
        radius          = get_radius.radius

    image               = None if not get_image else uploadImage(get_image,'shop-'+name+'-'+date_time)

    gst_image           = None if not get_gst_image else uploadImage(get_gst_image,'gst_image-'+name+'-'+date_time)
    license_image       = None if not get_license_image else uploadImage(get_license_image,'license_image-'+name+'-'+date_time)
    banner_image        = None if not get_banner_image else uploadImage(get_banner_image,'banner_image-'+name+'-'+date_time)


    # geolocator          = Nominatim(user_agent="geoapiExercises")
    # getlocation         = geolocator.reverse(latitude+","+longitude)
    # getaddress          = getlocation.raw['address']
    # country             = getaddress.get('country', '')
    # state               = getaddress.get('state', '')
    # city                = getaddress.get('city', '')
    # if(not city):
    #     city            = getaddress.get('county', '')
    # pin_code            = getaddress.get('postcode', '')

    # Make the curl request
    response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng="+latitude+","+longitude+"&key=AIzaSyA6sfxAGWorlekK-rkolU152WkN5mzn76A")

    # Parse the JSON response
    location_data = json.loads(response.text)
    # Extract the country, state, and city information
    for result in location_data['results']:
        for component in result['address_components']:
            if "country" in component['types']:
                country     = component['long_name']
            elif "administrative_area_level_1" in component['types']:
                state       = component['long_name']
            elif "administrative_area_level_3" in component['types']:
                city        = component['long_name']
            elif "postal_code" in component['types']:
                pin_code    = component['long_name']


    ###------get upi
    my_string           = name.replace(" ", "")
    upi_id              = my_string+'@wonderpoints'
    get_shopupi         = shops_tb.objects.all().filter(upi_id=upi_id)
    ###------get upi

    insert_data         = shops_tb(name=name,vendor_id=vendor_id,category_id=category_id,gst_number=gst_number,license_number=license_number,address=address,latitude=latitude,longitude=longitude,location=location,radius=radius,image=image,gst_image=gst_image,license_image=license_image,opening_time=opening_time,closing_time=closing_time,is_featured=is_featured,commission=commission,gst_pct=gst_pct,country=country,state=state,city=city,pin_code=pin_code,website_url=website_url,phone1=phone1,phone2=phone2,created_at=now,updated_at=now)
    insert_data.save()

    latest_id           = shops_tb.objects.latest('id')
    ###------set upi id
    if get_shopupi:
        upi_id          = my_string+latest_id.id+'@wonderpoints'
    shops_tb.objects.all().filter(id=latest_id.id).update(upi_id=upi_id,updated_at=now)
    ###------set upi

    insert_data         = shop_images_tb(image=image,shop_id=latest_id,is_shop_featured=True,created_at=now,updated_at=now)
    insert_data.save()

    response            =   {
                                "shop_id"   : latest_id.id,
                                "success"   : True,
                                "message"   : ""
                            }

    return JsonResponse(response, status=201)



def getCategories(request):
    categroy_list   = category_tb.objects.all()

    items_data      = []
    
    for item in categroy_list:
        items_data.append({
                'id'            : item.id,
                'name'          : item.name,
                'description'   : item.description,
                'image'         : "" if not item.image else item.image.url,
            })

    response        =   {
                            "categories"   : items_data,
                        }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def vendorAddBank(request):
    data                = json.loads(request.body.decode("utf-8"))

    name                = data.get('name')
    get_vendor_id       = data.get('user_id')
    vendor_id           = vendors_tb.objects.get(id=get_vendor_id)
    get_shop_id         = data.get('shop_id')
    shop_id             = shops_tb.objects.get(id=get_shop_id)
    account_number      = data.get('account_number')
    account_type        = data.get('account_type')
    ifsc_code           = data.get('ifsc_code')
    now                 = datetime.now()

    get_data            = bank_tb.objects.filter(shop_id=shop_id).exists()

    if get_data == True:
        response        =   {
                                "success"   : False,
                                "message"   : "This shop already have bank account"
                            }

        return JsonResponse(response, status=201)

    cheque_copy         = data.get('cheque_copy')

    now                 = datetime.now()
    date_time           = now.strftime("%Y%b%d%H%M%S")

    image               = uploadImage(cheque_copy,'cheque-'+name+'-'+date_time)

    insert_data         = bank_tb(name=name,vendor_id=vendor_id,shop_id=shop_id,account_number=account_number,account_type=account_type,ifsc_code=ifsc_code,cheque_copy=image,created_at=now,updated_at=now)
    insert_data.save()


    latest_id           = bank_tb.objects.latest('id')

    response            =   {
                                "bank_id"   : latest_id.id,
                                "success"   : True,
                                "message"   : ""
                            }

    return JsonResponse(response, status=201)


@method_decorator(csrf_exempt, name='dispatch')
def vendorProfile(request):
    data            = json.loads(request.body.decode("utf-8"))

    vendor_id       = data.get('user_id')
    get_vendor_data = vendors_tb.objects.all().filter(id=vendor_id).get()

    vendor_data     =   {
                            'user_id'   : get_vendor_data.id,
                            'name'      : get_vendor_data.name,
                            'email'     : get_vendor_data.email,
                            'phone'     : get_vendor_data.phone,
                            'image'     : '' if not get_vendor_data.profile_image else get_vendor_data.profile_image.url
                        }  


    response        =   {
                            "user_data" : vendor_data
                        }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def vendorEditProfile(request):
    data            = json.loads(request.body.decode("utf-8"))

    vendor_id       = data.get('user_id')
    name            = data.get('name')
    # phone           = data.get('phone')
    # email           = data.get('email')
    get_image       = data.get('image')

    now             = datetime.now()
    date_time       = now.strftime("%Y%b%d%H%M%S")

    # get_vendor      = vendors_tb.objects.all().filter(email=email).exclude(id=vendor_id)

    # get_vendor_phn  = vendors_tb.objects.all().filter(phone=phone).exclude(id=vendor_id)

    # if get_vendor:
    #     response    =   {
    #                         "success"   : False,
    #                         "message"   : "Email already exist"
    #                     }

    #     return JsonResponse(response, status=201)

    # if get_vendor_phn:
    #     response    =   {
    #                         "success"   : False,
    #                         "message"   : "Phone number already exist"
    #                     }

    #     return JsonResponse(response, status=201)

    vendors_tb.objects.all().filter(id=vendor_id).update(name=name,updated_at=now)

    if get_image != None:
        image   = uploadImage(get_image,'profile-'+name+'-'+date_time)

        vendors_tb.objects.all().filter(id=vendor_id).update(profile_image=image,updated_at=now)

    response    =   {
                        "success"   : True,
                        "message"   : ""
                    }

    return JsonResponse(response, status=201)


@method_decorator(csrf_exempt, name='dispatch')
def vendorShopLicenseDetails(request):
    data            = json.loads(request.body.decode("utf-8"))

    vendor_id       = data.get('user_id')

    get_shop_data   = shops_tb.objects.all().filter(vendor_id=vendor_id).get()


    shop_data       =   {
                            'shop_id'           : get_shop_data.id,
                            'license_number'    : get_shop_data.license_number,
                            'license_image'     : get_shop_data.license_image.url
                        }  

    response        =   {
                            "license_data"   : shop_data
                        }

    return JsonResponse(response, status=201)


@method_decorator(csrf_exempt, name='dispatch')
def vendorShopGSTDetails(request):
    data            = json.loads(request.body.decode("utf-8"))

    vendor_id       = data.get('user_id')

    get_shop_data   = shops_tb.objects.all().filter(vendor_id=vendor_id).get()


    shop_data       =   {
                            'shop_id'       : get_shop_data.id,
                            'gst_number'    : get_shop_data.gst_number,
                            'gst_image'     : get_shop_data.gst_image.url
                        }  

    response        =   {
                            "gst_data"  : shop_data
                        }

    return JsonResponse(response, status=201)


@method_decorator(csrf_exempt, name='dispatch')
def vendorShopBankDetails(request):
    data            = json.loads(request.body.decode("utf-8"))

    bank_id         = data.get('bank_id')

    get_bank_data   = bank_tb.objects.all().filter(id=bank_id).latest('id')

    bank_data       =   {
                            'bank_id'           : get_bank_data.id,
                            'name'              : get_bank_data.name,
                            'account_number'    : get_bank_data.account_number,
                            'account_type'      : get_bank_data.account_type,
                            'ifsc_code'         : get_bank_data.ifsc_code,
                            'cheque_copy'       : '' if not get_bank_data.cheque_copy else get_bank_data.cheque_copy.url,
                            'shop_id'           : '' if not get_bank_data.shop_id else get_bank_data.shop_id.id,
                            'shop_name'         : '' if not get_bank_data.shop_id else get_bank_data.shop_id.name,
                            'vendor_id'         : get_bank_data.vendor_id.id,
                            'vendor_name'       : get_bank_data.vendor_id.name,
                        }  

    response        =   {
                            "bank_data" : bank_data
                        }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def vendorEditBankDetails(request):
    data                = json.loads(request.body.decode("utf-8"))

    bank_id             = data.get('bank_id')
    name                = data.get('name')
    get_vendor_id       = data.get('user_id')
    vendor_id           = vendors_tb.objects.get(id=get_vendor_id)
    get_shop_id         = data.get('shop_id')
    shop_id             = shops_tb.objects.get(id=get_shop_id)
    account_number      = data.get('account_number')
    account_type        = data.get('account_type')
    ifsc_code           = data.get('ifsc_code')

    get_data            = bank_tb.objects.all().filter(shop_id=shop_id).exclude(id=bank_id)
            
    if get_data:
        response        =   {
                                "success"   : False,
                                "message"   : "This shop already have bank account"
                            }

        return JsonResponse(response, status=201)


    cheque_copy         = data.get('cheque_copy')

    now                 = datetime.now()
    date_time           = now.strftime("%Y%b%d%H%M%S")

    bank_tb.objects.all().filter(id=bank_id).update(name=name,vendor_id=vendor_id,shop_id=shop_id,account_number=account_number,account_type=account_type,ifsc_code=ifsc_code,updated_at=now)

    if cheque_copy != None:
        image           = uploadImage(cheque_copy,'cheque-'+name+'-'+date_time)
        bank_tb.objects.all().filter(id=bank_id).update(cheque_copy=image,updated_at=now)

    response            =   {
                                "success"   : True,
                                "message"   : ""
                            }

    return JsonResponse(response, status=201)


def getTermsAndConditions(request):
    data            = []

    get_data        = terms_and_conditions_tb.objects.all()

    if get_data:
        for x in get_data:
            data    =   {
                            'title'         : x.title,
                            'description'   : x.description,
                        } 
                         
    response        =   {
                            "terms" : data
                        }

    return JsonResponse(response, status=201)




def getPrivacyPolicy(request):
    data            = []

    get_data        = privacy_policy_tb.objects.all()

    if get_data:
        for x in get_data:
            data    =   {
                            'title'         : x.title,
                            'description'   : x.description,
                        }  
        response    =   {
                            "policy"    : data
                        }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def vendorNotificatons(request):
    data                    = json.loads(request.body.decode("utf-8"))

    vendor_id               = data.get('user_id')

    get_notification_data   = vendor_notification_tb.objects.all().filter(vendor_id=vendor_id).order_by('-id')
    notification_data       = []

    for notification in get_notification_data:
        notification_data.append({
                    'id'            : notification.id,
                    'user_id'       : notification.vendor_id.id,
                    'title'         : notification.title,
                    'description'   : notification.description,
                })

    response                =   {
                                    "notification_data"  : notification_data
                                }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def vendorInvoiceList(request):
    data                = json.loads(request.body.decode("utf-8"))

    vendor_id           = data.get('user_id')

    get_invoice_data    = invoice_data_tb.objects.all().filter(vendor_id=vendor_id).order_by('-id')

    invoice_data        = []
    for invoice in get_invoice_data:
        amount_data     =   vendorAmountData(invoice.id)

        invoice_data.append({
                    'id'            : invoice.id,
                    'customer_id'   : None if not invoice.user_id else invoice.user_id.id,
                    'customer_name' : None if not invoice.user_id else invoice.user_id.name,
                    'phone'         : None if not invoice.user_id else invoice.user_id.phone,
                    'user_id'       : invoice.vendor_id.id,
                    'vendor_phone'  : invoice.vendor_id.phone,
                    'shop_id'       : invoice.shop_id.id,
                    'shop_name'     : invoice.shop_id.name,
                    'invoice_image' : '' if not invoice.invoice_image else invoice.invoice_image.url,
                    'invoice_number': invoice.invoice_number,
                    'invoice_date'  : invoice.invoice_date,
                    'pre_tax_amount': invoice.pre_tax_amount,
                    'invoice_amount': invoice.invoice_amount,
                    'remark'        : invoice.remark,
                    'status'        : invoice.status,
                    'myself'        : True if invoice.submitted_by == 'Vendor' else False,
                    'vendor_image'  : "" if not invoice.vendor_id.profile_image else invoice.vendor_id.profile_image.url,
                    "user_image"    : "" if not invoice.user_id.profile_image else invoice.user_id.profile_image.url,
                    'amount_data'   : amount_data
                }) 

    response        =   {
                            "invoice_data" : invoice_data
                        }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def searchVenderShopInvoice(request):
    data                = json.loads(request.body.decode("utf-8"))

    search_key          = data.get('search_key')
    shop_id             = data.get('shop_id')
    date                = None
    user_phone          = None

    if is_valid_date(search_key):
        date            = search_key
    else:
        user_phone      = search_key


    if user_phone:
        user_ids        = user_data_tb.objects.all().filter(phone__icontains=user_phone).values('id')
        id_list         = [obj['id'] for obj in user_ids]
        get_invoice     = invoice_data_tb.objects.all().filter(user_id__in=id_list,shop_id=shop_id).order_by('-id')
    elif date:
        date_obj        = datetime.strptime(date, '%Y-%m-%d')
        date            = date_obj.date()
        get_invoice     = invoice_data_tb.objects.filter(invoice_date__date=date,shop_id=shop_id).order_by('-id')

    #-- Pagination
    paginator           = Paginator(get_invoice, per_page=20)
    page_number         = data.get('page')
    page                = paginator.get_page(page_number)
    total_pages         = paginator.num_pages
    #-- Pagination


    invoice_data        = []
    for invoice in page:
        amount_data     =   vendorAmountData(invoice.id)

        invoice_data.append({
                    'id'            : invoice.id,
                    'customer_id'   : None if not invoice.user_id else invoice.user_id.id,
                    'customer_name' : None if not invoice.user_id else invoice.user_id.name,
                    'phone'         : None if not invoice.user_id else invoice.user_id.phone,
                    'user_id'       : invoice.vendor_id.id,
                    'shop_id'       : invoice.shop_id.id,
                    'shop_name'     : invoice.shop_id.name,
                    'invoice_image' : '' if not invoice.invoice_image else invoice.invoice_image.url,
                    'invoice_number': invoice.invoice_number,
                    'invoice_date'  : invoice.invoice_date,
                    'pre_tax_amount': invoice.pre_tax_amount,
                    'invoice_amount': invoice.invoice_amount,
                    'remark'        : invoice.remark,
                    'status'        : invoice.status,
                    'myself'        : True if invoice.submitted_by == 'Vendor' else False,
                    'vendor_image'  : "" if not invoice.vendor_id.profile_image else invoice.vendor_id.profile_image.url,
                    "user_image"    : "" if not invoice.user_id.profile_image else invoice.user_id.profile_image.url,
                    'amount_data'   : amount_data
                }) 

    response        =   {
                            "invoice_data"  : invoice_data,
                            "page"          : page_number,
                            "total_pages"   : total_pages
                        }

    return JsonResponse(response, status=201)



def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False



def vendorAmountData(invoice_id):
    get_invoice_data    = invoice_data_tb.objects.all().filter(id=invoice_id).get()

    shop_commission     = get_invoice_data.shop_id.commission
    shop_half_commission= 50
    shop_wallet_amount  = 0 if not get_invoice_data.shop_id.wallet_amount else get_invoice_data.shop_id.wallet_amount
    invoice_amount      = 0 if get_invoice_data.pre_tax_amount == 'nan' else get_invoice_data.pre_tax_amount

    if get_invoice_data.is_import:
        commission_amount   = float(invoice_amount)
    else:
        commission_amount   = is_what_percent_of(float(shop_commission), float(invoice_amount))

    # commission_amount   = float(invoice_amount)
    vendor_commission   = is_what_percent_of(float(shop_half_commission), float(commission_amount))
    vendor_balance      = is_what_percent_of(float(shop_half_commission), float(commission_amount))


    amount              = 0

    shop_wallet_amount  = float(shop_wallet_amount)

    if(float(vendor_commission) > float(shop_wallet_amount)):
        amount          = float(vendor_commission) - float(shop_wallet_amount)

    vendor_name         = get_invoice_data.vendor_id.name
    vendor_email        = get_invoice_data.vendor_id.email

    get_razor_pay_data  = razor_pay_data_tb.objects.all().exists()

    if get_razor_pay_data == True:
        get_razor_pay_data  = razor_pay_data_tb.objects.latest('id')
    else:
        get_razor_pay_data  = {}

    amount_data         =   {
                                "current_amount"    : round(shop_wallet_amount,2),
                                "total_amount"      : round(commission_amount,2), 
                                "commission_amount" : round(vendor_commission,2), #half
                                "additional_amount" : round(amount),
                                "name"              : vendor_name,
                                "email"             : vendor_email,
                                "razor_key"         : None if not get_razor_pay_data else get_razor_pay_data.razor_key,
                                "razor_secret"      : None if not get_razor_pay_data else get_razor_pay_data.razor_secret,
                                "have_bank"         : bank_tb.objects.filter(shop_id=get_invoice_data.shop_id.id).exists(),
                                "vendor_balance"    : round(vendor_balance,2)
                            } 

    return amount_data



# def vendorAmountData(invoice_id):
#     get_invoice_data    = invoice_data_tb.objects.all().filter(id=invoice_id).get()

#     shop_commission     = get_invoice_data.shop_id.commission
#     shop_wallet_amount  = 0 if not get_invoice_data.shop_id.wallet_amount else get_invoice_data.shop_id.wallet_amount
#     invoice_amount      = 0 if get_invoice_data.pre_tax_amount == 'nan' else get_invoice_data.pre_tax_amount

#     if get_invoice_data.is_import:
#         commission_amount   = float(invoice_amount)
#     else:
#         commission_amount   = is_what_percent_of(float(shop_commission), float(invoice_amount))
#     amount              = 0

#     shop_wallet_amount  = float(shop_wallet_amount)

#     if(float(commission_amount) > float(shop_wallet_amount)):
#         amount          = float(commission_amount) - float(shop_wallet_amount)

#     vendor_name         = get_invoice_data.vendor_id.name
#     vendor_email        = get_invoice_data.vendor_id.email

#     get_razor_pay_data  = razor_pay_data_tb.objects.all().exists()

#     if get_razor_pay_data == True:
#         get_razor_pay_data  = razor_pay_data_tb.objects.latest('id')
#     else:
#         get_razor_pay_data  = {}

#     amount_data         =   {
#                                 "current_amount"    : round(shop_wallet_amount),
#                                 "commission_amount" : round(commission_amount),
#                                 "additional_amount" : round(amount),
#                                 "name"              : vendor_name,
#                                 "email"             : vendor_email,
#                                 "razor_key"         : None if not get_razor_pay_data else get_razor_pay_data.razor_key,
#                                 "razor_secret"      : None if not get_razor_pay_data else get_razor_pay_data.razor_secret,
#                                 "have_bank"         : bank_tb.objects.filter(shop_id=get_invoice_data.shop_id.id).exists()
#                             } 

#     return amount_data


@method_decorator(csrf_exempt, name='dispatch')
def vendorInvoiceDetails(request):
    data                = json.loads(request.body.decode("utf-8"))

    invoice_id          = data.get('invoice_id')

    get_invoice_data    = invoice_data_tb.objects.all().filter(id=invoice_id).get()

    invoice_data        =   {
                                'id'                : get_invoice_data.id,
                                'customer_id'       : None if not get_invoice_data.user_id else get_invoice_data.user_id.id,
                                'customer_name'     : None if not get_invoice_data.user_id else get_invoice_data.user_id.name,
                                'phone'             : None if not get_invoice_data.user_id else get_invoice_data.user_id.phone,
                                'user_id'           : get_invoice_data.vendor_id.id,
                                'vendor_name'       : get_invoice_data.vendor_id.name,
                                'vendor_phone'      : get_invoice_data.vendor_id.phone,
                                'shop_id'           : get_invoice_data.shop_id.id,
                                'shop_name'         : get_invoice_data.shop_id.name,
                                'invoice_image'     : '' if not get_invoice_data.invoice_image else get_invoice_data.invoice_image.url,
                                'invoice_number'    : get_invoice_data.invoice_number,
                                'invoice_date'      : get_invoice_data.invoice_date,
                                'pre_tax_amount'    : get_invoice_data.pre_tax_amount,
                                'invoice_amount'    : get_invoice_data.invoice_amount,
                                'remark'            : get_invoice_data.remark,
                                'status'            : get_invoice_data.status,
                                "pay_half_amount"   : get_invoice_data.pay_half_amount,
                                "have_due_amount"   : get_invoice_data.have_due_amount,
                                'myself'            : True if get_invoice_data.submitted_by == 'Vendor' else False,
                                'vendor_image'      : "" if not get_invoice_data.vendor_id.profile_image else get_invoice_data.vendor_id.profile_image.url,
                                "user_image"        : "" if not get_invoice_data.user_id.profile_image else get_invoice_data.user_id.profile_image.url,
                            }


    amount_data         =   vendorAmountData(invoice_id)

    response            =   {
                                "invoice_data"  : invoice_data,
                                "amount_data"   : amount_data
                            }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def vendorInvoiceStatusChange(request):
    data                = json.loads(request.body.decode("utf-8"))

    invoice_id          = data.get('invoice_id')
    status              = data.get('status')
    remark              = data.get('remark')
    now                 = datetime.now()

    if status == "Approve":
        response        = updateWalletAmount(invoice_id,None)
        return JsonResponse(response, status=201)
    elif status == "Reject":
        invoice_data_tb.objects.all().filter(id=invoice_id).update(status=status,remark=remark,updated_at=now)
    else:
        invoice_data_tb.objects.all().filter(id=invoice_id).update(status=status,updated_at=now)

    response        =   {
                            "success"   : True,
                            "message"   : ""
                        }

    return JsonResponse(response, status=201)




def updateWalletAmount(invoice_id,bank_transaction_id):
    now                 = datetime.now()
    get_invoice_data    = invoice_data_tb.objects.all().filter(id=invoice_id).get()


    if get_invoice_data.status == 'Approve' or get_invoice_data.status == 'Reject':
        response        =   {
                                "success"   : False,
                                "message"   : "Can't Approve ,this invoice already "+get_invoice_data.status
                            }   
        return response 


    user_id             = get_invoice_data.user_id.id
    vendor_id           = get_invoice_data.vendor_id.id
    shop_id             = get_invoice_data.shop_id.id
    shop_commission     = get_invoice_data.shop_id.commission
    shop_half_commission= 50
    shop_wallet_amount  = 0 if not get_invoice_data.shop_id.wallet_amount else get_invoice_data.shop_id.wallet_amount
    invoice_amount      = get_invoice_data.pre_tax_amount


    if get_invoice_data.is_import:
        commission_amount   = float(invoice_amount)
    else:
        commission_amount   = is_what_percent_of(float(shop_commission), float(invoice_amount))

    # commission_amount   = float(invoice_amount)
    vendor_commission   = is_what_percent_of(float(shop_half_commission), float(commission_amount))
    vendor_balance      = is_what_percent_of(float(shop_half_commission), float(commission_amount))

    expiry_days         = "30"
    if settings_tb.objects.all().exists() == True:
        get_expiry_days = settings_tb.objects.all().latest('id')
        expiry_days     = get_expiry_days.expiry_days


    expiry_date         = (date.today()+timedelta(days=int(expiry_days))).isoformat()
    get_balance_amount  = commission_amount
    wallet_type         = "Direct"
    
    if float(shop_wallet_amount) >= float(vendor_commission):
        
        invoice_data_tb.objects.all().filter(id=invoice_id).update(status="Approve",updated_at=now)
        
        shop_amount     = float(shop_wallet_amount) - float(commission_amount) # after wonder app commission 
        parent_id_list  = []

        for x in range(1,16):            
            level_pct           = levels_tb.objects.all().filter(level=x).get()
            pct                 = level_pct.percentage

            user_comsn          = is_what_percent_of(float(pct), float(commission_amount))

            balance_amount      = get_balance_amount - user_comsn

            get_balance_amount  = balance_amount

            get_user_id         = user_data_tb.objects.get(id=user_id)
            get_invoice         = invoice_data_tb.objects.get(id=invoice_id)
            
            #Insert user wallet amount 
            insert_data = wallet_transactions_tb(user_id=get_user_id,vendor_id=get_invoice_data.vendor_id,shop_id=get_invoice_data.shop_id,amount=user_comsn,invoice_id=get_invoice,entry_type="Credit",expiry_date=expiry_date,wallet_type=wallet_type,status="Approve",bank_transaction_id=bank_transaction_id,created_at=now,updated_at=now)
            insert_data.save()

            #update user wallet amount
            update_user_wallet  = (0 if not get_user_id.wallet_amount else float(get_user_id.wallet_amount)) + float(user_comsn)
            
            user_data_tb.objects.all().filter(id=user_id).update(wallet_amount=update_user_wallet,updated_at=now)

            #Insert shop wallet amount 
            insert_data = shop_wallet_transactions_tb(user_id=get_user_id,vendor_id=get_invoice_data.vendor_id,shop_id=get_invoice_data.shop_id,amount=user_comsn,invoice_id=get_invoice,entry_type="Debit",wallet_type=wallet_type,created_at=now,updated_at=now)
            insert_data.save()

            #update shop wallet amount
            # get_shop            = shops_tb.objects.get(id=shop_id)
            # update_shop_wallet  = (0 if not get_shop.wallet_amount else int(get_shop.wallet_amount)) - int(user_comsn)
            # #---after wonder app commission - only wonder app commission decrease from shop commission
            shops_tb.objects.all().filter(id=shop_id).update(wallet_amount=shop_amount,updated_at=now)

            
            get_parent_id       = user_data_tb.objects.all().filter(id=user_id).get()

            ###########--- Notification ---####
            if float(user_comsn) > 0:
                #--- To User ---#
                device_token    = get_parent_id.device_token
                title           = 'Congratulations'
                body            = 'Your wallet is credited with '+str(user_comsn)+' points'
                sendNotificationToUser(device_token,title,body)

                insert_data = user_notification_tb(user_id=get_parent_id,title=title,description=body,created_at=now,updated_at=now)
                insert_data.save()
            ###########--- Notification ---####

            if get_parent_id.parent_id:
                parent_id       = get_parent_id.parent_id.id
                user_id         = parent_id
                wallet_type     = "Indirect"
                parent_id_list.append(parent_id)

            else:
                break

        # remaining amount add to wonder app - first user is wonder app user
        get_first_user          = user_data_tb.objects.all().first()
        
        if get_balance_amount > 0:
            wonder_wallet_amount    = float(get_first_user.wallet_amount) + (get_balance_amount)
            user_data_tb.objects.all().filter(id=get_first_user.id).update(wallet_amount=wonder_wallet_amount,updated_at=now)
            insert_data             = wallet_transactions_tb(user_id=get_first_user,vendor_id=get_invoice_data.vendor_id,shop_id=get_invoice_data.shop_id,amount=get_balance_amount,invoice_id=get_invoice,entry_type="Credit",wallet_type="Indirect",expiry_date=expiry_date,status="Approve",bank_transaction_id=bank_transaction_id,created_at=now,updated_at=now)
            insert_data.save()
        #

        ##---update wallet amount with balance amount
        get_invoice_current             = invoice_data_tb.objects.get(id=invoice_id)
        get_shop_current_wallet_amount  = get_invoice_current.shop_id.wallet_amount
        calculate_shop_wallet           = float(get_shop_current_wallet_amount) + float(vendor_balance)
        shops_tb.objects.all().filter(id=get_invoice_current.shop_id.id).update(wallet_amount=calculate_shop_wallet,updated_at=now)
        #
        

        invoice_data_tb.objects.all().filter(id=invoice_id).update(status="Approve",updated_at=now)
        updateUserRoleCommissionAndShopBalance(invoice_id,vendor_balance)

        response            =   {
                                    "success"   : True,
                                    "message"   : ""
                                }    
    else:
        amount_data         =   vendorAmountData(invoice_id)


        response            =   {
                                    "amount"        : amount_data['additional_amount'],
                                    "name"          : amount_data['name'],
                                    "email"         : amount_data['email'],
                                    "invoice_id"    : invoice_id,
                                    "razor_key"     : amount_data['razor_key'],
                                    "razor_secret"  : amount_data['razor_secret'],
                                    "have_bank"     : amount_data['have_bank'],
                                    "success"       : False,
                                    "message"       : "No sufficient balance",
                                }    

    return response



def updateUserRoleCommissionAndShopBalance(invoice_id,balance):
    now                 = datetime.now()
    get_invoice_data    = invoice_data_tb.objects.all().filter(id=invoice_id).get()

    get_shop_data       = get_invoice_data.shop_id
    get_added_by        = get_shop_data.added_by
    get_business_rep_id = get_shop_data.business_rep_id

    invoice_amount      = get_invoice_data.pre_tax_amount
    vendor_id           = get_invoice_data.vendor_id.id
    user_comsn          = None

    get_data            = settings_tb.objects.all()

    if get_data:
        for x in get_data:
            first_month_commission  = x.first_month_commission,
            field_visit_commission  = x.field_visit_commission

    if get_added_by:
        if(get_added_by.field_visit_commission == True):   
            user_comsn      = is_what_percent_of(float(field_visit_commission), float(invoice_amount))
            
            get_user_comsn  = get_added_by.commission_amount
            user_comsn      = float(0 if not get_user_comsn else get_user_comsn) + float(0 if not user_comsn else user_comsn)

            user_data_tb.objects.all().filter(id=get_added_by.id).update(commission_amount=user_comsn,updated_at=now)

            insert_data     = user_transactions_tb(user_id=get_added_by,vendor_id=get_invoice_data.vendor_id,shop_id=get_invoice_data.shop_id,amount=user_comsn,invoice_id=get_invoice_data,entry_type="Credit",wallet_type='User Field Visit Commission',created_at=now,updated_at=now)
            insert_data.save() 
        else:
            # Calculate the datetime for one month ago
            one_month_ago   = timezone.now() - timedelta(days=30)

            # Check if the shop's creation date is after one month ago
            if get_shop_data.created_at < one_month_ago:
                user_data_tb.objects.all().filter(id=get_added_by.id).update(field_visit_commission=True,updated_at=now)
                updateUserRoleCommissionAndShopBalance(invoice_id,balance)
                
            else:
                user_comsn      = is_what_percent_of(float(first_month_commission), float(invoice_amount))
                get_user_comsn  = get_added_by.commission_amount
                user_comsn      = float(0 if not get_user_comsn else get_user_comsn) + float(0 if not user_comsn else user_comsn)

                user_data_tb.objects.all().filter(id=get_added_by.id).update(commission_amount=user_comsn,updated_at=now)

            insert_data         = user_transactions_tb(user_id=get_added_by,vendor_id=get_invoice_data.vendor_id,shop_id=get_invoice_data.shop_id,amount=user_comsn,invoice_id=get_invoice_data,entry_type="Credit",wallet_type='User First Month Commission',created_at=now,updated_at=now)
            insert_data.save()   

    if get_business_rep_id:
        one_month_ago   = timezone.now() - timedelta(days=30)

        # Check if the shop's creation date is after one month ago
        if get_shop_data.created_at > one_month_ago:
            user_comsn      = is_what_percent_of(float(first_month_commission), float(invoice_amount))
            get_user_comsn  = get_added_by.commission_amount
            user_comsn      = float(0 if not get_user_comsn else get_user_comsn) + float(0 if not user_comsn else user_comsn)

            user_data_tb.objects.all().filter(id=get_business_rep_id.id).update(commission_amount=user_comsn,updated_at=now)

            insert_data     = user_transactions_tb(user_id=get_added_by,vendor_id=get_invoice_data.vendor_id,shop_id=get_invoice_data.shop_id,amount=user_comsn,invoice_id=get_invoice_data,entry_type="Credit",wallet_type='User First Month Commission',created_at=now,updated_at=now)
            insert_data.save()   


    #update shop balance amount
    get_shop_balance_amount = get_shop_data.balance_amount
    shop_balance_amount     = float(0 if not get_shop_balance_amount else get_shop_balance_amount) + float(0 if not balance else balance)

    shops_tb.objects.all().filter(id=get_shop_data.id).update(balance_amount=shop_balance_amount,updated_at=now)
    
    insert_data             = user_transactions_tb(vendor_id=get_invoice_data.vendor_id,shop_id=get_invoice_data.shop_id,amount=balance,invoice_id=get_invoice_data,entry_type="Credit",wallet_type='Shop Due Amount',created_at=now,updated_at=now)
    insert_data.save()  

    return



# def updateWalletAmount(invoice_id,bank_transaction_id):
#     now                 = datetime.now()
#     get_invoice_data    = invoice_data_tb.objects.all().filter(id=invoice_id).get()


#     if get_invoice_data.status == 'Approve' or get_invoice_data.status == 'Reject':
#         response        =   {
#                                 "success"   : False,
#                                 "message"   : "Can't Approve ,this invoice already "+get_invoice_data.status
#                             }   
#         return response 


#     user_id             = get_invoice_data.user_id.id
#     vendor_id           = get_invoice_data.vendor_id.id
#     shop_id             = get_invoice_data.shop_id.id
#     shop_commission     = get_invoice_data.shop_id.commission
#     shop_wallet_amount  = 0 if not get_invoice_data.shop_id.wallet_amount else get_invoice_data.shop_id.wallet_amount
#     invoice_amount      = get_invoice_data.pre_tax_amount


#     if get_invoice_data.is_import:
#         commission_amount   = float(invoice_amount)
#     else:
#         commission_amount   = is_what_percent_of(float(shop_commission), float(invoice_amount))

#     expiry_days         = "30"
#     if settings_tb.objects.all().exists() == True:
#         get_expiry_days = settings_tb.objects.all().latest('id')
#         expiry_days     = get_expiry_days.expiry_days


#     expiry_date         = (date.today()+timedelta(days=int(expiry_days))).isoformat()
#     get_balance_amount  = commission_amount
#     wallet_type         = "Direct"
    
#     if float(shop_wallet_amount) >= float(commission_amount):
#         invoice_data_tb.objects.all().filter(id=invoice_id).update(status="Approve",updated_at=now)
        
#         shop_amount     = float(shop_wallet_amount) - float(commission_amount) # after wonder app commission 
#         parent_id_list  = []

#         for x in range(1,16):            
#             level_pct           = levels_tb.objects.all().filter(level=x).get()
#             pct                 = level_pct.percentage

#             user_comsn          = is_what_percent_of(float(pct), float(commission_amount))

#             balance_amount      = get_balance_amount - user_comsn

#             get_balance_amount  = balance_amount

#             get_user_id         = user_data_tb.objects.get(id=user_id)
#             get_invoice         = invoice_data_tb.objects.get(id=invoice_id)
            
#             #Insert user wallet amount 
#             insert_data = wallet_transactions_tb(user_id=get_user_id,vendor_id=get_invoice_data.vendor_id,shop_id=get_invoice_data.shop_id,amount=user_comsn,invoice_id=get_invoice,entry_type="Credit",expiry_date=expiry_date,wallet_type=wallet_type,status="Approve",bank_transaction_id=bank_transaction_id,created_at=now,updated_at=now)
#             insert_data.save()

#             #update user wallet amount
#             update_user_wallet  = (0 if not get_user_id.wallet_amount else float(get_user_id.wallet_amount)) + float(user_comsn)
            
#             user_data_tb.objects.all().filter(id=user_id).update(wallet_amount=update_user_wallet,updated_at=now)

#             #Insert shop wallet amount 
#             insert_data = shop_wallet_transactions_tb(user_id=get_user_id,vendor_id=get_invoice_data.vendor_id,shop_id=get_invoice_data.shop_id,amount=user_comsn,invoice_id=get_invoice,entry_type="Debit",wallet_type=wallet_type,created_at=now,updated_at=now)
#             insert_data.save()

#             #update shop wallet amount
#             # get_shop            = shops_tb.objects.get(id=shop_id)
#             # update_shop_wallet  = (0 if not get_shop.wallet_amount else int(get_shop.wallet_amount)) - int(user_comsn)
#             # #---after wonder app commission - only wonder app commission decrease from shop commission
#             shops_tb.objects.all().filter(id=shop_id).update(wallet_amount=shop_amount,updated_at=now)

            
#             get_parent_id       = user_data_tb.objects.all().filter(id=user_id).get()

#             ###########--- Notification ---####
#             if float(user_comsn) > 0:
#                 #--- To User ---#
#                 device_token    = get_parent_id.device_token
#                 title           = 'Congratulations'
#                 body            = 'Your wallet is credited with '+str(user_comsn)+' points'
#                 sendNotificationToUser(device_token,title,body)

#                 insert_data = user_notification_tb(user_id=get_parent_id,title=title,description=body,created_at=now,updated_at=now)
#                 insert_data.save()
#             ###########--- Notification ---####

#             if get_parent_id.parent_id:
#                 parent_id       = get_parent_id.parent_id.id
#                 user_id         = parent_id
#                 wallet_type     = "Indirect"
#                 parent_id_list.append(parent_id)

#             else:
#                 break

#         # remaining amount add to wonder app - first user is wonder app user
#         get_first_user          = user_data_tb.objects.all().first()
        
#         if get_balance_amount > 0:
#             wonder_wallet_amount    = float(get_first_user.wallet_amount) + (get_balance_amount)
#             user_data_tb.objects.all().filter(id=get_first_user.id).update(wallet_amount=wonder_wallet_amount,updated_at=now)
#             insert_data             = wallet_transactions_tb(user_id=get_first_user,vendor_id=get_invoice_data.vendor_id,shop_id=get_invoice_data.shop_id,amount=get_balance_amount,invoice_id=get_invoice,entry_type="Credit",wallet_type="Indirect",expiry_date=expiry_date,status="Approve",bank_transaction_id=bank_transaction_id,created_at=now,updated_at=now)
#             insert_data.save()
#         #

#         invoice_data_tb.objects.all().filter(id=invoice_id).update(status="Approve",updated_at=now)

#         response            =   {
#                                     "success"   : True,
#                                     "message"   : ""
#                                 }    
#     else:
#         amount_data         =   vendorAmountData(invoice_id)


#         response            =   {
#                                     "amount"        : amount_data['additional_amount'],
#                                     "name"          : amount_data['name'],
#                                     "email"         : amount_data['email'],
#                                     "invoice_id"    : invoice_id,
#                                     "razor_key"     : amount_data['razor_key'],
#                                     "razor_secret"  : amount_data['razor_secret'],
#                                     "have_bank"     : amount_data['have_bank'],
#                                     "success"       : False,
#                                     "message"       : "No sufficient balance",
#                                 }    

#     return response



@method_decorator(csrf_exempt, name='dispatch')
def vendorInvoiceStatusChangeAmountDetails(request):
    data                = json.loads(request.body.decode("utf-8"))
    invoice_id          = data.get('invoice_id')

    get_invoice_data    = invoice_data_tb.objects.all().filter(id=invoice_id).get()

    shop_commission     = get_invoice_data.shop_id.commission
    shop_wallet_amount  = 0 if not get_invoice_data.shop_id.wallet_amount else get_invoice_data.shop_id.wallet_amount
    invoice_amount      = get_invoice_data.pre_tax_amount
    shop_wallet_amount  = float(shop_wallet_amount)

    commission_amount   = is_what_percent_of(float(shop_commission), float(invoice_amount))

    amount              = float(commission_amount) - float(shop_wallet_amount)

    response            =   {
                                "current_amount"    : shop_wallet_amount,
                                "commission_amount" : commission_amount,
                                "additional_amount" : amount,
                                "invoice_id"        : invoice_id,
                            }    

    return JsonResponse(response, status=201)




def is_what_percent_of(num_a, num_b):
    return round((num_a / 100) * num_b,2)



@method_decorator(csrf_exempt, name='dispatch')
def vendorwalletTransactionsList(request):
    data                    = json.loads(request.body.decode("utf-8"))

    vendor_id               = data.get('user_id')

    get_transaction_data    = wallet_transactions_tb.objects.all().filter(vendor_id=vendor_id,wallet_type="Direct").order_by('-id')

    #-- Pagination
    paginator               = Paginator(get_invoice, per_page=20)
    page_number             = data.get('page')
    page                    = paginator.get_page(page_number)
    total_pages             = paginator.num_pages
    #-- Pagination

    transaction_data        = []
    for transaction in page:
        transaction_data.append({
                    'id'                    : transaction.id,
                    'customer_id'           : None if not transaction.user_id else transaction.user_id.id,
                    'user_id'               : transaction.vendor_id.id,
                    'shop_id'               : transaction.shop_id.id,
                    'invoice_number'        : None if not transaction.invoice_id else transaction.invoice_id.invoice_number,
                    'amount'                : transaction.amount,
                    'bank_transaction_id'   : None if not transaction.bank_transaction_id else transaction.bank_transaction_id.id,
                    'wallet_type'           : transaction.wallet_type,
                    'expiry_date'           : transaction.expiry_date, 
                    'entry_type'            : transaction.entry_type,
                    'remark'                : transaction.remark,
                    'status'                : transaction.status,
                    'created_at'            : transaction.created_at.strftime("%Y %b %d, %I:%M %p")
                }) 

    response        =   {
                            "transaction_data"  : transaction_data,
                            "page"              : page_number,
                            "total_pages"       : total_pages
                        }

    return JsonResponse(response, status=201)





@method_decorator(csrf_exempt, name='dispatch')
def searchVendorwalletTransactionsList(request):
    data                        = json.loads(request.body.decode("utf-8"))

    search_key                  = data.get('search_key')
    shop_id                     = data.get('shop_id')
    date                        = None
    user_phone                  = None

    if user_phone:
        user_ids                = user_data_tb.objects.all().filter(phone__icontains=user_phone).values('id')
        id_list                 = [obj['id'] for obj in user_ids]

        get_transaction_data    = wallet_transactions_tb.objects.all().filter(user_id__in=id_list,vendor_id=vendor_id,wallet_type="Direct").order_by('-id')

    elif date:
        user_ids                = user_data_tb.objects.all().filter(phone__icontains=user_phone).values('id')
        id_list                 = [obj['id'] for obj in user_ids]

        date_obj                = datetime.strptime(date, '%Y-%m-%d')
        date                    = date_obj.date()

        get_transaction_data    = wallet_transactions_tb.objects.all().filter(created_at__date=date,vendor_id=vendor_id,wallet_type="Direct").order_by('-id')

    
    #-- Pagination
    paginator                   = Paginator(get_transaction_data, per_page=20)
    page_number                 = data.get('page')
    page                        = paginator.get_page(page_number)
    total_pages                 = paginator.num_pages
    #-- Pagination

    transaction_data        = []
    for transaction in page:
        transaction_data.append({
                    'id'                    : transaction.id,
                    'customer_id'           : None if not transaction.user_id else transaction.user_id.id,
                    'user_id'               : transaction.vendor_id.id,
                    'shop_id'               : transaction.shop_id.id,
                    'invoice_number'        : None if not transaction.invoice_id else transaction.invoice_id.invoice_number,
                    'amount'                : transaction.amount,
                    'bank_transaction_id'   : None if not transaction.bank_transaction_id else transaction.bank_transaction_id.id,
                    'wallet_type'           : transaction.wallet_type,
                    'expiry_date'           : transaction.expiry_date, 
                    'entry_type'            : transaction.entry_type,
                    'remark'                : transaction.remark,
                    'status'                : transaction.status,
                    'created_at'            : transaction.created_at.strftime("%Y %b %d, %I:%M %p")
                }) 

    response        =   {
                            "transaction_data"  : transaction_data,
                            "page"              : page_number,
                            "total_pages"       : total_pages
                        }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def searchShopwalletTransactions(request):
    data                = json.loads(request.body.decode("utf-8"))

    search_key          = data.get('search_key')
    shop_id             = data.get('shop_id')
    date                = None
    user_phone          = None

    if is_valid_date(search_key):
        date            = search_key
    else:
        user_phone      = search_key

    if user_phone:
        user_ids                = user_data_tb.objects.all().filter(phone__icontains=user_phone).values('id')
        id_list                 = [obj['id'] for obj in user_ids]

        get_transaction_data    = shop_wallet_transactions_tb.objects.all().filter(user_id__in=id_list,shop_id=shop_id,wallet_type="Direct").order_by('-id')

    elif date:
        user_ids                = user_data_tb.objects.all().filter(phone__icontains=user_phone).values('id')
        id_list                 = [obj['id'] for obj in user_ids]

        date_obj                = datetime.strptime(date, '%Y-%m-%d')
        date                    = date_obj.date()

        get_transaction_data    = shop_wallet_transactions_tb.objects.all().filter(created_at__date=date,shop_id=shop_id,wallet_type="Direct").order_by('-id')


    #-- Pagination
    paginator                   = Paginator(get_transaction_data, per_page=20)
    page_number                 = data.get('page')
    page                        = paginator.get_page(page_number)
    total_pages                 = paginator.num_pages
    #-- Pagination

    transaction_data            = []
    for transaction in page:
        transaction_data.append({
                    'id'                    : transaction.id,
                    'customer_id'           : None if not transaction.user_id else transaction.user_id.id,
                    'customer_name'         : None if not transaction.user_id else transaction.user_id.name,
                    'phone'                 : None if not transaction.user_id else transaction.user_id.phone,
                    'user_id'               : transaction.vendor_id.id,
                    'shop_id'               : transaction.shop_id.id,
                    'invoice_number'        : None if not transaction.invoice_id else transaction.invoice_id.invoice_number,
                    'amount'                : transaction.amount,
                    'bank_transaction_id'   : transaction.bank_transaction_id,
                    'wallet_type'           : transaction.wallet_type,
                    'entry_type'            : transaction.entry_type,
                    'remark'                : transaction.remark,
                    'status'                : transaction.status,
                    'created_at'            : transaction.created_at.strftime("%Y %b %d, %I:%M %p")
                }) 

    response        =   {
                            "transaction_data"  : transaction_data,
                            "page"              : page_number,
                            "total_pages"       : total_pages
                        }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def shopwalletTransactionsList(request):
    data                        = json.loads(request.body.decode("utf-8"))

    shop_id                     = data.get('shop_id')
    entry_type                  = data.get('entry_type')

    if(entry_type):
        get_transaction_data    = shop_wallet_transactions_tb.objects.all().filter(shop_id=shop_id,wallet_type="Direct",entry_type=entry_type).order_by('-id')
    else:
        get_transaction_data    = shop_wallet_transactions_tb.objects.all().filter(shop_id=shop_id,wallet_type="Direct").order_by('-id')
    shop_data                   = shops_tb.objects.all().filter(id=shop_id).get()

    #-- Pagination
    paginator                   = Paginator(get_transaction_data, per_page=10)
    page_number                 = data.get('page')
    page                        = paginator.get_page(page_number)
    total_pages                 = paginator.num_pages
    #-- Pagination

    transaction_data        = []
    for transaction in page:
        transaction_data.append({
                    'id'                    : transaction.id,
                    'customer_id'           : None if not transaction.user_id else transaction.user_id.id,
                    'customer_name'         : None if not transaction.user_id else transaction.user_id.name,
                    'phone'                 : None if not transaction.user_id else transaction.user_id.phone,
                    'user_id'               : transaction.vendor_id.id,
                    'shop_id'               : transaction.shop_id.id,
                    'invoice_number'        : None if not transaction.invoice_id else transaction.invoice_id.invoice_number,
                    'amount'                : transaction.amount,
                    'bank_transaction_id'   : transaction.bank_transaction_id,
                    'wallet_type'           : transaction.wallet_type,
                    'entry_type'            : transaction.entry_type,
                    'remark'                : transaction.remark,
                    'status'                : transaction.status,
                    'created_at'            : transaction.created_at.strftime("%Y %b %d, %I:%M %p")
                }) 

    response        =   {
                            "shop_wallet_amount": round(float(0 if not shop_data.wallet_amount else shop_data.wallet_amount),2),
                            "transaction_data"  : transaction_data,
                            "page"              : page_number,
                            "total_pages"       : total_pages
                        }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def filterShopwalletTransactionsByDateRange(request):
    data                        = json.loads(request.body.decode("utf-8"))

    shop_id                     = data.get('shop_id')
    date_from                   = datetime.strptime(data.get('date_from'), "%Y-%m-%d")
    date_to                     = datetime.strptime(data.get('date_to'), "%Y-%m-%d")

    entry_type                  = data.get('entry_type')

    if(entry_type):
        get_transaction_data    =   (
                                        shop_wallet_transactions_tb.objects.all()
                                        .filter(shop_id=shop_id,wallet_type="Direct",entry_type=entry_type,created_at__date__gte=date_from.date(), created_at__date__lte=date_to.date())
                                        .exclude(created_at__date=date_to.date(), created_at__time__gt=time(23, 59, 59))
                                        .order_by('-id')
                                    )
    else:
        get_transaction_data    =   (
                                        shop_wallet_transactions_tb.objects.all()
                                        .filter(shop_id=shop_id,wallet_type="Direct",created_at__date__gte=date_from.date(), created_at__date__lte=date_to.date())
                                        .exclude(created_at__date=date_to.date(), created_at__time__gt=time(23, 59, 59))
                                        .order_by('-id')
                                    )

    shop_data               = shops_tb.objects.all().filter(id=shop_id).get()

    #-- Pagination
    paginator               = Paginator(get_transaction_data, per_page=10)
    page_number             = data.get('page')
    page                    = paginator.get_page(page_number)
    total_pages             = paginator.num_pages
    #-- Pagination

    transaction_data        = []
    for transaction in page:
        transaction_data.append({
                    'id'                    : transaction.id,
                    'customer_id'           : None if not transaction.user_id else transaction.user_id.id,
                    'customer_name'         : None if not transaction.user_id else transaction.user_id.name,
                    'phone'                 : None if not transaction.user_id else transaction.user_id.phone,
                    'user_id'               : transaction.vendor_id.id,
                    'shop_id'               : transaction.shop_id.id,
                    'invoice_number'        : None if not transaction.invoice_id else transaction.invoice_id.invoice_number,
                    'amount'                : transaction.amount,
                    'bank_transaction_id'   : transaction.bank_transaction_id,
                    'wallet_type'           : transaction.wallet_type,
                    'entry_type'            : transaction.entry_type,
                    'remark'                : transaction.remark,
                    'status'                : transaction.status,
                    'created_at'            : transaction.created_at.strftime("%Y %b %d, %I:%M %p")
                }) 

    response        =   {
                            "shop_wallet_amount": round(float(0 if not shop_data.wallet_amount else shop_data.wallet_amount),2),
                            "transaction_data"  : transaction_data,
                            "page"              : page_number,
                            "total_pages"       : total_pages
                        }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def filterShopwalletTransactionsByEntryType(request):
    data                    = json.loads(request.body.decode("utf-8"))

    shop_id                 = data.get('shop_id')
    entry_type              = data.get('entry_type')

    get_transaction_data    = shop_wallet_transactions_tb.objects.all().filter(shop_id=shop_id,wallet_type="Direct",entry_type=entry_type).order_by('-id')
    shop_data               = shops_tb.objects.all().filter(id=shop_id).get()

    #-- Pagination
    paginator               = Paginator(get_transaction_data, per_page=20)
    page_number             = data.get('page')
    page                    = paginator.get_page(page_number)
    total_pages             = paginator.num_pages
    #-- Pagination

    transaction_data        = []
    
    for transaction in page:
        transaction_data.append({
                    'id'                    : transaction.id,
                    'customer_id'           : None if not transaction.user_id else transaction.user_id.id,
                    'customer_name'         : None if not transaction.user_id else transaction.user_id.name,
                    'phone'                 : None if not transaction.user_id else transaction.user_id.phone,
                    'user_id'               : transaction.vendor_id.id,
                    'shop_id'               : transaction.shop_id.id,
                    'invoice_number'        : None if not transaction.invoice_id else transaction.invoice_id.invoice_number,
                    'amount'                : transaction.amount,
                    'bank_transaction_id'   : transaction.bank_transaction_id,
                    'wallet_type'           : transaction.wallet_type,
                    'entry_type'            : transaction.entry_type,
                    'remark'                : transaction.remark,
                    'status'                : transaction.status,
                    'created_at'            : transaction.created_at.strftime("%Y %b %d, %I:%M %p")
                }) 

    response        =   {
                            "shop_wallet_amount": round(float(0 if not shop_data.wallet_amount else shop_data.wallet_amount),2),
                            "transaction_data"  : transaction_data,
                            "page"              : page_number,
                            "total_pages"       : total_pages
                        }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def vendorBankTransactionsList(request):
    data                    = json.loads(request.body.decode("utf-8"))

    vendor_id               = data.get('user_id')

    get_transaction_data    = bank_transactions_tb.objects.all().filter(vendor_id=vendor_id).order_by('-id')

    transaction_data        = []
    for transaction in get_transaction_data:
        transaction_data.append({
                    'id'                        : transaction.id,
                    'customer_id'               : None if not transaction.user_id else transaction.user_id.id,
                    'user_id'                   : transaction.vendor_id.id,
                    'razorpay_transaction_id'   : transaction.razorpay_transaction_id,
                    'entry_type'                : transaction.entry_type,
                    'amount'                    : transaction.amount,
                    'bank'                      : transaction.bank_id.name,
                    'razorpay_status'           : transaction.razorpay_status,
                    'payment_type'              : transaction.payment_type,
                    'transaction_status'        : transaction.transaction_status, 
                }) 

    response        =   {
                            "transaction_data"  : transaction_data
                        }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def vendorInvoiceFilterByShop(request):
    data                = json.loads(request.body.decode("utf-8"))

    shop_id             = data.get('shop_id')

    get_invoice_data    = invoice_data_tb.objects.all().filter(shop_id=shop_id).order_by('-id')

    #-- Pagination
    paginator           = Paginator(get_invoice_data, per_page=10)
    page_number         = data.get('page')
    page                = paginator.get_page(page_number)
    # Get the total number of pages
    total_pages         = paginator.num_pages
    #-- Pagination

    invoice_data        = []
    for invoice in page:
        amount_data     =   vendorAmountData(invoice.id)

        invoice_data.append({
                    'id'            : invoice.id,
                    'customer_id'   : None if not invoice.user_id else invoice.user_id.id,
                    'customer_name' : None if not invoice.user_id else invoice.user_id.name,
                    'phone'         : None if not invoice.user_id else invoice.user_id.phone,
                    'user_id'       : invoice.vendor_id.id,
                    'shop_id'       : invoice.shop_id.id,
                    'shop_name'     : invoice.shop_id.name,
                    'invoice_image' : '' if not invoice.invoice_image else invoice.invoice_image.url,
                    'invoice_number': invoice.invoice_number,
                    'invoice_date'  : invoice.invoice_date,
                    'pre_tax_amount': invoice.pre_tax_amount,
                    'invoice_amount': invoice.invoice_amount,
                    'remark'        : invoice.remark,
                    'status'        : invoice.status,
                    'myself'        : True if invoice.submitted_by == 'Vendor' else False,
                    'vendor_image'  : "" if not invoice.vendor_id.profile_image else invoice.vendor_id.profile_image.url,
                    "user_image"    : "" if not invoice.user_id.profile_image else invoice.user_id.profile_image.url,
                    'amount_data'   : amount_data
                }) 

    response        =   {
                            "invoice_data"  : invoice_data,
                            "page"          : page_number,
                            "total_pages"   : total_pages
                        }
    
    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def shopInvoiceFilterByStatus(request):
    data                = json.loads(request.body.decode("utf-8"))

    shop_id             = data.get('shop_id')
    status              = data.get('status')

    if status=='All':
        get_invoice_data    = invoice_data_tb.objects.all().filter(shop_id=shop_id).order_by('-id')
    else:
        get_invoice_data    = invoice_data_tb.objects.all().filter(shop_id=shop_id,status=status).order_by('-id')

    #-- Pagination
    paginator           = Paginator(get_invoice_data, per_page=20)
    page_number         = data.get('page')
    page                = paginator.get_page(page_number)
    # Get the total number of pages
    total_pages         = paginator.num_pages
    #-- Pagination

    invoice_data        = []
    for invoice in page:
        amount_data     =   vendorAmountData(invoice.id)

        invoice_data.append({
                    'id'            : invoice.id,
                    'customer_id'   : None if not invoice.user_id else invoice.user_id.id,
                    'customer_name' : None if not invoice.user_id else invoice.user_id.name,
                    'phone'         : None if not invoice.user_id else invoice.user_id.phone,
                    'user_id'       : invoice.vendor_id.id,
                    'shop_id'       : invoice.shop_id.id,
                    'shop_name'     : invoice.shop_id.name,
                    'invoice_image' : '' if not invoice.invoice_image else invoice.invoice_image.url,
                    'invoice_number': invoice.invoice_number,
                    'invoice_date'  : invoice.invoice_date,
                    'pre_tax_amount': invoice.pre_tax_amount,
                    'invoice_amount': invoice.invoice_amount,
                    'remark'        : invoice.remark,
                    'status'        : invoice.status,
                    'myself'        : True if invoice.submitted_by == 'Vendor' else False,
                    'vendor_image'  : "" if not invoice.vendor_id.profile_image else invoice.vendor_id.profile_image.url,
                    "user_image"    : "" if not invoice.user_id.profile_image else invoice.user_id.profile_image.url,
                    'amount_data'   : amount_data
                }) 

    response        =   {
                            "invoice_data"  : invoice_data,
                            "page"          : page_number,
                            "total_pages"   : total_pages
                        }
    
    return JsonResponse(response, status=201)



def getAllUsers(request):
    get_users_list  = user_data_tb.objects.all().filter(active=True)

    users_data      = []
    
    for user in get_users_list:
        users_data.append({
                'id'            : user.id,
                'name'          : user.name,
                'phone'         : user.phone,
                'image'         : "" if not user.profile_image else user.profile_image.url,
            })

    response        =   {
                            "users_data"   : users_data,
                        }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def vendorAddInvoice(request):
    data                = json.loads(request.body.decode("utf-8"))

    
    get_vendor_id       = data.get('user_id')
    vendor_id           = vendors_tb.objects.get(id=get_vendor_id)
    get_shop_id         = data.get('shop_id')
    shop_id             = shops_tb.objects.get(id=get_shop_id)
    invoice_image       = data.get('invoice_image')
    invoice_number      = data.get('invoice_number')
    invoice_date        = data.get('invoice_date')
    pre_tax_amount      = data.get('pre_tax_amount')
    invoice_amount      = data.get('invoice_amount')
    remark              = data.get('remark')
    submitted_by        = 'Vendor'
    # status              = 'Approved'
    now                 = datetime.now()
    date_time           = now.strftime("%Y%b%d%H%M%S")

    #################################################################################
    phone               = data.get('phone')
    check_user_exist    = user_data_tb.objects.all().filter(phone=phone).exists()

    if check_user_exist:
        user_data       = user_data_tb.objects.get(phone=phone)
    else:
        user_data       = user_data_tb(phone=phone,active=True,created_at=now,updated_at=now)
        user_data.save()

        latest_id       = user_data_tb.objects.latest('id')

        get_all_data    = user_data_tb.objects.count()

        if get_all_data != 1:
            get_default_parent_id   = default_data_tb.objects.filter(title='user_default_parent_id').get()
            default_parent_id       = get_default_parent_id.value

            get_user_data           = user_data_tb.objects.filter(parent_id=default_parent_id).count()

            if get_user_data < 2:
                get_parent_id       = user_data_tb.objects.get(id=default_parent_id)
                user_data_tb.objects.all().filter(id=latest_id.id).update(parent_id=get_parent_id,updated_at=now)
                
            else:
                default_parent_id   = int(get_default_parent_id.value) + (1)
                get_parent_id       = user_data_tb.objects.get(id=default_parent_id)
                user_data_tb.objects.all().filter(id=latest_id.id).update(parent_id=get_parent_id,updated_at=now)
        else:
            default_parent_id       = latest_id.id
        #update current default parent id
        default_data_tb.objects.all().filter(title='user_default_parent_id').update(value=default_parent_id,updated_at=now)

    user_id             = user_data
    #################################################################################

    ##### check invoice exist - same invoice number not duplicate
    get_invoice         = invoice_data_tb.objects.all().filter(shop_id=shop_id.id,invoice_number=invoice_number)
    if get_invoice:
        response        =   {
                                "success"   : False,
                                "message"   : "Invoice exist"
                            }
        return JsonResponse(response, status=201)
    ##### check invoice exist ###

    if(invoice_image != None):
        image           = uploadImage(invoice_image,'invoice-'+invoice_number+'-'+date_time)
    else:
        image           = None

    insert_data         = invoice_data_tb(user_id=user_id,vendor_id=vendor_id,shop_id=shop_id,invoice_image=image,invoice_number=invoice_number,invoice_date=invoice_date,pre_tax_amount=pre_tax_amount,invoice_amount=invoice_amount,remark=remark,submitted_by=submitted_by,status='Verified',created_at=now,updated_at=now)
    insert_data.save()

    # Retrieve the ID of the newly created invoice record
    invoice_id          = insert_data.id
    invoice_data        = invoice_data_tb.objects.get(id=invoice_id)
    # invoice_data.invoice_number = 'Wonder' + shop_data.name + str(invoice_id)
    invoice_data.invoice_number = str(invoice_id)
    invoice_data.save()

    response            =   {
                                "invoice_id": invoice_id,
                                "success"   : True,
                                "message"   : ""
                            }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def vendorInvoiceAmountData(request):
    data                    = json.loads(request.body.decode("utf-8"))
    shop_id                 = data.get('shop_id')
    invoice_amount          = data.get('invoice_amount')

    get_shop_data           = shops_tb.objects.all().filter(id=shop_id).get()
    shop_commission         = get_shop_data.commission

    commission_amount       = is_what_percent_of(float(shop_commission), float(invoice_amount))

    level_pct               = levels_tb.objects.all().filter(level=1).get()
    pct                     = level_pct.percentage

    user_comsn              = is_what_percent_of(float(pct), float(commission_amount))
    #######################################

    shop_wallet_amount      = 0 if not get_shop_data.wallet_amount else get_shop_data.wallet_amount
    additional_amount       = 0
    first_commission        = 0

    if(float(commission_amount) > float(shop_wallet_amount)):
        additional_amount   = float(commission_amount) - float(shop_wallet_amount)
    
    ########################################

    verified_invoice_data   = invoice_data_tb.objects.all().filter(shop_id=get_shop_data.id,status='Verified')

    invoice_data        = []
    for invoice in verified_invoice_data:
        amount_data     =   vendorAmountData(invoice.id)
        invoice_data.append({
                    'id'            : invoice.id,
                    'amount_data'   : amount_data
                }) 

    #--- amount data
    cal_total_amount        = 0
    total_amount            = 0
    shop_wallet_amount      = float(0 if not get_shop_data.wallet_amount else get_shop_data.wallet_amount)
    for invoice in invoice_data:
        total_amount += invoice['amount_data']['commission_amount']

    total_amount            = total_amount + commission_amount

    if total_amount > shop_wallet_amount:
        cal_total_amount    = total_amount - shop_wallet_amount

    response                =   {
                                    "total_verified"    : cal_total_amount,
                                    "user_credit"       : user_comsn,
                                    "additional_amount" : invoice_amount
                                }

    return JsonResponse(response, status=201)




def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)

        return file_url
        return JsonResponse({'file_url': file_url})
    return JsonResponse({'error': 'Invalid request'})



@method_decorator(csrf_exempt, name='dispatch')
def getVendorEditShopDetails(request):
    data                = json.loads(request.body.decode("utf-8"))
    shop_id             = data.get('shop_id')
    shop                = shops_tb.objects.all().filter(id=shop_id).get()

    shop_data           =   {
                                'id'            : shop.id,
                                'shop_name'     : shop.name,
                                'featured_image': "" if not shop.image else shop.image.url,
                                'category_id'   : shop.category_id.id, 
                                'category'      : shop.category_id.name, 
                                'gst_number'    : shop.gst_number,
                                'license_number': shop.license_number,
                                'address'       : shop.address,
                                'location'      : shop.location,
                                'latitude'      : shop.latitude,
                                'longitude'     : shop.longitude,
                                'radius'        : shop.radius,
                                'is_featured'   : shop.is_featured,
                                'gst_image'     : "" if not shop.gst_image else shop.gst_image.url,
                                'license_image' : "" if not shop.license_image else shop.license_image.url,
                                'banner_image'  : "" if not shop.banner_image else shop.banner_image.url,
                                'commission'    : shop.commission,
                                'wallet_amount' : shop.wallet_amount,
                                'status'        : shop.status,
                                'gst_pct'       : shop.gst_pct,
                                'opening_time'  : "00:00" if not shop.opening_time else shop.opening_time,
                                'closing_time'  : "00:00" if not shop.closing_time else shop.closing_time,
                                'website_url'   : "" if not shop.website_url else shop.website_url,
                                'upi_id'        : shop.upi_id,
                                'phone1'        : shop.phone1,
                                'phone2'        : shop.phone2,
                            }

    response            =   {
                                "shop_data" : shop_data
                            }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def vendorEditShop(request):
    if request.method=="POST":
        data                = json.loads(request.body.decode("utf-8"))

        shop_id             = data.get('shop_id')
        name                = data.get('name')
        get_vendor_id       = data.get('user_id')
        vendor_id           = vendors_tb.objects.get(id=get_vendor_id)
        get_category_id     = data.get('category_id')
        category_id         = category_tb.objects.get(id=get_category_id)
        gst_number          = data.get('gst_number')
        address             = data.get('address')
        latitude            = data.get('latitude')
        longitude           = data.get('longitude')
        location            = data.get('location')
        radius              = "30"
        commission          = data.get('commission')
        license_number      = data.get('license_number')
        get_featured_image  = data.get('featured_image')
        get_gst_image       = data.get('gst_image')
        get_license_image   = data.get('license_image')
        get_banner_image    = data.get('banner_image')
        gst_pct             = data.get('gst_pct')
        opening_time        = data.get('opening_time')
        closing_time        = data.get('closing_time')

        website_url         = data.get('website_url')
        phone1              = data.get('phone1')
        phone2              = data.get('phone2')

        is_featured         = True if request.POST.get('is_featured') == 'true' else False

        if settings_tb.objects.all().exists() == True:
            get_radius      = settings_tb.objects.all().latest('id')
            radius          = get_radius.radius

        now                 = datetime.now()

        date_time           = now.strftime("%Y%b%d%H%M%S")


        # geolocator          = Nominatim(user_agent="geoapiExercises")
        # getlocation         = geolocator.reverse(latitude+","+longitude)
        # getaddress          = getlocation.raw['address']
        # country             = getaddress.get('country', '')
        # state               = getaddress.get('state', '')
        # city                = getaddress.get('city', '')
        # if(not city):
        #     city            = getaddress.get('county', '')
        # pin_code            = getaddress.get('postcode', '')

        # Make the curl request
        response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng="+latitude+","+longitude+"&key=AIzaSyA6sfxAGWorlekK-rkolU152WkN5mzn76A")

        # Parse the JSON response
        location_data = json.loads(response.text)
        # Extract the country, state, and city information
        for result in location_data['results']:
            for component in result['address_components']:
                if "country" in component['types']:
                    country     = component['long_name']
                elif "administrative_area_level_1" in component['types']:
                    state       = component['long_name']
                elif "administrative_area_level_3" in component['types']:
                    city        = component['long_name']
                elif "postal_code" in component['types']:
                    pin_code    = component['long_name']


        shops_tb.objects.all().filter(id=shop_id).update(name=name,vendor_id=vendor_id,category_id=category_id,gst_number=gst_number,address=address,latitude=latitude,location=location,radius=radius,commission=commission,is_featured=is_featured,license_number=license_number,gst_pct=gst_pct,country=country,state=state,city=city,pin_code=pin_code,website_url=website_url,opening_time=opening_time,closing_time=closing_time,phone1=phone1,phone2=phone2,updated_at=now)
        
        if get_featured_image != None:
            featured_image  = uploadImage(get_featured_image,'shop-featured-'+name+'-'+date_time)
            shops_tb.objects.all().filter(id=shop_id).update(image=featured_image,updated_at=now)

            shop_images_tb.objects.all().filter(shop_id=shop_id,is_shop_featured=True).update(image=featured_image,updated_at=now)

        if get_gst_image != None:
            gst_image       = uploadImage(get_gst_image,'shop-gst-'+name+'-'+date_time)
            shops_tb.objects.all().filter(id=shop_id).update(gst_image=gst_image,updated_at=now)

        if get_license_image != None:
            license_image   = uploadImage(get_license_image,'shop-license-'+name+'-'+date_time)
            shops_tb.objects.all().filter(id=shop_id).update(license_image=license_image,updated_at=now)

        if get_banner_image != None:
            banner_image    = uploadImage(get_banner_image,'shop-banner-'+name+'-'+date_time)
            shops_tb.objects.all().filter(id=shop_id).update(banner_image=banner_image,updated_at=now)


        response            =   {
                                    "success"   : True,
                                    "message"   : ""
                                }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def vendorGetAllShops(request):
    data            = json.loads(request.body.decode("utf-8"))
    vendor_id       = data.get('user_id')

    get_all_shop    = shops_tb.objects.all().filter(vendor_id=vendor_id)

    shop_data       = []
    
    for shop in get_all_shop:
        bank_data   = getShopBankData(shop.id)
        shop_data.append({
                'id'            : shop.id,
                'name'          : shop.name,
                'category_id'   : shop.category_id.id,
                'category'      : shop.category_id.name,
                'gst_number'    : shop.gst_number,
                'license_number': shop.license_number,
                'address'       : shop.address,
                'location'      : shop.location,
                'latitude'      : shop.latitude,
                'longitude'     : shop.longitude,
                'radius'        : shop.radius,
                'is_featured'   : shop.is_featured,
                'featured_image': "" if not shop.image else shop.image.url,
                'gst_image'     : "" if not shop.gst_image else shop.gst_image.url,
                'license_image' : "" if not shop.license_image else shop.license_image.url,
                'banner_image'  : "" if not shop.banner_image else shop.banner_image.url,
                'commission'    : shop.commission,
                'wallet_amount' : shop.wallet_amount,
                'status'        : shop.status,
                'gst_pct'       : shop.gst_pct,
                'opening_time'  : "00:00" if not shop.opening_time else shop.opening_time,
                'closing_time'  : "00:00" if not shop.closing_time else shop.closing_time,
                'website_url'   : "" if not shop.website_url else shop.website_url,
                'upi_id'        : shop.upi_id,
                'phone1'        : shop.phone1,
                'phone2'        : shop.phone2,
                'bank_data'     : bank_data
            })

    response        =   {
                            "shop_data"   : shop_data,
                        }


    return JsonResponse(response, status=201)



def getShopBankData(shop_id):
    bank_data       = {}

    get_bank        = bank_tb.objects.all().filter(shop_id=shop_id).exists()

    if get_bank == True:
        get_bank_data   = bank_tb.objects.all().filter(shop_id=shop_id).latest('id')

        bank_data       =   {
                                'bank_id'           : get_bank_data.id,
                                'name'              : get_bank_data.name,
                                'account_number'    : get_bank_data.account_number,
                                'account_type'      : get_bank_data.account_type,
                                'ifsc_code'         : get_bank_data.ifsc_code,
                                'cheque_copy'       : '' if not get_bank_data.cheque_copy else get_bank_data.cheque_copy.url,
                                'shop_id'           : '' if not get_bank_data.shop_id else get_bank_data.shop_id.id,
                                'shop_name'         : '' if not get_bank_data.shop_id else get_bank_data.shop_id.name,
                                'vendor_id'         : get_bank_data.vendor_id.id,
                                'vendor_name'       : get_bank_data.vendor_id.name,
                            }  

    return bank_data


@method_decorator(csrf_exempt, name='dispatch')
def vendorDeleteShop(request):
    data            = json.loads(request.body.decode("utf-8"))
    shop_id         = data.get('shop_id')

    fromReg         = shops_tb.objects.all().filter(id=shop_id)
    fromReg.delete()

    if fromReg.delete():
        response    =   {
                            "success"       : True,
                            "message"       : ""
                        }
    else:
        response    =   {
                            "success"       : False,
                            "message"       : "Something went to wrong"
                        }

    return JsonResponse(response, status=201)



# once vendor approve invoice - then they have enough money , they need to fill wallet. Razor pay is used for payment , in razor pay success call will shop wallet amount and share money to user like invoice approve
@method_decorator(csrf_exempt, name='dispatch')
def vendorInvoicePaymentSuccess(request):
    data                    = json.loads(request.body.decode("utf-8"))

    invoice_id              = data.get('invoice_id')
    amount                  = data.get('amount')
    razorpay_transaction_id = data.get('razorpay_transaction_id')
    razorpay_status         = data.get('razorpay_status')
    payment_type            = "Online"
    transaction_status      = "Completed"
    entry_type              = "Credit"
    wallet_type             = "Direct"
    now                     = datetime.now()


    get_invoice_data        = invoice_data_tb.objects.all().filter(id=invoice_id).get()

    user_id                 = get_invoice_data.user_id
    vendor_id               = get_invoice_data.vendor_id
    shop_id                 = get_invoice_data.shop_id
    bank_id                 = bank_tb.objects.filter(shop_id=shop_id.id).latest('id')

    shop_amount             = float(0 if not shop_id.wallet_amount else shop_id.wallet_amount) + float(amount)

    #insert bank 
    insert_data             = bank_transactions_tb(user_id=user_id,vendor_id=vendor_id,shop_id=shop_id,amount=amount,invoice_id=get_invoice_data,entry_type=entry_type,razorpay_transaction_id=razorpay_transaction_id,bank_id=bank_id,razorpay_status=razorpay_status,payment_type=payment_type,transaction_status=transaction_status,created_at=now,updated_at=now)
    insert_data.save()

    latest_id               = bank_transactions_tb.objects.latest('id')

    #Insert shop wallet amount 
    insert_data             = shop_wallet_transactions_tb(user_id=user_id,vendor_id=vendor_id,shop_id=shop_id,amount=amount,invoice_id=get_invoice_data,entry_type=entry_type,wallet_type=wallet_type,created_at=now,updated_at=now)
    insert_data.save()

    shops_tb.objects.all().filter(id=shop_id.id).update(wallet_amount=shop_amount,updated_at=now)

    response                = updateWalletAmount(invoice_id,latest_id)


    #--- capture razorpay
    capture                 = razorpayCapture(razorpay_transaction_id,amount)
    
    if capture != 'captured':
        response            =   {
                                    "success"       : False,
                                    "message"       : "Something went to wrong"
                                }

    #--- capture

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def vendorUpdatePretaxAmount(request):
    data             = json.loads(request.body.decode("utf-8"))

    invoice_id       = data.get('invoice_id')
    pre_tax_amount   = data.get('pre_tax_amount')
    now              = datetime.now()

    invoice_data_tb.objects.all().filter(id=invoice_id).update(pre_tax_amount=pre_tax_amount,updated_at=now)


    response        =   {
                            "success"       : True,
                            "message"       : ""
                        }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def vendorGetAllShopOffers(request):
    data            = json.loads(request.body.decode("utf-8"))
    shop_id         = data.get('shop_id')

    get_all_offers  = offer_tb.objects.all().filter(shop_id=shop_id)

    offer_data      = []
    
    for offer in get_all_offers:
        offer_data.append({
                'id'            : offer.id,
                'title'         : offer.name,
                'discount'      : offer.discount,
                'description'   : offer.description,
                'image'         : '' if not offer.image else offer.image.url,
                'status'        : offer.status,
            })

    response        =   {
                            "offer_data"   : offer_data,
                        }


    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def vendorAddShopOffers(request):
    data            = json.loads(request.body.decode("utf-8"))

    name                = data.get('name')
    get_shop_id         = data.get('shop_id')
    shop_id             = shops_tb.objects.get(id=get_shop_id)

    discount            = data.get('discount')
    description         = data.get('description')
    offer_image         = data.get('image')

    now                 = datetime.now()
    date_time           = now.strftime("%Y%b%d%H%M%S")

    image               = uploadImage(offer_image,'offer-'+shop_id.name+'-'+name+'-'+date_time)

    insert_data         = offer_tb(name=name,shop_id=shop_id,discount=discount,description=description,image=image,status="Active",created_at=now,updated_at=now)
    insert_data.save()

    latest_id           = shops_tb.objects.latest('id')

    response            =   {
                                "offer_id"      : latest_id.id,
                                "success"       : True,
                                "message"       : ""
                            }


    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def vendorShopOfferDetails(request):
    data                = json.loads(request.body.decode("utf-8"))

    offer_id            = data.get('offer_id')

    get_offer_data      = offer_tb.objects.all().filter(id=offer_id).get()

    offer_data          =   {
                                'id'            : get_offer_data.id,
                                'title'         : get_offer_data.name,
                                'discount'      : get_offer_data.discount,
                                'description'   : get_offer_data.description,
                                'image'         : '' if not get_offer_data.image else get_offer_data.image.url,
                                'status'        : get_offer_data.status,
                            }


    response            =   {
                                "offer_data"    : offer_data,
                            }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def vendorEditShopOffers(request):
    data                = json.loads(request.body.decode("utf-8"))

    offer_id            = data.get('offer_id')
    name                = data.get('name')
    get_shop_id         = data.get('shop_id')
    shop_id             = shops_tb.objects.get(id=get_shop_id)

    discount            = data.get('discount')
    description         = data.get('description')
    offer_image         = data.get('image')

    now                 = datetime.now()
    date_time           = now.strftime("%Y%b%d%H%M%S")

    offer_tb.objects.all().filter(id=offer_id).update(name=name,shop_id=shop_id,discount=discount,description=description,updated_at=now)

    if offer_image:
        image           = uploadImage(offer_image,'offer-'+shop_id.name+'-'+name+'-'+date_time)

        offer_tb.objects.all().filter(id=offer_id).update(image=image,updated_at=now)

    response            =   {
                                "success"       : True,
                                "message"       : ""
                            }


    return JsonResponse(response, status=201)


@method_decorator(csrf_exempt, name='dispatch')
def vendorBankTransfer(request):
    data                = json.loads(request.body.decode("utf-8"))
    shop_id             = data.get('shop_id')
    amount              = data.get('amount')
    now                 = datetime.now()

    get_shop            = shops_tb.objects.all().filter(id=shop_id).get()

    wallet_amount       = get_shop.wallet_amount

    if float(amount) > float(wallet_amount):
        response        =   {
                                "success"       : False,
                                "message"       : "Can't transfer, amount is greater than wallet amount"
                            }

        return JsonResponse(response, status=201)

    get_bank_data       = bank_tb.objects.filter(shop_id=shop_id).latest('id')
    linked_account_id   = get_bank_data.razorpay_id

    get_razor_pay_data  = razor_payx_payout_data_tb.objects.latest('id')

    response            = bankTransfer(get_razor_pay_data.razor_key,get_razor_pay_data.razor_secret,get_razor_pay_data.account_number,linked_account_id,amount)

    if response['status_code'] == 200:
        wallet_amount   = float(wallet_amount) - float(amount)
        shops_tb.objects.all().filter(id=shop_id).update(wallet_amount=wallet_amount,updated_at=now)

        #----- Notification ---- #
        #-- To vendor ---
        device_token    = get_shop.vendor_id.device_token
        title           = 'Transferred successfully'
        body            = str(amount) +' successfully transferred to your '+get_bank_data.name+' account'
        sendNotificationToUser(device_token,title,body)

        insert_data     = vendor_notification_tb(vendor_id=get_shop.vendor_id,title=title,description=body,created_at=now,updated_at=now)
        insert_data.save()
        #----------------------

    return JsonResponse(response, status=201)



def bankTransfer(razor_key,razor_secret,account_number,linked_account_id,amount):
    # Define your Razorpay Key ID and Secret
    key_id      = razor_key
    key_secret  = razor_secret

    amount      = float(amount) * 100

    # Define the endpoint for creating a transfer
    url = "https://api.razorpay.com/v1/payouts"

    # Define the data for the transfer request
    data = {
        "account_number": account_number,
        "fund_account_id": linked_account_id,
        "amount": amount,
        "currency": "INR",
        "currency": "INR",
        "mode": "IMPS",
        "purpose": "refund",
        "queue_if_low_balance": True,
        # "reference_id": "Acme Transaction ID 12345",
        # "narration": "Acme Corp Fund Transfer",
        "notes": {
            "Note": "Transfer amount"
        }
    }

    # Make the request to create a transfer
    response = requests.post(url, auth=(key_id, key_secret), json=data)

    # Check the status code of the response
    if response.status_code == 200:
        # Parse the JSON response data
        transfer_data = response.json()

        # Get the transfer ID
        transfer_id = transfer_data["id"]

        # Print the transfer data
        # print(transfer_data)
        response    =   {
                            "success"       : True,
                            "message"       : "",
                            "status_code"   : response.status_code,
                            "transfer_id"   : transfer_id
                        } 
    else:
        # Print the error message
        print(f"Failed to create transfer: {response.text}")
        response    =   {
                            "success"       : False,
                            "message"       : "Failed to create transfer",
                            "status_code"   : response.status_code
                        } 

    return response



def sendNotificationToUser(device_token,title,body):
    server_key  = "AAAAPgZgMIg:APA91bFZgYPmKrTDJ_sdvvU3ZfGHwaa8PHup6t3clMtF39OCMXedG0KG_9jGH6Mc7kkhgvsYIOL1s0hWC-7b6p8sdsKxn65RIAFfXB1cLar9bG8Sv1abCMy0RkCcTXAA0jiaVa36DOs9"
    # Set the FCM endpoint URL and your server key
    url = 'https://fcm.googleapis.com/fcm/send'

    # Set the FCM notification payload as a dictionary
    payload = {
        'to': device_token,
        'notification': {
            'title': title,
            'body': body
        }
    }

    # Set the headers with the server key and content type
    headers = {
        'Authorization': 'key=' + server_key,
        'Content-Type': 'application/json'
    }

    # Send the notification using the requests library
    response = requests.post(url, json=payload, headers=headers)

    # Print the response from FCM
    print(response.text)
    return



@method_decorator(csrf_exempt, name='dispatch')
def vendorUpdateDeviceToken(request):
    data            = json.loads(request.body.decode("utf-8"))

    user_id         = data.get('user_id')
    device_token    = data.get('device_token')
    now             = datetime.now()

    vendors_tb.objects.all().filter(id=user_id).update(device_token=device_token,updated_at=now)


    response        =   {
                            "success"       : True,
                            "message"       : ""
                        }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def vendorRequestCoin(request):
    data            = json.loads(request.body.decode("utf-8"))

    get_user_id     = data.get('user_id')
    get_shop_id     = data.get('shop_id')
    amount          = data.get('amount')
    now             = datetime.now()
    shop_id         = shops_tb.objects.get(id=get_shop_id)
    user_id         = user_data_tb.objects.get(id=get_user_id)

    insert_data     = vendor_request_coin(shop_id=shop_id,user_id=user_id,amount=amount,created_at=now,updated_at=now)
    insert_data.save()

    insert_data     = request_pay_history(shop_id=shop_id,user_id=user_id,amount=amount,is_request=True,created_at=now,updated_at=now)
    insert_data.save()

    #------ notification -----#
    #--- To User ---#
    device_token    = user_id.device_token
    title           = 'New request'
    body            = 'You received a request from '+shop_id.name +' shop for wallet transaction'
    sendNotificationToUser(device_token,title,body)

    insert_data     = user_notification_tb(user_id=user_id,title=title,description=body,created_at=now,updated_at=now)
    insert_data.save()
    #------ notification -----#

    response        =   {
                            "success"       : True,
                            "message"       : ""
                        }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def vendorForgotPassword(request):
    data            = json.loads(request.body.decode("utf-8"))

    user_id         = data.get('user_id')
    now             = datetime.now()

    get_user        = vendors_tb.objects.all().filter(id=user_id).get()
    email           = get_user.email

    digits          = '1234567890'
    pin             = ''.join(random.choice(digits) for i in range(4))

    url             = request.build_absolute_uri('/update-vendor-password/?id='+str(pin))
    vendors_tb.objects.all().filter(id=user_id).update(pin=pin,updated_at=now)
    
    sendEmailRestPin(email,'email/reset_vendor_password.html',url)
    
    response        =   {
                            "success"   : True,
                            "message"   : "",
                        }
    return JsonResponse(response, status=201)



@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def vendorResetPassword(request):
    if request.method=="POST":
        user_id         = request.POST['id']
        password        = request.POST['password']
        now             = datetime.now()

        hash_password   = make_password(password)

        vendors_tb.objects.all().filter(pin=user_id).update(password=hash_password,pin=None,updated_at=now)
        
        messages.success(request, 'Changes successfully updated.')
        return redirect('thank-you')
    else:
        user_id     = request.GET['id']
        return render(request,'admin/edit_vendor_password.html',{'user_id' : user_id})
    


@method_decorator(csrf_exempt, name='dispatch')
def deleteAllVendorNotification(request):
    data        = json.loads(request.body.decode("utf-8"))

    user_id     = data.get('user_id')

    fromReg     = vendor_notification_tb.objects.all().filter(vendor_id=user_id)
    fromReg.delete()
    if fromReg.delete():
        response=   {
                        "success"   : True,
                        "message"   : "",
                    }
    else:
        response=   {
                        "success"   : False,
                        "message"   : "Something went to wrong",
                    }
    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def vendorUpdateInvoicePretaxAmount(request):
    data            = json.loads(request.body.decode("utf-8"))

    invoice_id      = data.get('invoice_id')
    pretax_amount   = data.get('pretax_amount')
    invoice_number  = data.get('invoice_number')
    invoice_date    = data.get('invoice_date')
    now             = datetime.now()

    invoice_data_tb.objects.all().filter(id=invoice_id).update(pre_tax_amount=pretax_amount,invoice_number=invoice_number,invoice_date=invoice_date,updated_at=now)


    response        =   {
                            "success"       : True,
                            "message"       : ""
                        }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def vendorAddSupportRequest(request):
    data                = json.loads(request.body.decode("utf-8"))

    title               = data.get('title')
    description         = data.get('description')
    get_vendor_id       = data.get('user_id')
    vendor_id           = vendors_tb.objects.get(id=get_vendor_id)
    now                 = datetime.now()
   
    insert_data         = vendor_support_request_tb(title=title,description=description,vendor_id=vendor_id,created_at=now,updated_at=now)
    insert_data.save()

    response            =   {
                                "id"        : insert_data.id,
                                "success"   : True,
                                "message"   : ""
                            }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def vendorListSupportRequest(request):
    data                = json.loads(request.body.decode("utf-8"))

    user_id             = data.get('user_id')
    get_support_data    = vendor_support_request_tb.objects.filter(vendor_id=user_id)

    #-- Pagination
    paginator           = Paginator(get_support_data, per_page=20)
    page_number         = data.get('page')
    page                = paginator.get_page(page_number)
    # Get the total number of pages
    total_pages         = paginator.num_pages
    #-- Pagination

    support_data        = []
    for data in page:
        support_data.append({
                    'id'            : data.id,
                    'user_id'       : data.vendor_id.id,
                    'title'         : data.title,
                    'description'   : data.description,
                    'status'        : data.status
                }) 

    response                =   {
                                    "support_data"      : support_data,
                                    "total_pages"       : total_pages
                                }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def shopDueTransactionsList(request):
    data                        = json.loads(request.body.decode("utf-8"))

    shop_id                     = data.get('shop_id')
    entry_type                  = data.get('entry_type')

    get_transaction_data        = user_transactions_tb.objects.all().filter(shop_id=shop_id,wallet_type='Shop Due Amount').order_by('-id')
    
    shop_data                   = shops_tb.objects.all().filter(id=shop_id).get()

    #-- Pagination
    paginator                   = Paginator(get_transaction_data, per_page=10)
    page_number                 = data.get('page')
    page                        = paginator.get_page(page_number)
    total_pages                 = paginator.num_pages
    #-- Pagination

    transaction_data        = []
    for transaction in page:
        transaction_data.append({
                    'id'                    : transaction.id,
                    'user_id'               : transaction.vendor_id.id,
                    'shop_id'               : transaction.shop_id.id,
                    'invoice_number'        : None if not transaction.invoice_id else transaction.invoice_id.invoice_number,
                    'amount'                : transaction.amount,
                    'wallet_type'           : transaction.wallet_type,
                    'entry_type'            : transaction.entry_type,
                    'remark'                : transaction.remark,
                    'status'                : transaction.status,
                    'created_at'            : transaction.created_at.strftime("%Y %b %d, %I:%M %p")
                }) 

    response        =   {
                            "shop_wallet_amount": round(float(0 if not shop_data.balance_amount else shop_data.balance_amount),2),
                            "transaction_data"  : transaction_data,
                            "page"              : page_number,
                            "total_pages"       : total_pages
                        }

    return JsonResponse(response, status=201)






@method_decorator(csrf_exempt, name='dispatch')
def vendorWithdrawAmount(request):
    data            = json.loads(request.body.decode("utf-8"))

    shop_id         = data.get('shop_id')
    now             = datetime.now()

    get_user        = shops_tb.objects.all().filter(id=shop_id).get()
    email           = get_user.vendor_id.email

    digits          = '1234567890'
    pin             = ''.join(random.choice(digits) for i in range(4))

    url             = request.build_absolute_uri('/withdraw-amount/?id='+str(pin))
    shops_tb.objects.all().filter(id=shop_id).update(pin=pin,updated_at=now)
    
    sendEmailRestPin(email,'email/withdraw_amount.html',url)
    
    response        =   {
                            "success"   : True,
                            "message"   : "",
                        }
    return JsonResponse(response, status=201)



#Bank transfer through mobile app
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def vendorWithdrawShopWalletAmount(request):
    if request.method=="POST":
        shop_id         = request.POST['id']
        amount          = request.POST['amount']
        now             = datetime.now()

        get_shop        = shops_tb.objects.all().filter(id=shop_id).get()

        shop_wallet_amount  = float(0 if not get_shop.wallet_amount else get_shop.wallet_amount)

        balance_amount      = shop_wallet_amount - float(0 if not get_shop.balance_amount else get_shop.balance_amount)

        if amount > balance_amount:
            response    =   {
                                "success"       : False,
                                "message"       : "Can't transfer, amount is greater than wallet amount"
                            }

            messages.error(request, response['message'])
            return redirect('withdraw-amount')

        get_bank_data       = bank_tb.objects.filter(shop_id=shop_id).latest('id')
        linked_account_id   = get_bank_data.razorpay_id

        get_razor_pay_data  = razor_payx_payout_data_tb.objects.latest('id')

        response            = bankTransfer(get_razor_pay_data.razor_key,get_razor_pay_data.razor_secret,get_razor_pay_data.account_number,linked_account_id,amount)
        
        if response['status_code'] == 200:
            balance_amount  = float(shop_wallet_amount) - float(amount)
            shops_tb.objects.all().filter(id=shop_id).update(wallet_amount=balance_amount,updated_at=now)

            #----- Notification ---- #
            #-- To vendor ---
            device_token    = get_shop.vendor_id.device_token
            title           = 'Transferred successfully'
            body            = str(amount) +' successfully transferred to your '+get_bank_data.name+' account'
            sendNotificationToUser(device_token,title,body)

            insert_data     = vendor_notification_tb(vendor_id=get_shop.vendor_id,title=title,description=body,created_at=now,updated_at=now)
            insert_data.save()
            #----------------------

            shops_tb.objects.all().filter(id=shop_id).update(pin=None,updated_at=now)

            messages.success(request, 'Settled successfully.')
        else:
            messages.error(request, response['message'])
        return redirect('thankyou-withdraw-amount')
    else:
        pin             = request.GET['id']
        shop_data       = shops_tb.objects.all().filter(pin=pin).get()

        return render(request,'user/shop_withdrawal.html',{'shop_data' : shop_data})
    

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def thankYouWithdraw(request):
    return render(request,'user/thank_you_withdraw.html')


###########################-------- MOBILE USER --------##################################################################

@method_decorator(csrf_exempt, name='dispatch')
def userLogin(request):
    data        = json.loads(request.body.decode("utf-8"))

    phone       = data.get('phone')
    digits      = '1234567890'

    otp         = ''.join(random.choice(digits) for i in range(4))

    if(phone == '9061280048'):
        otp     = '1234'

    send_otp_sms(phone, otp)

    response    =   {
                        "phone"     : phone,
                        "otp"       : otp,
                    }

    return JsonResponse(response, status=201)



def send_otp_sms(phone_number, otp):
    api_key = "9e880f4a-7dc5-11ec-b9b5-0200cd936042"
    curl_command = "curl https://2factor.in/API/V1/"+api_key+"/SMS/"+phone_number+"/"+otp
    process = subprocess.Popen(curl_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    # print(output.decode("utf-8"))
    return


@method_decorator(csrf_exempt, name='dispatch')
def otpVerification(request):
    data        = json.loads(request.body.decode("utf-8"))

    phone       = data.get('phone')

    user        = user_data_tb.objects.all().filter(phone=phone)
    now         = datetime.now()

    if user:
        for x in user:
            response    =   {
                                "user_id"       : x.id,
                                "is_active"     : bool(x.active),
                                "have_mail"     : True if x.email else False,
                                "have_pin"      : True if x.user_pin else False,
                                "have_locaton"  : True if x.location else False,
                                "user_role"     : x.user_role_id.role if x.user_role_id else None,
                                "success"       : True,
                                "message"       : ""
                            }
    else:
        insert_data     = user_data_tb(phone=phone,active=True,created_at=now,updated_at=now)
        insert_data.save()

        latest_id       = user_data_tb.objects.latest('id')

        get_all_data    = user_data_tb.objects.count()

        if get_all_data != 1:
            get_default_parent_id   = default_data_tb.objects.filter(title='user_default_parent_id').get()
            default_parent_id       = get_default_parent_id.value

            get_user_data           = user_data_tb.objects.filter(parent_id=default_parent_id).count()

            if get_user_data < 2:
                get_parent_id       = user_data_tb.objects.get(id=default_parent_id)
                user_data_tb.objects.all().filter(id=latest_id.id).update(parent_id=get_parent_id,updated_at=now)
                
            else:
                default_parent_id   = int(get_default_parent_id.value) + (1)
                get_parent_id       = user_data_tb.objects.get(id=default_parent_id)
                user_data_tb.objects.all().filter(id=latest_id.id).update(parent_id=get_parent_id,updated_at=now)
        else:
            default_parent_id       = latest_id.id

        #update current default parent id
        default_data_tb.objects.all().filter(title='user_default_parent_id').update(value=default_parent_id,updated_at=now)

        response        =   {
                                "user_id"       : latest_id.id,
                                "is_active"     : bool(latest_id.active),
                                "have_mail"     : True if latest_id.email else False,
                                "have_pin"      : True if latest_id.user_pin else False,
                                "have_locaton"  : True if latest_id.location else False,
                                "user_role"     : x.user_role_id.role if x.user_role_id else None,
                                "success"       : True,
                                "message"       : ""
                            }

    return JsonResponse(response, status=201)


@method_decorator(csrf_exempt, name='dispatch')
def userUpdateEmailAndPin(request):
    data            = json.loads(request.body.decode("utf-8"))

    user_id         = data.get('user_id')
    name            = data.get('name')
    # email           = data.get('email')
    pin             = data.get('pin')
    now             = datetime.now()

    # get_user        = user_data_tb.objects.all().filter(email=email).exclude(id=user_id)

    # if get_user:
    #     response    =   {
    #                         "success"   : False,
    #                         "message"   : "Email already exist",
    #                     }
    # else:
    user_data_tb.objects.all().filter(id=user_id).update(name=name,user_pin=pin,updated_at=now)

    response    =   {
                        "success"   : True,
                        "message"   : "",
                    }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def resetUserPinNumber(request):
    data            = json.loads(request.body.decode("utf-8"))

    user_id         = data.get('user_id')

    get_user        = user_data_tb.objects.all().filter(id=user_id).get()
    email           = get_user.email

    url             = request.build_absolute_uri('/update-user-pin/?id='+str(user_id))

    sendEmailRestPin(email,'email/reset_user_pin.html',url)
    
    response        =   {
                            "success"   : True,
                            "message"   : "",
                        }
    return JsonResponse(response, status=201)


def sendEmailRestPin(email,template,url):
    html_template   = template
    html_message    = render_to_string(html_template,  {'url': url})
    subject         = 'Welcome to WonderApp'
    email_from      = settings.EMAIL_HOST_USER
    recipient_list  = [email]
    message         = EmailMessage(subject, html_message, email_from, recipient_list)
    message.content_subtype = 'html'
    message.send()
    return



@method_decorator(csrf_exempt, name='dispatch')
def getUserWalletDetails(request):
    data                        = json.loads(request.body.decode("utf-8"))

    user_id                     = data.get('user_id')
    now                         = datetime.now()

    get_wallet_data             = getUserWalletAmount(user_id,now)

    get_all_rewards             = wallet_transactions_tb.objects.all().filter(user_id=user_id,entry_type="Credit").order_by('-id')
    rewards_list                = []

    for reward in get_all_rewards:
        rewards_list.append({
                'id'            : reward.id,
                'amount'        : reward.amount,
                'shop_id'       : reward.shop_id.id,
                'shop_name'     : reward.shop_id.name,
                'wallet_type'   : reward.wallet_type,
                'expiry_date'   : reward.expiry_date.strftime("%Y %b %d"),
                'status'        : reward.status,
                'created_at'    : reward.created_at.strftime("%Y %b %d, %I:%M %p") 
            })

    get_all_transactions        = wallet_transactions_tb.objects.all().filter(user_id=user_id).order_by('-id')
    transaction_list            = []

    for transaction in get_all_transactions:
        transaction_list.append({
                'id'            : transaction.id,
                'amount'        : transaction.amount,
                'shop_id'       : transaction.shop_id.id,
                'shop_name'     : transaction.shop_id.name,
                'entry_type'    : transaction.entry_type,
                'wallet_type'   : transaction.wallet_type,
                'expiry_date'   : reward.expiry_date.strftime("%Y %b %d"),
                'status'        : transaction.status,
                'created_at'    : transaction.created_at.strftime("%Y %b %d, %I:%M %p") 
            })
    
    response                    =   {
                                    "total_balance"     : get_wallet_data['total_balance'],
                                    "redeemable_points" : get_wallet_data['redeemable_points'],
                                    "expired_points"    : get_wallet_data['expired_points'],
                                    "rewards"           : rewards_list,
                                    "transactions"      : transaction_list
                                }

    return JsonResponse(response, status=201)



def getUserWalletAmount(user_id,now):
    get_user_data                   = user_data_tb.objects.all().filter(id=user_id).get()
    user_wallet_debit               = 0
    user_wallet_debit_expired       = 0

    total_user_wallet_amount        = 0 if wallet_transactions_tb.objects.all().filter(user_id=user_id,entry_type="Credit",status="Approve").values('user_id').exists() == False else wallet_transactions_tb.objects.all().filter(user_id=user_id,entry_type="Credit",status="Approve").values('user_id').annotate(total_amount=Sum('amount')).distinct().get()
    total_balance                   = round(0 if total_user_wallet_amount == 0 else total_user_wallet_amount['total_amount'])
    
    #can redeem
    user_wallet_credit              = 0 if wallet_transactions_tb.objects.all().filter(expiry_date__gte=now,user_id=user_id,entry_type="Credit",status="Approve").values('user_id').exists() == False else wallet_transactions_tb.objects.all().filter(expiry_date__gte=now,user_id=user_id,entry_type="Credit",status="Approve").values('user_id').annotate(total_amount=Sum('amount')).distinct().get()
    user_wallet_credit              = round(0 if user_wallet_credit == 0 else user_wallet_credit['total_amount'])
    
    if user_wallet_credit != 0:
        min_date_credit             = wallet_transactions_tb.objects.all().filter(expiry_date__gte=now,user_id=user_id,entry_type="Credit",status="Approve").aggregate(Min('expiry_date'))['expiry_date__min']
        min_date_create             = wallet_transactions_tb.objects.all().filter(expiry_date=min_date_credit).first()
        min_date_credit             = min_date_create.created_at
        
        get_debit_data              = 0 if wallet_transactions_tb.objects.all().filter(user_id=user_id,created_at__gte=min_date_credit,entry_type="Debit",status="Approve").values('user_id').exists() == False else wallet_transactions_tb.objects.all().filter(created_at__gte=min_date_credit,entry_type="Debit",status="Approve",user_id=user_id).values('user_id').annotate(total_amount=Sum('amount')).distinct().get()
        
        user_wallet_debit           = round(0 if get_debit_data == 0 else get_debit_data['total_amount'])
        
    redeemable_points               = user_wallet_credit - user_wallet_debit
    #can redeem


    #expired
    user_wallet_credit_expired      = 0 if wallet_transactions_tb.objects.all().filter(expiry_date__lt=now,user_id=user_id,entry_type="Credit",status="Approve").values('user_id').exists() == False else wallet_transactions_tb.objects.all().filter(expiry_date__lt=now,user_id=user_id,entry_type="Credit",status="Approve").values('user_id').annotate(total_amount=Sum('amount')).distinct().get()
    user_wallet_credit_expired      = round(0 if user_wallet_credit_expired == 0 else user_wallet_credit_expired['total_amount'])

    if user_wallet_credit_expired != 0:
        # get_expired_data            = 0 if wallet_transactions_tb.objects.all().filter(created_at__lt=min_date_credit,entry_type="Debit",status="Approve",user_id=user_id).values('user_id').exists() == False else wallet_transactions_tb.objects.all().filter(created_at__lt=min_date_credit,entry_type="Debit",status="Approve").values('user_id').annotate(total_amount=Sum('amount')).distinct().get()
        get_expired_data            = 0 if wallet_transactions_tb.objects.all().filter(created_at__lt=min_date_credit, entry_type="Debit", status="Approve", user_id=user_id).exists() == False else wallet_transactions_tb.objects.all().filter(created_at__lt=min_date_credit, entry_type="Debit", status="Approve", user_id=user_id).values('user_id').annotate(total_amount=Sum('amount')).distinct().get()

        user_wallet_debit_expired   = round(0 if get_expired_data == 0 else get_expired_data['total_amount'])

    expired_points                  = user_wallet_credit_expired - user_wallet_debit_expired
    #expired
    

    response                        =   {
                                            "total_balance"     : total_balance,
                                            "redeemable_points" : redeemable_points,
                                            "expired_points"    : expired_points,
                                            "redeemed_points"   : user_wallet_debit
                                        }

    return response


# @method_decorator(csrf_exempt, name='dispatch')
# def userPayAmountForShop(request):
#     data                            = json.loads(request.body.decode("utf-8"))

#     user_id                         = data.get('user_id')
#     amount                          = data.get('amount')
#     pin                             = data.get('pin')
#     request_id                      = data.get('request_id')# for vendor request coin and user accept

#     upi_id                          = data.get('upi_id')
#     get_shop_data                   = shops_tb.objects.filter(upi_id=upi_id).get()
#     shop_id                         = get_shop_data.id

#     if shops_tb.objects.filter(id=shop_id).exists():
#         check_exist                 = user_data_tb.objects.all().filter(id=user_id,user_pin=pin).exists()

#         if check_exist == False:
#             response                = {
#                                         "success"       : False,
#                                         "message"       : "Incorrect pin",
#                                     } 

#             return JsonResponse(response, status=201)

#         wallet_type                 = 'Direct'
#         now                         = datetime.now()
#         get_expiry_date             = wallet_transactions_tb.objects.all().filter(user_id=user_id,entry_type="Credit",status="Approve").aggregate(Max('expiry_date'))
#         expiry_date                 = get_expiry_date['expiry_date__max']

#         get_user_data               = user_data_tb.objects.all().filter(id=user_id).get()
#         get_shop_data               = shops_tb.objects.get(id=shop_id)
#         get_vendor_id               = get_shop_data.vendor_id
#         get_shop_balance            = get_shop_data.balance_amount

#         user_wallet_data            = getUserWalletAmount(user_id,now)

#         redeemable_points           = user_wallet_data['redeemable_points']
        
#         if float(amount) > float(redeemable_points):
#             response                =   {
#                                             "success"       : False,
#                                             "message"       : "No sufficient balance",
#                                         } 

#             return JsonResponse(response, status=201)
#         else: 
#             user_total_amount       = float(get_user_data.wallet_amount) - float(amount)

#             user_wallet_amount      = float(redeemable_points) - float(amount)
#             shop_wallet_amount      = 0  if not get_shop_data.wallet_amount else float(get_shop_data.wallet_amount)
#             shop_wallet_amount      = shop_wallet_amount + float(amount)

#             # Update user wallet amount
#             user_data_tb.objects.all().filter(id=user_id).update(wallet_amount=user_total_amount,updated_at=now)


#             # Update shop wallet amount
#             shops_tb.objects.all().filter(id=shop_id).update(wallet_amount=shop_wallet_amount,updated_at=now)

#             # Create new entry user wallet transaction tb
#             insert_data = wallet_transactions_tb(user_id=get_user_data,vendor_id=get_vendor_id,shop_id=get_shop_data,amount=amount,entry_type="Debit",wallet_type=wallet_type,expiry_date=expiry_date,status="Approve",created_at=now,updated_at=now)
#             insert_data.save()

#             # Create new entry shop wallet transaction tb
#             insert_data = shop_wallet_transactions_tb(user_id=get_user_data,vendor_id=get_vendor_id,shop_id=get_shop_data,amount=amount,entry_type="Credit",wallet_type=wallet_type,created_at=now,updated_at=now)
#             insert_data.save()


#             # for vendor request coin and user accept
#             if request_id:
#                 vendor_request_coin.objects.all().filter(id=request_id).update(status='Paid',updated_at=now)
#             #user transfer amount for shop create history all time    
#             insert_data = request_pay_history(shop_id=get_shop_data,user_id=get_user_data,amount=amount,status='Paid',created_at=now,updated_at=now)
#             insert_data.save()


#             #-------- Notification -------#
#             #---- To User ---#
#             device_token    = get_user_data.device_token
#             title           = 'Debited'
#             body            = str(amount)+' points is debited from your wallet'
#             sendNotificationToUser(device_token,title,body)

#             insert_data     = user_notification_tb(user_id=get_user_data,title=title,description=body,created_at=now,updated_at=now)
#             insert_data.save()

#             #---- To Vendor ---#
#             device_token    = get_shop_data.vendor_id.device_token
#             title           = 'Congratulations'
#             body            = 'Your wallet is credited with '+str(amount)+' points'
#             sendNotificationToUser(device_token,title,body)

#             insert_data     = vendor_notification_tb(vendor_id=get_shop_data.vendor_id,title=title,description=body,created_at=now,updated_at=now)
#             insert_data.save()
#             #------


#             response        =   {
#                                     "success"       : True,
#                                     "message"       : "",
#                                 } 
#     else:
#         response            =   {
#                                     "success"       : False,
#                                     "message"       : "Shop not exist",
#                                 } 

#     return JsonResponse(response, status=201)


@method_decorator(csrf_exempt, name='dispatch')
def userPayAmountForShop(request):
    data                            = json.loads(request.body.decode("utf-8"))

    user_id                         = data.get('user_id')
    amount                          = float(data.get('amount'))
    pin                             = data.get('pin')
    request_id                      = data.get('request_id')# for vendor request coin and user accept

    upi_id                          = data.get('upi_id')
    get_shop_data                   = shops_tb.objects.filter(upi_id=upi_id).get()
    shop_id                         = get_shop_data.id

    if shops_tb.objects.filter(id=shop_id).exists():
        check_exist                 = user_data_tb.objects.all().filter(id=user_id,user_pin=pin).exists()

        if check_exist == False:
            response                = {
                                        "success"       : False,
                                        "message"       : "Incorrect pin",
                                    } 

            return JsonResponse(response, status=201)

        wallet_type                 = 'Direct'
        now                         = datetime.now()
        get_expiry_date             = wallet_transactions_tb.objects.all().filter(user_id=user_id,entry_type="Credit",status="Approve").aggregate(Max('expiry_date'))
        expiry_date                 = get_expiry_date['expiry_date__max']

        get_user_data               = user_data_tb.objects.all().filter(id=user_id).get()
        get_shop_data               = shops_tb.objects.get(id=shop_id)
        get_vendor_id               = get_shop_data.vendor_id
        get_shop_balance            = float(get_shop_data.balance_amount)

        user_wallet_data            = getUserWalletAmount(user_id,now)

        redeemable_points           = user_wallet_data['redeemable_points']
        
        if float(amount) > float(redeemable_points):
            response                =   {
                                            "success"       : False,
                                            "message"       : "No sufficient balance",
                                        } 

            return JsonResponse(response, status=201)
        else: 
            user_total_amount       = float(get_user_data.wallet_amount) - float(amount)

            user_wallet_amount      = float(redeemable_points) - float(amount)
            shop_wallet_amount      = 0  if not get_shop_data.wallet_amount else float(get_shop_data.wallet_amount)

            get_shop_balance        = (0 if not get_shop_balance else float(get_shop_balance))

            if get_shop_balance > float(amount) or get_shop_balance >= float(amount):
                get_shop_balance    = get_shop_balance - amount

                insert_data         = user_transactions_tb(vendor_id=get_shop_data.vendor_id,shop_id=get_shop_data,amount=amount,entry_type="Debit",wallet_type='Shop Due Amount',created_at=now,updated_at=now)
                insert_data.save() 

                insert_data         = shop_wallet_transactions_tb(user_id=get_user_data,vendor_id=get_vendor_id,shop_id=get_shop_data,amount=amount,entry_type="Credit",wallet_type=wallet_type,remark="Adjust with due entry",created_at=now,updated_at=now)
                insert_data.save()
            else:
                shop_wallet_amount  = shop_wallet_amount + float(amount)

                insert_data         = shop_wallet_transactions_tb(user_id=get_user_data,vendor_id=get_vendor_id,shop_id=get_shop_data,amount=amount,entry_type="Credit",wallet_type=wallet_type,created_at=now,updated_at=now)
                insert_data.save()


            # Update user wallet amount
            user_data_tb.objects.all().filter(id=user_id).update(wallet_amount=user_total_amount,updated_at=now)


            # Update shop wallet amount
            shops_tb.objects.all().filter(id=shop_id).update(wallet_amount=shop_wallet_amount,balance_amount=get_shop_balance,updated_at=now)

            # Create new entry user wallet transaction tb
            insert_data = wallet_transactions_tb(user_id=get_user_data,vendor_id=get_vendor_id,shop_id=get_shop_data,amount=amount,entry_type="Debit",wallet_type=wallet_type,expiry_date=expiry_date,status="Approve",created_at=now,updated_at=now)
            insert_data.save()

            # # Create new entry shop wallet transaction tb
            # insert_data = shop_wallet_transactions_tb(user_id=get_user_data,vendor_id=get_vendor_id,shop_id=get_shop_data,amount=amount,entry_type="Credit",wallet_type=wallet_type,created_at=now,updated_at=now)
            # insert_data.save()


            # for vendor request coin and user accept
            if request_id:
                vendor_request_coin.objects.all().filter(id=request_id).update(status='Paid',updated_at=now)
            #user transfer amount for shop create history all time    
            insert_data = request_pay_history(shop_id=get_shop_data,user_id=get_user_data,amount=amount,status='Paid',created_at=now,updated_at=now)
            insert_data.save()


            #-------- Notification -------#
            #---- To User ---#
            device_token    = get_user_data.device_token
            title           = 'Debited'
            body            = str(amount)+' points is debited from your wallet'
            sendNotificationToUser(device_token,title,body)

            insert_data     = user_notification_tb(user_id=get_user_data,title=title,description=body,created_at=now,updated_at=now)
            insert_data.save()

            #---- To Vendor ---#
            device_token    = get_shop_data.vendor_id.device_token
            title           = 'Congratulations'
            body            = 'Your wallet is credited with '+str(amount)+' points'
            sendNotificationToUser(device_token,title,body)

            insert_data     = vendor_notification_tb(vendor_id=get_shop_data.vendor_id,title=title,description=body,created_at=now,updated_at=now)
            insert_data.save()
            #------


            response        =   {
                                    "success"       : True,
                                    "message"       : "",
                                } 
    else:
        response            =   {
                                    "success"       : False,
                                    "message"       : "Shop not exist",
                                } 

    return JsonResponse(response, status=201)


@method_decorator(csrf_exempt, name='dispatch')
def userCheckPin(request):
    data            = json.loads(request.body.decode("utf-8"))

    user_id         = data.get('user_id')
    pin             = data.get('pin')

    check_exist     = user_data_tb.objects.all().filter(id=user_id,user_pin=pin).exists()

    if check_exist == True:
        response    =   {
                            "success"       : True,
                            "message"       : "",
                        } 
    else:
        response    =   {
                            "success"       : False,
                            "message"       : "Incorrect pin",
                        } 

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def userAddLocation(request):
    data            = json.loads(request.body.decode("utf-8"))

    user_id         = data.get('user_id')
    latitude        = data.get('latitude')
    longitude       = data.get('longitude')
    location        = data.get('location')
    now             = datetime.now()

    # geolocator      = Nominatim(user_agent="geoapiExercises")
    # getlocation     = geolocator.reverse(latitude+","+longitude)

    # address         = getlocation.raw['address']
    # country         = address.get('country', '')
    # state           = address.get('state', '')
    # city            = address.get('city', '')
    # if(not city):
    #     city        = address.get('county', '')
    # pin_code        = address.get('postcode', '')

    # Make the curl request
    response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng="+latitude+","+longitude+"&key=AIzaSyA6sfxAGWorlekK-rkolU152WkN5mzn76A")

    # Parse the JSON response
    location_data = json.loads(response.text)
    # Extract the country, state, and city information
    for result in location_data['results']:
        for component in result['address_components']:
            if "country" in component['types']:
                country     = component['long_name']
            elif "administrative_area_level_1" in component['types']:
                state       = component['long_name']
            elif "administrative_area_level_3" in component['types']:
                city        = component['long_name']
            elif "postal_code" in component['types']:
                pin_code    = component['long_name']

    user_data_tb.objects.all().filter(id=user_id).update(latitude=latitude,longitude=longitude,location=location,country=country,state=state,city=city,pin_code=pin_code,updated_at=now)


    response        =   {
                            "success"       : True,
                            "message"       : "",
                        } 

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def userHomeScreen(request):
    data                = json.loads(request.body.decode("utf-8"))
    user_id             = data.get('user_id')
    now                 = datetime.now()

    get_user_data       = user_data_tb.objects.all().filter(id=user_id).get()

    user_lat            = get_user_data.latitude
    user_long           = get_user_data.longitude

    get_wallet_data     = getUserWalletAmount(user_id,now)

    featured_shop       = shops_tb.objects.all().filter(is_featured=True,status='Active')
    featured_data       = []

    near_by_shop        = shops_tb.objects.all().filter(status='Active')
    near_by_shop_list   = []

    all_categories      = category_tb.objects.all()
    all_category_list   = []

    # nearby shop
    for shop in near_by_shop:
        shop_lat        = shop.latitude
        shop_long       = shop.longitude
        radius          = shop.radius

        coords_1        = (user_lat, user_long)
        coords_2        = (shop_lat, shop_long)
        distance        = geopy.distance.geodesic(coords_1, coords_2).km

        if float(radius) >= float(distance):
            near_by_shop_list.append({
                    'id'            : shop.id,
                    'shop_name'     : shop.name,
                    'featured_image': "" if not shop.image else shop.image.url,
                    'category_id'   : shop.category_id.id,
                    'category'      : shop.category_id.name, 
                    'gst_number'    : shop.gst_number,
                    'license_number': shop.license_number,
                    'address'       : shop.address,
                    'location'      : shop.location,
                    'latitude'      : shop.latitude,
                    'longitude'     : shop.longitude,
                    'radius'        : shop.radius,
                    'is_featured'   : shop.is_featured,
                    'gst_image'     : "" if not shop.gst_image else shop.gst_image.url,
                    'license_image' : "" if not shop.license_image else shop.license_image.url,
                    'banner_image'  : "" if not shop.banner_image else shop.banner_image.url,
                    'commission'    : shop.commission,
                    'wallet_amount' : shop.wallet_amount,
                    'status'        : shop.status,
                    'gst_pct'       : shop.gst_pct,
                    'opening_time'  : "00:00" if not shop.opening_time else shop.opening_time,
                    'closing_time'  : "00:00" if not shop.closing_time else shop.closing_time,
                    'website_url'   : "" if not shop.website_url else shop.website_url,
                    'upi_id'        : shop.upi_id,
                    'phone1'        : shop.phone1,
                    'phone2'        : shop.phone2,
                })


    # featured shop
    for shop in featured_shop:
        featured_data.append({
                'id'            : shop.id,
                'shop_name'     : shop.name,
                'featured_image': "" if not shop.image else shop.image.url,
                'category_id'   : shop.category_id.id,
                'category'      : shop.category_id.name,
                'gst_number'    : shop.gst_number,
                'license_number': shop.license_number,
                'address'       : shop.address,
                'location'      : shop.location,
                'latitude'      : shop.latitude,
                'longitude'     : shop.longitude,
                'radius'        : shop.radius,
                'is_featured'   : shop.is_featured,
                'gst_image'     : "" if not shop.gst_image else shop.gst_image.url,
                'license_image' : "" if not shop.license_image else shop.license_image.url,
                'banner_image'  : "" if not shop.banner_image else shop.banner_image.url,
                'commission'    : shop.commission,
                'wallet_amount' : shop.wallet_amount,
                'status'        : shop.status,
                'gst_pct'       : shop.gst_pct,
                'opening_time'  : "00:00" if not shop.opening_time else shop.opening_time,
                'closing_time'  : "00:00" if not shop.closing_time else shop.closing_time,
                'website_url'   : "" if not shop.website_url else shop.website_url,
                'upi_id'        : shop.upi_id,
                'phone1'        : shop.phone1,
                'phone2'        : shop.phone2,
            })


    # all categories
    for category in all_categories:
        all_category_list.append({
                'id'            : category.id,
                'category_name' : category.name,
                'image'         : "" if not category.image else category.image.url,
            })

    user_data       =   {
                            'user_id'   : get_user_data.id,
                            'name'      : get_user_data.name,
                            'email'     : get_user_data.email,
                            'phone'     : get_user_data.phone,
                            'image'     : '' if not get_user_data.profile_image else get_user_data.profile_image.url,
                        }

    user_location   =   {
                            'latitude'  : get_user_data.latitude,
                            'longitude' : get_user_data.longitude,
                            'location'  : get_user_data.location,
                        }


    response        =   {
                            "user_data"     : user_data,
                            "user_location" : user_location,
                            "wallet_data"   : get_wallet_data,
                            "featured_shop" : featured_data,
                            "near_by_shop"  : near_by_shop_list,
                            "categories"    : all_category_list
                        } 

    
    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def shopListBasedCategory(request):
    data                = json.loads(request.body.decode("utf-8"))
    user_id             = data.get('user_id')
    category_id         = data.get('category_id')

    get_user_data       = user_data_tb.objects.all().filter(id=user_id).get()

    user_lat            = get_user_data.latitude
    user_long           = get_user_data.longitude

    near_by_shop        = shops_tb.objects.all().filter(category_id=category_id,status='Active')
    near_by_shop_list   = []

    # nearby shop
    for shop in near_by_shop:
        shop_lat        = shop.latitude
        shop_long       = shop.longitude
        radius          = shop.radius
        
        coords_1        = (user_lat, user_long)
        coords_2        = (shop_lat, shop_long)
        distance        = geopy.distance.geodesic(coords_1, coords_2).km

        if float(radius) >= float(distance):
            near_by_shop_list.append({
                    'id'            : shop.id,
                    'shop_name'     : shop.name,
                    'featured_image': "" if not shop.image else shop.image.url,
                    'category_id'   : shop.category_id.id, 
                    'category'      : shop.category_id.name, 
                    'gst_number'    : shop.gst_number,
                    'license_number': shop.license_number,
                    'address'       : shop.address,
                    'location'      : shop.location,
                    'latitude'      : shop.latitude,
                    'longitude'     : shop.longitude,
                    'radius'        : shop.radius,
                    'is_featured'   : shop.is_featured,
                    'gst_image'     : "" if not shop.gst_image else shop.gst_image.url,
                    'license_image' : "" if not shop.license_image else shop.license_image.url,
                    'banner_image'  : "" if not shop.banner_image else shop.banner_image.url,
                    'commission'    : shop.commission,
                    'wallet_amount' : shop.wallet_amount,
                    'status'        : shop.status,
                    'gst_pct'       : shop.gst_pct,
                    'opening_time'  : "00:00" if not shop.opening_time else shop.opening_time,
                    'closing_time'  : "00:00" if not shop.closing_time else shop.closing_time,
                    'website_url'   : "" if not shop.website_url else shop.website_url,
                    'upi_id'        : shop.upi_id,
                    'phone1'        : shop.phone1,
                    'phone2'        : shop.phone2,
                })


    response        =   {
                            "shop_list" : near_by_shop_list,
                        } 
    
    return JsonResponse(response, status=201)
    




@method_decorator(csrf_exempt, name='dispatch')
def userAddInvoice(request):
    # data                = dict(request.POST.items())
    # data                = json.loads(json.dumps(data))

    data                = json.loads(request.body.decode("utf-8"))

    get_user_id         = data.get('user_id')
    user_id             = user_data_tb.objects.get(id=get_user_id)
    get_shop_id         = data.get('shop_id')
    shop_id             = shops_tb.objects.get(id=get_shop_id)
    invoice_image       = data.get('invoice_image')
    invoice_number      = data.get('invoice_number')
    invoice_date        = data.get('invoice_date')
    invoice_amount      = data.get('invoice_amount')
    remark              = data.get('remark')
    submitted_by        = 'User'
   
    now                 = datetime.now()

    ##### check invoice exist - same invoice number not duplicate
    get_invoice         = invoice_data_tb.objects.all().filter(shop_id=shop_id.id,invoice_number=invoice_number)
    if get_invoice:
        response        =   {
                                "success"   : False,
                                "message"   : "Invoice exist"
                            }
        return JsonResponse(response, status=201)
    ##### check invoice exist

    vendor_id           = shop_id.vendor_id  

    get_gst_pct         = shop_id.gst_pct

    if get_gst_pct:
        gst_amount      = is_what_percent_of(float(get_gst_pct), float(invoice_amount))
        pre_tax_amount  = float(invoice_amount) - float(gst_amount)
    else:
        pre_tax_amount  = float(invoice_amount)

    date_time           = now.strftime("%Y%b%d%H%M%S")


    # if request.FILES.get('invoice_image'): # pdf to image converter
    #     pdf_file = request.FILES.get('invoice_image')
        
    #     # get the number of pages in the PDF file
    #     pdf_reader = PyPDF2.PdfReader(pdf_file)
    #     page_count = len(pdf_reader.pages)
        
    #     # convert the first page of the PDF file to a JPEG image
    #     images = convert_from_bytes(pdf_file.read(), dpi=300)
    #     image_bytes = BytesIO()
    #     images[0].save(image_bytes, format='JPEG', size=(800, 600))
        
    #     # # encode the image as a base64 string
    #     # image_base64 = base64.b64encode(image_bytes.getvalue()).decode('utf-8')
        
    #     # invoice_image= image_base64

    #     # create a file name for the image
    #     # file_name = 'invoice-'+invoice_number+f"{uuid.uuid4()}.jpg"  # generate a unique file name
    #     file_name   = 'invoice-'+invoice_number+'-'+date_time+'.jpg'
        
    #     # create a file system storage object for the media/image folder
    #     fs = FileSystemStorage(location='media/image/')
        
    #     # save the image file to the media/image folder
    #     image_file = image_bytes.getvalue()
    #     fs.save(file_name, ContentFile(image_file))
         
    #     image           = 'image/'+file_name   
    #     print('-------;;;;;-------')
    #     print(image)
   
    image               = uploadImage(invoice_image,'invoice-'+invoice_number+'-'+date_time)
    

    insert_data         = invoice_data_tb(user_id=user_id,vendor_id=vendor_id,shop_id=shop_id,invoice_image=image,invoice_number=invoice_number,invoice_date=invoice_date,pre_tax_amount=pre_tax_amount,invoice_amount=invoice_amount,submitted_by=submitted_by,remark=remark,created_at=now,updated_at=now)
    insert_data.save()

    latest_id           = invoice_data_tb.objects.latest('id')


    #----- Notification ---- #
    #-- To vendor ---
    device_token        = shop_id.vendor_id.device_token
    title               = 'New invoice is added'
    body                = 'You have a new invoice'
    sendNotificationToUser(device_token,title,body)

    insert_data         = vendor_notification_tb(vendor_id=shop_id.vendor_id,title=title,description=body,created_at=now,updated_at=now)
    insert_data.save()
    #----------------------

    response            =   {
                                "invoice_id": latest_id.id,
                                "success"   : True,
                                "message"   : ""
                            }
                         
    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def userEditProfile(request):
    data            = json.loads(request.body.decode("utf-8"))

    user_id         = data.get('user_id')
    name            = data.get('name')
    # phone           = data.get('phone')
    email           = data.get('email')
    get_image       = data.get('image')

    now             = datetime.now()
    date_time       = now.strftime("%Y%b%d%H%M%S")

    get_user        = user_data_tb.objects.all().filter(email=email).exclude(id=user_id)
    # get_user_phone  = user_data_tb.objects.all().filter(phone=phone).exclude(id=user_id)

    if get_user:
        response    =   {
                            "success"   : False,
                            "message"   : "Email already exist"
                        }

        return JsonResponse(response, status=201)

    # if get_user_phone:
    #     response    =   {
    #                         "success"   : False,
    #                         "message"   : "Phone number already exist"
    #                     }

    #     return JsonResponse(response, status=201)
    user_data_tb.objects.all().filter(id=user_id).update(name=name,email=email,updated_at=now)

    if get_image != None:
        image       = uploadImage(get_image,'user-profile-'+name+'-'+date_time)
        user_data_tb.objects.all().filter(id=user_id).update(profile_image=image,updated_at=now)

    response        =   {
                            "success"   : True,
                            "message"   : ""
                        }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def userInvoiceList(request):
    data                = json.loads(request.body.decode("utf-8"))

    user_id             = data.get('user_id')

    get_invoice_data    = invoice_data_tb.objects.all().filter(user_id=user_id).order_by('-id')

    invoice_data        = []
    for invoice in get_invoice_data:
        get_shop_images = shop_images_tb.objects.all().filter(shop_id=invoice.shop_id.id)
        images_data     = []
        for images in get_shop_images:
            images_data.append({
                'image' : "" if not images.image else images.image.url
            }) 

        invoice_data.append({
                    'id'            : invoice.id,
                    'customer_id'   : None if not invoice.user_id else invoice.user_id.id,
                    'customer_name' : None if not invoice.user_id else invoice.user_id.name,
                    'phone'         : None if not invoice.user_id else invoice.user_id.phone,
                    'vendor_id'     : invoice.vendor_id.id,
                    'vendor_phone'  : invoice.vendor_id.phone,
                    'vendor_name'   : invoice.vendor_id.name,
                    'shop_id'       : invoice.shop_id.id,
                    'shop_name'     : invoice.shop_id.name,
                    'invoice_image' : '' if not invoice.invoice_image else invoice.invoice_image.url,
                    'invoice_number': invoice.invoice_number,
                    'invoice_date'  : invoice.invoice_date,
                    'pre_tax_amount': invoice.pre_tax_amount,
                    'invoice_amount': invoice.invoice_amount,
                    'remark'        : invoice.remark,
                    'status'        : invoice.status,
                    'myself'        : True if invoice.submitted_by == 'User' else False,
                    'vendor_image'  : "" if not invoice.vendor_id.profile_image else invoice.vendor_id.profile_image.url,
                    "user_image"    : "" if not invoice.user_id.profile_image else invoice.user_id.profile_image.url,
                    'shop_images'   : "" if not invoice.shop_id.image else invoice.shop_id.image.url,
                }) 

    response        =   {
                            "invoice_data" : invoice_data
                        }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def userInvoiceDetails(request):
    data                = json.loads(request.body.decode("utf-8"))

    invoice_id          = data.get('invoice_id')

    get_invoice_data    = invoice_data_tb.objects.all().filter(id=invoice_id).get()

    invoice_data        =   {
                                'id'            : get_invoice_data.id,
                                'customer_id'   : None if not get_invoice_data.user_id else get_invoice_data.user_id.id,
                                'customer_name' : None if not get_invoice_data.user_id else get_invoice_data.user_id.name,
                                'phone'         : None if not get_invoice_data.user_id else get_invoice_data.user_id.phone,
                                'vendor_id'     : get_invoice_data.vendor_id.id,
                                'vendor_phone'  : get_invoice_data.vendor_id.phone,
                                'vendor_name'   : get_invoice_data.vendor_id.name,
                                'shop_id'       : get_invoice_data.shop_id.id,
                                'shop_name'     : get_invoice_data.shop_id.name,
                                'invoice_image' : '' if not get_invoice_data.invoice_image else get_invoice_data.invoice_image.url,
                                'invoice_number': get_invoice_data.invoice_number,
                                'invoice_date'  : get_invoice_data.invoice_date,
                                'pre_tax_amount': get_invoice_data.pre_tax_amount,
                                'invoice_amount': get_invoice_data.invoice_amount,
                                'remark'        : get_invoice_data.remark,
                                'status'        : get_invoice_data.status,
                                'myself'        : True if get_invoice_data.submitted_by == 'User' else False,
                            }


    response            =   {
                                "invoice_data"  : invoice_data,
                            }

    return JsonResponse(response, status=201)



    
@method_decorator(csrf_exempt, name='dispatch')
def userGetVendorShopDetails(request):
    data                = json.loads(request.body.decode("utf-8"))
    shop_id             = data.get('shop_id')
    shop                = shops_tb.objects.all().filter(id=shop_id).get()

    shop_data           =   {
                                'id'            : shop.id,
                                'shop_name'     : shop.name,
                                'vendor_phone'  : "" if not shop.vendor_id.phone else shop.vendor_id.phone,
                                'featured_image': "" if not shop.image else shop.image.url,
                                'category_id'   : shop.category_id.id, 
                                'category'      : shop.category_id.name, 
                                'gst_number'    : shop.gst_number,
                                'license_number': shop.license_number,
                                'address'       : shop.address,
                                'location'      : shop.location,
                                'latitude'      : shop.latitude,
                                'longitude'     : shop.longitude,
                                'radius'        : shop.radius,
                                'is_featured'   : shop.is_featured,
                                'gst_image'     : "" if not shop.gst_image else shop.gst_image.url,
                                'license_image' : "" if not shop.license_image else shop.license_image.url,
                                'banner_image'  : "" if not shop.banner_image else shop.banner_image.url,
                                'commission'    : shop.commission,
                                'wallet_amount' : shop.wallet_amount,
                                'status'        : shop.status,
                                'gst_pct'       : shop.gst_pct,
                                'opening_time'  : "00:00" if not shop.opening_time else shop.opening_time,
                                'closing_time'  : "00:00" if not shop.closing_time else shop.closing_time,
                                'website_url'   : "" if not shop.website_url else shop.website_url,
                                'upi_id'        : shop.upi_id, 
                                'phone1'        : shop.phone1,
                                'phone2'        : shop.phone2,
                            }

    response            =   {
                                "shop_data" : shop_data
                            }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def userSearchShop(request):
    data                = json.loads(request.body.decode("utf-8"))

    search_key          = data.get('search_key')
    user_lat            = data.get('user_latitude')
    user_long           = data.get('user_longitude')

    near_by_shop        = shops_tb.objects.all().filter(name__icontains=search_key,status='Active')

    near_by_shop_list   = []

    # nearby shop
    for shop in near_by_shop:
        
        shop_lat        = shop.latitude
        shop_long       = shop.longitude
        radius          = shop.radius

        coords_1        = (user_lat, user_long)
        coords_2        = (shop_lat, shop_long)
        distance        = geopy.distance.geodesic(coords_1, coords_2).km

        if float(radius) >= float(distance):
            near_by_shop_list.append({
                    'id'            : shop.id,
                    'shop_name'     : shop.name,
                    'featured_image': "" if not shop.image else shop.image.url,
                    'category_id'   : shop.category_id.id, 
                    'category'      : shop.category_id.name, 
                    'gst_number'    : shop.gst_number,
                    'license_number': shop.license_number,
                    'address'       : shop.address,
                    'location'      : shop.location,
                    'latitude'      : shop.latitude,
                    'longitude'     : shop.longitude,
                    'radius'        : shop.radius,
                    'is_featured'   : shop.is_featured,
                    'gst_image'     : "" if not shop.gst_image else shop.gst_image.url,
                    'license_image' : "" if not shop.license_image else shop.license_image.url,
                    'banner_image'  : "" if not shop.banner_image else shop.banner_image.url,
                    'commission'    : shop.commission,
                    'wallet_amount' : shop.wallet_amount,
                    'status'        : shop.status,
                    'gst_pct'       : shop.gst_pct,
                    'opening_time'  : "00:00" if not shop.opening_time else shop.opening_time,
                    'closing_time'  : "00:00" if not shop.closing_time else shop.closing_time,
                    'website_url'   : "" if not shop.website_url else shop.website_url,
                    'upi_id'        : shop.upi_id,
                    'phone1'        : shop.phone1,
                    'phone2'        : shop.phone2,
                })


    response            =   {
                                "shop_data" : near_by_shop_list
                            }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def userUpdateDeviceToken(request):
    data            = json.loads(request.body.decode("utf-8"))

    user_id         = data.get('user_id')
    device_token    = data.get('device_token')
    now             = datetime.now()

    user_data_tb.objects.all().filter(id=user_id).update(device_token=device_token,updated_at=now)


    response        =   {
                            "success"       : True,
                            "message"       : ""
                        }

    return JsonResponse(response, status=201)




def getAllShop(request):
    shop_list       = shops_tb.objects.all().filter(status='Active')

    items_data      = []
    
    for shop in shop_list:
        items_data.append({
                'id'            : shop.id,
                'shop_name'     : shop.name,
                'featured_image': "" if not shop.image else shop.image.url,
                'category_id'   : shop.category_id.id, 
                'category'      : shop.category_id.name, 
                'gst_number'    : shop.gst_number,
                'license_number': shop.license_number,
                'address'       : shop.address,
                'location'      : shop.location,
                'latitude'      : shop.latitude,
                'longitude'     : shop.longitude,
                'radius'        : shop.radius,
                'is_featured'   : shop.is_featured,
                'gst_image'     : "" if not shop.gst_image else shop.gst_image.url,
                'license_image' : "" if not shop.license_image else shop.license_image.url,
                'banner_image'  : "" if not shop.banner_image else shop.banner_image.url,
                'commission'    : shop.commission,
                'wallet_amount' : shop.wallet_amount,
                'status'        : shop.status,
                'gst_pct'       : shop.gst_pct,
                'opening_time'  : "00:00" if not shop.opening_time else shop.opening_time,
                'closing_time'  : "00:00" if not shop.closing_time else shop.closing_time,
                'website_url'   : "" if not shop.website_url else shop.website_url,
                'upi_id'        : shop.upi_id,
                'phone1'        : shop.phone1,
                'phone2'        : shop.phone2,
            })

    response        =   {
                            "shop_list"   : items_data,
                        }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def getVendorRequestCoin(request):
    data                = json.loads(request.body.decode("utf-8"))

    user_id             = data.get('user_id')

    get_all_request     = vendor_request_coin.objects.all().filter(user_id=user_id,status='Pending')
    get_all_request     = get_all_request.order_by('-id')

    request_list        = []

    for data in get_all_request:
        request_list.append({
                'id'            : data.id,
                'user_id'       : data.user_id.id,
                'shop_id'       : data.shop_id.id,
                'shop_name'     : data.shop_id.name,
                'shop_upi_id'   : data.shop_id.upi_id,
                'amount'        : data.amount,
                'status'        : data.status
            })


    response            =   {
                                "request_list" : request_list
                            }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def userVendorPaymentHistory(request):
    data                = json.loads(request.body.decode("utf-8"))

    user_id             = data.get('user_id')
    shop_id             = data.get('shop_id')

    get_all_request     = request_pay_history.objects.all().filter(user_id=user_id,shop_id=shop_id)

    request_list        = []

    for data in get_all_request:
        request_list.append({
                'id'            : data.id,
                'user_id'       : data.user_id.id,
                'shop_id'       : data.shop_id.id,
                'shop_upi_id'   : data.shop_id.upi_id,
                'amount'        : data.amount,
                'status'        : data.status,
                'is_request'    : data.is_request,
                'date'          : data.created_at,
            })


    response            =   {
                                "request_list" : request_list
                            }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def checkUserData(request):
    data        = json.loads(request.body.decode("utf-8"))

    user_id     = data.get('user_id')
    user        = user_data_tb.objects.all().filter(id=user_id)

    if user:
        for x in user:
            response    =   {
                                "user_id"       : x.id,
                                "is_active"     : bool(x.active),
                                "have_mail"     : True if x.email else False,
                                "have_pin"      : True if x.user_pin else False,
                                "have_locaton"  : True if x.location else False,
                                "user_role"     : x.user_role_id.role if x.user_role_id else None,
                            }
    else:
        response        =   {
                                "success"    : False,
                                "message"   : "User not exist",
                            }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def userNotificatons(request):
    data                    = json.loads(request.body.decode("utf-8"))

    user_id                 = data.get('user_id')

    get_notification_data   = user_notification_tb.objects.all().filter(user_id=user_id).order_by('-id')
    notification_data       = []

    for notification in get_notification_data:
        notification_data.append({
                    'id'            : notification.id,
                    'user_id'       : notification.user_id.id,
                    'title'         : notification.title,
                    'description'   : notification.description,
                })

    response                =   {
                                    "notification_data"  : notification_data
                                }

    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def deleteAllUserNotification(request):
    data        = json.loads(request.body.decode("utf-8"))

    user_id     = data.get('user_id')

    fromReg     = user_notification_tb.objects.all().filter(user_id=user_id)
    fromReg.delete()
    if fromReg.delete():
        response=   {
                        "success"   : True,
                        "message"   : "",
                    }
    else:
        response=   {
                        "success"   : False,
                        "message"   : "Something went to wrong",
                    }
    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def userGetAllShopOffers(request):
    data            = json.loads(request.body.decode("utf-8"))
    shop_id         = data.get('shop_id')

    get_all_offers  = offer_tb.objects.all().filter(shop_id=shop_id,status="Active")

    offer_data      = []
    
    for offer in get_all_offers:
        offer_data.append({
                'id'            : offer.id,
                'title'         : offer.name,
                'discount'      : offer.discount,
                'description'   : offer.description,
                'image'         : '' if not offer.image else offer.image.url,
                'status'        : offer.status,
            })

    response        =   {
                            "offer_data"   : offer_data,
                        }


    return JsonResponse(response, status=201)



@method_decorator(csrf_exempt, name='dispatch')
def userGetVendorShopDetailsWonderID(request):
    data                = json.loads(request.body.decode("utf-8"))
    upi_id              = data.get('upi_id')
    shop                = shops_tb.objects.all().filter(upi_id=upi_id).get()

    shop_data           =   {
                                'id'            : shop.id,
                                'shop_name'     : shop.name,
                                'featured_image': "" if not shop.image else shop.image.url,
                                'category_id'   : shop.category_id.id, 
                                'category'      : shop.category_id.name, 
                                'gst_number'    : shop.gst_number,
                                'license_number': shop.license_number,
                                'address'       : shop.address,
                                'location'      : shop.location,
                                'latitude'      : shop.latitude,
                                'longitude'     : shop.longitude,
                                'radius'        : shop.radius,
                                'is_featured'   : shop.is_featured,
                                'gst_image'     : "" if not shop.gst_image else shop.gst_image.url,
                                'license_image' : "" if not shop.license_image else shop.license_image.url,
                                'banner_image'  : "" if not shop.banner_image else shop.banner_image.url,
                                'commission'    : shop.commission,
                                'wallet_amount' : shop.wallet_amount,
                                'status'        : shop.status,
                                'gst_pct'       : shop.gst_pct,
                                'opening_time'  : "00:00" if not shop.opening_time else shop.opening_time,
                                'closing_time'  : "00:00" if not shop.closing_time else shop.closing_time,
                                'website_url'   : "" if not shop.website_url else shop.website_url,
                                'upi_id'        : shop.upi_id,  
                                'phone1'        : shop.phone1,
                                'phone2'        : shop.phone2,
                            }

    response            =   {
                                "shop_data" : shop_data
                            }

    return JsonResponse(response, status=201)



def userGetAppBanners(request):
    list_all_banner     = user_app_banner_tb.objects.all().order_by('order')
    all_banners         = []
    image               = None
    shop_data           = []
    is_shop             = False

    for banner in list_all_banner:
        if banner.shop_id:
            shop        = banner.shop_id
            is_shop     = True
            image       = None if not banner.shop_id.banner_image else banner.shop_id.banner_image.url
            shop_data   =   {
                                'id'            : shop.id,
                                'shop_name'     : shop.name,
                                'featured_image': "" if not shop.image else shop.image.url,
                                'category_id'   : shop.category_id.id, 
                                'category'      : shop.category_id.name, 
                                'gst_number'    : shop.gst_number,
                                'license_number': shop.license_number,
                                'address'       : shop.address,
                                'location'      : shop.location,
                                'latitude'      : shop.latitude,
                                'longitude'     : shop.longitude,
                                'radius'        : shop.radius,
                                'is_featured'   : shop.is_featured,
                                'gst_image'     : "" if not shop.gst_image else shop.gst_image.url,
                                'license_image' : "" if not shop.license_image else shop.license_image.url,
                                'banner_image'  : "" if not shop.banner_image else shop.banner_image.url,
                                'commission'    : shop.commission,
                                'wallet_amount' : shop.wallet_amount,
                                'status'        : shop.status,
                                'gst_pct'       : shop.gst_pct,
                                'opening_time'  : "00:00" if not shop.opening_time else shop.opening_time,
                                'closing_time'  : "00:00" if not shop.closing_time else shop.closing_time,
                                'website_url'   : "" if not shop.website_url else shop.website_url,
                                'upi_id'        : shop.upi_id,  
                                'phone1'        : shop.phone1,
                                'phone2'        : shop.phone2,
                            }
        elif banner.image:
            is_shop     = False
            image       = banner.image.url
            shop_data   = []

        all_banners.append({
                            'id'        : banner.id,
                            'is_shop'   : is_shop,
                            'image'     : image,
                            'order'     : banner.order,
                            'shop_data' : shop_data
                        })

    response        =   {
                            "all_banners" : all_banners
                        }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def userRoleEarnings(request):
    data                = json.loads(request.body.decode("utf-8"))
    user_id             = data.get('user_id')
    transaction_data    = user_transactions_tb.objects.all().filter(user_id=user_id,settled_commission=True).exclude(wallet_type='Shop Due Amount')

    total_amount        = user_transactions_tb.objects.all().filter(user_id=user_id).exclude(wallet_type='Shop Due Amount').aggregate(total_amount=Sum('amount'))['total_amount']
    settlement_amount   = user_transactions_tb.objects.all().filter(user_id=user_id,settled_commission=False).exclude(wallet_type='Shop Due Amount').aggregate(total_amount=Sum('amount'))['total_amount']
    earnings_amount     = float(0 if not total_amount else total_amount) - float(0 if not settlement_amount else settlement_amount)


    earnings_data       = []
    for earnings in transaction_data:
        earnings_data.append({
                            'id'            : earnings.id,
                            'amount'        : earnings_data.amount,
                            'invoice_id'    : earnings_data.invoice_id.invoice_number,
                            'invoice_amount': earnings_data.invoice_id.pre_tax_amount,
                            'date'          : earnings_data.created_at,
                        })

    response            =   {
                                "earnings_data"     : earnings_data,
                                "earnings_amount"   : earnings_amount
                            }

    return JsonResponse(response, status=201)




@method_decorator(csrf_exempt, name='dispatch')
def userRoleSettilements(request):
    data                = json.loads(request.body.decode("utf-8"))
    user_id             = data.get('user_id')
    transaction_data    = user_settlement_transactions_tb.objects.all().filter(user_id=user_id)

    total_amount        = user_transactions_tb.objects.all().filter(user_id=user_id).exclude(wallet_type='Shop Due Amount').aggregate(total_amount=Sum('amount'))['total_amount']
    settlement_amount   = user_transactions_tb.objects.all().filter(user_id=user_id,settled_commission=False).exclude(wallet_type='Shop Due Amount').aggregate(total_amount=Sum('amount'))['total_amount']
    earnings_amount     = float(0 if not total_amount else total_amount) - float(0 if not settlement_amount else settlement_amount)

    settilement_data    = []
    for settilement in transaction_data:
        settilement_data.append({
                            'id'            : settilement.id,
                            'amount'        : settilement.amount,
                            'date'          : earnings_data.created_at,
                        })

    response            =   {
                                "settilement_data"  : settilement_data,
                                "pending_amount"    : settlement_amount,
                                "settled_amount"    : earnings_amount
                            }

    return JsonResponse(response, status=201)




#########################-- Frontend ---###################
def privacyPolicy(request):
    data            = []

    get_data        = privacy_policy_tb.objects.all()
    if get_data:
        for x in get_data:
            data    =   {
                            'title'         : x.title,
                            'description'   : x.description,
                        }  

    return render(request,'frontend/privacy_policy.html',{'data' : data})



#########################-- Frontend ---###################
def contactUs(request):
    if  request.method=='POST':
        name            = request.POST['name']
        email           = request.POST['email']
        company         = request.POST['company']
        user_messages   = request.POST['message']
        now             = datetime.now()

        insert_data     = user_contacts_tb(name=name,email=email,company=company,messages=user_messages,created_at=now,updated_at=now)
        insert_data.save()

        messages.success(request, 'Successfully submitted.')
        return redirect('contact-us')
    else:
        data            = []
        get_data        = contact_us_tb.objects.all()
        if get_data:
            for x in get_data:
                data    =   {
                                'id'        : x.id,
                                'email'     : x.email,
                                'mobile'    : x.mobile,
                                'address'   : x.address,
                                'location'  : x.location,
                                'latitude'  : x.latitude,
                                'longitude' : x.longitude
                            }  
        return render(request,'frontend/contact_us.html',{'data' : data})



#######################################################

@method_decorator(csrf_exempt, name='dispatch')
def updateWalletTransactionExpiryDate(request):
    # Retrieve all data from the table
    # wallet_transaction      = wallet_transactions_tb.objects.all()

    # Update the expiry_date field for each transaction
    # for transaction in wallet_transaction:
    #     transaction.expiry_date = datetime(product.expiry_date.year, 12, 31)
    #     transaction.save()
    wallet_transactions_tb.objects.update(expiry_date=datetime(2023, 12, 31, 0, 0, 0, 0))


    response        =   {
                            "success" : True
                        }

    return JsonResponse(response, status=201)



