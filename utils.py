def ppformat(obj: list[dict]) -> str:
    """Pretty print a dictionary or list."""
    
    return_str = "\n"
    for item in obj:
        return_str +=  str(item) + ",\n"
    
    return return_str