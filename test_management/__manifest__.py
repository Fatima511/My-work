{
    'name': 'Test Management',
    'version': '1.0',
    'summary': 'Module for managing software tests',
    'description': 'A module to manage software tests, test cases, and related tasks for QA Engineers and Software Developers.',
    'author': 'ApplyIT',
    'website': 'https://yourwebsite.com',
    'category': 'Quality Assurance',
    'depends': ['base','project'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/test_sequence.xml',
        'data/mail_activity_data.xml',

        'wizard/reopen_bug_view.xml',

        'views/project_view.xml',
        'views/component_view.xml',
        'views/test_case_view.xml',
        'views/test_run_view.xml',
        'views/test_bug.xml',
        'views/menu.xml',

    ],
    'installable': True,
    'application': True,
}
