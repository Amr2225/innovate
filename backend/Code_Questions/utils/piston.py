import requests
import ast
import sys

PISTON_URL = "https://emkc.org/api/v2/piston/execute"

def run_code(source_code, stdin, language="python3", version="3.10.0"):
    print("=== Code being sent to Piston ===")
    print(source_code)
    print("=== Input being sent to Piston ===")
    print(stdin)
    print("=================================")
    
    payload = {
        "language": language,
        "version": version,
        "files": [
            {
                "name": "main.py",
                "content": source_code
            }
        ],
        "stdin": stdin,
        "args": [],
        "compile_timeout": 10000,
        "run_timeout": 3000,
        "run_memory_limit": -1
    }

    try:
        res = requests.post(PISTON_URL, json=payload)
        data = res.json()
        print("=== Piston Response ===")
        print(data)
        print("=====================")
        run_result = data.get("run", {})
        return {
            "stdout": run_result.get("stdout"),
            "stderr": run_result.get("stderr"),
            "output": run_result.get("output"),
            "exit_code": run_result.get("code"),
            "signal": run_result.get("signal"),
        }
    except Exception as e:
        return {"error": str(e)}

def extract_function_info(student_code):
    """
    Extracts the function name and argument names from the student's code.
    Returns (function_name, [arg1, arg2, ...])
    """
    tree = ast.parse(student_code)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            arg_names = [arg.arg for arg in node.args.args]
            return function_name, arg_names
    raise ValueError("No function definition found")

def generate_wrapper(function_name, arg_names):
    args_str = ', '.join(arg_names)
    wrapper = f"""
import ast
import sys

try:
    # Get input and parse it
    input_str = input()
    print(f"Received input: {{input_str}}", file=sys.stderr)
    
    # Convert string representation of list to actual list
    input_list = ast.literal_eval(input_str)
    print(f"Parsed input list: {{input_list}}", file=sys.stderr)
    
    # Unpack the input list into variables
    {args_str} = input_list
    
    # Call the function and get result
    result = {function_name}({args_str})
    print(f"Function result: {{result}}", file=sys.stderr)
    
    # Print the result as a string
    print(str(result))
except Exception as e:
    print(f"Error occurred: {{str(e)}}", file=sys.stderr)
    raise
"""
    return wrapper

def prepare_code_for_piston(student_code):
    try:
        function_name, arg_names = extract_function_info(student_code)
        wrapper_code = generate_wrapper(function_name, arg_names)
        # Combine the code with proper spacing
        full_code = f"{student_code.strip()}\n\n{wrapper_code.strip()}"
        print("=== Full Code ===")
        print(full_code)
        print("================")
        return full_code
    except Exception as e:
        print(f"Error preparing code: {str(e)}")
        raise

