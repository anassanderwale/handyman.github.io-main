from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .usermanager import HandymanUserManager
import random 


# service_choices is a list of tuples with two choices each
# The first choice is saved in database and the second one is for the frontend
# Both service_choices and category_choices are used in registering and editing the handyman profile
service_choices = [
    ('Painting', 'Painting'),
    ('Furniture Assembly', 'Furniture Assembly'),
    ('General Handyman', 'General Handyman'),
    ('Help Moving', 'Help Moving'),
    ('TV Mounting', 'TV Mounting'),
    ('Gardening and Removal', 'Gardening and Removing'),
    ('Disinfecting Services', 'Disinfecting Services'),
    ('IKEA Services', 'IKEA Services'),
    ('Electrician', 'Electrician'),
    ('Plumber', 'Plumber'),
    ('All Services', 'All Services'),

]


"""
HandymanUser is usermodel which diffrentiates between handyman and employer by their
 boolean field is_handyman and is_employer.
 It also contains bio, contact, services and categories by the handyman. 

"""


#HandymanUser is responsible for storing the information of all kinds of users in the database 
# every kind of user ( handyman, employer, superuser and staff ) are determined from the boolean fields give below
class HandymanUser(AbstractBaseUser, PermissionsMixin):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)

    email = models.EmailField(
        unique=True, 
        null=False,
        blank=False, 
        help_text="Email field can't be empty!")

    handyman_image = models.ImageField(upload_to='handymanimages', null=True, blank=True)    
    bio = models.CharField(max_length=2000, blank=True, null=True)
    contact = models.CharField(max_length=12, null=True, blank=True)
    address = models.CharField(max_length=2000, null=True, blank=True)
    postcode = models.CharField(max_length=10, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    handyman_rating = models.FloatField(default=0)
    handyman_rating_count = models.IntegerField(default=0)
    handyman_services = models.CharField(
        choices=service_choices, 
        default='All Services', 
        max_length=100,
        blank=False, 
        )
    date_joined = models.DateField(auto_now_add=True, null=True, blank=True)
    service_tags = models.CharField(max_length=200,  null=True, blank=True)

    is_customer = models.BooleanField(default=False)
    is_FixR = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELD = ['firstname', 'lastname']




    """
    Objects in the django models helps us work with database queries. 
    AbstractBaseUser a class which help us customise our user. We explicitly write customusermanager 
    for AbstractBaseUser to create user and superuser. CustomUserManager is imported from usermanager.py
    """
    objects = HandymanUserManager()

    class Meta:
        verbose_name_plural = "Custom Users"



    "Below is the method to render the handymanuser list with the firstname and lastname if they are provided."
    "Otherwise render by email."
    def __str__(self):
        if self.firstname and self.lastname:
            return str(self.firstname + " " + self.lastname)

        return self.email

    # def savetags(self):
    #     if self.handyman_category in tagdict:
    #         self.service_tags = tagdict
    #         return self.service_tags
    #     else:
    #         return self.handyman_category



# stores the booked service method and saves the handyman's and employer's data as foreinkeys
class Booked(models.Model):
    FixR = models.ForeignKey(HandymanUser, on_delete=models.CASCADE, related_name="booked_handyman")
    customer = models.ForeignKey(HandymanUser, on_delete=models.CASCADE, related_name="booked_employer", null=True, blank=True)
    hoursneeded = models.IntegerField(default=2, verbose_name="Hours Needed")
    duedate = models.DateField(verbose_name="Select Date")
    time = models.TimeField(verbose_name="Select Time")
    description = models.TextField(max_length=2000,   verbose_name="Describe Your Task", null=True, blank=True,)
    service_images = models.ImageField(upload_to='media/',  null=True, blank=True, verbose_name="Image of Task")
    date_time_created = models.DateTimeField(null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    is_declined = models.BooleanField(default=False)
    is_reviewed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)



    class Meta:
        verbose_name_plural = "Bookings"
        ordering = ('duedate',)

    def __str__(self):
        return str(self.FixR)





class Rate(models.Model):
    customer = models.ForeignKey(HandymanUser, related_name="customer_rating", on_delete=models.CASCADE)
    FixR = models.ForeignKey(HandymanUser, related_name="FixR_rating", on_delete=models.CASCADE)
    # rating_int = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = "Ratings"




