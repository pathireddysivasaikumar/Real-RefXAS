"""
Example SciCat authentication configuration.

Copy this file to _auth_constants.py locally and replace the
placeholder values with runtime/local credentials.
Do not commit the real _auth_constants.py.
"""

import scicat_py

USERNAME = "admin"
PASSWORD = "CHANGE_ME_SCICAT_PASSWORD"

CONFIGURATION = scicat_py.Configuration(
    host="http://scicat:3000",
)
