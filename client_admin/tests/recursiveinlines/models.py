# Copyright 2015 Concentric Sky, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
