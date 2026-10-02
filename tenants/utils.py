import os

from django.conf import settings


def register_tenant_database(tenant):
    """
    Registers a tenant's database into Django's settings.DATABASES at runtime
    (if not already registered). The DB alias is always tenant.db_name.

    Currently using SQLite (like the rest of the project) — each tenant gets
    its own .sqlite3 file inside the 'tenant_databases/' folder.

    When moving to Postgres (recommended for production/multi-tenant scale),
    just change the config below — everything else stays the same:

        settings.DATABASES[alias] = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': f'hrms_{alias}',
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': '5432',
        }
    """
    alias = tenant.db_name

    if alias not in settings.DATABASES:
        db_dir = os.path.join(settings.BASE_DIR, 'tenant_databases')
        os.makedirs(db_dir, exist_ok=True)

        settings.DATABASES[alias] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(db_dir, f'{alias}.sqlite3'),
            'ATOMIC_REQUESTS': False,
            'CONN_MAX_AGE': 0,
            'OPTIONS': {},
            'TIME_ZONE': None,
            'AUTOCOMMIT': True,
        }

        # Django caches its resolved database settings on the connection
        # handler (as a cached_property called 'settings', exposed read-only
        # via the 'databases' property). On newer Django versions that
        # property has no setter, so instead of assigning to it directly we
        # just drop the cached value — the next access recomputes it fresh
        # from settings.DATABASES, which now includes our new alias.
        from django.db import connections
        connections.__dict__.pop('settings', None)

    return alias