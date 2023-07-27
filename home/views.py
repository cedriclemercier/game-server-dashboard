from django.shortcuts import render, redirect
from admin_datta.forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.views.generic import CreateView
from django.contrib.auth import logout

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from discord import SyncWebhook
from .forms import ServerForm

import boto3, os

aws_access_key = os.environ.get('AWS_ACCESSKEY')
aws_secret_key = os.environ.get('AWS_SECRETKEY')
aws_region = 'ap-southeast-1'  # Replace this with your desired AWS region

session = boto3.Session(
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

ec2_client = session.client('ec2')

def is_instance_running(instance_id):
    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])

        if 'Reservations' in response and len(response['Reservations']) > 0:
            instances = response['Reservations'][0]['Instances']
            if len(instances) > 0:
                instance_status = instances[0]['State']['Name']
                print(f"Instance {instance_id} status: {instance_status}")
                return instance_status == 'running', instance_status
    except Exception as e:
        print(f"Error checking instance status: {e}")

    return False
  
def start_stop_ec2_instance(instance_id, action):
    try:
      if action == 'start':
          ec2_client.start_instances(InstanceIds=[instance_id])
          print(f"Successfully started instance {instance_id}")
          return True
      else:
          ec2_client.stop_instances(InstanceIds=[instance_id])
          print(f"Successfully stopped instance {instance_id}")
          return False
    except Exception as e:
        print(f"Error starting instance: {e}")
        return False

def index(request):
  context = {
    'segment': 'index'
  }
  return render(request, "pages/index.html", context)


@csrf_exempt
def servers_page(request):
  icon = {
    'running': '🟢',
    'stopping': '⏳',
    'stopped': '🔴',
    'pending': '🟢'
  }
  instance_id = 'i-0429aa1a2d080c4b5'
  
  if (request.method == 'POST'):
    print(request.POST['status'])
    if (request.POST['status'] == False or request.POST['status'] == 'False'):
      status = start_stop_ec2_instance(instance_id, 'start')
      action = 'start'
    else:
      status = start_stop_ec2_instance(instance_id, 'stop')
      action = 'stop'
      
    instance_details ={
      'status': status,
      'instanceId': instance_id
    }
    
    form = ServerForm(instance_details)
    _, status_name = is_instance_running(instance_id)
    
    context = {
      'segment': 'servers',
      'servers': [
        {
          'name': 'The Lab',
          'no_players': '1/16',
          'status': status,
          'status_name': status_name.capitalize(),
          'form': form,
          'icon': icon[status_name],
          'sent': True
        }
      ]
    }
    
    if action == 'start':
      WEBHOOK = os.environ.get('DISCORD_WEBHOOK')
      hook_id = WEBHOOK.split('/')[5]
      token = WEBHOOK.split('/')[6]
      webhook = SyncWebhook.partial(hook_id, token)
      webhook.send("Starting Terraria Server...")
    
    return render(request, "pages/servers.html", context)
    
  else:
    status, status_name = is_instance_running(instance_id)
    instance_details ={
      'status': status,
      'instanceId': instance_id
    }
    
    form = ServerForm(instance_details)
    
    context = {
      'segment': 'servers',
      'servers': [
        {
          'name': 'The Lab',
          'no_players': '1/16',
          'status_name': status_name.capitalize(),
          'status': status,
          'form': form,
          'icon': icon[status_name]
        }
      ]
    }
    return render(request, "pages/servers.html", context)

def tables(request):
  context = {
    'segment': 'tables'
  }
  return render(request, "pages/tables.html", context)

# Components
@login_required(login_url='/accounts/login/')
def bc_button(request):
  context = {
    'parent': 'basic_components',
    'segment': 'button'
  }
  return render(request, "pages/components/bc_button.html", context)

@login_required(login_url='/accounts/login/')
def bc_badges(request):
  context = {
    'parent': 'basic_components',
    'segment': 'badges'
  }
  return render(request, "pages/components/bc_badges.html", context)

@login_required(login_url='/accounts/login/')
def bc_breadcrumb_pagination(request):
  context = {
    'parent': 'basic_components',
    'segment': 'breadcrumbs_&_pagination'
  }
  return render(request, "pages/components/bc_breadcrumb-pagination.html", context)

@login_required(login_url='/accounts/login/')
def bc_collapse(request):
  context = {
    'parent': 'basic_components',
    'segment': 'collapse'
  }
  return render(request, "pages/components/bc_collapse.html", context)

@login_required(login_url='/accounts/login/')
def bc_tabs(request):
  context = {
    'parent': 'basic_components',
    'segment': 'navs_&_tabs'
  }
  return render(request, "pages/components/bc_tabs.html", context)

@login_required(login_url='/accounts/login/')
def bc_typography(request):
  context = {
    'parent': 'basic_components',
    'segment': 'typography'
  }
  return render(request, "pages/components/bc_typography.html", context)

@login_required(login_url='/accounts/login/')
def icon_feather(request):
  context = {
    'parent': 'basic_components',
    'segment': 'feather_icon'
  }
  return render(request, "pages/components/icon-feather.html", context)


# Forms and Tables
@login_required(login_url='/accounts/login/')
def form_elements(request):
  context = {
    'parent': 'form_components',
    'segment': 'form_elements'
  }
  return render(request, 'pages/form_elements.html', context)

@login_required(login_url='/accounts/login/')
def basic_tables(request):
  context = {
    'parent': 'tables',
    'segment': 'basic_tables'
  }
  return render(request, 'pages/tbl_bootstrap.html', context)

# Chart and Maps
@login_required(login_url='/accounts/login/')
def morris_chart(request):
  context = {
    'parent': 'chart',
    'segment': 'morris_chart'
  }
  return render(request, 'pages/chart-morris.html', context)

@login_required(login_url='/accounts/login/')
def google_maps(request):
  context = {
    'parent': 'maps',
    'segment': 'google_maps'
  }
  return render(request, 'pages/map-google.html', context)

# Authentication
class UserRegistrationView(CreateView):
  template_name = 'accounts/auth-signup.html'
  form_class = RegistrationForm
  success_url = '/accounts/login/'

class UserLoginView(LoginView):
  template_name = 'accounts/auth-signin.html'
  form_class = LoginForm

class UserPasswordResetView(PasswordResetView):
  template_name = 'accounts/auth-reset-password.html'
  form_class = UserPasswordResetForm

class UserPasswrodResetConfirmView(PasswordResetConfirmView):
  template_name = 'accounts/auth-password-reset-confirm.html'
  form_class = UserSetPasswordForm

class UserPasswordChangeView(PasswordChangeView):
  template_name = 'accounts/auth-change-password.html'
  form_class = UserPasswordChangeForm

def logout_view(request):
  logout(request)
  return redirect('/accounts/login/')

@login_required(login_url='/accounts/login/')
def profile(request):
  context = {
    'segment': 'profile',
  }
  return render(request, 'pages/profile.html', context)

@login_required(login_url='/accounts/login/')
def sample_page(request):
  context = {
    'segment': 'sample_page',
  }
  return render(request, 'pages/sample-page.html', context)