"""
Treasury Agent for XMRT DAO - Autonomous Treasury Management
Handles portfolio optimization, risk assessment, and financial operations
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Blueprint, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Import agent hub utilities
from agent_hub import check_inbox, send_agent_message, request_capability

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

treasury_bp = Blueprint('treasury', __name__)

class TreasuryAgent:
    """Autonomous Treasury Management Agent"""
    
    def __init__(self):
        self.agent_name = 'treasury'
        self.scheduler = BackgroundScheduler()
        self.memory = {
            'portfolio_data': {},
            'optimization_history': [],
            'risk_assessments': [],
            'recommendations': [],
            'last_rebalance': None
        }
        self.capabilities = [
            'treasury_management',
            'portfolio_optimization', 
            'risk_assessment',
            'financial_analysis'
        ]
        
        # Treasury configuration
        self.config = {
            'rebalance_threshold': 0.05,  # 5% deviation triggers rebalance
            'max_risk_score': 0.7,
            'min_liquidity_ratio': 0.15,
            'optimization_interval': 3600,  # 1 hour
            'check_interval': 300  # 5 minutes
        }
        
        # Start scheduler
        self.scheduler.add_job(
            self.check_inbox_task,
            'interval',
            seconds=15,
            id='treasury_inbox_check'
        )
        
        self.scheduler.add_job(
            self.autonomous_optimization_check,
            'interval',
            seconds=self.config['optimization_interval'],
            id='treasury_optimization'
        )
        
        self.scheduler.start()
        logger.info("Treasury Agent initialized with autonomous scheduling")
    
    def check_inbox_task(self):
        """Scheduled task to check for new messages"""
        try:
            messages = check_inbox(self.agent_name)
            for message in messages:
                self.handle_message(message)
        except Exception as e:
            logger.error(f"Treasury inbox check error: {e}")
    
    def handle_message(self, message: Dict[str, Any]):
        """Handle incoming messages from other agents"""
        try:
            content = message.get('content', '')
            sender = message.get('sender', '')
            message_type = message.get('message_type', 'general')
            
            logger.info(f"Treasury agent received {message_type} from {sender}")
            
            if message_type == 'optimization_request':
                result = self.optimize_portfolio(message.get('metadata', {}))
                self.send_response(sender, result, 'optimization_result')
            
            elif message_type == 'risk_assessment_request':
                result = self.assess_portfolio_risk()
                self.send_response(sender, result, 'risk_assessment_result')
            
            elif message_type == 'rebalance_request':
                result = self.execute_rebalance(message.get('metadata', {}))
                self.send_response(sender, result, 'rebalance_result')
            
            elif message_type == 'treasury_status_request':
                result = self.get_treasury_status()
                self.send_response(sender, result, 'treasury_status_result')
            
            else:
                # General treasury advice
                result = self.provide_treasury_advice(content)
                self.send_response(sender, result, 'treasury_advice')
                
        except Exception as e:
            logger.error(f"Treasury message handling error: {e}")
    
    def send_response(self, receiver: str, content: Any, message_type: str):
        """Send response to another agent"""
        try:
            send_agent_message(
                sender=self.agent_name,
                receiver=receiver,
                content=json.dumps(content) if isinstance(content, dict) else str(content),
                message_type=message_type
            )
        except Exception as e:
            logger.error(f"Treasury response sending error: {e}")
    
    def autonomous_optimization_check(self):
        """Autonomous check for portfolio optimization needs"""
        try:
            logger.info("Treasury agent performing autonomous optimization check")
            
            # Get current portfolio data
            portfolio_data = self.get_current_portfolio()
            
            # Check if optimization is needed
            if self.needs_optimization(portfolio_data):
                logger.info("Portfolio optimization needed, executing autonomous rebalance")
                
                # Notify other agents about optimization
                send_agent_message(
                    sender=self.agent_name,
                    receiver='eliza',
                    content='Autonomous portfolio optimization initiated based on risk thresholds',
                    message_type='autonomous_action_notification'
                )
                
                # Execute optimization
                optimization_result = self.optimize_portfolio()
                
                # Store result in memory
                self.memory['optimization_history'].append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'autonomous',
                    'result': optimization_result
                })
                
                # Notify completion
                send_agent_message(
                    sender=self.agent_name,
                    receiver='eliza',
                    content=f'Autonomous optimization completed: {optimization_result.get("summary", "Success")}',
                    message_type='autonomous_action_completed'
                )
                
        except Exception as e:
            logger.error(f"Autonomous optimization check error: {e}")
    
    def get_current_portfolio(self) -> Dict[str, Any]:
        """Get current portfolio data (simulated for demo)"""
        # In a real system, this would fetch from blockchain/APIs
        base_time = datetime.now()
        return {
            'total_value_usd': 1500000 + (base_time.minute * 1000),
            'allocations': {
                'XMRT': 0.40 + (base_time.second * 0.001),
                'ETH': 0.30 + (base_time.second * 0.0005),
                'USDC': 0.20,
                'BTC': 0.05,
                'Other': 0.05
            },
            'performance_24h': 2.5 + (base_time.second / 60),
            'risk_score': 0.35 + (base_time.second * 0.01),
            'liquidity_ratio': 0.18,
            'last_updated': base_time.isoformat()
        }
    
    def needs_optimization(self, portfolio_data: Dict[str, Any]) -> bool:
        """Check if portfolio needs optimization"""
        try:
            # Check risk score
            if portfolio_data.get('risk_score', 0) > self.config['max_risk_score']:
                return True
            
            # Check liquidity ratio
            if portfolio_data.get('liquidity_ratio', 0) < self.config['min_liquidity_ratio']:
                return True
            
            # Check time since last rebalance
            if self.memory.get('last_rebalance'):
                last_rebalance = datetime.fromisoformat(self.memory['last_rebalance'])
                if datetime.now() - last_rebalance > timedelta(days=7):
                    return True
            
            # Check allocation drift
            allocations = portfolio_data.get('allocations', {})
            target_allocations = {
                'XMRT': 0.45,
                'ETH': 0.35,
                'USDC': 0.15,
                'Other': 0.05
            }
            
            for asset, current_allocation in allocations.items():
                target = target_allocations.get(asset, 0)
                if abs(current_allocation - target) > self.config['rebalance_threshold']:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Optimization check error: {e}")
            return False
    
    def optimize_portfolio(self, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """Optimize portfolio allocation"""
        try:
            current_portfolio = self.get_current_portfolio()
            constraints = constraints or {}
            
            # Simulate optimization algorithm
            optimized_allocations = {
                'XMRT': 0.45,
                'ETH': 0.35,
                'USDC': 0.15,
                'BTC': 0.03,
                'Other': 0.02
            }
            
            # Calculate expected improvements
            current_risk = current_portfolio.get('risk_score', 0.5)
            optimized_risk = max(0.25, current_risk - 0.1)
            
            expected_return = 0.12 + (datetime.now().second * 0.001)
            
            optimization_result = {
                'success': True,
                'current_allocations': current_portfolio.get('allocations', {}),
                'optimized_allocations': optimized_allocations,
                'risk_reduction': current_risk - optimized_risk,
                'expected_annual_return': expected_return,
                'implementation_cost': 0.002,  # 0.2% of portfolio
                'confidence_score': 0.85,
                'timestamp': datetime.now().isoformat(),
                'summary': f'Optimization reduces risk by {((current_risk - optimized_risk) * 100):.1f}% while maintaining {(expected_return * 100):.1f}% expected return'
            }
            
            # Update memory
            self.memory['last_rebalance'] = datetime.now().isoformat()
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Portfolio optimization error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def assess_portfolio_risk(self) -> Dict[str, Any]:
        """Assess current portfolio risk"""
        try:
            portfolio_data = self.get_current_portfolio()
            
            # Risk assessment components
            market_risk = 0.3 + (datetime.now().second * 0.005)
            liquidity_risk = max(0.1, 0.5 - portfolio_data.get('liquidity_ratio', 0.2))
            concentration_risk = self.calculate_concentration_risk(portfolio_data.get('allocations', {}))
            
            overall_risk = (market_risk + liquidity_risk + concentration_risk) / 3
            
            risk_assessment = {
                'overall_risk_score': overall_risk,
                'risk_level': 'Low' if overall_risk < 0.3 else 'Medium' if overall_risk < 0.6 else 'High',
                'components': {
                    'market_risk': market_risk,
                    'liquidity_risk': liquidity_risk,
                    'concentration_risk': concentration_risk
                },
                'recommendations': self.generate_risk_recommendations(overall_risk),
                'timestamp': datetime.now().isoformat()
            }
            
            # Store in memory
            self.memory['risk_assessments'].append(risk_assessment)
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Risk assessment error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def calculate_concentration_risk(self, allocations: Dict[str, float]) -> float:
        """Calculate concentration risk using Herfindahl index"""
        try:
            herfindahl_index = sum(allocation ** 2 for allocation in allocations.values())
            # Normalize to 0-1 scale (1 = maximum concentration)
            return min(1.0, herfindahl_index)
        except Exception:
            return 0.5  # Default moderate risk
    
    def generate_risk_recommendations(self, risk_score: float) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        if risk_score > 0.6:
            recommendations.extend([
                "Consider reducing exposure to high-volatility assets",
                "Increase USDC allocation for stability",
                "Implement stop-loss mechanisms"
            ])
        elif risk_score > 0.4:
            recommendations.extend([
                "Monitor market conditions closely",
                "Consider gradual rebalancing",
                "Maintain current liquidity levels"
            ])
        else:
            recommendations.extend([
                "Portfolio risk is well-managed",
                "Consider opportunities for higher yield",
                "Maintain diversification"
            ])
        
        return recommendations
    
    def execute_rebalance(self, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute portfolio rebalancing"""
        try:
            optimization_result = self.optimize_portfolio(parameters)
            
            if not optimization_result.get('success'):
                return optimization_result
            
            # Simulate rebalancing execution
            execution_result = {
                'success': True,
                'trades_executed': [
                    {'asset': 'XMRT', 'action': 'buy', 'amount': 50000, 'price': 0.52},
                    {'asset': 'ETH', 'action': 'buy', 'amount': 10, 'price': 3520},
                    {'asset': 'USDC', 'action': 'sell', 'amount': 25000, 'price': 1.0}
                ],
                'total_cost': 1200,  # Gas + fees
                'execution_time': datetime.now().isoformat(),
                'new_allocations': optimization_result['optimized_allocations']
            }
            
            # Update memory
            self.memory['last_rebalance'] = datetime.now().isoformat()
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Rebalance execution error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def provide_treasury_advice(self, query: str) -> Dict[str, Any]:
        """Provide treasury management advice"""
        try:
            query_lower = query.lower()
            
            if 'yield' in query_lower or 'apy' in query_lower:
                advice = {
                    'topic': 'yield_optimization',
                    'advice': 'Consider staking XMRT for 12% APY or providing liquidity to ETH/XMRT pool for 15% APY',
                    'risk_level': 'Medium',
                    'implementation_steps': [
                        'Assess current liquidity needs',
                        'Allocate 30% to staking',
                        'Monitor pool performance'
                    ]
                }
            elif 'risk' in query_lower:
                advice = {
                    'topic': 'risk_management',
                    'advice': 'Current portfolio risk is moderate. Consider increasing USDC allocation to 20% for stability',
                    'risk_level': 'Low',
                    'implementation_steps': [
                        'Gradually increase stablecoin allocation',
                        'Set up automated rebalancing',
                        'Monitor correlation metrics'
                    ]
                }
            else:
                advice = {
                    'topic': 'general_treasury',
                    'advice': 'Treasury is performing well. Focus on maintaining diversification and monitoring market conditions',
                    'risk_level': 'Low',
                    'implementation_steps': [
                        'Continue current strategy',
                        'Monitor for rebalancing opportunities',
                        'Stay informed on market trends'
                    ]
                }
            
            advice['timestamp'] = datetime.now().isoformat()
            advice['confidence'] = 0.8
            
            return advice
            
        except Exception as e:
            logger.error(f"Treasury advice error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_treasury_status(self) -> Dict[str, Any]:
        """Get comprehensive treasury status"""
        try:
            portfolio_data = self.get_current_portfolio()
            risk_assessment = self.assess_portfolio_risk()
            
            status = {
                'agent_status': 'active',
                'portfolio': portfolio_data,
                'risk_assessment': risk_assessment,
                'last_optimization': self.memory.get('last_rebalance'),
                'optimization_count': len(self.memory.get('optimization_history', [])),
                'capabilities': self.capabilities,
                'autonomous_features': {
                    'auto_optimization': True,
                    'risk_monitoring': True,
                    'rebalancing': True
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Treasury status error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_memory(self):
        """Save agent memory to persistent storage"""
        try:
            with open(f'{self.agent_name}_memory.json', 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.error(f"Memory save error: {e}")
    
    def load_memory(self):
        """Load agent memory from persistent storage"""
        try:
            with open(f'{self.agent_name}_memory.json', 'r') as f:
                self.memory = json.load(f)
        except FileNotFoundError:
            logger.info("No existing memory file found, starting fresh")
        except Exception as e:
            logger.error(f"Memory load error: {e}")

# Global treasury agent instance
treasury_agent = TreasuryAgent()

@treasury_bp.route('/receive', methods=['POST'])
def receive_message():
    """Webhook endpoint for receiving messages from other agents"""
    try:
        data = request.get_json()
        treasury_agent.handle_message(data)
        return jsonify({'status': 'received'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@treasury_bp.route('/optimize', methods=['POST'])
def optimize_portfolio():
    """Manual portfolio optimization endpoint"""
    try:
        data = request.get_json() or {}
        constraints = data.get('constraints', {})
        result = treasury_agent.optimize_portfolio(constraints)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@treasury_bp.route('/risk-assessment', methods=['GET'])
def get_risk_assessment():
    """Get current portfolio risk assessment"""
    try:
        result = treasury_agent.assess_portfolio_risk()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@treasury_bp.route('/rebalance', methods=['POST'])
def execute_rebalance():
    """Execute portfolio rebalancing"""
    try:
        data = request.get_json() or {}
        result = treasury_agent.execute_rebalance(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@treasury_bp.route('/advice', methods=['POST'])
def get_treasury_advice():
    """Get treasury management advice"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        result = treasury_agent.provide_treasury_advice(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@treasury_bp.route('/status', methods=['GET'])
def get_treasury_status():
    """Get treasury agent status"""
    try:
        result = treasury_agent.get_treasury_status()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@treasury_bp.route('/memory', methods=['GET'])
def get_memory():
    """Get treasury agent memory"""
    try:
        return jsonify({
            'success': True,
            'memory': treasury_agent.memory
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

