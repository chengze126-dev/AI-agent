"""
GitHub Issue Triager using LangGraph.

Analyzes a GitHub issue and produces: severity label, category,
reproduction steps summary, and suggested assignee type.

Usage:
    python agent.py --title "Login fails on mobile Safari" --body "When I try..."
    python agent.py --issue-url https://github.com/owner/repo/issues/123
"""

import argparse
import os
import json

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

TRIAGE_PROMPT = """You are a GitHub issue triager. Analyze the issue and return a JSON object with:
{
  "severity": "critical|high|medium|low",
  "category": "bug|feature|documentation|question|performance|security",
  "priority_score": 1-10,
  "labels": ["list", "of", "suggested", "labels"],
  "summary": "one sentence summary",
  "reproduction_clear": true/false,
  "assignee_type": "frontend|backend|devops|documentation|security|any",
  "needs_more_info": true/false,
  "triage_notes": "2-3 sentences of triager notes"
}
Return only valid JSON, no markdown."""


def triage_issue(title: str, body: str, labels: list[str] = None) -> dict:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    issue_text = f"Title: {title}\n\nBody:\n{body}"
    if labels:
        issue_text += f"\n\nExisting labels: {', '.join(labels)}"

    messages = [
        SystemMessage(content=TRIAGE_PROMPT),
        HumanMessage(content=issue_text),
    ]

    response = llm.invoke(messages)
    return json.loads(response.content)


def fetch_github_issue(url: str) -> tuple[str, str, list]:
    """Fetch issue details from GitHub API."""
    import re
    import requests

    match = re.match(r"https://github.com/([^/]+)/([^/]+)/issues/(\d+)", url)
    if not match:
        raise ValueError(f"Invalid GitHub issue URL: {url}")

    owner, repo, issue_num = match.groups()
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}"
    headers = {}
    if token := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {token}"

    r = requests.get(api_url, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data["title"], data.get("body", ""), [l["name"] for l in data.get("labels", [])]


def main():
    parser = argparse.ArgumentParser(description="GitHub Issue Triager")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--issue-url", help="GitHub issue URL")
    group.add_argument("--title", help="Issue title (use with --body)")
    parser.add_argument("--body", default="", help="Issue body text")
    args = parser.parse_args()

    if args.issue_url:
        print(f"\n🔍 Fetching issue from GitHub...")
        title, body, labels = fetch_github_issue(args.issue_url)
    else:
        title, body, labels = args.title, args.body, []

    print(f"\n🏷️  Triaging: {title}\n")
    result = triage_issue(title, body, labels)

    severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(result["severity"], "⚪")

    print("=" * 60)
    print("📋 TRIAGE REPORT")
    print("=" * 60)
    print(f"{severity_emoji} Severity: {result['severity'].upper()} (Priority: {result['priority_score']}/10)")
    print(f"📁 Category: {result['category']}")
    print(f"👤 Assignee: {result['assignee_type']} team")
    print(f"🏷️  Labels: {', '.join(result['labels'])}")
    print(f"📝 Summary: {result['summary']}")
    print(f"❓ Needs more info: {'Yes' if result['needs_more_info'] else 'No'}")
    print(f"🔍 Reproduction clear: {'Yes' if result['reproduction_clear'] else 'No'}")
    print(f"\n💭 Notes: {result['triage_notes']}")


if __name__ == "__main__":
    main()
