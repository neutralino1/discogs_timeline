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
from django.utils import simplejson
import discogs_client as discogs
import logging

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

def search2(request):
    params = {}
    params['query'] = request.GET['q']
    page = request.GET['p'] if ('p' in request.GET.keys()) else 1
    s = discogs.Search(params['query'], only='releases')
    total = int(s.data['searchresults']['numResults'])
    params['results'] = []
    for p in range(1, min(10, total/20 +1) ):
        res = s.results(page=p)
        for r in res:
            rec = {}
            if not isinstance(r, discogs.MasterRelease):
                continue
            for v in r.data['versions']:
                if 'LP' in v['format'] and 'released' in v.keys():
                    rec['catno'] = v['catno']
                    rec['released'] = v['released']
                    rec['name'] = v['title']
                    rec['label'] = v['label']
                    rec['artist'] = r.data['artists'][0]['name']
                    rec['id'] = v['id']
                    if 'images' in r.data.keys():
                        rec['thumb'] = r.data['images'][0]['uri150']
                        for i in r.data['images']:
                            if i['type'] == 'primary':
                                rec['thumb'] = i['uri150']
                    params['results'] += [rec]
                    logging.debug(rec)
                    if rec: break
    params['total'] = len(params['results'])
    params['page'] = 1
    params['prevpage'] = 0
    params['nextpage'] = 2
    params['pages'] = 3
    params['releases'] = get_releases(request.user)
    return render_to_response('timeline/home.html', params, context_instance=RequestContext(request))

def search(request):
    params = {}
    params['query'] = request.GET['q']
    page = int(request.GET['p']) if ('p' in request.GET.keys()) else 1
    s = discogs.Search(params['query'], only='releases')
    total = int(s.data['searchresults']['numResults'])
    total_pages = total/20 + 1
    params['results'] = []
    res = s.results(page=page)
    n = 0
    for r in res:
        rec = {}
        if not isinstance(r, discogs.Release):
            continue
        ok = 0
        for f in r.data['formats']:
            if 'Vinyl' in f['name']:
                ok = 1
                break
        if ok:
            params['results'] += [r]
    params['total'] = total
    params['page'] = page
#    params['releases'] = get_releases(request.user)
    t = loader.get_template('timeline/search-results.html')
    c = Context(params)
    return HttpResponse(simplejson.dumps({'total':total_pages, 'page':page, 'query':params['query'],
                                          'content':t.render(c), 'nres':len(params['results']), 'tres':total}), 
                        mimetype='application/javascript')

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
    params = {}
    logging.debug(request)
    id = request.GET['id']
    logging.debug(id)
    release = Release.objects.get(id=id)
    release.owners.remove(request.user.timelineuser)
    params['releases'] = get_releases(request.user)
    t = loader.get_template('timeline/my_releases.html')
    c = Context(params)
    return HttpResponse(t.render(c))
    #
    #return HttpResponseRedirect(reverse('timeline.views.home'))

def timeline(request):
    releases = get_releases(request.user, order_by='released')
    line = Timeline(releases)
    params = {'line':line}
    return render_to_response('timeline/timeline.html', params,
                              context_instance=RequestContext(request))
