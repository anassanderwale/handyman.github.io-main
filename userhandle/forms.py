from cProfile import label
from re import A
from tkinter.ttk import Widget
from django import forms
from .models import Booked, HandymanUser, service_choices
from django.contrib.auth.password_validation import validate_password
from django.core import validators


"""
HandymanRegistration form takes cleaned data from html form and if the form data is valid then it is save to the data base. 
In views.py look for HandymanRegister function which uses this form to register the users. 
"""
class HandymanRegisterform(forms.Form):
    firstname = forms.CharField(required=True)
    lastname = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    zipcode = forms.CharField(max_length=8, required=True, help_text="Zipcome must be walid.")
    contact = forms.IntegerField(required=True, help_text="Contact must be valid.")
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()
    is_handyman = forms.BooleanField(required=False)
    is_employer = forms.BooleanField(required=False)

    def savepassword(self):
        if self.password1 != self.password2:
            raise ValueError("Password mismatch!")
        elif self.password1 == self.password:
            return self.password2





#HandymanProfileEditForm works with the existing users and edits the fields of the users which are handyman only. 
# widget of the forms are chages from python itself and we don't have to mention then in the html explicitly
class HandymanProfileEditForm(forms.Form):
    class Meta:
        model = HandymanUser
        fields = ('firstname', 'lastname', 'bio', 'service_tags', 'handyman_services', 'handyman_category')

        def __init__(self, *args, **kwargs):
            super().__init__(self, *args, **kwargs)
            self.fields['firstname'].widget.attrs.update({'class':'form-control'})
            self.fields['lastname'].widget.attrs.update({'class':'form-control'})
            self.fields['bio'].widget.attrs.update({'class':'form-control'})
            self.fields['handyman_services'].widget.attrs.update({'class':'form-control'})
            self.fields['handyman_category'].widget.attrs.update({'class':'form-control'})
            self.fields['firstservice_tagsname'].widget.attrs.update({'class':'form-control'})





# this converts the duedate field of the servicemodel from Character Field to the DateField 
# DateInput is used in the form ServiceRequestModelForm below
class DateInput(forms.DateInput):
    input_type = 'date'
    

class TimeInput(forms.TimeInput):
    input_type = 'time'


class ServiceBookingForm(forms.ModelForm):

    class Meta:
        model = Booked
        fields = ('description', 'duedate', 'time', 'hoursneeded', 'service_images' )
        widgets = {
            'duedate' : DateInput,
            'time' : TimeInput,
            
        }











#Booking form only filter the form data from the html form and doesn't save anything in the database
# Data from the booking form are only used to send the mail to handyman with information to date time and hours for the job
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booked
        fields = ('duedate','time', 'hoursneeded' )

        def __init__(self, *args, **kwargs):
            super().__init__(self, *args, **kwargs)
            self.fields['date'].widget.attrs.update({'class':'form-control-1'})
            self.fields['time'].widget.attrs.update({'class':'form-control-1'})
            self.fields['hours'].widget.attrs.update({'class':'form-control-1'})

