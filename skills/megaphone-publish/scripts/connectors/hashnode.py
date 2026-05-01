"""Hashnode connector.

Auth: Personal Access Token (Settings → Developer).
Posting: GraphQL mutation `publishPost` against https://gql.hashnode.com.

Credential schema: { "token": "xxx", "publication_id": "yyy" }

The draft frontmatter should provide `title` (required by Hashnode). Tags are
optional but supported."""

from __future__ import annotations

from typing import Optional

from connectors._base import PostResult
from _http import HttpError, post_json

API = "https://gql.hashnode.com"

MUTATION = """
mutation PublishPost($input: PublishPostInput!) {
  publishPost(input: $input) {
    post { id slug url }
  }
}
"""

QUERY_PUBS = """
query Me { me { publications(first: 10) { edges { node { id title } } } } }
"""


def publish(body: str, credentials: dict, overrides: Optional[dict] = None) -> PostResult:
    token = credentials.get("token")
    pub_id = credentials.get("publication_id")
    if not token or not pub_id:
        return PostResult(
            ok=False,
            error_type="auth_error",
            error_message="Missing token or publication_id.",
        )

    overrides = overrides or {}
    title = overrides.get("title") or "Untitled"
    tags = overrides.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    input_payload = {
        "title": title,
        "publicationId": pub_id,
        "contentMarkdown": body,
    }
    if tags:
        input_payload["tags"] = [{"slug": t.lower(), "name": t} for t in tags[:5]]

    try:
        resp = post_json(
            API,
            {"query": MUTATION, "variables": {"input": input_payload}},
            headers={"Authorization": token},
        )
    except HttpError as e:
        if e.status in (401, 403):
            return PostResult(ok=False, error_type="auth_error", error_message=e.body[:300])
        return PostResult(ok=False, error_type="unknown", error_message=e.body[:300])

    if resp.get("errors"):
        msg = resp["errors"][0].get("message", "Hashnode error")
        return PostResult(ok=False, error_type="bad_body", error_message=msg)

    post = resp.get("data", {}).get("publishPost", {}).get("post", {})
    return PostResult(ok=True, url=post.get("url"), raw=resp)


def connect(prompt) -> dict:
    print()
    print("Hashnode setup")
    print("--------------")
    print("1. Open https://hashnode.com/settings/developer")
    print("2. Generate a Personal Access Token.")
    print("3. Paste it below; we'll then look up your publication ID for you.\n")
    token = prompt("Hashnode token: ", secret=True)
    if not token:
        raise RuntimeError("Token is required.")
    try:
        resp = post_json(API, {"query": QUERY_PUBS}, headers={"Authorization": token})
    except HttpError as e:
        raise RuntimeError(f"Hashnode rejected the token: {e.body[:200]}") from e
    edges = resp.get("data", {}).get("me", {}).get("publications", {}).get("edges", [])
    if not edges:
        raise RuntimeError("No publications found on this account; create one on hashnode.com first.")
    print("Publications on your account:")
    for i, edge in enumerate(edges, 1):
        node = edge.get("node", {})
        print(f"  [{i}] {node.get('title','(untitled)')}  ({node.get('id')})")
    pick = prompt("Pick the number to use as the default publication: ")
    try:
        idx = int(pick) - 1
        pub_id = edges[idx]["node"]["id"]
    except (ValueError, IndexError):
        raise RuntimeError("Invalid choice.")
    return {"token": token, "publication_id": pub_id}
