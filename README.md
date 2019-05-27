Script to be able to recursively search through a directory and have a summary per file.

Example:
```
./finder.py hello world test

FILE              | hello | world | test
login.html        |     1 |     0 |    0
logout.html       |     0 |     1 |    0
script.js         |     4 |     2 |    0
more_details.html |     1 |     3 |    0
main.py           |     2 |     2 |    3
test.py           |     0 |     0 |   10
TOTAL             |     8 |     8 |   13

```

Accepted parameters:
```
-dir    directory         -> choose the directory where the search will be applied (current folder by default)
-v      verbose           -> print the row for every match - usefull to get the context
-fn     full name         -> Use file path instead of name as references
-cs     case sensitive    -> Apply the search with case sensitiveness
```

A log file will also be created (by default in your current directory) where you can see a detailed view of the search)

By default the script will only search py/html/js/txt files but you can easily change that from the script.
