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

# Import MCP integration for inter-agent communication
try:
    from app.services.mcp_integration import MCPIntegration
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP integration not available")


class ElizaAgent:
    """Core autonomous agent with 24/7 capabilities and MCP inter-agent communication"""
    
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
        
        # MCP configuration
        self.mcp_enabled = os.getenv('MCP_ENABLED', 'true').lower() == 'true'
        
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
            'mcp_messages_sent': 0,
            'mcp_messages_received': 0,
            'mcp_discoveries_shared': 0,
            'uptime_start': None,
            'last_cycle_time': None,
            'last_cycle_duration': 0,
            'status': 'stopped',
            'mcp_status': 'disabled'
        }
        
        # Activity log
        self.activity_log = []
        self.max_log_size = 100
        
        # Initialize connections
        self._initialize_github()
        self._initialize_ai()
        self._initialize_mcp()
    
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
    
    def _initialize_mcp(self):
        """Initialize MCP integration for inter-agent communication"""
        try:
            if self.mcp_enabled and MCP_AVAILABLE:
                self.mcp = MCPIntegration()
                # Register this agent with MCP backend
                if self.mcp.register_agent():
                    self.metrics['mcp_status'] = 'connected'
                    self.log('success', 'MCP integration initialized - connected to Supabase backend')
                    
                    # List other active agents
                    active_agents = self.mcp.list_active_agents()
                    if active_agents:
                        agent_names = [a.get('agent_id', 'unknown') for a in active_agents]
                        self.log('info', f'Found {len(active_agents)} active Eliza agents: {", ".join(agent_names)}')
                else:
                    self.metrics['mcp_status'] = 'connection_failed'
                    self.log('warning', 'MCP registration failed')
            else:
                self.mcp = None
                self.metrics['mcp_status'] = 'disabled'
                if not self.mcp_enabled:
                    self.log('info', 'MCP integration disabled')
                elif not MCP_AVAILABLE:
                    self.log('warning', 'MCP integration not available')
        except Exception as e:
            self.mcp = None
            self.metrics['mcp_status'] = 'error'
            self.log('error', f'MCP initialization failed: {e}')
    
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
        """Run a complete enhancement cycle with MCP communication"""
        results = {
            'cycle': self.current_cycle,
            'improvements': 0,
            'ecosystem_improvements': 0,
            'tools': 0,
            'utilities': 0,
            'mcp_messages': 0,
            'mcp_discoveries': 0
        }
        
        # Phase 0: MCP - Check messages from other agents
        if self.mcp and self.metrics['mcp_status'] == 'connected':
            self.log('info', 'Phase 0: Checking MCP messages')
            self._process_mcp_messages()
        
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
        
        # Phase 3.5: MCP - Share tool discoveries with other agents
        if self.mcp and self.metrics['mcp_status'] == 'connected' and tools:
            self.log('info', 'Phase 3.5: Sharing discoveries via MCP')
            for tool in tools[:3]:  # Share top 3 tools
                if self.mcp.share_discovery('tool', tool):
                    results['mcp_discoveries'] += 1
                    self.metrics['mcp_discoveries_shared'] += 1
        
        # Phase 4: Build utilities
        self.log('info', 'Phase 4: Utility creation')
        utilities = self._build_utilities(tools[:2])
        results['utilities'] = len(utilities)
        self.metrics['utilities_built'] += len(utilities)
        
        # Phase 4.5: MCP - Get shared discoveries from other agents
        if self.mcp and self.metrics['mcp_status'] == 'connected':
            self.log('info', 'Phase 4.5: Getting shared discoveries from MCP')
            shared_discoveries = self.mcp.get_shared_discoveries()
            if shared_discoveries:
                self.log('info', f'Received {len(shared_discoveries)} discoveries from other agents')
                results['mcp_discoveries'] += len(shared_discoveries)
        
        # Phase 5: Generate report
        self._generate_cycle_report(results)
        
        # Phase 6: MCP - Broadcast status
        if self.mcp and self.metrics['mcp_status'] == 'connected':
            self.log('info', 'Phase 6: Broadcasting status via MCP')
            status_data = {
                'cycle': self.current_cycle,
                'metrics': self.metrics,
                'results': results
            }
            self.mcp.broadcast_status(status_data)
        
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
    
    def _process_mcp_messages(self):
        """Process messages from other Eliza agents via MCP"""
        try:
            messages = self.mcp.receive_messages()
            
            for msg in messages:
                from_agent = msg.get('from_agent', 'unknown')
                msg_type = msg.get('message_type', 'unknown')
                content = msg.get('content', {})
                
                self.log('info', f'MCP message from {from_agent}: {msg_type}')
                self.metrics['mcp_messages_received'] += 1
                
                # Handle different message types
                if msg_type == 'assistance_request':
                    self._handle_assistance_request(from_agent, content)
                elif msg_type == 'discovery_share':
                    self._handle_discovery_share(from_agent, content)
                elif msg_type == 'task_coordination':
                    self._handle_task_coordination(from_agent, content)
                elif msg_type == 'status_update':
                    self.log('info', f'Status from {from_agent}: {content.get("status", "unknown")}')
                
        except Exception as e:
            self.log('error', f'MCP message processing error: {e}')
    
    def _handle_assistance_request(self, from_agent, content):
        """Handle assistance request from another agent"""
        try:
            request_type = content.get('type', 'unknown')
            self.log('info', f'Assistance request from {from_agent}: {request_type}')
            
            # Send acknowledgment
            response = {
                'type': 'assistance_response',
                'request_type': request_type,
                'status': 'acknowledged',
                'message': f'Eliza-xmrtnet received your request'
            }
            self.mcp.send_message(from_agent, 'assistance_response', response)
            self.metrics['mcp_messages_sent'] += 1
            
        except Exception as e:
            self.log('error', f'Assistance handling error: {e}')
    
    def _handle_discovery_share(self, from_agent, content):
        """Handle discovery shared by another agent"""
        try:
            discovery_type = content.get('type', 'unknown')
            self.log('info', f'Discovery from {from_agent}: {discovery_type}')
            
            # Log the discovery for potential use
            discovery_data = content.get('data', {})
            self.log('info', f'Shared discovery data: {str(discovery_data)[:100]}...')
            
        except Exception as e:
            self.log('error', f'Discovery handling error: {e}')
    
    def _handle_task_coordination(self, from_agent, content):
        """Handle task coordination request"""
        try:
            task_type = content.get('task_type', 'unknown')
            self.log('info', f'Task coordination from {from_agent}: {task_type}')
            
            # Send acknowledgment
            response = {
                'type': 'task_response',
                'task_type': task_type,
                'status': 'accepted',
                'message': f'Eliza-xmrtnet will participate in {task_type}'
            }
            self.mcp.send_message(from_agent, 'task_response', response)
            self.metrics['mcp_messages_sent'] += 1
            
        except Exception as e:
            self.log('error', f'Task coordination error: {e}')
    
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

