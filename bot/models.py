from datetime import timedelta,datetime

from django.db import models


# Create your models here.

class MessengerUser(models.Model):
    id = models.CharField(max_length=25, primary_key=True)
    first_name = models.TextField(max_length=30)
    last_name = models.TextField(max_length=30)
    email = models.EmailField(max_length=100, null=True)
    appid = models.CharField(max_length=25, null=True, db_index=True)
    context = models.TextField(default="{}")


class UserActivity(models.Model):
    class Meta:
        unique_together = (('uid', 'activity_name'),)

    uid = models.ForeignKey(MessengerUser, on_delete=models.CASCADE)
    activity_name = models.CharField(max_length=30)
    is_productive = models.BooleanField(default=False)


class Checkin(models.Model):
    activity = models.OneToOneField(UserActivity, on_delete=models.CASCADE, primary_key=True)
    check_in_time = models.DateTimeField(auto_now_add=True)


class CheckinStore(models.Model):
    activity = models.ForeignKey(UserActivity, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(blank=False)
    check_out_time = models.DateTimeField(auto_now_add=True)
    total_time = models.FloatField()

    def save(self, *args, **kwargs):
        import pytz
        if self.check_out_time == None:
            self.check_out_time = pytz.timezone("Asia/Kolkata").localize(datetime.now())
        time_diff: timedelta = self.check_out_time - self.check_in_time
        self.total_time = time_diff.total_seconds() / 3600
        super(CheckinStore, self).save(*args, **kwargs)
