
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

