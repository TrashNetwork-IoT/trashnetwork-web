from django.db import models

# Create your models here.

CLEANING_ACCOUNT_GENDER_MALE = 'M'
CLEANING_ACCOUNT_GENDER_FEMALE = 'F'
CLEANING_ACCOUNT_TYPE_CLEANER = 'C'
CLEANING_ACCOUNT_TYPE_MANAGER = 'M'


class CleaningAccount(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    phone_number = models.CharField(max_length=20)
    password = models.CharField(max_length=20, null=False)
    name = models.CharField(max_length=25, unique=True, null=False)
    gender = models.CharField(max_length=1, choices=(
        (CLEANING_ACCOUNT_GENDER_MALE, 'Male'),
        (CLEANING_ACCOUNT_GENDER_FEMALE, 'Female')
    ), null=False)
    account_type = models.CharField(max_length=1, choices=(
        (CLEANING_ACCOUNT_TYPE_CLEANER, 'Cleaner'),
        (CLEANING_ACCOUNT_TYPE_MANAGER, 'Manager')
    ), null=False)
    portrait = models.BinaryField(null=True)
    register_date = models.DateField(auto_now_add=True, null=False)

    class Meta:
        db_table = 'cleaning_account'


class CleaningGroup(models.Model):
    group_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    portrait = models.BinaryField(null=False)


class CleaningGroupMembership(models.Model):
    group = models.ForeignKey(CleaningGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(CleaningAccount, on_delete=models.CASCADE)


# NOTE: All timestamp property must be named timestamp
class CleaningBulletin(models.Model):
    poster = models.ForeignKey(CleaningAccount, on_delete=models.SET_NULL)
    group = models.ForeignKey(CleaningGroup, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=60, null=False)
    text = models.TextField(null=False)
