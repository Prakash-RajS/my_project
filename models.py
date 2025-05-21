"""from django.db import models
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
        return f"{self.user.email if self.user.email else self.user.userid} - {self.current_plan}""""
from django.db import models
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
import secrets #api 

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
        ('platinum', 'Platinum'),
    )

    DURATION_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserData', on_delete=models.CASCADE, related_name='subscriptions')

    email = models.EmailField(blank=True, null=True)
    userid = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    current_plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='basic')
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES, blank=True, null=True)
    original_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    discount_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)

    total_members = models.IntegerField(default=1)  # Automatically calculated in save()

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
        # Auto-set total_members based on current_plan
        plan_members_map = {
            'basic': 1,
            'silver': 1,
            'gold': 5,
            'platinum': 7
        }
        self.total_members = plan_members_map.get(self.current_plan, 1)

        # Set renews_on and plan_expiring_date only if not basic
        if self.current_plan != 'basic':
            if self.duration == 'monthly':
                self.renews_on = timezone.now().date() + relativedelta(months=1)
                self.plan_expiring_date = timezone.now() + relativedelta(months=1)
            elif self.duration == 'yearly':
                self.renews_on = timezone.now().date() + relativedelta(years=1)
                self.plan_expiring_date = timezone.now() + relativedelta(years=1)
        else:
            self.renews_on = None
            self.plan_expiring_date = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email or self.user.userid} - {self.current_plan}"



class BillingHistory(models.Model):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name="billing_history")
    plan_name = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=[
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("pending", "Pending")
    ])
    
    invoice_id = models.CharField(max_length=100, unique=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    paid_on = models.DateField(default=timezone.now)
    invoice = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan_name} - {self.paid_on}"
    


class BillingInfo(models.Model):
    user = models.ForeignKey('UserData', on_delete=models.CASCADE, related_name='billing_infos')
    
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)

    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.full_name} - {self.email}"



class APIKeyManager(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Basic (10 credits/month)'),
        ('pro', 'Pro (50 credits/month)'),
        ('enterprise', 'Enterprise (Unlimited)'),
    ]

    user = models.OneToOneField('UserData', on_delete=models.CASCADE, related_name='api_key_manager')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')
    active_keys = models.CharField(max_length=50, help_text="List of active API keys, e.g. ['asfrbrrrnrnrrdaas']")
    revoked_keys = models.JSONField(default=list, help_text="Audit history of revoked keys with reason and date")
    monthly_credits = models.IntegerField(default=10, help_text="Credits allocated per month based on plan")
    credits_remaining = models.IntegerField(default=0, help_text="monthly_credits - usage_count")
    usage_count = models.IntegerField(default=0, help_text="Number of credits used this month")
    is_active = models.BooleanField(default=True, help_text="If false, all keys disabled globally")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Update credits_remaining based on usage_count and monthly_credits
        self.credits_remaining = max(self.monthly_credits - self.usage_count, 0)

        # Deactivate if credits exhausted and not enterprise plan
        if self.plan != 'enterprise' and self.credits_remaining == 0:
            self.is_active = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} | Plan: {self.plan} | Active: {self.is_active} | Credits left: {self.credits_remaining}"

    class Meta:
        verbose_name = "API Key Manager"
        verbose_name_plural = "API Key Managers"



class APILog(models.Model):
    api_key = models.ForeignKey(APIKeyManager, on_delete=models.CASCADE, related_name='logs')
    request_time = models.DateTimeField(auto_now_add=True)
    endpoint = models.CharField(max_length=255)
    status_code = models.IntegerField()
    message = models.TextField(blank=True, null=True)

    # Future fields (optional)
    #ip_address = models.GenericIPAddressField(blank=True, null=True)
    #user_agent = models.TextField(blank=True, null=True)
    #method = models.CharField(max_length=10, blank=True, null=True)
    #duration_ms = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.api_key.key[:8]}... - {self.endpoint} - {self.request_time}"
 

class ApiAccessRequest(models.Model):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    contact_number = models.CharField(max_length=15)
    company_name = models.CharField(max_length=150, blank=True)
    address = models.TextField(blank=True)
    message = models.TextField()
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.email})"
