from django.utils.translation import ugettext as _
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request

from trashnetwork.view.v1.mobile.recycle import account
from trashnetwork.util import view_utils
from trashnetwork import models


@api_view(['POST'])
def post_feedback(req: Request):
    poster = None
    if req.META.get('HTTP_AUTH_TOKEN') is not None:
        poster = account.token_check(req)
    new_feedback = models.Feedback(poster=poster, title=req.data['title'],
                                   text=req.data['text_content'])
    new_feedback.save()
    return view_utils.get_json_response(status=status.HTTP_201_CREATED,
                                        message=_('Post feedback successfully'))
