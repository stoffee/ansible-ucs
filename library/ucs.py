"""This is a utility module to hand off a ucs handle to calling ansible
   modules"""

import os
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.ucsconstants import NamingId

HANDLE_LIST = []

def get_handle(module):
    """get a handle by parsing the modules params, if the handle is already
       open, then give the caller that handle, else try and open a new one
       let the module handle any login failures"""

    ucsm = module.params['hostname']
    ucs_user = module.params['username']
    ucs_password = module.params['password']
    port = module.params['port']
    secure = module.params['secure']

    for handle in HANDLE_LIST:
        if handle.ip == ucsm or handle.name == ucsm:
            return handle

    handle = UcsHandle(ucsm, ucs_user, ucs_password, secure=bool(secure),
                       port=port)

    try:
        handle.login()
        HANDLE_LIST.append(handle)
    except Exception as handle_exception:
        module.fail_json(msg=handle_exception)

    return handle

def get_ucs_argument_spec(**kwargs):
    """Get the base argument spec for connecting to ucsm"""

    ucsm_ip = os.environ.get("UCSM_IP", "localhost")
    ucsm_user = os.environ.get("UCSM_USER", "admin")
    ucsm_password = os.environ.get("UCSM_PASSWORD", "password")
    ucsm_port = os.environ.get("UCSM_PORT", 443)
    ucsm_secure = os.environ.get("UCSM_SECURE", "true")


    spec = dict(
        hostname=dict(
            type="str",
            default=ucsm_ip
        ),
        username=dict(
            type="str",
            default=ucsm_user
        ),
        password=dict(
            type="str",
            default=ucsm_password
        ),
        port=dict(
            required=False,
            type="int",
            default=ucsm_port
        ),
        secure=dict(
            required=False,
            type="bool",
            default=ucsm_secure
        ),
    )

    spec.update(kwargs)
    return spec

def get_org(handle, org_name):
    """check if the org exists and return it if does"""

    ret_val = None
    filt_str = '(name , "{0}", type="eq")'.format(org_name)
    org_list = handle.query_classid(NamingId.ORG_ORG, filter_str=filt_str)
    for org in org_list:
        if org.name == org_name:
            ret_val = org

    return ret_val
