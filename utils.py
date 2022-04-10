import yaml
import os
import re
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def authenticate() -> GoogleAuth:
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return gauth

def get_drive() -> GoogleDrive:
    gauth = authenticate()
    return GoogleDrive(gauth)

def get_file(filename: str, drive: GoogleDrive) -> bool:
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    _id = None
    for file_dst in file_list:
        if file_dst['title'] == filename:
            _id = file_dst['id']
            break
    if _id is None:
        print('File not found!')
        return False
    file_src = drive.CreateFile({'id': _id})
    file_src.GetContentFile(filename)
    return True

def put_file(filename: str, drive: GoogleDrive) -> None:
    file_dst = drive.CreateFile({'title': filename})
    file_dst.SetContentFile(filename)
    file_dst.Upload()

def is_even(k: int) -> bool:
    '''Is the input integer even?
    '''
    return k % 2 == 0

def get_cfg() -> dict:
    '''Load the configuration and envsubst the raw yaml.
    '''
    with open('config.yaml', 'r') as f:
        raw_yaml = f.read()
    subst_yaml = envsubst(raw_yaml)
    return yaml.safe_load(subst_yaml)


def envsubst(raw_yaml: str) -> str:
    '''Substitute $ENV_VAL into every expression of 
    ${ENV_VAL} in the raw yaml.
    '''
    # Find arbitrary number of occurences of ${} inside raw yaml.
    pattern = r'(\$\{[^\}]*\})+'
    split_yaml = re.split(
        pattern, 
        raw_yaml, 
        flags=re.DOTALL|re.MULTILINE,
    ) # Make our yaml into a list
    outlist = [] 
    for k, x in enumerate(split_yaml):
        if is_even(k): # Interleave everything that's not inside ${}...
            outlist.append(x)
        else: # with everything that is.
            # Variable name is everything between '${' and '}'
            y = os.getenv(x[2:-1]) # Get the value from OS
            outlist.append(y)
    return ''.join(outlist) # Turn substituted list into a string
