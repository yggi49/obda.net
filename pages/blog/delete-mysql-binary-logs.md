title: 'Delete MySQL Binary Logs'
published: 2014-05-22
tags: [mysql, cheat-sheet]

{% include 'cheat-sheet.md' %}

From the [MySQL](http://dev.mysql.com/)
[manual](http://dev.mysql.com/doc/refman/5.6/en/binary-log.html):

> The binary log contains “events” that describe database changes such as
> table creation operations or changes to table data. It also contains events
> for statements that potentially could have made changes (for example, a
> `DELETE` which matched no rows), unless row-based logging is used. The
> binary log also contains information about how long each statement took that
> updated data.

The binary log is primarily needed for master-slave-setups and data recovery
operations.  Files are never deleted and pile up in the `datadir`
(e.g. `/var/lib/mysql`), named `mysqld-bin.000001`, `mysqld-bin.000002`, …
(Alternatively, the files might be named *`hostname`*`-bin.000001`, …)

To get rid of them, run the following two commands as MySQL’s admin user:

    :::mysql
    mysql> FLUSH LOGS;
    mysql> RESET MASTER;

The first command flushes unsaved transactions to the database, and the second
one deletes all binary logs.

If you do not need the binary logs at all, you can also disable them entirely
by removing the `log-bin` option from your `my.cnf` configuration file.
