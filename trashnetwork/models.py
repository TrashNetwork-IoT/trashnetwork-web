from django.db import models

# Create your models here.

CLEANING_ACCOUNT_GENDER_MALE = 'M'
CLEANING_ACCOUNT_GENDER_FEMALE = 'F'
CLEANING_ACCOUNT_TYPE_CLEANER = 'C'
CLEANING_ACCOUNT_TYPE_MANAGER = 'M'
SPECIAL_WORK_GROUP_ID = 1


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

    def __str__(self):
        return 'Cleaning user ' + self.name


class Trash(models.Model):
    trash_id = models.BigAutoField(primary_key=True)
    description = models.CharField(null=True, max_length=60)
    longitude = models.FloatField(null=False)
    latitude = models.FloatField(null=False)
    bottle_recycle = models.BooleanField(null=False, default=False)

    def __str__(self):
        return 'Trash %s' % (self.description)


class CleaningGroup(models.Model):
    group_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    portrait = models.BinaryField(null=False)

    def __str__(self):
        return 'Cleaning group %s' % (self.name)


class CleaningGroupMembership(models.Model):
    group = models.ForeignKey(CleaningGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(CleaningAccount, on_delete=models.CASCADE)

    class Meta:
        db_table = 'cleaning_group_member'
        unique_together = ('group', 'user')

    def __str__(self):
        return 'Cleaning user %s in %s' % (self.user.name, self.group.name)


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

    def __str__(self):
        return 'Cleaning bulletin %s in group %s' % (self.title, self.group.name)


class CleaningWorkRecord(models.Model):
    user = models.ForeignKey(CleaningAccount, on_delete=models.CASCADE)
    trash = models.ForeignKey(Trash, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'timestamp')
        ordering = ['-timestamp']

    def __str__(self):
        return 'Cleaning user %s at trash %s' % (self.user.name, self.trash.description)


class RecycleAccount(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    user_name = models.CharField(max_length=20, null=False, unique=True)
    password = models.CharField(max_length=20, null=False)
    email = models.EmailField(null=False)
    credit = models.IntegerField(null=False, default=0)
    register_date = models.DateField(auto_now_add=True, null=False)

    def __str__(self):
        return 'Recycle user %s' % (self.user_name)


class RecycleCreditRecord(models.Model):
    user = models.ForeignKey(RecycleAccount, on_delete=models.CASCADE, null=False)
    good_description = models.CharField(null=False, max_length=100)
    quantity = models.IntegerField(null=False, default=1)
    credit = models.IntegerField(null=False, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'timestamp')
        ordering = ['-timestamp']

    def __str__(self):
        return 'Recycle credit %s' % (self.good_description)


class Feedback(models.Model):
    poster = models.ForeignKey(RecycleAccount, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=60, null=False)
    text = models.TextField(null=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return 'Feedback %s' % (self.title)
