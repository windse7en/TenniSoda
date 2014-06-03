from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


# Create your models here.

class AccountManager(BaseUserManager):
    def create_user(self, email, password=None):
        """

        Creates and saves a User with the given email and password
        :param email:
        :param password:
        :return:
        """
        if not email:
            raise ValueError('You must provide an email address')

        user = self.model(
<<<<<<< HEAD
            email=self.normalize_email(email),
=======
            email=AccountManager.normalize_email(email),
>>>>>>> adc855ff71d051fa68cd4d6e8b71a27a8cc0e713
        )


        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """

        Creates and saves a superuser with the email and password.
        :param email:
        :param password:
        :return:
        """
        user = self.create_user(email, password=password,)
        user.is_admin = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        db_index=True,
    )
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class Profile(models.Model):
	LEVEL=(('1','1'),('1.5','1.5'),('2','2'),('2.5','2.5'),('3','3'),('3.5','3.5'),('4','4'),('4.5','4.5'),('5','5'),('5.5','5.5'),('6','6'),('6.5','6.5'),('7','7'),('7.5','7.5'),)
	GENDER=(('1','male'),('0','female'))
	CITY=(('1','Suzhou'),('2','Beijing'),('3','Shanghai'))
	user = models.OneToOneField(Account,primary_key=True)
	username = models.CharField(max_length = 100)
	level = models.CharField(max_length=15, choices=LEVEL, default='3')
	phone = models.CharField(max_length=11)
	gender = models.CharField(max_length=2, choices=GENDER)
	city = models.CharField(max_length=3,choices=CITY, default='1')
	
Account.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])
