title: 'Export Postgres Table to CSV'
published: 2014-10-23
tags: [postgresql, cheat-sheet]

{% include 'cheat-sheet.md' %}

PostgreSQL’s `psql` command line client features a `\copy` command that allows
dumping a table to a CSV file:

    :::psql
    \copy table_name to 'filename.csv' delimiter ',' csv header

The `header` argument at the end will add a header line with the column names
to the CSV file.  Use `;` as delimiter if the CSV file shall be compatible
with Microsoft’s Excel.
