#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from netboxapi_client.netboxapi_client import Api, get_list, get
import json

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}

DOCUMENTATION = '''
---
# If a key doesn't apply to your module (ex: choices, default, or
# aliases) you can use the word 'null', or an empty list, [], where
# appropriate.
#
# See http://docs.ansible.com/ansible/dev_guide/developing_modules_documenting.html for more information
#
module: netbox_facts
short_description: Queries netbox api and stores result as ansible facts
description:
    - This is to be used with netbox (https://github.com/digitalocean/netbox)
    - Permits to get data stored in netbox as ansible facts.
	- Useful to use those data as variables in your playbooks.
version_added: "2.4"
author: "Benoit Petit (@bpetit)"
options:
# One or more of the following
	url:
		description:
			- URL of the target Netbox instance
			- In the form: http://mynetbox.example.org or https://mynetbox.example.org
		required: true
		default: null
	token:
		description:
			- Token used to permit requests to netbox API
			- This is a string
			- You can generate one by getting on a netbox user profile page
		required: true
		default: null
	model:
		description:
			- Defines which "category" of objects you want to edit
		choices:
			- dcim
			- ipam
			- circuits
			- secrets
			- tenancy
			- extras
		required: true
		default: null
	obj:
		description:
			- Defines which kind of object you want to edit
			- Choices depend on the choosed model. Here is the available options:
			- http://netbox.readthedocs.io/en/latest/data-model/dcim/
			- http://netbox.readthedocs.io/en/latest/data-model/circuits/
			- http://netbox.readthedocs.io/en/latest/data-model/ipam/
			- http://netbox.readthedocs.io/en/latest/data-model/secrets/
			- http://netbox.readthedocs.io/en/latest/data-model/tenancy/
			- http://netbox.readthedocs.io/en/latest/data-model/extras/
		required: true
		default: null
	name:
		description:
			- Name of the object you want to get informations from
			- You should provide either this parameter or ident
		required: false
		default: null	
	ident:
		description:
			- Numerical identifier of the object you want to get informations from.
			- You should provide either this parameter of name.
		required: false
		default: null
notes:
	- To use this module locally, use connection: local
    - This module is handy to use with netbox module
requirements:
    - netboxapi_client >= 0.1
'''

EXAMPLES = '''
    - name: get data from device sw-02-par-eq3
      netbox_facts:
        url: 'http:/netbox.example.org/'
        token: 'OhshohghaiCiezuaha8quiech6quie2thu3fee5eb2zeKai1ie'
        model: 'dcim'
        obj: 'devices'
        name: 'sw-02-par-eq3'
    - debug: var=netbox_result
    - name: get the list of ip subnet aggregates stored in netbox
      netbox_facts:
        url: 'http:/netbox.example.org/'
        token: 'OhshohghaiCiezuaha8quiech6quie2thu3fee5eb2zeKai1ie'
        model: 'ipam'
        obj: 'aggregates'
    - debug: var=netbox_result
'''

def main():
    module = AnsibleModule(
        argument_spec = dict(
            name      = dict(required=False),
            ident     = dict(required=False),
            model     = dict(required=True),
            obj       = dict(required=True),
            token     = dict(required=True),
            url       = dict(required=True)
        ),
        # supports_check_mode=True,
        mutually_exclusive = [ ('name', 'ident') ]
    )

    # we initialize the Api object
    api = Api(
        url=module.params['url'],
        token=module.params['token']
    )

    ansible_facts = dict()

    # if no name or id is specified, we enumerate objects
    if not module.params['name'] and not module.params['ident']:
        res = get_list(api, model=module.params['model'], obj=module.params['obj'])
        ansible_facts['netbox_result'] = res

    if module.params['name'] and not module.params['ident']:
        res = get(api, model=module.params['model'], obj=module.params['obj'], name=module.params['name'])
        ansible_facts['netbox_result'] = res

    if not module.params['name'] and module.params['ident']:
        res = get(api, model=module.params['model'], obj=module.params['obj'], ident=module.params['ident'])
        ansible_facts['netbox_result'] = res

    module.exit_json(changed=False, result=res, ansible_facts=ansible_facts)

if __name__ == '__main__':
    main()
