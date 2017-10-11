#!/usr/bin/python
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}

DOCUMENTATION = '''
---
# If a key doesn't apply to your module (ex: choices, default, or
# aliases) you can use the word 'null', or an empty list, [], where
# appropriate.
#
# See http://docs.ansible.com/ansible/dev_guide/developing_modules_documenting.html for more information
#
module: netbox
short_description: Permits to create, update or delete objects in netbox ipam and dcim tool (https://github.com/digitalocean/netbox)
description:
    - 
    - You might include instructions.
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
	state:
		description:
			- If the object is present or absent
		choices:
			- present
			- absent
		required: true
		default: present
	name:
		description:
			- Name of the object
		required: true
		default: null
	template:
		description:
			- Path to a jinja2 template that provides data for the object
			- This is a quoted string like 'templates/myobject.j2'
		required: false
		default: null
	data:
		description:
			- Dictionnary set of data for the object
			- Has to exist if template is not here
			- Example:
			-	...
			-	model: dcim
			-	obj: sites
			-	data:
			-		name: 'testsite'
			-		slug: 'testsite'
			-		asn: 64542
			-	...
		required: false
		default: null
notes:
    - model, obj, data parameters and template content depends on the Netbox API
	- The description of those parameters may evolve with the API
requirements:
    - netboaxapi_client >= 0.1
'''

from ansible.module_utils.basic import AnsibleModule
from netboxapi_client import Api, create, get, update, delete
from pprint import pprint
from jinja2 import Environment, meta, FileSystemLoader
import json
from os import path

def json_are_the_same(first, second):
    res = False
    for k, v in first.items():
        if k not in second:
            return False
        else:
            if v is not dict:
                if not first[k] == second[k]:
                    return False
                res = True
            else:
                 json_are_the_same(first[k], second[k])
    return res

def missing_field(res):
    for k, v in res.items():
        if type(v) is list and 'is required' in v[0]:
            return True
    return False

def main():
    module = AnsibleModule(
        argument_spec = dict(
            name      = dict(required=False),
            ident     = dict(required=False),
            model     = dict(required=True),
            obj       = dict(required=True),
            token     = dict(required=True),
            url       = dict(required=True),
            state     = dict(required=True, choices=['present', 'absent']),
            template  = dict(required=False),
            data      = dict(required=False)
        ),
        # supports_check_mode=True,
        mutually_exclusive = [ ('name', 'ident') ]
    )

    api = Api(
        url=module.params['url'],
        token=module.params['token']
    )

    changed = False
    failed = False

    res = {}

    current = get(
      api, model=module.params['model'],
      obj=module.params['obj'],
      ident=module.params['ident'],
      name=module.params['name']
    )

    # state = present
    if module.params['state'] == 'present':
        if 'template' in module.params and module.params['template'] is not None:
            # get current object
            # get the data from the template
            template = module.params['template']
            env = Environment(
                loader=FileSystemLoader(path.dirname(template))
            )
            template = env.get_template(path.basename(template))
            data = json.loads(template.render().replace("'", "\""))
        elif 'data' in module.params:
            data = json.loads(module.params['data'].replace("'", "\""))

        # if current object data and required object data are the same
        if not json_are_the_same(data, current): #FIX
            if 'detail' in current and current['detail'] == 'Not found.':
                 res = create(api, model=module.params['model'], obj=module.params['obj'], name=module.params['name'], ident=module.params['ident'], data=data)
            else:
                 res = update(api, model=module.params['model'], obj=module.params['obj'], name=module.params['name'], ident=module.params['ident'], data=data)

            # if update failed because of already used slug or name
            if ('name' in res and "already exists" in res['name'][0]) or ('slug' in res and "already exists" in res['slug'][0]):
                changed=False
                failed=False
            elif 'non_field_errors' in res:
                changed=False
                failed=False
            elif missing_field(res):
                changed=False
                failed=True
            else:
                changed=True

            result = res
        else:
            result = "Nothing changed."
    elif module.params['state'] == 'absent':
        res = delete(api, model=module.params['model'], obj=module.params['obj'], name=module.params['name'], ident=module.params['ident'])
        result = res
    else:
        raise Exception

    module.exit_json(changed=changed, result=result, failed=failed)

if __name__ == '__main__':
    main()
