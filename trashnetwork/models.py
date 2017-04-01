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


SPECIAL_WORK_GROUP_ID = 1


class CleaningGroup(models.Model):
    group_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    portrait = models.BinaryField(null=False)


class CleaningGroupMembership(models.Model):
    group = models.ForeignKey(CleaningGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(CleaningAccount, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('group', 'user')


# NOTE: All timestamp property must be named timestamp
class CleaningGroupBulletin(models.Model):
    poster = models.ForeignKey(CleaningAccount, on_delete=models.CASCADE)
    group = models.ForeignKey(CleaningGroup, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=60, null=False)
    text = models.TextField(null=False)

    class Meta:
        unique_together = ('group', 'poster', 'timestamp')
        ordering = ['-timestamp']


class RecycleAccount(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    user_name = models.CharField(max_length=20, null=False, unique=True)
    password = models.CharField(max_length=20, null=False)
    email = models.EmailField(null=False)
    credit = models.IntegerField(null=False, default=0)
    register_date = models.DateField(auto_now_add=True, null=False)


class RecycleCreditRecord(models.Model):
    user = models.ForeignKey(RecycleAccount, on_delete=models.CASCADE, null=False)
    good_description = models.CharField(null=False, max_length=100)
    quantity = models.IntegerField(null=False, default=1)
    credit = models.IntegerField(null=False, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'timestamp')
        ordering = ['-timestamp']


class Trash(models.Model):
    trash_id = models.BigAutoField(primary_key=True)
    description = models.CharField(null=True, max_length=60)
    longitude = models.FloatField(null=False)
    latitude = models.FloatField(null=False)
    bottle_recycle = models.BooleanField(null=False, default=False)


class Feedback(models.Model):
    poster = models.ForeignKey(RecycleAccount, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=60, null=False)
    text = models.TextField(null=False)

    class Meta:
        ordering = ['-timestamp']
