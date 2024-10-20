import re
import sqlite3
from flask import Flask, request, jsonify

class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.node_type = node_type
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Node({self.node_type}, {self.value}, {self.left}, {self.right})"

    def to_dict(self):
        return {
            'node_type': self.node_type,
            'value': self.value,
            'left': self.left.to_dict() if self.left else None,
            'right': self.right.to_dict() if self.right else None
        }

# Initialize Flask app
app = Flask(__name__)

# Initialize SQLite database connection
conn = sqlite3.connect('rules.db', check_same_thread=False)
c = conn.cursor()

# Create rules table in SQLite to store rule strings
c.execute('''
    CREATE TABLE IF NOT EXISTS rules (
        rule_name TEXT PRIMARY KEY,
        rule_string TEXT
    )
''')
conn.commit()

# Function to save rule in the database
def save_rule_to_db(rule_name, rule_string):
    c.execute('INSERT OR REPLACE INTO rules (rule_name, rule_string) VALUES (?, ?)', (rule_name, rule_string))
    conn.commit()

# Function to load rule from the database
def load_rule_from_db(rule_name):
    c.execute('SELECT rule_string FROM rules WHERE rule_name=?', (rule_name,))
    row = c.fetchone()
    return row[0] if row else None

# Function to parse rule string and create AST
def create_rule(rule_string):
    tokens = re.findall(r'\(|\)|AND|OR|[a-zA-Z0-9_><=!\']+', rule_string)

    def parse_expression(tokens):
        if not tokens:
            return None

        token = tokens.pop(0)

        if token == '(':
            left_node = parse_expression(tokens)
            operator = tokens.pop(0) if tokens else None

            if operator is None:
                raise ValueError("Expected an operator after '('")

            right_node = parse_expression(tokens)
            if right_node is None:
                raise ValueError("Expected a right operand after operator")

            if not tokens or tokens.pop(0) != ')':
                raise ValueError("Expected closing parenthesis ')'")

            return Node("operator", operator, left_node, right_node)

        elif re.match(r'[a-zA-Z0-9_]+', token):
            operator = tokens.pop(0) if tokens else None
            value = tokens.pop(0) if tokens else None

            if operator and value:
                return Node("operand", f"{token} {operator} {value}")
            else:
                raise ValueError(f"Invalid operand format: '{token}'. Expected format: 'field operator value'.")

        raise ValueError(f"Unexpected token: {token}")

    return parse_expression(tokens)

# Function to evaluate rule AST against user data
# Add predefined valid fields for validation
VALID_FIELDS = {"age", "department", "salary", "experience"}

def evaluate_rule(node, data):
    if node.node_type == "operand":
        parts = re.split(r'([><=!]+)', node.value)

        if len(parts) != 3:
            raise ValueError(f"Invalid operand format: '{node.value}'. Expected format: 'field operator value'.")

        field, operator, value = parts
        field = field.strip()
        value = value.strip()

        # Validate the field
        if field not in VALID_FIELDS:
            raise ValueError(f"Invalid field '{field}' in rule. Allowed fields are: {VALID_FIELDS}")

        field_value = data.get(field)
        if field_value is None:
            raise ValueError(f"Field '{field}' not found in provided data.")

        # Handle string values wrapped in single quotes
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]  # Remove single quotes around the value

        else:
            # Try to convert the value to float if it's not a string
            try:
                value = float(value)
            except ValueError:
                raise ValueError(f"Invalid value format: '{value}'. Must be a number or a string.")

        # Debugging information
        print(f"Evaluating: {field} {operator} {value} (field_value: {field_value})")

        # Comparison Logic
        if operator == '>':
            return field_value > value
        elif operator == '<':
            return field_value < value
        elif operator == '=':
            return field_value == value
        elif operator == '!=':
            return field_value != value
        else:
            raise ValueError(f"Unknown operator: {operator}")

    elif node.node_type == "operator":
        left_result = evaluate_rule(node.left, data)
        right_result = evaluate_rule(node.right, data)

        print(f"Operator: {node.value}, Left Result: {left_result}, Right Result: {right_result}")

        if node.value == "AND":
            return left_result and right_result
        elif node.value == "OR":
            return left_result or right_result
        else:
            raise ValueError(f"Unknown operator: {node.value}")

def combine_rules(rules, operator):
    if not rules:
        raise ValueError("No rules provided for combination.")

    # Start with the first rule
    combined_ast = rules[0]

    # Combine subsequent rules with the chosen operator (AND/OR)
    for rule_ast in rules[1:]:
        combined_ast = Node("operator", operator, combined_ast, rule_ast)

    return combined_ast

# API to create rule and store it in SQLite
@app.route('/create_rule', methods=['POST'])
def api_create_rule():
    rule_string = request.json.get('rule_string')
    rule_name = request.json.get('rule_name', 'rule')

    try:
        ast = create_rule(rule_string)
        save_rule_to_db(rule_name, rule_string)
        return jsonify({"rule_name": rule_name, "ast": ast.to_dict()}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# API to evaluate rule against user data
@app.route('/evaluate_rule', methods=['POST'])
def api_evaluate_rule():
    rule_name = request.json.get('rule_name')
    data = request.json.get('data')

    rule_string = load_rule_from_db(rule_name)
    if rule_string is None:
        return jsonify({"error": "Rule not found"}), 404

    ast = create_rule(rule_string)
    result = evaluate_rule(ast, data)
    return jsonify({"result": result})

# API to modify an existing rule
@app.route('/modify_rule', methods=['POST'])
def modify_rule():
    rule_name = request.json.get('rule_name')
    new_rule_string = request.json.get('new_rule_string')

    if load_rule_from_db(rule_name) is None:
        return jsonify({"error": "Rule not found"}), 404

    try:
        new_ast = create_rule(new_rule_string)
        save_rule_to_db(rule_name, new_rule_string)
        return jsonify({"message": "Rule modified successfully", "new_ast": new_ast.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# API to combine multiple rules
@app.route('/combine_rules', methods=['POST'])
def api_combine_rules():
    rule_names = request.json.get('rule_names')
    operator = request.json.get('operator', 'AND')  # Default to AND if no operator is provided
    combined_rule_name = request.json.get('combined_rule_name', 'combined_rule')  # Name for the combined rule

    # Load the rules from the database
    rules = []
    combined_rule_string = ""
    for rule_name in rule_names:
        rule_string = load_rule_from_db(rule_name)
        if rule_string is None:
            return jsonify({"error": f"Rule '{rule_name}' not found"}), 404
        
        # Combine rule strings for storage
        if combined_rule_string:
            combined_rule_string += f" {operator} ({rule_string})"
        else:
            combined_rule_string = f"({rule_string})"

        # Parse the rule string to create an AST
        rule_ast = create_rule(rule_string)
        rules.append(rule_ast)

    # Combine the rules into a single AST using the provided operator
    try:
        combined_ast = combine_rules(rules, operator)
        
        # Save the combined rule in the database
        save_rule_to_db(combined_rule_name, combined_rule_string)  # Save combined rule as a string
        
        return jsonify({"combined_ast": combined_ast.to_dict(), "rule_name": combined_rule_name}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
