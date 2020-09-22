import module_dictionary

tmlistfile = open('tm.list', 'r')
dict_file = open('mdictionary.py', 'w')
dict_list = module_dictionary.modules_dicts

for line in tmlistfile:
    line = line.replace('\n','')

    new_dict = {
            'OPCODE': line,
            'NAME': 'null',             # could ask for user input here for each one ?? 
            'DESCRIPTION': 'null',      # ^
            'SUBSYSTEM': 'null',        # ^
            'VALUE': 'null'             # ^
        }

    if new_dict not in dict_list:
        # name = input('What is the name for {0}'.format(line))
        dict_list.append(new_dict)
    else:
        # Exists, so just pass.
        pass

dict_file.write('modules_dicts = ')
dict_file.write(''.join(str(dict_list)))