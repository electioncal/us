import datetime
import os
import parse
import requests
import tomlkit

state_ids = set((922,))
ids_done = set()

# Set to true to do all states. Otherwise only those in state_ids will be run.
recurse = True

debug = False

state_mapping = {"virgin_islands": "u.s._virgin_islands"}

payload = r'field_state_target_id={}&view_name=state_voter_information&view_display_id=block_1&view_args=&view_path=%2Fnode%2F8071&view_base_path=&view_dom_id=7745264f37990f8ab7a323719ae66eadc99f4277bcd52ac6ff1deb105bdf7622&pager_element=0&_drupal_ajax=1&ajax_page_state%5Btheme%5D=eac_subtheme&ajax_page_state%5Btheme_token%5D=&ajax_page_state%5Blibraries%5D=bootstrap%2Fpopover%2Cbootstrap%2Ftooltip%2Ccore%2Fhtml5shiv%2Cgoogle_analytics%2Fgoogle_analytics%2Cresponsive_tables_filter%2Ftablesaw-filter%2Csemantic_connector%2Fgeneral%2Csimple_addthis%2Faddthis%2Csystem%2Fbase%2Cviews%2Fviews.ajax%2Cviews%2Fviews.module'
headers = {
    "Accept-Language": "en-US,en;q=0.5",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Accept": "Accept: application/json, text/javascript, */*; q=0.01",
    "Origin": "https://www.eac.gov",
    "Referer": "https://www.eac.gov/voters/register-and-vote-in-your-state",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}

# value="918">Virginia</option><option
form_option = parse.compile("value=\"{:d}\">{}</option><option")
# value="919" selected="selected">Washington</option><option
selected_option = parse.compile("value=\"{:d}\" selected=\"selected\">{}</option>")
# <p><a href="https://www.sos.wa.gov/elections/" target="_blank">State Election Office Website</a></p>
link = parse.compile("<p><a href=\"{url}\" target=\"_blank\">{text}</a></p>")
link_w_title = parse.compile("<p><a href=\"{url}\" target=\"_blank\" title=\"{title}\">{text}</a></p>")
# </tr><tr><td>Congressional Primary</td>
election_name = parse.compile("</tr><tr><td>{}</td>")
# <td>July 27, 2020 (online/mail)*</td>
election_date = parse.compile("<td>{}</td>")
# <p><em>Updated on February 29, 2020.</em></p>
last_updated = parse.compile("<p><em>Updated on {}.</em></p>")
# <p>*Washington offers same-day registration during early voting through Election Day. See state election office website for more information.</p>
note = parse.compile("<p>{}</p>")

search_order = [form_option, selected_option, link, link_w_title, election_name, election_date, note]

while state_ids:
    state_id = state_ids.pop()
    response = requests.post("https://www.eac.gov/views/ajax?_wrapper_format=drupal_ajax", headers=headers, data=payload.format(state_id))
    new_data = response.json()[2]["data"]
    elections = []
    links = []
    notes = []
    current_election = None
    current_state = None
    for line in new_data.split("\n"):
        if debug:
            print(line)
        for search in search_order:
            result = search.search(line)
            if not result:
                continue
            if search == form_option:
                value, _ = result
                if recurse and value not in ids_done:
                    state_ids.add(value)

            elif search == selected_option:
                value, state_name = result
                print(value, state_name)
                current_state = state_name

                lower_name = state_name.lower().replace(" ", "_")
                if lower_name in state_mapping:
                    lower_name = state_mapping[lower_name]
            elif search == election_name:
                current_election = {"name": result[0]}
                elections.append(current_election)
            elif (search == election_date or
                  # Super hack for North Carolina registration date that is within a <p></p> on a separate line.
                  (current_state == "North Carolina" and search == note and "registration_deadline_str" not in current_election)
                  ):
                if current_state == "Louisiana":
                    span_result = parse.parse("<span>{}</span>", result[0])
                    if span_result:
                        result = span_result
                try:
                    date = datetime.datetime.strptime(result[0], "%B %d, %Y").date()
                except ValueError:
                    date = None
                key = "registration_deadline"
                if key + "_str" in current_election:
                    key = "election_date"

                if date:
                    current_election[key] = date
                current_election[key + "_str"] = result[0]
            elif search in (link, link_w_title):
                links.append({"text": result["text"], "url": result["url"]})
            elif search == note:
                note_stripped = result[0].strip()
                if note_stripped:
                    notes.append(note_stripped)
            break

    print(links)
    print(notes)
    if lower_name == "military_&amp;_overseas":
        continue

    d = os.path.join("states", lower_name)
    elections_fn = os.path.join(d, "elections.toml")
    if os.path.exists(elections_fn):
        with open(elections_fn, "r") as f:
            elections_file = tomlkit.loads(f.read())
    else:
        elections_file = {}

    elections_raw_fn = os.path.join(d, "elections_raw.toml")
    if os.path.exists(elections_raw_fn):
        with open(elections_raw_fn, "r") as f:
            elections_raw_file = tomlkit.loads(f.read())
    else:
        elections_raw_file = tomlkit.document()
        elections_raw_file.add(tomlkit.comment("This holds raw scraped data for reference and shouldn't be hand edited."))

    for election in elections:
        print(election)
        key = election["election_date"].strftime("%Y%m%d")
        if key not in elections_file:
            elections_file[key] = {"original_date": election["election_date"],
                                   "date": election["election_date"],
                                   "name": election["name"]}
            elections_raw_file[key] = {}
        election["notes"] = notes
        elections_raw_file[key]["eac"] = election

    with open(elections_fn, "w") as f:
        f.write(tomlkit.dumps(elections_file))
    with open(elections_raw_fn, "w") as f:
        f.write(tomlkit.dumps(elections_raw_file))
    print()

    ids_done.add(state_id)
