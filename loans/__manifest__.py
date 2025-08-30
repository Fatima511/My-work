{
    'name': 'Loan Management',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Employees',
    'summary': """Complete loan Management""",
    'description': 'This module is very useful to manage all process of loan'
                   ,
    'author': 'Fatima',
    'depends': ['hr'],
    'data': [
        'security/loan_management_groups.xml',
        'security/loan_management_record.xml',
         'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/loan_document_view.xml',
        'views/loan_request_view.xml',
        'views/loan_type_view.xml',
        'views/prepayment_line_view.xml',
        'views/res_config_settings.xml',
        'wizard/reject_loan_view.xml',


    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
