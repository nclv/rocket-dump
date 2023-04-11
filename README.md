# Rocket-Dump

Simple tool to dump the messages of a [rocket.chat](https://www.rocket.chat/) instance using [rocketchat_API](https://github.com/jadolg/rocketchat_API).
It can be used to collect all the informations accessible to an anonymous user.

[Endpoints reference](https://developer.rocket.chat/reference/api/rest-api/endpoints)

## Requirements
```bash
pip3 install rocketchat_API rich-click
```

## Usage

```bash
python3 main.py --help
# Authentication with username:password 
python3 main.py --user <xx>@lieboe.com --password <xx> --server-url https://chat.<domain>/
# Authentication with user-id:auth-token 
python3 main.py --user-id <xx> --auth-token <xx> --server-url https://chat.<domain>/
```

You can find the user ID and the authentication token in the requests headers:
```bash
X-Auth-Token: <xxxx>
X-User-Id: <xxxx>
```

The default dump file is `dump.ndjson` (newline-delimited JSON). Replace `}{` by `}\n{` in the dump file for a more readable stream.

You can then use `jq` to extract useful informations from the dump :
```bash
# Online users
cat dump.ndjson | jq 'select(.user.status!=null and .user.status!="offline")'
# All the usernames
cat dump.ndjson | jq -r 'select(.user.username!=null) | .user.username'
# The files URLs
cat dump.ndjson | jq -r 'select(.files.url!=null) | .files.url'
```

## Notes

- It doesn't prevent rate-limiting errors : `Error, too many requests. Please slow down. You must wait 50 seconds before trying this endpoint again.`.
- There is no error handling.
