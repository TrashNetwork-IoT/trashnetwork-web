import os
import sys
from trashnetwork.settings import BASE_DIR


def register_test_account(sender, **kwargs):
    from trashnetwork.models import CleaningAccount

    test_cleaner_account = CleaningAccount.objects.filter(user_id=123456)
    test_manager_account = CleaningAccount.objects.filter(user_id=233333)
    if not test_cleaner_account or not test_manager_account:
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
            print('Test cleaner account created.')

        if not test_manager_account:
            test_manager_account = CleaningAccount(user_id=233333,
                                                   phone_number='233333',
                                                   password='123456',
                                                   gender='F',
                                                   account_type='M',
                                                   name='Test Manager 1',
                                                   portrait=img_bin)
            test_manager_account.save()
            print('Test manager account created.')


if sys.argv[1] == 'migrate':
    from django.db.models.signals import post_migrate
    post_migrate.connect(register_test_account)
