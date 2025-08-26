from datetime import timedelta
from odoo import api, fields, models, _
from datetime import datetime, timedelta

class TestBug(models.Model):
    """
    Test Bug Model
    This model represents a bug reported during testing. It tracks the bug's lifecycle,
    including its state, severity, priority, and related test cases or steps.
    """

    _name = "test.bug"
    _inherit = ['mail.thread.main.attachment', 'mail.thread', 'mail.activity.mixin']
    _order = 'ref desc'

    # ==========================
    # Fields
    # ==========================

    # Identification Fields
    ref = fields.Char(
        string='REF',
        copy=False,
        required=True,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('test.bug'),
        help="Unique reference number for the bug."
    )
    name = fields.Char(
        string="Summary",
        required=True,
        tracking=True,
        help="Short summary of the bug."
    )
    description = fields.Text(
        string="Bug Description",
        help="Detailed description of the bug."
    )
    environment = fields.Text(
        string="Environment",
        help="Environment where the bug was encountered."
    )

    # Date Fields
    due_date = fields.Date(
        string='Due Date',
        help="Expected date by which the bug should be resolved."
    )
    reported_date = fields.Datetime(
        string="Reported Date",
        default=fields.Datetime.now,
        help="Date and time when the bug was reported."
    )
    fix_start_date = fields.Datetime(
        string="Fix Start Date",
    )
    fix_end_date = fields.Datetime(
        string="Fix Start Date",
    )

    # Relational Fields
    test_case_id = fields.Many2one(
        'test.case',
        string="Test Case",
        help="Test case associated with this bug."
    )
    test_step_id = fields.Many2one(
        'test.case.steps',
        string="Test Step",
        ondelete='cascade',
        help="Test step where the bug was encountered."
    )
    dependency = fields.Many2one(
        'test.bug',
        string="Dependencies",
        help="Parent bug if this bug is a duplicate or related to another bug."
    )
    assignee_id = fields.Many2one(
        'res.users',
        string="Assigned Developer",
        help="Developer assigned to fix the bug."
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project",
        related="test_case_id.project_id",
        store=True,
        help="Project associated with the bug."
    )
    reported_by = fields.Many2one(
        'res.users',
        string="Reported By",
        default=lambda self: self.env.user,
        help="User who reported the bug."
    )
    fixed_by = fields.Many2one(
        'res.users',
        string="Fixed By",
        help="User who fixed the bug."
    )
    test_run_id = fields.Many2one(
        'test.run',
        string='Test Run',
        help="Test run during which the bug was encountered."
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Attachments",
        help="Files attached to the bug report."
    )
    component_id = fields.Many2one(
        'component',
        string='Component/Module',
        related='test_case_id.component_id',
        store=True,
        help="Component to which this bug belongs."
    )

    # Selection Fields
    severity = fields.Selection(
        selection=[
            ('low', 'Minor'),
            ('medium', 'Medium'),
            ('high', 'Major'),
            ('critical', 'Critical'),
            ('blocker', 'Blocker')
        ],
        string="Severity",
        default='medium',
        tracking=True,
        help="Severity level of the bug."
    )
    priority = fields.Selection(
        selection=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent')
        ],
        string="Priority",
        default='medium',
        tracking=True,
        help="Priority level of the bug."
    )
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('confirmed', 'Confirmed'),
            ('in_progress', 'In Progress'),
            ('fixed', 'Resolved'),
            ('retest', 'Retesting'),
            ('reject', 'Re-opened'),
            ('closed', 'Closed')
        ],
        string="State",
        default='new',
        tracking=True,
        help="Current state of the bug."
    )
    rejection_reason = fields.Text(string="Reopen Reason")
   
    active = fields.Boolean('Active', default=True)

    # ==========================
    # Methods
    # ==========================


    def write(self, vals):
        """
        Override the write method to handle assignment and reopening activities.
        """
        if 'assignee_id' in vals:
            self._schedule_assignment_activity(vals['assignee_id'])
        if 'rejection_reason' in vals:
            self._schedule_reopened_activity()
        return super(TestBug, self).write(vals)

    def unlink(self):
        """
        Override the unlink method to prevent deletion of bugs that are not in the 'draft' state.
        """
        for record in self:
            if record.state != 'draft':
                raise UserError(
                    _("You cannot delete a bug that is not in draft state. Please archive it instead.")
                )
        return super(TestBug, self).unlink()

    @api.onchange('test_case_id')
    def _onchange_test_case_id(self):
        """
        Update the project when the test case is changed.
        Apply a domain to restrict test cases to those in 'failed' or 'running' states.
        """
        if self.test_case_id:
            self.project_id = self.test_case_id.project_id
            return {'domain': {'test_case_id': ['|', ('state', '=', 'failed'), ('state', '=', 'running')]}}
        return {}

    @api.onchange('test_step_id')
    def _onchange_test_step_id(self):
        """
        Update the test case when the test step is changed.
        """
        if self.test_step_id:
            self.test_case_id = self.test_step_id.test_case_id

    # ==========================
    # State Transition Methods
    # ==========================

    def confirm(self):
        """
        Transition the bug to the 'Confirmed' state.
        """
        self.state = 'confirmed'

    def in_progress(self):
        """
        Transition the bug to the 'In Progress' state.
        """
        self.state = 'in_progress'
        self.fix_start_date = fields.Datetime.now()

    def fixed(self):
        """
        Transition the bug to the 'Fixed' state.
        Set the fixed by user and fixed date.
        """
        self.state = 'fixed'
        self.fixed_by = self.env.user
        self.fix_end_date = fields.Datetime.now()
        self._schedule_fixed_activity()

    def rejected(self):
        """
        Transition the bug to the 'Rejected' state.
        """
        self.state = 'reject'

    def closed(self):
        """
        Transition the bug to the 'Closed' state.
        """
        self.state = 'closed'
        self._schedule_closed_activity()

    def re_open(self):
        """
        Transition the bug to the 'confirmed' state.
        """
        self.state = 'confirmed'

    

    def action_open_reopen_wizard(self):
        """
        Open the wizard for reopening a bug.
        """
        return {
            'name': 'Reopen Bug',
            'type': 'ir.actions.act_window',
            'res_model': 'reopen.bug.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }

    # Helper Methods
    def _schedule_assignment_activity(self, assignee_id):
        """
        Schedule an activity when a bug is assigned to a developer.
        """
        self.activity_schedule(
            'test_management.mail_activity_assignment',
            user_id=assignee_id,
            summary=f'You have been assigned a new bug: {self.ref}'
        )

    def _schedule_reopened_activity(self):
        """
        Schedule an activity when a bug is reopened.
        """
        self.activity_schedule(
            'test_management.mail_activity_reopened',
            user_id=self.assignee_id.id,
            summary=f'{self.ref} Your bug have been reopened !!'
        )

    def _schedule_fixed_activity(self):
        """
        Schedule an activity when a bug is fixed.
        """
        try:
            # Ensure the method is called on a single record
            self.ensure_one()

            # Schedule the activity
            self.activity_schedule(
                'test_management.mail_activity_fixed',
                user_id=self.reported_by.id,
                summary=f'{self.ref} Your bug has been fixed!'
            )
        except Exception as e:
            _logger.error(f"Failed to schedule activity for bug {self.ref}: {e}")

    def _schedule_closed_activity(self):
        """
        Schedule an activity when a bug is closed.
        """
        self.activity_schedule(
            'test_management.mail_activity_assignment',
            user_id=self.assignee_id.id,
            summary=f'  {self.ref} Well done your bug have been closed!'
        )



