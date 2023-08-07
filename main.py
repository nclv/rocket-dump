#!/usr/bin/env python3

from requests import sessions
from pprint import pprint
from rocketchat_API.rocketchat import RocketChat

import json
import time
import rich_click as click

"""
Setup
    pip3 install rocketchat_API rich-click

https://developer.rocket.chat/reference/api/rest-api/endpoints
https://developer.rocket.chat/reference/api/rest-api/endpoints/core-endpoints/users-endpoints/create-users-token

Find the following in the requests:
X-Auth-Token: xxxx
X-User-Id: xxxx

Doesn't prevent against rate-limiting errors : `Error, too many requests. Please slow down. You must wait 50 seconds before trying this endpoint again.`.
No error handling.

Usage :
    python3 main.py --user bb@lieboe.com --password bb --server-url https://chat.<domain>/
    or
    python3 main.py --user-id xx --auth-token xx --server-url https://chat.<domain>/

    Replace }{ by }\n{ in the dump file
"""

extract_id = lambda json_array: [channel["_id"] for channel in json_array]


@click.command()
@click.option("--user", default=None, help="Username")
@click.option("--password", default=None, help="Password")
@click.option("--user-id", default=None, help="X-User-Id header value")
@click.option("--auth-token", default=None, help="X-Auth-Token header value")
@click.option("--server-url", default="", prompt="Server URL", help="Server URL")
@click.option(
    "--dump-file", default="dump.ndjson", prompt="Dump file name", help="Dump file name"
)
def main(user, password, user_id, auth_token, server_url, dump_file):
    # Append mode
    with open(dump_file, "a") as dump:
        with sessions.Session() as session:
            rocket = RocketChat(
                user=user,
                password=password,
                user_id=user_id,
                auth_token=auth_token,
                server_url=server_url,
                session=session,
            )

            me = rocket.me().json()
            json.dump(me, dump)
            pprint(me)

            public_settings = rocket.settings_public().json()
            json.dump(public_settings, dump)
            pprint(public_settings)

            channels = rocket.channels_list().json()
            json.dump(channels, dump)
            groups = rocket.groups_list().json()
            json.dump(groups, dump)

            users = rocket.users_list().json()
            json.dump(users, dump)
            pprint(users)

            users_id_set = set()

            print("Channels")

            for channel_id in extract_id(channels["channels"] if 'channels' in channels else []):
                counters = rocket.channels_counters(channel_id).json()
                json.dump(counters, dump)
                pprint(f"{channel_id} : {counters}")

                info = rocket.channels_info(channel_id).json()
                json.dump(info, dump)

                members = rocket.channels_members(
                    channel_id, count=counters["members"]
                ).json()
                json.dump(info, dump)
                pprint(members)
                # Prevent rate-limiting
                time.sleep(0.5)

                users_id_set.update(extract_id(members["members"]))

                moderators = rocket.channels_moderators(channel_id).json()
                json.dump(moderators, dump)
                pprint(moderators)

                # {'error': 'Channel does not exists', 'success': False}
                online = rocket.channels_online(f'{{"_id": {channel_id}}}').json()
                json.dump(online, dump)
                pprint(online)

                # {'error': 'unauthorized', 'success': False}
                integrations = rocket.channels_get_integrations(
                    channel_id, count=100
                ).json()
                json.dump(integrations, dump)
                pprint(integrations)

                roles = rocket.channels_roles(channel_id).json()
                json.dump(roles, dump)
                pprint(roles)

                roles = rocket.channels_get_all_user_mentions_by_channel(
                    channel_id, count=counters["members"]
                ).json()
                json.dump(roles, dump)
                pprint(roles)

                history = rocket.channels_history(
                    channel_id, count=counters["msgs"]
                ).json()
                json.dump(history, dump)
                pprint(
                    f"Message count : {len(history['messages'] if 'messages' in history else [])}"
                )

                files = rocket.channels_files(channel_id, count=3000).json()
                json.dump(files, dump)
                pprint(
                    f"Files count : {len(files['files'] if 'files' in files else [])}"
                )

                if "files" in files:
                    files_endpoints = [file["url"] for file in files["files"]]
                    pprint(f"Files : {files_endpoints}")

            print("Groups")

            for group_id in extract_id(groups["groups"] if 'groups' in groups else []):
                info = rocket.groups_info(group_id).json()
                json.dump(info, dump)
                pprint(info)

                members = rocket.groups_members(
                    group_id, count=info["group"]["usersCount"]
                ).json()
                json.dump(info, dump)
                pprint(members)
                # Prevent rate-limiting
                time.sleep(0.5)

                users_id_set.update(extract_id(members["members"]))

                moderators = rocket.groups_moderators(group_id).json()
                json.dump(moderators, dump)
                pprint(moderators)

                roles = rocket.groups_roles(group_id).json()
                json.dump(roles, dump)
                pprint(roles)

                # {'error': 'unauthorized', 'success': False}
                integrations = rocket.groups_get_integrations(
                    group_id, count=100
                ).json()
                json.dump(integrations, dump)
                pprint(integrations)

                history = rocket.groups_history(
                    group_id, count=info["group"]["msgs"]
                ).json()
                json.dump(history, dump)
                pprint(
                    f"Message count : {len(history['messages'] if 'messages' in history else [])}"
                )

                files = rocket.groups_files(group_id, count=3000).json()
                json.dump(files, dump)
                pprint(
                    f"Files count : {len(files['files'] if 'files' in files else [])}"
                )

                if "files" in files:
                    files_endpoints = [file["url"] for file in files["files"]]
                    pprint(f"Files : {files_endpoints}")

            print("Users")

            for user_id in users_id_set:
                info = rocket.users_info(user_id).json()
                json.dump(info, dump)
                pprint(info)
                # Prevent rate-limiting
                time.sleep(6)

                presence = rocket.users_get_presence(user_id).json()
                json.dump(presence, dump)
                pprint(presence)


if __name__ == "__main__":
    main()
