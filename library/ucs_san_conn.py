#!/usr/bin/python

from ucsmsdk.ucsconstants import NamingId
from ucsmsdk.mometa.vnic.VnicFc import VnicFc
from ucsmsdk.mometa.vnic.VnicSanConnPolicy import VnicSanConnPolicy
from ucsmsdk.mometa.vnic.VnicFcNode import VnicFcNode

DOCUMENTATION = '''
---
module: ucs_san_con
short_description: Create and Delete ucs lan_conn_policy
author:  "Kyle Jones (@excilsploft)"
version_added: "<version_tag>"
description:
    - Create UCS san_conn_policy in a UCS version 2.2X and greater. This module,
      allows you to create a policy, assign an hba based on a template, name it,
      order it and Assign a vnic policy.
notes:
    - This only works with existing hba templates and vnic policies.
requirements:
    - "python >= 2.7.5"
    - "ucsmsdk"
options:
    san_con_name:
      description:
        - "A UCS san connection policy name"
      required: true
      default: None
    san_con_descr:
      description:
        - "description label for the policy"
      required: false
      default: None
    state:
      description:
        - "a choice, either 'present' or 'absent'"
    org_name:
      description:
        - "organizational object name to create the policy under"
        required: true
        default: None
    wwnn_pool: "world wide node name pool"
    hbas:
      description:
         - "a list of vnic dictionaries examples as below
           name: vnic name
           order: order in policy
           templ: vnic template
           policy: policy name for the vnic"

      required: true
      default: None
'''

EXAMPLES = '''
# Create a san conn policy exchange server on dev ucs
- ucs_san_conn:
    state: present
    hostname: dev_ucsm_hostname
    username: admin
    password: admin
    port: 443
    org_name: myorgname
    san_con_name: exchange
    san_con_descr: exchange server san con policy
    wwnn_pool: exchange_fc_pool
    hbas:
      - name: hba1
        order: 1
        templ: exchange_a
        policy: Windows

      - name: hba2
        order: 2
        templ: exchange_b
        policy: Windows
'''


def get_san_con(handle, org_obj, name):
    """verify the san conn policy exists"""

    ret_val = None
    filter_str = '(name, "{0}", type="eq")'.format(name)
    san_con_list = handle.query_children(in_mo=org_obj,
                                         class_id=NamingId.VNIC_SAN_CONN_POLICY,
                                         filter_str=filter_str,
                                         hierarchy=False)
    for san in san_con_list:
        if san.name == name:
            ret_val = san
            break

    return ret_val

def san_con_present(handle, params):
    """make the san con policy """

    org_obj = get_org(handle, params['org_name'])

    if org_obj:
        san_con_pol = VnicSanConnPolicy(parent_mo_or_dn=org_obj,
                                        name=params['san_con_name'],
                                        descr=params['san_con_descr'])

        fc_node = VnicFcNode(parent_mo_or_dn=san_con_pol,
                             ident_pool_name=params['wwnn_pool'])
        for hba in params['hbas']:
            hba_obj = VnicFc(parent_mo_or_dn=san_con_pol,
                             name=hba['name'],
                             order=str(hba['order']),
                             nw_templ_name=hba['templ'],
                             adaptor_profile_name=hba['policy'])

        handle.add_mo(san_con_pol, True)
        handle.commit()

        if get_san_con(handle, org_obj, params['san_con_name']):
            #return ({'changed': True, 'failed': False})
            return True
    else:
        #return ({'changed': False, 'failed': True})
        return False

def san_con_absent(handle, params):
    """remove the san con policy"""

    org_obj = get_org(handle, params['org_name'])

    if org_obj:
        filter_str = '(name, "{0}", type="eq")'.format(params['san_con_name'])
        san_con_list = handle.query_children(in_mo=org_obj,
                                             class_id=NamingId.VNIC_SAN_CONN_POLICY,
                                             filter_str=filter_str,
                                             hierarchy=False)
        for s_con in san_con_list:
            if s_con.name == params['san_con_name']:
                handle.remove_mo(s_con)
                handle.commit()
                break

    if get_san_con(handle, org_obj, params['san_con_name']):
        #return ({'changed': True, 'failed': False})
        return True
    else:
        #return ({'changed': False, 'failed': True})
        return False

def main():
    """main entry point"""

    spec = get_ucs_argument_spec(**dict(
        org_name=dict(
            required=True,
            type="str"
        ),
        san_con_name=dict(
            required=True,
            type="str"
        ),
        san_con_descr=dict(
            required=False,
            type="str"
        ),
        wwnn_pool=dict(
            required=True,
            type="str"
        ),
        hbas=dict(
            type="list"
        ),
        state=dict(
            default="present",
            choices=["present", "absent"],
            type="str"
        ),
    ))


    module = AnsibleModule(argument_spec=spec)

    handle = get_handle(module)

    if module.params['state'] == 'present':
        result = san_con_present(handle, module.params)
    else:
        result = san_con_absent(handle, module.params)

    module.exit_json(changed=result)


from ansible.module_utils.basic import *
from ucs import *

if __name__ == '__main__':
    main()
