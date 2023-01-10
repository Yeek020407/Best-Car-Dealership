from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from .models import CarMake,CarModel
from .restapis import get_dealers_from_cf,get_dealer_by_id_from_cf,get_dealer_by_id,post_request
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context={}
    if request.method == "GET":
        return render(request,'djangoapp/about.html',context)


# Create a `contact` view to return a static contact page
def contact(request):
    context={}
    if request.method == "GET":
        return render(request,'djangoapp/contact_us.html',context)


def login_request(request):
    context={}
    if request.method == "POST":
        username=request.POST['username']
        password=request.POST['psw']
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('djangoapp:index')
        else:
            context['message']="Invalid username or password"
            return render(request,'djangoapp:login',context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context={}
    if request.method=="GET":
        return render(request,'djangoapp/sign_up.html',context)
    elif request.method=="POST":
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New User")
        
        if not user_exist:
            user = User.objects.create(username=username,password=password,first_name=first_name,last_name=last_name)
            login(request,user)
            return redirect('djangoapp:index')
        else:
            context['message']="User already exist"
            return render(request,'djangoapp/sign_up.html',context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/553466ab-3c3a-4993-af23-13d5e950cf92/default/dealership"
        dealerships = get_dealers_from_cf(url)
        context['dealers']=dealerships
        return render(request,'djangoapp/index.html',context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context={}
    if request.method =="GET":
        url1 = "https://us-south.functions.appdomain.cloud/api/v1/web/553466ab-3c3a-4993-af23-13d5e950cf92/default/review"
        url2 = "https://us-south.functions.appdomain.cloud/api/v1/web/553466ab-3c3a-4993-af23-13d5e950cf92/default/dealership"
        reviews = get_dealer_by_id_from_cf(url1,dealer_id)
        dealer_details = get_dealer_by_id(url2,dealer_id)
        context['reviews']=reviews
        context['dealer_details']=dealer_details
        return render(request,'djangoapp/dealer_details.html',context)





# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    user = request.user
    if request.method == "GET":
        if user.is_authenticated:
            context ={}
            carMake = CarMake.objects.all()
            url = "https://us-south.functions.appdomain.cloud/api/v1/web/553466ab-3c3a-4993-af23-13d5e950cf92/default/dealership"
            dealer_details = get_dealer_by_id(url,dealer_id)
            context['dealer_details']=dealer_details
            context['carMake']=carMake
            return render(request,'djangoapp/add_review.html',context)
        else:
            context={}
            context['message']="Please login/signup so that you can leave review for the dealers!"
            return render(request,'djangoapp/sign_up.html',context)
    elif request.method =="POST":
        context={}
        if user.is_authenticated:
            try:
                payload = {}
                review_details = {}
                review_details['dealership']=dealer_id
                review_details['name']  = user.first_name + " " + user.last_name
                request.POST['purchase']
                review_details['purchase'] = True
                review_details['review'] = request.POST.get('review')
                review_details['purchase_date'] =request.POST['purchase_date']
                carId = request.POST['car']
                carModel = get_object_or_404(CarModel,pk=carId)
                review_details['car_make'] = carModel.carMake.name
                review_details['car_model'] = carModel.name
                review_details['car_year'] = carModel.year
                review_details['id'] = user.id
                payload['review']=review_details
                url = "https://us-south.functions.appdomain.cloud/api/v1/web/553466ab-3c3a-4993-af23-13d5e950cf92/default/review"
                post_request(url,payload)

                #get dealer details
                url2 = "https://us-south.functions.appdomain.cloud/api/v1/web/553466ab-3c3a-4993-af23-13d5e950cf92/default/dealership"
                dealer_details = get_dealer_by_id(url2,dealer_id)
                context['dealer_details']=dealer_details

                context['message']="The review is successfully added!"
                return render(request,'djangoapp/add_review.html',context)

            except:
                payload = {}
                review_details = {}
                review_details['name']  = user.first_name + " " + user.last_name
                review_details['dealership']=dealer_id
                review_details['review'] = request.POST.get('review')
                review_details['purchase']=False
                review_details['purchase_date'] = False
                review_details['car_make'] = False
                review_details['car_model'] = False
                review_details['car_year'] = False
                review_details['id'] = user.id
                payload['review']=review_details
                url = "https://us-south.functions.appdomain.cloud/api/v1/web/553466ab-3c3a-4993-af23-13d5e950cf92/default/review"
                post_request(url,payload)
                context['message']="The review is successfully added!"
                
                # get dealer details
                url2 = "https://us-south.functions.appdomain.cloud/api/v1/web/553466ab-3c3a-4993-af23-13d5e950cf92/default/dealership"
                dealer_details = get_dealer_by_id(url2,dealer_id)
                context['dealer_details']=dealer_details

                return render(request,'djangoapp/add_review.html',context)
       

    
