from cal.helpers import json_response, TimeNodeChain
from cal.models import ColorCategory, GoogleCredentials, GoogleFlow, Profile, Tag

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from oauth2client import client, crypt
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.django_orm import Storage


@ensure_csrf_cookie
def home(request):
    context = RequestContext(request)

    if request.user.is_authenticated():
        color_categories = [{
            'label': c.label,
            'hours': TimeNodeChain(c.get_last_week()).total_time / 3600 }
            for c in ColorCategory.objects.filter(user=request.user)]
        context['color_categories'] = color_categories
        tags = [{
            'label': t.label,
            'hours': t.total_time() / 3600,
            }
            for t in Tag.objects.filter(user=request.user)]
        context['tags'] = tags

        return render_to_response(template_name='home_logged_in.html',
                                  context=context)
    else:
        return render_to_response(template_name='home_logged_out.html',
                                  context=context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")

@login_required
def clear_auth(request):
    """
    Clears the credentials for the requesting user
    """
    if request.user:
        profile, _ = Profile.get_or_create(user=request.user)
        profile.clear_credentials()
    return HttpResponseRedirect("/")

@login_required
def accounts_profile(request):
    """
    Shows the account information for a user
    For now, redirects to homepage.
    """
    # TODO either remove this view or change Python Social Auth after login
    return HttpResponseRedirect("/")

@login_required
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
    default_flow.params['access_type'] = 'offline'

    # Try to retrieve an existing flow, or create one if it doesn't exist
    gflow = GoogleFlow.objects.filter(id=request.user).last()
    if not gflow:
        gflow = GoogleFlow(id=request.user,
                          flow=default_flow)
        gflow.save()
    flow = gflow.flow

    code = request.GET.get('code', None)
    error = request.GET.get('error', None)

    if error:
        # TODO eventually make this prettier, like redirect to some landing page
        return HttpResponseBadRequest("Authentication failed. Reason: {}".format(error))
    elif code:
        credential = flow.step2_exchange(code)
        # Save the credentials
        storage = Storage(GoogleCredentials, 'user', request.user, 'credential')
        storage.put(credential)
        profile, _ = Profile.get_or_create(user=request.user)
        profile.authed = True
        profile.save()
        # TODO improve the latency over here
        request.user.googlecredentials.import_calendars()

        return HttpResponseRedirect("/")
    else:
        auth_uri = flow.step1_get_authorize_url()
        return HttpResponseRedirect(auth_uri)

@require_POST
def login_google(request):
    """
    Logs in the user using Google sign in
    """
    id_token = request.POST.get('id_token', None)
    code = request.POST.get('code', None)
    if not id_token or not code:
        return HttpResponseBadRequest("Missing code or id_token")
    try:
        idinfo = client.verify_id_token(id_token, settings.GOOGLE_CALENDAR_API_CLIENT_ID)
    except crypt.AppIdentityError:
        return HttpResponseBadRequest("Invalid id_token.")
    except Exception as e:
        return HttpResponseServerError("Error: {}".format(e))

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
        # Fill in additional data only for the first time
        profile.google_id = idinfo['sub']
        profile.locale = idinfo['locale']
        profile.picture_url = idinfo['picture']
        profile.save()

    if not request.user.is_authenticated():
        # Log them in
        user = authenticate(email=user.email)
        if user is not None:
            if user.is_active:
                login(request, user)
            else:
                return HttpResponseBadRequest("User inactive - likely banned")
        else:
            return HttpResponseBadRequest("Failed to log in user")

    # At this point, all users should be logged in.
    return json_response({"message": "Successfully logged in!"}, status=200)
