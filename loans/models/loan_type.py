from odoo import api, Command, fields, models, _

class LoanType(models.Model):
    _name = 'loan.type'

    name = fields.Char('Name', required=True)
    amount = fields.Integer('Loan Amount', required=True)
    tenure = fields.Integer(
    string="Tenure in Months",
    default=1,
    help="Amortization period, usually in months or years depending on configuration.")
    processing_fees= fields.Integer('Processing Fee')
    disbursal_amount = fields.Float(string='Disbursal Amount',help="Net amount disbursed to the customer after deducting processing fee.",
                                   compute='_compute_disbursal_amount', store=True)
    document_ids = fields.Many2many('loan.document')
    criteria = fields.Text('Approving Criteria')
    company_id = fields.Many2one('res.company',string='Company', default=lambda self: self.env.company)

    @api.depends('amount','processing_fees')
    def _compute_disbursal_amount(self):
        for type in self:
            type.disbursal_amount = type.amount - type.processing_fees

