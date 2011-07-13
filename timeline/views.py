from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.views import login, logout
from timeline.models import TimelineUser, Release, Timeline
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import discogs_client as discogs
import logging
logger = logging.getLogger(__name__)
discogs.user_agent = 'DiscogsTimeline/0.1 +http://twitter.com/neutralino1'

def get_releases(user, order_by='name'):
    releases = []
    if user:
        releases = user.timelineuser.releases.order_by(order_by).all()
    return releases

def home(request):
    releases = get_releases(request.user)
    return render_to_response('timeline/home.html', {'releases':releases}, 
                              context_instance=RequestContext(request))


def details(request, user_id):
    raise Http404

def create(request):
    email = request.POST['email']
    passw = request.POST['password']
    try:
        user = User.objects.get(username=email)
    except ObjectDoesNotExist:
        user = User.objects.create_user(email, email, passw)
        user.save()
        timeline = TimelineUser(user=user)
        timeline.save()
    user = authenticate(username=email, password=passw)
    if user is not None:
        login(request, user)
    return HttpResponseRedirect(reverse('timeline.views.home'))
#    return render_to_response('timeline/home.html', {}, context_instance=RequestContext(request))

def search(request):
    params = {}
    params['query'] = request.GET['q']
    page = request.GET['p'] if ('p' in request.GET.keys()) else 1
    s = discogs.Search(params['query'], page=page, only='releases')
    params['results'] = []
    params['total'] = int(s.data['searchresults']['numResults'])
    params['page'] = int(s.data['searchresults']['start'])/20+1
    params['prevpage'] = params['page'] - 1
    params['nextpage'] = params['page'] + 1
    params['pages'] = params['total']/20+1
    for r in s.results(page=page):
        original = r.data
        if not isinstance(r, discogs.MasterRelease):
            continue
        for v in r.data['versions']:
            if 'released' in v.keys():
                if ('released' not in original.keys()) or \
                        ('released' in original.keys() and v['released'] < original['released'] and \
                             len(v['released']) > 4):
                    original['released'] = v['released']
                    original['catno'] = v['catno']
                    original['name'] = v['title']
                    original['label'] = v['label']
            else:
                original['released'] = original['year']
        if 'images' in original.keys():
        #if (not 'thumb' in original.keys()) and ('images' in r.data.keys()):
            original['thumb'] = original['images'][0]['uri150']
            for i in original['images']:
                if i['type'] == 'primary':
                    original['thumb'] = i['uri150']
            original['artist'] = original['artists'][0]
        params['results'] += [original]
    params['releases'] = get_releases(request.user)
    return render_to_response('timeline/home.html', params, context_instance=RequestContext(request))
#    return HttpResponseRedirect(reverse('timeline.views.home'))#, {'results': s.results()})

def add_release(request):
    catno = request.POST['catno']
    try:
        release = Release.objects.get(catno=catno)
    except ObjectDoesNotExist:
        release = Release(name=request.POST['name'],
                          catno=request.POST['catno'],
                          discogs_id=request.POST['discogs_id'],
                          artist=request.POST['artist'],
                          label=request.POST['label'],
                          thumb=request.POST['thumb'],
                          released=request.POST['released'])
        release.clean_and_save()
    release.owners.add(request.user.timelineuser)
    return HttpResponseRedirect(reverse('timeline.views.home'))

def delete_release(request):
    id = request.GET['id']
    release = Release.objects.get(id=id)
    release.owners.remove(request.user.timelineuser)
    return HttpResponseRedirect(reverse('timeline.views.home'))

def timeline(request):
    releases = get_releases(request.user, order_by='released')
    line = Timeline(releases)
    params = {'line':line}
    return render_to_response('timeline/timeline.html', params,
                              context_instance=RequestContext(request))
