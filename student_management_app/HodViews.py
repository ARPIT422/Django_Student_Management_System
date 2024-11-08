from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from student_management_app.models import CustomerUser,Staffs,Courses,Students,Subjects,SessionYearModel,FeedBackStudent,FeedBackStaff,LeaveReportStudent,LeaveReportStaff,Attendance,AttendanceReport
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
import json

def admin_home(request):
    #for cards
    student_count=Students.objects.all().count()
    staff_count=Staffs.objects.all().count()
    course_count=Courses.objects.all().count()
    subject_count=Subjects.objects.all().count()
    print('----------*************------------')
    print(student_count)
    #donut chart
    #total student in each course
    course_name,subject_count_list=[],[]
    student_count_list_in_courses=[]
    course_all=Courses.objects.all()
    for course in course_all:
        students=Students.objects.filter(course_id=course.id).count()
        subjects=Subjects.objects.filter(course_id=course.id).count()
        course_name.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_courses.append(students)
    
    #total students in each subject
    subjects_all=Subjects.objects.all()
    subject_list, student_count_list_in_subject=[],[]
    subjects=Students.objects.all()
    for subject in subjects_all:
        course=Courses.objects.get(id=subject.course_id.id)
        student_count=Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)

    #bar chart(#staff leave vs attendance)
    staffs=Staffs.objects.all()
    attendance_present_list_staff,attendance_absent_list_staff=[],[]
    staff_name_list=[]
    for staff in staffs:
        subjects_ids=Subjects.objects.filter(staff_id=staff.admin.id)
        attendance=Attendance.objects.filter(subject_id__in=subjects_ids).count()
        leaves=LeaveReportStaff.objects.filter(staff_id=staff.id,leave_status=1).count()
        attendance_present_list_staff.append(attendance)
        attendance_absent_list_staff.append(leaves)
        staff_name_list.append(staff.admin.username)
    return render(request,'hod_template/home.html',{'student_count':student_count,'staff_count':staff_count,'course_count':course_count,'subject_count':subject_count,'course_name':course_name,'subject_count_list':subject_count_list,'student_count_list_in_courses':student_count_list_in_courses,'subject_list':subject_list,'student_count_list_in_subject':student_count_list_in_subject,'attendance_present_list_staff':attendance_present_list_staff,'attendance_absent_list_staff':attendance_absent_list_staff,'staff_name_list':staff_name_list})


#add staff page view only
def add_staff(request):
    return render(request,'hod_template/add_staff_template.html')

#adding staff
def add_staff_save(request):
    if request.method!='POST':
        return HttpResponse("Method Not Allowed")
    else:
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email=request.POST.get('email')
        username=request.POST.get('username')
        password=request.POST.get('password')
        address=request.POST.get('address')
        try:
            user=CustomerUser.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password,user_type=2)
            user.staffs.address=address
            user.save()
            messages.success(request,'Staff Added Successfully')
            return HttpResponseRedirect('/add_staff')
        except Exception as e:
            print(e)
            messages.error(request,'Failed to Add Staff')
            return HttpResponseRedirect('/add_staff')
        
def add_course(request):
    return render(request,'hod_template/add_course_template.html')

def add_course_save(request):
    if request.method!='POST':
        return HttpResponse('Method not allowed')
    else:
        course_name=request.POST.get('coursename')
        try:
            course_model = Courses(course_name=course_name)
            course_model.save()
            messages.success(request,'Course Added Successfully')
            return HttpResponseRedirect('/add_course')
        except:
            messages.error(request,'Failed to Add Course')

def add_student(request):
    courses = Courses.objects.all()
    session_model=SessionYearModel.objects.all()
    return render(request,'hod_template/add_student_template.html',{'courses':courses,'sessions':session_model})

def add_student_save(request):
    if request.method!='POST':
        return HttpResponse('Method not allowed')
    else:
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email=request.POST.get('email')
        username=request.POST.get('username')
        password=request.POST.get('password')
        address=request.POST.get('address')
        gender=request.POST.get('gender')
        course_id=request.POST.get('courses')
        session_id=request.POST.get('session_id')
        profile_pic=request.FILES['profile_pic']
        fs=FileSystemStorage()
        filename=fs.save(profile_pic.name,profile_pic)
        profile_pic_url=fs.url(filename)
        try:
            user=CustomerUser.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password,user_type=3)
            user.students.address=address
            user.students.gender=gender
            course_obj=Courses.objects.get(id=course_id)
            user.students.course_id=course_obj
            user.students.profile_pic=""
            session_obj=SessionYearModel.objects.get(id=session_id)
            user.students.session_year_id=session_obj
            user.students.profile_pic=profile_pic_url
            user.save()
            messages.success(request,'Student Added Successfully')
            return HttpResponseRedirect('/add_student')
        except:
            messages.error(request,'Failed to Add Student')
            return HttpResponseRedirect('/add_student')

def add_subject(request):
   courses = Courses.objects.all()
   staffs=CustomerUser.objects.filter(user_type=2)
   return render(request,'hod_template/add_subject_template.html',{'courses':courses,'staffs':staffs})

def add_subject_save(request):
    if request.method!='POST':
        return HttpResponse('Method not allowed')
    else:
        subject_name=request.POST.get('subject_name')
        course_id=request.POST.get('course')
        course=Courses.objects.get(id=course_id)
        staff_id=request.POST.get('staff')
        staff=CustomerUser.objects.get(id=staff_id)
        try:
            subject=Subjects.objects.create(subject_name=subject_name,course_id=course,staff_id=staff)
            subject.save()
            messages.success(request,'Subjects Added Successfully')
            return HttpResponseRedirect('/add_subject')
        except Exception as e:
            print(e)
            messages.error(request,'Failed to Add Subjects')
            return HttpResponseRedirect('/add_subject')

def manage_staff(request):
    staffs=Staffs.objects.all()
    return render(request,'hod_template/manage_staff_template.html',{'staffs':staffs})

def manage_student(request):
    students=Students.objects.all()
    return render(request,'hod_template/manage_student_template.html',{'students':students})

def manage_course(request):
    courses=Courses.objects.all()
    return render(request,'hod_template/manage_course_template.html',{'courses':courses})

def manage_subject(request):
    subjects=Subjects.objects.all()
    return render(request,'hod_template/manage_subject_template.html',{'subjects':subjects})

def edit_staff(request,staff_id):
    staff=Staffs.objects.get(admin=staff_id)
    return render(request,'hod_template/edit_staff_template.html',{'staff':staff,'id':staff_id})

def edit_staff_save(request):
    if request.method!='POST':
        return HttpResponse('Method not allowed')
    else:
        email=request.POST.get('email')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        address=request.POST.get('address')
        staff_id=request.POST.get('staff_id')
        try:
            user=CustomerUser.objects.get(id=staff_id)
            staff_model=Staffs.objects.get(admin=staff_id)
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.save()
            staff_model.address=address
            staff_model.save()
            messages.success(request,"Succefully edited staff")
            return HttpResponseRedirect(reverse('edit_staff',kwargs={'staff_id':staff_id}))
        except:
            messages.error(request,'failed to edit staff')
            return HttpResponseRedirect(reverse('edit_staff',staff_id))

def edit_student(request,student_id):
    courses=Courses.objects.all()
    sessions=SessionYearModel.objects.all()
    student=Students.objects.get(admin=student_id)
    return render(request,'hod_template/edit_student_template.html',{'student':student,'courses':courses,'sessions':sessions,'id':student_id})

def edit_student_save(request):
     if request.method!='POST':
        return HttpResponse('Method not allowed')
     else:
        email=request.POST.get('email')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        username=request.POST.get('username')
        address=request.POST.get('address')
        course_id=request.POST.get('course')
        session_id=request.POST.get('session_id')
        session_obj=SessionYearModel.objects.get(id=session_id)
        student_id=request.POST.get('student_id')
        if request.FILES.get('profile_pic',False): 
            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
        else:
            profile_pic_url=None

        try:
            user=CustomerUser.objects.get(id=student_id)
            student_model=Students.objects.get(admin=student_id)
            course=Courses.objects.get(id=course_id)
            
            user.first_name=first_name
            user.last_name=last_name
            user.email=email
            user.username=username
            user.save()
            student_model.address=address
            student_model.session_year_id=session_obj
            student_model.course_id=course
            if profile_pic_url:
                student_model.profile_pic=profile_pic_url
            student_model.save()
            messages.success(request,"Succefully edited Students")
            return HttpResponseRedirect('/edit_student/'+student_id)
        except Exception as e:
            print(e)
            messages.error(request,'failed to edit staff')
            return HttpResponseRedirect('/edit_student/'+student_id)

def edit_subject(request,subject_id):
    courses=Courses.objects.all()
    staffs=CustomerUser.objects.filter(user_type=2)
    subject_model=Subjects.objects.get(id=subject_id)
    return render(request,'hod_template/edit_subject_template.html',{'subject':subject_model,'courses':courses,'staffs':staffs,'id':subject_id})
    

def edit_subject_save(request):
    if request.method!='POST':
        return HttpResponse('Method not allowed')
    else:
        subject_name=request.POST.get('subject_name')
        course_id=request.POST.get('course_id')
        staff_id=request.POST.get('staff_id')
        subject_id=request.POST.get('subject_id')
        try:
            sub_model=Subjects.objects.get(id=subject_id)
            course_model=Courses.objects.get(id=course_id)
            staff=CustomerUser.objects.get(id=staff_id)
            sub_model.subject_name=subject_name
            sub_model.staff_id=staff
            sub_model.course_id=course_model
            sub_model.save()
            messages.success(request,"Succefully edited Subjects")
            return HttpResponseRedirect('/edit_subject/'+subject_id)
        except:
            messages.error(request,"Failed to Subjects")
            return HttpResponseRedirect('/edit_subject/'+subject_id)

def edit_course(request,course_id):
    course_model=Courses.objects.get(id=course_id)
    return render(request,'hod_template/edit_course_template.html',{'course':course_model,'id':course_id})

def edit_course_save(request):
    if request.method!='POST':
        return HttpResponse('Method not allowed')
    else:
        course_name=request.POST.get('coursename')
        course_id=request.POST.get('course_id')
        try:
            course=Courses.objects.get(id=course_id)
            course.course_name=course_name
            course.save()
            messages.success(request,"Succefully edited course")
            return HttpResponseRedirect('/edit_course/'+course_id)
        except:
            messages.error(request,'failed to edit course')
            return HttpResponseRedirect('/edit_student/'+course_id)
        
def manage_session(request):
    return render(request,'hod_template/manage_session_template.html')

def manage_session_save(request):
    if request.method!='POST':
        return HttpResponse('Method not allowed')
    else:
        start_year=request.POST.get('start_year')
        end_year=request.POST.get('end_year')
        try:
            session_model=SessionYearModel.objects.create(session_start_year=start_year,session_end_year=end_year)
            session_model.save()
            messages.success(request,"Session Year Added Successfully")
            return HttpResponseRedirect('/manage_session')
        except:
            messages.error(request,'failed to Add session')
            return HttpResponseRedirect('/manage_session')
        
def student_feedback_message(request):
    feedbacks=FeedBackStudent.objects.all()
    return render(request,'hod_template/student_feedback_template.html',{'feedbacks':feedbacks})

def staff_feedback_message(request):
    feedbacks=FeedBackStaff.objects.all()
    return render(request,'hod_template/staff_feedback_template.html',{'feedbacks':feedbacks})

def student_leave_view(request):
    leaves=LeaveReportStudent.objects.all()
    return render(request,'hod_template/student_leave_template.html',{'leaves':leaves})

@csrf_exempt 
def student_feedback_message_replied(request):
    if request.method!='POST':
        return HttpResponse('Method not allowed')
    else:
        feedback_id=request.POST.get('id')
        feedback_message=request.POST.get('message')
        try:
            feedback=FeedBackStudent.objects.get(id=feedback_id)
            feedback.feedback_reply=feedback_message
            feedback.save()
            return HttpResponse('True')
        except Exception as e:
            return HttpResponse('False')
@csrf_exempt
def staff_feedback_message_replied(request):
    if request.method!='POST':
        return HttpResponse('Method not allowed')
    else:
        feedback_id=request.POST.get('id')
        feedback_message=request.POST.get('message')
        try:
            feedback=FeedBackStaff.objects.get(id=feedback_id)
            feedback.feedback_reply=feedback_message
            feedback.save()
            return HttpResponse('True')
        except Exception as e:
            return HttpResponse('False')

def student_approve_leave(request,leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect('/student_leave_view')

def student_disapprove_leave(request,leave_id):
    leave=LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect('/student_leave_view')


def staff_leave_view(request):
    leaves=LeaveReportStaff.objects.all()
    return render(request,'hod_template/staff_leave_template.html',{'leaves':leaves})

def staff_approve_leave(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=1
    leave.save()
    return HttpResponseRedirect('/staff_leave_view')

def staff_disapprove_leave(request,leave_id):
    leave=LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status=2
    leave.save()
    return HttpResponseRedirect('/staff_leave_view')

def admin_profile(request):
    user=CustomerUser.objects.get(id=request.user.id)
    return render(request,'hod_template/admin_profile.html',{'user':user})

def admin_profile_save(request):
    if request.method!='POST':
        return HttpResponseRedirect('/admin_profile')
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
            return HttpResponseRedirect('/admin_profile')
        
def admin_view_attendance(request):
    subjects=Subjects.objects.all()
    session_year_id=SessionYearModel.objects.all()
    return render(request,'hod_template/admin_view_attendace.html',{'subjects':subjects,'session_year_id':session_year_id})

@csrf_exempt
def admin_get_attendance_dates(request):
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
def admin_get_attendance_student(request):
    attendance_date=request.POST.get('attendance_date')
    attendance=Attendance.objects.get(id=attendance_date)
    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]
    for student in attendance_data:
        data_small={'id':student.student_id.admin.id,'name':student.student_id.admin.first_name+" "+student.student_id.admin.last_name,'status':student.status}
        list_data.append(data_small)
    return JsonResponse(json.dumps(list_data),content_type='application/json',safe=False)

@csrf_exempt
def check_email_exist(request):
    email=request.POST.get('email')
    user_obj=CustomerUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)
    
@csrf_exempt
def check_username_exist(request):
    username=request.POST.get('username')
    user_obj=CustomerUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)