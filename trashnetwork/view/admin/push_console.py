from django.http import HttpRequest, HttpResponseForbidden, HttpResponseNotAllowed
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from requests import Request
from rest_framework import status

from trashnetwork import admin_site, settings
from trashnetwork.util import view_utils
from django.utils.translation import ugettext as _
import requests

JPUSH_AUTH_HEADER = {
    'Authorization': 'Basic %s' % settings.JPUSH_AUTH_BASE64
}


def get_cid():
    params = {'count': 1, 'type': 'push'}
    r = requests.get('https://api.jpush.cn/v3/push/cid', params=params, headers=JPUSH_AUTH_HEADER)
    if r.status_code == 200:
        return r.json()['cidlist'][0]
    return None


def push_console_view(req: HttpRequest):
    if not req.user.is_superuser:
        return HttpResponseForbidden('<h1>403 Forbidden</h1>')
    ctx = admin_site.site.each_context(req)
    ctx.update(title=_('Push Console'))
    ctx.update(cid=get_cid())
    return TemplateResponse(req, 'admin/push_console.html', context=ctx)


@csrf_exempt
def push_notification(req: HttpRequest):
    if not req.user.is_superuser:
        return HttpResponseForbidden('403 Forbidden')
    if req.method != 'POST':
        return HttpResponseNotAllowed(permitted_methods=['POST'])
    data = {
        'cid': req.POST['cid'],
        'platform': 'all',
        'audience': 'all',
        'notification': {
            'alert': req.POST['message'],
            'android': {
                'title': req.POST['title']
            }
        },
        'options': {
            'time_to_live': int(req.POST['ttl'])
        }
    }
    r = requests.post('https://api.jpush.cn/v3/push', json=data, headers=JPUSH_AUTH_HEADER)

    if r.status_code != 200 and r.status_code != 201:
        return view_utils.get_json_response(status=r.status_code, result_code=int(r.json()['error']['code']),
                                            message='From JPush: ' + r.json()['error']['message'])
    return view_utils.get_json_response(status=status.HTTP_201_CREATED, message=_('Push notification successfully'),
                                        new_cid=get_cid())
