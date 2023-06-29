# RFC Reader

This script allows you to read and search for RFCs (Request for Comments) through the command line. RFCs are a type of document from the technology community that describe methods, behaviors, research, or innovations applicable to the working of the Internet and Internet-connected systems. You can read more about RFCs on [Wikipedia](https://en.wikipedia.org/wiki/Request_for_Comments).

## Dependencies
- Python 3
- Python libraries: `requests`, `datetime`, `argparse`, `json`, `re`, `os`

## Usage

The script is invoked from the command line with the following format:

```
python3 rfc.py [OPTIONS] RFC
```


### Options

- `--info`: Return general information about an RFC.
- `--search` or `-s`: Force search.

The `RFC` is a required argument that specifies the RFC number you wish to read. If a search term is used instead, potential matches from the RFC list will be returned.

## Example

To get information about RFC 1234, you would run:

```
python3 rfc.py --info 1234
```

To search for an RFC related to a specific term, for instance "security", you would run:

```
python3 rfc.py --search security
```

Since the script itself relies on a reading program of your choice, you can pipe it to something like `less` with the `-R` tag

```
python3 rfc.py 6193 | less -R
```

## Maintenance

This script is maintained by Benjamin. For any issues or suggestions, you can reach out at `ben@pacman.sh`. 

## License

This project is licensed under the MIT License.