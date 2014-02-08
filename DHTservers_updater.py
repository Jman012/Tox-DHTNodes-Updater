#!/usr/bin/env python3

import urllib.request
import urllib.error
import sys
import time
import threading


def spin(stop: threading.Event):
    if stop is None:
        return

    print("|", end="")
    while True:
        for c in "/-\\|":
            if stop.is_set():
                return

            sys.stdout.write("\b{}".format(c))
            sys.stdout.flush()
            time.sleep(0.1)


def main():
    if len(sys.argv) != 2:
        print("Usage: {} /path/to/DHTservers".format(sys.argv[0]))
        return

    print("Downloading")
    stop = threading.Event()
    spinner = threading.Thread(target=spin, args=(stop,))
    spinner.start()

    try:
        request = urllib.request.urlopen("http://wiki.tox.im/Servers")
        raw_page = request.read().decode("utf-8")
    except urllib.error:
        print("Couldn't download")
        stop.set()
        return

    stop.set()
    sys.stdout.write("\b")
    sys.stdout.flush()
    print("Parsing")

    # Get rid of everything around the table
    raw_table = raw_page[raw_page.find("<table"):raw_page.find("</table")]
    del raw_page

    # Get rid of the `<table border="0" cell...>`,
    # and the `</table>` is already gone
    raw_table = raw_table[raw_table.find("\n"):]

    # Get rid of the header
    raw_table = raw_table[raw_table.find("<tr "):]

    # Separate each section into a list
    raw_server_list = []
    count = raw_table.count("<tr ")
    for i in range(count):
        ipv4 = raw_table[raw_table.find("<td>") + 4:raw_table.find("</td>") - 1]
        raw_table = raw_table[raw_table.find("</td>\n<td>")+5:]
        ipv6 = raw_table[raw_table.find("<td>") + 4:raw_table.find("</td>") - 1]
        raw_table = raw_table[raw_table.find("</td>\n<td>")+5:]
        port = raw_table[raw_table.find("<td>") + 4:raw_table.find("</td>") - 1]
        raw_table = raw_table[raw_table.find("</td>\n<td>")+5:]
        key = raw_table[raw_table.find("<td>") + 4:raw_table.find("</td>") - 1]
        raw_table = raw_table[raw_table.find("</td>\n<td>")+5:]
        name = raw_table[raw_table.find("<td>") + 4:raw_table.find("</td>") - 1]
        raw_table = raw_table[raw_table.find("</td>\n<td>")+5:]
        location = raw_table[raw_table.find("<td>") + 4:raw_table.find("</td>") - 1]
        raw_table = raw_table[raw_table.find("</td>\n<td>")+5:]
        status = raw_table[raw_table.find("<td>") + 4:raw_table.find("</td>") - 1]
        raw_table = raw_table[raw_table.find("</td></tr>")+5:]

        # print(ipv4, ipv6, port, key, name, location, status)
        raw_server_list.append("{} {} {}".format(ipv4, port, key))

    del raw_table

    print("Writing")

    # Write
    with open(sys.argv[1], "w") as DHTservers:
        for line in raw_server_list:
            DHTservers.write(line + "\n")

    print("Success")


if __name__ == "__main__":
    main()

