from django.conf.urls import url
from . import views


app_name = 'booksys'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^loginhandler/$', views.loginhandler, name='loginhandler'),
    url(r'^register/$', views.register, name='register'),
    url(r'^registerhandler/$', views.registerhandler, name='registerhandler'),
    url(r'^reader/(\d+)/$', views.reader, name='reader'),
    url(r'^query/(\d+)/$', views.query, name='query'),
    url(r'^queryresult/(\d+)/$', views.queryresult, name='queryresult'),
    url(r'^bookinfo/(\d+)/(\d+)/$', views.bookinfo, name='bookinfo'),
    url(r'^borrowbook/(\d+)/(\d+)/$', views.borrowinfo, name='borrowinfo'),
    url(r'^queryinfo/(\d+)/$', views.queryinfo, name='queryinfo'),
    url(r'^updateinfo/(\d+)/$', views.updateinfo, name='updateinfo'),
    url(r'^updateinfohandler/(\d+)/$', views.updateinfohandler, name='updateinfohandler'),
    url(r'^history/(\d+)/$', views.history, name='history'),
    url(r'^exit/$', views.exit, name='exit'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^editor/$', views.editor, name='editor'),
    url(r'^emailto/$', views.emailto, name='emailto'),
    url(r'^active/(.*?)/$', views.active, name='active'),
    url(r'^ajax/$', views.ajax, name='ajax'),
    url(r'^ajaxajax/$', views.ajaxajax, name='ajaxajax'),
    url(r'^verify/$', views.verify, name='verify'),
    url(r'^checkuser/$', views.checkuser, name='checkuser'),
]