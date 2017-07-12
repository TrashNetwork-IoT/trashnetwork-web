import datetime

from django.http import HttpRequest, HttpResponseForbidden, HttpResponseNotAllowed
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from trashnetwork import admin_site
from trashnetwork.util import scheduler_utils, view_utils
from trashnetwork.view.v1.mobile.recycle import recycle_point


def red_packet_scheduler_view(req: HttpRequest):
    if not req.user.is_superuser:
        return HttpResponseForbidden('<h1>403 Forbidden</h1>')
    ctx = admin_site.site.each_context(req)
    ctx.update(title=_('Red Packet Scheduler'))
    ctx.update(is_scheduler_running=scheduler_utils.is_job_scheduled(recycle_point.JOB_RED_PACKET_POINT))
    return TemplateResponse(req, 'admin/red_packet_scheduler.html', context=ctx)


@csrf_exempt
def schedule_red_packet(req: HttpRequest):
    if not req.user.is_superuser:
        return HttpResponseForbidden('403 Forbidden')
    if req.method != 'POST':
        return HttpResponseNotAllowed(permitted_methods=['POST'])
    if scheduler_utils.is_job_scheduled(recycle_point.JOB_RED_PACKET_POINT):
        scheduler_utils.remove_job(recycle_point.JOB_RED_PACKET_POINT)
    if int(req.POST['restart']) != 0:
        args = {
            'max_red_packet_point_ratio': float(req.POST['max_red_packet_point_ratio']),
            'probability': float(req.POST['probability']),
            'each_min_red_packet_credit': int(req.POST['each_min_red_packet_credit']),
            'each_max_red_packet_credit': int(req.POST['each_max_red_packet_credit']),
            'each_min_last_time': int(req.POST['each_min_last_time']),
            'each_max_last_time': int(req.POST['each_max_last_time']),
        }
        scheduler_utils.add_interval_job(job_id=recycle_point.JOB_RED_PACKET_POINT,
                                         job_func=recycle_point.update_red_packet_point,
                                         minutes=int(req.POST['update_interval']),
                                         start_time=datetime.datetime.now() + datetime.timedelta(seconds=5),
                                         args=[args])
    else:
        recycle_point.clear_red_packet()
    return view_utils.get_json_response(status=status.HTTP_201_CREATED,
                                        scheduler_running=scheduler_utils.is_job_scheduled(
                                            recycle_point.JOB_RED_PACKET_POINT))
