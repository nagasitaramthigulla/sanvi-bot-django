from bot.messenger import *

u=MessengerUser.objects.all()[2]

uas=["python","django","node","facebook","twitter","quora","whatsapp","webapp","machinelearning","cycling","gym","cricket","football","volleyball","deeplearning"]
import random
for i in random.sample(uas,10):
    ua=UserActivity(uid=u,activity_name=i)
    ua.save()
d=pytz.timezone("Asia/Kolkata").localize(datetime.now()-timedelta(days=55))
for i in range(40):
    cs=CheckinStore.objects.create(activity=random.choice(ual),check_in_time=d)
    d+=timedelta(hours=random.randint(0,5),minutes=random.randint(0,59))
    cs.check_out_time=d
    cs.save()
