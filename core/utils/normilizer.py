def prepare(context):
    dict_answers = {}
    
    # Split by newline and ignore empty strings
    lines = [line for line in context.split("\n") if line.strip() != ""]
    
    for line in lines:
        line = line.strip()
        
        # Check for the asterisk flag at the very end
        exclude_lowercase = line.endswith("*")
        if exclude_lowercase:
            line = line[:-1].strip() # Remove the asterisk and clean space
            
        # Split on the FIRST space to separate number from content
        parts = line.split(' ', 1)
        
        if len(parts) == 2:
            key_num = parts[0]
            answers_string = parts[1]
            key = f"question{key_num}"
            
            # Use a list to maintain order, but check against a set for uniqueness
            raw_variants = [v.strip() for v in answers_string.split("/") if v.strip()]
            processed_variants = []
            seen = set()

            for variant in raw_variants:
                # Potential versions
                versions = [variant, variant.upper()]
                if not exclude_lowercase:
                    versions.append(variant.lower())

                for v in versions:
                    if v not in seen:
                        processed_variants.append(v)
                        seen.add(v)
            
            dict_answers[key] = processed_variants

    return dict_answers

# --- Example Usage ---
# context = """
# 1 Aminjon Rustamov * 
# 2 Samarkand / Samarkand city *
# 3 three/3
# 4 Dog
# 5 Cat
# """

# import json
# print(json.dumps(prepare(context), indent=4))