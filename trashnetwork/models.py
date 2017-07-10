import os

from django.core.files.storage import FileSystemStorage
from django.db import models

# Create your models here.
from django.utils.safestring import mark_safe

from trashnetwork import settings

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
        result = 'Unknown-'
        if self.account_type == CLEANING_ACCOUNT_TYPE_CLEANER:
            result = 'Cleaner-'
        else:
            result = 'Manager-'
        return result + self.name


class Trash(models.Model):
    trash_id = models.BigAutoField(primary_key=True)
    description = models.CharField(null=True, max_length=60)
    longitude = models.FloatField(null=False)
    latitude = models.FloatField(null=False)

    def __str__(self):
        return '#%d %s' % (self.trash_id, self.description)


class CleaningGroup(models.Model):
    group_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    portrait = models.BinaryField(null=False)

    def __str__(self):
        return '#%d %s' % (self.group_id, self.name)


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
    timestamp = models.DateTimeField(auto_now_add=True, db_column='post_time')
    title = models.CharField(max_length=60, null=False)
    text = models.TextField(null=False)

    class Meta:
        unique_together = ('group', 'poster', 'timestamp')
        ordering = ['-timestamp']

    def __str__(self):
        return 'Bulletin %s in group %s' % (self.title, self.group.name)


class CleaningWorkRecord(models.Model):
    user = models.ForeignKey(CleaningAccount, on_delete=models.CASCADE)
    trash = models.ForeignKey(Trash, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True, db_column='record_time')

    class Meta:
        unique_together = ('user', 'timestamp')
        ordering = ['-timestamp']

    def __str__(self):
        return '%s at %s' % (self.user.name, self.trash.description)


RECYCLE_ACCOUNT_NORMAL_USER = 'N'
RECYCLE_ACCOUNT_GARBAGE_COLLECTOR = 'C'


class RecycleAccount(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    user_name = models.CharField(max_length=20, null=False, unique=True)
    password = models.CharField(max_length=20, null=False)
    account_type = models.CharField(max_length=1, choices=(
        (RECYCLE_ACCOUNT_NORMAL_USER, 'Normal User'),
        (RECYCLE_ACCOUNT_GARBAGE_COLLECTOR, 'Garbage Collector')
    ), null=False, blank=False)
    email = models.EmailField(null=False)
    credit = models.IntegerField(null=False, default=0)
    delivery_address = models.TextField(null=True)
    register_date = models.DateField(auto_now_add=True, null=False)

    def __str__(self):
        result = 'Unknown: '
        if self.account_type == RECYCLE_ACCOUNT_NORMAL_USER:
            result = 'User - '
        else:
            result = 'Garbage Collector - '
        return result + self.user_name


class RecycleCreditRecord(models.Model):
    user = models.ForeignKey(RecycleAccount, on_delete=models.CASCADE, null=False)
    item_description = models.CharField(null=False, max_length=100)
    credit = models.IntegerField(null=False, default=0)
    timestamp = models.DateTimeField(auto_now_add=True, db_column='record_time')

    class Meta:
        unique_together = ('user', 'timestamp')
        ordering = ['-timestamp']

    def __str__(self):
        return '%s - %s x%d - %s' % (self.user.user_name, self.item_description, self.quantity, str(self.timestamp))


class RecyclePoint(models.Model):
    point_id = models.BigAutoField(primary_key=True, null=False)
    owner = models.ForeignKey(RecycleAccount, on_delete=models.CASCADE, null=False)
    description = models.CharField(null=True, max_length=60)
    longitude = models.FloatField(null=False)
    latitude = models.FloatField(null=False)
    bottle_num = models.IntegerField(null=True)

    def __str__(self):
        return '#%d %s' % (self.point_id, self.description)


class RecycleCleaningRecord(models.Model):
    user = models.ForeignKey(RecycleAccount, on_delete=models.CASCADE, null=False)
    recycle_point = models.ForeignKey(RecyclePoint, on_delete=models.CASCADE, null=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_column='recycle_time')
    bottle_num = models.IntegerField(null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return '%s - %s - %s' % (self.user.user_name, self.recycle_point.description, str(self.timestamp))


class Feedback(models.Model):
    poster = models.ForeignKey(RecycleAccount, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_column='feedback_time')
    title = models.CharField(max_length=60, null=False)
    text = models.TextField(null=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        user_name = 'Anonymous User'
        if self.poster:
            user_name = self.poster.user_name
        return '%s - %s - %s' % (self.title, user_name, str(self.timestamp))


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, **kwargs):
        if self.exists(name):
            os.remove(name)
        return name


class Event(models.Model):
    title = models.CharField(max_length=50, null=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_column='release_time')
    digest = models.CharField(max_length=120, null=True)
    event_image = models.ImageField(null=True, upload_to='trashnetwork/events/assets/images', storage=OverwriteStorage())
    url = models.CharField(max_length=256, null=True)

    def event_image_preview(self):
        if not self.event_image:
            return 'No image'
        return mark_safe('<img src="/%s" width=400/>' % self.event_image)

    class Meta:
        unique_together = ('title', 'timestamp')
        ordering = ['-timestamp']

    def __str__(self):
        return '%s - %s' % (self.title, str(self.timestamp))


COMMODITY_TYPE_VIRTUAL = 'V'
COMMODITY_TYPE_PHYSICAL = 'P'


class Commodity(models.Model):
    commodity_id = models.BigAutoField(primary_key=True, null=False)
    title = models.CharField(max_length=100, null=False)
    description = models.TextField(null=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_column='added_time')
    credit = models.IntegerField(null=False)
    thumbnail = models.ImageField(null=True,
                                  upload_to='trashnetwork/commodities/assets/thumbnails',
                                  storage=OverwriteStorage())
    stock = models.IntegerField(null=False)
    quantity_limit = models.IntegerField(null=False)
    commodity_type = models.CharField(max_length=1, null=False, choices=(
        (COMMODITY_TYPE_VIRTUAL, 'Virtual'),
        (COMMODITY_TYPE_PHYSICAL, 'Physical'),
    ))

    def commodity_thumbnail_preview(self):
        if not self.thumbnail:
            return 'No image'
        return mark_safe('<img src="/%s" width=200/>' % self.thumbnail)

    class Meta:
        unique_together = ('title', 'timestamp')
        ordering = ['-timestamp']

    def __str__(self):
        return '%s - %s' % (self.title, str(self.timestamp))


class CommodityImage(models.Model):
    commodity = models.ForeignKey(Commodity, null=False)
    image = models.ImageField(null=True,
                              upload_to='trashnetwork/commodities/assets/images',
                              storage=OverwriteStorage())

    def commodity_image_preview(self):
        if not self.image:
            return 'No image'
        return mark_safe('<img src="/%s" width=400/>' % self.image)

    def __str__(self):
        return '%s - %s' % (self.commodity.title, str(self.image))


ORDER_CANCELLED = 'C'
ORDER_DELIVERING = 'D'
ORDER_IN_PROGRESS = 'P'
ORDER_FINISHED = 'F'


class Order(models.Model):
    order_id = models.CharField(max_length=24, primary_key=True)
    buyer = models.ForeignKey(RecycleAccount, on_delete=models.CASCADE, null=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_column='submit_time')
    commodity_id = models.BigIntegerField(null=True)
    title = models.CharField(max_length=100, null=False)
    credit = models.IntegerField(null=False)
    quantity = models.IntegerField(null=False, default=1)
    remark = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=1, choices=(
        (ORDER_IN_PROGRESS, 'In progress'),
        (ORDER_DELIVERING, 'Delivering'),
        (ORDER_CANCELLED, 'Cancelled'),
        (ORDER_FINISHED, 'Finished'),
    ), default=ORDER_IN_PROGRESS)
    delivery_address = models.TextField(null=True)
    delivery = models.TextField(null=True)

    def __str__(self):
        return '%s - %s - %s' % (self.title, self.buyer.user_name, str(self.timestamp))

    class Meta:
        ordering = ['-timestamp']
