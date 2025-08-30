from odoo import fields, models
class ResCompany(models.Model):
    _inherit='res.company'

    secondary_amount = fields.Monetary( string="Secondary Double Validation Amount", default=10000,help="Minimum amount for which a double validation is required")
    # Automatic Default Terms & Conditions in Purchase Orders
    default_terms = fields.Html('Default Terms', translate=True)
