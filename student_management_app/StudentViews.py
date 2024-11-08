from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from student_management_app.models import CustomerUser,LeaveReportStudent,Students,FeedBackStudent,AttendanceReport,Subjects,Courses,Attendance,SessionYearModel
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import datetime

def student_home(request):
    student_obj=Students.objects.get(admin=request.user.id)
    attendance_total=AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present=AttendanceReport.objects.filter(student_id=student_obj,status=True).count()
    attendance_absent=AttendanceReport.objects.filter(student_id=student_obj,status=False).count()
    course=Courses.objects.get(id=student_obj.course_id.id)
    subjects=Subjects.objects.filter(course_id=course).count()

    #bar chart
    subject_name, data_present, data_absent=[],[],[]
    subject_data=Subjects.objects.filter(course_id=student_obj.course_id)
    for subject in subject_data:
        attendance=Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=True,student_id=student_obj.id).count()
        attendance_absent_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=False,student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)
    return render(request,'student_template/student_home_template.html',{'attendance_total':attendance_total,'attendance_present':attendance_present,'attendance_absent':attendance_absent,'subjects':subjects,'subject_name':subject_name,'data_present':data_present,'data_absent':data_absent})

def student_apply_leave(request):
    student_obj= Students.objects.get(admin=request.user.id)
    leave_data=LeaveReportStudent.objects.filter(student_id=student_obj)
    return render(request,'student_template/student_apply_leave.html',{'leave_data':leave_data})
    #return render(request,'student_template/student_apply_leave.html')

def student_apply_leave_save(request):
    if request.method!='POST':
        return HttpResponse('Method not allowed')
    else:
        leave_date=request.POST.get('leave_date')
        leave_reason=request.POST.get('leave_reason')
        try:
            student_obj=Students.objects.get(admin=request.user.id)
            leave_report=LeaveReportStudent.objects.create(student_id=student_obj,leave_date=leave_date,leave_message=leave_reason,leave_status=0)
            leave_report.save()
            messages.success(request,'Leave Applied Successfully')
            return HttpResponseRedirect('/student_apply_leave')
        except:
            messages.error(request,'Failed to Apply for Leave')
            return HttpResponseRedirect('/student_apply_leave')

def student_feedback(request):
    student_obj= Students.objects.get(admin=request.user.id)
    feedback_data=FeedBackStudent.objects.filter(student_id=student_obj)
    return render(request,'student_template/student_feedback_template.html',{'feedback_data':feedback_data})
    #return render(request,'student_template/student_feedback_template.html')
    
def student_feedback_save(request):
    if request.method!='POST':
        return HttpResponse('Method not allowed')
    else:
        feedback_message=request.POST.get('feedback')
        try:
            student_obj=Students.objects.get(admin=request.user.id)
            feedback_obj=FeedBackStudent.objects.create(student_id=student_obj,feedback=feedback_message,feedback_reply="")
            feedback_obj.save()
            messages.success(request,'Feedback Submitted Successfully')
            return HttpResponseRedirect('/student_feedback')
        except:
            messages.error(request,'Failed to Submit Feedback')
            return HttpResponseRedirect('/student_feedback')
        
def student_profile(request):
    user=CustomerUser.objects.get(id=request.user.id)
    return render(request,'student_template/student_profile.html',{'user':user})

def student_profile_save(request):
    if request.method!='POST':
        return HttpResponseRedirect('/student_profile')
    else:
        first_name=request.POST.get('firstname')
        last_name=request.POST.get('lastname')
        password=request.POST.get('password')
        try:
            customeruser=CustomerUser.objects.get(id=request.user.id)
            customeruser.first_name=first_name
            customeruser.last_name=last_name
            if password!=None and password!="":
                customeruser.set_password(password)
            customeruser.save()
            messages.success(request,"Successfully Updated Profile")
            return HttpResponseRedirect('/login')
        except:
            messages.error(request,"Failed to Update Profile")
            return HttpResponseRedirect('/student_profile')

def student_view_attendance(request):
    student=Students.objects.get(admin=request.user.id)
    course=Courses.objects.get(id=student.course_id.id)
    subjects=Subjects.objects.filter(course_id=course)
    return render(request,'student_template/student_view_attendance.html',{'subjects':subjects})

def student_view_attendance_past(request):
    subject_id=request.POST.get('subject_id')
    start_date=request.POST.get('start_date')
    end_date=request.POST.get('end_date')
    start_date_parse=datetime.datetime.strptime(start_date,"%Y-%m-%d").date()
    end_date_parse=datetime.datetime.strptime(end_date,"%Y-%m-%d").date()
    subject_obj=Subjects.objects.get(id=subject_id)
    user_object=CustomerUser.objects.get(id=request.user.id)
    stud_obj=Students.objects.get(admin=user_object)

    attendance=Attendance.objects.filter(attendance_date__range=(start_date_parse,end_date_parse),subject_id=subject_obj)
    attendance_reports=AttendanceReport.objects.filter(attendance_id__in=attendance,student_id=stud_obj)
    return render(request,'student_template/student_attendance_data.html',{'attendance_reports':attendance_reports})