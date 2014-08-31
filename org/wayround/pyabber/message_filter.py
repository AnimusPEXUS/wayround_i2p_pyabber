

def is_message_acceptable(
    operation_mode,
    message_type,
    contact_bare_jid, contact_resource,
    active_bare_jid, active_resource
    ):

    if not operation_mode in ['normal', 'chat', 'groupchat', 'private']:
        raise ValueError(
            "`operation_mode' must be in"
            " ['normal', 'chat', 'groupchat', 'private']"
            )

    ret = False

    if operation_mode == 'chat':

        ret = (contact_bare_jid == active_bare_jid
               and message_type == 'message_chat')

    elif operation_mode == 'groupchat':

        ret = (contact_bare_jid == active_bare_jid
               and message_type == 'message_groupchat')

    elif operation_mode == 'private':

        ret = (contact_bare_jid == active_bare_jid
               and contact_resource == active_resource
               and message_type == 'message_chat')

    #    elif operation_mode == 'normal':
    #
    #        ret = (contact_bare_jid == active_bare_jid
    #               and contact_resource == active_resource
    #               and message_type == 'normal_chat')

    else:
        pass

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
