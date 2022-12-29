import crypter
import os

class MaxNotesError(Exception):
    pass
class SameKeyError(Exception):
    pass

def create_file(serverid):
    empty = {}
    crypter.dict_to_json(empty, serverid)

def append(serverid,key, value):
    key = str(key)
    value = str(value)
    if os.path.isfile(crypter.server_to_file(serverid)):
        dec_dict = crypter.read_to_dict(serverid)
        if len(dec_dict) == 100:
            raise MaxNotesError
        elif key in dec_dict.keys():
            raise SameKeyError
        else:
            new={key: value}
            dec_dict.update(new)  #update dictionary
            crypter.dict_to_json(dec_dict, serverid)
    else:
        create_file(serverid)
        append(serverid, key, value)
        
def get_content(serverid,key):
    dec_dict = crypter.read_to_dict(serverid)

    if key in dec_dict.keys():
        value = dec_dict.get(key)
    else:
        raise KeyError

    return value

def listkeys(serverid):
    dec_dict = crypter.read_to_dict(serverid)

    keys = dec_dict.keys()
    keyslist=list(keys)

    return keyslist

def deletename(serverid,name):
    dec_dict = crypter.read_to_dict(serverid)

    del dec_dict[name]

    crypter.dict_to_json(dec_dict, serverid)

def renamekey(serverid, name, rename):    
    dec_dict = crypter.read_to_dict(serverid)
    if key not in dec_dict.keys():
        raise KeyError
    else:
      content = dec_dict.pop(name)
      dec_dict.update({str(rename):content})
  
      crypter.dict_to_json(dec_dict, serverid)

def editvalue(serverid, key, content):    
    dec_dict = crypter.read_to_dict(serverid)

    if key not in dec_dict.keys():
        raise KeyError
    else:
        dec_dict[key]=str(content)

        crypter.dict_to_json(dec_dict, serverid)

def remove_file(serverid):
    os.remove(crypter.server_to_file(serverid))