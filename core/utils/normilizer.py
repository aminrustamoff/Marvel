def prepare(context):
    # submit = {"question1" : "Hello", "question2" : "1234", "question3" : None}

    # answers = """
    # 1 Hello/hello/hola there
    # 2 1234
    # 3 None
    # """
    splitted = context.split("\r\n")
    dict_answers = {}
    temp_sp = []

    for sp in splitted:
        if sp != "":
            temp_sp.append(sp)
    splitted = temp_sp
    print(splitted)

    for i in splitted:
        space = i.find(' ')
        key_num = i[:space]
        print(key_num)
        key = f"question{key_num}"
        dict_answers[key] = i[space+1:]


    for id_num in dict_answers:
        variants = dict_answers[id_num].split("/")
        for variant in variants:
            clean_variant = variant.strip()
            variants.remove(variant)
            variants.append(clean_variant)
        dict_answers[id_num] = variant
        
    return dict_answers
