from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from .models import Booked, HandymanUser
from django.contrib.auth import authenticate , login, logout
from .forms import HandymanRegisterform
from django.db.models import Q
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import datetime
from .models import Rate
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
import re

# all the libraries of django and python are imported above to be used in the function below.



# index checks if the user is authenticated and what is the tag user has ( handyman or customer )
# and accordingly redirects them to eithsearch page or the index page with has profile and searvice functions
def index(request):  
    a = {}
    if request.user.is_authenticated:
        if request.user.is_customer:
            return redirect('handyman-search')
        elif request.user.is_FixR:            
            services = Booked.objects.all().filter(FixR_id=request.user.id, is_accepted=False, is_declined=False)
            current_time = datetime.datetime.now().time()             
            if len(services) == 0:
                service_flag = True
            elif len(services)>=1:
                service_flag = False
            context = {'services':services, 'current_time':current_time, 'service_flag':service_flag}
            return render(request, "index.html", context)
        return render(request, "index.html")
    else:
        return render(request, 'search.html' , a)


def previous_booking_list(request):
    if request.user.is_authenticated:
        if request.user.is_customer:
            services = Booked.objects.all().filter(customer=request.user)
            return render(request, 'previous_booking.html', {'services': services})
        elif request.user.is_FixR:
            return redirect('index')
    else:
        return redirect('handyman-login')
    

def handyman_rating_view(request, id, booking_id):
    try:
        handyman = HandymanUser.objects.get(id=id)
        booking = Booked.objects.get(id=booking_id)        
    except Exception as e:
        print(e)
    if Rate.objects.filter(FixR_id = id, customer_id=request.user.id).exists():
        messages.error(request, f'You have already given review to {handyman.firstname} {handyman.lastname}.')
        return HttpResponseRedirect(reverse('previous-booking'))
    else:            
        if request.method == "POST":
            current_rating = request.POST['rating']
            current_rating = int(current_rating)
            previous_rating = handyman.handyman_rating            
            if previous_rating == 0:
                final_rating = current_rating
            elif previous_rating >0:        
                final_rating = current_rating + previous_rating 
                final_rating = final_rating/2       
            handyman.handyman_rating = round(final_rating, 1)
            print(round(final_rating, 1))
            handyman.handyman_rating_count = handyman.handyman_rating_count + 1          
            handyman.save()
            Booked.objects.filter(FixR_id=handyman.id, customer_id=request.user.id).update(is_reviewed=True)
            Rate.objects.create(FixR_id = id, customer_id=request.user.id)
            return render(request, 'success_rating.html')
        else:
            print("rating not updated!")
            return render(request, 'rating_form.html', {'userdetails':handyman, 'booking':booking})



# In the handyman registrations logic if the method of the form is post then the following data is
# pushed to the HandymanRegisterForm and then saved in the database  
def HandymanRegister(request):
    form = HandymanRegisterform()
    special_character = "[()[\]{}|\\`~!@#$%^&*_\-+=;:\',<>./?]"
    if request.method == "POST":
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        contact = request.POST['contact']
        postcode = request.POST['postcode']
        password1 = request.POST['password1']
        password2 = request.POST['password2']  
        form = HandymanRegisterform(request.POST)  
        if password1 != password2:
            messages.error(request, "Password didn't match.")
            return render(request, 'registration.html')   
        elif len(password2) < 8:
            messages.error(request, 'Password should be atleast 8 characters. ')   
            return render(request, 'registration.html') 
        elif not re.findall('\d', password2):
            messages.error(request, 'Your password must contain a numeric value.')
            return render(request, 'registration.html')
        elif not re.findall('[A-Z]', password2):
            messages.error(request, "Password must contain atleast one capital letter. ")
            return render(request, "registration.html")
        elif not re.findall(special_character, password2):
            messages.error(request, 'Please include atleast one special character to your password.')
            messages.error(request, f"{special_character}")
            return render(request, 'registration.html')      
        location = 'UPDATE ADDRESS!'
        if HandymanUser.objects.filter(email=email).exists():
            messages.error(request, "Email address is taken. Please give another email address.")
            return render(request, "registration.html")
        if form.is_valid:
            if "is_FixR" in request.POST and "is_customer" in request.POST:
                messages.error(request, "You can't choose both hiring and working at the same time. Please choose one.")
                return redirect('handyman-registration')
            # if handyman checkbox is ticked then create an user with handyman flag 
            if "is_FixR" in request.POST:                
                HandymanUser.objects.create_user(
                email=email, firstname=firstname, lastname=lastname, 
                is_FixR=True, is_customer= False, password=password2,
                postcode = postcode, contact = contact,
                )
            elif "is_customer" in request.POST:
                HandymanUser.objects.create_user(
                email=email, firstname=firstname, lastname=lastname, 
                is_customer=True,is_FixR = False, password=password2,
                postcode = postcode, contact = contact,
                )
            # if none of the boxes are checked while registration this else statement belows throws an error and renders the registration
            # to create new registration.
            else:
                messages.error(request, "Form is not valid saved. ")
                print("form is not valid due to handyman flag! ")
                return render(request, "registration.html")           
            return redirect("handyman-login")
        else:
            messages.error(request, "Something went wrong. Please try again in sometime for Signup.")
            print("Something went wrong. Please try again in sometime for Signup.")
            return render(request, 'registration.html')
    return render(request, 'registration.html', {'form':form})



# Handyman logic takes the email and password data and using inbuild django authenticate on line 143
# it send the users to their respective location
def HandymanLogin(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        # checks if the user is already authenticated so the he doesn't have to login.
        if request.user.is_authenticated:
            return redirect('index')
        # login the user with the email and password provided from the html form     
        else: 
            handymanuser = authenticate(request, email=email, password=password)
            if handymanuser is not None:
                login(request, handymanuser)
                return redirect('index')
            else:
                messages.error(request, "Check email and password again")
                return render(request, 'login.html')
    else:
        return render(request, 'login.html')


# logout is django in build library to logout the user
def HandymanLogout(request):
    logout(request)
    return redirect("index")

#ChangePasswordView inherits PasswordChangeView of django and uses PasswordChangeForm as form class to 
# change password of the logged in user.
class ChangePasswordView(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'password_change.html'
    success_url = reverse_lazy('index')



# below is the profile edit logic built by generic view of django
# class ProfileEditViewHandyman inherits the UpdateView and edits the field mentioned in the "fields"
# UpdateView only cares about success_url i.e. where to redirect the user after editing the profile 
# it also takes the template anme and looks for the form in html and renders the fields which are supposed to be edited 
# below logic is only available for handyman user which are checked in the htm page. 
# look for {% if user.is_FixR %} in profile.html 
class ProfileEditViewHandyman(UpdateView):
    model = HandymanUser
    fields = ['firstname', 'lastname', 'bio', 'service_tags', 'handyman_services', 'price', 'handyman_image']
    template_name = 'profile.html'
    success_url = reverse_lazy('index')


# below is the profile edit logic built by generic view of django
# class ProfileEditViewcustomer inherits the UpdateView and edits the field mentioned in the "fields"
# this only edits firstname, lastname and contacts as an customer doesn't need to edit service and categories
class ProfileEditViewCustomer(UpdateView):
    model = HandymanUser
    fields = ['firstname', 'lastname', 'contact', 'handyman_image']
    template_name = 'profile.html'
    success_url = reverse_lazy('index')


# HandymanSearch looks for services, category and postcode from the home page and filters HandymanUser with the following data
# In the end it displays two instead of one list 
# The another list is of handymans with all service and all category in their profile
# both of the lists exclude if the user has customer or superuser flag
def HandymaSearch(request):
    services = request.POST.get('services')
    postcode = request.POST.get('zipcode')
    if services is not None and  postcode is not None:
        servicelist = HandymanUser.objects.filter(
                    Q(handyman_services=services )|
                    Q(postcode__contains=postcode)
                    ).exclude(
                        Q(is_customer=True)|
                        Q(is_superuser=True)
                        )
        for s in servicelist:
            s_id = s.id
        allservicelist = HandymanUser.objects.filter(
            Q(handyman_category="All Category")&
            Q(handyman_services="All Services")
            ).exclude(Q(is_customer=True)|
                        Q(is_superuser=True)|
                        Q(handyman_services=services )|
                        Q(postcode__contains=postcode)

                        ) 
        count  = 0
        nextcount = 0
        for s in servicelist:
            count+=1   
        for se in allservicelist:
            nextcount+=1      
        total = count+nextcount  
        if total == 0:
            total = "No handyman found!"
        elif total == 1:
            total = f"1 Handyman Found" 
        elif total>=1:
            total = f"{total} Handymans Found"  
        total_handyman_count = HandymanUser.objects.filter(is_FixR=True).count        
        context = {
            'servicelist':servicelist, 
            'allservicelist': allservicelist,
            'total_handyman_count':total_handyman_count,
            'total':total,          
            }
        return render(request, 'search_result.html', context)
    else: 
        return render(request, 'search.html')










# tags are added by the handyman during editing the profile
# tags help handyman to be found easily
# in SearchTags using the post.get method value of tag is saved and filtered through data base for a maching query
# tags go through handyman's category, tags, services and description and generated the best result
def SearchTags(request):    
    if request.method == "POST":
        tags = request.POST.get('tags')
        services = request.POST.get('services')
        postcode = request.POST.get('zipcode')
        servicelist = HandymanUser.objects.exclude(
            Q(is_superuser=True) |
            Q(is_customer=True))
        if services:
            servicelist = servicelist.filter(handyman_services=services)
        if postcode:
            servicelist = servicelist.filter(postcode__contains=postcode)
        if tags is not None:
            servicelist = servicelist.filter(
                Q(service_tags__contains=tags) |
                Q(handyman_services__contains=tags) |
                Q(bio__contains=tags)|
                Q(firstname__contains=tags)|
                Q(lastname__contains=tags)).exclude(Q(is_FixR=False))
            count = len(servicelist)        
            total = count
            if total == 0:
                total = "No handyman found!"
            elif total == 1:
                total = "1 Handyman Found"
            elif total >= 1:
                total = f"{total} Handymen Found"
            context = {'servicelist': servicelist, "total": total}
            return render(request, 'search_result.html', context)
        else:
            pass
    else:
        return HttpResponseRedirect(reverse('search-tags'))


# fetch an user with id from the data base 
# this id is taken from the html page
def SearchDetailView(request, id):
    from .forms import ServiceBookingForm
    user = request.user
    try:
        userdetails = HandymanUser.objects.get(id=id)
    except ValueError as ne:
        print(ne)
        messages.error(request, f"Sorry the user with id {id} doens't exists")
    if user.is_authenticated and user.is_customer:
        form = ServiceBookingForm()
        return render(request, 'selected_user_details.html', {'userdetails':userdetails, 'form':form})
    if user.is_anonymous:
        return redirect('handyman-login')
    else:
        return render(request, '404.html')




# every service in database have boolean is_booked to be False by default and this function saves them to be true
# if they are accepted by a handyman then the item is moved to the approved section 
def HandymanAccept(request, id):
    user  = request.user

    services = Booked.objects.get(id=id)
    subject = 'Booking Accepted!'
    plain_message = f"FixR, {request.user}, has accepted the Booking Request made by you on {services.duedate}."
    plain_message_fixr = f"You have successfuly accepted the booking made by {services.customer}."
    from_email = f'Kwik-FixR <{request.user.email}>'
    to = str(f'{services.customer.email}')
    to_fixr = str(f'{services.FixR.email}')

    if services.is_accepted == False:
        services.is_accepted = True
        services.save()
        mail.send_mail(subject, plain_message, from_email, [to],)
        mail.send_mail(subject, plain_message_fixr, from_email, [to_fixr],)
        messages.success(request, f"You have accepted the request made by {services.customer.firstname} {services.customer.lastname}.")
        return redirect('index')

    else:
        services.is_accepted = False
        services.save()
        return HttpResponseRedirect(reverse('index'))


# this function has the same logic but it turns the is_declined boolean of the servicemodel to True 
# onle services with the boolean is_declined False are displayed to handyman 
def HandymanDecline(request, id):
    services = Booked.objects.get(id=id)
    subject = 'Booking Declined!'
    plain_message = f"FixR, {request.user}, has declined the Booking Request made by you on {services.duedate}."
    plain_message_fixr = f'You have declined the booking made by {services.customer}'
    from_email = f'Kwik-FixR <{request.user.email}>'
    to = str(f'{services.customer.email}') 
    to_fixr = str(f'{services.FixR.email}')
    if services.is_declined == False:
        services.is_declined = True
        services.save()
        mail.send_mail(subject, plain_message, from_email, [to],)
        mail.send_mail(subject, plain_message_fixr, from_email, [to_fixr],)
        messages.success(request, f"You have declined the request made by {services.customer.firstname} {services.customer.lastname}.")
        return HttpResponseRedirect(reverse('index'))
    else:
        services.is_declined = False
        services.save()
        return HttpResponseRedirect(reverse('index'))

def HandymanComplete(request, id):
    service = Booked.objects.get(id=id)
    subject = 'Booking complete!'
    plain_message = f"FixR, {service.FixR}, has completed the Booking Request made by you on {service.duedate}. You may give ratings to the FixR now."
    plain_message_fixr = f'You have completed the booking made by {service.customer}.'
    from_email = f'Kwik-FixR <{request.user.email}>'
    to = str(f'{service.customer.email}') 
    to_fixr = str(f'{service.FixR.email}')
    if service.is_completed == False:
        service.is_completed = True
        service.save()
        mail.send_mail(subject, plain_message, from_email, [to],)
        mail.send_mail(subject, plain_message_fixr, from_email, [to_fixr],)
        messages.success(request, f'You have marked the booking from {service.customer.firstname} {service.customer.lastname}.')
        return HttpResponseRedirect(reverse('service-approved'))
    else:
        service.is_completed = False
        service.save()
        return HttpResponseRedirect(reverse('service-approved'))


def HandymanServiceApproved(request):
    serviceIsAccepted = Booked.objects.all().filter(FixR_id=request.user.id, is_accepted=True)
    current_time = datetime.datetime.now().time()
    context = {'services': serviceIsAccepted, 'current_time': current_time}
    return render(request, 'service_approved.html', context)


def HandymanServiceApprovedDetails(request, id):
    customer = Booked.objects.get(id=id)
    return render(request, "approved_customer_detail.html", {'booking':customer})




#BookService does a couple of things:
# It records date, time and hours from the customer (This data is not saved but only send to the customer after booking is done).
# subject of the mail is stored and html file is converted in string to send the mail to browers supporting html and strings
# plaing messages removes the html tags like <body> <div> and <head> from the html 
#finally if the email address of the handyman is valid then handyman will recieve a mail from Handyman00789@gmail.com
# Handyman00789@gmail.com is companies mail to send to the users  
def BookService(request, id):
    from .forms import ServiceBookingForm
    user = request.user 
    try:
        service = HandymanUser.objects.get(id=id)        
    except Exception:
        messages.error(request, "Failed to book service! Please try again in sometime.")
        return render(request, 'selected_user_details.html')
    if user.is_authenticated and user.is_customer:  
        if request.method == "POST":
            if Booked.objects.filter(Q(FixR_id=id) & Q(customer_id=user.id) & Q(is_accepted=False) & Q(is_declined=False)).exists():
                failed_message1 = 'You have requested a existing booking to this FixR.'
                failed_message2 = 'Please wait for them to either accept or decline.'
                context = {'failed_message1':failed_message1, 'failed_message2':failed_message2}
                return render(request, 'booking_failed.html', context)          
            form = ServiceBookingForm(request.POST, request.FILES )
            if form.is_valid():               
                form_duedate = form.cleaned_data['duedate']             
                if Booked.objects.filter(Q(FixR_id=id)& Q(duedate=form_duedate) &Q(is_completed=False)).exists():
                    failed_message1 = 'This FixR is booked on the date you have chosen.'
                    failed_message2 = 'Please go back and choose another date.'
                    context = {'failed_message1':failed_message1, 'failed_message2':failed_message2}
                    return render(request, 'booking_failed.html', context)
                frm = form.save(commit=False)
                frm.FixR = service
                frm.customer = request.user
                frm.date_time_created = datetime.date.today()
                frm.save()
                context = {'handyman':service, 'user':user}
                subject = 'Booking done from Kwik-is_FixR!'
                subject_customer = f'Booking Request successfull!'
                html_message = render_to_string('booked_mail.html', context)
                plain_message = strip_tags(html_message)
                plain_message_to_customer = f'Booking Request successfull to {service.firstname} {service.lastname}'
                from_email = f'Kwik-is_FixR <{user.email}>'
                to_FixR = str(f'{service.email}')
                to_customer = str(f'{user.email}')
                mail.send_mail(subject, plain_message, from_email, [to_FixR], html_message=html_message)
                mail.send_mail(subject_customer, plain_message_to_customer, from_email, [to_customer] )
                return render(request, "success_booking.html")
            else:
                print("Booking form is not saved!")
                return redirect('handyman-booking')
        else: 
            form = ServiceBookingForm()
            request.session['form'] = form 
            return reverse('handyman-booking')

    elif user.is_FixR:
        messages.error(request, "Users with FixR account can't request bookings.")
        return redirect('index')
    else:
        return redirect('handyman-login')



