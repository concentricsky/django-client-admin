from django.db import models

class Federation(models.Model):
    name = models.CharField(max_length=127)

    def __unicode__(self):
        return self.name

class Quadrant(models.Model):
    name = models.CharField(max_length=127)
    federation = models.ForeignKey(Federation)

    def __unicode__(self):
        return self.name

class Planet(models.Model):
    name = models.CharField(max_length=127)
    quadrant = models.ForeignKey(Quadrant)

    def __unicode__(self):
        return self.name

class Starship(models.Model):
    name = models.CharField(max_length=127)
    federation = models.ForeignKey(Federation)

    def __unicode__(self):
        return self.name

class Crew(models.Model):
    name = models.CharField(max_length=127)
    rank = models.CharField(max_length=127)
    starshp = models.ForeignKey(Starship)

    def __unicode__(self):
        return "%s %s " % (self.rank, self.name)

class Mission(models.Model):
    content = models.TextField()
    starship = models.ForeignKey(Starship)

    def __unicode__(self):
        return self.content
