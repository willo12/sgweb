
from django.conf.urls import patterns, url
from sgdata import views

urlpatterns = patterns('',url(r'^$',views.index, name='index' ),  
                          url(r'^(?P<project>[\w]+)/(?P<exp>[\w]+)/(?P<field>[\w]+)$', views.ret_field, name = 'ret_field'),
                          url(r'^(?P<project>[\w]+)/(?P<exp>[\w]+)/(?P<field>[\w]+)/(?P<op>[\w]+)$', views.ret_field_op, name = 'ret_field_op'),
                          url(r'^gmaps/$', views.gmaps, name = 'gmaps'),
                      )
