# 🌐 🇸🇪 🔍 HyQL - Hylla Query Language

Overview
HQL is a querying language tailored for HyllaDB, enabling users to fetch and manipulate data through a structured, readable syntax. It is inspired by GraphQL and glom, focusing on simplicity and expressiveness.

## 🛠️ ⛓️ Syntax Components

### 🧭 <u>Path</u>

**Definition:**

-   Represents the location of data within HyllaDB.

**Syntax:**

-   `section.subsection.shelf`

**Example:**

-   `books.fiction.scifi`

**Usage:**

-   Specifies the hierarchical path to a particular data shelf.

### 📋 <u>Fields</u>

**Definition:**

-   Specific data entries or keys within a shelf.

**Syntax:**

-   `{field1, field2}`

**Example:**

-   `{title, author}`

**Usage:**

-   Selects only the specified fields from a shelf.

### 🔍 <u>Filters</u>

**Definition:**

-   Conditions to narrow down the selection of data.

**Syntax:**

-   `(condition1 && condition2)`

**Example:**

-   `(author == 'Asimov' && year > 1950)`

**Usage:**

-   Retrieves data that meets all the specified conditions.

### 🪆 <u>Nested Queries</u>

**Definition:**

-   Queries within queries, allowing retrieval of related data.

**Example:**

-   `library{section{shelf{field1, field2}}}`

**Usage:**

-   Enables fetching data from multiple levels in a single query.

### 📊 <u>Metadata Queries</u>

**Definition:**

-   Queries specifically designed to fetch metadata.

**Examples:**

-   `section.shelf.metadata{key1, key2}`
-   `section.metadata{key1, key2}` - Note how sections can also have metadata.
    **Usage:**
-   Targets metadata storage within sections or shelves.

## 🪜 Query Processing Steps

1. **Parsing:** The HQL query is parsed and broken down into its components (paths, fields, filters).

1. **Path Resolution:** The specified path is navigated to locate the target shelf or section.

1. **Data Retrieval:** Data is fetched from the database according to the path and fields specified.

1. **Filter Application:** Any filter conditions are applied to the retrieved data.

## 📦 Response Formation:

The final step in processing an HQL query where the data, conforming to the structure of the query, is compiled and returned as a Python dictionary.

**Format Consistency:**

The response is formatted to mirror the way data is structured within HyllaDB. This ensures a natural and intuitive representation, especially when retrieving various data scales—from single items to complex nested structures.

**Usage:**

The dictionary format allows for easy access and manipulation of the response data, making it particularly suitable for Python applications.

**Example:**

For a query like `section.shelf{field1, field2}`, assuming section is books, shelf is novels, and the fields are title and author, the response might look like this:

```python
{
    "books": {
        "novels": {
            "title": "Foundation",
            "author": "Asimov"
        }
    }
}
```

## 💡 Best Practices and Usage Tips

**Clarity:**

-   Keep queries as clear and concise as possible.

**Field Selection:**

-   Request only the fields you need to optimize performance.

**Filtering:**

-   Use filters judiciously to retrieve specific data subsets.

**Nested Queries:**

-   Utilize nested queries for complex data structures.
