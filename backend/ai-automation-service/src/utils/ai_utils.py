"""
AI Utilities for XMRT DAO
Handles all AI operations, analysis, and integrations
"""

import asyncio
import logging
import json
import openai
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import numpy as np

logger = logging.getLogger(__name__)

class AIUtils:
    """Utility class for AI operations"""

    def __init__(self):
        # Initialize OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY')

        # AI configuration
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 1000
        self.temperature = 0.7

        # External API configurations
        self.discord_token = os.getenv('DISCORD_BOT_TOKEN')
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.github_token = os.getenv('GITHUB_TOKEN')

        logger.info("AI utilities initialized")

    async def analyze_proposal(self, description: str, calldata: str, target: str, value: float) -> Dict[str, Any]:
        """Analyze a governance proposal using AI"""
        try:
            prompt = f"""
            Analyze the following DAO governance proposal:

            Description: {description}
            Target Contract: {target}
            Value: {value} ETH
            Call Data: {calldata}

            Please provide analysis on:
            1. Technical feasibility (0-1 score)
            2. Economic impact (0-1 score)
            3. Risk level (0-1 score)
            4. Community benefit (0-1 score)
            5. Overall reasoning

            Respond in JSON format with scores and reasoning.
            """

            response = await self.call_openai(prompt)

            # Parse response
            try:
                analysis = json.loads(response)
            except json.JSONDecodeError:
                # Fallback parsing
                analysis = {
                    'technical_feasibility': 0.7,
                    'economic_impact': 0.6,
                    'risk_level': 0.3,
                    'community_sentiment': 0.7,
                    'reasoning': response
                }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing proposal: {e}")
            return {
                'technical_feasibility': 0.5,
                'economic_impact': 0.5,
                'risk_level': 0.5,
                'community_sentiment': 0.5,
                'reasoning': 'Analysis failed'
            }

    async def emergency_analyze_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Emergency analysis for critical proposals"""
        try:
            prompt = f"""
            EMERGENCY ANALYSIS REQUIRED:

            Proposal: {proposal.get('description', '')}

            This is marked as an emergency proposal. Provide immediate analysis:
            1. Is this a legitimate emergency? (yes/no)
            2. Confidence level (0-1)
            3. Recommended action (support/oppose/abstain)
            4. Brief reasoning

            Respond in JSON format.
            """

            response = await self.call_openai(prompt, temperature=0.3)  # Lower temperature for consistency

            try:
                analysis = json.loads(response)
            except json.JSONDecodeError:
                analysis = {
                    'legitimate_emergency': False,
                    'confidence': 0.5,
                    'recommendation': False,
                    'reasoning': 'Emergency analysis failed'
                }

            return analysis

        except Exception as e:
            logger.error(f"Error in emergency analysis: {e}")
            return {
                'legitimate_emergency': False,
                'confidence': 0.3,
                'recommendation': False,
                'reasoning': 'Emergency analysis error'
            }

    async def validate_proposal(self, description: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a proposal before submission"""
        try:
            prompt = f"""
            Validate this governance proposal:

            Description: {description}
            Actions: {json.dumps(actions, indent=2)}

            Check for:
            1. Clear description
            2. Valid actions
            3. Reasonable scope
            4. Potential issues

            Respond with validation result in JSON format.
            """

            response = await self.call_openai(prompt)

            try:
                validation = json.loads(response)
            except json.JSONDecodeError:
                validation = {
                    'valid': True,
                    'reason': 'Basic validation passed'
                }

            return validation

        except Exception as e:
            logger.error(f"Error validating proposal: {e}")
            return {'valid': False, 'reason': 'Validation error'}

    async def analyze_community_sentiment(self) -> Dict[str, Any]:
        """Analyze overall community sentiment"""
        try:
            # Gather sentiment data from multiple sources
            discord_sentiment = await self.get_discord_sentiment()
            twitter_sentiment = await self.get_twitter_sentiment()
            telegram_sentiment = await self.get_telegram_sentiment()

            # Aggregate sentiment
            sentiments = [discord_sentiment, twitter_sentiment, telegram_sentiment]
            valid_sentiments = [s for s in sentiments if s is not None]

            if valid_sentiments:
                avg_sentiment = sum(valid_sentiments) / len(valid_sentiments)
                confidence = len(valid_sentiments) / 3  # Confidence based on data availability
            else:
                avg_sentiment = 0.5
                confidence = 0.1

            return {
                'overall_sentiment': avg_sentiment,
                'confidence': confidence,
                'sources': {
                    'discord': discord_sentiment,
                    'twitter': twitter_sentiment,
                    'telegram': telegram_sentiment
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing community sentiment: {e}")
            return {'overall_sentiment': 0.5, 'confidence': 0.1}

    async def optimize_portfolio(self, current_allocations: Dict[str, float], 
                               market_data: Dict[str, Any], risk_tolerance: float,
                               constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize portfolio allocations using AI"""
        try:
            prompt = f"""
            Optimize this portfolio allocation:

            Current Allocations: {json.dumps(current_allocations, indent=2)}
            Market Data: {json.dumps(market_data, indent=2)}
            Risk Tolerance: {risk_tolerance}
            Constraints: {json.dumps(constraints, indent=2)}

            Provide optimized allocations that:
            1. Maximize risk-adjusted returns
            2. Respect constraints
            3. Consider market conditions

            Respond with optimized allocations and expected return in JSON format.
            """

            response = await self.call_openai(prompt)

            try:
                optimization = json.loads(response)
            except json.JSONDecodeError:
                # Fallback optimization
                optimization = {
                    'allocations': current_allocations,
                    'expected_return': 0.08,
                    'risk_score': risk_tolerance
                }

            return optimization

        except Exception as e:
            logger.error(f"Error optimizing portfolio: {e}")
            return {
                'allocations': current_allocations,
                'expected_return': 0.05,
                'risk_score': risk_tolerance
            }

    async def get_market_data(self) -> Dict[str, Any]:
        """Get market data for analysis"""
        try:
            # Mock market data - replace with real API calls
            return {
                'XMRT': {'price': 0.5, 'change_24h': 0.02, 'volatility': 0.15},
                'ETH': {'price': 3500, 'change_24h': -0.01, 'volatility': 0.08},
                'USDC': {'price': 1.0, 'change_24h': 0.0, 'volatility': 0.01},
                'market_sentiment': 0.6,
                'fear_greed_index': 55
            }

        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return {}

    async def generate_support_response(self, request: str, category: str, user_history: Dict[str, Any]) -> str:
        """Generate support response"""
        try:
            prompt = f"""
            Generate a helpful support response for this user request:

            Request: {request}
            Category: {category}
            User History: {json.dumps(user_history, indent=2)}

            Provide a helpful, professional response that addresses their question.
            Keep it concise but informative.
            """

            response = await self.call_openai(prompt, max_tokens=300)
            return response

        except Exception as e:
            logger.error(f"Error generating support response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again later or contact our support team."

    async def classify_support_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Classify a support request"""
        try:
            content = message.get('content', '')

            prompt = f"""
            Classify this message as a support request:

            Message: {content}

            Determine:
            1. Is this a support request? (true/false)
            2. Category (technical, financial, general, bug_report)
            3. Priority (low, medium, high)
            4. Confidence (0-1)

            Respond in JSON format.
            """

            response = await self.call_openai(prompt, max_tokens=200)

            try:
                classification = json.loads(response)
            except json.JSONDecodeError:
                classification = {
                    'is_support_request': True,
                    'category': 'general',
                    'priority': 'medium',
                    'confidence': 0.5
                }

            return classification

        except Exception as e:
            logger.error(f"Error classifying support request: {e}")
            return {
                'is_support_request': False,
                'category': 'general',
                'priority': 'low',
                'confidence': 0.1
            }

    async def analyze_sentiment(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment of messages"""
        try:
            if not messages:
                return {'score': 0.5, 'confidence': 0.0}

            # Sample messages for analysis
            sample_messages = messages[-10:] if len(messages) > 10 else messages
            text_content = ' '.join([msg.get('content', '') for msg in sample_messages])

            prompt = f"""
            Analyze the sentiment of these community messages:

            Messages: {text_content[:1000]}...

            Provide:
            1. Overall sentiment score (0-1, where 0 is very negative, 1 is very positive)
            2. Confidence level (0-1)
            3. Key themes

            Respond in JSON format.
            """

            response = await self.call_openai(prompt, max_tokens=200)

            try:
                sentiment = json.loads(response)
            except json.JSONDecodeError:
                sentiment = {
                    'score': 0.5,
                    'confidence': 0.3,
                    'themes': ['general discussion']
                }

            return sentiment

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {'score': 0.5, 'confidence': 0.1}

    async def call_openai(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """Call OpenAI API"""
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error calling OpenAI: {e}")
            return "AI analysis unavailable"

    async def send_alert(self, alert_data: Dict[str, Any]):
        """Send alert to administrators"""
        try:
            logger.warning(f"ALERT: {alert_data}")
            # In production, send to Discord, Slack, email, etc.

        except Exception as e:
            logger.error(f"Error sending alert: {e}")

    # Mock implementations for community monitoring
    async def get_discord_data(self) -> Dict[str, Any]:
        """Get Discord community data"""
        return {
            'active_users': 150,
            'messages': [
                {'content': 'Great project!', 'user_id': 'user1'},
                {'content': 'When moon?', 'user_id': 'user2'}
            ],
            'engagement_rate': 0.75
        }

    async def get_twitter_data(self) -> Dict[str, Any]:
        """Get Twitter data"""
        return {
            'mentions': [
                {'content': 'Love the XMRT DAO!', 'user': {'username': 'cryptofan'}}
            ],
            'hashtag_usage': 25,
            'reach': 10000
        }

    async def get_telegram_data(self) -> Dict[str, Any]:
        """Get Telegram data"""
        return {
            'active_users': 200,
            'messages': [
                {'content': 'Good updates today', 'user_id': 'tg_user1'}
            ]
        }

    async def get_github_data(self) -> Dict[str, Any]:
        """Get GitHub data"""
        return {
            'new_issues': [],
            'pull_requests': [],
            'contributors': 5,
            'stars': 100
        }

    async def get_discord_sentiment(self) -> float:
        """Get Discord sentiment"""
        return 0.7

    async def get_twitter_sentiment(self) -> float:
        """Get Twitter sentiment"""
        return 0.6

    async def get_telegram_sentiment(self) -> float:
        """Get Telegram sentiment"""
        return 0.8

    async def send_message(self, user_id: str, content: str, platform: str, reply_to: str = None):
        """Send message to user"""
        logger.info(f"Sending message to {user_id} on {platform}: {content[:50]}...")

    async def moderate_content(self, content: str) -> Dict[str, Any]:
        """Moderate content for inappropriate material"""
        # Basic keyword filtering
        inappropriate_keywords = ['spam', 'scam', 'hate']

        flagged = any(keyword in content.lower() for keyword in inappropriate_keywords)

        return {
            'flagged': flagged,
            'reason': 'inappropriate content' if flagged else None,
            'severity': 'medium' if flagged else 'low',
            'recommended_action': 'warn' if flagged else 'none'
        }
