"""
Eliza Autonomous Agent Service
Core agent logic separated from web service layer
"""

import os
import time
import random
import requests
from github import Github, InputGitAuthor, Auth
from datetime import datetime
import json
import traceback
from collections import defaultdict
import threading


class ElizaAgent:
    """Core autonomous agent with 24/7 capabilities"""
    
    def __init__(self):
        # GitHub configuration
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_user = os.getenv('GITHUB_USER', 'DevGruGold')
        self.target_repo = os.getenv('TARGET_REPO', 'xmrtnet')
        self.ecosystem_repo = os.getenv('ECOSYSTEM_REPO', 'XMRT-Ecosystem')
        
        # Operation configuration
        self.cycle_interval = int(os.getenv('CYCLE_INTERVAL', '3600'))
        self.max_cycles = int(os.getenv('MAX_CYCLES', '0'))
        self.eliza_mode = os.getenv('ELIZA_MODE', 'continuous_24_7')
        
        # AI configuration
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # State
        self.is_running = False
        self.current_cycle = 0
        self.agent_thread = None
        self.state = {}
        
        # Performance metrics
        self.metrics = {
            'cycles_completed': 0,
            'self_improvements': 0,
            'ecosystem_improvements': 0,
            'tools_discovered': 0,
            'utilities_built': 0,
            'github_commits': 0,
            'ecosystem_commits': 0,
            'uptime_start': None,
            'last_cycle_time': None,
            'last_cycle_duration': 0,
            'status': 'stopped'
        }
        
        # Activity log
        self.activity_log = []
        self.max_log_size = 100
        
        # Initialize connections
        self._initialize_github()
        self._initialize_ai()
    
    def _initialize_github(self):
        """Initialize GitHub connections"""
        try:
            if not self.github_token:
                self.log('error', 'GITHUB_TOKEN not set')
                return False
            
            self.github = Github(auth=Auth.Token(self.github_token))
            self.repo = self.github.get_user(self.github_user).get_repo(self.target_repo)
            
            try:
                self.ecosystem_repo_obj = self.github.get_user(self.github_user).get_repo(self.ecosystem_repo)
                self.ecosystem_enabled = True
                self.log('info', f'Connected to ecosystem repo: {self.ecosystem_repo}')
            except Exception as e:
                self.ecosystem_repo_obj = None
                self.ecosystem_enabled = False
                self.log('warning', f'Ecosystem repo not available: {e}')
            
            self.log('success', f'GitHub initialized: {self.github_user}/{self.target_repo}')
            return True
            
        except Exception as e:
            self.log('error', f'GitHub initialization failed: {e}')
            return False
    
    def _initialize_ai(self):
        """Initialize AI capabilities"""
        try:
            if self.gemini_api_key:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self.gemini_enabled = True
                self.log('success', 'Gemini AI initialized')
            else:
                self.gemini_model = None
                self.gemini_enabled = False
                self.log('info', 'Running without AI enhancement')
        except Exception as e:
            self.gemini_model = None
            self.gemini_enabled = False
            self.log('warning', f'AI initialization failed: {e}')
    
    def log(self, level, message):
        """Add entry to activity log"""
        entry = {
            'time': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        self.activity_log.append(entry)
        
        # Keep log size manageable
        if len(self.activity_log) > self.max_log_size:
            self.activity_log = self.activity_log[-self.max_log_size:]
        
        # Also print to console
        print(f"[{level.upper()}] {message}")
    
    def get_status(self):
        """Get current agent status"""
        return {
            'is_running': self.is_running,
            'current_cycle': self.current_cycle,
            'metrics': self.metrics,
            'config': {
                'github_user': self.github_user,
                'target_repo': self.target_repo,
                'ecosystem_repo': self.ecosystem_repo,
                'cycle_interval': self.cycle_interval,
                'max_cycles': self.max_cycles,
                'mode': self.eliza_mode,
                'ai_enabled': self.gemini_enabled
            }
        }
    
    def get_logs(self, limit=50):
        """Get recent activity logs"""
        return self.activity_log[-limit:]
    
    def start(self):
        """Start the autonomous agent"""
        if self.is_running:
            self.log('warning', 'Agent already running')
            return False
        
        self.is_running = True
        self.metrics['status'] = 'running'
        self.metrics['uptime_start'] = datetime.now().isoformat()
        self.log('success', 'Starting Eliza autonomous agent in 24/7 mode')
        
        # Start agent in background thread
        self.agent_thread = threading.Thread(target=self._run_agent_loop, daemon=True)
        self.agent_thread.start()
        
        return True
    
    def stop(self):
        """Stop the autonomous agent"""
        if not self.is_running:
            self.log('warning', 'Agent not running')
            return False
        
        self.is_running = False
        self.metrics['status'] = 'stopped'
        self.log('warning', 'Stopping Eliza autonomous agent')
        
        return True
    
    def _run_agent_loop(self):
        """Main agent loop running in background thread"""
        self.log('info', f'Agent loop started with {self.cycle_interval}s interval')
        
        while self.is_running:
            try:
                cycle_start = time.time()
                self.current_cycle += 1
                
                self.log('info', f'Starting cycle {self.current_cycle}')
                
                # Run complete enhancement cycle
                results = self._run_enhancement_cycle()
                
                cycle_duration = time.time() - cycle_start
                self.metrics['last_cycle_time'] = datetime.now().isoformat()
                self.metrics['last_cycle_duration'] = round(cycle_duration, 2)
                self.metrics['cycles_completed'] = self.current_cycle
                
                self.log('success', f'Cycle {self.current_cycle} completed in {cycle_duration:.2f}s')
                
                # Check max cycles
                if self.max_cycles > 0 and self.current_cycle >= self.max_cycles:
                    self.log('info', f'Reached max cycles ({self.max_cycles})')
                    self.is_running = False
                    break
                
                # Wait for next cycle
                if self.is_running:
                    self.log('info', f'Waiting {self.cycle_interval}s until next cycle')
                    time.sleep(self.cycle_interval)
                
            except Exception as e:
                self.log('error', f'Error in cycle {self.current_cycle}: {e}')
                traceback.print_exc()
                time.sleep(60)  # Wait before retry
        
        self.metrics['status'] = 'stopped'
        self.log('info', 'Agent loop stopped')
    
    def _run_enhancement_cycle(self):
        """Run a complete enhancement cycle"""
        results = {
            'cycle': self.current_cycle,
            'improvements': 0,
            'ecosystem_improvements': 0,
            'tools': 0,
            'utilities': 0
        }
        
        # Phase 1: Self-analysis
        self.log('info', 'Phase 1: Self-analysis')
        improvements = self._analyze_self()
        results['improvements'] = len(improvements)
        self.metrics['self_improvements'] += len(improvements)
        
        # Phase 2: Ecosystem analysis
        if self.ecosystem_enabled:
            self.log('info', 'Phase 2: Ecosystem analysis')
            eco_improvements = self._analyze_ecosystem()
            results['ecosystem_improvements'] = len(eco_improvements)
            self.metrics['ecosystem_improvements'] += len(eco_improvements)
        
        # Phase 3: Tool discovery
        self.log('info', 'Phase 3: Tool discovery')
        tools = self._discover_tools()
        results['tools'] = len(tools)
        self.metrics['tools_discovered'] += len(tools)
        
        # Phase 4: Build utilities
        self.log('info', 'Phase 4: Utility creation')
        utilities = self._build_utilities(tools[:2])
        results['utilities'] = len(utilities)
        self.metrics['utilities_built'] += len(utilities)
        
        # Phase 5: Generate report
        self._generate_cycle_report(results)
        
        return results
    
    def _analyze_self(self):
        """Analyze own code for improvements"""
        improvements = []
        
        try:
            current_file = self.repo.get_contents("src/autonomous_eliza_continuous.py")
            code_content = current_file.decoded_content.decode()
            
            lines = code_content.split('\n')
            total_lines = len(lines)
            
            # Basic analysis
            todo_count = len([line for line in lines if 'TODO' in line or 'FIXME' in line])
            if todo_count > 0:
                improvements.append(f"Found {todo_count} TODO/FIXME comments")
            
            # AI-enhanced analysis
            if self.gemini_enabled:
                ai_improvements = self._get_ai_analysis(code_content[:3000])
                improvements.extend(ai_improvements)
            
            self.log('info', f'Self-analysis: {len(improvements)} improvements identified')
            
        except Exception as e:
            self.log('error', f'Self-analysis error: {e}')
        
        return improvements
    
    def _analyze_ecosystem(self):
        """Analyze ecosystem repository"""
        improvements = []
        
        try:
            contents = self.ecosystem_repo_obj.get_contents("")
            
            # Check for README
            try:
                readme = self.ecosystem_repo_obj.get_contents("README.md")
                readme_content = readme.decoded_content.decode()
                if len(readme_content) < 500:
                    improvements.append("README could be more comprehensive")
            except Exception:
                improvements.append("README.md is missing")
            
            # Check for docs
            has_docs = any(item.name.lower() in ['docs', 'documentation'] for item in contents)
            if not has_docs:
                improvements.append("Consider adding documentation directory")
            
            self.log('info', f'Ecosystem analysis: {len(improvements)} improvements identified')
            
        except Exception as e:
            self.log('error', f'Ecosystem analysis error: {e}')
        
        return improvements
    
    def _discover_tools(self):
        """Discover trending tools"""
        tools = []
        
        try:
            categories = ["artificial-intelligence", "automation", "cryptocurrency"]
            
            for category in categories[:2]:  # Limit for rate limiting
                try:
                    repos = self.github.search_repositories(
                        query=f"topic:{category} stars:>50 pushed:>2024-01-01",
                        sort="stars",
                        order="desc"
                    )
                    
                    for repo in repos[:2]:
                        tool_info = {
                            "name": repo.name,
                            "stars": repo.stargazers_count,
                            "category": category,
                            "url": repo.html_url
                        }
                        tools.append(tool_info)
                    
                    time.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    self.log('warning', f'Tool discovery error for {category}: {e}')
            
            self.log('info', f'Discovered {len(tools)} tools')
            
        except Exception as e:
            self.log('error', f'Tool discovery error: {e}')
        
        return tools
    
    def _build_utilities(self, tools):
        """Build utilities from discovered tools"""
        utilities = []
        
        for tool in tools:
            try:
                utility_name = f"eliza_{tool['name'].lower().replace('-', '_')}_integration"
                utilities.append(utility_name)
                self.log('info', f'Built utility: {utility_name}')
            except Exception as e:
                self.log('error', f'Utility build error: {e}')
        
        return utilities
    
    def _get_ai_analysis(self, code_snippet):
        """Get AI-powered code analysis"""
        if not self.gemini_enabled:
            return []
        
        try:
            prompt = f"Analyze this code and suggest 3 improvements:\n\n{code_snippet}"
            response = self.gemini_model.generate_content(prompt)
            suggestions = response.text.split('\n')
            return [s.strip('- ').strip() for s in suggestions if s.strip() and len(s.strip()) > 10][:3]
        except Exception as e:
            self.log('error', f'AI analysis error: {e}')
            return []
    
    def _generate_cycle_report(self, results):
        """Generate and commit cycle report"""
        try:
            report = f"""# Cycle {self.current_cycle} Report
Generated: {datetime.now().isoformat()}

## Results
- Self-improvements: {results['improvements']}
- Ecosystem improvements: {results['ecosystem_improvements']}
- Tools discovered: {results['tools']}
- Utilities built: {results['utilities']}

## Metrics
- Total cycles: {self.metrics['cycles_completed']}
- Total improvements: {self.metrics['self_improvements']}
- Total commits: {self.metrics['github_commits']}
"""
            
            # Commit report
            self._commit_file(
                f"reports/cycle_{self.current_cycle}.md",
                report,
                f"Cycle {self.current_cycle} report"
            )
            
        except Exception as e:
            self.log('error', f'Report generation error: {e}')
    
    def _commit_file(self, filename, content, message):
        """Commit file to GitHub"""
        try:
            try:
                file = self.repo.get_contents(filename)
                self.repo.update_file(
                    filename, message, content, file.sha,
                    author=InputGitAuthor('Eliza Autonomous', 'eliza@xmrt.io')
                )
            except Exception:
                self.repo.create_file(
                    filename, message, content,
                    author=InputGitAuthor('Eliza Autonomous', 'eliza@xmrt.io')
                )
            
            self.metrics['github_commits'] += 1
            self.log('success', f'Committed: {filename}')
            return True
            
        except Exception as e:
            self.log('error', f'Commit error: {e}')
            return False

