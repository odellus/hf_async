import yaml
import os
import re

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
