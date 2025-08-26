from odoo import models,fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    #adding  customer_id field
    customer_id = fields.Char('Customer ID', required=True)

    _sql_constraints = [
        ('uniq_name', 'unique(customer_id)', 'Customer ID field must be unique.')
    ]

