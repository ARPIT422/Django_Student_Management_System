from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.contrib.auth import login,logout
from student_management_app.EmailBackEnd import EmailBackEnd
from django.core.files.storage import FileSystemStorage
from student_management_app.models import *
from django.contrib import messages
from django.urls import reverse

def front_page(request):
    return render(request,'front_template.html')

def login_user(request):
    return render(request,'login_page.html')

def signup_admin(request):
    return render(request,'admin_login.html')

def do_admin_signup(request):
    if request.method!="POST":
        return HttpResponse("<h2> Method not allowed <h2>")
    else:
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        try:
            user=CustomerUser.objects.create(username=username,email=email,user_type=1)
            user.set_password(password)
            user.save()
            messages.success(request,"Admin user created")
            return HttpResponseRedirect("/login")
        except Exception as e:
            messages.error(request,"Failed to create admin profile")
            return HttpResponseRedirect("/login")
        
def signup_student(request):
    courses=Courses.objects.all()
    sessionyears=SessionYearModel.objects.all()
    return render(request,'student_login.html',{'courses':courses,'sessionyears':sessionyears})

def do_student_signup(request):
    first_name = request.POST.get('firstname')
    last_name = request.POST.get('lastname')
    email=request.POST.get('email')
    username=request.POST.get('username')
    password=request.POST.get('password')
    address = request.POST.get('address')
    gender = request.POST.get('gender')
    course_id=request.POST.get('course')
    session_id=request.POST.get('session_id')
    profile_pic=request.FILES.get('profile_pic')
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
        return HttpResponseRedirect('/login')
    except Exception as e:
        print('--------------************-------------')
        print(e)
        messages.error(request,'Failed to Add Student')
        return HttpResponseRedirect('/login')

def signup_staff(request):
    return render(request,'staff_login.html')

def do_staff_signup(request):
    if request.method!="POST":
        return HttpResponse("<h2> Method not allowed <h2>")
    else:
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        address=request.POST.get('address')
        firstname=request.POST.get('firstname')
        lastname=request.POST.get('lastname')
        try:
            user=CustomerUser.objects.create(username=username,email=email,first_name=firstname,last_name=lastname,user_type=2)
            user.staffs.address=address
            user.set_password(password)
            user.save()
            messages.success(request,"Staff user created")
            return HttpResponseRedirect("/login")
        except Exception as e:
            messages.error(request,"Failed to create staff profile")
            return HttpResponseRedirect("/login")

def dologin(request):
    if request.method!="POST":
        return HttpResponse("<h2> Method not allowed <h2>")
    else:
        email=request.POST.get('email')
        password=request.POST.get('password')
        user=EmailBackEnd.authenticate(request,email=email,password=password)
        if user!=None:
            login(request,user)
            if user.user_type=='1':
                return HttpResponseRedirect('/admin_home')
            elif user.user_type=='2':
                return HttpResponseRedirect(reverse('staff_home'))
            else:
                return HttpResponseRedirect(reverse('student_home'))
        else:
            messages.error(request,'Invalid credentials')
            return HttpResponseRedirect('/login')
    
def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/login')
