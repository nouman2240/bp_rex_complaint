# -*- coding: utf-8 -*-
# from odoo import http
from odoo.addons.website.controllers import form
from odoo.http import request

class WebsiteForm(form.WebsiteForm):

    def _handle_website_form(self, model_name, **kwargs):
        """
        finds customer represtentative assigned for the flat, tenant provided in website form and
        assigns to the complaint submitted.
        Creates or finds partner object based on email provided by tenant in website form.
        """
        email = kwargs.get('tenant_email')
        flat_id = kwargs.get('flat_id')
        if flat_id:
            flat_id = request.env['rex.flat'].sudo().search([('id','=',flat_id)])
            if flat_id:
                kwargs['representative_id'] = flat_id.representative_id.id
        if email:
            partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
            if not partner:
                partner = request.env['res.partner'].sudo().create({
                    'email': email,
                    'name': kwargs.get('tenant_name', False),
                    'lang': request.lang.code,
                })
            kwargs['tenant_id'] = partner.id

        return super(WebsiteForm, self)._handle_website_form(model_name, **kwargs)