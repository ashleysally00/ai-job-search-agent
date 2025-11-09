#!/usr/bin/env python3
"""
AI Job Search Agent
Greenhouse + Lever job board crawler with URL verification output.
Two-tier filtering:
- STRICT: AI content / UX / prompt / design roles
- WIDE:   product-, UX-, or solutions-adjacent AI roles (not deep ML infra)
"""

import requests
import json
from datetime import datetime
from typing import List, Dict
import time
import random


class JobSearchAgent:
    def __init__(self):
        self.results = []
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/92.0.902.55',
        ]

    def _get_headers(self):
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "application/json",
        }

    # ---------- GREENHOUSE ----------
    def search_greenhouse_jobs(self) -> List[Dict]:
        """Fetch Greenhouse job boards using the official Job Board API"""
        jobs = []
        print("Searching Greenhouse job boards...")

        greenhouse_companies = [
            "anthropic",
            "figma",
            "canva",
            "discord",
            "airtable",
            "reddit",
            "facebook",
        ]

        for company in greenhouse_companies:
            try:
                url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
                headers = self._get_headers()
                headers["Referer"] = f"https://boards.greenhouse.io/{company}"

                print(f"\nFetching: {url}")
                response = requests.get(url, headers=headers, timeout=10)
                print(f"Requested: {url}")
                print(f"Final URL: {response.url}")
                print(f"Status: {response.status_code}")

                if response.status_code != 200:
                    print(response.text[:300])
                    continue

                data = response.json()
                job_posts = data.get("jobs", [])
                print(f"   {company}: API working, {len(job_posts)} jobs listed")

                found_count = 0
                for job in job_posts:
                    title = job.get("title", "")
                    if not title:
                        continue

                    strict = self._matches_strict(title)
                    wide = self._matches_wide(title)

                    if not strict and not wide:
                        continue

                    location = (job.get("location") or {}).get("name", "Not specified")

                    jobs.append(
                        {
                            "title": title,
                            "company": company.title(),
                            "location": location,
                            "url": job.get("absolute_url", ""),
                            "source": "Greenhouse",
                            "posted_date": job.get("updated_at", "Recent"),
                            "tier": "strict" if strict else "wide",
                        }
                    )
                    found_count += 1

                if found_count:
                    print(f"   Found {found_count} matching/wide-net jobs")
                time.sleep(1.5)

            except Exception as e:
                print(f"Error with Greenhouse/{company}: {e}")
        return jobs

    # ---------- LEVER ----------
    def search_lever_jobs(self) -> List[Dict]:
        """Fetch Lever job boards using Lever postings API"""
        jobs = []
        print("\nSearching Lever job boards...")

        lever_companies = ["shopify", "grammarly", "retool", "plaid"]

        for company in lever_companies:
            try:
                url = f"https://api.lever.co/v0/postings/{company}?mode=json"
                headers = self._get_headers()
                headers.pop("Accept", None)

                print(f"\nFetching: {url}")
                response = requests.get(url, headers=headers, timeout=10)
                print(f"Requested: {url}")
                print(f"Final URL: {response.url}")
                print(f"Status: {response.status_code}")

                if response.status_code != 200:
                    print(response.text[:300])
                    continue

                job_posts = response.json()
                print(f"   {company}: API working, {len(job_posts)} jobs listed")

                found_count = 0
                for job in job_posts:
                    title = job.get("text", "")
                    if not title:
                        continue

                    strict = self._matches_strict(title)
                    wide = self._matches_wide(title)

                    if not strict and not wide:
                        continue

                    categories = job.get("categories", {}) or {}
                    location = categories.get("location", "Not specified")
                    commitment = categories.get("commitment", "")

                    jobs.append(
                        {
                            "title": title,
                            "company": company.title(),
                            "location": location,
                            "type": commitment,
                            "url": job.get("hostedUrl", ""),
                            "source": "Lever",
                            "posted_date": job.get("createdAt", "Recent"),
                            "tier": "strict" if strict else "wide",
                        }
                    )
                    found_count += 1

                if found_count:
                    print(f"   Found {found_count} matching/wide-net jobs")
                time.sleep(1.5)
            except Exception as e:
                print(f"Error with Lever/{company}: {e}")
        return jobs

    # ---------- FILTERS ----------
    def _matches_strict(self, title: str) -> bool:
        """Strict filter: AI content / UX / prompt / design roles."""
        title_lower = title.lower()
        ai_keywords = ["ai", "artificial intelligence", "ml", "machine learning", "llm", "gpt", "claude"]
        function_keywords = [
            "prompt engineer",
            "content engineer",
            "ai content",
            "ai writer",
            "content strategist",
            "ux",
            "user experience",
            "product design",
            "interaction design",
        ]
        for kw in function_keywords:
            if kw in title_lower:
                if kw in ["ux", "user experience", "product design", "interaction design"]:
                    return any(ai in title_lower for ai in ai_keywords)
                return True
        return False

    def _matches_wide(self, title: str) -> bool:
        """Wide-net filter: AI-related but product/UX/solutions adjacent, not deep ML infra."""
        title_lower = title.lower()

        wide_keywords = [
            "ai",
            "artificial intelligence",
            "ml",
            "machine learning",
            "llm",
            "gpt",
            "genai",
            "generative ai",
        ]
        if not any(kw in title_lower for kw in wide_keywords):
            return False

        role_anchor_keywords = [
            "product",
            "manager",
            "pm",
            "platform",
            "tooling",
            "integration",
            "integrations",
            "solutions",
            "solution",
            "architect",
            "architecture",
            "experience",
            "developer",
            "content",
            "documentation",
            "design",
            "designer",
            "ux",
            "collaboration",
            "human-ai",
        ]
        if not any(anchor in title_lower for anchor in role_anchor_keywords):
            return False

        exclude_terms = [
            "fraud",
            "ads",
            "ranking",
            "relevance",
            "recommendation",
            "infra",
            "infrastructure",
            "risk",
            "security",
            "platform security",
            "ml feature platform",
            "feature platform",
            "acceleration",
        ]
        if any(ex in title_lower for ex in exclude_terms):
            return False

        return True

    def _format_date(self, date_val) -> str:
        """Prettify ISO or millisecond timestamps."""
        if date_val in (None, ""):
            return ""
        if isinstance(date_val, (int, float)):
            try:
                dt = datetime.fromtimestamp(date_val / 1000.0)
                return dt.strftime("%b %d, %Y").replace(" 0", " ")
            except Exception:
                return str(date_val)
        if isinstance(date_val, str):
            if date_val == "Recent":
                return "Recent"
            try:
                ds = date_val.replace("Z", "+00:00")
                dt = datetime.fromisoformat(ds)
                return dt.strftime("%b %d, %Y").replace(" 0", " ")
            except Exception:
                return date_val
        return str(date_val)

    # ---------- MAIN RUN ----------
    def search_all(self) -> List[Dict]:
        print("Starting AI Job Search Agent...\n")
        all_jobs = self.search_greenhouse_jobs() + self.search_lever_jobs()

        seen = {}
        for job in all_jobs:
            key = (job["title"].lower(), job["company"].lower())
            existing = seen.get(key)
            if not existing:
                seen[key] = job
            elif existing.get("tier") == "wide" and job.get("tier") == "strict":
                seen[key] = job

        self.results = list(seen.values())
        return self.results

    def generate_report(self, jobs: List[Dict]) -> str:
        strict_jobs = [j for j in jobs if j.get("tier") == "strict"]
        wide_jobs = [j for j in jobs if j.get("tier") == "wide"]

        lines = [
            "=" * 80,
            f"AI JOB SEARCH RESULTS - {datetime.now().strftime('%B %d, %Y')}",
            "=" * 80,
            f"\nFound {len(strict_jobs)} strict-match roles and {len(wide_jobs)} wider-net roles ({len(jobs)} total).\n",
        ]

        lines.append("\nSTRICT MATCH ROLES (AI content / UX / prompt / design)")
        lines.append("-" * 80)
        lines.extend(self._render_jobs(strict_jobs))

        lines.append("\nOTHER AI ROLES (WIDER NET)")
        lines.append("-" * 80)
        lines.extend(self._render_jobs(wide_jobs))

        lines.append("=" * 80)
        lines.append(f"Total: {len(jobs)} jobs found")
        lines.append("=" * 80)
        return "\n".join(lines)

    def _render_jobs(self, job_list: List[Dict]) -> List[str]:
        if not job_list:
            return ["No roles found.\n"]
        grouped = {}
        for j in job_list:
            grouped.setdefault(j["company"], []).append(j)

        lines = []
        for company, lst in sorted(grouped.items()):
            lines.append(f"\n{'─'*80}\n{company.upper()}\n{'─'*80}")
            for j in lst:
                lines.append(f"• {j['title']}")
                lines.append(f"   Location: {j['location']}")
                if j.get("type"):
                    lines.append(f"   Type: {j['type']}")
                formatted_date = self._format_date(j.get("posted_date"))
                if formatted_date:
                    lines.append(f"   Posted: {formatted_date}")
                lines.append(f"   Apply: {j['url']}")
                lines.append("")
        return lines

    def save_results(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        jsf, txtf = f"job_results_{ts}.json", f"job_results_{ts}.txt"
        with open(jsf, "w") as jf:
            json.dump({"jobs": self.results}, jf, indent=2)
        with open(txtf, "w") as tf:
            tf.write(self.generate_report(self.results))
        print(f"\nResults saved to {jsf}\nReport saved to {txtf}")


def main():
        agent = JobSearchAgent()
        jobs = agent.search_all()
        print("\n" + agent.generate_report(jobs))
        agent.save_results()
        if jobs:
            print(f"\nQuick Summary: {len(jobs)} jobs across {len(set(j['company'] for j in jobs))} companies")
        else:
            print("\nRun this daily to catch new postings!")


if __name__ == "__main__":
    main()

