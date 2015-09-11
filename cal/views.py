from django.contrib.auth import logout
from django.shortcuts import render_to_response


def home(request):
    if request.user.is_authenticated():
        return render_to_response(template_name='home_logged_in.html')
    return render_to_response(template_name='home_logged_out.html')


def logout_view(request):
    logout(request)
    return render_to_response(template_name='home_logged_out.html')
