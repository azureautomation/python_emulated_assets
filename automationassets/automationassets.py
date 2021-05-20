""" Azure Automation assets module to be used with Azure Automation during offline development """
# ----------------------------------------------------------------------------------
#
# MIT License

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ----------------------------------------------------------------------------------

# Support for python3
try:
    dict.iteritems
except AttributeError:
    # Python 3
    def iteritems(d):
        return iter(d.items())
else:
    # Python 2
    def iteritems(d):
        return d.iteritems()

# Constant keys for extracing items from automation assets.
_KEY_NAME = "Name"
_KEY_VALUE = "Value"
_KEY_USERNAME = "Username"
_KEY_PASSWORD = "Password"
_KEY_CERTPATH = "CertPath"
_KEY_CONNECTION_FIELDS = "ValueFields"

# Assets supported in Azure automation within python scripts
_KEY_VARIABLE = "Variable"
_KEY_CERTIFICATE = "Certificate"
_KEY_CREDENTIAL = "Credential"
_KEY_CONNECTION = "Connection"

# Get Azure Automation asset json file
def _get_automation_asset_file():
    import os
    if os.environ.get('AUTOMATION_ASSET_FILE') is not None:
        return os.environ.get('AUTOMATION_ASSET_FILE')
    return os.path.join(os.path.dirname(__file__), "localassets.json")

# Helper function to find an asset of a specific type and name in the asset file
def _get_asset_value(asset_file, asset_type, asset_name):
    import json
    json_data = open(asset_file)
    json_string = json_data.read()
    local_assets = json.loads(json_string)

    return_value = None
    for asset, asset_values in iteritems(local_assets):
        if asset == asset_type:
            for value in asset_values:
                if value[_KEY_NAME] == asset_name:
                    return_value = value
                    break
        if return_value != None:
            # Found the value so break out of loop
            break

    return return_value

# Returns an asset from the asses file
def _get_asset(asset_type, asset_name):
    local_assets_file = _get_automation_asset_file()

    # Look in assets file for value
    return_value = _get_asset_value(local_assets_file, asset_type, asset_name)

    if return_value is None:
        raise LookupError("asset:" + asset_name + " not found")
    return return_value

# Helper function to set an asset of a specific type and name in the assetFile
def _set_asset_value(asset_file, asset_type, asset_name, asset_value):
    import json
    json_data = open(asset_file)
    json_string = json_data.read()
    local_assets = json.loads(json_string)
    item_found = False

    for asset, asset_values in iteritems(local_assets):
        if asset == asset_type:
            for value in asset_values:
                if value[_KEY_NAME] == asset_name:
                    value[_KEY_VALUE] = asset_value
                    with open(asset_file, 'w') as asset_file_content:
                        asset_file_content.write(json.dumps(local_assets, indent=4))
                        item_found = True
                        break

        if item_found:
            break

    return item_found

# Updates an asset in the assets file
def _set_asset(asset_type, asset_name, asset_value):
    local_assets_file = _get_automation_asset_file()
    # Check assets file for value.
    item_found = _set_asset_value(local_assets_file,
                                  asset_type, asset_name, asset_value)

    if item_found is False:
        raise LookupError("asset:" + asset_name + " not found")

# Below are the 5 supported calls that can be made to automation assets from within
# a python script
def get_automation_variable(name):
    """ Returns an automation variable """
    variable = _get_asset(_KEY_VARIABLE, name)
    return variable[_KEY_VALUE]


def set_automation_variable(name, value):
    """ Sets an automation variable """
    _set_asset(_KEY_VARIABLE, name, value)


def get_automation_credential(name):
    """ Returns an automation credential as a dictionay with username and password as keys """
    credential = _get_asset(_KEY_CREDENTIAL, name)

    # Return a dictionary of the credential asset
    credential_dictionary = {}
    credential_dictionary['username'] = credential['Username']
    credential_dictionary['password'] = credential['Password']
    return credential_dictionary


def get_automation_connection(name):
    """ Returns an automation connection dictionary """
    connection = _get_asset(_KEY_CONNECTION, name)
    return connection[_KEY_CONNECTION_FIELDS]


def get_automation_certificate(name):
    """ Returns an automation certificate in PKCS12 bytes """
    from OpenSSL import crypto
    certificate = _get_asset(_KEY_CERTIFICATE, name)
    pks12_cert = crypto.load_pkcs12(open(certificate[_KEY_CERTPATH], 'rb').read(),
                                    certificate[_KEY_PASSWORD])
    return crypto.PKCS12.export(pks12_cert)
