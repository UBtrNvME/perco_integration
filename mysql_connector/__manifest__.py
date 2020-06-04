{
    'name'        : 'SQL Connector',
    'version'     : '1.0',
    'summary'     : 'SQL connector',
    'description' : """The abstract model which allows connection to the SQL database, and introduces mechanics of the
                    queries""",
    'category'    : 'Connecter',
    'author'      : 'UBtrNvME',
    'website'     : 'https://qzhub.com',
    'license'     : 'AGPL-3',
    'depends'     : ["hr_attendance"],
    'data'        : ["security/ir.model.access.csv",
                     "views/connector_view.xml"],
    'demo'        : [],
    'installable' : True,
    'auto_install': False
}
