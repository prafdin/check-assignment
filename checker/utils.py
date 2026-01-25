import tempfile
import pygit2
from bs4 import BeautifulSoup
from typing import Any, Dict


class CICommit:
    def __init__(self, repo_ssh_url: str, branch: str, config: Dict[str, Any]):
        assert repo_ssh_url.startswith("git") is True
        self.repo_ssh_url = repo_ssh_url
        self.branch = branch
        self.config = config
        self.tmpdir = tempfile.TemporaryDirectory()
        self.callbacks = pygit2.RemoteCallbacks(
            credentials=pygit2.KeypairFromAgent("git")
        )
        self.repo = pygit2.clone_repository(self.repo_ssh_url, self.tmpdir.name, callbacks=self.callbacks, checkout_branch=self.branch)
        self.branch_ref = f"refs/heads/{self.branch}"
        self.repo.checkout(self.branch_ref)
        author = pygit2.Signature(self.config["sa_login"], self.config["sa_mail"])
        committer = pygit2.Signature(self.config["sa_login"], self.config["sa_mail"])
        tree = self.repo.index.write_tree()
        parent = self.repo.head.target
        commit_message = "ci"
        self.commit_sha = self.repo.create_commit(
            self.branch_ref,
            author,
            committer,
            commit_message,
            tree,
            [parent]
        )

    def push(self):
        remote = self.repo.remotes["origin"]
        remote.push([self.branch_ref], callbacks=self.callbacks)


def extract_deploy_ref(body) -> str:
    soup = BeautifulSoup(body, "html.parser")
    meta_tag = soup.find("meta", attrs={"name": "deployref"})
    if meta_tag:
        return meta_tag.get("content")
    else:
        raise ValueError("Meta tag with 'deployref' name not found on page")
