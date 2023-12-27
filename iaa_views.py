from datetime import timedelta
from functools import reduce, wraps
from itertools import chain
from django.db.models.functions import *
from django.db import transaction
from django.http import *
import csv
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import numpy as np
import requests
from .models import *
import json
from django.http import JsonResponse
from django.core.management.base import BaseCommand
from bs4 import UnicodeDammit
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import *  # login_required
from django.views.decorators.cache import cache_control
from django.db.models import *

from django.utils import timezone
import pandas as pd
import ast

import psycopg2
# import mysql.connector

from .modeltblclname import *

# import pytz
# time_zone = "Asia/Kolkata"
# datetimenow = datetime.now(pytz.timezone(time_zone))
date_format = "%Y-%m-%dT%H:%M"

def loginrequired(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            session = request.session
            if 'empId' in session and 'language' in session and 'location' in session:
                return view_func(request, *args, **kwargs)
            else:
                request.session.flush()
                request.session.clear()
                return redirect('/dash/')
        except Exception as er:
            print(er)
            return redirect('/dash/')
    return _wrapped_view

# def custom_token_login_required(view_func):
#     def _wrapped_view(request, *args, **kwargs):
#         EmployeeID = request.session.get('employeeID')
#         Token = request.session.get('token')
#         url = ...
#         data = {
#             'EmpID': EmployeeID,
#             'Token': Token
#         }
#         response = requests.post(url, data=data)

#         # if response.status_code == 200:

#         if Token == response.token:
#             return view_func(request, *args, **kwargs)
#         else:
#             return HttpResponseRedirect('https://google.com')
#         # else:
#         # return HttpResponseRedirect('https://google.com')
#     return _wrapped_view

# def createUserProfile(EmployeeID, Token):
#     # url = ...
#     # data = {
#     #     'EmpID': EmployeeID,
#     #     'Token' : Token
#     # }
#     # response = requests.post(url, data=data)

#     # if response.status_code == 200:

#     employeeName = 'bharath'  # response.employeeName
#     location = 'mnw'  # response.location
#     reportingperson = '1234'  # response.reportingperson
#     productionstartdate = timezone.now()  # response.productionstartdate
#     Token = 'lkhkjhjkgjhfgjhvhgf'  # response.token

#     if Token == request.session.get('token'):

#         UserID, created = userProfile.objects.update_or_create(
#             employeeID=EmployeeID,
#             defaults={'employeeName': employeeName,
#                       'location': location, 'reporting': reportingperson,
#                       'prodStart_date': productionstartdate
#                       })

#         request.session['empId'] = UserID.id
#         request.session['employeeID'] = EmployeeID
#         request.session['employeeName'] = employeeName
#         request.session['token'] = Token

#         permlist = Roles.objects.filter(
#             userprofile_id__employeeID=EmployeeID).values_list('role')
#         request.session['permlist'] = list(permlist)

#     else:
#         request.session.flush()
#         request.session.clear()
#         request.session.clear_expired()
#         return HttpResponseRedirect('https://google.com')
#     # else:
#     #     return HttpResponseRedirect('https://google.com')


@csrf_exempt
# @custom_token_login_required
def home(request):
    if request.method == 'POST':
        data = request.POST.get('token')
        request.session['token'] = data
        status = 'success'
        responseData = {'status': 'successpost'}
        return JsonResponse(responseData)
    else:
        data = request.GET.get('token')
        employeeid = request.GET.get('user')
        # employeename = request.GET.get('empname')

        # request.session['token'] = data
        # request.session['user'] = employeeid

        # UserID, created = userProfile.objects.update_or_create(
        # employeeID=employeeid,
        # defaults={'employeeName': employeename,
        #         #   'location': location, 'reporting': reportingperson,
        #             })
        # Roles.objects.update_or_create(
        #     userprofile_id=UserID.id, role='Admin')
        # request.session['empId'] = UserID.id
        # request.session['employeeID'] = employeeid
        # permlist = Roles.objects.filter(
        #     userprofile_id__employeeID=employeeid).values('role')
        # request.session['permlist'] = [i['role'] for i in permlist]

        return redirect('/dash/')


def custom_token_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # token_key= request.session.get('token')
        token_key = '20231120063621W4189771'
        print(token_key, "hi")
        try:
            conn = mysql.connector.connect(
                host="mpulse-backup.cxqifsxuei8y.ap-south-1.rds.amazonaws.com",
                user="mpulse",
                password="smile2021!",
                database="mpulse"
            )
            cursor_obj = conn.cursor()
            print("connection establishes")
            sql = f"""
            select * from users at2 where at2.token ='{token_key}'
            """
            cursor_obj.execute(sql)
            result = cursor_obj.fetchall()
            print(result, "result____")
            if len(result) > 0:
                request.session['user'] = result[0][3]
                request.session['token'] = result[0][11]
                print(request.session.get('token'))
                print(request.session.get('user'))
                # return HttpResponseRedirect('/dash/')
                pass
                # return redirect('/dash/')
            else:
                return JsonResponse({'error': 'Unauthorized'}, status=401)
        except Exception as er:
            print(er)
            return JsonResponse({'error': str(er)}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @custom_token_login_required
def dashboardView(request):
    if request.method == 'POST':
        employeeid = request.POST.get('empid')
        employeename = request.POST.get('empname')
        password = request.POST.get('password')

        if password == 'admin123$':

            UserID, created = userProfile.objects.update_or_create(
                employeeID=employeeid,
                defaults={'employeeName': employeename})
            request.session['empId'] = UserID.id
            request.session['employeeID'] = employeeid

            userrec = userProfile.objects
            language = userrec.filter(id=UserID.id).values('language')[0]
            location = userrec.filter(id=UserID.id).values('location')
            
            # Roles.objects.update_or_create(
            #   userprofile_id=UserID.id, role='Admin')
            try:        
              request.session['language'] = ast.literal_eval(language['language'])
            except Exception as er:
              request.session['language'] = list('English')
              print(er)
            request.session['location'] = [i['location'] for i in location]
            permlist = Roles.objects.filter(
                userprofile_id__employeeID=employeeid).values('role')

            request.session['permlist'] = [i['role'] for i in permlist]
            
            return render(request, 'index.html')
        else:
            return render(request, 'index.html')
    else:           
        return render(request, 'index.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @custom_token_login_required
@loginrequired
def app_logOut(request):
    request.session.flush()
    request.session.clear()
    request.session.clear_expired()
    return HttpResponseRedirect('/dash/')


@loginrequired
def userTable(request):
    if request.method == "POST":
        employeeID = request.POST.get('employeeID')
        # print(employeeID)
        userdatas = userProfile.objects.filter(employeeID=employeeID).values(
            'id', 'employeeName', 'employeeID', 'location', 'language', 'reporting', 'prodStart_date', 'created_at')
        roles = Roles.objects.filter(
            userprofile_id__employeeID=employeeID).values('role')
        shift =  ShiftTime.objects.filter(userprofile__employeeID=employeeID).values('starttime','endtime').last()
        return render(request, 'pages/userManagement.html', {'userdatas': userdatas[0], 'roles': [i['role'] for i in roles],'shift':shift})
    else:
        userdatas = userProfile.objects.values(
            'id', 'employeeName', 'employeeID', 'location', 'language', 'reporting', 'prodStart_date', 'created_at')
        roles = Roles.objects.values('userprofile_id__employeeID','role')
        return render(request, 'pages/UserTable.html', {'userDatas': userdatas,'roles':roles})


@loginrequired
def OverAllRole(request):
    if request.method == 'POST':
        employeeID = request.POST.get('employeeid')
        roles = request.POST.getlist('roles')
        try:
            UseTable = userProfile.objects
            empall = [eid.strip() for eid in employeeID.split(',')]
            for EmpId in empall:
                UseTable.update_or_create(
                    employeeID=EmpId)

            UserID = UseTable.filter(
                employeeID__in=empall).values('id')
            for ids in UserID:
                for role in roles:
                    Roles.objects.create(
                        userprofile_id=ids['id'], role=role, created_by_id=request.session.get('empId'))
            return JsonResponse({'status': 200, 'message': 'Success'})

        except Exception as er:
            return JsonResponse({'status': 400, 'message': str(er)})
    else:
        return redirect('/api/v5/userTable/')


@loginrequired
def UserManagement(request):
    if request.method == "POST":
        key = request.POST.get('key')
        if key == 'userdata':
            employeeID = request.POST.get('employeeid')
            employeeName = request.POST.get('employeeName')
            reporting = request.POST.get('reporting')
            location = request.POST.get('location')
            language = request.POST.getlist('language')
            prodStart_date = request.POST.get('prodStart_date')
            roles = request.POST.getlist('role')

            UserID, created = userProfile.objects.update_or_create(
                employeeID=employeeID,
                defaults={'employeeName': employeeName,
                          'reporting': reporting,
                          'language':language,
                          'location': location,
                          'prodStart_date': prodStart_date})
            try:
                rolestable = Roles.objects
                for role in roles:
                    if not rolestable.filter(role=role,userprofile_id=UserID.id).exists():
                        rolestable.update_or_create(
                            userprofile_id=UserID.id, role=role, created_by_id=request.session.get('empId'))                    
                rolestable.filter(userprofile_id=UserID.id,).exclude(role__in=roles).delete()
            except Exception as er:
                return JsonResponse({'status': 400, 'message': str(er)})
            return JsonResponse({'status': 200, 'message': 'Success'})

        else:
            userprofile = request.POST.get('userprofile')
            shift_starttime = request.POST.get('shift_starttime')
            shift_endtime = request.POST.get('shift_endtime')
            ShiftTime.objects.update_or_create(
                userprofile_id=userprofile, starttime=shift_starttime, endtime=shift_endtime, created_by_id=request.session.get('empId'))
            return redirect('/api/v5/userTable/')
    else:
        return render(request, 'pages/userManagement.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@loginrequired
def uploadView(request):
    EmpID = request.session.get('empId')
    if request.method == 'POST':
        language = request.POST.get('language', None)
        file_name = request.FILES.get('file', None)
        fileExtention = str(file_name).split('.')
        key = request.POST.get('key', None)

        if fileExtention and file_name:
            fileType = fileExtention[1]

            last_RECD = basefile.objects.order_by('-id').first()
            if last_RECD:
                last_id = int(last_RECD.batch_name[5:])
                new_id = last_id + 1
            else:
                new_id = 1
            batch_name = f'BATCH{new_id:05}'

            if fileType == 'csv':
                excel_data = pd.read_csv(file_name, encoding='utf-8', encoding_errors='ignore')
                to_dict = excel_data.to_dict('records')
                baseid = basefile.objects.create(batch_name=batch_name,filename=file_name,language=language,created_by_id=EmpID)
                try:
                    with transaction.atomic():
                        for i in to_dict:
                            raw_data.objects.create(
                                id_value=i.get('id_value', None),
                                question=i.get('question', None),
                                asin=i.get('asin', None),
                                title=i.get('title', None),
                                product_url=i.get('product_url', None),
                                imagepath=i.get('imagepath', None),
                                evidence=i.get('evidence', None),
                                answer_one=i.get('answer_one', None),
                                answer_two=i.get('answer_two', None),
                                baseid_id=baseid.id
                            )
                        responseData = {'status': 'success',
                                        'result': 'Data Upload Successfully'}
                        return JsonResponse(responseData)
                except Exception as er:
                    print(er)
                    responseData = {'status': 'failed',
                                    'result': ",File Already Exist"}
                    return JsonResponse(responseData)
            else:
                file_content = file_name.read()
                parsed_data = json.loads(file_content)
                # cleaned_data = remove_binary_and_newlines(
                #     parsed_data)  # Remove binary and newline characters
                # cleaned_json = json.dumps(cleaned_data, indent=4)
                baseid = basefile.objects.create(batch_name=batch_name,filename=file_name,language=language,created_by_id=EmpID)
                try:
                    with transaction.atomic():
                        for i in parsed_data:
                            raw_data.objects.create(
                                id_value=i.get('id_value', None),
                                question=i.get('question', None),
                                asin=i.get('asin', None),
                                title=i.get('title', None),
                                product_url=i.get('product_url', None),
                                imagepath=i.get('imagepath', None),
                                evidence=i.get('evidence', None),
                                answer_one=i.get('answer_one', None),
                                answer_two=i.get('answer_two', None),
                                baseid_id=baseid.id
                            )
                        responseData = {'status': 'success',
                                        'result': 'Data Upload Successfully'}
                        return JsonResponse(responseData)
                except Exception as er:
                    print(er)
                    responseData = {'status': 'failed',
                                    'result': "File Already Exist"}
                    return JsonResponse(responseData)

        elif key == 'MiniRecords':
            fromdate = request.POST.get('fromDate')                       
            todate = request.POST.get('toDate')
            language = request.POST.get('language')
            request.session['fromDate'] = fromdate
            request.session['toDate'] = todate

            status = request.POST.get('status', None)
            request.session['smpstatus'] = status

            conditions = Q()
            if status != 'All':
                conditions &= Q(status=status)
            if fromdate and todate:
                conditions &= Q(baseid_id__created_at__range=(fromdate, todate))
            if language != 'All':
                conditions &= Q(baseid_id__language= language)

            datas = raw_data.objects.filter(conditions )
            if datas.count() > 0:
                tabledata = datas.annotate(uploaded_at=TruncMinute('baseid_id__created_at')).values('baseid_id__batch_name', 'status', 'baseid_id__created_by_id__employeeID', 'uploaded_at', 'baseid_id__filename','baseid_id__language').annotate(
                    count=Count('status')).order_by('uploaded_at').distinct()
                content = 'show'
            else:
                tabledata = []
                content = 'hide'
            return render(request, 'pages/upload.html', {'tabledata': tabledata, 'content': content})
        else:
            responseData = {'status': 'failed', 'result': 'Data is Required'}
            return JsonResponse(responseData)
    else:
        datas = raw_data.objects.filter(~Q(status='deleted'))
        if datas.count() > 0:
            tabledata = datas.annotate(uploaded_at=TruncMinute('baseid_id__created_at')).values('baseid_id__batch_name', 'status', 'baseid_id__created_by_id__employeeID', 'uploaded_at', 'baseid_id__filename','baseid_id__language').annotate(
                count=Count('status')).order_by('uploaded_at').distinct()
            content = 'show'
        else:
            tabledata = []
            content = 'hide'
        # raw_data.objects.filter(baseid_id__batch_name='BATCH00003').delete()
        return render(request, 'pages/upload.html', {'tabledata': tabledata, 'content': content, 'key': 'all'})


@loginrequired
def miniFileDownload(request):
    if request.method == "POST":
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="MiniFileDownload.csv"'

        status = request.session.get('smpstatus', None)
        fromdate = request.session['fromDate']
        todate = request.session['toDate']

        conditions = Q()
        if status:
            conditions &= Q(status=status)
        if fromdate and todate:
            conditions &= Q(baseid_id__created_at__range=(fromdate, todate))

        datas = raw_data.objects.filter(~Q(status='deleted'), conditions)
        if datas.count() > 0:
            tabledata = datas.annotate(uploaded_at=TruncMinute('baseid_id__created_at')).values('baseid_id__batch_name', 'status', 'baseid_id__created_by_id__employeeID', 'uploaded_at', 'baseid_id__filename').annotate(
                count=Count('status')).order_by('uploaded_at').distinct()
            writer = csv.writer(response)
            title = [
                "BAtch ID",
                "File Name",
                "Status",
                "Uploaded By",
                "Uploaded At"]
            writer.writerow(title)
            for v in tabledata:
                record = [v["baseid_id__batch_name"],
                          v["baseid_id__filename"],
                          v["status"],
                          v["baseid_id__created_by_id__employeeID"],
                          v["uploaded_at"]]
                writer.writerow(record)
            return response


@loginrequired
def fileDownload(request, batchid, filename_form):
    batchID = batchid
    filename = filename_form

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="FileDownload"' + \
        batchID+'_'+filename+'".csv"'

    records = raw_data.objects.filter(baseid_id__batch_name=batchID).values("id_value", "baseid_id__batch_name", "baseid_id__created_at", "baseid_id__created_by_id__employeeID",
                                                                 "question",
                                                                 "asin",
                                                                 "title",
                                                                 "product_url",
                                                                 "imagepath",
                                                                 "evidence",
                                                                 "answer_one",
                                                                 "answer_two", "baseid_id__filename")
    writer = csv.writer(response)
    title = [
        "batchID",
        "File Name",
        "id_value",
        "question",
        "asin",
        "title",
        "product_url",
        "imagepath",
        "evidence",
        "answer_one",
        "answer_two",
        "created_at",
        "created_by"]
    writer.writerow(title)
    for v in records:
        record = [v["baseid_id__batch_name"],
                  v["baseid_id__filename"],
                  v["id_value"],
                  v["question"],
                  v["asin"],
                  v["title"],
                  v["product_url"],
                  v["imagepath"],
                  v["evidence"],
                  v["answer_one"],
                  v["answer_two"],
                  v['baseid_id__created_at'],
                  v["baseid_id__created_by_id__employeeID"]]
        writer.writerow(record)

    if records.exists():
        return response
    else:
        return JsonResponse({'status': 400, 'message': 'No Records'})


@loginrequired
def fileMamagement(request):
    if request.method == 'POST':        
        key = request.POST.get('key')     

        if key == 'delete':
            filename = request.POST.get('filename')
            raw_data.objects.filter(baseid_id__filename=filename).update( status='deleted')
            basefile.objects.filter(filename=filename).update(filename=str(filename)+'Deleted')
        elif key == 'processing':
            batch_name = request.POST.get('batch_name')
            selectbox = request.POST.get('selectedValue')
            if selectbox == 'ALL' :
                raw_data.objects.filter( baseid_id__batch_name=batch_name).update(status='hold')
            elif selectbox == 'DA1' :
                raw_data.objects.filter( Q(l1_status__isnull=True) | Q(l1_status__isnull=False),baseid_id__batch_name=batch_name).update(status='hold')
            elif selectbox == 'DA2' :
                raw_data.objects.filter( Q(l2_status__isnull=True) | Q(l2_status__isnull=False),baseid_id__batch_name=batch_name).update(status='hold')
            elif selectbox == 'QC' :
                raw_data.objects.filter((Q(l1_status__isnull=True) | Q(l1_status__isnull=False)) & (Q(l2_status__isnull=True) | Q(l2_status__isnull=False)) & (Q(l3_status__isnull=True) | Q(l3_status__isnull=False)),baseid_id__batch_name=batch_name).update(status='hold')
            elif selectbox == 'QA' :
                raw_data.objects.filter( (Q(l1_status__isnull=True) | Q(l1_status__isnull=False)) & (Q(l2_status__isnull=True) | Q(l2_status__isnull=False)) & (Q(l4_status__isnull=True) | Q(l4_status__isnull=False)),baseid_id__batch_name=batch_name).update(status='hold')

        elif key == 'hold':
            batch_name = request.POST.get('batch_name')
            selectbox = request.POST.get('selectedValue')
            if selectbox == 'ALL' :
                raw_data.objects.filter( baseid_id__batch_name=batch_name).update(status='processing')
            elif selectbox == 'DA1' :
                raw_data.objects.filter( Q(l1_status__isnull=True) | Q(l1_status__isnull=False),baseid_id__batch_name=batch_name).update(status='processing')
            elif selectbox == 'DA2' :
                raw_data.objects.filter( Q(l2_status__isnull=True) | Q(l2_status__isnull=False),baseid_id__batch_name=batch_name).update(status='processing')
            elif selectbox == 'QC' :
                raw_data.objects.filter((Q(l1_status__isnull=True) | Q(l1_status__isnull=False)) & (Q(l2_status__isnull=True) | Q(l2_status__isnull=False)) & (Q(l3_status__isnull=True) | Q(l3_status__isnull=False)),baseid_id__batch_name=batch_name).update(status='processing')
            elif selectbox == 'QA' :
                raw_data.objects.filter( (Q(l1_status__isnull=True) | Q(l1_status__isnull=False)) & (Q(l2_status__isnull=True) | Q(l2_status__isnull=False)) & (Q(l4_status__isnull=True) | Q(l4_status__isnull=False)),baseid_id__batch_name=batch_name).update(status='processing')
            
        return JsonResponse({'status': 'Success'})
    # return render(request, 'pages/upload.html')


@loginrequired
def remove_binary_and_newlines(data):
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if isinstance(value, bytes):
                del data[key]  # Remove binary value
            else:
                data[key] = remove_binary_and_newlines(value)
    elif isinstance(data, list):
        data = [remove_binary_and_newlines(item) for item in data]
    elif isinstance(data, str):
        data = data.replace('\n', '')

    return data


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@loginrequired
def SampleFileDownloadView(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="evaluate.csv"'
    csv_writer = csv.writer(response)
    header = ["id_value", "question", "asin", "title", "product_url",
              "imagepath", "evidence", "answer_one", "answer_two"]
    csv_writer.writerow(header)
    return response


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @login_required(login_url="/")
@loginrequired
def loneproductionView(request):
    EmpID = request.session.get('empId')
    language = request.session.get('language')
    location = request.session.get('location')
    # EmpLoc = request.session.get('empLoc') Location/area wise filter
    # ,Q(created_by_id__location = EmpLoc)

    if request.method == 'GET':
        try:
            with transaction.atomic():
                l1_count = raw_data.objects.filter(Q(l1_status='completed') & Q(l1_emp_id=EmpID)).exclude(status__in=['hold', 'deleted']).count()
                if l1_count is not None:
                    l1_count = l1_count
                else:
                    l1_count = 0

                query = Q()
                if language:
                    query = Q(baseid_id__language__in=language)

                instance = raw_data.objects.select_for_update(skip_locked=True).filter( query, 
                                (Q(l1_status='picked') & Q(l1_emp_id=EmpID)) | (Q(l1_status='not_picked') & Q(l1_emp_id__isnull=True)) & (Q(l1_loc__isnull=True) & Q(l2_loc__isnull=True) | Q(l2_loc=location[0]))).values('id', 'id_value', 'question', 'asin', 'title', 'product_url', 'imagepath', 'evidence', 'answer_one', 'answer_two', 'l1_emp_id').exclude(status__in=['hold', 'deleted']).exclude(l2_emp_id=EmpID).order_by('-l1_status').first()

                if instance:
                    l1prod = l1_production.objects
                    if l1prod.filter(qid_id=instance['id']).exists():
                        l1_production.objects.filter(qid_id=instance['id']).update(start_time = timezone.now())
                    else:
                        prodid = l1_production.objects.create(qid_id=instance['id'], start_time = timezone.now())
                        raw_data.objects.filter(id=instance['id']).update(
                            l1_status='picked', l1_emp_id=EmpID,l1_loc=location[0],l1_prod_id=prodid.id)
        except Exception as er:
            print(er)
            instance = []
        return render(request, 'pages/l1_production.html', {'result': instance, 'l1_count': l1_count,'start_time': timezone.now()})
    else:
        key = request.POST.get('key', None)
        eid = request.POST.get('eid', None)
        q1 = request.POST.get('q1', None)
        q2 = request.POST.get('q2', None)
        q2_1 = request.POST.get('q2_1', None)
        is_present_both = request.POST.get('is_present_both', None)
        q3 = request.POST.get('q3', None)
        q4_1 = request.POST.get('q4_1', None)
        q4_a_1 = request.POST.get('q4_a_1', None)
        q5_1 = request.POST.get('q5_1', None)
        q6_other_1 = request.POST.get('q6_other_1', None)
        q7_1 = request.POST.get('q7_1', None)
        q7_other_1 = request.POST.getlist('q7_other_1[]', [])
        # q7_other_1 = request.POST.get('q7_other_1', None)
        q8_1 = request.POST.get('q8_1', None)
        q9_1 = request.POST.get('q9_1', None)
        q10_1 = request.POST.get('q10_1', None)
        q11_1 = request.POST.get('q11_1', None)
        q12_1 = request.POST.get('q12_1', None)
        q4_2 = request.POST.get('q4_2', None)
        q4_a_2 = request.POST.get('q4_a_2', None)
        q5_2 = request.POST.get('q5_2', None)
        q6_other_2 = request.POST.get('q6_other_2', None)
        q7_2 = request.POST.get('q7_2', None)
        # q7_other_2 = request.POST.get('q7_other_2', None)
        q7_other_2 = request.POST.getlist('q7_other_2[]', [])
        q8_2 = request.POST.get('q8_2', None)
        q9_2 = request.POST.get('q9_2', None)
        q10_2 = request.POST.get('q10_2', None)
        q11_2 = request.POST.get('q11_2', None)
        q12_2 = request.POST.get('q12_2', None)
        annot_commant = request.POST.get('annot_commant', None)
        general_que1 = request.POST.getlist('general_que1', None)
        general_que2 = request.POST.get('general_que2', None)
        general_que2_2 = request.POST.get('general_que2_2', None)
        general_que3 = request.POST.get('general_que3', None)
        start_time = request.POST.get('start_time', None)

        if key == 'submit':
            try:
                with transaction.atomic():
                    l1prod = l1_production.objects.filter(qid_id=eid)
                    l1prod.update( end_time=timezone.now(), que1=q1, que2=q2, que2_1=q2_1, que3=q3, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1,  que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1,  q12_ans1=q12_1, que4_ans2=q4_2, que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, q12_ans2=q12_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, general_ques2_2=general_que2_2, general_ques3=general_que3, created_by_id=EmpID)

                    l1prod_values = l1prod.values_list('id', flat=True)

                    link_objects = [
                        l1_production_link(
                            production_id=l1prod_values, link=value, linkfor='q7_1')
                        for value in q7_other_1 if value
                    ] + [
                        l1_production_link(
                            production_id=l1prod_values, link=value, linkfor='q7_2')
                        for value in q7_other_2 if value
                    ]

                    with transaction.atomic():
                        l1_production_link.objects.bulk_create(link_objects)

                responseData = {'status': 'success',
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l1_prod_id=l1prod_values,
                                                           l1_status='completed', l1_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        elif key == 'submit_close':
            try:
                with transaction.atomic():
                    l1prod = l1_production.objects.filter(qid_id=eid)
                    l1prod.update(end_time=timezone.now(), que1=q1, que2=q2, que2_1=q2_1, que3=q3, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1,  q12_ans1=q12_1, que4_ans2=q4_2, que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, q12_ans2=q12_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, general_ques2_2=general_que2_2, general_ques3=general_que3, created_by_id=EmpID)

                l1prod_values = l1prod.values_list('id', flat=True)
                link_objects = [
                    l1_production_link(
                        production_id=l1prod_values, link=value, linkfor='q7_1')
                    for value in q7_other_1 if value
                ] + [
                    l1_production_link(
                        production_id=l1prod_values, link=value, linkfor='q7_2')
                    for value in q7_other_2 if value
                ]

                with transaction.atomic():
                    l1_production_link.objects.bulk_create(link_objects)
                redirect_url = '/'
                responseData = {'status': 'success', 'redirect_url': redirect_url,
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l1_prod_id=l1prod_values,
                                                           l1_status='completed', l1_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        else:
            try:
                with transaction.atomic():
                    l1prod = l1_production.objects.filter(qid_id=eid)
                    l1prod.update(end_time=timezone.now(), que1=q1, que2=q2, que2_1=q2_1, que3=q3, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, q12_ans1=q12_1, que4_ans2=q4_2, que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, q12_ans2=q12_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, general_ques2_2=general_que2_2, general_ques3=general_que3, created_by_id=EmpID)

                responseData = {'status': 'success',
                                'result': "Production  Hold"}
                if eid:
                    raw_data.objects.filter(id=eid).update(
                        l1_status='hold', l1_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @login_required(login_url="/")
@loginrequired
def ltwoproductionView(request):
    EmpID = request.session.get('empId')
    language = request.session.get('language')
    location = request.session.get('location')
    if request.method == 'GET':
        try:
            with transaction.atomic():
                l2_count = raw_data.objects.filter(Q(l2_status='completed') & Q(l2_emp_id=EmpID)).exclude(status__in=['hold', 'deleted']).count()
                if l2_count is not None:
                    l2_count = l2_count
                else:
                    l2_count = 0

                query = Q()
                if language:
                    query = Q(baseid_id__language__in=language)

                instance = raw_data.objects.select_for_update(skip_locked=True).filter( query, 
                        (Q(l2_status='picked') & Q(l2_emp_id=EmpID)) | (Q(l2_status='not_picked') & Q(l2_emp_id__isnull=True)) & (Q(l2_loc__isnull=True) & Q(l1_loc__isnull=True) | Q(l1_loc=location[0]))).values('id', 'id_value', 'question', 'asin', 'title', 'product_url', 'imagepath', 'evidence', 'answer_one', 'answer_two', 'l2_emp_id').exclude(status__in=['hold', 'deleted']).order_by('-l2_status').exclude(l1_emp_id=EmpID).first()

                if instance:
                    l2prod = l2_production.objects
                    if l2prod.filter(qid_id=instance['id']).exists():
                        l2_production.objects.filter(qid_id=instance['id']).update(start_time = timezone.now())
                    else:
                        prodid = l2_production.objects.create(qid_id=instance['id'], start_time = timezone.now())
                        raw_data.objects.filter(id=instance['id']).update(
                            l2_status='picked', l2_emp_id=EmpID,l2_loc=location[0],l2_prod_id=prodid.id)
        except Exception as er:
            print(er)
            instance = []
        return render(request, 'pages/l2_production.html', {'result': instance, "l2_count": l2_count,'start_time': timezone.now()})
    else:
        key = request.POST.get('key', None)
        eid = request.POST.get('eid', None)
        q1 = request.POST.get('q1', None)
        q2 = request.POST.get('q2', None)
        q2_1 = request.POST.get('q2_1', None)
        is_present_both = request.POST.get('is_present_both', None)
        q3 = request.POST.get('q3', None)
        q4_1 = request.POST.get('q4_1', None)
        q4_a_1 = request.POST.get('q4_a_1', None)
        q5_1 = request.POST.get('q5_1', None)
        q6_other_1 = request.POST.get('q6_other_1', None)
        q7_1 = request.POST.get('q7_1', None)
        # q7_other_1 = request.POST.get('q7_other_1', None)
        q7_other_1 = request.POST.getlist('q7_other_1[]', [])
        q8_1 = request.POST.get('q8_1', None)
        q9_1 = request.POST.get('q9_1', None)
        q10_1 = request.POST.get('q10_1', None)
        q11_1 = request.POST.get('q11_1', None)
        q12_1 = request.POST.get('q12_1', None)
        q4_2 = request.POST.get('q4_2', None)
        q4_a_2 = request.POST.get('q4_a_2', None)
        q5_2 = request.POST.get('q5_2', None)
        q6_other_2 = request.POST.get('q6_other_2', None)
        q7_2 = request.POST.get('q7_2', None)
        # q7_other_2 = request.POST.get('q7_other_2', None)
        q7_other_2 = request.POST.getlist('q7_other_2[]', [])
        q8_2 = request.POST.get('q8_2', None)
        q9_2 = request.POST.get('q9_2', None)
        q10_2 = request.POST.get('q10_2', None)
        q11_2 = request.POST.get('q11_2', None)
        q12_2 = request.POST.get('q12_2', None)
        annot_commant = request.POST.get('annot_commant', None)
        general_que1 = request.POST.getlist('general_que1', None)        
        general_que2 = request.POST.get('general_que2', None)
        general_que2_2 = request.POST.get('general_que2_2', None)
        general_que3 = request.POST.get('general_que3', None)
        start_time = request.POST.get('start_time')
        if key == 'submit':
            try:
                with transaction.atomic():
                    l2prod = l2_production.objects.filter(qid_id=eid)
                    l2prod.update(end_time=timezone.now(), que1=q1, que2=q2, que2_1=q2_1, que3=q3, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, q12_ans1=q12_1, que4_ans2=q4_2, que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, q12_ans2=q12_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, general_ques2_2=general_que2_2, general_ques3=general_que3, created_by_id=EmpID)

                l2prod_values = l2prod.values_list('id', flat=True)
                link_objects = [
                    l2_production_link(
                        production_id=l2prod_values, link=value, linkfor='q7_1')
                    for value in q7_other_1 if value
                ] + [
                    l2_production_link(
                        production_id=l2prod_values, link=value, linkfor='q7_2')
                    for value in q7_other_2 if value
                ]

                with transaction.atomic():
                    l2_production_link.objects.bulk_create(link_objects)

                responseData = {'status': 'success',
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l2_prod_id=l2prod.values_list('id'),
                                                           l2_status='completed', l2_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        elif key == 'submit_close':
            try:
                with transaction.atomic():
                    l2prod = l2_production.objects.filter(qid_id=eid)
                    l2prod.update(end_time=timezone.now(), que1=q1, que2=q2, que2_1=q2_1, que3=q3, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, q12_ans1=q12_1, que4_ans2=q4_2, que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, q12_ans2=q12_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, general_ques2_2=general_que2_2, general_ques3=general_que3, created_by_id=EmpID)

                l2prod_values = l2prod.values_list('id', flat=True)
                link_objects = [
                    l2_production_link(
                        production_id=l2prod_values, link=value, linkfor='q7_1')
                    for value in q7_other_1 if value
                ] + [
                    l2_production_link(
                        production_id=l2prod_values, link=value, linkfor='q7_2')
                    for value in q7_other_2 if value
                ]
                with transaction.atomic():
                    l2_production_link.objects.bulk_create(link_objects)

                redirect_url = '/'
                responseData = {'status': 'success', 'redirect_url': redirect_url,
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l2_prod_id=l2prod.values_list('id'),
                                                           l2_status='completed', l2_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        else:
            try:
                with transaction.atomic():
                    l2prod = l2_production.objects.filter(qid_id=eid)
                    l2prod.update(end_time=timezone.now(), que1=q1, que2=q2, que2_1=q2_1, que3=q3, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, q12_ans1=q12_1, que4_ans2=q4_2, que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, q12_ans2=q12_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, general_ques2_2=general_que2_2, general_ques3=general_que3, created_by_id=EmpID)

                responseData = {'status': 'success',
                                'result': "Production  Hold"}
                if eid:
                    raw_data.objects.filter(id=eid).update(
                        l2_status='hold', l2_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

def queue():
    rawData = raw_data.objects.filter(Q(l1_status='completed') & Q(l2_status='completed') & Q(l1_l2_accuracy__isnull=True)).values('id')
    for i in rawData:
        fromqueue = l1_l2Comparison(i['id'])
        queue = fromqueue['result']
        if 'Not Matched' in queue['Comparison'].values:
            l1_l2_accuracy = 'fail'
        else:
            l1_l2_accuracy = 'pass'
        raw_data.objects.filter(id=i['id']).update( l1_l2_accuracy=l1_l2_accuracy)
    return

def l1_l2Comparison(id):
    l1_prod = l1_production.objects.filter(qid_id=id).values('id', 'que1', 'que2', 'que2_1', 'que3', 'is_present_both', 'que4_ans1', 'que5_ans1', 'que6_ans1',
                                                             'que7_ans1', 'que8_ans1', 'que9_ans1', 'que10_ans1', 'que11_ans1', 'q12_ans1', 'que4_ans2', 'que5_ans2', 'que6_ans2', 'que7_ans2',
                                                              'que8_ans2', 'que9_ans2', 'que10_ans2', 'que11_ans2', 'q12_ans2')
    l2_prod = l2_production.objects.filter(qid_id=id).values('id', 'que1', 'que2', 'que2_1', 'que3', 'is_present_both', 'que4_ans1', 'que5_ans1', 'que6_ans1', 'que7_ans1',
                                                             'que8_ans1', 'que9_ans1', 'que10_ans1', 'que11_ans1', 'q12_ans1', 'que4_ans2', 'que5_ans2', 'que6_ans2', 'que7_ans2', 'que8_ans2',
                                                             'que9_ans2', 'que10_ans2', 'que11_ans2', 'q12_ans2')

    df1 = pd.DataFrame(l1_prod).fillna('null')
    df2 = pd.DataFrame(l2_prod).fillna('null')

    if not df1.empty and not df2.empty:

        fields_to_compare = ['que1', 'que2', 'que2_1', 'que3', 'is_present_both', 'que4_ans1', 'que5_ans1', 'que6_ans1', 'que7_ans1', 'que8_ans1', 'que9_ans1', 'que10_ans1', 'que11_ans1',
                             'q12_ans1', 'que4_ans2', 'que5_ans2', 'que6_ans2', 'que7_ans2', 'que8_ans2', 'que9_ans2', 'que10_ans2', 'que11_ans2', 'q12_ans2'
                             ]

        l1id = int(df1['id'].item())
        l2id = int(df2['id'].item())

        if l1id:
            l1_prod_link = l1_production_link.objects.filter(
                production_id=l1id).values('linkfor', 'link')
        else:
            l1_prod_link = []
        if l2id:
            l2_prod_link = l2_production_link.objects.filter(
                production_id=l2id).values('linkfor', 'link')
        else:
            l2_prod_link = []

        result_list = []
        for field in fields_to_compare:
            # print(df1[field],"===========", df2[field])
            comparison_result = 'Matched' if (
                df1[field] == df2[field]).all() else 'Not Matched'
            result_list.append(
                {'Field': field, 'Comparison': comparison_result, 'DA2ans': str(df2[field].item())})

        result_df = pd.DataFrame(result_list)

        l2_generalcommndas = l2_production.objects.filter(qid_id=id).values('general_ques1','general_ques2','general_ques2_2','general_ques3','annotation_comment')[0]

        datas = {'result': result_df, 'l1_prod_link': l1_prod_link,
                 'l2_prod_link': l2_prod_link,'l2gencomds':l2_generalcommndas}
        return datas
    else:
        return False


@loginrequired
def lthreeproductionView(request):
    EmpID = request.session.get('empId')
    language = request.session.get('language')
    location = request.session.get('location')
    if request.method == "POST":
        key = request.POST.get('key', None)
        eid = request.POST.get('eid', None)
        q1 = request.POST.get('q1', None)
        q2 = request.POST.get('q2', None)
        q2_1 = request.POST.get('q2_1', None)
        is_present_both = request.POST.get('is_present_both', None)
        q3 = request.POST.get('q3', None)
        q4_1 = request.POST.get('q4_1', None)
        q4_a_1 = request.POST.get('q4_a_1', None)
        q5_1 = request.POST.get('q5_1', None)
        q6_other_1 = request.POST.get('q6_other_1', None)
        q7_1 = request.POST.get('q7_1', None)
        q7_other_1 = request.POST.getlist('q7_other_1[]', [])
        q8_1 = request.POST.get('q8_1', None)
        q9_1 = request.POST.get('q9_1', None)
        q10_1 = request.POST.get('q10_1', None)
        q11_1 = request.POST.get('q11_1', None)
        q12_1 = request.POST.get('q12_1', None)
        q4_2 = request.POST.get('q4_2', None)
        q4_a_2 = request.POST.get('q4_a_2', None)
        q5_2 = request.POST.get('q5_2', None)
        q6_other_2 = request.POST.get('q6_other_2', None)
        q7_2 = request.POST.get('q7_2', None)
        q7_other_2 = request.POST.getlist('q7_other_2[]', [])
        q8_2 = request.POST.get('q8_2', None)
        q9_2 = request.POST.get('q9_2', None)
        q10_2 = request.POST.get('q10_2', None)
        q11_2 = request.POST.get('q11_2', None)
        q12_2 = request.POST.get('q12_2', None)
        annot_commant = request.POST.get('annot_commant', None)
        general_que1 = request.POST.get('general_que1', None)
        general_que2 = request.POST.get('general_que2', None)
        general_que2_2 = request.POST.get('general_que2_2', None)
        general_que3 = request.POST.get('general_que3', None)
        start_time = request.POST.get('start_time')
        if key == 'submit':
            try:
                with transaction.atomic():
                    pass

                    l3prod = l3_production.objects.filter(qid_id=eid)
                    l3prod.update(end_time=timezone.now(), que1=q1, que2=q2, que2_1=q2_1, que3=q3, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, q12_ans1=q12_1, que4_ans2=q4_2, que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, q12_ans2=q12_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, general_ques2_2=general_que2_2, general_ques3=general_que3, created_by_id=EmpID)
                    l3prod_values = l3prod.values_list('id', flat=True)

                    link_objects = [
                        QcQa_production_link(
                            l3production_id=l3prod_values, link=value, linkfor='q7_1', prodtype='QC')
                        for value in q7_other_1 if value
                    ] + [
                        QcQa_production_link(
                            l3production_id=l3prod_values, link=value, linkfor='q7_2', prodtype='QC')
                        for value in q7_other_2 if value
                    ]
                    with transaction.atomic():
                        QcQa_production_link.objects.bulk_create(link_objects)

                responseData = {'status': 'success',
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l3_prod_id=l3prod.values_list('id'),
                                                           l3_status='completed', l3_emp_id=EmpID)
            except Exception as er:
                print(er)
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

        elif key == 'submit_close':
            try:
                with transaction.atomic():
                    l3prod = l3_production.objects.filter(qid_id=eid)

                    l3prod.update(end_time=timezone.now(), que1=q1, que2=q2, que2_1=q2_1, que3=q3, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, q12_ans1=q12_1, que4_ans2=q4_2, que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, q12_ans2=q12_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, general_ques2_2=general_que2_2, general_ques3=general_que3, created_by_id=EmpID)

                l3prod_values = l3prod.values_list('id', flat=True)

                link_objects = [
                    QcQa_production_link(
                        l3production_id=l3prod_values, link=value, linkfor='q7_1', prodtype='QC')
                    for value in q7_other_1 if value
                ] + [
                    QcQa_production_link(
                        l3production_id=l3prod_values, link=value, linkfor='q7_2', prodtype='QC')
                    for value in q7_other_2 if value
                ]
                with transaction.atomic():
                    QcQa_production_link.objects.bulk_create(link_objects)

                redirect_url = '/'
                responseData = {'status': 'success', 'redirect_url': redirect_url,
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l3_prod_id=l3prod.values_list('id'),
                                                           l3_status='completed', l3_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        else:
            try:
                with transaction.atomic():
                    l3prod = l3_production.objects.filter(qid_id=eid)
                    l3prod.update(end_time=timezone.now(), que1=q1, que2=q2, que2_1=q2_1, que3=q3, annotation_comment=annot_commant, is_status=1, is_present_both=is_present_both, que4_ans1=q4_1, que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, q12_ans1=q12_1, que4_ans2=q4_2, que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, q12_ans2=q12_2, is_production_status='Completed', general_ques1=general_que1, general_ques2=general_que2, general_ques2_2=general_que2_2, general_ques3=general_que3, created_by_id=EmpID)

                responseData = {'status': 'success',
                                'result': "Production  Hold"}
                if eid:
                    raw_data.objects.filter(id=eid).update(
                        l3_status='hold', l3_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

    else:
        l3_count = raw_data.objects.filter(Q(l3_status='completed') & Q(l3_emp_id=EmpID)).exclude(status__in=['hold', 'deleted']).count()
        if l3_count is not None:
            l3_count = l3_count
        else:
            l3_count = 0
        try:
            query = Q()
            if language:
                query = Q(baseid_id__language__in=language)

            with transaction.atomic():
                rawData = raw_data.objects.select_for_update(skip_locked=True).filter(Q(l1_status='completed') & Q(l2_status='completed') & query, (Q(l3_status='not_moved') & Q(l3_emp_id__isnull=True)) | (Q(l3_status='picked') & Q(l3_emp_id=EmpID)),
                    (Q(l1_l2_accuracy__isnull=True) | Q(l1_l2_accuracy='fail'))).values('id', 'id_value', 'question', 'asin', 'title', 'product_url', 'imagepath', 'evidence', 'answer_one', 'answer_two').exclude(l1_emp_id=EmpID, l2_emp_id=EmpID, status__in=['hold', 'deleted'],l1_l2_accuracy='pass').order_by('-l3_status').first()

            if rawData:                
                l3comp = l1_l2Comparison(rawData['id'])
                if l3comp:
                    l3input = l3comp['result']
                    l3link = l3comp
                    if 'Not Matched' in l3input['Comparison'].values:
                        l1_l2_accuracy = 'fail'

                        l3prod = l3_production.objects                        
                        if l3prod.filter(qid_id=rawData['id']).exists():
                            l3_production.objects.filter(qid_id=rawData['id']).update(start_time = timezone.now())
                        else:
                            prodid = l3_production.objects.create(qid_id=rawData['id'], start_time = timezone.now())                        
                            raw_data.objects.filter(id=rawData['id']).update(
                                l3_status='picked', l3_emp_id=EmpID, l1_l2_accuracy=l1_l2_accuracy,l3_prod_id=prodid.id)
                        
                        l3dict = json.dumps(l3input.to_dict(orient='records'))
                        return render(request, 'pages/l3_production.html', {'start_time': timezone.now(),'l3_count': l3_count, 'result': rawData, 'status': l3dict, 'l1_prod_link': l3link['l1_prod_link'], 'l2_prod_link': l3link['l2_prod_link'],'gencomds':l3comp['l2gencomds']})
                    else:
                        l1_l2_accuracy = 'pass'
                        raw_data.objects.filter(id=rawData['id']).update(l1_l2_accuracy = l1_l2_accuracy)
                        return redirect('/api/v5/productionl3/')
            return render(request, 'pages/l3_production.html', {'l3_count': l3_count, 'result': []})
        except Exception as er:
            print(er)
            rawData = []
        return render(request, 'pages/l3_production.html', {'l3_count': l3_count, 'result': rawData})


@loginrequired
def lfourproductionView(request):
    EmpID = request.session.get('empId')
    language = request.session.get('language')
    location = request.session.get('location')
    if request.method == "POST":
        key = request.POST.get('key', None)
        eid = request.POST.get('eid', None)
        q1 = request.POST.get('q1', None)
        q2 = request.POST.get('q2', None)
        q2_1 = request.POST.get('q2_1', None)
        is_present_both = request.POST.get('is_present_both', None)
        q3 = request.POST.get('q3', None)
        q4_1 = request.POST.get('q4_1', None)        
        q5_1 = request.POST.get('q5_1', None)
        q6_other_1 = request.POST.get('q6_other_1', None)
        q7_1 = request.POST.get('q7_1', None)
        q7_other_1 = request.POST.getlist('q7_other_1[]', [])
        q8_1 = request.POST.get('q8_1', None)
        q9_1 = request.POST.get('q9_1', None)
        q10_1 = request.POST.get('q10_1', None)
        q11_1 = request.POST.get('q11_1', None)
        q12_1 = request.POST.get('q12_1', None)
        q4_2 = request.POST.get('q4_2', None)        
        q5_2 = request.POST.get('q5_2', None)
        q6_other_2 = request.POST.get('q6_other_2', None)
        q7_2 = request.POST.get('q7_2', None)
        q7_other_2 = request.POST.getlist('q7_other_2[]', [])
        q8_2 = request.POST.get('q8_2', None)
        q9_2 = request.POST.get('q9_2', None)
        q10_2 = request.POST.get('q10_2', None)
        q11_2 = request.POST.get('q11_2', None)
        q12_2 = request.POST.get('q12_2', None)
        annot_commant = request.POST.get('annot_commant', None)
        general_que1 = request.POST.get('general_que1', None)
        general_que2 = request.POST.get('general_que2', None)
        general_que2_2 = request.POST.get('general_que2_2', None)
        general_que3 = request.POST.get('general_que3', None)
        start_time = request.POST.get('start_time')
        
        if key == 'submit':
            try:
                with transaction.atomic():
                    l4prod = l4_production.objects.filter(qid_id=eid)
                    l4prod.update(end_time=timezone.now(), que1=q1, que2=q2, que2_1=q2_1, que3=q3, annotation_comment=annot_commant, is_present_both=is_present_both, que4_ans1=q4_1, que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, q12_ans1=q12_1, que4_ans2=q4_2, que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, q12_ans2=q12_2, general_ques1=general_que1, general_ques2=general_que2, general_ques2_2=general_que2_2, general_ques3=general_que3, created_by_id=EmpID)

                l4prod_values = l4prod.values_list('id', flat=True)
                link_objects = [
                    QcQa_production_link(
                        l4production_id=l4prod_values, link=value, linkfor='q7_1', prodtype='QA')
                    for value in q7_other_1 if value
                ] + [
                    QcQa_production_link(
                        l4production_id=l4prod_values, link=value, linkfor='q7_2', prodtype='QA')
                    for value in q7_other_2 if value
                ]
                with transaction.atomic():
                    QcQa_production_link.objects.bulk_create(link_objects)

                responseData = {'status': 'success',
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l4_prod_id=l4prod.values_list('id'),
                                                           l4_status='completed', l4_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

        elif key == 'submit_close':
            try:
                with transaction.atomic():
                    l4prod = l4_production.objects.filter(qid_id=eid)
                    l4prod.update(end_time=timezone.now(), que1=q1, que2=q2, que2_1=q2_1, que3=q3, annotation_comment=annot_commant,  is_present_both=is_present_both, que4_ans1=q4_1, que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, q12_ans1=q12_1, que4_ans2=q4_2,  que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, q12_ans2=q12_2, general_ques1=general_que1, general_ques2=general_que2, general_ques2_2=general_que2_2, general_ques3=general_que3, created_by_id=EmpID)

                l4prod_values = l4prod.values_list('id', flat=True)
                link_objects = [
                    QcQa_production_link(
                        l4production_id=l4prod_values, link=value, linkfor='q7_1', prodtype='QA')
                    for value in q7_other_1 if value
                ] + [
                    QcQa_production_link(
                        l4production_id=l4prod_values, link=value, linkfor='q7_2', prodtype='QA')
                    for value in q7_other_2 if value
                ]
                with transaction.atomic():
                    QcQa_production_link.objects.bulk_create(link_objects)

                redirect_url = '/'
                responseData = {'status': 'success', 'redirect_url': redirect_url,
                                'result': "Production Completed"}
                if eid:
                    raw_data.objects.filter(id=eid).update(l4_prod_id=l4prod.values_list('id'),
                                                           l4_status='completed', l4_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)
        else:
            try:
                with transaction.atomic():
                    l4prod = l4_production.objects.filter(qid_id=eid)
                    l4prod.update(end_time=timezone.now(), que1=q1, que2=q2, que2_1=q2_1, que3=q3, annotation_comment=annot_commant, is_present_both=is_present_both, que4_ans1=q4_1, que5_ans1=q5_1, que6_ans1=q6_other_1, que7_ans1=q7_1, que8_ans1=q8_1, que9_ans1=q9_1,
                                  que10_ans1=q10_1, que11_ans1=q11_1, q12_ans1=q12_1, que4_ans2=q4_2, que5_ans2=q5_2, que6_ans2=q6_other_2, que7_ans2=q7_2, que8_ans2=q8_2, que9_ans2=q9_2, que10_ans2=q10_2, que11_ans2=q11_2, q12_ans2=q12_2, general_ques1=general_que1, general_ques2=general_que2,general_ques2_2=general_que2_2, general_ques3=general_que3, created_by_id=EmpID)

                responseData = {'status': 'success',
                                'result': "Production  Hold"}
                if eid:
                    raw_data.objects.filter(id=eid).update(
                        l4_status='hold', l4_emp_id=EmpID)
            except Exception as er:
                responseData = {'status': 'failed', 'result': str(er)}
            return JsonResponse(responseData)

    else:
        l4_count = raw_data.objects.filter(Q(l4_status='completed') & Q(l4_emp_id=EmpID)).exclude(status__in=['hold', 'deleted']).count()
        if l4_count is not None:
            l4_count = l4_count
        else:
            l4_count = 0
        try:
            query = Q()
            if language:
                query = Q(baseid_id__language__in=language)

            with transaction.atomic():                
                rawData = raw_data.objects.select_for_update(skip_locked=True).filter(Q(l1_status='completed') & Q(l2_status='completed') & query, (Q(l4_status='not_picked') & Q(l4_emp_id__isnull=True) | Q(l4_status='picked') & Q(l4_emp_id=EmpID)),
                    (Q(l1_l2_accuracy__isnull=True) | Q(l1_l2_accuracy='pass'))).values('id', 'id_value', 'question', 'asin', 'title', 'product_url', 'imagepath', 'evidence', 'answer_one', 'answer_two').exclude(l1_emp_id=EmpID, l2_emp_id=EmpID, status__in=['hold', 'deleted'],l1_l2_accuracy='fail').order_by('-l4_status').first()

            if rawData:                
                l4comp = l1_l2Comparison(rawData['id'])
                if l4comp:
                    l4input = l4comp['result']

                    if 'Not Matched' in l4input['Comparison'].values:
                        l1_l2_accuracy = 'fail'
                        raw_data.objects.filter(id=rawData['id']).update(l1_l2_accuracy = l1_l2_accuracy)
                        return redirect('/api/v5/productionl4/')
                    else:
                        l1_l2_accuracy = 'pass'

                        l4prod = l4_production.objects                        
                        if l4prod.filter(qid_id=rawData['id']).exists():
                            l4_production.objects.filter(qid_id=rawData['id']).update(start_time = timezone.now())
                        else:
                            prodid = l4_production.objects.create(qid_id=rawData['id'], start_time = timezone.now())
                        
                            raw_data.objects.filter(id=rawData['id']).update(
                                l4_status='picked', l4_emp_id=EmpID, l1_l2_accuracy=l1_l2_accuracy,l4_prod_id=prodid.id)
                        l4dict = json.dumps(l4input.to_dict(orient='records'))
                        return render(request, 'pages/l4_production.html', {'start_time': timezone.now(), 'l4_count': l4_count, 'result': rawData, 'status': l4dict, 'l1_prod_link': l4comp['l1_prod_link'], 'l2_prod_link': l4comp['l2_prod_link'],'gencomds':l4comp['l2gencomds']})
            return render(request, 'pages/l4_production.html', {'l4_count': l4_count, 'result': []})
        except Exception as er:
            print(er)
            rawData = []
        return render(request, 'pages/l4_production.html', {'l4_count': l4_count, 'result': rawData})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @login_required(login_url="/")
@loginrequired
def outputDownload(request):
    # EmpLoc = request.session.get('empLoc') Location/area wise filter
    # ,Q(created_by_id__location = EmpLoc)
    filenames = raw_data.objects.values('baseid_id__filename').distinct()
    
    if request.method == 'POST':
        key = request.POST.get('key')        

        filename = request.POST.get('filename')        
        fromdate = request.POST.get('fromDate')
        todate = request.POST.get('toDate')
        reporttype = request.POST.get('reporttype')
        language = request.POST.get('language')
        # location = request.POST.get('location')
                    
        if language == 'All':
            query = Q()
        else:
            query = Q(baseid_id__language=language)

        try:
            if fromdate and todate:
                conditions1 = Q(l1_prod_id__end_time__range=(fromdate, todate))
                conditions2 = Q(l2_prod_id__end_time__range=(fromdate, todate))
                conditions3 = Q(l3_prod_id__end_time__range=(fromdate, todate))
                conditions4 = Q(l4_prod_id__end_time__range=(fromdate, todate))
            else:
                conditions1 = Q()
                conditions2 = Q()
                conditions3 = Q()
                conditions4 = Q()

            dL1raw = raw_data.objects.filter(conditions1 & query, l1_status='completed').annotate(timtakn=Sum(F('l1_prod_id__end_time') - F('l1_prod_id__start_time'))).values('id','l1_prod_id__end_time__date', 'id_value', 'l1_prod_id', 'l1_emp_id__employeeID', 'question', 'asin' , 'product_url' , 'title' , 'evidence' , 'imagepath', 'answer_one', 'answer_two', 'l1_prod_id__general_ques1', 'l1_prod_id__general_ques2','l1_prod_id__general_ques2_2', 'l1_prod_id__general_ques3', 'l1_prod_id__start_time', 'l1_prod_id__end_time',
                                                                                                                                                                    'l1_emp_id__employeeName', 'l1_emp_id__location', 'baseid_id__batch_name', 'baseid_id__filename', 'l1_status', 'timtakn', 'l1_prod_id__que1', 'l1_prod_id__que2', 'l1_prod_id__que2_1', 'l1_prod_id__que3', 'l1_prod_id__annotation_comment', 'l1_prod_id__is_status', 'l1_prod_id__is_present_both', 'l1_prod_id__que4_ans1', 'l1_prod_id__que5_ans1',
                                                                                                                                                                    'l1_prod_id__que6_ans1', 'l1_prod_id__que7_ans1', 'l1_prod_id__que8_ans1', 'l1_prod_id__que9_ans1', 'l1_prod_id__que10_ans1', 'l1_prod_id__que11_ans1', 'l1_prod_id__q12_ans1', 'l1_prod_id__que4_ans2', 'l1_prod_id__que5_ans2', 'l1_prod_id__que6_ans2', 'l1_prod_id__que7_ans2',
                                                                                                                                                                    'l1_prod_id__que8_ans2', 'l1_prod_id__que9_ans2', 'l1_prod_id__que10_ans2', 'l1_prod_id__que11_ans2', 'l1_prod_id__q12_ans2').exclude(status__in=['hold', 'deleted'])        
            l1prodid = dL1raw.values_list('l1_prod_id', flat=True)
            dL1link = l1_production_link.objects.filter(
                production_id__in=l1prodid).values('production_id', 'linkfor', 'link')

            dL2raw = raw_data.objects.filter(conditions2 & query, l2_status='completed').annotate(timtakn=Sum(F('l2_prod_id__end_time') - F('l2_prod_id__start_time'))).values('id','l2_prod_id__end_time__date', 'id_value', 'l2_prod_id', 'l2_emp_id__employeeID', 'question', 'asin' , 'product_url' , 'title' , 'evidence' , 'imagepath', 'answer_one', 'answer_two', 'l2_prod_id__general_ques1', 'l2_prod_id__general_ques2','l2_prod_id__general_ques2_2', 'l2_prod_id__general_ques3', 'l2_prod_id__start_time', 'l2_prod_id__end_time',
                                                                                                                                                                    'l2_emp_id__employeeName', 'l2_emp_id__location', 'baseid_id__batch_name', 'baseid_id__filename', 'l2_status', 'timtakn', 'l2_prod_id__que1', 'l2_prod_id__que2', 'l2_prod_id__que2_1', 'l2_prod_id__que3', 'l2_prod_id__annotation_comment', 'l2_prod_id__is_status', 'l2_prod_id__is_present_both', 'l2_prod_id__que4_ans1', 'l2_prod_id__que5_ans1',
                                                                                                                                                                    'l2_prod_id__que6_ans1', 'l2_prod_id__que7_ans1', 'l2_prod_id__que8_ans1', 'l2_prod_id__que9_ans1', 'l2_prod_id__que10_ans1', 'l2_prod_id__que11_ans1', 'l2_prod_id__q12_ans1', 'l2_prod_id__que4_ans2', 'l2_prod_id__que5_ans2', 'l2_prod_id__que6_ans2', 'l2_prod_id__que7_ans2', 
                                                                                                                                                                    'l2_prod_id__que8_ans2', 'l2_prod_id__que9_ans2', 'l2_prod_id__que10_ans2', 'l2_prod_id__que11_ans2', 'l2_prod_id__q12_ans2').exclude(status__in=['hold', 'deleted'])
            l2prodid = dL2raw.values_list('l2_prod_id', flat=True)
            dL2link = l2_production_link.objects.filter(
                production_id__in=l2prodid).values('production_id', 'linkfor', 'link')

            dL3raw = raw_data.objects.filter(conditions3 & query, l3_status='completed').annotate(timtakn=Sum(F('l3_prod_id__end_time') - F('l3_prod_id__start_time'))).values('id','l3_prod_id__end_time__date', 'id_value', 'l3_prod_id', 'l3_emp_id__employeeID', 'question', 'asin' , 'product_url' , 'title' , 'evidence' , 'imagepath', 'answer_one', 'answer_two', 'l3_prod_id__general_ques1', 'l3_prod_id__general_ques2','l3_prod_id__general_ques2_2', 'l3_prod_id__general_ques3', 'l3_prod_id__start_time', 'l3_prod_id__end_time',
                                                                                                                                                                    'l3_emp_id__employeeName', 'l3_emp_id__location', 'baseid_id__batch_name', 'baseid_id__filename', 'l3_status', 'timtakn', 'l3_prod_id__que1', 'l3_prod_id__que2', 'l3_prod_id__que2_1', 'l3_prod_id__que3', 'l3_prod_id__annotation_comment', 'l3_prod_id__is_status', 'l3_prod_id__is_present_both', 'l3_prod_id__que4_ans1', 'l3_prod_id__que5_ans1',
                                                                                                                                                                    'l3_prod_id__que6_ans1', 'l3_prod_id__que7_ans1', 'l3_prod_id__que8_ans1', 'l3_prod_id__que9_ans1', 'l3_prod_id__que10_ans1', 'l3_prod_id__que11_ans1', 'l3_prod_id__q12_ans1', 'l3_prod_id__que4_ans2', 'l3_prod_id__que5_ans2', 'l3_prod_id__que6_ans2', 'l3_prod_id__que7_ans2', 
                                                                                                                                                                    'l3_prod_id__que8_ans2', 'l3_prod_id__que9_ans2', 'l3_prod_id__que10_ans2', 'l3_prod_id__que11_ans2', 'l3_prod_id__q12_ans2').exclude(status__in=['hold', 'deleted'])
            l3prodid = dL3raw.values_list('l3_prod_id', flat=True)
            dL3link = QcQa_production_link.objects.filter(
                l3production_id__in=l3prodid).values('l3production_id', 'linkfor', 'link')

            dL4raw = raw_data.objects.filter(conditions4 & query,l1_l2_accuracy='pass').annotate(timtakn=Sum(F('l4_prod_id__end_time') - F('l4_prod_id__start_time'))).values('id','l4_prod_id__end_time__date', 'id_value', 'l4_prod_id', 'l4_emp_id__employeeID', 'question', 'asin' , 'product_url' , 'title' , 'evidence' , 'imagepath', 'answer_one', 'answer_two', 'l4_prod_id__general_ques1', 'l4_prod_id__general_ques2','l4_prod_id__general_ques2_2', 'l4_prod_id__general_ques3', 'l4_prod_id__start_time', 'l4_prod_id__end_time',
                                                                                                                                                                    'l4_emp_id__employeeName', 'l4_emp_id__location', 'baseid_id__batch_name', 'baseid_id__filename', 'l4_status', 'timtakn', 'l4_prod_id__que1', 'l4_prod_id__que2', 'l4_prod_id__que2_1', 'l4_prod_id__que3', 'l4_prod_id__annotation_comment', 'l4_prod_id__is_status', 'l4_prod_id__is_present_both', 'l4_prod_id__que4_ans1', 'l4_prod_id__que5_ans1',
                                                                                                                                                                    'l4_prod_id__que6_ans1', 'l4_prod_id__que7_ans1', 'l4_prod_id__que8_ans1', 'l4_prod_id__que9_ans1', 'l4_prod_id__que10_ans1', 'l4_prod_id__que11_ans1', 'l4_prod_id__q12_ans1', 'l4_prod_id__que4_ans2', 'l4_prod_id__que5_ans2', 'l4_prod_id__que6_ans2', 'l4_prod_id__que7_ans2',
                                                                                                                                                                    'l4_prod_id__que8_ans2', 'l4_prod_id__que9_ans2', 'l4_prod_id__que10_ans2', 'l4_prod_id__que11_ans2', 'l4_prod_id__q12_ans2').exclude(status__in=['hold', 'deleted'])
            l4prodid = dL4raw.values_list('l4_prod_id', flat=True)
            dL4link = QcQa_production_link.objects.filter(
                l4production_id__in=l4prodid).values('l4production_id', 'linkfor', 'link')

            if key == 'Download':
                response = HttpResponse(content_type='text/csv;charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="' + \
                    reporttype+"|"+str(timezone.now().date())+'".csv"'
                writer = csv.writer(response)

                if reporttype in ['DA1', 'DA2', 'QC/QA']:                    
                    writer.writerow(title)

                if reporttype == 'DA1':
                    for v in dL1raw:
                        records = [
                            'DA1',
                            v['baseid_id__batch_name'],
                            v['baseid_id__filename'],
                            v['id_value'],
                            v['asin'],
                            v['product_url'],
                            v['title'],
                            v['evidence'],
                            v['imagepath'],                            
                            v['question'],
                            v['answer_one'],
                            v['answer_two'],

                            v['l1_prod_id__que1'],
                            v['l1_prod_id__que2'],
                            v['l1_prod_id__que2_1'],
                            v['l1_prod_id__is_present_both'],

                            v['l1_prod_id__que4_ans1'],
                            v['l1_prod_id__que5_ans1'],
                            v['l1_prod_id__que6_ans1'],
                            v['l1_prod_id__que7_ans1'],
                            " | ".join([i['link'] for i in dL1link if i['linkfor']
                                    == 'q7_1' and i['production_id'] == v['l1_prod_id']]),
                            v['l1_prod_id__que8_ans1'],
                            v['l1_prod_id__que9_ans1'],
                            v['l1_prod_id__que10_ans1'],
                            v['l1_prod_id__que11_ans1'],
                            v['l1_prod_id__q12_ans1'],

                            v['l1_prod_id__que4_ans2'],
                            v['l1_prod_id__que5_ans2'],
                            v['l1_prod_id__que6_ans2'],
                            v['l1_prod_id__que7_ans2'],
                            " | ".join([i['link'] for i in dL1link if i['linkfor']
                                    == 'q7_2' and i['production_id'] == v['l1_prod_id']]),
                            v['l1_prod_id__que8_ans2'],
                            v['l1_prod_id__que9_ans2'],
                            v['l1_prod_id__que10_ans2'],
                            v['l1_prod_id__que11_ans2'],
                            v['l1_prod_id__q12_ans2'],
                            v['l1_prod_id__que3'],

                            str(v['l1_prod_id__general_ques1']).strip(
                                "[]") if v['l1_prod_id__general_ques1'] is not None else None,
                            v['l1_prod_id__general_ques2'],
                            v['l1_prod_id__general_ques2_2'],
                            v['l1_prod_id__general_ques3'],

                            v['l1_prod_id__annotation_comment'],

                            v['l1_emp_id__employeeID'],
                            v['l1_emp_id__employeeName'],
                            v['l1_emp_id__location'],
                            v['l1_prod_id__start_time'],
                            v['l1_prod_id__end_time'],
                            v['timtakn'],
                            v['l1_prod_id__end_time__date']
                        ]
                        writer.writerow(records)

                if reporttype == 'DA2':
                    for v in dL2raw:
                        records = [
                            'DA2',
                            v['baseid_id__batch_name'],
                            v['baseid_id__filename'],
                            v['id_value'],
                            v['asin'],
                            v['product_url'],
                            v['title'],
                            v['evidence'],
                            v['imagepath'],                            
                            v['question'],                           
                            v['answer_one'],
                            v['answer_two'],

                            v['l2_prod_id__que1'],
                            v['l2_prod_id__que2'],
                            v['l2_prod_id__que2_1'],
                            v['l2_prod_id__is_present_both'],

                            v['l2_prod_id__que4_ans1'],
                            v['l2_prod_id__que5_ans1'],
                            v['l2_prod_id__que6_ans1'],
                            v['l2_prod_id__que7_ans1'],
                            " | ".join([i['link'] for i in dL2link if i['linkfor']
                                    == 'q7_1' and i['production_id'] == v['l2_prod_id']]),
                            v['l2_prod_id__que8_ans1'],
                            v['l2_prod_id__que9_ans1'],
                            v['l2_prod_id__que10_ans1'],
                            v['l2_prod_id__que11_ans1'],
                            v['l2_prod_id__q12_ans1'],

                            v['l2_prod_id__que4_ans2'],
                            v['l2_prod_id__que5_ans2'],
                            v['l2_prod_id__que6_ans2'],
                            v['l2_prod_id__que7_ans2'],
                            " | ".join([i['link'] for i in dL2link if i['linkfor']
                                    == 'q7_2' and i['production_id'] == v['l2_prod_id']]),
                            v['l2_prod_id__que8_ans2'],
                            v['l2_prod_id__que9_ans2'],
                            v['l2_prod_id__que10_ans2'],
                            v['l2_prod_id__que11_ans2'],
                            v['l2_prod_id__q12_ans2'],
                            v['l2_prod_id__que3'],

                            str(v['l2_prod_id__general_ques1']).strip(
                                "[]") if v['l2_prod_id__general_ques1'] is not None else None,
                            v['l2_prod_id__general_ques2'],
                            v['l2_prod_id__general_ques2_2'],
                            v['l2_prod_id__general_ques3'],

                            v['l2_prod_id__annotation_comment'],

                            v['l2_emp_id__employeeID'],
                            v['l2_emp_id__employeeName'],
                            v['l2_emp_id__location'],
                            v['l2_prod_id__start_time'],
                            v['l2_prod_id__end_time'],
                            v['timtakn'],
                            v['l2_prod_id__end_time__date']
                        ]
                        writer.writerow(records)

                if reporttype == 'QC/QA':
                    for v in dL3raw:
                        records = [
                            'QC',
                            v['baseid_id__batch_name'],
                            v['baseid_id__filename'],
                            v['id_value'],
                            v['asin'],
                            v['product_url'],
                            v['title'],
                            v['evidence'],
                            v['imagepath'],                            
                            v['question'],                           
                            v['answer_one'],
                            v['answer_two'],

                            v['l3_prod_id__que1'],
                            v['l3_prod_id__que2'],
                            v['l3_prod_id__que2_1'],
                            v['l3_prod_id__is_present_both'],

                            v['l3_prod_id__que4_ans1'],
                            v['l3_prod_id__que5_ans1'],
                            v['l3_prod_id__que6_ans1'],
                            v['l3_prod_id__que7_ans1'],
                            " | ".join([i['link'] for i in dL3link if i['linkfor']
                                    == 'q7_1' and i['l3production_id'] == v['l3_prod_id']]),
                            v['l3_prod_id__que8_ans1'],
                            v['l3_prod_id__que9_ans1'],
                            v['l3_prod_id__que10_ans1'],
                            v['l3_prod_id__que11_ans1'],
                            v['l3_prod_id__q12_ans1'],

                            v['l3_prod_id__que4_ans2'],
                            v['l3_prod_id__que5_ans2'],
                            v['l3_prod_id__que6_ans2'],
                            v['l3_prod_id__que7_ans2'],
                            " | ".join([i['link'] for i in dL3link if i['linkfor']
                                    == 'q7_2' and i['l3production_id'] == v['l3_prod_id']]),
                            v['l3_prod_id__que8_ans2'],
                            v['l3_prod_id__que9_ans2'],
                            v['l3_prod_id__que10_ans2'],
                            v['l3_prod_id__que11_ans2'],
                            v['l3_prod_id__q12_ans2'],
                            v['l3_prod_id__que3'],

                            str(v['l3_prod_id__general_ques1']).strip(
                                "[]") if v['l3_prod_id__general_ques1'] is not None else None,
                            v['l3_prod_id__general_ques2'],
                            v['l3_prod_id__general_ques2_2'],
                            v['l3_prod_id__general_ques3'],

                            v['l3_prod_id__annotation_comment'],

                            v['l3_emp_id__employeeID'],
                            v['l3_emp_id__employeeName'],
                            v['l3_emp_id__location'],
                            v['l3_prod_id__start_time'],
                            v['l3_prod_id__end_time'],
                            v['timtakn'],
                            v['l3_prod_id__end_time__date']
                        ]
                        writer.writerow(records)

                    for v in dL4raw:
                        records = [
                            'QA',
                            v['baseid_id__batch_name'],
                            v['baseid_id__filename'],
                            v['id_value'],
                            v['asin'],
                            v['product_url'],
                            v['title'],
                            v['evidence'],
                            v['imagepath'],                            
                            v['question'],                         
                            v['answer_one'],
                            v['answer_two'],

                            v['l4_prod_id__que1'],
                            v['l4_prod_id__que2'],
                            v['l4_prod_id__que2_1'],
                            v['l4_prod_id__is_present_both'],

                            v['l4_prod_id__que4_ans1'],
                            v['l4_prod_id__que5_ans1'],
                            v['l4_prod_id__que6_ans1'],
                            v['l4_prod_id__que7_ans1'],
                            " | ".join([i['link'] for i in dL4link if i['linkfor']
                                    == 'q7_1' and i['l4production_id'] == v['l4_prod_id']]),
                            v['l4_prod_id__que8_ans1'],
                            v['l4_prod_id__que9_ans1'],
                            v['l4_prod_id__que10_ans1'],
                            v['l4_prod_id__que11_ans1'],
                            v['l4_prod_id__q12_ans1'],

                            v['l4_prod_id__que4_ans2'],
                            v['l4_prod_id__que5_ans2'],
                            v['l4_prod_id__que6_ans2'],
                            v['l4_prod_id__que7_ans2'],
                            " | ".join([i['link'] for i in dL4link if i['linkfor']
                                    == 'q7_2' and i['l4production_id'] == v['l4_prod_id']]),
                            v['l4_prod_id__que8_ans2'],
                            v['l4_prod_id__que9_ans2'],
                            v['l4_prod_id__que10_ans2'],
                            v['l4_prod_id__que11_ans2'],
                            v['l4_prod_id__q12_ans2'],
                            v['l4_prod_id__que3'],

                            str(v['l4_prod_id__general_ques1']).strip(
                                "[]") if v['l4_prod_id__general_ques1'] is not None else None,
                            v['l4_prod_id__general_ques2'],
                            v['l4_prod_id__general_ques2_2'],
                            v['l4_prod_id__general_ques3'],

                            v['l4_prod_id__annotation_comment'],

                            v['l4_emp_id__employeeID'],
                            v['l4_emp_id__employeeName'],
                            v['l4_emp_id__location'],
                            v['l4_prod_id__start_time'],
                            v['l4_prod_id__end_time'],
                            v['timtakn'],
                            v['l4_prod_id__end_time__date']
                        ]
                        writer.writerow(records)

                return response
        except Exception as er:
            print(er)
        return render(request, 'pages/outputDownload.html', {'filenames':filenames, 'dL1raw': dL1raw, 'dL2raw': dL2raw, 'dL3raw': dL3raw, 'dL4raw': dL4raw,'fromdate':fromdate,'toDate':todate,'language':language,'filename':filename})
    else:
        return render(request, 'pages/outputDownload.html',{'filenames':filenames})

@loginrequired
def ConsolidateOutput(request):
    fromdate = request.POST.get('fromDate')
    todate = request.POST.get('toDate')
    language = request.POST.get('language')
    key = request.POST.get('key')

    if language == 'All':
        query = Q()
    else:
        query = Q(baseid_id__language=language)

    if fromdate and todate:    
        conditions1 = Q(l1_prod_id__end_time__range=(fromdate, todate))
        conditions2 = Q(l2_prod_id__end_time__range=(fromdate, todate))
        conditions3 = Q(l3_prod_id__end_time__range=(fromdate, todate))
        conditions4 = Q(l4_prod_id__end_time__range=(fromdate, todate))
    else:
        conditions1 = Q()
        conditions2 = Q()
        conditions3 = Q()
        conditions4 = Q()
    try:
        status = Q()
        status &= Q(l1_status="completed")
        status &= Q(l2_status="completed")
        status |= Q(l3_status="completed")
        status |= Q(l1_l2_accuracy="pass")

        rawtable = raw_data.objects
        cons = rawtable.filter(conditions1 | conditions2 | conditions3 | conditions4 & status ,query).values(
            'id_value',
            'baseid_id__batch_name',
            'baseid_id__filename',
            'question',
            'asin',
            'product_url',
            'imagepath',
            'evidence',
            'answer_one',
            'answer_two',
            *l1list if rawtable.filter(conditions1 & Q(l1_status='completed')) else [],
            *l2list if rawtable.filter(conditions2 & Q(l2_status='completed')) else [],
            *l3list if rawtable.filter(conditions3 & Q(l3_status='completed')) else [],
            *l4list if rawtable.filter(conditions4 & Q(l1_l2_accuracy="pass")) else []
        ).exclude(status__in=['hold', 'deleted'])
        # print(cons.values('l1_prod_id__end_time__date','l2_prod_id__end_time__date','l3_prod_id__end_time__date','l4_prod_id__end_time__date'))

        cnstable = pd.DataFrame(cons)
        cnstable.fillna('')

        l1genq1 = 'l1_prod_id__general_ques1'
        l2genq1 = 'l2_prod_id__general_ques1'
        l3genq1 = 'l3_prod_id__general_ques1'
        l4genq1 = 'l4_prod_id__general_ques1'

        stat = []
        if l1genq1 in cnstable.columns:
            stat.append('l1_status')
            cnstable[l1genq1] = cnstable[l1genq1].apply(
                lambda x: x.strip("[]") if pd.notna(x) else x)

        if l2genq1 in cnstable.columns:
            stat.append('l2_status')
            cnstable[l2genq1] = cnstable[l2genq1].apply(
                lambda x: x.strip("[]") if pd.notna(x) else x)

        if l3genq1 in cnstable.columns:
            stat.append('l3_status')
            cnstable[l3genq1] = cnstable[l3genq1].apply(
                lambda x: x.strip("[]") if pd.notna(x) else x)

        if l4genq1 in cnstable.columns:
            stat.append('l4_status')
            cnstable[l4genq1] = cnstable[l4genq1].apply(
                lambda x: x.strip("[]") if pd.notna(x) else x)

        l1link = pd.DataFrame(l1_production_link.objects.filter(production_id__in=cons.values_list('l1_prod_id', flat=True)).values(
            'link', 'linkfor', id_value=F('production_id__qid_id__id_value'),batch=F('production_id__qid_id__baseid_id__batch_name'))).fillna('')
        l2link = pd.DataFrame(l2_production_link.objects.filter(production_id__in=cons.values_list('l2_prod_id', flat=True)).values(
            'link', 'linkfor', id_value=F('production_id__qid_id__id_value'),batch=F('production_id__qid_id__baseid_id__batch_name'))).fillna('')
        l3link = pd.DataFrame(QcQa_production_link.objects.filter(l3production_id__in=cons.values_list(
            'l3_prod_id', flat=True), prodtype='QC').values('prodtype', 'link', 'linkfor', id_value=F('l3production_id__qid_id__id_value'),batch=F('l3production_id__qid_id__baseid_id__batch_name'))).fillna('')
        l4link = pd.DataFrame(QcQa_production_link.objects.filter(l4production_id__in=cons.values_list(
            'l4_prod_id', flat=True), prodtype='QA').values('prodtype', 'link', 'linkfor', id_value=F('l4production_id__qid_id__id_value'),batch=F('l4production_id__qid_id__baseid_id__batch_name'))).fillna('')

        if not cnstable.empty:
            df_cleaned = cnstable.dropna(axis=1, how='all')
            df_cleaned['DA1-Total Time Taken'] = df_cleaned['l1_prod_id__end_time'] - df_cleaned['l1_prod_id__start_time'] if all(col in df_cleaned.columns for col in ['l1_prod_id__start_time', 'l1_prod_id__end_time']) else None
            df_cleaned['DA2-Total Time Taken'] = df_cleaned['l2_prod_id__end_time'] - df_cleaned['l2_prod_id__start_time'] if all(col in df_cleaned.columns for col in ['l2_prod_id__start_time', 'l2_prod_id__end_time']) else None
            df_cleaned['QC-Total Time Taken'] = df_cleaned['l3_prod_id__end_time'] - df_cleaned['l3_prod_id__start_time'] if all(col in df_cleaned.columns for col in ['l3_prod_id__start_time', 'l3_prod_id__end_time']) else None
            df_cleaned['QA-Total Time Taken'] = df_cleaned['l4_prod_id__end_time'] - df_cleaned['l4_prod_id__start_time'] if all(col in df_cleaned.columns for col in ['l4_prod_id__start_time', 'l4_prod_id__end_time']) else None
            # print(df_cleaned['l1_prod_id__start_time'],"==",  df_cleaned['l1_prod_id__end_time'],df_cleaned['l1_prod_id__end_time'] - df_cleaned['l1_prod_id__start_time'])
            mrgd = df_cleaned

        links = []
        keys = []
        if not l1link.empty:
            l1link['prodtype'] = 'DA1'
            links.append(l1link)
            keys.append('l1')

        if not l2link.empty:
            l2link['prodtype'] = 'DA2'
            links.append(l2link)
            keys.append('l2')

        if not l3link.empty:
            l3link['prodtype'] = 'QC'
            links.append(l3link)
            keys.append('l3')

        if not l4link.empty:
            l4link['prodtype'] = 'QA'
            links.append(l4link)
            keys.append('l4')

        if links:
            merged_df = pd.concat(links, keys=keys)
            filtered_df = merged_df[merged_df['linkfor'].isin(['q7_1', 'q7_2'])]

            vals = []
            filtered_df1 = merged_df['linkfor'].isin(['q7_1'])
            filtered_df2 = merged_df['linkfor'].isin(['q7_2'])
            if filtered_df1.any():
                vals.append('q7_1')
            if filtered_df2.any():
                vals.append('q7_2')

            linkstable = filtered_df.pivot_table(
                index=['id_value', 'prodtype','batch'], columns='linkfor', values='link', aggfunc=lambda x: ' | '.join(filter(None, x))).reset_index()
            
            pivot_df = linkstable.pivot(index=['id_value','batch'], columns='prodtype', values=vals).reset_index()
            pivot_df.columns = [f'{col[1]}_{col[0]}' if col[1]
                                != '' else col[0] for col in pivot_df.columns]

            dataout_df = pivot_df.rename(columns={'id_value': 'id_value','batch':'baseid_id__batch_name'})

            dataout_df = dataout_df.where(pd.notna(dataout_df), None)
            
            mrgd = pd.merge(mrgd, dataout_df, on=['id_value','baseid_id__batch_name'], how='outer')
        if not cnstable.empty:
            columns_to_drop = [
                col for col in mrgd.columns if col.endswith(('_y', '_x', '_z'))]
            mrgd = mrgd.drop(columns=columns_to_drop)
            mrgd = mrgd.drop(columns=stat)

            df_cleaned = mrgd.dropna(axis=1, how='all')
            mrgd = df_cleaned.drop_duplicates()

            mrgd.rename(columns=ColumnName, inplace=True)

            existing_columns = [col for col in order if col in mrgd.columns]
            mrgd = mrgd[existing_columns]

            if key == "withoutdata":    
                mrgd = mrgd.drop(columns=[col for col in without if col in mrgd.columns])
                lable = str(key)+'"OverallReport"'
            else:
                lable = '"OverallReport"'

            if not mrgd.empty:
                response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="'+ lable + \
                    str(timezone.now().date())+'".csv"'

                mrgd.to_csv(path_or_buf=response, index=False, encoding='utf-8-sig')

                return response
        else:
            return render(request, 'pages/outputDownload.html',{'Alert':{'type':'info','message':'No Records'}})    
    except Exception as er:
        print(er)
        return render(request, 'pages/outputDownload.html',{'Alert':'Error'})    

@loginrequired
def ProductionCount(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        scope = request.POST.get('scope')
        location = request.POST.get('location')

        targets = pd.DataFrame(userProfile.objects.filter(
            created_at__date=date, scope=scope, location=location).values('id', 'employeeID', 'target'))
        proddetails = pd.DataFrame(raw_data.objects.filter(created_at__date=date, scope=scope, location=location).annotate(completed=Count('l1_status', Q(
            l1_status='completed'))).values('id', 'completed', employeeID=F('l1_emp_id__employeeID')))
        
        # fromdate = request.POST.get('fromDate')
        # todate = request.POST.get('toDate')
        # key = request.POST.get('key')

        # conditions = Q()
        # if fromdate and todate:
        #     conditions &= Q(l4_prod_id__end_time__range=(fromdate, todate))
        # dL4raw = raw_data.objects.filter(conditions).annotate(tcount=Count('status'), da1count=Count('l1_status', Q(l1_status='completed')), da2count=Count('l2_status', Q(
        #     l2_status='completed')), qccount=Count('l3_status', Q(l3_status='completed')), qacount=Count('l4_status', Q(l4_status='completed'))).values('da1count', 'da2count', 'qccount', 'qacount')

        return HttpResponse({'status': 200})
    else:
        targets = pd.DataFrame(targets.objects.values(
            'id', 'employeeID', 'target'))
        proddetails = pd.DataFrame(raw_data.objects.filter(l1_status='completed').annotate(completed=Count('l1_status', Q(
            l1_status='completed'))).values('id', 'completed', employeeID=F('l1_emp_id__employeeID')))

        merged_df = pd.merge(proddetails, targets,
                             on='employeeID', how='outer')
        print(merged_df)

        print(proddetails)
        return render(request, 'pages/basicl4report.html')

@loginrequired
def target(request):
    locations = userProfile.objects.filter(Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    scope = Roles.objects.filter(Q(role__isnull=False) & ~Q(role='')).values('role').distinct()
    
    if request.method == 'POST':
        scopes = request.POST.get('scope')
        location = request.POST.getlist('location')

        if 'All' in location:
            query = Q()  
        else:
            query = Q(userprofile_id__location__in=location)

        if 'All' in scopes:
            query1 = ~Q(role='Admin') & ~Q(role='Super Admin')
        else:
            query1 = Q(role=scopes) 

        targetusers = Roles.objects.filter(query,query1).values(
            'id',
            'userprofile_id__employeeName',
            'userprofile_id',
            'role',
            'userprofile_id__location',
            'userprofile_id__employeeName'
        )

        datais = bool(targetusers)  

        return render(request, 'pages/targetsetpage.html', {
            'datais': datais,
            'targetusers': targetusers,
            'location': locations,
            'scope': scope
        })
    else:
        return render(request, 'pages/targetsetpage.html', {
            'datais': False,
            'location': locations,
            'scope': scope
        })
       
# def save_table_data(request):
#     EmpID = request.session.get('empId')
#     if request.method == 'POST':
#         try:
#             table_data = json.loads(request.POST.get('tableData'))  
#             target_date = request.POST.get('target_date')
#             for row_data in table_data:
#                 employee_id = row_data['employeeID']
#                 targetfor = row_data['role']                
#                 percentage_val = row_data['percentageval']
#                 targetsetting.objects.create(targetempid_id=employee_id,targetfor=targetfor,target_date = target_date,target= percentage_val,created_by_id =EmpID)

#             response_data = {'message': 'Data saved successfully'}
#             return JsonResponse(response_data)
#         except Exception as er:
#             print(er)
#             response_data = {'message': f'Error: {str(er)}'}
#             return JsonResponse(response_data, status=500)
    
@loginrequired
def save_table_data(request):
    EmpID = request.session.get('empId')
    if request.method == 'POST':
        try:
            table_data = json.loads(request.POST.get('tableData'))  
            target_date = request.POST.get('target_date')
            
            for row_data in table_data:
                employee_id = row_data['employeeID']
                targetfor = row_data['role']                
                percentage_val = row_data['percentageval']
                
                # Check if a record with the same combination exists
                existing_record = targetsetting.objects.filter(
                    targetempid_id=employee_id,
                    target_date=target_date,
                    targetfor=targetfor
                ).first()

                if existing_record:
                    # If the record exists, update it
                    existing_record.target = percentage_val
                    existing_record.save()
                else:
                    # If the record doesn't exist, create a new one
                    targetsetting.objects.create(targetempid_id=employee_id,targetfor=targetfor,target_date=target_date,target=percentage_val,
                        created_by_id=EmpID
                    )

            response_data = {'message': 'Data saved successfully'}
            return JsonResponse(response_data)
        except Exception as er:
            print(er)
            response_data = {'message': f'Error: {str(er)}'}
            return JsonResponse(response_data, status=500)

@loginrequired
def batchwisetracking(request):
    queue()
    filenames = raw_data.objects.values('baseid_id__filename').distinct()
    locations = userProfile.objects.filter(Q(location__isnull=False) & ~Q(location='')).values('location').distinct()

    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        location = request.POST.get('location')
        filename = request.POST.get('filename')

        # Convert string dates to datetime objects
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')

        if 'All' in location:
            query = Q()  
        else:
            query = Q(baseid_id__created_by_id__location=location)

        if 'All' in filename:
            query1 = Q()
        else:
            query1 = Q(baseid_id__filename=filename)


        trackdata = raw_data.objects.filter(
            baseid_id__created_at__date__range=(from_date, to_date)).filter(query,query1).values(
            'baseid_id__created_at__date',
            'baseid_id__batch_name',
            'baseid_id__filename',
            'baseid_id__created_by_id__location'
        ).annotate(
            inputcount=Count('baseid_id__batch_name'),
            da1_count=Count('l1_status', Q(l1_status='completed')),
            da2_count=Count('l2_status', Q(l2_status='completed')),
            qc_queue=Count('l1_l2_accuracy', Q(l1_l2_accuracy='fail')),
            qc_count=Count('l3_status', Q(l3_status='completed')),
            qa_queue=Count('l1_l2_accuracy', Q(l1_l2_accuracy='pass')),
            qa_count=Count('l4_status', Q(l4_status='completed'))
        ).exclude(status__in=['hold', 'deleted'])

        return render(request, 'pages/batchwisetracking.html', {'trackdata': trackdata, 'locations': locations, 'filename': filenames})
    else:
        return render(request, 'pages/batchwisetracking.html', {'locations': locations, 'filename': filenames})

@loginrequired
def userwisetracking(request):
    queue()
    locations = userProfile.objects.filter(Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    scopes = Roles.objects.filter(Q(role__isnull=False) & ~Q(role='')).values('role').exclude(role__in=['Admin','Super Admin']).distinct()
    if request.method == 'POST':
        date = request.POST.get('date')
        location = request.POST.get('location')
        scope = request.POST.get('scope')
        
        userid = Roles.objects.filter(role=scope).values_list('userprofile_id',flat=True)
        qscopes = Q()
        if 'DA1' in userid:
            qscopes = Q(l1_emp_id__in=userid)
        elif 'DA2' in userid:
            qscopes = Q(l2_emp_id__in=userid)
        elif 'QC' in userid:
            qscopes = Q(l3_emp_id__in=userid)
        elif 'QA' in userid:
            qscopes = Q(l4_emp_id__in=userid)

        if scope == 'DA1':
            trackdata = raw_data.objects.filter(qscopes,
                baseid_id__created_at__date=date,
                baseid_id__created_by_id__location=location           
            ).values(empid = F('l1_emp_id')).annotate(
                count=Count('l1_status', Q(l1_status='completed'))
            ).exclude(status__in=['hold', 'deleted'])
        if scope == 'DA2':
            trackdata = raw_data.objects.filter(qscopes,
                baseid_id__created_at__date=date,
                baseid_id__created_by_id__location=location           
            ).values(empid = F('l2_emp_id')).annotate(
                count=Count('l2_status', Q(l2_status='completed')),
            ).exclude(status__in=['hold', 'deleted'])
        if scope == 'QC':
            trackdata = raw_data.objects.filter(qscopes,
                baseid_id__created_at__date=date,
                baseid_id__created_by_id__location=location           
            ).values(empid = F('l3_emp_id')).annotate(
                count=Count('l3_status', Q(l3_status='completed')),
            ).exclude(status__in=['hold', 'deleted'])
        if scope == 'QA':
            trackdata = raw_data.objects.filter(qscopes,
                baseid_id__created_at__date=date,
                baseid_id__created_by_id__location=location           
            ).values(empid = F('l4_emp_id')).annotate(
                count=Count('l4_status', Q(l4_status='completed'))
            ).exclude(status__in=['hold', 'deleted'])
        
        targetdata = targetsetting.objects.filter(targetempid_id__in = userid,target_date__date = date).values('targetempid_id__employeeID','target','targetempid__location',empid = F('targetempid_id'))

        df_trackdata = pd.DataFrame(trackdata)
        df_targetdata = pd.DataFrame(targetdata)
        datais = False
        if not df_targetdata.empty and not df_trackdata.empty:
            mrgd = pd.merge(df_trackdata,df_targetdata,on='empid',how='right')
            if not mrgd.empty:
                mrgd.fillna(0,inplace=True)
                mrgd['Achieved %'] = mrgd.apply(lambda row: round((int(row['count']) / int(row['target'])) * 100,2) if not pd.isna(row['count']) else 0, axis=1)
                mrgd['Completed Count'] = mrgd['count'].astype(int)
                mrgd.index = np.arange(1, len(mrgd) + 1)
                mrgd = mrgd.drop(columns=['empid'])
                mrgd = mrgd.rename(columns={'targetempid_id__employeeID':'Employee Id','targetempid__location':'Location','target':'Target Count'})
                # mrgd.reset_index(drop=True, inplace=True)
                ord = ['Employee Id','Location','Target Count','Completed Count','Achieved %']
                mrgd = mrgd[ord]
                mrgd = mrgd.to_html().replace('<table border="1" class="dataframe">','<table class="table table-hover">').replace('<thead>','<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">','<tr>').replace('<th></th>','<th>S.No</th>')     
                datais = True
            return render(request, 'pages/userwisetracking.html', {'datais':datais,'mrgd': mrgd,'locations':locations,'scope':scopes})
        return render(request, 'pages/userwisetracking.html', {'datais':datais,'locations':locations,'scope':scopes,'Alert': {'type': 'Info', 'message': 'Agents have No Target'}})
    else:
        return render(request,'pages/userwisetracking.html',{'datais':False,'locations':locations,'scope':scopes})


# @loginrequired
def hourlytarget(request):
    locations = userProfile.objects.filter(Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    if request.method == 'POST':
        scope = request.POST.get('scope')
        location = request.POST.get('location')
        date = request.POST.get('date')  
        key =request.POST.get('key')     
        
        role = Q()
        if not scope == 'All':
            role = Q(targetfor = scope)

        locprod = Q()
        loctarget = Q()
        if not location == 'All':
            locprod = Q(created_by__location = location)
            loctarget = Q(targetempid__location = location)
        
        prod_Date = Q(end_time__date=date)

        table_names = []
        if scope == 'DA1' or scope == 'All':
            table_names.extend(['l1_production'])
        if scope == 'DA2' or scope == 'All':
            table_names.extend(['l2_production'])
        if scope == 'QC' or scope == 'All':
            table_names.extend(['l3_production'])
        if scope == 'QA' or scope == 'All':
            table_names.extend(['l4_production'])

        def getcount(filename):
            if filename:
                count = raw_data.objects.filter(baseid__filename = filename).count()
                return count
            else:
                return 0

        querysets = []
        for table_name in table_names:
            queryset = globals()[table_name].objects.filter(prod_Date,locprod).values(
                        date=F('created_at__date'),
                        empid=F('created_by__employeeID'),
                        empname=F('created_by__employeeName')
                    ).annotate(
                        source_table=Value(str(table_name), output_field=CharField()),                        
                        crtdhr=ExtractHour('end_time'),
                        count=Count('created_by_id'),
                        filename=F('qid__baseid__filename'),
                    ).exclude(qid__status__in=['hold', 'deleted'])
            querysets.append(queryset)
        productionhourly = list(chain(*querysets))

        targetdata = targetsetting.objects.filter(role,loctarget,target_date__date = date).values('target','targetempid__location',empid = F('targetempid_id__employeeID'),empname = F('targetempid__employeeName'))
        qsifttime = ShiftTime.objects.filter(created_at__date=date).annotate(
                shifttime=ExtractHour(Sum(F('endtime') - F('starttime')))
            ).values('shifttime',empid=F('userprofile__employeeID'))

        df_prodhoure = pd.DataFrame(productionhourly)
        df_targetdata = pd.DataFrame(targetdata)
        df_sifttime = pd.DataFrame(qsifttime)
        if not df_prodhoure.empty and not df_targetdata.empty and not df_sifttime.empty:
            mrgd = pd.merge(df_prodhoure, df_targetdata, on=['empid','empname'], how='outer')
            mrgd = mrgd.pivot_table(index=['empid', 'empname', 'filename', 'targetempid__location','target'],
                                    columns='crtdhr',
                                    values='count',
                                    fill_value=0).reset_index()
            mrgd = pd.merge(mrgd,df_sifttime,on='empid',how='left').fillna(0)

            mrgd['houretarget'] = mrgd.apply(lambda row: round((int(row['target']) * getcount(row['filename'])) / 100,2), axis=1)                        
            mrgd['houretarget'] = mrgd.apply(lambda row: round(int(row['houretarget']) / int(row['shifttime']),1), axis=1)                        
            tablecolumn = ['empid', 'filename', 'empname', 'targetempid__location', 'target','Hourly Target']
            mrgd = mrgd.rename(columns=lambda x: str(x) if x not in tablecolumn else x)
            mrgd = mrgd.fillna(0)
            mrgd.insert(mrgd.columns.get_loc('target') + 1, 'Hourly Target', mrgd['houretarget'])
            mrgd = mrgd.drop(columns=['houretarget','shifttime'])

            # mrgd = mrgd[tablecolumn]
            mrgd = mrgd.rename(columns=rnmhourlycolumn)
            mrgd.index = np.arange(1, len(mrgd) + 1)

            if key == 'Download':
                lable = 'Hourly_Report'
                response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="'+ lable + \
                    str(timezone.now().date())+'".csv"'
                mrgd.to_csv(path_or_buf=response, index=False, encoding='utf-8-sig')

                return response
            else:
                mrgd = mrgd.to_html().replace('<table border="1" class="dataframe">','<table id="dftable" class="table table-hover">').replace('<thead>','<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">','<tr>').replace('<th></th>','<th>S.No</th>')  
                return render(request, 'pages/hourly_target.html', {'houretarget': mrgd,'locations': locations,  'scope': scope,'location': location, 'date':date})
        else:
            return render(request, 'pages/hourly_target.html', {'locations': locations, 'date':date, 'scope': scope,'location': location, 'Alert':json.dumps({'type':'Info','message':'No records'})})   
    else:
        return render(request, 'pages/hourly_target.html', {'locations': locations})   


# Function to count true/false values and calculate percentage
def count_and_percentage(column):
    counts = df_report[column].value_counts()
    true_count = counts.get(True, 0)
    false_count = counts.get(False, 0)
    total_count = true_count + false_count

    return true_count, false_count, f'{true_count / total_count * 100:.2f}%' if total_count != 0 else '0%'

# Function to create count_df for a set of columns
def create_count_df(columns):
    count_df = pd.DataFrame(index=['True', 'False', 'Percentage'])
    
    for column in columns:
        count_df[column] = count_and_percentage(column)

    return count_df


@loginrequired
def resetuser(request):
    batch_names = raw_data.objects.filter().values('baseid__batch_name').distinct()    
    if request.method == 'POST':
        keyval = request.POST.get('keyval')
        key = request.POST.get('key')
        if key =='GetItem':
            batch_name = request.POST.get('batch_name')
            id_vals = request.POST.get('id_value')
            targetusers = raw_data.objects.filter(baseid__batch_name=batch_name,id_value=id_vals).values(
                'id',
                'baseid__batch_name',
                'id_value',
                'asin',
                'l1_prod__created_by__employeeID',
                'l1_status',
                'l2_prod__created_by__employeeID',
                'l2_status',
                'l3_prod__created_by__employeeID',
                'l3_status',
                'l4_prod__created_by__employeeID',
                'l4_status'
            )
            return render(request, 'pages/filebaseduserchech.html', {'batch_names':batch_names,'targetusers': targetusers,'batch_name': batch_name})
        
        if key == "userassign":
            batch_name = request.POST.get('batch_name1')
            scope = request.POST.get('scope1')  
            # production_staus = request.POST.get('production_staus')
            status_data = request.POST.get('hold_unhold')
            assignuser_id = Roles.objects.filter(role = scope).values('id','role','userprofile__employeeID','userprofile_id')
            
            if status_data == 'hold':
                if scope == "DA1":
                    query1 = Q(l1_status = status_data)
                if scope == "DA2":
                    query2 = Q(l2_status = status_data)
                if scope == "QC":
                    query3 = Q(l3_status = status_data)
                if scope == "QA":
                    query4 = Q(l4_status = status_data)
                exc = Q()
            
            elif status_data == 'picked':
                if scope == "DA1":
                    query1 = Q(l1_status = 'picked')
                if scope == "DA2":
                    query2 = Q(l2_status = 'picked')
                if scope == "QC":
                    query3 = Q(l3_status = 'picked')
                if scope == "QA":
                    query4 = Q(l4_status = 'picked')
                exc = Q()
            else:
                if scope == "DA1":
                    query1 = Q(l1_status = 'not_picked')
                    exc = Q(l1_status='completed') | Q(l1_status='picked')
                if scope == "DA2":
                    query2 = Q(l2_status = 'not_picked')
                    exc = Q(l2_status='completed') | Q(l2_status='picked')
                if scope == "QC":
                    query3 = Q(l3_status = 'not_moved') & Q(l1_status = 'completed') & Q(l2_status = 'completed') & Q(l1_l2_accuracy = 'fail')
                    exc = Q(l3_status='completed') | Q(l3_status='picked')
                if scope == "QA":
                    query4 = Q(l4_status = 'not_picked') & Q(l1_status = 'completed') & Q(l2_status = 'completed') & Q(l1_l2_accuracy = 'pass')
                    exc = Q(l4_status='completed') | Q(l4_status='picked')
                
            if scope == "DA1":
                asignuser = raw_data.objects.filter(query1,
                                baseid__batch_name=batch_name
                            ).values(
                                'id',
                                'id_value',
                                'l1_prod__created_by__employeeID',
                                'l1_status',
                                'l2_prod__created_by__employeeID',
                                'l2_status',
                                'l3_prod__created_by__employeeID',
                                'l3_status',
                                'l4_prod__created_by__employeeID',
                                'l4_status',
                                'status'
                            ).exclude(status__in=['hold', 'deleted']).exclude(exc)
            elif scope == "DA2":
                asignuser = raw_data.objects.filter(query2,
                                baseid__batch_name=batch_name,
                            ).values(
                                'id',
                                'id_value',
                                'l1_prod__created_by__employeeID',
                                'l1_status',
                                'l2_prod__created_by__employeeID',
                                'l2_status',
                                'l3_prod__created_by__employeeID',
                                'l3_status',
                                'l4_prod__created_by__employeeID',
                                'l4_status',
                                'status'
                            ).exclude(status__in=['hold', 'deleted']).exclude(exc)
            elif scope == "QC":
                asignuser = raw_data.objects.filter(query3,
                                baseid__batch_name=batch_name,
                            ).values(
                                'id',
                                'id_value',
                                'l1_prod__created_by__employeeID',
                                'l1_status',
                                'l2_prod__created_by__employeeID',
                                'l2_status',
                                'l3_prod__created_by__employeeID',
                                'l3_status',
                                'l4_prod__created_by__employeeID',
                                'l4_status',
                                'status'
                            ).exclude(status__in=['hold', 'deleted']).exclude(exc)
            elif scope == "QA":
                asignuser = raw_data.objects.filter(query4,
                                baseid__batch_name=batch_name,
                            ).values(
                                'id',
                                'id_value',
                                'l1_prod__created_by__employeeID',
                                'l1_status',
                                'l2_prod__created_by__employeeID',
                                'l2_status',
                                'l3_prod__created_by__employeeID',
                                'l3_status',
                                'l4_prod__created_by__employeeID',
                                'l4_status',
                                'status'
                            ).exclude(status__in=['hold', 'deleted']).exclude(exc)
            return render(request, 'pages/filebaseduserchech.html', {'assignuser_id':assignuser_id,'batch_name1':batch_name,'status_data':status_data,'scope':scope,'asignuser': asignuser,'batch_names': batch_names})               
            
        if keyval == 'assignuser':
            id_values = request.POST.getlist('idval[]')
            assigemployee = request.POST.get('assigningemployee_id')  
            assigning_for = request.POST.get('assigning_for')
            if assigning_for == "DA1":
                for id_value in id_values:
                    raw_data.objects.filter(id_value=id_value).update(l1_emp_id = assigemployee , l1_status = 'picked')
            if assigning_for == "DA2":
                for id_value in id_values:
                    raw_data.objects.filter(id_value=id_value).update(l2_emp_id = assigemployee , l2_status = 'picked')
            if assigning_for == "QC":
                for id_value in id_values:
                    raw_data.objects.filter(id_value=id_value).update(l3_emp_id = assigemployee , l3_status = 'picked')
            if assigning_for == "QA":
                for id_value in id_values:
                    raw_data.objects.filter(id_value=id_value).update(l4_emp_id = assigemployee , l4_status = 'picked')
        if keyval == 'hold':
            id_values = request.POST.getlist('idval[]')
            assigning_for = request.POST.get('assigning_for')

            if assigning_for == "DA1":
                for id_value in id_values:
                    raw_data.objects.filter(id_value=id_value).update( l1_status = 'picked')
            if assigning_for == "DA2":
                for id_value in id_values:
                    raw_data.objects.filter(id_value=id_value).update( l2_status = 'picked')
            if assigning_for == "QC":
                for id_value in id_values:
                    raw_data.objects.filter(id_value=id_value).update( l3_status = 'picked')
            if assigning_for == "QA":
                for id_value in id_values:
                    raw_data.objects.filter(id_value=id_value).update( l4_status = 'picked')
        if keyval == 'reset':
            id_values = request.POST.getlist('idval[]')        
            assigning_for = request.POST.get('assigning_for')
            if assigning_for == "DA1":
                for id_value in id_values:
                    raw_data.objects.filter(id_value=id_value).update( l1_status = 'not_picked', l1_loc=None, l1_emp = None )
                    # raw_data.objects.filter(id_value=id_value).delete()
            if assigning_for == "DA2":
                for id_value in id_values:
                    raw_data.objects.filter(id_value=id_value).update( l2_status = 'not_picked', l2_loc=None, l2_emp = None)
            if assigning_for == "QC":
                for id_value in id_values:
                    raw_data.objects.filter(id_value=id_value).update( l3_status = 'not_moved',l3_emp = None)
            if assigning_for == "QA":
                for id_value in id_values:
                    raw_data.objects.filter(id_value=id_value).update( l4_status = 'not_picked', l4_emp = None)
        return JsonResponse({'status':'success','code':200})
    else:
        queue()
        return render(request, 'pages/filebaseduserchech.html', {'datais': False,'batch_names': batch_names})
    
@loginrequired
def ut_report(request):
    filenames = raw_data.objects.values('baseid_id__filename').distinct()    
    if request.method == "POST":
        key = request.POST.get('key')

        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        filename = request.POST.get('filename')
        location = request.POST.get('location')
        language = request.POST.get('language')

        query = Q()
        if fromdate and todate:
            query &= Q(end_time__date__range = (fromdate,todate))
        if not 'All' == location:
            query &= Q(qid__baseid__created_by__location=location)

        if not 'All' == filename:           
            query &= Q(qid__baseid__filename=filename)
        
        if not 'All' == language:
            query &= Q(qid__baseid__language=language)

        querysets = []
        for table_name in ['l1_production','l2_production','l3_production','l4_production']:
            queryset = globals()[table_name].objects.filter(query).values(
                        date=F('created_at__date'),
                        empid=F('created_by__employeeID'),
                        filename=F('qid__baseid__filename'),
                        language=F('qid__baseid__language'),
                        location=F('qid__baseid__created_by__location'),
                        empname=F('created_by__employeeName')
                    ).annotate(
                        productiontime=Sum(F('end_time') - F('start_time')),
                    ).exclude(qid__status__in=['hold', 'deleted'])
            querysets.append(queryset)
        productions = list(chain(*querysets))
        df_production = pd.DataFrame(productions)
        if not df_production.empty:
            df_production['Percentage %'] = round(df_production['productiontime'] / timedelta(hours=9) * 100,2)
            df_production.rename(columns=utcolumns,inplace=True)
            utord = ['Date', 'Employee ID', 'Employee Name', 'Filename', 'Location', 'Language', 'Production Time','Percentage %']
            df_production = df_production[utord]
            df_production.index = np.arange(1, len(df_production) + 1)
            if key == 'Download':
                    lable = 'UT_Report'
                    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
                    response['Content-Disposition'] = 'attachment; filename="'+ lable + \
                        str(timezone.now().date())+'".csv"'
                    df_production.to_csv(path_or_buf=response, index=False, encoding='utf-8-sig')

                    return response
            else:
                df_production = df_production.to_html().replace('<table border="1" class="dataframe">','<table id="dftable" class="table table-hover">').replace('<thead>','<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">','<tr>').replace('<th></th>','<th>S.No</th>')  
                return render(request, 'pages/ut_report.html', {'ut_report': df_production, 'filenames': filenames,'fromdate':fromdate,'todate':todate,'filename':filename, 'location':location, 'language':language})
        else:
            # df_production.loc['Total'] = df_production.iloc[:, 3:-1].sum()
            # df_production.loc['Total','Utilization %'] = 
            return render(request,'pages/ut_report.html',{'filenames':filenames,'fromdate':fromdate,'todate':todate,'filename':filename, 'location':location, 'language':language})
    else:
        return render(request,'pages/ut_report.html',{'filenames':filenames})

@loginrequired
def aht_report(request):
    filenames = raw_data.objects.values('baseid_id__filename').distinct()    
    if request.method == "POST":
        key = request.POST.get('key')

        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        filename = request.POST.get('filename')
        location = request.POST.get('location')
        language = request.POST.get('language')
        scope = request.POST.get('scope')

        query = Q()
        if fromdate and todate:
            query &= Q(end_time__date__range = (fromdate,todate))
        if not 'All' in location:
            query &= Q(qid__baseid__created_by__location=location)

        if not 'All' in filename:           
            query &= Q(qid__baseid__filename=filename)
        
        if not 'All' in language:
            query &= Q(qid__baseid__language=language)

        table_names = []
        if scope == 'DA1' or scope == 'All':
            table_names.extend(['l1_production'])
        if scope == 'DA2' or scope == 'All':
            table_names.extend(['l2_production'])
        if scope == 'QC' or scope == 'All':
            table_names.extend(['l3_production'])
        if scope == 'QA' or scope == 'All':
            table_names.extend(['l4_production'])

        querysets = []
        for table_name in table_names:
            queryset = globals()[table_name].objects.filter(query).values(
                        date=F('created_at__date'),
                        empid=F('created_by__employeeID'),
                        filename=F('qid__baseid__filename'),
                        language=F('qid__baseid__language'),
                        location=F('qid__baseid__created_by__location'),
                        empname=F('created_by__employeeName')
                    ).annotate(
                        productiontime=Sum(F('end_time') - F('start_time')),
                        prodcount = Count('created_by__employeeID')
                    ).exclude(qid__status__in=['hold', 'deleted'])
            querysets.append(queryset)
        productions = list(chain(*querysets))
        df_production = pd.DataFrame(productions)
        if not df_production.empty:
            df_production['AHT'] = (df_production['productiontime'] / df_production['prodcount']).apply(lambda x: '{:02}:{:02}:{:.2f}'.format(int(x.seconds // 3600),int((x.seconds % 3600) // 60),x.seconds % 60 + x.microseconds / 1e6)) #().astype(str).str.split().str[-1]
            utcolumns.update({'prodcount':'Production Count'})
            df_production.rename(columns=utcolumns,inplace=True)
            utord = ['Date', 'Employee ID', 'Employee Name', 'Filename', 'Location', 'Language', 'Production Time', 'Production Count','AHT']
            df_production = df_production[utord]
            df_production.index = np.arange(1, len(df_production) + 1)
            if key == 'Download':
                lable = 'AHT_Report'
                response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
                response['Content-Disposition'] = 'attachment; filename="'+ lable + \
                    str(timezone.now().date())+'".csv"'
                df_production.to_csv(path_or_buf=response, index=False, encoding='utf-8-sig')
                return response
            else:
                df_production = df_production.to_html().replace('<table border="1" class="dataframe">','<table id="dftable" class="table table-hover">').replace('<thead>','<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">','<tr>').replace('<th></th>','<th>S.No</th>')  
                return render(request, 'pages/aht_report.html', {'aht_report': df_production, 'filenames': filenames,'fromdate':fromdate,'todate':todate,'filename':filename, 'location':location, 'language':language, 'scope':scope})
        else:
            return render(request, 'pages/aht_report.html', {'filenames': filenames,'fromdate':fromdate,'todate':todate,'filename':filename, 'location':location, 'language':language, 'scope':scope})            
    else:
        return render(request,'pages/aht_report.html',{'filenames':filenames})


@loginrequired
def qualityreport(request):

    filenames = raw_data.objects.values('baseid_id__filename').distinct()
    locations = userProfile.objects.filter(Q(location__isnull=False) & ~Q(location='')).values('location').distinct()
    language =  userProfile.objects.filter(Q(language__isnull=False) & ~Q(language='')).values('language').distinct()

    language_list = []
    for item in language:
        language_list.extend(ast.literal_eval(item['language']))
    language_list = list(set(language_list))
    
    if request.method == 'POST':
        try:
            
            fromdate = request.POST.get('fromdate')
            todate = request.POST.get('todate')
            filename = request.POST.get('filename')
            location = request.POST.get('location')
            scope = request.POST.get('scope')
            key = request.POST.get('key')
            language_sl = request.POST.get('language')
            options = request.POST.get('options')

            print(fromdate,todate,filename,location,scope,key,language_sl,options)

            raw_data_query = Q(l1_status="completed", l2_status="completed", l3_status="completed")

            if filename != "ALL":
                
                raw_data_query &= Q(baseid__filename=filename)

            if location != "ALL":
                
                raw_data_query &= Q(Q(l1_loc=location) | Q(l2_loc=location))

            if language_sl != "ALL":
                
                raw_data_query &= Q(baseid__language=[language_sl])
            
            raw_data_query &= Q(l1_prod__end_time__date__range=(fromdate, todate))
            raw_data_query &= Q(l2_prod__end_time__date__range=(fromdate, todate))
            raw_data_query &= Q(l3_prod__end_time__date__range=(fromdate, todate))
            
            raw_data_values = raw_data.objects.filter(raw_data_query).values('baseid__filename',
                    'baseid__batch_name',         
                    'l1_emp__employeeName',
                    'l1_emp__employeeID',
                    'l2_emp__employeeID',
                    'l1_loc',
                    'l2_emp__employeeName',
                    'l2_loc',
                    'id_value', 
                    'question', 
                    'asin', 
                    'title', 
                    'product_url', 
                    'imagepath', 
                    'evidence', 
                    'answer_one', 
                    'answer_two',
                    'l1_status',
                    'l2_status',
                    'l4_status',
                    'l3_status',
                    'l1_l2_accuracy',
                    'l1_prod__que1',
                    'l1_prod__que2',
                    'l1_prod__que2_1',
                    'l1_prod__que3',
                    'l1_prod__is_present_both',
                    'l1_prod__que4_ans1',
                    'l1_prod__que5_ans1', 
                    'l1_prod__que6_ans1', 
                    'l1_prod__que7_ans1',
                    'l1_prod__que8_ans1',
                    'l1_prod__que9_ans1',
                    'l1_prod__que10_ans1',
                    'l1_prod__que11_ans1',
                    'l1_prod__q12_ans1',
                    'l1_prod__que4_ans2',
                    'l1_prod__que5_ans2',
                    'l1_prod__que6_ans2',
                    'l1_prod__que7_ans2',
                    'l1_prod__que8_ans2',
                    'l1_prod__que9_ans2',
                    'l1_prod__que10_ans2',
                    'l1_prod__que11_ans2',
                    'l1_prod__q12_ans2',
                    'l2_prod__que1',
                    'l2_prod__que2',
                    'l2_prod__que2_1',
                    'l2_prod__que3',
                    'l2_prod__is_present_both',
                    'l2_prod__que4_ans1',
                    'l2_prod__que5_ans1', 
                    'l2_prod__que6_ans1', 
                    'l2_prod__que7_ans1',
                    'l2_prod__que8_ans1',
                    'l2_prod__que9_ans1',
                    'l2_prod__que10_ans1',
                    'l2_prod__que11_ans1',
                    'l2_prod__q12_ans1',
                    'l2_prod__que4_ans2',
                    'l2_prod__que5_ans2',
                    'l2_prod__que6_ans2',
                    'l2_prod__que7_ans2',
                    'l2_prod__que8_ans2',
                    'l2_prod__que9_ans2',
                    'l2_prod__que10_ans2',
                    'l2_prod__que11_ans2',
                    'l2_prod__q12_ans2',
                    'l3_prod__que1',
                    'l3_prod__que2',
                    'l3_prod__que2_1',
                    'l3_prod__que3',
                    'l3_prod__is_present_both',
                    'l3_prod__que4_ans1',
                    'l3_prod__que5_ans1', 
                    'l3_prod__que6_ans1', 
                    'l3_prod__que7_ans1',
                    'l3_prod__que8_ans1',
                    'l3_prod__que9_ans1',
                    'l3_prod__que10_ans1',
                    'l3_prod__que11_ans1',
                    'l3_prod__q12_ans1',
                    'l3_prod__que4_ans2',
                    'l3_prod__que5_ans2',
                    'l3_prod__que6_ans2',
                    'l3_prod__que7_ans2',
                    'l3_prod__que8_ans2',
                    'l3_prod__que9_ans2',
                    'l3_prod__que10_ans2',
                    'l3_prod__que11_ans2',
                    'l3_prod__q12_ans2')
            
            result_df = pd.DataFrame()
            
            for row in raw_data_values:
                
                if scope == 'DA1':
                    
                    fromfun = userwisequalityreportDA1(row)
                    
                    result_df = pd.concat([result_df, fromfun], ignore_index=True)
                    
                elif scope == 'DA2':

                    fromfun = userwisequalityreportDA2(row)

                    result_df = pd.concat([result_df, fromfun], ignore_index=True)
                   
                elif scope == 'ALL' :

                    fromfun1 = userwisequalityreportDA1(row)

                    result_df = pd.concat([result_df, fromfun1], ignore_index=True)
                    
                    fromfun2 = userwisequalityreportDA2(row)
                
                    result_df = pd.concat([result_df, fromfun2], ignore_index=True)
            
            if key == 'Download' :                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
                    if options == 'USER':

                        csv_data = result_df.to_csv(index=True, encoding='utf-8')

                        response = HttpResponse(csv_data, content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename="quality_report.csv"'
                        return response
                    
                    elif  options == 'FIELD':
                        rows = [
                            '1_prod', '2_prod', '3_prod',
                            '4_prod', '5_prod',
                            '6_prod', '7_prod', '8_prod',
                            '9_prod', '10_prod', '11_prod',
                            '12_prod', '13_prod', '14_prod',
                            '15_prod', '16_prod', '17_prod',
                            '18_prod', '19_prodp', '20_prod',
                            '21_prod', '22_prod', '23_prod'
                        ]

                        new_df = pd.DataFrame(rows, columns=['PRODUCTION'])

                        new_df['Audited_count'] = result_df.apply(lambda row: row[:-2].eq(True).sum(), axis=1)
                        new_df['Total_error'] = result_df.apply(lambda row: row[:-2].eq(False).sum(), axis=1)
                        new_df['Field_count'] = new_df['Audited_count'] * 25
                        new_df['Audited_count_wise_accuracy'] = (1 - (new_df['Total_error'] / new_df['Audited_count'])) * 100
                        new_df['field_count_wise_accuracy'] = (1 - (new_df['Total_error'] / new_df['Field_count'])) * 100
                        
                        csv_data = new_df.to_csv(index=True, encoding='utf-8')

                        response = HttpResponse(csv_data, content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename="quality_report.csv"'
                        return response
                    
            else :
                    
                    if options == 'USER':

                        data_list = result_df.to_dict(orient='records')

                        return render(request, 'pages/QualityReport.html', {'locations': locations, 'filenames': filenames,'language':language_list,'response_data_list':data_list})
                    
                    elif  options == 'FIELD':   
                        rows = [
                            '1_prod', '2_prod', '3_prod',
                            '4_prod', '5_prod',
                            '6_prod', '7_prod', '8_prod',
                            '9_prod', '10_prod', '11_prod',
                            '12_prod', '13_prod', '14_prod',
                            '15_prod', '16_prod', '17_prod',
                            '18_prod', '19_prodp', '20_prod',
                            '21_prod', '22_prod', '23_prod'
                        ]

                        new_df = pd.DataFrame(rows, columns=['PRODUCTION'])

                        new_df['Audited_count'] = result_df.apply(lambda row: row[:-2].eq(True).sum(), axis=1)
                        new_df['Total_error'] = result_df.apply(lambda row: row[:-2].eq(False).sum(), axis=1)
                        new_df['Field_count'] = new_df['Audited_count'] * 25
                        new_df['Audited_count_wise_accuracy'] = (1 - (new_df['Total_error'] / new_df['Audited_count'])) * 100
                        new_df['field_count_wise_accuracy'] = (1 - (new_df['Total_error'] / new_df['Field_count'])) * 100
                        data_list = new_df.to_dict(orient='records')
                        return render(request, 'pages/QualityReport.html', {'locations': locations, 'filenames': filenames,'language':language_list,'data_list2':data_list})

        except Exception as e:
            return render(request, 'pages/QualityReport.html', {'locations': locations, 'filenames': filenames,'language':language_list})

    return render(request, 'pages/QualityReport.html', {'locations': locations, 'filenames': filenames,'language':language_list})

def userwisequalityreportDA1(userid):
         
            df_report = pd.DataFrame([userid])
                
            df_report['PRODUCTION'] = 'DA1'
            df_report['1_prod'] = (df_report['l1_prod__que1']==df_report['l3_prod__que1'])
            df_report['2_prod'] = (df_report['l1_prod__que2']==df_report['l3_prod__que2'])
            df_report['3_prod'] = (df_report['l1_prod__que2_1']==df_report['l3_prod__que2_1'])
            df_report['4_prod'] = (df_report['l1_prod__que3']==df_report['l3_prod__que3'])
            df_report['5_prod'] = (df_report['l1_prod__is_present_both']==df_report['l3_prod__is_present_both'])
            df_report['6_prod'] = (df_report['l1_prod__que4_ans1']==df_report['l3_prod__que4_ans1'])
            df_report['7_prod'] = (df_report['l1_prod__que5_ans1']==df_report['l3_prod__que5_ans1'])
            df_report['8_prod'] = (df_report['l1_prod__que6_ans1']==df_report['l3_prod__que6_ans1'])
            df_report['9_prod'] = (df_report['l1_prod__que7_ans1']==df_report['l3_prod__que7_ans1'])
            df_report['10_prod'] = (df_report['l1_prod__que8_ans1']==df_report['l3_prod__que8_ans1'])
            df_report['11_prod'] = (df_report['l1_prod__que9_ans1']==df_report['l3_prod__que9_ans1'])
            df_report['12_prod'] = (df_report['l1_prod__que10_ans1']==df_report['l3_prod__que10_ans1'])
            df_report['13_prod'] = (df_report['l1_prod__que11_ans1']==df_report['l3_prod__que11_ans1'])
            df_report['14_prod'] = (df_report['l1_prod__q12_ans1']==df_report['l3_prod__q12_ans1'])
            df_report['15_prod'] = (df_report['l1_prod__que4_ans2']==df_report['l3_prod__que4_ans2'])
            df_report['16_prod'] = (df_report['l1_prod__que5_ans2']==df_report['l3_prod__que5_ans2'])
            df_report['17_prod'] = (df_report['l1_prod__que6_ans2']==df_report['l3_prod__que6_ans2'])
            df_report['18_prod'] = (df_report['l1_prod__que7_ans2']==df_report['l3_prod__que7_ans2'])
            df_report['19_prod'] = (df_report['l1_prod__que8_ans2']==df_report['l3_prod__que8_ans2'])
            df_report['20_prod'] = (df_report['l1_prod__que9_ans2']==df_report['l3_prod__que9_ans2'])
            df_report['21_prod'] = (df_report['l1_prod__que10_ans2']==df_report['l3_prod__que10_ans2'])
            df_report['22_prod'] = (df_report['l1_prod__que11_ans2']==df_report['l3_prod__que11_ans2'])
            df_report['23_prod'] = (df_report['l1_prod__q12_ans2']==df_report['l3_prod__q12_ans2'])


            columns_to_remove = [
                'l1_status', 'l2_status', 'l4_status', 'l3_status', 'l1_l2_accuracy',
                'l1_prod__que1', 'l1_prod__que2', 'l1_prod__que2_1', 'l1_prod__que3',
                'l1_prod__is_present_both', 'l1_prod__que4_ans1', 'l1_prod__que5_ans1',
                'l1_prod__que6_ans1', 'l1_prod__que7_ans1', 'l1_prod__que8_ans1',
                'l1_prod__que9_ans1', 'l1_prod__que10_ans1', 'l1_prod__que11_ans1',
                'l1_prod__q12_ans1', 'l1_prod__que4_ans2', 'l1_prod__que5_ans2',
                'l1_prod__que6_ans2', 'l1_prod__que7_ans2', 'l1_prod__que8_ans2',
                'l1_prod__que9_ans2', 'l1_prod__que10_ans2', 'l1_prod__que11_ans2',
                'l1_prod__q12_ans2', 'l2_prod__que1', 'l2_prod__que2', 'l2_prod__que2_1',
                'l2_prod__que3', 'l2_prod__is_present_both', 'l2_prod__que4_ans1',
                'l2_prod__que5_ans1', 'l2_prod__que6_ans1', 'l2_prod__que7_ans1',
                'l2_prod__que8_ans1', 'l2_prod__que9_ans1', 'l2_prod__que10_ans1',
                'l2_prod__que11_ans1', 'l2_prod__q12_ans1', 'l2_prod__que4_ans2',
                'l2_prod__que5_ans2', 'l2_prod__que6_ans2', 'l2_prod__que7_ans2',
                'l2_prod__que8_ans2', 'l2_prod__que9_ans2', 'l2_prod__que10_ans2',
                'l2_prod__que11_ans2', 'l2_prod__q12_ans2', 'l3_prod__que1',
                'l3_prod__que2', 'l3_prod__que2_1', 'l3_prod__que3', 'l3_prod__is_present_both',
                'l3_prod__que4_ans1', 'l3_prod__que5_ans1', 'l3_prod__que6_ans1',
                'l3_prod__que7_ans1', 'l3_prod__que8_ans1', 'l3_prod__que9_ans1',
                'l3_prod__que10_ans1', 'l3_prod__que11_ans1', 'l3_prod__q12_ans1',
                'l3_prod__que4_ans2', 'l3_prod__que5_ans2', 'l3_prod__que6_ans2',
                'l3_prod__que7_ans2', 'l3_prod__que8_ans2', 'l3_prod__que9_ans2',
                'l3_prod__que10_ans2', 'l3_prod__que11_ans2', 'l3_prod__q12_ans2','l2_emp__employeeID','l2_emp__employeeName','l2_loc'
            ]

            df_report = df_report.drop(columns=columns_to_remove)

            new_column_names = {'l1_emp__employeeID': 'Employee_id', 'l1_emp__employeeName': 'Employee_Name','l1_loc':'Location'}

            df_report.rename(columns=new_column_names, inplace=True)

            df_report['Audited_count'] = df_report.apply(lambda row: row[:-2].eq(True).sum(), axis=1)


            df_report['Total_error'] = df_report.apply(lambda row: row[:-2].eq(False).sum(), axis=1)

            df_report['Field_count'] = df_report['Audited_count']*25

            df_report['Audited_count_wise_accuracy'] = (1 - (df_report['Total_error'] / df_report['Audited_count']))*100

            df_report['field_count_wise_accuracy'] = (1 - (df_report['Total_error'] / df_report['Field_count']))*100
            
            return df_report

def userwisequalityreportDA2(userid):

            df_report = pd.DataFrame([userid])

            # comparing l2 == l3
            df_report['PRODUCTION'] = 'DA2'
            df_report['1_prod'] = (df_report['l2_prod__que1']==df_report['l3_prod__que1'])
            df_report['2_prod'] = (df_report['l2_prod__que2']==df_report['l3_prod__que2'])
            df_report['3_prod'] = (df_report['l2_prod__que2_1']==df_report['l3_prod__que2_1'])
            df_report['4_prod'] = (df_report['l2_prod__que3']==df_report['l3_prod__que3'])
            df_report['5_prod'] = (df_report['l2_prod__is_present_both']==df_report['l3_prod__is_present_both'])
            df_report['6_prod'] = (df_report['l2_prod__que4_ans1']==df_report['l3_prod__que4_ans1'])
            df_report['7_prod'] = (df_report['l2_prod__que5_ans1']==df_report['l3_prod__que5_ans1'])
            df_report['8_prod'] = (df_report['l2_prod__que6_ans1']==df_report['l3_prod__que6_ans1'])
            df_report['9_prod'] = (df_report['l2_prod__que7_ans1']==df_report['l3_prod__que7_ans1'])
            df_report['10_prod'] = (df_report['l2_prod__que8_ans1']==df_report['l3_prod__que8_ans1'])
            df_report['11_prod'] = (df_report['l2_prod__que9_ans1']==df_report['l3_prod__que9_ans1'])
            df_report['12_prod'] = (df_report['l2_prod__que10_ans1']==df_report['l3_prod__que10_ans1'])
            df_report['13_prod'] = (df_report['l2_prod__que11_ans1']==df_report['l3_prod__que11_ans1'])
            df_report['14_prod'] = (df_report['l2_prod__q12_ans1']==df_report['l3_prod__q12_ans1'])
            df_report['15_prod'] = (df_report['l2_prod__que4_ans2']==df_report['l3_prod__que4_ans2'])
            df_report['16_prod'] = (df_report['l2_prod__que5_ans2']==df_report['l3_prod__que5_ans2'])
            df_report['17_prod'] = (df_report['l2_prod__que6_ans2']==df_report['l3_prod__que6_ans2'])
            df_report['18_prod'] = (df_report['l2_prod__que7_ans2']==df_report['l3_prod__que7_ans2'])
            df_report['19_prod'] = (df_report['l2_prod__que8_ans2']==df_report['l3_prod__que8_ans2'])
            df_report['20_prod'] = (df_report['l2_prod__que9_ans2']==df_report['l3_prod__que9_ans2'])
            df_report['21_prod'] = (df_report['l2_prod__que10_ans2']==df_report['l3_prod__que10_ans2'])
            df_report['22_prod'] = (df_report['l2_prod__que11_ans2']==df_report['l3_prod__que11_ans2'])
            df_report['23_prod'] = (df_report['l2_prod__q12_ans2']==df_report['l3_prod__q12_ans2'])
            

            columns_to_remove = [
                'l1_status', 'l2_status', 'l4_status', 'l3_status', 'l1_l2_accuracy',
                'l1_prod__que1', 'l1_prod__que2', 'l1_prod__que2_1', 'l1_prod__que3',
                'l1_prod__is_present_both', 'l1_prod__que4_ans1', 'l1_prod__que5_ans1',
                'l1_prod__que6_ans1', 'l1_prod__que7_ans1', 'l1_prod__que8_ans1',
                'l1_prod__que9_ans1', 'l1_prod__que10_ans1', 'l1_prod__que11_ans1',
                'l1_prod__q12_ans1', 'l1_prod__que4_ans2', 'l1_prod__que5_ans2',
                'l1_prod__que6_ans2', 'l1_prod__que7_ans2', 'l1_prod__que8_ans2',
                'l1_prod__que9_ans2', 'l1_prod__que10_ans2', 'l1_prod__que11_ans2',
                'l1_prod__q12_ans2', 'l2_prod__que1', 'l2_prod__que2', 'l2_prod__que2_1',
                'l2_prod__que3', 'l2_prod__is_present_both', 'l2_prod__que4_ans1',
                'l2_prod__que5_ans1', 'l2_prod__que6_ans1', 'l2_prod__que7_ans1',
                'l2_prod__que8_ans1', 'l2_prod__que9_ans1', 'l2_prod__que10_ans1',
                'l2_prod__que11_ans1', 'l2_prod__q12_ans1', 'l2_prod__que4_ans2',
                'l2_prod__que5_ans2', 'l2_prod__que6_ans2', 'l2_prod__que7_ans2',
                'l2_prod__que8_ans2', 'l2_prod__que9_ans2', 'l2_prod__que10_ans2',
                'l2_prod__que11_ans2', 'l2_prod__q12_ans2', 'l3_prod__que1',
                'l3_prod__que2', 'l3_prod__que2_1', 'l3_prod__que3', 'l3_prod__is_present_both',
                'l3_prod__que4_ans1', 'l3_prod__que5_ans1', 'l3_prod__que6_ans1',
                'l3_prod__que7_ans1', 'l3_prod__que8_ans1', 'l3_prod__que9_ans1',
                'l3_prod__que10_ans1', 'l3_prod__que11_ans1', 'l3_prod__q12_ans1',
                'l3_prod__que4_ans2', 'l3_prod__que5_ans2', 'l3_prod__que6_ans2',
                'l3_prod__que7_ans2', 'l3_prod__que8_ans2', 'l3_prod__que9_ans2',
                'l3_prod__que10_ans2', 'l3_prod__que11_ans2', 'l3_prod__q12_ans2','l1_emp__employeeID','l1_emp__employeeName','l1_loc'
            ]

            df_report = df_report.drop(columns=columns_to_remove)

            new_column_names = {'l2_emp__employeeID': 'Employee_id', 'l2_emp__employeeName': 'Employee_Name','l2_loc':'Location'}

            df_report.rename(columns=new_column_names, inplace=True)

            df_report['Audited_count'] = df_report.apply(lambda row: row[:-2].eq(True).sum(), axis=1)


            df_report['Total_error'] = df_report.apply(lambda row: row[:-2].eq(False).sum(), axis=1)

            df_report['Field_count'] = df_report['Audited_count']*25

            df_report['Audited_count_wise_accuracy'] = (1 - (df_report['Total_error'] / df_report['Audited_count']))*100

            df_report['field_count_wise_accuracy'] = (1 - (df_report['Total_error'] / df_report['Field_count']))*100

            return df_report



@loginrequired
def iaa(request):

    batchname = basefile.objects.filter(Q(batch_name__isnull=False) & ~Q(batch_name='')).values('batch_name').distinct()

    if request.method == 'POST':

        # try:
            totaldata = pd.DataFrame()
    
            fromdate = request.POST.get('fromdate')
            todate = request.POST.get('todate')
            batchname_filter = request.POST.get('batchname')
            key = request.POST.get('key')

            from datetime import datetime, timedelta

            fromdates = datetime.strptime(fromdate, '%Y-%m-%d')
            todates = datetime.strptime(todate, '%Y-%m-%d')

            date_difference = (todates - fromdates).days

            list_of_dates = [fromdates + timedelta(days=i) for i in range(date_difference + 1)]

            formatted_dates = [date.strftime('%Y-%m-%d') for date in list_of_dates]

            question_list = [
                "Questions",
                "Q1: Do you understand the query?",
                "Q2: What is the query type?",
                "Q2.A: Select the entity?",
                "Are both answers present?",
                "Q4: Is the answer 1 free of any sensitive content?",
                "Q5: Do you think that the answer 1 is relevant?",
                "Q6: Do you think that the answer 1 is informative/helpful?",
                "Q7: Is the answer 1 factually correct?",
                "Q7-A. Enter the evidence answer 1",
                "Q8: Do you think the answer 1 is clear?",
                "Q9: Do you think the answer 1 is objective?",
                "Q10: Do you think the answer 1 has an appropriate tone?",
                "Q11: Is the answer 1 from the perspective of Amazon’s virtual assistant?",
                "Q12: Does the answer 1 respect the structure guidelines?",
                "Q4: Is the answer 2 free of any sensitive content?",
                "Q5: Do you think that the answer 2 is relevant?",
                "Q6: Do you think that the answer 2 is informative/helpful?",
                "Q7: Is the answer 2 factually correct?",
                "Q7-A. Enter the evidence answer 2",
                "Q8: Do you think the answer 2 is clear?",
                "Q9: Do you think the answer 2 is objective?",
                "Q10: Do you think the answer 2 has an appropriate tone?",
                "Q11: Is the answer 2 from the perspective of Amazon’s virtual assistant?"
            ]

            for formatted_date in formatted_dates:
                # iterating for date wise data
                dayvalues = iaa_date_wise(formatted_date,formatted_date,batchname_filter)
                
                if not dayvalues.empty:

                    totaldata = pd.merge(totaldata, dayvalues,left_index=True, right_index=True,how='right')

            raw_data_query = Q(l1_status="completed", l2_status="completed", l3_status="completed")

            if batchname_filter != "ALL":
                
                raw_data_query &= Q(baseid__batch_name=batchname_filter)

            raw_data_query &= Q(l1_prod__end_time__date__range=(fromdate, todate))
            raw_data_query &= Q(l2_prod__end_time__date__range=(fromdate, todate))
            raw_data_query &= Q(l3_prod__end_time__date__range=(fromdate, todate))

            raw_data_values = raw_data.objects.filter(raw_data_query).values('baseid__filename',
                    'baseid__batch_name',         
                    'l1_emp__employeeName',
                    'l1_emp__employeeID',
                    'l2_emp__employeeID',
                    'l1_loc',
                    'l2_emp__employeeName',
                    'l2_loc',
                    'id_value', 
                    'question', 
                    'asin', 
                    'title', 
                    'product_url', 
                    'imagepath', 
                    'evidence', 
                    'answer_one', 
                    'answer_two',
                    'l1_status',
                    'l2_status',
                    'l4_status',
                    'l3_status',
                    'l1_l2_accuracy',
                    'l1_prod__que1',
                    'l1_prod__que2',
                    'l1_prod__que2_1',
                    'l1_prod__que3',
                    'l1_prod__is_present_both',
                    'l1_prod__que4_ans1',
                    'l1_prod__que5_ans1', 
                    'l1_prod__que6_ans1', 
                    'l1_prod__que7_ans1',
                    'l1_prod__que8_ans1',
                    'l1_prod__que9_ans1',
                    'l1_prod__que10_ans1',
                    'l1_prod__que11_ans1',
                    'l1_prod__q12_ans1',
                    'l1_prod__que4_ans2',
                    'l1_prod__que5_ans2',
                    'l1_prod__que6_ans2',
                    'l1_prod__que7_ans2',
                    'l1_prod__que8_ans2',
                    'l1_prod__que9_ans2',
                    'l1_prod__que10_ans2',
                    'l1_prod__que11_ans2',
                    'l1_prod__q12_ans2',
                    'l2_prod__que1',
                    'l2_prod__que2',
                    'l2_prod__que2_1',
                    'l2_prod__que3',
                    'l2_prod__is_present_both',
                    'l2_prod__que4_ans1',
                    'l2_prod__que5_ans1', 
                    'l2_prod__que6_ans1', 
                    'l2_prod__que7_ans1',
                    'l2_prod__que8_ans1',
                    'l2_prod__que9_ans1',
                    'l2_prod__que10_ans1',
                    'l2_prod__que11_ans1',
                    'l2_prod__q12_ans1',
                    'l2_prod__que4_ans2',
                    'l2_prod__que5_ans2',
                    'l2_prod__que6_ans2',
                    'l2_prod__que7_ans2',
                    'l2_prod__que8_ans2',
                    'l2_prod__que9_ans2',
                    'l2_prod__que10_ans2',
                    'l2_prod__que11_ans2',
                    'l2_prod__q12_ans2',
                    'l3_prod__que1',
                    'l3_prod__que2',
                    'l3_prod__que2_1',
                    'l3_prod__que3',
                    'l3_prod__is_present_both',
                    'l3_prod__que4_ans1',
                    'l3_prod__que5_ans1', 
                    'l3_prod__que6_ans1', 
                    'l3_prod__que7_ans1',
                    'l3_prod__que8_ans1',
                    'l3_prod__que9_ans1',
                    'l3_prod__que10_ans1',
                    'l3_prod__que11_ans1',
                    'l3_prod__q12_ans1',
                    'l3_prod__que4_ans2',
                    'l3_prod__que5_ans2',
                    'l3_prod__que6_ans2',
                    'l3_prod__que7_ans2',
                    'l3_prod__que8_ans2',
                    'l3_prod__que9_ans2',
                    'l3_prod__que10_ans2',
                    'l3_prod__que11_ans2',
                    'l3_prod__q12_ans2')



            result_df = pd.DataFrame(raw_data_values)

            new_columns_list = []

            # List of columns to compare
            columns_to_compare = [
                ('l1_prod__que1', 'l2_prod__que1', 'l3_prod__que1'),
                ('l1_prod__que2', 'l2_prod__que2', 'l3_prod__que2'),
                ('l1_prod__que2_1', 'l2_prod__que2_1', 'l3_prod__que2_1'),
                ('l1_prod__que3', 'l2_prod__que3', 'l3_prod__que3'),
                ('l1_prod__is_present_both', 'l2_prod__is_present_both', 'l3_prod__is_present_both'),
                ('l1_prod__que4_ans1', 'l2_prod__que4_ans1', 'l3_prod__que4_ans1'),
                ('l1_prod__que5_ans1', 'l2_prod__que5_ans1', 'l3_prod__que5_ans1'),
                ('l1_prod__que6_ans1', 'l2_prod__que6_ans1', 'l3_prod__que6_ans1'),
                ('l1_prod__que7_ans1', 'l2_prod__que7_ans1', 'l3_prod__que7_ans1'),
                ('l1_prod__que8_ans1', 'l2_prod__que8_ans1', 'l3_prod__que8_ans1'),
                ('l1_prod__que9_ans1', 'l2_prod__que9_ans1', 'l3_prod__que9_ans1'),
                ('l1_prod__que10_ans1', 'l2_prod__que10_ans1', 'l3_prod__que10_ans1'),
                ('l1_prod__que11_ans1', 'l2_prod__que11_ans1', 'l3_prod__que11_ans1'),
                ('l1_prod__q12_ans1', 'l2_prod__q12_ans1', 'l3_prod__q12_ans1'),
                ('l1_prod__que4_ans2', 'l2_prod__que4_ans2', 'l3_prod__que4_ans2'),
                ('l1_prod__que5_ans2', 'l2_prod__que5_ans2', 'l3_prod__que5_ans2'),
                ('l1_prod__que6_ans2', 'l2_prod__que6_ans2', 'l3_prod__que6_ans2'),
                ('l1_prod__que7_ans2', 'l2_prod__que7_ans2', 'l3_prod__que7_ans2'),
                ('l1_prod__que8_ans2', 'l2_prod__que8_ans2', 'l3_prod__que8_ans2'),
                ('l1_prod__que9_ans2', 'l2_prod__que9_ans2', 'l3_prod__que9_ans2'),
                ('l1_prod__que10_ans2', 'l2_prod__que10_ans2', 'l3_prod__que10_ans2'),
                ('l1_prod__que11_ans2', 'l2_prod__que11_ans2', 'l3_prod__que11_ans2'),
                ('l1_prod__q12_ans2', 'l2_prod__q12_ans2', 'l3_prod__q12_ans2'),
            ]

            # Loop through each set of three columns and perform the comparison
            for i, (col1, col2, col3) in enumerate(columns_to_compare):
                result_df[f'compare_{i}_l1_l2'] = result_df[col1] == result_df[col2]
                result_df[f'compare_{i}_l1_l3'] = result_df[col1] == result_df[col3]
                result_df[f'compare_{i}_l2_l3'] = result_df[col2] == result_df[col3]
                new_column_col = f'new_column_{i}'
                new_columns_list.append(new_column_col)
                # Add the values
                result_df[f'new_column_{i}'] = (
                    result_df[f'compare_{i}_l1_l2'].astype(int) +
                    result_df[f'compare_{i}_l1_l3'].astype(int) +
                    result_df[f'compare_{i}_l2_l3'].astype(int)
                )

            # Drop the intermediate comparison columns if needed
            result_df = result_df.drop(columns=[f'compare_{i}_l1_l2' for i in range(len(columns_to_compare))] +
                                            [f'compare_{i}_l1_l3' for i in range(len(columns_to_compare))] +
                                            [f'compare_{i}_l2_l3' for i in range(len(columns_to_compare))])

            
            result_df.loc['Total number of zeros'] = result_df[new_columns_list].eq(0).sum()
            result_df.loc['Total number of ones'] = result_df[new_columns_list].eq(1).sum()
            result_df.loc['Total number of threes'] = result_df[new_columns_list].eq(3).sum()

            result_df.loc['Total of above three'] = result_df.loc['Total number of zeros'] + result_df.loc['Total number of ones'] + result_df.loc['Total number of threes']
          
            result_df.loc['percentage for '+str(fromdate)+' to '+str(todate)] = ((result_df.loc['Total number of ones'] + result_df.loc['Total number of threes']) / result_df.loc['Total of above three']) * 100

            percentage_df = pd.DataFrame(result_df.loc['percentage for '+str(fromdate)+' to '+str(todate)]).transpose()

            columns_to_remove = ['baseid__filename',
                    'baseid__batch_name',         
                    'l1_emp__employeeName',
                    'l1_emp__employeeID',
                    'l2_emp__employeeID',
                    'l1_loc',
                    'l2_emp__employeeName',
                    'l2_loc',
                    'id_value', 
                    'question', 
                    'asin', 
                    'title', 
                    'product_url', 
                    'imagepath', 
                    'evidence', 
                    'answer_one', 
                    'answer_two',
                    'l1_status',
                    'l2_status',
                    'l4_status',
                    'l3_status',
                    'l1_l2_accuracy',
                    'l1_prod__que1',
                    'l1_prod__que2',
                    'l1_prod__que2_1',
                    'l1_prod__que3',
                    'l1_prod__is_present_both',
                    'l1_prod__que4_ans1',
                    'l1_prod__que5_ans1', 
                    'l1_prod__que6_ans1', 
                    'l1_prod__que7_ans1',
                    'l1_prod__que8_ans1',
                    'l1_prod__que9_ans1',
                    'l1_prod__que10_ans1',
                    'l1_prod__que11_ans1',
                    'l1_prod__q12_ans1',
                    'l1_prod__que4_ans2',
                    'l1_prod__que5_ans2',
                    'l1_prod__que6_ans2',
                    'l1_prod__que7_ans2',
                    'l1_prod__que8_ans2',
                    'l1_prod__que9_ans2',
                    'l1_prod__que10_ans2',
                    'l1_prod__que11_ans2',
                    'l1_prod__q12_ans2',
                    'l2_prod__que1',
                    'l2_prod__que2',
                    'l2_prod__que2_1',
                    'l2_prod__que3',
                    'l2_prod__is_present_both',
                    'l2_prod__que4_ans1',
                    'l2_prod__que5_ans1', 
                    'l2_prod__que6_ans1', 
                    'l2_prod__que7_ans1',
                    'l2_prod__que8_ans1',
                    'l2_prod__que9_ans1',
                    'l2_prod__que10_ans1',
                    'l2_prod__que11_ans1',
                    'l2_prod__q12_ans1',
                    'l2_prod__que4_ans2',
                    'l2_prod__que5_ans2',
                    'l2_prod__que6_ans2',
                    'l2_prod__que7_ans2',
                    'l2_prod__que8_ans2',
                    'l2_prod__que9_ans2',
                    'l2_prod__que10_ans2',
                    'l2_prod__que11_ans2',
                    'l2_prod__q12_ans2',
                    'l3_prod__que1',
                    'l3_prod__que2',
                    'l3_prod__que2_1',
                    'l3_prod__que3',
                    'l3_prod__is_present_both',
                    'l3_prod__que4_ans1',
                    'l3_prod__que5_ans1', 
                    'l3_prod__que6_ans1', 
                    'l3_prod__que7_ans1',
                    'l3_prod__que8_ans1',
                    'l3_prod__que9_ans1',
                    'l3_prod__que10_ans1',
                    'l3_prod__que11_ans1',
                    'l3_prod__q12_ans1',
                    'l3_prod__que4_ans2',
                    'l3_prod__que5_ans2',
                    'l3_prod__que6_ans2',
                    'l3_prod__que7_ans2',
                    'l3_prod__que8_ans2',
                    'l3_prod__que9_ans2',
                    'l3_prod__que10_ans2',
                    'l3_prod__que11_ans2',
                    'l3_prod__q12_ans2']

            percentage_df = percentage_df.drop(columns=columns_to_remove)

            percentage_df.reset_index(inplace=True)

            melted_percentage_df = pd.melt(percentage_df)


            totaldata = pd.merge(totaldata, melted_percentage_df['value'],left_index=True, right_index=True,how='right')

            totaldata['questions'] = question_list[:len(totaldata)]

            totaldata.columns = totaldata.iloc[0]

            totaldata = totaldata[1:].reset_index(drop=True)

            totaldata.index = np.arange(1, len(totaldata) + 1)

            totaldata = totaldata[['Questions'] + [col for col in totaldata.columns if  col != 'Questions']]

            if key == 'Download':

                csv_data = totaldata.to_csv(index=True, encoding='utf-8')
                
                response = HttpResponse(csv_data, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="quality_report.csv"'
                return response
            
            else :
                tabledata = totaldata.to_html().replace('<table border="1" class="dataframe">','<table id="dftable" class="table table-hover">').replace('<thead>','<thead class="thead-light align-item-center">').replace('<tr style="text-align: right;">','<tr>').replace('<th></th>','<th>S.No</th>')  
                return render(request, 'pages/iaa.html', {'batchname':batchname,'tabledata':tabledata})
        # except Exception as e:
        #     return render(request, 'pages/iaa.html', {'batchname':batchname})

    return render(request, 'pages/iaa.html', {'batchname':batchname})


def iaa_date_wise(fromdate,todate,batchname_filter):
   
            raw_data_query = Q(l1_status="completed", l2_status="completed", l3_status="completed")

            if batchname_filter != "ALL":
                
                raw_data_query &= Q(baseid__batch_name=batchname_filter)

            raw_data_query &= Q(l1_prod__end_time__date__range=(fromdate, todate))
            raw_data_query &= Q(l2_prod__end_time__date__range=(fromdate, todate))
            raw_data_query &= Q(l3_prod__end_time__date__range=(fromdate, todate))

            

            raw_data_values = raw_data.objects.filter(raw_data_query).values('baseid__filename',
                    'baseid__batch_name',         
                    'l1_emp__employeeName',
                    'l1_emp__employeeID',
                    'l2_emp__employeeID',
                    'l1_loc',
                    'l2_emp__employeeName',
                    'l2_loc',
                    'id_value', 
                    'question', 
                    'asin', 
                    'title', 
                    'product_url', 
                    'imagepath', 
                    'evidence', 
                    'answer_one', 
                    'answer_two',
                    'l1_status',
                    'l2_status',
                    'l4_status',
                    'l3_status',
                    'l1_l2_accuracy',
                    'l1_prod__que1',
                    'l1_prod__que2',
                    'l1_prod__que2_1',
                    'l1_prod__que3',
                    'l1_prod__is_present_both',
                    'l1_prod__que4_ans1',
                    'l1_prod__que5_ans1', 
                    'l1_prod__que6_ans1', 
                    'l1_prod__que7_ans1',
                    'l1_prod__que8_ans1',
                    'l1_prod__que9_ans1',
                    'l1_prod__que10_ans1',
                    'l1_prod__que11_ans1',
                    'l1_prod__q12_ans1',
                    'l1_prod__que4_ans2',
                    'l1_prod__que5_ans2',
                    'l1_prod__que6_ans2',
                    'l1_prod__que7_ans2',
                    'l1_prod__que8_ans2',
                    'l1_prod__que9_ans2',
                    'l1_prod__que10_ans2',
                    'l1_prod__que11_ans2',
                    'l1_prod__q12_ans2',
                    'l2_prod__que1',
                    'l2_prod__que2',
                    'l2_prod__que2_1',
                    'l2_prod__que3',
                    'l2_prod__is_present_both',
                    'l2_prod__que4_ans1',
                    'l2_prod__que5_ans1', 
                    'l2_prod__que6_ans1', 
                    'l2_prod__que7_ans1',
                    'l2_prod__que8_ans1',
                    'l2_prod__que9_ans1',
                    'l2_prod__que10_ans1',
                    'l2_prod__que11_ans1',
                    'l2_prod__q12_ans1',
                    'l2_prod__que4_ans2',
                    'l2_prod__que5_ans2',
                    'l2_prod__que6_ans2',
                    'l2_prod__que7_ans2',
                    'l2_prod__que8_ans2',
                    'l2_prod__que9_ans2',
                    'l2_prod__que10_ans2',
                    'l2_prod__que11_ans2',
                    'l2_prod__q12_ans2',
                    'l3_prod__que1',
                    'l3_prod__que2',
                    'l3_prod__que2_1',
                    'l3_prod__que3',
                    'l3_prod__is_present_both',
                    'l3_prod__que4_ans1',
                    'l3_prod__que5_ans1', 
                    'l3_prod__que6_ans1', 
                    'l3_prod__que7_ans1',
                    'l3_prod__que8_ans1',
                    'l3_prod__que9_ans1',
                    'l3_prod__que10_ans1',
                    'l3_prod__que11_ans1',
                    'l3_prod__q12_ans1',
                    'l3_prod__que4_ans2',
                    'l3_prod__que5_ans2',
                    'l3_prod__que6_ans2',
                    'l3_prod__que7_ans2',
                    'l3_prod__que8_ans2',
                    'l3_prod__que9_ans2',
                    'l3_prod__que10_ans2',
                    'l3_prod__que11_ans2',
                    'l3_prod__q12_ans2')



            result_df = pd.DataFrame(raw_data_values)

            if result_df.empty:

                return result_df

            new_columns_list = []

            # List of columns to compare
            columns_to_compare = [
                ('l1_prod__que1', 'l2_prod__que1', 'l3_prod__que1'),
                ('l1_prod__que2', 'l2_prod__que2', 'l3_prod__que2'),
                ('l1_prod__que2_1', 'l2_prod__que2_1', 'l3_prod__que2_1'),
                ('l1_prod__que3', 'l2_prod__que3', 'l3_prod__que3'),
                ('l1_prod__is_present_both', 'l2_prod__is_present_both', 'l3_prod__is_present_both'),
                ('l1_prod__que4_ans1', 'l2_prod__que4_ans1', 'l3_prod__que4_ans1'),
                ('l1_prod__que5_ans1', 'l2_prod__que5_ans1', 'l3_prod__que5_ans1'),
                ('l1_prod__que6_ans1', 'l2_prod__que6_ans1', 'l3_prod__que6_ans1'),
                ('l1_prod__que7_ans1', 'l2_prod__que7_ans1', 'l3_prod__que7_ans1'),
                ('l1_prod__que8_ans1', 'l2_prod__que8_ans1', 'l3_prod__que8_ans1'),
                ('l1_prod__que9_ans1', 'l2_prod__que9_ans1', 'l3_prod__que9_ans1'),
                ('l1_prod__que10_ans1', 'l2_prod__que10_ans1', 'l3_prod__que10_ans1'),
                ('l1_prod__que11_ans1', 'l2_prod__que11_ans1', 'l3_prod__que11_ans1'),
                ('l1_prod__q12_ans1', 'l2_prod__q12_ans1', 'l3_prod__q12_ans1'),
                ('l1_prod__que4_ans2', 'l2_prod__que4_ans2', 'l3_prod__que4_ans2'),
                ('l1_prod__que5_ans2', 'l2_prod__que5_ans2', 'l3_prod__que5_ans2'),
                ('l1_prod__que6_ans2', 'l2_prod__que6_ans2', 'l3_prod__que6_ans2'),
                ('l1_prod__que7_ans2', 'l2_prod__que7_ans2', 'l3_prod__que7_ans2'),
                ('l1_prod__que8_ans2', 'l2_prod__que8_ans2', 'l3_prod__que8_ans2'),
                ('l1_prod__que9_ans2', 'l2_prod__que9_ans2', 'l3_prod__que9_ans2'),
                ('l1_prod__que10_ans2', 'l2_prod__que10_ans2', 'l3_prod__que10_ans2'),
                ('l1_prod__que11_ans2', 'l2_prod__que11_ans2', 'l3_prod__que11_ans2'),
                ('l1_prod__q12_ans2', 'l2_prod__q12_ans2', 'l3_prod__q12_ans2'),
            ]

            # Loop through each set of three columns and perform the comparison
            for i, (col1, col2, col3) in enumerate(columns_to_compare):
                result_df[f'compare_{i}_l1_l2'] = result_df[col1] == result_df[col2]
                result_df[f'compare_{i}_l1_l3'] = result_df[col1] == result_df[col3]
                result_df[f'compare_{i}_l2_l3'] = result_df[col2] == result_df[col3]
                new_column_col = f'new_column_{i}'
                new_columns_list.append(new_column_col)
                # Add the values
                result_df[f'new_column_{i}'] = (
                    result_df[f'compare_{i}_l1_l2'].astype(int) +
                    result_df[f'compare_{i}_l1_l3'].astype(int) +
                    result_df[f'compare_{i}_l2_l3'].astype(int)
                )

            # Drop the intermediate comparison columns if needed
            result_df = result_df.drop(columns=[f'compare_{i}_l1_l2' for i in range(len(columns_to_compare))] +
                                            [f'compare_{i}_l1_l3' for i in range(len(columns_to_compare))] +
                                            [f'compare_{i}_l2_l3' for i in range(len(columns_to_compare))])

            
            result_df.loc['Total number of zeros'] = result_df[new_columns_list].eq(0).sum()
            result_df.loc['Total number of ones'] = result_df[new_columns_list].eq(1).sum()
            result_df.loc['Total number of threes'] = result_df[new_columns_list].eq(3).sum()

            result_df.loc['Total of above three'] = result_df.loc['Total number of zeros'] + result_df.loc['Total number of ones'] + result_df.loc['Total number of threes']
          
            result_df.loc['percentage for '+str(fromdate)] = ((result_df.loc['Total number of ones'] + result_df.loc['Total number of threes']) / result_df.loc['Total of above three']) * 100

            percentage_df = pd.DataFrame(result_df.loc['percentage for '+str(fromdate)]).transpose()

            columns_to_remove = ['baseid__filename',
                    'baseid__batch_name',         
                    'l1_emp__employeeName',
                    'l1_emp__employeeID',
                    'l2_emp__employeeID',
                    'l1_loc',
                    'l2_emp__employeeName',
                    'l2_loc',
                    'id_value', 
                    'question', 
                    'asin', 
                    'title', 
                    'product_url', 
                    'imagepath', 
                    'evidence', 
                    'answer_one', 
                    'answer_two',
                    'l1_status',
                    'l2_status',
                    'l4_status',
                    'l3_status',
                    'l1_l2_accuracy',
                    'l1_prod__que1',
                    'l1_prod__que2',
                    'l1_prod__que2_1',
                    'l1_prod__que3',
                    'l1_prod__is_present_both',
                    'l1_prod__que4_ans1',
                    'l1_prod__que5_ans1', 
                    'l1_prod__que6_ans1', 
                    'l1_prod__que7_ans1',
                    'l1_prod__que8_ans1',
                    'l1_prod__que9_ans1',
                    'l1_prod__que10_ans1',
                    'l1_prod__que11_ans1',
                    'l1_prod__q12_ans1',
                    'l1_prod__que4_ans2',
                    'l1_prod__que5_ans2',
                    'l1_prod__que6_ans2',
                    'l1_prod__que7_ans2',
                    'l1_prod__que8_ans2',
                    'l1_prod__que9_ans2',
                    'l1_prod__que10_ans2',
                    'l1_prod__que11_ans2',
                    'l1_prod__q12_ans2',
                    'l2_prod__que1',
                    'l2_prod__que2',
                    'l2_prod__que2_1',
                    'l2_prod__que3',
                    'l2_prod__is_present_both',
                    'l2_prod__que4_ans1',
                    'l2_prod__que5_ans1', 
                    'l2_prod__que6_ans1', 
                    'l2_prod__que7_ans1',
                    'l2_prod__que8_ans1',
                    'l2_prod__que9_ans1',
                    'l2_prod__que10_ans1',
                    'l2_prod__que11_ans1',
                    'l2_prod__q12_ans1',
                    'l2_prod__que4_ans2',
                    'l2_prod__que5_ans2',
                    'l2_prod__que6_ans2',
                    'l2_prod__que7_ans2',
                    'l2_prod__que8_ans2',
                    'l2_prod__que9_ans2',
                    'l2_prod__que10_ans2',
                    'l2_prod__que11_ans2',
                    'l2_prod__q12_ans2',
                    'l3_prod__que1',
                    'l3_prod__que2',
                    'l3_prod__que2_1',
                    'l3_prod__que3',
                    'l3_prod__is_present_both',
                    'l3_prod__que4_ans1',
                    'l3_prod__que5_ans1', 
                    'l3_prod__que6_ans1', 
                    'l3_prod__que7_ans1',
                    'l3_prod__que8_ans1',
                    'l3_prod__que9_ans1',
                    'l3_prod__que10_ans1',
                    'l3_prod__que11_ans1',
                    'l3_prod__q12_ans1',
                    'l3_prod__que4_ans2',
                    'l3_prod__que5_ans2',
                    'l3_prod__que6_ans2',
                    'l3_prod__que7_ans2',
                    'l3_prod__que8_ans2',
                    'l3_prod__que9_ans2',
                    'l3_prod__que10_ans2',
                    'l3_prod__que11_ans2',
                    'l3_prod__q12_ans2']



            percentage_df = percentage_df.drop(columns=columns_to_remove)

            percentage_df.reset_index(inplace=True)

            melted_percentage_df = pd.melt(percentage_df)

            return melted_percentage_df['value']

    
