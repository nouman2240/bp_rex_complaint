# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import http
from odoo.exceptions import ValidationError
from odoo.tests.common import HttpCase, tagged


@tagged('-at_install', 'post_install')
class RexComplaint(HttpCase):

    def setUp(self):
        super(RexComplaint, self).setUp()
        self.building_id = self.env['rex.building'].create({
            'building_name': 'building1',
            'building_city': 'Meg',
            'postal_code': '123',
        })
        self.flat_id = self.env['rex.flat'].create({
            'name': 'flat1',
            'building_id': self.building_id,
            'representative_id': self.env.user.partner_id.id
        })
        self.type_id = self.env['rex.complaint.type'].create({
            'name': 'heating isssue',
        })

    def test_website_complaint_submission(self):
        """ Public user should be able to submit a ticket"""
        self.authenticate(None, None)
        complaint_data = {
            'tenant_name': "jean",
            'tenant_email': 'jean@michel.com',
            'building_id': self.building_id.id,
            'flat_id': self.flat_id.id,
            'type_id': self.type_id.id,
            'description': 'Heating issue',
            'csrf_token': http.Request.csrf_token(self),
        }
        response = self.url_open('/website/form/rex.complaint.ticket', data=complaint_data)
        complaint = self.env['rex.complaint.ticket'].browse(response.json().get('id'))
        self.assertTrue(complaint.exists())
        complaint_submitted_response = self.url_open('/your-ticket-has-been-submitted')
        self.assertEqual(complaint_submitted_response.status_code, 200)
        complaint_submitted_response_ticket_id = (
            re.search(
                rb'Your Complaint Number is #<span>(?P<ticket_id>.*?)</span>',
                complaint_submitted_response.content)
            .group('ticket_id')
        ).decode()
        self.assertIn(
            complaint_submitted_response_ticket_id,
            (complaint.ticket_ref, str(complaint.id)),
            "Ticket ID on the submitted page does not match with the ticket created"
        )

    def test_website_complaint_submission_multiple(self):
        REPEAT = 3
        for i in range(REPEAT):
            try:
                self.test_website_complaint_submission()
            except AssertionError:
                raise AssertionError("Fail on the iteration %s/%s" % (i+1, REPEAT))
