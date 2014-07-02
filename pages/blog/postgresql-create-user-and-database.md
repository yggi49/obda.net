title: 'PostgreSQL: Create User and Database'
published: 2014-04-30
tags: [postgresql, cheat-sheet]

{% include 'cheat-sheet.md' %}

*(Taken from
[PostgreSQL add or create a user account and grant permission for database](http://www.cyberciti.biz/faq/howto-add-postgresql-user-account/).)*

    :::console
    user@host:~$ psql -U postgres

<!-- -->

    :::psql
    postgres=# CREATE USER tom WITH PASSWORD 'myPassword';
    postgres=# CREATE DATABASE jerry;
    postgres=# GRANT ALL PRIVILEGES ON DATABASE jerry to tom;

Or, with multi-line input directly from the command line:

    :::console
    user@host:~$ cat <<EOF | psql -U postgres
    CREATE USER tom WITH PASSWORD 'myPassword';
    CREATE DATABASE jerry;
    GRANT ALL PRIVILEGES ON DATABASE jerry to tom;
    EOF

You can specify a different collation than the default collation by using
`template0` as template database:

    :::console
    user@host:~$ cat <<EOF | psql -U postgres
    CREATE DATABASE jerry TEMPLATE = template0 LC_COLLATE = 'de_AT.UTF-8';
    EOF
