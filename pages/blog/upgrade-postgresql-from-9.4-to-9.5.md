title: Upgrade PostgreSQL from 9.4 to 9.5
published: 2016-02-16
tags: [linux, gentoo, postgresql]

{% include 'gentoo-disclaimer.md' %}

After installing PostgreSQL 9.5, first setup the initial database environment:

    emerge --config dev-db/postgresql:9.5

Next, compare and update the configuration files:

  * `/etc/conf.d/postgresql-9.5`
  * `/etc/postgresql-9.5/*`

If needed, run `/etc/init.d/postgresql-9.4 stop` to stop the old database
server before proceeding with the upgrade.

Now, switch to the `postgres` user, and execute [`pg_upgrade`][1], which does
the hard work.  Run it with the `--check` option first to perform only the
necessary checks without changing any data:

    :::console
    # su - postgres
    $ /usr/lib/postgresql-9.5/bin/pg_upgrade \
          --old-bindir=/usr/lib/postgresql-9.4/bin/ \
          --new-bindir=/usr/lib/postgresql-9.5/bin/ \
          --old-datadir=/var/lib/postgresql/9.4/data/ \
          --new-datadir=/var/lib/postgresql/9.5/data/ \
          --check

*(This uses the default paths for the data directories; adjust the command
accordingly if your setup is different.)*

If the command runs without errors, execute it again without the `--check`
flag to perform the actual upgrade.  Once it is finished, you can start the
new database server via `/etc/init.d/postgresql-9.5 start`, do some cleanup
tasks that `pg_upgrade` might have you prompted for, and verify that
everything works as before.  Finally, uninstall the old PostgreSQL version,
and don’t forget to add/delete services from runlevels if necessary.

[1]: http://www.postgresql.org/docs/9.5/static/pgupgrade.html
