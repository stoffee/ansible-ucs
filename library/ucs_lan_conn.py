#!/usr/bin/python

from ucsmsdk.ucsconstants import NamingId
from ucsmsdk.mometa.vnic.VnicEther import VnicEther
from ucsmsdk.mometa.vnic.VnicLanConnPolicy import VnicLanConnPolicy

DOCUMENTATION = '''
---
module: ucs_lan_con
short_description: Create and Delete ucs lan_conn_policy
author:  "Kyle Jones (@excilsploft)"
version_added: "<version_tag>"
description:
    - Create UCS lan_conn_policy in a UCS version 2.2X and greater. This module,
      allows you to create a policy, assign a vnic based on a template, name it,
      order it and Assign a vnic policy.
notes:
    - This only works with existing vnic templates and vnic policies.
requirements:
    - "python >= 2.7.5"
    - "ucsmsdk"
options:
    lan_con_name:
      description:
        - "A UCS lan connection policy name"
      required: true
      default: None
    lan_con_descr:
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
    vnics:
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
# Create lan conn policy exchange server on dev ucs
- ucs_lan_con:
    state: present
    hostname: dev_ucsm_hostname
    username: admin
    password: admin
    port: 443
    secure: true
    org_name: myorgname
    lan_con_name: exchange
    lan_con_descr: exchange server lan con policy
    vnics:
      - name: nic1
        order: 1
        templ: exchange_a
        policy: Windows

      - name: nic2
        order: 2
        templ: exchange_b
        policy: Windows
'''

def get_vcon(handle, org_obj, name):
    """verify the vcon exists"""

    ret_val = None
    filter_str = '(name, "{0}", type="eq")'.format(name)
    vcon_list = handle.query_children(in_mo=org_obj,
                                      class_id=NamingId.VNIC_LAN_CONN_POLICY,
                                      filter_str=filter_str,
                                      hierarchy=False)
    for vcon in vcon_list:
        if vcon.name == name:
            ret_val = vcon
            break

    return ret_val


def vcon_present(handle, params):
    """make the vcon"""

    org_obj = get_org(handle, params['org_name'])

    if org_obj:

        vnic_pol = VnicLanConnPolicy(parent_mo_or_dn=org_obj,
                                     name=params['lan_con_name'],
                                     descr=params['lan_con_descr'])

        for vnic in params['vnics']:
            vnic = VnicEther(parent_mo_or_dn=vnic_pol,
                             name=vnic['name'],
                             order=str(vnic['order']),
                             nw_templ_name=vnic['templ'],
                             adaptor_profile_name=vnic['policy'])

        handle.add_mo(vnic_pol, True)
        handle.commit()

        if get_vcon(handle, org_obj, params['lan_con_name']):
            #return ({'changed': True, 'failed': False})
            return True
    else:
        #return ({'changed': False, 'failed': True})
        return False


def vcon_absent(handle, params):
    """remove the vcon"""

    org_obj = get_org(handle, params['org_name'])

    if org_obj:
        filter_str = '(name, "{0}", type="eq")'.format(params['lan_con_name'])
        vcon_list = handle.query_children(in_mo=org_obj,
                                          class_id=NamingId.VNIC_LAN_CONN_POLICY,
                                          filter_str=filter_str,
                                          hierarchy=False)
        for vcon in vcon_list:
            if vcon.name == params['lan_con_name']:
                handle.remove_mo(vcon)
                handle.commit()
                break

    if get_vcon(handle, org_obj, params['lan_con_name']):
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
        lan_con_name=dict(
            required=True,
            type="str"
        ),
        lan_con_descr=dict(
            required=False,
            type="str"
        ),
        vnics=dict(
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
        result = vcon_present(handle, module.params)
    else:
        result = vcon_absent(handle, module.params)

    module.exit_json(changed=result)


from ansible.module_utils.basic import *
from ucs import *

if __name__ == '__main__':
    main()
