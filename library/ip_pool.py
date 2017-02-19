#!/usr/bin/python

from ucsmsdk.ucsconstants import NamingId
from ucsmsdk.mometa.ippool.IppoolPool import IppoolPool
from ucsmsdk.mometa.ippool.IppoolBlock import IppoolBlock

DOCUMENTATION = '''
---
module: ucs_ip_pool
short_description: Create and Delete ucs IP Pools
author:  "Chris Dunlap (@stoffee)"
version_added: "<version_tag>"
description:
    - Create UCS ip_pool in a UCS version 2.2X and greater. This module,
      allows you to create a IP Pool, add an IP Pool block to an existing IP Pool, 
notes:
    - 
requirements:
    - "python >= 2.7.5"
    - "ucsmsdk"
options:
    ip_pool_name:
      description:
        - "a UCS IP Pool name"
      required: true
      default: None
    ip_pool_descr:
      description:
        - "description label for the ip pool"
      required: false
      default: None
    state:
      description:
        - "a choice, either 'enabled' or 'disabled'"
    ip_v4_pool_block:
      description:
        - "IP Block of IPv4 address type"
      required: false
      default: None
    org_name:
      description:
        - "organizational object name to create the ip pool under"
        required: true
        default: None
'''

EXAMPLES = '''
# Create IP Pool Pool and Blocks ucs
- ucs_ip_pool:
    state: present
    hostname: dev_ucsm_hostname
    username: admin
    password: admin
    port: 443
    secure: true
    org_name: myorgname
    ip_pool_name: DC03
    ip_pool_descr: datacenter 03 ip pool
    ip_v4_pool_block: 
      - name: IPv4_DC_Exchange
        description: v4 IP Block for exchange server and domain controllers
        starting_address: 10.10.0.1
        number_of_ip: 100
        default_route: 10.10.0.1
	primary_dns: 10.10.0.10
	secondary_dns: 10.10.0.11

      - name: IPv4_Oracle
        description: v4 IP Block for Oracle
        starting_address: 10.10.1.1
        number_of_ip: 200
        default_route: 10.10.1.1
	primary_dns: 10.10.1.10
	secondary_dns: 10.10.1.11
'''

##### Start-Of-PythonScript #####
## Adding IP Pool and v4 IP Block
#mo = IppoolPool(parent_mo_or_dn="org-root", is_net_bios_enabled="disabled", name="Booger", descr="", policy_owner="local", ext_managed="internal", supports_dhcp="disabled", assignment_order="sequential")
#mo_1 = IppoolBlock(parent_mo_or_dn=mo, to="10.10.0.100", r_from="10.10.0.1", def_gw="10.10.0.1", prim_dns="10.10.0.250")
#handle.add_mo(mo)
#handle.commit()
##### End-Of-PythonScript #####

##### Start-Of-PythonScript #####
## delete named IP Pool Pool
#mo = handle.query_dn("org-root/ip-pool-Bogus")
#handle.remove_mo(mo)
#handle.commit()
##### End-Of-PythonScript #####

##### Start-Of-PythonScript #####
### delete a IP Pool Block
#mo = handle.query_dn("org-root/ip-pool-Booger/block-10.10.0.1-10.10.0.100")
#handle.remove_mo(mo)
#handle.commit()
##### End-Of-PythonScript #####


##random code from devnet for #inspriation ##
#Create IP Pool
#mo = IppoolPool(parent_mo_or_dn=my_Full_Path_Org, is_net_bios_enabled="disabled", name="ext_mgmt", descr="KVM", policy_owner="local", ext_managed="internal", supports_dhcp="disabled", assignment_order="sequential")
#mo_1 = IppoolBlock(parent_mo_or_dn=mo, prim_dns=my_Primary_DNS, r_from=my_kvm_pool_first, def_gw=my_KVM_Gateway, sec_dns=my_Secondary_DNS, to=my_kvm_last_addr)
#handle.add_mo(mo)
#handle.commit()


def get_ip_pool(handle, org_obj, name):
    """verify if ip pool already exists"""

    ret_val = None
    filter_str = '(name, "{0}", type="eq")'.format(name)
    ip_pool_list = handle.query_children(in_mo=org_obj,
                                      class_id=NamingId.IppoolPool,
                                      filter_str=filter_str,
                                      hierarchy=False)
    for ip_pool in ip_pool_list:
        if ip_pool.name == name:
            ret_val = ip_pool
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
        ip_pool_name=dict(
            required=True,
            type="str"
        ),
        ip_pool_descr=dict(
            required=False,
            type="str"
        ),
        ip_v4_pool_block=dict(
            required=False,
            type="str"
        ),
        current_ip_pools=dict(
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
