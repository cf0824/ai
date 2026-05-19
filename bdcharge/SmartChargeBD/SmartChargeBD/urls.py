"""SmartCharge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, re_path, include
# from django.conf.urls import url
from django.views.generic import TemplateView

from app.api import user, charge, hardware, devops, wjs, awz, test, file, wx, information
# from app import wx       #,send_msg
from app import views
from app import xcx_jump


urlpatterns = [
    # path('a/', admin.site.urls),
    # re_path(r'^api/demo', demo.sys_handle),
    re_path(r'^api/wjs', wjs.sys_handle),  # 好像没用
    re_path(r'^api/awz', awz.sys_handle),  # 好像没用
    re_path(r'^api/user', user.sys_handle),
    re_path(r'^api/charge', charge.sys_handle),
    re_path(r'^api/information', information.sys_handle),
    # re_path(r'^api/file', file.sys_handle),
    re_path(r'^api/hardware/test', hardware.test),
    re_path(r'^api/hardware/A2S', hardware.get_A2T),  # 管理台
    re_path(r'^api/devops', devops.sys_handle),
    # re_path(r'^api/test', test.sys_handle),  # 没用
    re_path(r'^api/wx-pay-notice', views.wx_pay_success_notice),
    re_path(r'^api/wx-transfer-money-notice', views.wx_transfer_money_success_notice),
    # re_path(r'api/file/upload1', file.upload),
    re_path(r'api/file/upload_tencent', file.upload_tencent),
    re_path(r'^api/wx/QRCode', views.wx_QRCode_check),
    re_path(r'^api/wx/MP_verify_HNQVq1j223OSOfvI.txt', views.wx_url_check),
    re_path(r'^api/wx/test_temp', wx.test_temp),
    re_path(r'^api/wx', wx.wx),

    # re_path(r'^api/wx/test', wx.test),
    re_path(r'^code/eDI7Gjj9T4.txt', views.code_check),
    re_path(r'^eDI7Gjj9T4.txt', views.code_check),
    re_path(r'^ZKtRQdCH3I.txt', views.qr_code_check),
    re_path(r'^code', views.code),
    re_path(r'^jump2xcx', xcx_jump.jump_to_mini),

    # re_path(r'^charge/get_site_list', charge.get_site_list),
    #
    # path('charge/', include('charge.urls_charge')),
    # path('user/', include('charge.urls_user'))
    re_path(r'^api/test-redirect', wx.redirect_miniprogram)
]
