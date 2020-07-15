"""Return twitter accounts for a given state"""
import os
import sys
import tomlkit


def twitter_accounts(state_lower):
    accounts = ""
    states = os.listdir("states/")
    if state_lower in states:
        state_info_fn = os.path.join("states", state_lower, "info.toml")
        with open(state_info_fn, "r") as file:
            state_info = dict(tomlkit.loads(file.read()))
            for key in state_info.keys():
                if str(key).endswith("_twitter"):
                    if type(state_info[key]) == tomlkit.items.String:
                        accounts += f"@{state_info[key]} "
                    elif type(state_info[key]) == tomlkit.items.Array:
                        for account in state_info[key]:
                            if len(account) >= 1:
                                accounts += f"@{account} "
                    else:
                        RuntimeError(f"Cannot process {key}")
        return accounts
    else:
        return f"'{state_lower}' is not valid directory under states."

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(f"\nproper usage: twitter_for new_york")
    else:
        print(f"\n\t{twitter_accounts(sys.argv[1])}\n")

