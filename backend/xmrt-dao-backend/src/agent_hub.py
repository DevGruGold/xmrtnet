"""
Agent Hub for XMRT DAO - Async Messaging and Communication System
Handles inter-agent communication, message routing, and coordination
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from queue import Queue, Empty
from dataclasses import dataclass, asdict
from flask import Flask, Blueprint, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
import redis
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentMessage:
    """Standard message format for inter-agent communication"""
    id: str
    sender: str
    receiver: str
    content: str
    message_type: str
    timestamp: str
    priority: int = 1  # 1=low, 2=medium, 3=high
    requires_response: bool = False
    metadata: Dict[str, Any] = None

    def to_dict(self):
        return asdict(self)

class MessageQueue:
    """Enhanced message queue with Redis support for scalability"""
    
    def __init__(self, use_redis=False):
        self.use_redis = use_redis
        self.local_queue = Queue()
        
        if use_redis:
            try:
                self.redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Connected to Redis for message queue")
            except Exception as e:
                logger.warning(f"Redis connection failed, falling back to local queue: {e}")
                self.use_redis = False
                self.redis_client = None
        else:
            self.redis_client = None
    
    def put(self, message: AgentMessage):
        """Add message to queue"""
        if self.use_redis and self.redis_client:
            try:
                # Use Redis list for message queue
                queue_key = f"agent_queue:{message.receiver}"
                self.redis_client.lpush(queue_key, json.dumps(message.to_dict()))
                logger.info(f"Message queued for {message.receiver} via Redis")
            except Exception as e:
                logger.error(f"Redis queue error, falling back to local: {e}")
                self.local_queue.put(message)
        else:
            self.local_queue.put(message)
    
    def get(self, agent_name: str, timeout=1) -> Optional[AgentMessage]:
        """Get message from queue for specific agent"""
        if self.use_redis and self.redis_client:
            try:
                queue_key = f"agent_queue:{agent_name}"
                message_data = self.redis_client.brpop(queue_key, timeout=timeout)
                if message_data:
                    message_dict = json.loads(message_data[1])
                    return AgentMessage(**message_dict)
                return None
            except Exception as e:
                logger.error(f"Redis get error: {e}")
                return None
        else:
            try:
                message = self.local_queue.get(timeout=timeout)
                if message.receiver == agent_name:
                    return message
                else:
                    # Put back if not for this agent
                    self.local_queue.put(message)
                    return None
            except Empty:
                return None
    
    def get_all_for_agent(self, agent_name: str) -> List[AgentMessage]:
        """Get all pending messages for an agent"""
        messages = []
        if self.use_redis and self.redis_client:
            try:
                queue_key = f"agent_queue:{agent_name}"
                while True:
                    message_data = self.redis_client.rpop(queue_key)
                    if not message_data:
                        break
                    message_dict = json.loads(message_data)
                    messages.append(AgentMessage(**message_dict))
            except Exception as e:
                logger.error(f"Redis get_all error: {e}")
        else:
            # For local queue, we need to check all messages
            temp_messages = []
            while not self.local_queue.empty():
                try:
                    message = self.local_queue.get_nowait()
                    if message.receiver == agent_name:
                        messages.append(message)
                    else:
                        temp_messages.append(message)
                except Empty:
                    break
            
            # Put back messages not for this agent
            for msg in temp_messages:
                self.local_queue.put(msg)
        
        return messages

class AgentRegistry:
    """Registry of active agents and their capabilities"""
    
    def __init__(self):
        self.agents = {}
        self.agent_capabilities = {}
        self.agent_status = {}
    
    def register_agent(self, agent_name: str, capabilities: List[str], endpoint: str = None):
        """Register an agent with its capabilities"""
        self.agents[agent_name] = {
            'name': agent_name,
            'capabilities': capabilities,
            'endpoint': endpoint,
            'registered_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat()
        }
        self.agent_capabilities[agent_name] = capabilities
        self.agent_status[agent_name] = 'active'
        logger.info(f"Agent {agent_name} registered with capabilities: {capabilities}")
    
    def update_agent_status(self, agent_name: str, status: str):
        """Update agent status"""
        if agent_name in self.agents:
            self.agent_status[agent_name] = status
            self.agents[agent_name]['last_seen'] = datetime.now().isoformat()
    
    def get_agents_by_capability(self, capability: str) -> List[str]:
        """Get agents that have a specific capability"""
        return [name for name, caps in self.agent_capabilities.items() 
                if capability in caps and self.agent_status.get(name) == 'active']
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all registered agents"""
        return self.agents

class AgentHub:
    """Central hub for agent communication and coordination"""
    
    def __init__(self, use_redis=False):
        self.message_queue = MessageQueue(use_redis)
        self.agent_registry = AgentRegistry()
        self.scheduler = BackgroundScheduler()
        self.message_history = []
        self.running = False
        
        # Register default agents
        self._register_default_agents()
        
        # Start scheduler
        self.scheduler.start()
        logger.info("Agent Hub initialized")
    
    def _register_default_agents(self):
        """Register default XMRT DAO agents"""
        default_agents = [
            {
                'name': 'eliza',
                'capabilities': ['natural_language', 'governance_analysis', 'treasury_advice', 'cross_chain_guidance'],
                'endpoint': 'http://localhost:5000/eliza'
            },
            {
                'name': 'treasury',
                'capabilities': ['treasury_management', 'portfolio_optimization', 'risk_assessment', 'financial_analysis'],
                'endpoint': 'http://localhost:5000/treasury'
            },
            {
                'name': 'reputation',
                'capabilities': ['reputation_tracking', 'community_metrics', 'voting_analysis', 'member_scoring'],
                'endpoint': 'http://localhost:5000/reputation'
            },
            {
                'name': 'cross_chain',
                'capabilities': ['bridge_operations', 'multi_chain_monitoring', 'fee_optimization', 'liquidity_management'],
                'endpoint': 'http://localhost:5001'
            },
            {
                'name': 'zk_privacy',
                'capabilities': ['zero_knowledge_proofs', 'private_voting', 'verifiable_computation', 'privacy_analysis'],
                'endpoint': 'http://localhost:5002'
            }
        ]
        
        for agent in default_agents:
            self.agent_registry.register_agent(
                agent['name'], 
                agent['capabilities'], 
                agent['endpoint']
            )
    
    def send_message(self, sender: str, receiver: str, content: str, 
                    message_type: str = 'general', priority: int = 1, 
                    requires_response: bool = False, metadata: Dict = None) -> str:
        """Send a message between agents"""
        message_id = f"{sender}_{receiver}_{int(time.time() * 1000)}"
        
        message = AgentMessage(
            id=message_id,
            sender=sender,
            receiver=receiver,
            content=content,
            message_type=message_type,
            timestamp=datetime.now().isoformat(),
            priority=priority,
            requires_response=requires_response,
            metadata=metadata or {}
        )
        
        # Add to queue
        self.message_queue.put(message)
        
        # Add to history
        self.message_history.append(message.to_dict())
        
        logger.info(f"Message sent from {sender} to {receiver}: {message_type}")
        return message_id
    
    def get_messages(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get all pending messages for an agent"""
        messages = self.message_queue.get_all_for_agent(agent_name)
        return [msg.to_dict() for msg in messages]
    
    def route_message_by_capability(self, sender: str, capability: str, 
                                  content: str, message_type: str = 'capability_request') -> List[str]:
        """Route message to agents with specific capability"""
        capable_agents = self.agent_registry.get_agents_by_capability(capability)
        message_ids = []
        
        for agent in capable_agents:
            if agent != sender:  # Don't send to self
                message_id = self.send_message(
                    sender=sender,
                    receiver=agent,
                    content=content,
                    message_type=message_type,
                    metadata={'capability_requested': capability}
                )
                message_ids.append(message_id)
        
        return message_ids
    
    def broadcast_message(self, sender: str, content: str, 
                         message_type: str = 'broadcast', exclude: List[str] = None) -> List[str]:
        """Broadcast message to all active agents"""
        exclude = exclude or []
        all_agents = self.agent_registry.get_all_agents()
        message_ids = []
        
        for agent_name in all_agents:
            if agent_name != sender and agent_name not in exclude:
                if self.agent_registry.agent_status.get(agent_name) == 'active':
                    message_id = self.send_message(
                        sender=sender,
                        receiver=agent_name,
                        content=content,
                        message_type=message_type
                    )
                    message_ids.append(message_id)
        
        return message_ids
    
    def add_scheduled_task(self, agent_name: str, task_function, interval_seconds: int):
        """Add a scheduled task for an agent"""
        job_id = f"{agent_name}_scheduled_task_{int(time.time())}"
        self.scheduler.add_job(
            task_function,
            'interval',
            seconds=interval_seconds,
            id=job_id,
            args=[agent_name]
        )
        logger.info(f"Scheduled task added for {agent_name} every {interval_seconds} seconds")
        return job_id
    
    def get_agent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent agent communication logs"""
        return self.message_history[-limit:]
    
    def get_hub_status(self) -> Dict[str, Any]:
        """Get hub status and statistics"""
        return {
            'status': 'active',
            'total_agents': len(self.agent_registry.agents),
            'active_agents': len([a for a in self.agent_registry.agent_status.values() if a == 'active']),
            'total_messages': len(self.message_history),
            'queue_type': 'redis' if self.message_queue.use_redis else 'local',
            'scheduler_running': self.scheduler.running,
            'agents': self.agent_registry.get_all_agents()
        }

# Global hub instance
hub = AgentHub(use_redis=os.getenv('USE_REDIS', 'false').lower() == 'true')

# Flask Blueprint for API endpoints
agent_hub_bp = Blueprint('agent_hub', __name__)

@agent_hub_bp.route('/send-message', methods=['POST'])
def send_message():
    """API endpoint to send a message between agents"""
    try:
        data = request.get_json()
        
        required_fields = ['sender', 'receiver', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        message_id = hub.send_message(
            sender=data['sender'],
            receiver=data['receiver'],
            content=data['content'],
            message_type=data.get('message_type', 'general'),
            priority=data.get('priority', 1),
            requires_response=data.get('requires_response', False),
            metadata=data.get('metadata', {})
        )
        
        return jsonify({
            'success': True,
            'message_id': message_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_hub_bp.route('/get-messages/<agent_name>', methods=['GET'])
def get_messages(agent_name):
    """API endpoint to get messages for an agent"""
    try:
        messages = hub.get_messages(agent_name)
        return jsonify({
            'success': True,
            'messages': messages,
            'count': len(messages)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_hub_bp.route('/route-by-capability', methods=['POST'])
def route_by_capability():
    """API endpoint to route message by capability"""
    try:
        data = request.get_json()
        
        required_fields = ['sender', 'capability', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        message_ids = hub.route_message_by_capability(
            sender=data['sender'],
            capability=data['capability'],
            content=data['content'],
            message_type=data.get('message_type', 'capability_request')
        )
        
        return jsonify({
            'success': True,
            'message_ids': message_ids,
            'agents_contacted': len(message_ids)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_hub_bp.route('/broadcast', methods=['POST'])
def broadcast():
    """API endpoint to broadcast message to all agents"""
    try:
        data = request.get_json()
        
        required_fields = ['sender', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        message_ids = hub.broadcast_message(
            sender=data['sender'],
            content=data['content'],
            message_type=data.get('message_type', 'broadcast'),
            exclude=data.get('exclude', [])
        )
        
        return jsonify({
            'success': True,
            'message_ids': message_ids,
            'agents_contacted': len(message_ids)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_hub_bp.route('/register-agent', methods=['POST'])
def register_agent():
    """API endpoint to register a new agent"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'capabilities']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        hub.agent_registry.register_agent(
            agent_name=data['name'],
            capabilities=data['capabilities'],
            endpoint=data.get('endpoint')
        )
        
        return jsonify({
            'success': True,
            'message': f"Agent {data['name']} registered successfully"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_hub_bp.route('/agent-logs', methods=['GET'])
def get_agent_logs():
    """API endpoint to get agent communication logs"""
    try:
        limit = request.args.get('limit', 100, type=int)
        logs = hub.get_agent_logs(limit)
        
        return jsonify({
            'success': True,
            'logs': logs,
            'count': len(logs)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_hub_bp.route('/status', methods=['GET'])
def get_hub_status():
    """API endpoint to get hub status"""
    try:
        status = hub.get_hub_status()
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agent_hub_bp.route('/agents', methods=['GET'])
def get_all_agents():
    """API endpoint to get all registered agents"""
    try:
        agents = hub.agent_registry.get_all_agents()
        return jsonify({
            'success': True,
            'agents': agents
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Utility functions for agents to use
def check_inbox(agent_name: str):
    """Utility function for agents to check their inbox"""
    return hub.get_messages(agent_name)

def send_agent_message(sender: str, receiver: str, content: str, **kwargs):
    """Utility function for agents to send messages"""
    return hub.send_message(sender, receiver, content, **kwargs)

def request_capability(sender: str, capability: str, content: str):
    """Utility function to request a capability from other agents"""
    return hub.route_message_by_capability(sender, capability, content)

