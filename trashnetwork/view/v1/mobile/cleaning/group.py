from rest_framework import status
from rest_framework.decorators import api_view

from trashnetwork.models import CleaningAccount


@api_view(['GET'])
def all_groups():
    pass


@api_view(['GET'])
def bulletin2(group_id, limit_num):
    pass


@api_view(['GET'])
def bulletin3(group_id, end_time, limit_num):
    pass


@api_view(['GET'])
def bulletin4(group_id, start_time, end_time, limit_num):
    pass


@api_view(['POST'])
def new_bulletin():
    pass

