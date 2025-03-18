"""
URL configuration for project_1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from project_1.views import *

urlpatterns = [
    path('bills', BillsView.as_view(), name='bills'),
    # path to the bill view, bill_id is a required parameter
    path('bill/<int:bill_id>/', BillView.as_view(), name='bill'),
    path('person/<int:people_id>/', PersonView.as_view(), name='person'),
    path('rollcall/<int:rollcall_id>/', RollCallView.as_view(), name='rollcall'),
]
