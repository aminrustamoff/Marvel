def prepare(context):
    dict_answers = {}
    
    # Split by newline and ignore empty strings immediately
    lines = [line for line in context.split("\n") if line.strip() != ""]
    
    for line in lines:
        # Split on the FIRST space only to separate the number from the answers
        parts = line.strip().split(' ', 1)
        
        # Ensure we actually have a number and an answer part
        if len(parts) == 2:
            key_num = parts[0]
            answers_string = parts[1]
            
            key = f"question{key_num}"
            
            # Split by "/", strip whitespace from each, and assign the list
            dict_answers[key] = [variant.strip() for variant in answers_string.split("/")]

    return dict_answers
