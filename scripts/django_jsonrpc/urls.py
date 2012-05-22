from django.conf.urls.defaults import *
from jsonrpc import jsonrpc_site
import ucap_site.ucapapp.views # you must import the views that need connected

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^json/browse/', 'jsonrpc.views.browse', name="jsonrpc_browser"), # for the graphical browser/web console only, omissible
    url(r'^json/', jsonrpc_site.dispatch, name="jsonrpc_mountpoint"),
    (r'^json/(?P<method>[a-zA-Z0-9.]+)$', jsonrpc_site.dispatch), # for HTTP GET only, also omissible
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': '/srv/tmp'}),
    # Example:
    # (r'^ucap_site/', include('ucap_site.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
