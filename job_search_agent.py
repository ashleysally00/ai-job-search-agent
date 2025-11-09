#!/usr/bin/env python3
"""
AI Job Search Agent
Greenhouse + Lever job board crawler with URL verification output.
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
            "Accept": "application/json"
        }

    # ---------- GREENHOUSE ----------
    def search_greenhouse_jobs(self) -> List[Dict]:
        """Test and fetch Greenhouse job boards using the official Job Board API"""
        jobs = []
        print("Searching Greenhouse job boards...")

        greenhouse_companies = [
            "anthropic", "figma", "canva",
            "discord", "airtable", "reddit", "facebook"
        ]

        for company in greenhouse_companies:
            try:
                url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
                headers = self._get_headers()
                headers["Referer"] = f"https://boards.greenhouse.io/{company}"

                # Debug: print every attempt
                print(f"\nFetching: {url}")
                response = requests.get(url, headers=headers, timeout=10)
                print(f"Requested: {url}")
                print(f"Final URL: {response.url}")
                print(f"Status: {response.status_code}")

                # Keep visible verification output
                if response.status_code != 200:
                    print(response.text[:300])
                    continue

                data = response.json()
                job_posts = data.get("jobs", [])
                print(f"   ✅ {company}: API working, {len(job_posts)} jobs listed")

                found_count = 0
                for job in job_posts:
                    title = job.get("title", "")
                    if self._matches_criteria(title):
                        location = (job.get("location") or {}).get("name", "Not specified")
                        jobs.append({
                            "title": title,
                            "company": company.title(),
                            "location": location,
                            "url": job.get("absolute_url", ""),
                            "source": "Greenhouse",
                            "posted_date": job.get("updated_at", "Recent"),
                        })
                        found_count += 1
                if found_count:
                    print(f"   Found {found_count} matching jobs")
                time.sleep(1.5)

            except Exception as e:
                print(f"Error with Greenhouse/{company}: {e}")
        return jobs

    # ---------- LEVER ----------
    def search_lever_jobs(self) -> List[Dict]:
        """Test and fetch Lever job boards using Lever postings API"""
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
                print(f"   ✅ {company}: API working, {len(job_posts)} jobs listed")

                found_count = 0
                for job in job_posts:
                    title = job.get("text", "")
                    if self._matches_criteria(title):
                        categories = job.get("categories", {}) or {}
                        jobs.append({
                            "title": title,
                            "company": company.title(),
                            "location": categories.get("location", "Not specified"),
                            "type": categories.get("commitment", ""),
                            "url": job.get("hostedUrl", ""),
                            "source": "Lever",
                            "posted_date": job.get("createdAt", "Recent"),
                        })
                        found_count += 1
                if found_count:
                    print(f"   Found {found_count} matching jobs")
                time.sleep(1.5)
            except Exception as e:
                print(f"Error with Lever/{company}: {e}")
        return jobs

    # ---------- FILTER ----------
    def _matches_criteria(self, title: str) -> bool:
        title_lower = title.lower()
        ai_keywords = ["ai", "artificial intelligence", "ml", "machine learning", "llm", "gpt"]
        function_keywords = [
            "prompt engineer", "content engineer", "ai content",
            "ai writer", "content strategist", "ux", "user experience",
            "product design", "interaction design"
        ]
        for kw in function_keywords:
            if kw in title_lower:
                if kw in ["ux", "user experience", "product design", "interaction design"]:
                    return any(ai in title_lower for ai in ai_keywords)
                return True
        return False

    # ---------- MAIN RUN ----------
    def search_all(self) -> List[Dict]:
        print("Starting AI Job Search Agent...\n")
        all_jobs = self.search_greenhouse_jobs() + self.search_lever_jobs()
        seen = set()
        unique = []
        for job in all_jobs:
            key = (job["title"].lower(), job["company"].lower())
            if key not in seen:
                seen.add(key)
                unique.append(job)
        self.results = unique
        return unique

    def generate_report(self, jobs: List[Dict]) -> str:
        lines = [
            "=" * 80,
            f"AI JOB SEARCH RESULTS - {datetime.now().strftime('%B %d, %Y')}",
            "=" * 80,
            f"\nFound {len(jobs)} matching positions!\n",
        ]
        if not jobs:
            lines.append("No jobs found matching your criteria.\n")
            return "\n".join(lines)

        grouped = {}
        for j in jobs:
            grouped.setdefault(j["company"], []).append(j)

        for company, lst in sorted(grouped.items()):
            lines.append(f"\n{'─'*80}\n{company.upper()}\n{'─'*80}")
            for j in lst:
                lines.append(f"• {j['title']}")
                lines.append(f"   Location: {j['location']}")
                if j.get("type"): lines.append(f"   Type: {j['type']}")
                lines.append(f"   Apply: {j['url']}")
                lines.append("")
        lines.append("="*80)
        lines.append(f"Total: {len(jobs)} jobs found")
        lines.append("="*80)
        return "\n".join(lines)

    def save_results(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        jsf, txtf = f"job_results_{ts}.json", f"job_results_{ts}.txt"
        with open(jsf, "w") as jf: json.dump({"jobs": self.results}, jf, indent=2)
        with open(txtf, "w") as tf: tf.write(self.generate_report(self.results))
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
