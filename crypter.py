import json
from cryptography.fernet import Fernet
import config

PATH = './dumps/'
EXT = '.json'

def server_to_file(serverid):
	return PATH + str(serverid)+EXT

def read_to_dict(serverid):
	filename = server_to_file(serverid)

	with open(filename, "rb") as read_file:
		file_data = read_file.read()

	decrypted = fernet.decrypt(file_data)
	dec_dict = json.loads(decrypted.decode('utf-8'))

	return dec_dict

def dict_to_json(data, serverid):
    enc_dict = fernet.encrypt(json.dumps(data,indent = 2).encode('utf-8')) #encrypt
    filename = server_to_file(serverid)

    # Write the updated data back to the file
    with open(filename, "wb") as write_file:
        write_file.write(enc_dict)

key = config.get_key()
fernet = Fernet(key)