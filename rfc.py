#!/bin/python3

# The idea of this script is to allow me to read and search for RFCs through the commandline.
# I often anyways end up reading them, googling them is a bit annoying, this should make things a lot easier
# About RFCs: https://en.wikipedia.org/wiki/Request_for_Comments
import requests
import datetime
import argparse
import json
import re
import os


RFC_LIST="https://www.ietf.org/rfc/rfc-index"
RFC_TEXT_PREFIX="https://www.ietf.org/rfc/rfc" # 9411.txt




class RfcObject:
    def __init__(self, id):
        self.id = id
        self.fill_variables()
        
    def fill_variables(self):
        self.text           = return_web_page(f"{RFC_TEXT_PREFIX}{self.id}.txt")
        self.json           = return_json_of_rfc(self.id)
        self.title          = self.json['title'         ] 
        self.abstract       = self.json['abstract'      ] # This does not necessarily always exist, thus we should check for the content before printing a potentially empty string.
        self.authors        = self.json['authors'       ] 
        self.page_count     = self.json['page_count'    ]
        self.keywords       = self.json['keywords'      ] # Does not always exist
        self.obsoleted_by   = self.json['obsoleted_by'  ]
        self.pub_date       = self.json['pub_date'      ]

def colorize(text, regex="", colour='\x1b[38;5;180m{}\x1b[0m'):
            # Cyan:     "\x1b[38;5;14m{}\x1b[0m"
            # Green:    "\x1b[38;5;2m{}\x1b[0m"
            # Red:      "\x1b[38;5;1m{}\x1b[0m"
            # Peach:    "\x1b[38;5;180m{}\x1b[0m" (default)
            # Yellow:   "\x1b[38;5;3m{}\x1b[0m"
            # Blue:     "\x1b[38;5;4m{}\x1b[0m"
            # Magenta:  "\x1b[38;5;5m{}\x1b[0m"
    # Underline RFC tags
    text = re.sub(r'\b(?:RFC)?(\d{4})\b' ,\
                  lambda m: '\x1b[4m{}\x1b[0m'.format(m.group()), text)
    # make matches chosen colours
    return re.sub(regex ,lambda m:colour .format(m.group()), text)

def parse_arguments():
    parser = argparse.ArgumentParser(prog="rfc",description="Search for and read RFCs",epilog="Ben 2023, ben@pacman.sh")
    
    parser.add_argument('rfc', metavar='rfc', nargs='*'\
                        , help="The RFC # you wish to read. You can also use search terms in order to find potential ")
    
    parser.add_argument('--info', default=False, action='store_true',
                        help="Return general information about an RFC")
    
    parser.add_argument('--search', '-s', action='store_true',
                        help="Force search")
    
    args = parser.parse_args()
    if not args.rfc:
        print("A search term is required!")
        exit(1)

    return  args

def fix_text_for_reading(text): # -> string
    text_output = colorize(text, "([A-Za-z0-9\.\-\_\/\+]*\@| \
                           https?\:\/\/)([A-Za-z0-9\.\_\/\+])* \
                           \.[a-z]*\/?[A-Za-z0-9\.\-\_\/]*", \
                           colour='\x1b[38;5;14m{}\x1b[0m')
    #-> tee jotain muuta :D
    return text_output

def return_json_of_rfc(id):
    json_text       = return_web_page(f'{RFC_TEXT_PREFIX}{id}.json')
    json_object     = json.loads(json_text)
    if isinstance(json_object, list):
        json_object = json_object[0]
    return json_object
    
def return_web_page (url): # -> string 
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Error querying page: {url} \n{r.status_code}")
        exit(1)
    
    return r.text

def find_rfc(query):
    search_term = re.compile(' '.join(query), \
                                 flags=re.IGNORECASE)
    rfc_list = return_rfc_index()
    for rfc_item in rfc_list:
        if search_term.search(rfc_item):
            print(colorize(rfc_item, search_term))
                
def return_rfc_index ():
    # We don't want to always query the website, it's relatively slow. Instead we want to see how old our local index is and utilize that instead if possible :)
    location = os.path.expanduser('~')+"/.local/rfc/rfc_index.txt"

    if os.path.exists(location):
        print("Index exists, checking age")
        today = datetime.datetime.today()
        last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(location))
        
        if (today - last_modified).days > 30:
            print("Index is too old, fetching a new one")
            index = return_web_page("https://www.ietf.org/rfc/rfc-index")
            with open(location, 'w') as f:
                f.write(index)
        else:
            print("Reading index from local db")
            with open(location, 'r') as file_reader:
                index = file_reader.read()
    else:
        print("Index does not exist, fetching...")
        index = return_web_page("https://www.ietf.org/rfc/rfc-index")
        parent_dir = os.path.dirname(location)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        with open(location, 'w') as f:
            f.write(index)
    
    
    entries = re.findall(r'\d{4}.*?\n\n', index, re.DOTALL)
    entry_list = [entry.strip() for entry in entries]

    return entry_list

def print_rfc(rfc_id, args=None):
    # There are a few ways os printing the rfc 
    # We can either print the entire RFC, or the TLDR. Whichever the client prefers is decided with the -tldr tag.
    # First, lets fetch the actual rfc:
    rfc_object = RfcObject(rfc_id)
    if not args.info:
        print(fix_text_for_reading(rfc_object.text))
    else:
        print(f"General information about RFC{rfc_id}:\
              \nTitle:           {rfc_object.title}\
              \n\nAbstract:        \n{rfc_object.abstract}\n\
              \nPage count:      {rfc_object.page_count}\
              \nKeywords:        {', '.join(rfc_object.keywords)}\
              \nAuthors:         {', '.join(rfc_object.authors)}\
              \nPublishing date: {rfc_object.pub_date}")
    # Now, that should be able to fetch the actual rfc. NB! We need to add 

def main (arguments):   # -> int
    if not arguments.rfc[0].isdigit() or arguments.search: # If it's not a digit, then we'll just return the list of potential matches from the RFC list
        find_rfc(arguments.rfc)
        exit(0)
    rfc_id = "{:04d}".format(int(arguments.rfc[0]))
    # okay, so now if the user is not searching for RFC's, we can try to actually fetch an rfc

    print_rfc(rfc_id, args=arguments)

if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)