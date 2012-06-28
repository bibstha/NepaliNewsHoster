from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('', 
    (r'^patrika/static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATICFILES_DIRS[0]}),
    (r'^patrika/media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
)
urlpatterns += patterns('',
	url(r'^patrika/$', 'fileindex.views.index', {'baseName':'patrika'}, name='home'),
	url(r'^patrika//$', 'fileindex.views.list', {'baseName':'patrika'}, name='home'),
	url(r'^patrika/(?P<urlRelativePath>.*)/$', 'fileindex.views.list', {'baseName':'patrika'}, name='list'),
    # Examples:
    # url(r'^$', 'nepalipatrika.views.home', name='home'),
    # url(r'^nepalipatrika/', include('nepalipatrika.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

#handler500 = 'fileindex.views.custom_500'
#print urlpatterns