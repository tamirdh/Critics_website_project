# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Actor(models.Model):
    id = models.OneToOneField('Person', models.DO_NOTHING, db_column='ID', primary_key=True)  # Field name made lowercase.
    gender = models.CharField(max_length=45, blank=True, null=True)
    birthday = models.CharField(max_length=45, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    popularity = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Actor'


class Appearances(models.Model):
    movie = models.OneToOneField('Movie', models.DO_NOTHING, primary_key=True)
    actor = models.ForeignKey(Actor, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Appearances'
        unique_together = (('movie', 'actor'),)


class Critic(models.Model):
    bio = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=2083, blank=True, null=True)
    id = models.OneToOneField('Person', models.DO_NOTHING, db_column='ID', primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Critic'


class Director(models.Model):
    id = models.OneToOneField('Person', models.DO_NOTHING, db_column='ID', primary_key=True)  # Field name made lowercase.
    gender = models.CharField(max_length=45, blank=True, null=True)
    birthday = models.CharField(max_length=45, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Director'


class Genre(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    category_name = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'Genre'


class Movie(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    title = models.CharField(max_length=300, blank=True, null=True)
    category = models.ForeignKey(Genre, models.DO_NOTHING, blank=True, null=True)
    director = models.ForeignKey(Director, models.DO_NOTHING, blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    vote_avg = models.FloatField(blank=True, null=True)
    vote_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Movie'


class Person(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Person'


class Review(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    movie = models.ForeignKey(Movie, models.DO_NOTHING)
    critics_pick = models.IntegerField(blank=True, null=True)
    critic = models.ForeignKey(Critic, models.DO_NOTHING)
    headline = models.CharField(max_length=200, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    date = models.CharField(max_length=45, blank=True, null=True)
    link = models.CharField(max_length=2083, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Review'
