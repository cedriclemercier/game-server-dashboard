from django.shortcuts import render, redirect
from admin_datta.forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.views.generic import CreateView
from django.contrib.auth import logout

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from discord import SyncWebhook, Embed
from .forms import ServerForm

import boto3
import os, time

# import asyncio


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
    instance_state = 'pending'
    
    try:
        if action == 'start':
            instance = ec2_client.start_instances(InstanceIds=[instance_id])
            while instance_state != 'running':
                response = ec2_client.describe_instances(InstanceIds=[instance_id])
                instance_state = response['Reservations'][0]['Instances'][0]['State']['Name']
                time.sleep(1)
            print(f"Successfully started instance {instance_id}")
            return True
        else:
            ec2_client.stop_instances(InstanceIds=[instance_id])
            print(f"Successfully stopped instance {instance_id}")
            return False
    except Exception as e:
        print(f"Error starting instance: {e}")
        return False


def get_instance_ip(instance_id):
    ec2 = boto3.resource('ec2', aws_access_key_id=aws_access_key,
                         aws_secret_access_key=aws_secret_key, region_name=aws_region)

    instance = ec2.Instance(instance_id)
    instance_ip = instance.public_ip_address

    return instance_ip


def index(request):
    context = {
        'segment': 'index'
    }
    return render(request, "pages/index.html", context)


@csrf_exempt
def servers_page(request):
    icon = {
        'running': '🟢',
        'stopping': '🟠',
        'stopped': '🔴',
        'pending': '⏳'
    }
    instance_id = 'i-0429aa1a2d080c4b5'
    instance_id_mc = 'i-053b0752a146b85ee'

    servers_list = [
        {
            'instance_id': 'i-0429aa1a2d080c4b5',
            'name': 'The Lab',
            'no_players': '1/16',
            'status_name': '',
            'status': '',
            'form': '',
            'icon': '',
            'ip': ''
        },
        {
            'instance_id': 'i-053b0752a146b85ee',
            'name': 'Minecraft SG 2023',
            'no_players': '1/16',
            'status_name': '',
            'status': '',
            'form': '',
            'icon': '',
            'ip': ''
        }
    ]

    server_name = None
    server_ip = None
    if (request.method == 'POST'):
        print(request.POST)
        if (request.POST['status'] == False or request.POST['status'] == 'False'):
            status = start_stop_ec2_instance(
                request.POST['instanceId'], 'start')
            action = 'start'
        else:
            status = start_stop_ec2_instance(
                request.POST['instanceId'], 'stop')
            action = 'stop'

        for server_info in servers_list:
            status, status_name = is_instance_running(
                server_info['instance_id'])
            instance_details = {
                'status': status,
                'instanceId': server_info['instance_id']
            }
            form = ServerForm(instance_details)

            server_info['status'] = status
            server_info['status_name'] = status_name.capitalize()
            server_info['form'] = form
            server_info['icon'] = icon[status_name]
            server_info['ip'] = get_instance_ip(server_info['instance_id'])
            
            if request.POST['instanceId'] == server_info['instance_id']:
                server_name = server_info['name']
                server_ip = server_info['ip']

        instance_details = {
            'status': status,
            'instanceId': request.POST['instanceId']
        }
        
        context = {
            'segment': 'servers',
            'servers': servers_list
        }
        
        if action == 'start':
            WEBHOOK = os.environ.get('DISCORD_WEBHOOK')
            hook_id = WEBHOOK.split('/')[5]
            token = WEBHOOK.split('/')[6]
            webhook = SyncWebhook.partial(hook_id, token)
            embed = Embed(title="G'day mate!", description=f"Hey @want-to-play! I just started {server_name} server, have fun!", color=0x1DE7B9)
            embed.add_field(name="Website link", value="[Link](https://terraria-lab.vercel.app/)", inline=False)
            embed.add_field(name="IP", value=server_ip, inline=False)
            webhook.send(embed=embed)

        return render(request, "pages/servers.html", context)

    else:

        for server_info in servers_list:
            status, status_name = is_instance_running(
                server_info['instance_id'])
            instance_details = {
                'status': status,
                'instanceId': server_info['instance_id']
            }
            form = ServerForm(instance_details)

            server_info['status'] = status
            server_info['status_name'] = status_name.capitalize()
            server_info['form'] = form
            server_info['icon'] = icon[status_name]
            server_info['ip'] = get_instance_ip(server_info['instance_id'])

        context = {
            'segment': 'servers',
            'servers': servers_list
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
