from odoo import api, Command, fields, models, _

class LoanDocument(models.Model):
    _name = 'loan.document'
    _description = "Loan Document"
    _rec_name = "document_name"

    document_name = fields.Char(string='Proofs', required=True)
    company_id = fields.Many2one('res.company',string='Company', readonly=True, default=lambda self: self.env.company)

    _sql_constraints = [
        ('name_uniq', 'unique (document_name)', "Document name already exists!"),
    ]
