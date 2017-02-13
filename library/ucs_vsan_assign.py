#!/usr/bin/python

from ucsmsdk.mometa.fabric.FabricFcVsanPortEp import FabricFcVsanPortEp


DOCUMENTATION = '''
---
module: ucs_vsan_assign
short_description: Assign FC Ports to a VSAN
author:  "Kyle Jones (@excilsploft)"
version_added: "<version_tag>"
description:
    - Assign FC ports to a VSAN
notes:
    - VSAN and Unified (ie FC ports) must already be configured
requirements:
    - "python >= 2.7.5"
    - "ucsmsdk"
options:
    vsan_id:
      description:
        - "A UCS VSAN ID"
      required: true
      default: None
    switch_id:
      description:
        - "A UCS Fabric Interconnect (A or B)"
      required: true
    ports:
      description:
        - "a list of unified FC ports in module/port notation (ie 1/16, 3/5, etc)"
      required: true
      default: None
'''

EXAMPLES = '''
# Create lan conn policy exchange server on dev ucs
- ucs_vsan_assign:
    hostname: dev_ucsm_hostname
    username: admin
    password: admin
    port: 443
    secure: true
    vsan_id: 1020
    switch_id: A
    ports:
      - 4/13
      - 4/14
      - 4/15
      - 4/16
'''


def get_vsan(handle, vsan_id, switch_id):
    """ Get The vsan object """

    #filter_str = '(id, "{0}", type="eq")'.format(vsan_id)
    vsan_dn = "fabric/san/{0}/net-{1}".format(switch_id, vsan_id)
    vsan_obj = handle.query_dn(vsan_dn)
    return vsan_obj

def assign_ports(handle,  params):
    """ assign the ports to the vsan """

    vsan_id = params['vsan_id']
    switch_id = params['switch_id']

    vsan_obj = get_vsan(handle, vsan_id, switch_id)

    if vsan_obj:
        for port in params['ports']:
            slot_id, port_id = port.split('/')
            port_ep = FabricFcVsanPortEp(parent_mo_or_dn=vsan_obj,
                                         name="",
                                         auto_negotiate='yes',
                                         switch_id=switch_id,
                                         slot_id=slot_id,
                                         admin_state='enabled',
                                         port_id=port_id)
            handle.add_mo(port_ep, True)

        handle.commit()
        return True
    else:
        return False



def main():
    """main entry point"""

    spec = get_ucs_argument_spec(**dict(
        vsan_id=dict(
            required=True,
            type="str"
        ),
        switch_id=dict(
            required=True,
            type="str"
        ),
        ports=dict(
            type="list"
        ),
    ))


    module = AnsibleModule(argument_spec=spec)

    handle = get_handle(module)

    result = assign_ports(handle, module.params)

    module.exit_json(changed=result)


from ansible.module_utils.basic import *
from ucs import *

if __name__ == '__main__':
    main()


