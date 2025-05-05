from django.db import models
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone

# Manage signup, profile update, forget password, login pages
class UserData(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    provider = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    userid = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Social login field

    def __str__(self):
        return f"{self.email} ({self.provider})"


# Manage contact us page
class ContactUs(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    contact_number = models.CharField(max_length=15)
    subject = models.CharField(max_length=30)
    message = models.TextField()
    source = models.CharField(max_length=20, default='contact_us')
    submitted_at = models.DateTimeField(auto_now_add=True)


# Pricing page 
class UserSubscription(models.Model):
    PLAN_CHOICES = (
        ('basic', 'Basic'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
    )

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserData', on_delete=models.CASCADE, related_name='subscriptions')
    email = models.EmailField(blank=True, null=True)
    userid = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    current_plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='basic')
    pricing = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    start_date = models.DateField(auto_now_add=True)
    plan_expiring_date = models.DateTimeField(blank=True, null=True)
    renews_on = models.DateField(blank=True, null=True)

    total_credits = models.IntegerField(default=10)
    used_credits = models.IntegerField(default=0)
    total_credits_used_all_time = models.IntegerField(default=0)

    @property
    def balance_credits(self):
        return self.total_credits - self.used_credits

    def save(self, *args, **kwargs):
        if not self.renews_on:
            self.renews_on = timezone.now().date() + relativedelta(months=1)
        if not self.plan_expiring_date:
            self.plan_expiring_date = timezone.now() + relativedelta(months=1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email if self.user.email else self.user.userid} - {self.current_plan}"
