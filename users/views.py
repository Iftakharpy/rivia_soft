from django.http.response import Http404, HttpResponse, HttpResponseForbidden
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict


# models and forms
from .models import CustomUser
from .forms import CustomUserChangeForm, CustomUserLoginForm, CustomUserCreationForm, CustomUserSignupForm

# queries
from .queries import search_CustomUser, search_CustomUser_by_email

# serializer
from .serializers import CustomUserSerializer

from companies.url_variables import APPLICATION_NAME, URL_NAMES, URL_PATHS, Full_URL_PATHS_WITHOUT_ARGUMENTS, URL_NAMES_PREFIXED_WITH_APP_NAME
from companies.url_variables import *


application_name = APPLICATION_NAME
# these path names will be passed to templates to use in the navbar links
URLS = {
  'home': f'{application_name}:home',

  **Full_URL_PATHS_WITHOUT_ARGUMENTS.get_dict(),
  **URL_NAMES_PREFIXED_WITH_APP_NAME.get_dict()
}


# Create your views here.
def signup_user(request):
    context = {}
    context['form']= CustomUserSignupForm()
    if request.method == 'POST':
        form = CustomUserSignupForm(request.POST)
        context['form'] = form
        if form.is_valid():
            user = form.save(commit=False)
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            next_url = request.POST.get('next')
            user.is_active = True
            user.save()

            user = authenticate(email=email, password=password)
            if user:
                # if authenticated then let the user login
                login(request, user)
                if next_url:
                    return redirect(next_url)
                return redirect('/')
    return render(request, 'users/signup.html', context=context)

def login_user(request):
    context = {'form': CustomUserLoginForm()}
    if request.method=='POST':
        form = CustomUserLoginForm(request.POST)
        context['form'] = form
        if form.is_valid():
            email = request.POST.get('email')
            password = request.POST.get('password')
            next_url = request.POST.get('next')
            # see if the user can login with the creedentials
            user = authenticate(request=request, email=email, password=password)
            if user:
                # if authenticated then let the user login
                login(request, user)
                if next_url:
                    return redirect(next_url)
                return redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Merged_Tracker_home_name)
        context['message'] = 'Incorrect email or password.'
    return render(request, 'users/login.html', context=context)

@login_required
def logout_user(request):
    logout(request)
    return redirect('users_login')

@login_required
def update_user(request, user_id=None):
    user = get_object_or_404(CustomUser, user_id=user_id)
    if user_id!=request.user.user_id or user_id==None:
        return HttpResponseForbidden()
    context = {
        **URLS,
        'page_title': f'Update Limited',
        'view_url': URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_home_name,
        'id': request.user.user_id,
        'update_url':  URL_NAMES_PREFIXED_WITH_APP_NAME.Limited_update_name,
        'form_title': 'Limited Update Form',
        'form': CustomUserChangeForm(instance=user)
    }
    if request.method=='POST':
        form = CustomUserChangeForm()
    return render(request, 'users/update_info.html', context = context)


# Content-type to return the search results
content_type = 'application/json'
# serialize the results with the format
serialize_format = 'json'

def serialize_queryset_to_json(queryset):
    data = serialize(queryset=queryset, format=serialize_format)
    return data

@login_required
def search_users_by_email(request, search_text='', limit=-1):
    if request.method=='GET' and request.headers.get('Content-Type')==content_type:
        results = search_CustomUser_by_email(search_text, limit)
        return HttpResponse(serialize_queryset_to_json(results), content_type=content_type)
    raise Http404()

@login_required
def search_users_extended(request, limit=-1):
    if request.method=='GET' and request.headers.get('Content-Type')==content_type:
        search_text = request.GET.get('q', '')
        results = search_CustomUser(search_text, limit)
        return HttpResponse(serialize_queryset_to_json(results), content_type=content_type)
    raise Http404()

@login_required
def all_users(request):
    if request.method=='GET' and request.headers.get('Content-Type')==content_type:
        results = CustomUser.objects.all()
        return HttpResponse(serialize_queryset_to_json(results), content_type=content_type)
    raise Http404()

@login_required
def get_user_details(request, user_id=None):
    if request.method=='GET' and request.headers.get('Content-Type')=='application/json':
        record = get_object_or_404(CustomUser, user_id=user_id)
        response = CustomUserSerializer(instance=record).data
        return HttpResponse(json.dumps(response))
    raise Http404
