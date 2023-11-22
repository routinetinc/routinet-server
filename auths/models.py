from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,UserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class User(AbstractBaseUser,PermissionsMixin):
    table_name    = 'user'
    
    username         = models.CharField(max_length=20,unique=True)  
    email = models.EmailField(_("email address"), blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    USERNAME_FIELD = "username" 
    
    objects = UserManager()
    
    def __str__(self):
        return f"「{self.username}」"