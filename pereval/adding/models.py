from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.functions import Now


class Users(AbstractUser):
    patronymic = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)

    class Meta(AbstractUser.Meta):
        db_table = "auth_user"
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email')
        ]


class Status(models.TextChoices):
    NEW = "new",
    PEND = "pending",
    ACC = "accepted",
    REJ = "rejected"


class Pereval(models.Model):
    beauty_title = models.TextField(null=True, blank=True)
    title = models.TextField()
    connect = models.TextField(null=True, blank=True)

    other_titles = ArrayField(models.CharField(), default=[])
    add_time = models.DateTimeField(db_default=Now())

    winter = models.CharField(max_length=10, null=True, blank=True)
    summer = models.CharField(max_length=10, null=True, blank=True)
    autumn = models.CharField(max_length=10, null=True, blank=True)
    spring = models.CharField(max_length=10, null=True, blank=True)
    status = models.CharField(choices=Status.choices, max_length=10, default=Status.NEW)
    coord_id = models.ForeignKey(
        'adding.Coords',
        models.SET_NULL,
        null=True,
        blank=True,
    )
    added_user = models.ForeignKey(
        'adding.Users',
        models.SET_NULL,
        null=True,
    )

    images = models.ManyToManyField('Image', through='PerevalImages', related_name='perevals')

    class Meta:
        managed = True
        db_table = "pereval_added"


class Coords(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    height = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "Coords"


class Image(models.Model):
    date_added = models.DateTimeField()
    img = models.BinaryField()
    title = models.TextField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = "pereval_images"


class PerevalImages(models.Model):
    pereval = models.ForeignKey(Pereval, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = "PerevalImages"


class Area(models.Model):
    id_parent = models.IntegerField()
    title = models.TextField()

    class Meta:
        managed = True
        db_table = "pereval_areas"


class SPRActivityTypes(models.Model):
    title = models.TextField()

    class Meta:
        managed = True
        db_table = "spr_activities_types"
