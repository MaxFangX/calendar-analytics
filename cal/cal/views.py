from cal.models import GoogleCredentials, GoogleFlow, Profile

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST

from oauth2client import client, crypt
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.django_orm import Storage


def home(request):
    context = RequestContext(request, {
        'base_url': settings.BASE_URL,
    })

    if request.user.is_authenticated():
        return render_to_response(template_name='home_logged_in.html',
                                  context=context)

    return render_to_response(template_name='home_logged_out.html',
                              context=context)


@require_POST
def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)

    context= RequestContext(request)

    if user is not None:
        login(request, user)
        return render_to_response(template_name='home_logged_in.html', context=context)
    else:
        return HttpResponse("Failed to log in.")


def logout_view(request):
    context= RequestContext(request)
    logout(request)
    return render_to_response(template_name='home_logged_out.html', context=context)


def google_auth(request):
    """
    Handles Google oauth flow. For details, visit
    https://developers.google.com/api-client-library/python/guide/aaa_oauth#OAuth2WebServerFlow
    https://developers.google.com/api-client-library/python/guide/django
    """

    flow = None
    default_flow = OAuth2WebServerFlow(client_id=settings.GOOGLE_CALENDAR_API_CLIENT_ID,
                                       client_secret=settings.GOOGLE_CALENDAR_API_CLIENT_SECRET,
                                       scope=['https://www.googleapis.com/auth/calendar','profile','email'],
                                       redirect_uri=settings.BASE_URL + '/auth/google')

    # TODO perhaps create a new user upon oauth, to skip this check
    if request.user.is_authenticated():
        # Try to retrieve an existing flow, or create one if it doesn't exist
        gflow = GoogleFlow.objects.filter(id=request.user).last()
        if not gflow:
            gflow = GoogleFlow(id=request.user,
                              flow=default_flow)
            gflow.save()
        flow = gflow.flow
    else:
        flow = default_flow

    code = request.GET.get('code', None)
    error = request.GET.get('error', None)

    if error:
        # TODO eventually make this prettier, like redirect to some landing page
        return HttpResponseBadRequest("Authentication failed. Reason: {}".format(error))
    elif code:
        credentials = flow.step2_exchange(code)
        if request.user.is_authenticated():
            # Save the credentials
            storage = Storage(GoogleCredentials, 'id', request.user, 'credential')
            storage.put(credentials)

        return HttpResponseRedirect("/")
    else:
        auth_uri = flow.step1_get_authorize_url()
        return HttpResponseRedirect(auth_uri)


def complete_google(request):
    """
    Completes the Google oauth flow. For details, visit
    https://developers.google.com/api-client-library/python/guide/aaa_oauth#OAuth2WebServerFlow
    https://developers.google.com/api-client-library/python/guide/django
    """
    id_token = request.POST.get('id_token', None)
    code = request.POST.get('code', None)
    if not id_token or not code:
        return HttpResponseBadRequest("Missing code or id_token")
    try:
        idinfo = client.verify_id_token(id_token, settings.GOOGLE_CALENDAR_API_CLIENT_ID)
    except crypt.AppIdentityError:
        return HttpResponseBadRequest("Invalid id_token.")

    try:
        user = User.objects.get(email=idinfo['email'])
    except User.DoesNotExist:
        # TODO allow changing the username
        first_name = idinfo['given_name']
        last_name = idinfo['family_name']
        username = (first_name + last_name)[:30]
        extra_fields = {
            'first_name': first_name,
            'last_name' : last_name,
        }
        user = User.objects.create_user(username=username, email=idinfo['email'], extra_fields=extra_fields)

    profile, created = Profile.get_or_create(user)
    if created:
        # Fill in additional data for the first time
        profile.google_id = idinfo['sub']
        profile.locale = idinfo['locale']
        profile.main_calendar = None  # TODO make API call
        profile.picture_url = idinfo['picture']
        profile.save()

    if not request.user.is_authenticated():
        # Log them in
        authed_user = authenticate(email=user.email)
        if authed_user is not None and authed_user.is_active:
            login(request, authed_user)

    return HttpResponse(status=200)
