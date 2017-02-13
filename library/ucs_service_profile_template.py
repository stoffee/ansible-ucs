#!/usr/bin/python

DOCUMENTATION = '''
---
module: ucs_service_profile_template
short_description: Create and Delete ucs service profile template
author:  "Kyle Jones (@excilsploft)"
version_added: "<version_tag>"
description:
    - Create a UCS Service Profile Tempalte in a UCS version 2.2X and Greater.
      This module allows you to create a service profile template within an
      org
notes:
    - This only works with existing templates and policies.
requirements:
    - "python >= 2.7.5"
    - "ucsmsdk"
options:
    service_profile_name:
      description:
        - "A ucs Service Profile Template name"
      required: true
      default: None
    template_descr:
      description:
        - "description label for the template"
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
    uuid:
      description:
        - "uuid pool to derive from"
      required: true
      default: None
    bios_policy:
      description:
        - "bios policy to use in the template"
      required: true
      default: default
    boot_policy:
      description:
        - "boot policy to use in the template"
      required: true
      default: default
    firmware_policy:
      description:
        - "firmware policy to use in the template"
      required: true
      default: default
    disk_policy:
      description:
        - "local disk policy to use in the template"
      required: true
      default: default
    management_ip:
      desciption:
        - "management ip pool to use in the template"
      required: true
      default: None
    maintenance_policy:
      description:
        - "a maintenance policy to use in the template"
      required: true
      default: None
    kvm_policy:
       description:
         - "a kvm policy to use in the template"
       required: true
       default: None
    lan_con_policy:
       description:
         - "a lan connection policy to use"
       required: true
       default: None
    san_con_policy:
         - "a san connection policy to use"
       required: true
       default: None

'''

EXAMPLES = '''
# Create a esxi template under org HR
- ucs_service_profile_template
  state: present
  hostname: dev_ucsm_hostname
  username: admin
  password: admin
  port: 443
  secure: false
  org_name: HR
  service_profile_name: esxi
  template_descr: "esxi template for HR"
  uuid: hr_uuid
  bios_policy: hr_esxi
  boot_policy: esxi_boot
  firmware_policy: 31_2c
  disk_policy: no_disk
  management_ip: ext_mgmt
  maintenance_policy: user_ack
  kvm_policy: kvm_enabled
  lan_con_policy: esxi_hr_lan
  san_con_policy: esxi_hr_san
'''

def main():
    """main entry point"""

    spec = get_ucs_argument_spec(**dict(
        org_name=dict(
            required=True,
            type="str"
        ),
        service_profile_name=dict(
            required=True,
            type="str"
        ),
        template_descr=dict(
            required=False,
            type="str"
        ),
        uuid=dict(
            required=True,
            type="str"
        ),
        bios_policy=dict(
            required=True,
            type="str"
        ),
        boot_policy=dict(
            required=True,
            type="str"
        ),
        firmware_policy=dict(
            required=True,
            type="str"
        ),
        disk_policy=dict(
            required=True,
            type="str"
        ),
        management_ip=dict(
            required=True,
            type="str"
        ),
        maintenance_policy=dict(
            required=True,
            type="str"
        ),
        kvm_policy=dict(
            required=True,
            type="str"
        ),
        lan_con_policy=dict(
            required=True,
            type="str"
        ),
        san_con_policy=dict(
            required=True,
            type="str"
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
        result = sp_template_present(handle, module.params)
    else:
        result = sp_template_absent(handle, module.params)

    module.exit_json(changed=result)


from ansible.module_utils.basic import *
from ucs import *

if __name__ == '__main__':
    main()
