from odoo import models, fields, api

class RejectLoanWizard(models.TransientModel):
    _name = 'reject.loan.wizard'
    _description = 'Reject Loan Wizard'

    reject_reason = fields.Text(string="Reject Reason", required=True)

    def action_reject_loan(self):
        loan_id = self.env.context.get('active_id')
        loan = self.env['loan.request'].browse(loan_id)
        loan.write({
            'state': 'rejected',
            'rejection_reason': self.reject_reason,
        })
