# -*- coding:utf-8 -*-
import datetime
import os
import time

from django.conf import settings
from django.core.files.storage import DefaultStorage
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .configs import MDConfig

# TODO 此处获取default配置，当用户设置了其他配置时，此处无效，需要进一步完善
MDEDITOR_CONFIGS = MDConfig('default')


class UploadView(generic.View):
    """ upload image file """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UploadView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        upload_image = request.FILES.get("editormd-image-file", None)
        media_root = settings.MEDIA_ROOT

        # image none check
        if not upload_image:
            return JsonResponse({
                'success': 0,
                'message': "未获取到要上传的图片",
                'url': ""
            })

        # image format check
        file_name_list = upload_image.name.split('.')
        file_extension = file_name_list.pop(-1)
        file_name = '.'.join(file_name_list)
        if file_extension not in MDEDITOR_CONFIGS['upload_image_formats']:
            return JsonResponse({
                'success': 0,
                'message': "上传图片格式错误，允许上传图片格式为：%s" % ','.join(
                    MDEDITOR_CONFIGS['upload_image_formats']),
                'url': ""
            })

        # 改为对 DEFAULT_FILE_STORAGE+MEDIA_URL 的支持
        try:
            url_path = os.path.join(settings.MEDIA_URL,
                                    MDEDITOR_CONFIGS['image_folder'],
                                    time.strftime("%Y/%m/%d", time.localtime()),
                                    '%s.%s' % (file_name, file_extension))

            url_path = str(url_path).replace('//', '/').strip('/')
            storage = DefaultStorage()
            storage.save(url_path, upload_image)
            url = storage.url(url_path)
            return JsonResponse({'success': 1,
                                 'message': "上传成功！",
                                 'url': url
                                 })
        except Exception as err:
            return JsonResponse({
                'success': 0,
                'message': "上传失败：%s" % str(err),
                'url': ""
            })
