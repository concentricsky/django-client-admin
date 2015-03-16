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

from django.contrib import admin
from client_admin import admin as client_admin
from django import forms

from .models import *


class PlanetInline(admin.StackedInline):
    model = Planet

class CrewInline(admin.StackedInline):
    model = Crew
    extra = 0

class MissionInline(admin.TabularInline):
    model = Mission

class StarshipInline(client_admin.StackedRecursiveInline):
    model = Starship
    inlines = [CrewInline, MissionInline]

class QuadrantInline(client_admin.StackedRecursiveInline):
    model = Quadrant
    inlines = [PlanetInline]

class FederationAdmin(client_admin.RecursiveInlinesModelAdmin):
    model = Federation
    inlines = [QuadrantInline, StarshipInline]

site = admin.AdminSite(name="admin")
site.register(Federation, FederationAdmin)

