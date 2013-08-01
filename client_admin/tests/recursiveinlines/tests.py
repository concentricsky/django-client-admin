#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Concentric Sky, Inc.
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

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.test.utils import override_settings

from .admin import *
from .models import *


@override_settings(PASSWORD_HASHERS=('django.contrib.auth.hashers.SHA1PasswordHasher',))
class TestRecursiveInline(TestCase):
    urls = 'client_admin.tests.recursiveinlines.urls'
    fixtures = ['admin-views-users.xml', 'federation.xml']

    def setUp(self):
        #holder = Holder(dummy=13)
        #holder.save()
        #Inner(dummy=42, holder=holder).save()
        #self.change_url = '/admin/admin_inlines/holder/%i/' % holder.id

        result = self.client.login(username='super', password='secret')
        self.assertEqual(result, True)

    def tearDown(self):
        self.client.logout()

    def test_view(self):
        response = self.client.get('/admin/recursiveinlines/federation/1/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="inline-group" id="quadrant_set-group">')
        self.assertContains(response, 'Add another Planet')
        self.assertContains(response, 'Add another Quadrant')
        self.assertContains(response, '<div class="inline-group" id="starship_set-group">')
        self.assertContains(response, 'Add another Crew')
        self.assertContains(response, 'Add another Mission')

    def test_edit(self):
        data = {
            'name' : 'United Federation of Planets',
            'quadrant_set-TOTAL_FORMS' : '3',
            'quadrant_set-INITIAL_FORMS' : '2',
            'quadrant_set-0-name' : 'Alpha',
            'quadrant_set-0-id' : '1',
            'quadrant_set-0-federation' : '1',
            'quadrant_set-0-planet_set-TOTAL_FORMS' : '5',
            'quadrant_set-0-planet_set-INITIAL_FORMS' : '2',
            'quadrant_set-0-planet_set-0-id' : '1',
            'quadrant_set-0-planet_set-0-quadrant' : '1',
            'quadrant_set-0-planet_set-0-name' : 'Earth',
            'quadrant_set-0-planet_set-1-id' : '2',
            'quadrant_set-0-planet_set-1-quadrant' : '1',
            'quadrant_set-0-planet_set-1-name' : 'Omicron Persei 8',
            'quadrant_set-0-planet_set-1-DELETE' : 'on',
            'quadrant_set-0-planet_set-2-quadrant' : '1',
            'quadrant_set-0-planet_set-3-quadrant' : '1',
            'quadrant_set-0-planet_set-4-quadrant' : '1',
            'quadrant_set-0-planet_set-__prefix__-quadrant' : '1',
            'quadrant_set-1-name' : 'Beta',
            'quadrant_set-1-id' : '2',
            'quadrant_set-1-federation' : '1',
            'quadrant_set-1-planet_set-TOTAL_FORMS' : '4',
            'quadrant_set-1-planet_set-INITIAL_FORMS' : '1',
            'quadrant_set-1-planet_set-0-id' : '3',
            'quadrant_set-1-planet_set-0-quadrant' : '2',
            'quadrant_set-1-planet_set-0-name' : 'Qo\'noS',
            'quadrant_set-1-planet_set-1-quadrant' : '2',
            'quadrant_set-1-planet_set-2-quadrant' : '2',
            'quadrant_set-1-planet_set-3-quadrant' : '2',
            'quadrant_set-1-planet_set-__prefix__-quadrant' : '2',
            'quadrant_set-2-name' : 'Gamma',
            'quadrant_set-2-federation' : '1',
            'quadrant_set-__prefix__-federation' : '1',
            'starship_set-TOTAL_FORMS' : '2',
            'starship_set-INITIAL_FORMS' : '2',
            'starship_set-0-name' : 'Enterprise',
            'starship_set-0-id' : '1',
            'starship_set-0-federation' : '1',
            'starship_set-0-crew_set-TOTAL_FORMS' : '3',
            'starship_set-0-crew_set-INITIAL_FORMS' : '3',
            'starship_set-0-crew_set-0-id' : '1',
            'starship_set-0-crew_set-0-starshp' : '1',
            'starship_set-0-crew_set-0-name' : 'Jean-Luc Picard',
            'starship_set-0-crew_set-0-rank' : 'Captain',
            'starship_set-0-crew_set-1-id' : '2',
            'starship_set-0-crew_set-1-starshp' : '1',
            'starship_set-0-crew_set-1-name' : 'William Riker',
            'starship_set-0-crew_set-1-rank' : 'Commander',
            'starship_set-0-crew_set-2-id' : '3',
            'starship_set-0-crew_set-2-starshp' : '1',
            'starship_set-0-crew_set-2-name' : 'Data',
            'starship_set-0-crew_set-2-rank' : 'Lieutenant Commander',
            'starship_set-0-crew_set-__prefix__-starshp' : '1',
            'starship_set-0-mission_set-TOTAL_FORMS' : '6',
            'starship_set-0-mission_set-INITIAL_FORMS' : '3',
            'starship_set-0-mission_set-0-id' : '1',
            'starship_set-0-mission_set-0-starship' : '1',
            'starship_set-0-mission_set-0-content' : 'to explore strange new worlds',
            'starship_set-0-mission_set-1-id' : '2',
            'starship_set-0-mission_set-1-starship' : '1',
            'starship_set-0-mission_set-1-content' : 'to seek out new life forms and new civilizations',
            'starship_set-0-mission_set-2-id' : '3',
            'starship_set-0-mission_set-2-starship' : '1',
            'starship_set-0-mission_set-2-content' : 'to go boldly where no one has gone before',
            'starship_set-0-mission_set-3-starship' : '1',
            'starship_set-0-mission_set-4-starship' : '1',
            'starship_set-0-mission_set-5-starship' : '1',
            'starship_set-0-mission_set-__prefix__-starship' : '1',
            'starship_set-1-name' : 'Planet Express Ship',
            'starship_set-1-id' : '2',
            'starship_set-1-federation' : '1',
            'starship_set-1-crew_set-TOTAL_FORMS' : '3',
            'starship_set-1-crew_set-INITIAL_FORMS' : '3',
            'starship_set-1-crew_set-MAX_NUM_FORMS' : '',
            'starship_set-1-crew_set-0-id' : '4',
            'starship_set-1-crew_set-0-starshp' : '2',
            'starship_set-1-crew_set-0-name' : 'Turanga Leela',
            'starship_set-1-crew_set-0-rank' : 'Captain',
            'starship_set-1-crew_set-1-id' : '5',
            'starship_set-1-crew_set-1-starshp' : '2',
            'starship_set-1-crew_set-1-name' : 'Philip J. Fry',
            'starship_set-1-crew_set-1-rank' : 'Delivery Boy',
            'starship_set-1-crew_set-2-id' : '6',
            'starship_set-1-crew_set-2-starshp' : '2',
            'starship_set-1-crew_set-2-name' : 'Bender Bending RodrÃ­guez',
            'starship_set-1-crew_set-2-rank' : 'Cook',
            'starship_set-1-crew_set-__prefix__-starshp' : '2',
            'starship_set-1-mission_set-TOTAL_FORMS' : '4',
            'starship_set-1-mission_set-INITIAL_FORMS' : '1',
            'starship_set-1-mission_set-0-id' : '4',
            'starship_set-1-mission_set-0-starship' : '2',
            'starship_set-1-mission_set-0-content' : 'When you see the robot: DRINK!',
            'starship_set-1-mission_set-1-starship' : '2',
            'starship_set-1-mission_set-2-starship' : '2',
            'starship_set-1-mission_set-3-starship' : '2',
            'starship_set-1-mission_set-__prefix__-starship' : '2',
            'starship_set-__prefix__-federation' : '1',
        }

        self.assertEqual(Planet.objects.filter(name='Omicron Persei 8').count(), 1)
        self.assertEqual(Quadrant.objects.filter(name='Gamma').count(), 0)
        self.assertEqual(Mission.objects.get(pk=3).content, 'to boldly go where no one has gone before')

        response = self.client.post('/admin/recursiveinlines/federation/1/', data)
        self.assertEqual(response.status_code, 302)

        # we deleted Omicron Persei 8, added the Gamma Quadrant, and
        # updated the Enterprise's misison statement
        self.assertEqual(Planet.objects.filter(name='Omicron Persei 8').count(), 0)
        self.assertEqual(Quadrant.objects.filter(name='Gamma').count(), 1)
        self.assertEqual(Mission.objects.get(pk=3).content, 'to go boldly where no one has gone before')

    def test_add(self):
        response = self.client.get('/admin/recursiveinlines/federation/add/')
        self.assertEqual(response.status_code, 200)

        data = {
            'name' : 'Terran Empire',
            'quadrant_set-TOTAL_FORMS' : '1',
            'quadrant_set-INITIAL_FORMS' : '0',
            'quadrant_set-0-name' : 'Zeta',
            'starship_set-TOTAL_FORMS' : '1',
            'starship_set-INITIAL_FORMS' : '0',
            'starship_set-0-name' : 'Avenger',
        }

        response = self.client.post('/admin/recursiveinlines/federation/add/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Federation.objects.filter(name='Terran Empire').count(), 1)
        self.assertEqual(Quadrant.objects.filter(name='Zeta').count(), 1)
        self.assertEqual(Starship.objects.filter(name='Avenger').count(), 1)

