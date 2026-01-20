import tempfile
import pygit2
from bs4 import BeautifulSoup



def push_ci_commit(repo_ssh_url, branch, config):
    assert repo_ssh_url.startswith("git") is True
    callbacks = pygit2.RemoteCallbacks(
        credentials=pygit2.KeypairFromAgent("git")
    )
    with tempfile.TemporaryDirectory() as tmpdirname:
        repo = pygit2.clone_repository(repo_ssh_url, tmpdirname, callbacks=callbacks, checkout_branch=branch)
        branch_ref = f"refs/heads/{branch}"
        repo.checkout(branch_ref)
        author = pygit2.Signature(config["sa_login"], config["sa_mail"])
        committer = pygit2.Signature(config["sa_login"], config["sa_mail"])
        tree = repo.index.write_tree()
        parent = repo.head.target
        commit_message = "ci"
        repo.create_commit(
            branch_ref,
            author,
            committer,
            commit_message,
            tree,
            [parent]
        )
        remote = repo.remotes["origin"]
        remote.push([branch_ref], callbacks=callbacks)

def extract_date(body) -> str:
    soup = BeautifulSoup(body, "html.parser")
    meta_tag = soup.find("meta", attrs={"name": "deploydate"})
    if meta_tag:
        return meta_tag.get("content")
    else:
        raise ValueError("Meta tag with 'deploydate' name not found on page")
