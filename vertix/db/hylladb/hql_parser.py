from rich import print
from typing import Any
from pyparsing import (
    ParserElement,
    Word,
    ZeroOrMore,
    alphas,
    alphanums,
    Optional,
    Group,
    delimitedList,
    oneOf,
    quotedString,
    Suppress,
    Forward,
    Dict,
    Combine,
)


# Define the HyQLParser class
class HyQLParser:
    def __init__(self) -> None:
        # Identifier rule: words starting with an alphabet and may contain alphanumeric characters and underscores
        self.identifier = Word(alphas, alphanums + "_")

        # Path rule: delimited list of identifiers separated by a period (.)
        self.path: ParserElement = delimitedList(
            self.identifier, delim="."
        ).setResultsName("path")

        # DotSeparatedField rule: matches dot-separated identifiers (e.g., field1.subfield.sub_subfield)
        self.dotSeparatedField = Combine(
            Word(alphas, alphanums + "_")
            + ZeroOrMore("." + Word(alphas, alphanums + "_"))
        )
        # Fields rule: optional, matches a list of dotSeparatedFields enclosed in curly braces ({})
        self.fields: ParserElement = Optional(
            Suppress("{")
            + delimitedList(self.dotSeparatedField, delim=",")
            + Suppress("}")
        ).setResultsName("fields")

        # Comparison operators
        self.comparisonOp: ParserElement = oneOf("== != < > <= >=")
        # Logical operators
        self.logicalOp: ParserElement = oneOf("and or")
        # Condition rule: matches an identifier followed by a comparison operator and a value (which could be alphanumeric or a quoted string)
        self.condition = Group(
            self.identifier + self.comparisonOp + (Word(alphanums) | quotedString)
        )

        # Forward declaration for filter expressions (used for recursive patterns)
        self.filterExpr = Forward()
        # Atom rule: matches either a condition or a nested filter expression enclosed in parentheses
        self.atom: ParserElement = self.condition | Suppress(
            "("
        ) + self.filterExpr + Suppress(")")
        # Filter expression rule: matches an atom followed by zero or more combinations of logical operators and atoms
        self.filterExpr <<= (
            self.atom + ZeroOrMore(self.logicalOp + self.atom)
        ).setResultsName("filter")

        # Query rule: combines path, fields, and filter expressions into a single Group
        self.query = (
            self.path.setResultsName("path")
            + self.fields.setResultsName("fields")
            + self.filterExpr.setResultsName("filter")
        )

    # Parse method: takes a query string and returns the parsed result as a dictionary
    def parse(self, queryString) -> dict[str, Any]:
        return self.query.parseString(queryString).asDict()


# Function to parse a HyQL query string using the HyQLParser class
def parse_HyQL_query(queryString) -> dict[str, Any]:
    return HyQLParser().parse(queryString)


# Main execution block
if __name__ == "__main__":
    # Example query string
    exampleQuery = "parent_section.child_section.shelf_name{field1.subfield.sub_subfield, field2}(field1 == 'value' and field2 < 10 or field2 != 'otherValue')"
    # Parse the example query and print the result
    parsedQuery = parse_HyQL_query(exampleQuery)
    print(parsedQuery)


example_desired_query_structure = """
{
    "path": "parent_section.child_section.shelf_name",
    "keys": {
        field1,
        field2
    }
    "filters": (
        field1 == 'value'
        and field2 < 10
        or field2 != 'otherValue'
    )
}
"""
