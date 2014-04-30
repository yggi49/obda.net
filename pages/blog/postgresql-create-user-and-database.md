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
    template1=# CREATE USER tom WITH PASSWORD 'myPassword';
    template1=# CREATE DATABASE jerry;
    template1=# GRANT ALL PRIVILEGES ON DATABASE jerry to tom;

Or, with multi-line input directly from the command line:

    :::console
    user@host:~$ cat <<EOF | psql -U postgres -d template1
    CREATE USER tom WITH PASSWORD 'myPassword';
    CREATE DATABASE jerry;
    GRANT ALL PRIVILEGES ON DATABASE jerry to tom;
    EOF
