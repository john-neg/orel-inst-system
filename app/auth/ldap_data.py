from ldap3 import Server, Connection
from ldap3.core.exceptions import LDAPBindError

from config import FlaskConfig


def get_user_data(username: str, password: str) -> tuple[str, list]:
    """Получение данных пользователя от LDAP сервера."""

    server = Server(FlaskConfig.AD_SERVER, connect_timeout=5, get_info='ALL')
    search_parameters = {
        'search_base': FlaskConfig.AD_SEARCH_TREE,
        'search_filter': f'(sAMAccountName={username})',
        'attributes': ['cn', 'memberOf'],
    }
    name, groups = '', []
    try:
        conn = Connection(
            server,
            user=f"{username}@{FlaskConfig.AD_DOMAIN}",
            password=password,
            read_only=True,
            auto_bind=True
        )
        conn.search(**search_parameters)
        if conn.entries:
            name = conn.entries[0]['cn']
            groups = [group.split(',')[0][3:] for group in conn.entries[0]['memberOf']]
        conn.unbind()
    except LDAPBindError:
        pass
    return name, groups
