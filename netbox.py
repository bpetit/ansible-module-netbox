#!/usr/bin/python3

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
            if "already exists" in res['name'][0] or "already exists" in res['slug'][0]:
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
