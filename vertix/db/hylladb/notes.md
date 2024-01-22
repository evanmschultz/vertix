# Hylla

HyllaDB, the Ikea of databases. It is a flat-pack database that is easy to assemble and use, but you decide the level of complexity based on its simple modular forms. It is a fast, simple, and easy to use database that allows for storage of complex data types like Python class instances. It is essentially as key-value database that allows whatever level of nesting you desire while maintaining fast lookup, O(1) for any value, no matter how nested. The Library is your database. In it, Sections, similar to a bookcase or library, are essentially directories holding 'Shelves' or other 'Sections', which are Python shelve files. Shelves can act similar to tables, but are dictionaries. It uses Python's pathlib module to quickly access directories, files, and then keys for fast lookups. With this design pattern, depending on system, you can get O(1), constant time, lookups while building ridiculously nested and complex structures. Or better, if your data is flat, you can just use it as a key-value store that allows for storage of complex data types.

Inspired by a lack of options to persist NetworkX graphs and its statement of "It's dictionaries all the way down."

This is a fast database built on python's shelve module that allows for storage of complex data types like class instances. It is not a relational or document database, but a key-value store. Shelves kind of act like tables, but are essentially dictionaries. Shelves are individual files, so you can have multiple shelves in a directory, and multiple directories. It uses Python's pathlib module to quickly access directories, files, and then keys for fast lookups. With this design pattern, depending on system, you can get O(1), constant time, lookups while building ridiculously nested and complex structures.

Using shelve to store data allows for storage of complex data types that can't be serialized into JSON or other similar formats. This allows you to store instances of classes, functions, and other complex data types and quickly retrieve them without having to rebuild them. This is useful for storing large graphs, or other complex data structures.

## Speed

Don't be fooled by the fact that it is written in python, it is fast as every retrieval is in constant O(1) time. As long as you structure your data accordingly.

## Complex Joins, etc.

Complex joins and other relational operations are only possible based on how you structure you data. Be aware, how you structure your data determines the time complexity of your lookups. For instance:

```Python
# Data structure
        "directory": {
            "shelf": {
                "dict_1": {
                    "item": {
                        "nested_item_to_filter_for": "desired_filter_result"
                        } # item['nested_item_to_filter_for'] needs to be check for each dictionary in `shelf`
                },
                "dict_2": {
                    "item": {
                        "nested_item_to_filter_for": "UNDESIRED_filter_result"
                        } # item['nested_item_to_filter_for'] needs to be check for each dictionary in `shelf`
                }
            }
        }
```

This will result in at least O(n) lookup time. Due to how the nesting was structured and that it would have to run through every element of the `shelf` to 'filter' for a value from a key.

## Cautions:

Do not add complex data types (eg. class instances, etc.) to this database if you did not create them, or do not trust the source as it suffers from all of the security issues of python's pickle module, namely potential of running malicious code on deserialization. We have optional sandboxing logic on the roadmap to mitigate this concern when allowing others to add to your database.

<!-- Shelves are not relational, so you can't do joins or other relational operations. You can't do complex queries like you can with document databases. You can't do aggregations like you can with document databases. You can't do transactions like you can with relational databases. You can't do indexing like you can with relational databases. You can't do any of the things that make relational and document databases so powerful. But you can store complex data types and retrieve them quickly. -->

```

```
