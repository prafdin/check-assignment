import sys, os, json
from typing import AnyStr


if len(sys.argv) > 1 and 'debug' in sys.argv[1]:

    for key in sorted(os.environ):
        print(f"{key}={os.environ[key]}")
    exit(0)

def calc_ssh_repo_url() -> str:
    if ("HEAD_REPOSITORY" not in os.environ) or not os.environ["HEAD_REPOSITORY"]:
        raise RuntimeError("HEAD_REPOSITORY env variable is emtpy")
    repo = os.environ["HEAD_REPOSITORY"]

    ssh_repo_link = f"git@github.com:{repo}.git"
    return ssh_repo_link

out_parameters = {}

if __name__ == '__main__':
    out_parameters["repo_url"] = calc_ssh_repo_url()

    params_file = sys.argv[1]
    with open(params_file) as f:
        params = json.load(f)

    if "ASSIGNEE_LOGIN" not in os.environ or not os.environ["ASSIGNEE_LOGIN"]:
        raise RuntimeError("ASSIGNEE_LOGIN env variable is emtpy")
    assignee = os.environ["ASSIGNEE_LOGIN"]

    user = next((u for u in params["users"] if u["login"] == assignee), None)

    if user is None:
        out_parameters["authorized"] = False
    else:
        out_parameters["authorized"] = True
        out_parameters["id"] = user["id"]
        out_parameters["login"] = user["login"]
        out_parameters["app"] = user["app"]

    out_parameters["proxy"] = params["proxy"]
    out_parameters["sa_login"] = params["sa_login"]
    out_parameters["sa_mail"] = params["sa_mail"]

    output_str = "\n".join(f"{k}={str(v).lower()}" for k, v in out_parameters.items())
    print(output_str)