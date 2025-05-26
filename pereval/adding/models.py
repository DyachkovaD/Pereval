from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.functions import Now



class Users(models.Model):
    email = models.EmailField(unique=True)
    fam = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    otc = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=25, null=True, blank=True)

    class Meta:
        managed = True
        db_table = "Users"


class Status(models.TextChoices):
    NEW = "new",
    PEND = "pending",
    ACC = "accepted",
    REJ = "rejected"


class Pereval(models.Model):
    beauty_title = models.TextField(null=True, blank=True)
    title = models.TextField()
    connect = models.TextField(null=True, blank=True)

    add_time = models.DateTimeField(db_default=Now())

    other_titles = models.CharField(max_length=10, null=True, blank=True)
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
    date_added = models.DateTimeField(db_default=Now())
    img = models.BinaryField()
    title = models.TextField(null=True, blank=True)
    pereval = models.ForeignKey(
        'adding.Pereval',
        models.CASCADE,
        related_name='images',
    )

    class Meta:
        managed = True
        db_table = "pereval_images"


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
