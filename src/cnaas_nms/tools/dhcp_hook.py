#!/usr/bin/env python3

import sys

from cnaas_nms.cmdb.device import Device, DeviceState
from cnaas_nms.cmdb.session import session_scope
import cnaas_nms.cmdb.helper

if len(sys.argv) < 2:
    sys.exit(1)
if sys.argv[1] == "commit":
    try:
        ztp_mac = cnaas_nms.cmdb.helper.canonical_mac(sys.argv[2])
        dhcp_ip = sys.argv[3]
    except Exception as e:
        print(str(e))
        sys.exit(2)
    with session_scope() as session:
        db_entry = session.query(Device).filter(Device.ztp_mac==ztp_mac).first()
        if not db_entry:
            new_device = Device()
            new_device.ztp_mac = ztp_mac
            new_device.hostname = ztp_mac
            new_device.state = DeviceState.PRE_CONFIGURED 
            session.add(new_device)
        #TODO: if entry exists, update state depending on previous state?