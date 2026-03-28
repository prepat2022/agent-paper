import argparse
import os
import smtplib
import urllib.parse
import urllib.request
from urllib.error import URLError
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Iterable, List

ARXIV_API = "https://export.arxiv.org/api/query"
DEFAULT_QUERY = (
    'all:"embodied intelligence" OR all:"embodied AI" OR all:"robot learning" '
    'OR all:"vision-language-action" OR all:"humanoid robot" OR all:"robotics foundation model"'
)


@dataclass
class Paper:
    title: str
    authors: str
    published: datetime
    summary: str
    link: str


def _parse_datetime(dt_str: str) -> datetime:
    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")


def _fetch_arxiv_xml(days: int, max_results: int) -> bytes:
    _ = days
    params = {
        "search_query": DEFAULT_QUERY,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_API}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read()


def fetch_recent_papers(days: int = 7, max_results: int = 40) -> List[Paper]:
    cutoff = datetime.utcnow() - timedelta(days=days)
    try:
        xml_data = _fetch_arxiv_xml(days=days, max_results=max_results)
    except URLError:
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_data)
    papers: List[Paper] = []

    for entry in root.findall("atom:entry", ns):
        published_text = entry.findtext("atom:published", default="", namespaces=ns)
        if not published_text:
            continue

        published = _parse_datetime(published_text)
        if published < cutoff:
            continue

        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip().replace("\n", " ")
        summary = " ".join((entry.findtext("atom:summary", default="", namespaces=ns) or "").split())
        link = entry.findtext("atom:id", default="", namespaces=ns)
        authors = ", ".join(
            (a.findtext("atom:name", default="", namespaces=ns) or "")
            for a in entry.findall("atom:author", ns)
        )

        papers.append(Paper(title=title, authors=authors, published=published, summary=summary, link=link))

    return papers


def _format_papers(papers: Iterable[Paper], limit: int) -> str:
    lines = []
    for idx, p in enumerate(list(papers)[:limit], start=1):
        lines.append(
            f"{idx}. {p.title}\n"
            f"   作者: {p.authors}\n"
            f"   发布时间(UTC): {p.published.strftime('%Y-%m-%d %H:%M')}\n"
            f"   链接: {p.link}\n"
            f"   摘要: {p.summary[:450]}...\n"
        )
    return "\n".join(lines)


def build_email_content(papers: List[Paper], days: int, limit: int) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    header = (
        f"具身智能热点论文周报\n"
        f"生成时间: {now}\n"
        f"统计窗口: 最近 {days} 天\n"
        f"论文数量: {len(papers)}（展示前 {min(limit, len(papers))} 篇）\n\n"
    )
    if not papers:
        return header + "本周期未检索到符合条件的新论文。"
    return header + _format_papers(papers, limit)


def send_email(subject: str, body: str) -> None:
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    mail_from = os.getenv("MAIL_FROM", smtp_user)
    mail_to = os.getenv("MAIL_TO", "510948205@qq.com")

    required = [smtp_host, smtp_user, smtp_password, mail_from, mail_to]
    if not all(required):
        raise ValueError("SMTP/邮件环境变量未完整配置。")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr(("Agent Paper", mail_from))
    msg["To"] = mail_to

    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(mail_from, [mail_to], msg.as_string())


def run_once(days: int = 7) -> None:
    max_papers = int(os.getenv("MAX_PAPERS", "20"))
    papers = fetch_recent_papers(days=days, max_results=max(40, max_papers * 2))
    subject = f"[Agent-Paper] 最近{days}天具身智能热点论文 {datetime.now().strftime('%Y-%m-%d')}"
    body = build_email_content(papers, days=days, limit=max_papers)
    send_email(subject, body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embodied intelligence paper digest sender")
    parser.add_argument("--once", action="store_true", help="run one-time fetch + send")
    parser.add_argument("--days", type=int, default=7, help="paper window in days")
    parser.add_argument("--preview", action="store_true", help="print digest without sending email")
    args = parser.parse_args()

    if args.preview:
        papers = fetch_recent_papers(days=args.days, max_results=20)
        print(build_email_content(papers, args.days, 10))
    else:
        run_once(days=args.days)
