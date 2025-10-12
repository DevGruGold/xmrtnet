"""
MCP (Model Context Protocol) Integration Service
Enables communication between Eliza agents across repositories
"""

import os
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional


class MCPIntegration:
    """Integration with Supabase MCP for inter-agent communication"""
    
    def __init__(self):
        self.mcp_url = "https://mcp.supabase.com/mcp?project_ref=vawouugtzwmejxqkeqqj"
        self.agent_id = "eliza-xmrtnet"
        self.repository = "xmrtnet"
        self.related_repos = ["xmrtassistant", "XMRT-Ecosystem"]
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Eliza-Agent-xmrtnet/3.0'
        })
    
    def register_agent(self) -> bool:
        """Register this Eliza agent with the MCP backend"""
        try:
            payload = {
                "action": "register_agent",
                "agent_id": self.agent_id,
                "repository": self.repository,
                "capabilities": [
                    "self_improvement",
                    "ecosystem_analysis",
                    "tool_discovery",
                    "utility_creation",
                    "code_analysis"
                ],
                "status": "active",
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(self.mcp_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✓ Registered with MCP backend: {self.agent_id}")
                return True
            else:
                print(f"✗ MCP registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ MCP registration error: {e}")
            return False
    
    def send_message(self, target_agent: str, message_type: str, content: Dict) -> bool:
        """Send a message to another Eliza agent"""
        try:
            payload = {
                "action": "send_message",
                "from_agent": self.agent_id,
                "to_agent": target_agent,
                "message_type": message_type,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(self.mcp_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✓ Message sent to {target_agent}: {message_type}")
                return True
            else:
                print(f"✗ Failed to send message to {target_agent}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Message send error: {e}")
            return False
    
    def receive_messages(self) -> List[Dict]:
        """Receive messages from other Eliza agents"""
        try:
            payload = {
                "action": "get_messages",
                "agent_id": self.agent_id,
                "limit": 50
            }
            
            response = self.session.post(self.mcp_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get('messages', [])
                if messages:
                    print(f"✓ Received {len(messages)} messages from MCP")
                return messages
            else:
                print(f"✗ Failed to receive messages: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"✗ Message receive error: {e}")
            return []
    
    def broadcast_status(self, status: Dict) -> bool:
        """Broadcast status update to all agents"""
        try:
            payload = {
                "action": "broadcast_status",
                "agent_id": self.agent_id,
                "repository": self.repository,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(self.mcp_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✓ Status broadcast successful")
                return True
            else:
                print(f"✗ Status broadcast failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Status broadcast error: {e}")
            return False
    
    def share_discovery(self, discovery_type: str, discovery_data: Dict) -> bool:
        """Share a discovery with other Eliza agents"""
        try:
            payload = {
                "action": "share_discovery",
                "agent_id": self.agent_id,
                "repository": self.repository,
                "discovery_type": discovery_type,
                "data": discovery_data,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(self.mcp_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✓ Discovery shared: {discovery_type}")
                return True
            else:
                print(f"✗ Discovery share failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Discovery share error: {e}")
            return False
    
    def get_shared_discoveries(self, discovery_type: Optional[str] = None) -> List[Dict]:
        """Get discoveries shared by other Eliza agents"""
        try:
            payload = {
                "action": "get_discoveries",
                "agent_id": self.agent_id,
                "discovery_type": discovery_type,
                "limit": 50
            }
            
            response = self.session.post(self.mcp_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                discoveries = data.get('discoveries', [])
                if discoveries:
                    print(f"✓ Retrieved {len(discoveries)} shared discoveries")
                return discoveries
            else:
                print(f"✗ Failed to get discoveries: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"✗ Get discoveries error: {e}")
            return []
    
    def sync_improvements(self, improvements: List[Dict]) -> bool:
        """Sync improvements with other agents"""
        try:
            payload = {
                "action": "sync_improvements",
                "agent_id": self.agent_id,
                "repository": self.repository,
                "improvements": improvements,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(self.mcp_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✓ Improvements synced: {len(improvements)} items")
                return True
            else:
                print(f"✗ Improvements sync failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Improvements sync error: {e}")
            return False
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Get status of another Eliza agent"""
        try:
            payload = {
                "action": "get_agent_status",
                "agent_id": agent_id
            }
            
            response = self.session.post(self.mcp_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('status')
            else:
                print(f"✗ Failed to get agent status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"✗ Get agent status error: {e}")
            return None
    
    def list_active_agents(self) -> List[Dict]:
        """List all active Eliza agents"""
        try:
            payload = {
                "action": "list_agents",
                "status": "active"
            }
            
            response = self.session.post(self.mcp_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                agents = data.get('agents', [])
                print(f"✓ Found {len(agents)} active agents")
                return agents
            else:
                print(f"✗ Failed to list agents: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"✗ List agents error: {e}")
            return []
    
    def coordinate_task(self, task_type: str, task_data: Dict, target_agents: List[str] = None) -> bool:
        """Coordinate a task across multiple Eliza agents"""
        try:
            if target_agents is None:
                target_agents = ["eliza-xmrtassistant", "eliza-ecosystem"]
            
            payload = {
                "action": "coordinate_task",
                "from_agent": self.agent_id,
                "target_agents": target_agents,
                "task_type": task_type,
                "task_data": task_data,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(self.mcp_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✓ Task coordinated: {task_type} with {len(target_agents)} agents")
                return True
            else:
                print(f"✗ Task coordination failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Task coordination error: {e}")
            return False
    
    def request_assistance(self, assistance_type: str, details: Dict) -> Optional[Dict]:
        """Request assistance from other Eliza agents"""
        try:
            payload = {
                "action": "request_assistance",
                "from_agent": self.agent_id,
                "assistance_type": assistance_type,
                "details": details,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(self.mcp_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Assistance requested: {assistance_type}")
                return data
            else:
                print(f"✗ Assistance request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"✗ Assistance request error: {e}")
            return None
    
    def share_learning(self, learning_type: str, learning_data: Dict) -> bool:
        """Share learning/insights with other agents"""
        try:
            payload = {
                "action": "share_learning",
                "agent_id": self.agent_id,
                "repository": self.repository,
                "learning_type": learning_type,
                "data": learning_data,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(self.mcp_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✓ Learning shared: {learning_type}")
                return True
            else:
                print(f"✗ Learning share failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Learning share error: {e}")
            return False
    
    def close(self):
        """Close the MCP session"""
        try:
            self.session.close()
            print("✓ MCP session closed")
        except Exception as e:
            print(f"✗ Error closing MCP session: {e}")

