import re
import os
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm
from urllib.parse import urlparse

root_dir = os.path.join("Test", "Q1")


def write_names(names, file_name):
    # get the names and the last interacted date here and save in a file
    names_csv = "Name | Date of Last Interaction \n"
    names_csv += "\n".join([
        key + " | " + value.strftime("%m/%d/%Y, %H:%M:%S")
        for key, value in names.items()
    ])
    with open(f"Results/{file_name}", "w") as names_last_interaction_out_file:
        names_last_interaction_out_file.write(names_csv)


def write_urls(urls):
    # the domain and the url file handling here
    domain_count_map = {}
    for url in urls:
        domain = urlparse(url).netloc
        if domain:
            domain_count_map[domain] = domain_count_map.get(domain, 0) + 1

    with open("Results/urls.csv", "w") as urlfile:
        urlfile.write("\n".join(urls))

    with open("Results/domains.csv", "w") as urlfile:
        write_str = "\n".join([
            key + " | " + str(value)
            for key, value in domain_count_map.items()
        ])
        urlfile.write(write_str)


def write_words_to_file(file_name, list_to_write):
    headers = list_to_write[0].keys()

    csv_str = "|".join(headers) + "\n"
    for doc in list_to_write:
        csv_str += "|".join(str(doc[header]) for header in headers)
        csv_str += "\n"

    with open(f"Results/{file_name}", "w") as outfile:
        outfile.write(csv_str)


def get_names_and_last_interaction(soup, old_names_list={}):
    # get session div
    names = old_names_list

    sessions = soup.findAll("div", "mplsession")
    for sess in sessions:
        # find the fist ul
        table = sess.find("table")
        rows = table.find_all("tr")
        date = sess.find("h2").text
        try:
            # Nov 05, 2011
            date = re.split(r"Session Start: \w+, ", date)[1]
            date = datetime.strptime(date, "%B %d, %Y")
        except IndexError:
            # April-15-12
            date = date.split("Session Start: ")[1]
            date = datetime.strptime(date, "%B-%d-%y")

        for row in rows:
            time_username = row.find("th").text
            time_username = time_username.replace(u"\xa0", " ")
            try:
                time, username = re.findall(r"(\(.*:.* .[AM|PM]\)) (.*):", time_username)[0]
            except IndexError:
                continue

            time = time[1:-1]
            hour_min, am_pm = time.split(" ")
            hour, min = hour_min.split(":")
            if am_pm == "PM" and int(hour) < 12:
                hour = int(hour) + 12

            time_of_conversation = date.replace(hour=int(hour), minute=int(min))
            if not names.get(username) or names.get(username) < time_of_conversation:
                names[username] = time_of_conversation

    return names


def get_urls(soup, urls=set()):
    sessions = soup.findAll("div", "mplsession")

    for session in sessions:
        found_urls = [atag['href'] for atag in session.find_all("a", href=True)]
        urls.update(set(found_urls))
    return urls


def get_words(soup, names_list, word):

    sessions = soup.findAll("div", "mplsession")
    for sess in sessions:
        # find the fist ul
        table = sess.find("table")
        rows = table.find_all("tr")
        date = sess.find("h2").text
        try:
            # Nov 05, 2011
            date = re.split(r"Session Start: \w+, ", date)[1]
            date = datetime.strptime(date, "%B %d, %Y")
        except IndexError:
            # April-15-12
            date = date.split("Session Start: ")[1]
            date = datetime.strptime(date, "%B-%d-%y")

        for row in rows:
            if word not in row.text:
                continue

            time_username = row.find("th").text
            time_username = time_username.replace(u"\xa0", " ")
            try:
                time, username = re.findall(r"(\(.*:.* .[AM|PM]\)) (.*):", time_username)[0]
            except IndexError:
                continue

            time = time[1:-1]
            hour_min, am_pm = time.split(" ")
            hour, min = hour_min.split(":")
            if am_pm == "PM" and int(hour) < 12:
                hour = int(hour) + 12

            time_of_conversation = date.replace(hour=int(hour), minute=int(min))
            names_list.append({
                "username": username,
                "time_of_conversation": time_of_conversation,
                "text_of_appearence": row.text
            })
    return names_list


def read_html(
    file_path,
    names,
    urls,
    f_word_list,
    n_word_list,
    group_people_list,
    grp_ppl_weed,
):
    with open(file_path, encoding="utf-16") as html_file:
        webpage = html_file.read()

    soup = BeautifulSoup(webpage, "html.parser")
    # names = get_names_and_last_interaction(soup, names)
    # urls = get_urls(soup, urls)
    f_word_names_date_time = get_words(soup, f_word_list, "fuck")
    n_word_names_date_time = get_words(soup, n_word_list, "nigger")

    if "Good Group" in file_path:
        group_people_list = get_names_and_last_interaction(soup, group_people_list)
        grp_ppl_weed = get_words(soup, grp_ppl_weed, "weed")

    return names, urls, f_word_names_date_time, n_word_names_date_time, group_people_list, grp_ppl_weed


def main():
    names = {}
    urls = set()
    f_word_list = []
    n_word_list = []
    group_people_list = {}
    grp_ppl_weed = []

    for root, subdirs, files in tqdm(os.walk(root_dir)):
        if len(subdirs) != 0:
            continue
        
        # we are inside the html files
        for f in files:
            names, urls, f_word_list, n_word_list, group_people_list, grp_ppl_weed = read_html(
                os.path.join(root, f),
                names,
                urls,
                f_word_list,
                n_word_list,
                group_people_list,
                grp_ppl_weed,
            )

    # writing to files

    write_names(names, "names_and_last_interaction.csv")
    write_urls(urls)
    write_words_to_file("Fword.csv", f_word_list)
    write_words_to_file("Nword.csv", n_word_list)

    write_names(group_people_list, "group_list.csv")
    write_words_to_file("WeedGroup.csv", grp_ppl_weed)


main()
