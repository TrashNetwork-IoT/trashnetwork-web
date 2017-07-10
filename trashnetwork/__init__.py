import datetime
import os
import sys

from trashnetwork.settings import BASE_DIR


def create_test_data(sender, **kwargs):
    from trashnetwork.models import CleaningAccount
    from trashnetwork.models import RecycleAccount
    from trashnetwork.models import Trash
    from trashnetwork.models import CleaningGroup
    from trashnetwork.models import CleaningGroupMembership
    from trashnetwork.models import RecyclePoint
    from trashnetwork import models

    test_cleaner_account = CleaningAccount.objects.filter(user_id=123456)
    test_manager_account = CleaningAccount.objects.filter(user_id=233333)
    test_recycle_account = RecycleAccount.objects.filter(user_name='test')
    img_file = open(os.path.join(BASE_DIR, 'trashnetwork/default_portrait.png'), 'rb')
    img_bin = bytes(img_file.read())
    if not test_cleaner_account:
        test_cleaner_account = CleaningAccount(user_id=123456,
                                               phone_number='123456',
                                               password='123456',
                                               gender='M',
                                               account_type='C',
                                               name='Test Cleaner 1',
                                               portrait=img_bin)
        test_cleaner_account.save()
        print('Test cleaning cleaner account created.')
    else:
        test_cleaner_account = test_cleaner_account.get()

    if not test_manager_account:
        test_manager_account = CleaningAccount(user_id=233333,
                                               phone_number='233333',
                                               password='123456',
                                               gender='F',
                                               account_type='M',
                                               name='Test Manager 1',
                                               portrait=img_bin)
        test_manager_account.save()
        print('Test cleaning manager account created.')
    else:
        test_manager_account = test_manager_account.get()

    if not test_recycle_account:
        test_recycle_account = RecycleAccount(user_id=100, user_name='test',
                                              password='123456',
                                              account_type=models.RECYCLE_ACCOUNT_GARBAGE_COLLECTOR,
                                              email='foo@example.com', credit=0,
                                              register_date=datetime.date.today())
        test_recycle_account.save()
        print('Test recycle account created.')
    else:
        test_recycle_account = test_recycle_account.get()

    if not RecyclePoint.objects.all():
        test_recycle_point = RecyclePoint(point_id=1,
                                          description='Trash can on layer 2, No.9 student apartment',
                                          longitude=116.355769,
                                          latitude=39.96431,
                                          owner=test_recycle_account,
                                          bottle_num=0)
        test_recycle_point.save()
        print('Test recycle point created.')

    if not Trash.objects.all():
        test_trash = Trash(trash_id=1,
                           description='Trash can on layer 2, No.9 student apartment',
                           longitude=116.355769,
                           latitude=39.96431)
        test_trash.save()
        print('Test trash created.')
    if not CleaningGroup.objects.all():
        work_group = CleaningGroup(group_id=models.SPECIAL_WORK_GROUP_ID, name='Work Group', portrait=img_bin)
        work_group.save()
        print('Work group created.')
        test_group = CleaningGroup(name='Test Group', portrait=img_bin)
        test_group.save()
        member = CleaningGroupMembership(group=test_group, user=test_cleaner_account)
        member.save()
        member = CleaningGroupMembership(group=test_group, user=test_manager_account)
        member.save()
        print('Test group created.')

if sys.argv[1] == 'migrate':
    from django.db.models.signals import post_migrate
    post_migrate.connect(create_test_data)
elif sys.argv[1] == 'runserver':
    default_app_config = 'trashnetwork.apps.TrashNetworkConfig'
