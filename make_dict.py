from spanish_dict.dictdlib import DictDB
import json
old_spanish_dict = DictDB()
new_spanish_dict = {}



words = old_spanish_dict.getdeflist()
for word in words:
    if word in ['00databasealphabet', '00databasedictfmt1121', '00databaseinfo', '00databaseshort', '00databaseurl', '00databaseutf8']:
        continue
    definitions = old_spanish_dict.getdef(word)
    new_spanish_dict[word] = definitions


import pdb; pdb.set_trace()

json_dict = json.dumps(new_spanish_dict)
f = open("spanish_dict.json","w+")
f.write(json_dict)
f.close()