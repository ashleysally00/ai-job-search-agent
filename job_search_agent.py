#!/usr/bin/env python3
"""
AI Job Search Agent
Searches multiple job boards for AI-related positions and aggregates results.
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict
import time

class JobSearchAgent:
    def __init__(self):
        self.job_titles = [
            "AI UX Designer",
            "AI UX Researcher", 
            "Content Engineer",
            "Prompt Engineer",
            "AI Content Writer",
            "AI Content Strategist"
        ]
        self.results = []
        
    def search_greenhouse_jobs(self) -> List[Dict]:
        """Search companies using Greenhouse for jobs"""
        jobs = []
        print("🔍 Searching Greenhouse job boards...")
        
        greenhouse_companies = [
            "anthropic", "openai", "deepmind", "notion", "figma",
            "canva", "discord", "ramp", "airtable", "reddit", "coinbase"
        ]
        
        for company in greenhouse_companies:
            try:
                url = f"https://boards.greenhouse.io/{company}/jobs"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_posts = soup.find_all('div', class_='opening')
                    
                    for job in job_posts:
                        title_elem = job.find('a')
                        if title_elem:
                            title = title_elem.text.strip()
                            link = title_elem.get('href', '')
                            
                            if self._matches_criteria(title):
                                location_elem = job.find('span', class_='location')
                                location = location_elem.text.strip() if location_elem else "Not specified"
                                
                                jobs.append({
                                    'title': title,
                                    'company': company.title(),
                                    'location': location,
                                    'url': f"https://boards.greenhouse.io{link}" if not link.startswith('http') else link,
                                    'source': 'Greenhouse',
                                    'posted_date': 'Recent'
                                })
                                
                time.sleep(1)
                
            except Exception as e:
                print(f"   Error searching {company}: {str(e)}")
                continue
                
        return jobs
    
    def search_lever_jobs(self) -> List[Dict]:
        """Search companies using Lever for jobs"""
        jobs = []
        print("🔍 Searching Lever job boards...")
        
        lever_companies = [
            "netflix", "shopify", "stripe", "grammarly", 
            "retool", "vercel", "plaid", "affirm"
        ]
        
        for company in lever_companies:
            try:
                url = f"https://jobs.lever.co/{company}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_posts = soup.find_all('div', class_='posting')
                    
                    for job in job_posts:
                        title_elem = job.find('h5')
                        link_elem = job.find('a', class_='posting-title')
                        
                        if title_elem and link_elem:
                            title = title_elem.text.strip()
                            
                            if self._matches_criteria(title):
                                location_elem = job.find('span', class_='sort-by-location')
                                location = location_elem.text.strip() if location_elem else "Not specified"
                                
                                commitment = job.find('span', class_='sort-by-commitment')
                                job_type = commitment.text.strip() if commitment else ""
                                
                                jobs.append({
                                    'title': title,
                                    'company': company.title(),
                                    'location': location,
                                    'type': job_type,
                                    'url': link_elem.get('href', ''),
                                    'source': 'Lever',
                                    'posted_date': 'Recent'
                                })
                                
                time.sleep(1)
                
            except Exception as e:
                print(f"   Error searching {company}: {str(e)}")
                continue
                
        return jobs
    
    def _matches_criteria(self, title: str) -> bool:
        """Check if job title matches our search criteria"""
        title_lower = title.lower()
        
        keywords = [
            'prompt engineer', 'content engineer', 'ai content',
            'ai writer', 'content strategist', 'ux', 'user experience', 
            'product design', 'interaction design'
        ]
        
        ai_keywords = ['ai', 'artificial intelligence', 'ml', 'machine learning', 'llm', 'gpt']
        
        for keyword in keywords:
            if keyword in title_lower:
                if keyword in ['ux', 'user experience', 'product design', 'interaction design']:
                    if any(ai_term in title_lower for ai_term in ai_keywords):
                        return True
                else:
                    return True
                    
        return False
    
    def search_all(self) -> List[Dict]:
        """Run all job searches"""
        print("🤖 Starting AI Job Search Agent...\n")
        
        all_jobs = []
        all_jobs.extend(self.search_greenhouse_jobs())
        all_jobs.extend(self.search_lever_jobs())
        
        seen = set()
        unique_jobs = []
        
        for job in all_jobs:
            key = (job['title'].lower(), job['company'].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        self.results = unique_jobs
        return unique_jobs
    
    def generate_report(self, jobs: List[Dict]) -> str:
        """Generate a formatted report of found jobs"""
        report = []
        report.append("=" * 80)
        report.append(f"AI JOB SEARCH RESULTS - {datetime.now().strftime('%B %d, %Y')}")
        report.append("=" * 80)
        report.append(f"\n✨ Found {len(jobs)} matching positions!\n")
        
        if not jobs:
            report.append("No jobs found matching your criteria. Try again later.\n")
            return "\n".join(report)
        
        jobs_by_company = {}
        for job in jobs:
            company = job['company']
            if company not in jobs_by_company:
                jobs_by_company[company] = []
            jobs_by_company[company].append(job)
        
        for company, company_jobs in sorted(jobs_by_company.items()):
            report.append(f"\n{'─' * 80}")
            report.append(f"🏢 {company.upper()}")
            report.append(f"{'─' * 80}\n")
            
            for job in company_jobs:
                report.append(f"📌 {job['title']}")
                report.append(f"   📍 Location: {job['location']}")
                if 'type' in job and job['type']:
                    report.append(f"   💼 Type: {job['type']}")
                report.append(f"   🔗 Apply: {job['url']}")
                report.append(f"   📅 Posted: {job['posted_date']}")
                report.append("")
        
        report.append("=" * 80)
        report.append(f"Total: {len(jobs)} jobs found")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_results(self, filename: str = None):
        """Save results to JSON and text files"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'job_results_{timestamp}'
        
        json_file = f'{filename}.json'
        with open(json_file, 'w') as f:
            json.dump({
                'search_date': datetime.now().isoformat(),
                'total_jobs': len(self.results),
                'jobs': self.results
            }, f, indent=2)
        
        print(f"💾 Results saved to {json_file}")
        
        txt_file = f'{filename}.txt'
        report = self.generate_report(self.results)
        with open(txt_file, 'w') as f:
            f.write(report)
        
        print(f"📄 Report saved to {txt_file}")
        
        return json_file, txt_file


def main():
    """Main function to run the job search"""
    agent = JobSearchAgent()
    jobs = agent.search_all()
    print("\n" + agent.generate_report(jobs))
    agent.save_results()
    
    if jobs:
        print(f"\n🎯 Quick Summary:")
        print(f"   • {len(jobs)} jobs found")
        print(f"   • {len(set(j['company'] for j in jobs))} companies")
        print(f"   • Next steps: Review the results and start applying!")
    else:
        print("\n💡 Tip: Run this daily to catch new postings early!")


if __name__ == "__main__":
    main()
