import base64
import datetime

from django.db.models import Q
from django.http import JsonResponse
from trashnetwork import models


def get_json_response(result_code: int = 0, message: str = '', status: int = 200, **kwargs):
    j = dict(result_code=result_code, message=message)
    j.update(kwargs)
    return JsonResponse(j, status=status)


def get_cleaning_user_info_dict(user: models.CleaningAccount):
    portrait_base64 = base64.b64encode(user.portrait).decode()
    result = dict(name=user.name, gender=user.gender, account_type=user.account_type,
                  portrait=portrait_base64, user_id=user.user_id, phone_number=user.phone_number)
    return result


def get_recycle_user_basic_info_dict(user: models.RecycleAccount):
    result = dict(user_id=user.user_id, account_type=user.account_type, credit=user.credit)
    return result


def get_trash_info_dict(trash: models.Trash):
    return dict(trash_id=trash.trash_id, description=trash.description,
                longitude=trash.longitude, latitude=trash.latitude)


def get_group_dict(group: models.CleaningGroup):
    member_list = []
    if group.group_id == models.SPECIAL_WORK_GROUP_ID:  # Special work group
        for u in models.CleaningAccount.objects.all():
            member_list.append(u.user_id)
    else:
        for gm in models.CleaningGroupMembership.objects.filter(group=group):
            member_list.append(gm.user.user_id)
    return dict(group_id=group.group_id, name=group.name, portrait=base64.b64encode(group.portrait).decode(),
                member_list=member_list)


def get_bulletin_dict(bulletin: models.CleaningGroupBulletin):
    return dict(poster_id=bulletin.poster_id,
                post_time=int(bulletin.timestamp.timestamp()),
                title=bulletin.title,
                text_content=bulletin.text)


def get_work_record_dict(record: models.CleaningWorkRecord):
    return dict(user_id=record.user_id,
                trash_id=record.trash_id,
                record_time=int(record.timestamp.timestamp()))


def get_feedback_dict(feedback: models.Feedback):
    result = get_model_dict(feedback, excluded_fields=['poster'], modify_fields={'text': 'text_content'})
    if feedback.poster:
        result.update({'user_name': feedback.poster.user_name})
    return result


def get_recycle_point_dict(point: models.RecyclePoint, is_owner: bool = False):
    bottle_recycle = point.bottle_num is not None
    result = get_model_dict(point, excluded_fields=['bottle_num', 'owner'],
                            modify_fields={'point_id': 'recycle_point_id'})
    result.update(bottle_recycle=bottle_recycle)
    if is_owner:
        if bottle_recycle:
            result.update(bottle_num=point.bottle_num)
        result.update(owner_id=point.owner_id)
    return result


def general_query_time_limit(end_time=None, start_time=None, **kwargs):
    if end_time is not None:
        q = Q(timestamp__lte=datetime.datetime.fromtimestamp(int(end_time)))
    else:
        q = Q(timestamp__lte=datetime.datetime.now())
    if start_time is not None:
        q &= Q(timestamp__gte=datetime.datetime.fromtimestamp(int(start_time)))
    for k, v in kwargs.items():
        if v is not None:
            d = {k: v}
            q &= Q(**d)
    return q


def get_encoded_file(filename: str):
    with open(str(filename), 'rb') as f:
        return base64.b64encode(bytes(f.read())).decode()


def get_model_dict(model: models.models.Model, excluded_fields: list=None, modify_fields: dict=None):
    result_dict = {}
    for field in model._meta.get_fields():
        if field.name == 'id' or isinstance(field, (models.models.ManyToOneRel, models.models.OneToOneRel, models.models.ManyToManyRel)):
            continue
        if excluded_fields and field.name in excluded_fields:
            continue
        modify_flag = False
        key_name = field.name
        if modify_fields and field.name in modify_fields:
            key_name = modify_fields[field.name]
            modify_flag = True

        if isinstance(field, (models.models.ForeignKey, models.models.OneToOneField, models.models.ManyToManyField)):
            field_value = eval('model.%s_id' % field.name)
            if not modify_flag:
                key_name = '%s_id' % field.name
        else:
            field_value = eval('model.%s' % field.name)

        if field_value is None:
            continue
        if isinstance(field, models.models.BinaryField):
            field_value = base64.b64encode(field_value).decode()
        elif isinstance(field, models.models.DateTimeField):
            field_value = int(field_value.timestamp())
        elif isinstance(field, (models.models.ImageField, models.models.FileField)):
            field_value = get_encoded_file(field_value)
        if field.db_column and not modify_flag:
            key_name = field.db_column
        result_dict.update({key_name: field_value})
    return result_dict
