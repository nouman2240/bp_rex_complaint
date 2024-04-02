# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.tools import format_date

class RexComplaintTicket(models.Model):
    _name = 'rex.complaint.ticket'
    _description = 'Tenant Complaint Model'
    _order = 'complaint_number DESC'
    _rec_name = 'complaint_number'

    _inherit = ['mail.thread','mail.activity.mixin']

    # fields for din5008 report
    l10n_din5008_template_data = fields.Binary(compute='_compute_l10n_din5008_template_data')
    l10n_din5008_document_title = fields.Char(compute='_compute_l10n_din5008_document_title')

    def _compute_l10n_din5008_template_data(self):
        for record in self:
            record.l10n_din5008_template_data = data = []
            if record.tenant_name:
                data.append((_("Tenant Name"), record.tenant_name))
            if record.tenant_email:
                data.append((_("Tenant Email"), record.tenant_email))
            if record.flat_id:
                data.append((_("Address: "), record.flat_id.name+", "+record.building_id.name))
            if record.create_date:
                data.append((_("Date"), format_date(self.env, record.create_date)))


    def _compute_l10n_din5008_document_title(self):
        for record in self:
            record.l10n_din5008_document_title = _("Work Order")

    # main model fields for tenant complaints
    complaint_number = fields.Char(string='Complaint Number',
                                    copy=False, readonly=True, index=True)
    representative_id = fields.Many2one('res.partner',
                                        string="Assigned Representative",
                                        tracking=True)
    tenant_name = fields.Char()
    tenant_email = fields.Char()
    tenant_id = fields.Many2one('res.partner',string="Tenant Partner") # a partner object for tenant to easily organize tenants
    type_id = fields.Many2one('rex.complaint.type',string="Complaint Type")
    description = fields.Text(string="Description")
    action_plan = fields.Text(string="Action Plan",tracking=True)
    complaint_stage = fields.Selection([
        ('new', 'New'),
        ('in_review', 'In Review'),
        ('in_progress', 'In Progress'),
        ('solved', 'Solved'),
        ('dropped', 'Dropped')
        ], string='Stage', default='new',tracking=True)
    building_id = fields.Many2one('rex.building')
    flat_id = fields.Many2one('rex.flat')
    drop_reason = fields.Many2one('rex.drop.reason')


    def open_mail_compose(self):
        """
        opens mail compose view on button click in solved and dropped stage
        to email tenants notifying them the outcome of their complaint.
        """
        if self.complaint_stage in ['solved','dropped']:
            print("in condition",self.complaint_stage)
            template_id = self.env.ref('rex_complaint_mgmt.complaint_closed').id
            mail_template_id = self.env['mail.template'].browse(template_id).id
            print(mail_template_id,"mtid")
            compose_ctx = dict(
                default_composition_mode= 'mass_mail',
                default_model='rex.complaint.ticket',
                default_template_id=mail_template_id,
            )
            print(compose_ctx)
            return {
                'type': 'ir.actions.act_window',
                'name': _('Contact Tenant'),
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': compose_ctx,
            }

    def create(self, vals):
        """
        creates a seaquence for complaint number and sends confirmation email to tenant.
        assigns tenant and representative partner to followers list of the created record.
        """
        vals['complaint_number'] = self.env['ir.sequence'].next_by_code('rex.ticket.seq')
        res = super().create(vals)
        template_id = self.env.ref('rex_complaint_mgmt.complaint_received').id

        self.env['mail.template'].browse(template_id).send_mail(res.id, force_send=True)
        follower_ids = []
        if res.representative_id:
            follower_ids.append(res.representative_id.id)
        if res.tenant_id:
            follower_ids.append(res.tenant_id.id)
        if follower_ids:
            res.message_subscribe(partner_ids=follower_ids)
        return res

class RexComplaintType(models.Model):
    _name = 'rex.complaint.type'
    _description = 'Tenant Complaint Type'
    _rec_name = 'name'

    name = fields.Char()

class RexBuilding(models.Model):
    _name = 'rex.building'
    _description = 'Tenant Building Address'
    _rec_name = 'name'
    
    @api.depends('building_name','postal_code','building_city')
    def _complete_address(self):
        """
        Appends the complete building address to name so tenants can easily find their
        building address in website form.
        """
        for rec in self:
            if rec.building_name and rec.building_city and rec.postal_code:
                rec.name = rec.building_name +", "+rec.postal_code+", "+rec.building_city
            else:
                rec.name = ''

    name = fields.Char(string="Building Address", compute="_complete_address", store=True)
    building_name = fields.Char(String="Building Name",required=True)
    building_city = fields.Char(string="City",required=True)
    postal_code = fields.Char(string='Postal Code', size=5, required=True)
    available_in_form = fields.Boolean(default=True)

class RexFlat(models.Model):
    _name = 'rex.flat'
    _description = 'Tenant Flat No'
    _rec_name = 'name'

    name = fields.Char()
    building_id = fields.Many2one('rex.building')
    representative_id = fields.Many2one('res.partner')
    available_in_form = fields.Boolean(default=True)

class RexDropReason(models.Model):
    _name = 'rex.drop.reason'
    _description = 'Reason to drop complaint'

    name = fields.Char('name')
    