#from student_management_app.models import CustomerUser,Staffs,Courses,Students,Subjects,SessionYearModel,Attendance,AttendanceReport,LeaveReportStaff,FeedBackStaff
from student_management_app.models import *
from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.urls import reverse
import json
def staff_home(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    course_id_list=[]
    for subject in subjects:
        course=Courses.objects.get(id=subject.course_id.id)
        course_id_list.append(course.id)
    final_course=list(set(course_id_list))
    #attendance count
    attendance_count=Attendance.objects.filter(subject_id__in=subjects).count()
    #leave count
    staff=Staffs.objects.get(admin=request.user.id)
    leave_count=LeaveReportStaff.objects.filter(staff_id=staff,leave_status=1).count()
    #student count
    student_count=Students.objects.filter(course_id__in=final_course).count()
    #subject count
    subject_counts = subjects.count()

    #bar chart
    subject_list=[]
    attendance_list=[]
    for subject in subjects:
        attendance_count1=Attendance.objects.filter(subject_id=subject).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance_count1)
    return render(request,'staff_template/staff_home_template.html',{'student_count':student_count,'attendance_count':attendance_count,'leave_count':leave_count,'subject_counts':subject_counts,'subject_list':subject_list,'attendance_list':attendance_list})

def staff_take_attendance(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    sessions=SessionYearModel.objects.all()
    return render(request,'staff_template/staff_take_attendance.html',{'subjects':subjects,'sessions':sessions})

@csrf_exempt
def get_students(request):
    subject_id=request.POST.get('subject_id')
    session_id=request.POST.get('session_year_id')
    sub_obj=Subjects.objects.get(id=subject_id)
    session_obj=SessionYearModel.objects.get(id=session_id)
    student_obj=Students.objects.filter(course_id=sub_obj.course_id,session_year_id=session_obj)
    list_data=[]
    for student in student_obj:
        data_small={'id':student.admin.id,'name':student.admin.first_name+" "+student.admin.last_name}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type='application/json',safe=False)

@csrf_exempt
def save_attendance_data(request):
    student_ids=request.POST.get('student_ids')
    subject_id=request.POST.get('subject_id')
    attendance_date=request.POST.get('attendance_date')
    session_year_id=request.POST.get('session_year_id')

    subject_model=Subjects.objects.get(id=subject_id)
    session_model=SessionYearModel.objects.get(id=session_year_id)
    json_student=json.loads(student_ids)
    attendance=Attendance(subject_id=subject_model,attendance_date=attendance_date,session_year_id=session_model)
    attendance.save()
    for stud in json_student:
        student=Students.objects.get(admin=stud['id'])
        attendance_report=AttendanceReport(student_id=student, attendance_id=attendance, status=stud['status'])
        attendance_report.save()
    return HttpResponse('okay')

def staff_update_attendance(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    session_year_id=SessionYearModel.objects.all()
    return render(request,'staff_template/staff_update_attendance.html',{'subjects':subjects,'session_year_id':session_year_id})
    
@csrf_exempt
def get_attendance_dates(request):
    subject=request.POST.get('subject_id')
    session_year_id=request.POST.get('session_year_id')

    subject_obj=Subjects.objects.get(id=subject)
    session_year_obj=SessionYearModel.objects.get(id=session_year_id)

    attendance=Attendance.objects.filter(subject_id=subject_obj,session_year_id=session_year_obj)
    attendance_obj=[]
    for attendance_single in attendance:
        data={'id':attendance_single.id,'attendance_date':str(attendance_single.attendance_date.strftime('%Y-%m-%d')),"session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)
    return JsonResponse(json.dumps(attendance_obj),safe=False)

@csrf_exempt
def get_attendance_student(request):
    attendance_date=request.POST.get('attendance_date')
    attendance=Attendance.objects.get(id=attendance_date)
    
    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]
    for student in attendance_data:
        data_small={'id':student.student_id.admin.id,'name':student.student_id.admin.first_name+" "+student.student_id.admin.last_name,'status':student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type='application/json',safe=False)

@csrf_exempt
def save_updateattendance_data(request):
    student_ids=request.POST.get('student_ids')
    attendance_date=request.POST.get('attendance_date')
    attendance=Attendance.objects.get(id=attendance_date)
    json_student=json.loads(student_ids)
    for stud in json_student:
        student=Students.objects.get(admin=stud['id'])
        attendance_report=AttendanceReport.objects.get(student_id=student, attendance_id=attendance)
        attendance_report.status=stud['status']
        attendance_report.save()
    return HttpResponse('okay')

def staff_apply_leave(request):
    staff_obj= Staffs.objects.get(admin=request.user.id)
    leave_data=LeaveReportStaff.objects.filter(staff_id=staff_obj)
    return render(request,'staff_template/staff_apply_leave.html',{'leave_data':leave_data})

def staff_feedback(request):
    staff_obj= Staffs.objects.get(admin=request.user.id)
    feedback_data=FeedBackStaff.objects.filter(staff_id=staff_obj)
    return render(request,'staff_template/staff_feedback_template.html',{'feedback_data':feedback_data})

def staff_apply_leave_save(request):
     if request.method!='POST':
        return HttpResponse('Method not allowed')
     else:
        leave_date=request.POST.get('leave_date')
        leave_reason=request.POST.get('leave_reason')
        try:
            staff_obj=Staffs.objects.get(admin=request.user.id)
            leave_report=LeaveReportStaff.objects.create(staff_id=staff_obj,leave_date=leave_date,leave_message=leave_reason,leave_status=0)
            leave_report.save()
            messages.success(request,'Leave Applied Successfully')
            return HttpResponseRedirect('/staff_apply_leave')
        except:
            messages.error(request,'Failed to Apply for Leave')
            return HttpResponseRedirect('/staff_apply_leave')
        
def staff_feedback_save(request):
    if request.method!='POST':
        return HttpResponse('Method not allowed')
    else:
        feedback_message=request.POST.get('feedback')
        try:
            staff_obj=Staffs.objects.get(admin=request.user.id)
            feedback_obj=FeedBackStaff.objects.create(staff_id=staff_obj,feedback=feedback_message,feedback_reply="")
            feedback_obj.save()
            messages.success(request,'Feedback Submitted Successfully')
            return HttpResponseRedirect('/staff_feedback')
        except Exception as e:
            print(e)
            messages.error(request,'Failed to Submit Feedback')
            return HttpResponseRedirect('/staff_feedback')
        
def staff_profile(request):
    user=CustomerUser.objects.get(id=request.user.id)
    staff=Staffs.objects.get(admin=user)
    return render(request,'staff_template/staff_profile.html',{'user':user,'staff':staff})


def staff_profile_save(request):
    if request.method!='POST':
        return HttpResponseRedirect('/staff_profile')
    else:
        first_name=request.POST.get('firstname')
        last_name=request.POST.get('lastname')
        address=request.POST.get('address')
        password=request.POST.get('password')
        try:
            customeruser=CustomerUser.objects.get(id=request.user.id)
            staff=Staffs.objects.get(admin=customeruser)
            customeruser.first_name=first_name
            customeruser.last_name=last_name
            staff.address=address
            if password!=None and password!="":
                customeruser.set_password(password)
            customeruser.save()
            staff.save()
            messages.success(request,"Successfully Updated Profile")
            return HttpResponseRedirect('/login')
        except Exception as e:
            print(e)
            messages.error(request,"Failed to Update Profile")
            return HttpResponseRedirect('/staff_profile')

def staff_add_result(request):
    subjects=Subjects.objects.get(id=request.user.id)
    return render(request,'staff_template/staff_add_result.html',{'subjects':subjects})