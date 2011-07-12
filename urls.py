from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('timeline.views',
                       # Examples:
                           url(r'^$', 'home'),
                       (r'^users/(?P<user_id>\d+)/$', 'details'),
                       (r'^users/create/$', 'create'),
                       (r'^search', 'search'),
                       (r'^users/add_release/$', 'add_release'),
                       (r'^users/delete_release/$', 'delete_release'),
                       (r'^timeline', 'timeline')
    # url(r'^discogs_timeline/', include('discogs_timeline.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
                        (r'^login/$', 'django.contrib.auth.views.login'),
                        (r'^logout/$', 'django.contrib.auth.views.logout'),
                        )
