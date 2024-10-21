# Rule Engine with AST

This project is a **Rule Engine** designed to evaluate user eligibility based on attributes such as `age`, `department`, `salary`, and `experience`. The system dynamically creates rules, stores them in an SQLite database, combines rules, modifies them, and evaluates rules using an **Abstract Syntax Tree (AST)**.

## Features

- **Create Rule**: Define new rules and store them in the database.
- **Evaluate Rule**: Test if a user's data meets the criteria of a specific rule.
- **Modify Rule**: Update existing rules.
- **Combine Rules**: Merge multiple rules using logical operators (`AND`, `OR`).
- **Error Handling**: Handles invalid rule formats, unknown fields, and missing operators or parentheses.
- **Field Validation**: Ensures that only allowed fields like `age`, `department`, `salary`, and `experience` are used in the rules.

## Bonus Features
1. **Error Handling for Invalid Rule Strings**: 
   - Handles common errors like unbalanced parentheses, invalid operators, or missing operands.
2. **Field Validation**: 
   - Only predefined fields (`age`, `department`, `salary`, `experience`) can be used in the rules.
3. **Rule Modification**: 
   - The `/modify_rule` API allows dynamic modification of existing rules, including changing operators and operands.
4. **Storing Combined Rules**: 
   - The `/combine_rules` API allows combining multiple rules into one and storing them for later use.

## Setup

1. **Clone the Repository**:
   ```
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Install Dependencies**:
   Use a virtual environment for better dependency management:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   Start the Flask server:
   ```bash
   python rule_engine.py
   ```
   The server will run on `http://127.0.0.1:5000/`.

## API Documentation
   **POSTMAN API**:
   **Create POST file**:
   - After creation of collections select body under that select raw with JSON content and then write the SQL queries.
   - Created collections like create_rule, evaluate_rule, modify_rule, and combine_rules.
   - create_rule is used to create sql queries.
   - evaluate_rule is used to evaluate the queries.
   - modify_rule is used to change the query rules.
   - Finally combine_rules is used to combine the multiple rules.
        - For multiple rules we need to create more create_rule collections.
        - Then add query for combibine the query rules.
   - Verify for the multiple testcases for the better output.
   - Use testcases like multiple nodes, multiple number of rules and so on...
   
### 1. **Create Rule**
   - **Endpoint**: `/create_rule`
   - **Method**: `POST`
   - **Description**: This endpoint creates a new rule and stores it in the database.
   - **Request Body**:
     ```json
     {
       "rule_name": "rule1",
       "rule_string": "((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)"
     }
     ```
   - **Response** (Success):
     ```json
     {
    "ast": {
        "left": {
            "left": {
                "left": null,
                "node_type": "operand",
                "right": null,
                "value": "age > 30"
            },
            "node_type": "operator",
            "right": {
                "left": null,
                "node_type": "operand",
                "right": null,
                "value": "department = 'Sales'"
            },
            "value": "AND"
        },
        "node_type": "operator",
        "right": {
            "left": {
                "left": null,
                "node_type": "operand",
                "right": null,
                "value": "age < 25"
            },
            "node_type": "operator",
            "right": {
                "left": null,
                "node_type": "operand",
                "right": null,
                "value": "department = 'Marketing'"
            },
            "value": "AND"
        },
        "value": "OR"
    },
    "rule_name": "rule1"
}
     ```

### 2. **Evaluate Rule**
   - **Endpoint**: `/evaluate_rule`
   - **Method**: `POST`
   - **Description**: This endpoint evaluates a rule against user data.
   - **Request Body**:
     ```json
     {
       "rule_name": "rule1",
       "data": {
         "age": 35,
         "department": "Sales"
       }
     }
     ```
   - **Response** (Success):
     ```json
     {
       "result": true
     }
     ```
   - **Response** (Error):
     ```json
     {
       "error": "Rule not found"
     }
     ```

### 3. **Modify Rule**
   - **Endpoint**: `/modify_rule`
   - **Method**: `POST`
   - **Description**: This endpoint allows you to modify an existing rule in the database.
   - **Request Body**:
     ```json
     {
       "rule_name": "rule1",
       "new_rule_string": "(age > 40 AND department = 'Marketing')"
     }
     ```
   - **Response**:
     ```json
     {
       "message": "Rule modified successfully",
       "new_ast": {
         "node_type": "operator",
         "value": "AND",
         "left": {
           "node_type": "operand",
           "value": "age > 40"
         },
         "right": {
           "node_type": "operand",
           "value": "department = 'Marketing'"
         }
       }
     }
     ```

### 4. **Combine Rules**
   - **Endpoint**: `/combine_rules`
   - **Method**: `POST`
   - **Description**: This endpoint combines two or more existing rules using a logical operator (`AND` or `OR`).
   - **Request Body**:
     ```json
     {
       "rule_names": ["rule1", "rule2"],
       "operator": "AND",
       "combined_rule_name": "combined_rule"
     }
     ```
   - **Response**:
     ```json
     {
       "combined_ast": {
         "node_type": "operator",
         "value": "AND",
         "left": {
           "node_type": "operator",
           "value": "AND",
           "left": {
             "node_type": "operand",
             "value": "age > 30"
           },
           "right": {
             "node_type": "operand",
             "value": "department = 'Sales'"
           }
         },
         "right": {
           "node_type": "operator",
           "value": "AND",
           "left": {
             "node_type": "operand",
             "value": "age > 40"
           },
           "right": {
             "node_type": "operand",
             "value": "department = 'Marketing'"
           }
         }
       }
     }
     ```
### 5. **Create Rule**
   - **Endpoint**: `/create_rule`
   - **Method**: `POST`
   - **Description**: This endpoint creates a new rule and stores it in the database.
   - **Request Body**:
     ```json
     {
       "rule_name": "rule2",
       "rule_string": "((age > 30 AND department = 'Marketing')) AND (salary > 20000 OR experience > 5)"
     }
     ```
   - **Response** (Success):
     ```json
     {
    "ast": {
        "left": {
            "left": null,
            "node_type": "operand",
            "right": null,
            "value": "age > 30"
        },
        "node_type": "operator",
        "right": {
            "left": null,
            "node_type": "operand",
            "right": null,
            "value": "department = 'Marketing'"
        },
        "value": "AND"
    },
    "rule_name": "rule2"
}
     ```

## Contact

For any inquiries or issues, please contact:
- Email: pavank0066@gmail.com
- Phone: +91 9398099646

---
