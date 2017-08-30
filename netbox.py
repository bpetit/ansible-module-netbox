#!/usr/bin/python3

from ansible.module_utils.basic import AnsibleModule
from netboxapi_client import Api, create, get, update
from pprint import pprint
from jinja2 import Environment, meta, FileSystemLoader
import json
from os import path

def json_are_the_same(first, second):
    for k, v in first.items():
        if k not in second:
            return False
        else:
            if v is not dict:
                if not v == second[k]:
                    return False
                return True
            else:
                json_are_the_same(first[k], second[k])

def main():
    module = AnsibleModule(
        argument_spec = dict(
            name      = dict(required=False),
            ident     = dict(required=False),
            model     = dict(required=True),
            obj       = dict(required=True),
            token     = dict(required=True),
            url       = dict(required=True),
            state     = dict(required=True),
            template  = dict(required=True)
        ),
        # supports_check_mode=True,
        mutually_exclusive = [ ('name', 'ident') ]
    )

    api = Api(
        url=module.params['url'],
        token=module.params['token']
    )

    res = {}

    # state = present
    if module.params['state'] == 'present' and 'template' in module.params:
        # get current object
        current = get(api, model=module.params['model'], obj=module.params['obj'], ident=module.params['ident'], name=module.params['name'])
        # get the data from the template
        template = module.params['template']
        env = Environment(
            loader=FileSystemLoader(path.dirname(template))
        )
        template = env.get_template(path.basename(template))
        data = json.loads(template.render().replace("'", "\""))
        res = data
        # if current object data and required object data are the same
        if json_are_the_same(current, res):
            module.exit_json(changed=False, result=res, ansible_facts=res)
        # if not
        else:
            if 'detail' in current and current['detail'] == 'Not found.':
                res = create(api, model=module.params['model'], obj=module.params['obj'], name=module.params['name'], ident=module.params['ident'], data=data)
            else:
                res = update(api, model=module.params['model'], obj=module.params['obj'], name=module.params['name'], ident=module.params['ident'], data=data)
        result = res.json()
    module.exit_json(changed=True, result=result)

if __name__ == '__main__':
    main()
