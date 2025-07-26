#!/usr/bin/env python3
"""
ELIZA HEALTH CHECK - RENDER CRON JOB
"""

import os
import logging
from datetime import datetime
from github import Github, Auth
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

def health_check():
    try:
        github_token = os.getenv('GITHUB_TOKEN')
        repo_name = os.getenv('GITHUB_REPO', 'DevGruGold/xmrtnet')
        
        auth = Auth.Token(github_token)
        github = Github(auth=auth)
        repo = github.get_repo(repo_name)
        
        # Check recent activity
        recent_commits = list(repo.get_commits())[:3]
        
        health_summary = f"""# 🔍 ELIZA HEALTH CHECK REPORT
**Check Time:** {datetime.now().isoformat()}
**Performed By:** Render Cron Job
**Status:** MONITORING ✅

## System Status
- GitHub API: ✅ Connected
- Repository Access: ✅ Active
- Recent Commits: {len(recent_commits)} found
- Health Monitoring: ✅ Operational

## Recent Activity
{chr(10).join([f"- {commit.commit.message[:50]}..." for commit in recent_commits])}

---
*Automated health check from Render cron job*
"""
        
        try:
            health_file = repo.get_contents("ELIZA_HEALTH_CHECK.md")
            repo.update_file(
                "ELIZA_HEALTH_CHECK.md",
                "🔍 Automated Health Check Update",
                health_summary,
                health_file.sha
            )
        except:
            repo.create_file(
                "ELIZA_HEALTH_CHECK.md",
                "🔍 Initialize Health Check Monitoring",
                health_summary
            )
        
        logging.info("✅ Health check completed successfully")
        
    except Exception as e:
        logging.error(f"❌ Health check failed: {e}")

if __name__ == "__main__":
    health_check()
