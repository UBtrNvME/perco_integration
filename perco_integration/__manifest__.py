{
    'name'        : 'PERCo Integration',
    'version'     : '1',
    'summary'     : 'HTTP controllers for PERCo integration',
    'description' : 'Set of controllers for establishment of the connection between PERCo MySQL database and odoo web '
                    'server',
    'category'    : 'HTTP Controller',
    'author'      : 'UBtrNvME',
    'website'     : 'https://www.qzhub.com',
    'license'     : 'AGPL-3',
    'depends'     : ['hr_attendance'],
    'data'        : ['security/ir.model.access.csv',
                     'views/connector_view.xml',
                     'data/call_mysql_job.xml'],
    'demo'        : [],
    'installable' : True,
    'auto_install': False,
    'application' : False
}
