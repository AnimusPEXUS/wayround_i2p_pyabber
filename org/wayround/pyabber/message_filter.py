

def is_message_acceptable(
    operation_mode,
    contact_bare_jid, contact_resource,
    active_bare_jid, active_resource
    ):

    if not operation_mode in ['chat', 'groupchat', 'private']:
        raise ValueError(
            "`operation_mode' must be in ['chat', 'groupchat', 'private']"
            )

    ret = False

    jid_resource = None
    if operation_mode == 'private':
        jid_resource = contact_resource

    if (contact_bare_jid == active_bare_jid and
        (jid_resource == None
         or (jid_resource != None
             and jid_resource == active_resource))
        ):
        ret = True

    return ret


def gen_get_history_records_parameters(
    operation_mode,
    contact_bare_jid, contact_resource
    ):

    if not operation_mode in ['chat', 'groupchat', 'private']:
        raise ValueError(
            "`operation_mode' must be in ['chat', 'groupchat', 'private']"
            )

    jid_resource = None
    if operation_mode == 'private':
        jid_resource = contact_resource

    types_to_load = ['message_chat']
    if operation_mode == 'groupchat':
        types_to_load = ['message_groupchat']

    return jid_resource, types_to_load
