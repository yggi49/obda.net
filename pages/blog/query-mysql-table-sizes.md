title: Query MySQL Table Sizes
published: 2018-11-22
tags: [mysql, cheat-sheet]
refs:
    - '[How to get the sizes of the tables of a MySQL
      database?](https://stackoverflow.com/questions/9620198/) (Stack
      Overflow)'

{% include 'cheat-sheet.md' %}

The following query lists all tables within a MySQL instance along with their
row counts and sizes in [<abbr title='mebibytes'>MiB</abbr>][1]:

    :::sql
    SELECT
         table_schema as `database`,
         table_name as `table`,
         table_rows as `rows`,
         ROUND(((data_length + index_length) / 1024 / 1024), 2) `size_mib`
    FROM information_schema.tables
    ORDER BY (data_length + index_length) DESC;

[1]: https://en.wikipedia.org/wiki/Mebibyte
