mysql-convert-charset
=====================

Generates/executes SQL statements to convert MySQL databases
to another charset (likely `utf8mb4_unicode_ci`).

Usage
-----

* Install `mysqlclient` in your Python 3 environment.
* Run `python3 mysql-convert-charset.py -d yourdatabasename` to see what would be executed.
* Add `-x` (or `--execute`) to actually run the queries too.

