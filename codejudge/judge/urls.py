from django.conf.urls import *
from judge import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^home/$', views.home, name='index'),
	url(r'^login/$', views.userLogin, name='index'),
	url(r'^logout/$', views.userLogout, name='index'),
	url(r'^register/$', views.register, name='index'),
	url(r'^profile/$', views.profile, name='index'),
	url(r'^(?P<contestId>\d+)/problem/(?P<problemId>\d+)/$', views.problem, name='index'),
	url(r'^contest/(?P<contestId>\d+)/$', views.contest, name='index'),
	url(r'^changepic/$', views.changeProfilePic, name='index'),
	url(r'^removepic/$', views.removeProfilePic, name='index'),
	url(r'^submitsolution/$', views.submitSolution, name='index'),
	url(r'^success/$', views.success, name='index'),
	url(r'^submission/$', views.submission, name='index'),
	url(r'^comment/$', views.comment, name='index'),
	url(r'^changepassword/$', views.changePassword, name='index'),
	url(r'^newUser/$', views.newUser, name='index'),
	url(r'^changePass/$', views.change, name='index'),
	url(r'^trail/$', views.trial, name='index'),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'media/(?P<path>.*)', 'serve', {'document_root': settings.MEDIA_ROOT}),
    )
