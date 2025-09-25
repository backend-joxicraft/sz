#!/usr/bin/env python3
"""
Example: Hello World
This is a simple example showing how to add code to the sz project.
"""

def hello_world(name="World"):
    """
    Returns a greeting message.
    
    Args:
        name (str): The name to greet. Defaults to "World".
    
    Returns:
        str: A greeting message.
    """
    return f"Hello, {name}!"

if __name__ == "__main__":
    # Example usage
    print(hello_world())
    print(hello_world("sz Project"))