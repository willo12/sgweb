
from django.conf.urls import patterns, url
from sgdata import views

urlpatterns = patterns('',url(r'^$',views.index, name='index' ),  
                          url(r'^(?P<project>[\w]+)/(?P<exp>[\w\-\+]+)/(?P<field>[\w]+)$', views.ret_field, name = 'ret_field'),

                         url(r'^projects/(?P<project>[\w]+)/list_ops/$', views.return_list_ops, name = 'list_ops'),

                         url(r'^projects/(?P<project>[\w]+)/(?P<exp>[\w\.]+)/$', views.list_exp, name = 'list_exp'),


                          url(r'^projects/(?P<project>[\w]+)/$', views.list_project, name = 'list_project'),


                         url(r'^projects/$', views.projects, name = 'projects'),


                           url(r'^(?P<project>[\w]+)/(?P<exp>[\w]+)/(?P<field>[\w]+)/method/(?P<method>[\w]+)/$', views.ret_field_method, name = 'ret_field_method'),                         
 

                           url(r'^(?P<project>[\w]+)/(?P<exp>[\w\-\+\.]+)/(?P<field>[\w]+)/ops/$', views.ret_field_ops_old, name = 'ret_field_ops_old'),      


                           url(r'^(?P<project>[\w]+)/(?P<fields>[\w\-\+\.]+)/ops/$', views.ret_field_ops, name = 'ret_field_ops'),                                                    
                          url(r'^gmaps/$', views.gmaps, name = 'gmaps'),

                      )
