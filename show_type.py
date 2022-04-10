import argparse

def parse_args():
    '''LED is a better example for async because processing long documents
    is compute intensive.
    '''
    parser = argparse.ArgumentParser(description='An async NLP server.')
    parser.add_argument('--qa', action='store_true')
    return parser.parse_args()

args = parse_args()

# I'm "statically typing" everything now so I need to know what 
# type argparse.ArugmentParser.parse_args() returns
print(type(args))
# Turns out it's a argparse.Namespace
