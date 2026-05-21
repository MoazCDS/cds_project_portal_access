# -*- coding: utf-8 -*-
{
    'name': "CDS Project Portal Access",
    'summary': """
    """,
    'description': """
    """,
    'author': "CDS Solutions SRL",
    'website': "https://www.cdsegypt.com",
    'contributors': [
        'Ramadan Khalil <rkhalil1990@gmail.com>',
        'Moaz Elbahr',
    ],
    'version': '0.1',
    'depends': ['base', 'mail', 'project'],
    'data': [
        'security/cds_project_portal_access_security.xml',
        'views/portal_templates.xml',
    ],
    'assets': {},
    "pre_init_hook": None,
    "post_init_hook": None,
    'license': 'OPL-1',
}