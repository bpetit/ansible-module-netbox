#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from netboxapi_client import Api, get_list, get
import json

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

    module.exit_json(changed=True, result=res, ansible_facts=ansible_facts)

if __name__ == '__main__':
    main()
