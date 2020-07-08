"""
    Validates all keys in all elections.toml files are valid according to
    the keys in election_schema, plus a few hardcoded values

    It might be that the key is a new key and we've not deciced to what to do
    with it yet. That might be fine.

    Usually its a typo though.

    NOTE: This doesn't check valid hierarchy, only key names.
"""

import  os
import sys
import tomlkit
from election_schema import methods, deadlines

# These keys are not specifed in election_schema, but they are also valid.
all_valid_keys = ["date", "name", "original_date", "results", "sources", ]

# Known invalid keys: These keys are not in-use yet, but we know about them
# And they're fine.
known_invalid_keys = ["in_person_start","mailed_out"]

# We need a flat list of keys.
for method in methods:
    all_valid_keys.append(method)
for deadline in deadlines:
    all_valid_keys.append(deadline)
    for deadline_type in deadlines[deadline]:
        all_valid_keys.append(deadline_type)

for state in sorted(os.listdir("states/")):
    errors = False
    state_fn = os.path.join("states", state, "elections.toml")
    if not os.path.exists(state_fn):
        continue
    with open(state_fn, "r") as f:
        state_elections = dict(tomlkit.loads(f.read()))
    for election in state_elections:
        state_election = dict(state_elections[election])
        for state_election_key in state_election:
            if state_election_key not in all_valid_keys:
                errors = True
                print(f"{state_election_key} is a suspicious key in {state}/elections.toml")
            if state_election_key in deadlines:
                for state_election_event in state_election[state_election_key]:
                    if state_election_event not in all_valid_keys:
                        errors = True
                        print(f"{state_election_event} is a suspicious key in {state}/elections.toml")
    if errors:
        print()
    errors = False


print(f"\nCompare to all valid keys:\n{all_valid_keys}")
if len(known_invalid_keys) > 0:
    print(f"\nAnd known acceptable invalid keys:\n{known_invalid_keys}\n")
