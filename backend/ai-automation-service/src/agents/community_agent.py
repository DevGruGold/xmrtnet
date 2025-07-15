"""
XMRT DAO Community Agent
Handles community engagement, support, and communication automation
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from web3 import Web3
from eth_account import Account
import openai

logger = logging.getLogger(__name__)

class CommunityAgent:
    """AI agent for autonomous community management"""

    def __init__(self, blockchain_utils, ai_utils):
        self.blockchain_utils = blockchain_utils
        self.ai_utils = ai_utils
        self.active = True
        self.last_community_check = None
        self.active_conversations = {}
        self.community_metrics = {}

        # Community management configuration
        self.response_time_target = 300  # 5 minutes
        self.sentiment_threshold = 0.3  # Below this triggers intervention
        self.engagement_target = 0.7  # Target engagement rate

        logger.info("Community Agent initialized")

    async def monitor_community(self):
        """Monitor community channels and engagement"""
        try:
            logger.info("👥 Monitoring community...")

            # Monitor Discord
            discord_data = await self.monitor_discord()

            # Monitor Twitter/X
            twitter_data = await self.monitor_twitter()

            # Monitor Telegram
            telegram_data = await self.monitor_telegram()

            # Monitor GitHub
            github_data = await self.monitor_github()

            # Aggregate community data
            community_data = {
                'discord': discord_data,
                'twitter': twitter_data,
                'telegram': telegram_data,
                'github': github_data,
                'timestamp': datetime.now().isoformat()
            }

            # Analyze overall community health
            health_analysis = await self.analyze_community_health(community_data)

            # Handle any issues
            if health_analysis.get('issues'):
                await self.handle_community_issues(health_analysis['issues'])

            # Update metrics
            self.community_metrics = health_analysis
            self.last_community_check = datetime.now()

            # Store monitoring data
            await self.store_community_data(community_data, health_analysis)

        except Exception as e:
            logger.error(f"Error monitoring community: {e}")

    async def monitor_discord(self) -> Dict[str, Any]:
        """Monitor Discord community"""
        try:
            # Get Discord messages and activity
            discord_data = await self.ai_utils.get_discord_data()

            # Analyze sentiment
            sentiment = await self.ai_utils.analyze_sentiment(discord_data.get('messages', []))

            # Check for support requests
            support_requests = await self.identify_support_requests(discord_data.get('messages', []))

            # Handle support requests
            for request in support_requests:
                await self.handle_support_request(request, 'discord')

            return {
                'active_users': discord_data.get('active_users', 0),
                'messages_count': len(discord_data.get('messages', [])),
                'sentiment': sentiment,
                'support_requests': len(support_requests),
                'engagement_rate': discord_data.get('engagement_rate', 0)
            }

        except Exception as e:
            logger.error(f"Error monitoring Discord: {e}")
            return {}

    async def monitor_twitter(self) -> Dict[str, Any]:
        """Monitor Twitter/X mentions and engagement"""
        try:
            # Get Twitter mentions and hashtags
            twitter_data = await self.ai_utils.get_twitter_data()

            # Analyze sentiment
            sentiment = await self.ai_utils.analyze_sentiment(twitter_data.get('tweets', []))

            # Identify influential mentions
            influential_mentions = await self.identify_influential_mentions(twitter_data.get('mentions', []))

            # Respond to important mentions
            for mention in influential_mentions:
                await self.respond_to_mention(mention)

            return {
                'mentions': len(twitter_data.get('mentions', [])),
                'hashtag_usage': twitter_data.get('hashtag_usage', 0),
                'sentiment': sentiment,
                'influential_mentions': len(influential_mentions),
                'reach': twitter_data.get('reach', 0)
            }

        except Exception as e:
            logger.error(f"Error monitoring Twitter: {e}")
            return {}

    async def monitor_telegram(self) -> Dict[str, Any]:
        """Monitor Telegram community"""
        try:
            # Get Telegram messages
            telegram_data = await self.ai_utils.get_telegram_data()

            # Analyze sentiment
            sentiment = await self.ai_utils.analyze_sentiment(telegram_data.get('messages', []))

            # Check for spam or inappropriate content
            moderation_issues = await self.check_moderation_issues(telegram_data.get('messages', []))

            # Handle moderation
            for issue in moderation_issues:
                await self.handle_moderation_issue(issue, 'telegram')

            return {
                'active_users': telegram_data.get('active_users', 0),
                'messages_count': len(telegram_data.get('messages', [])),
                'sentiment': sentiment,
                'moderation_issues': len(moderation_issues)
            }

        except Exception as e:
            logger.error(f"Error monitoring Telegram: {e}")
            return {}

    async def monitor_github(self) -> Dict[str, Any]:
        """Monitor GitHub repository activity"""
        try:
            # Get GitHub activity
            github_data = await self.ai_utils.get_github_data()

            # Check for new issues
            new_issues = github_data.get('new_issues', [])

            # Respond to issues
            for issue in new_issues:
                await self.respond_to_github_issue(issue)

            return {
                'new_issues': len(new_issues),
                'pull_requests': len(github_data.get('pull_requests', [])),
                'contributors': github_data.get('contributors', 0),
                'stars': github_data.get('stars', 0)
            }

        except Exception as e:
            logger.error(f"Error monitoring GitHub: {e}")
            return {}

    async def identify_support_requests(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify support requests in messages"""
        support_requests = []

        support_keywords = [
            'help', 'issue', 'problem', 'error', 'bug', 'support',
            'how to', 'can't', 'unable', 'not working', 'broken'
        ]

        for message in messages:
            content = message.get('content', '').lower()

            # Check for support keywords
            if any(keyword in content for keyword in support_keywords):
                # Use AI to classify the request
                classification = await self.ai_utils.classify_support_request(message)

                if classification.get('is_support_request', False):
                    support_requests.append({
                        'message': message,
                        'classification': classification,
                        'priority': classification.get('priority', 'medium'),
                        'category': classification.get('category', 'general')
                    })

        return support_requests

    async def handle_support_request(self, request: Dict[str, Any], platform: str):
        """Handle a support request"""
        try:
            message = request['message']
            classification = request['classification']

            logger.info(f"🎧 Handling support request on {platform}: {classification.get('category', 'general')}")

            # Generate response using AI
            response = await self.ai_utils.generate_support_response(
                request=message.get('content', ''),
                category=classification.get('category', 'general'),
                user_history=await self.get_user_history(message.get('user_id'))
            )

            # Send response
            await self.send_response(message, response, platform)

            # Track conversation
            self.active_conversations[message.get('user_id')] = {
                'platform': platform,
                'category': classification.get('category'),
                'started': datetime.now().isoformat(),
                'messages': [message, {'content': response, 'sender': 'agent'}]
            }

            # Escalate if needed
            if classification.get('priority') == 'high':
                await self.escalate_to_human(request, platform)

        except Exception as e:
            logger.error(f"Error handling support request: {e}")

    async def identify_influential_mentions(self, mentions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify influential mentions that need response"""
        influential = []

        for mention in mentions:
            user = mention.get('user', {})

            # Check influence metrics
            if (user.get('followers', 0) > 10000 or 
                user.get('verified', False) or
                mention.get('retweets', 0) > 50):

                # Analyze sentiment and importance
                analysis = await self.ai_utils.analyze_mention_importance(mention)

                if analysis.get('should_respond', False):
                    influential.append({
                        'mention': mention,
                        'analysis': analysis,
                        'priority': analysis.get('priority', 'medium')
                    })

        return influential

    async def respond_to_mention(self, mention_data: Dict[str, Any]):
        """Respond to an influential mention"""
        try:
            mention = mention_data['mention']
            analysis = mention_data['analysis']

            logger.info(f"🐦 Responding to influential mention from @{mention.get('user', {}).get('username')}")

            # Generate appropriate response
            response = await self.ai_utils.generate_twitter_response(
                mention=mention.get('content', ''),
                context=analysis.get('context', ''),
                tone=analysis.get('recommended_tone', 'professional')
            )

            # Send response
            await self.ai_utils.send_twitter_response(mention.get('id'), response)

        except Exception as e:
            logger.error(f"Error responding to mention: {e}")

    async def check_moderation_issues(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for moderation issues in messages"""
        issues = []

        for message in messages:
            # Use AI to detect inappropriate content
            moderation_result = await self.ai_utils.moderate_content(message.get('content', ''))

            if moderation_result.get('flagged', False):
                issues.append({
                    'message': message,
                    'reason': moderation_result.get('reason', 'inappropriate'),
                    'severity': moderation_result.get('severity', 'medium'),
                    'action': moderation_result.get('recommended_action', 'warn')
                })

        return issues

    async def handle_moderation_issue(self, issue: Dict[str, Any], platform: str):
        """Handle a moderation issue"""
        try:
            message = issue['message']
            action = issue['action']

            logger.warning(f"⚠️ Moderation issue on {platform}: {issue['reason']}")

            if action == 'warn':
                # Send warning to user
                warning = await self.ai_utils.generate_warning_message(issue['reason'])
                await self.send_direct_message(message.get('user_id'), warning, platform)

            elif action == 'delete':
                # Delete message
                await self.ai_utils.delete_message(message.get('id'), platform)

            elif action == 'ban':
                # Escalate to human moderators
                await self.escalate_moderation_issue(issue, platform)

            # Log moderation action
            await self.log_moderation_action(issue, action, platform)

        except Exception as e:
            logger.error(f"Error handling moderation issue: {e}")

    async def respond_to_github_issue(self, issue: Dict[str, Any]):
        """Respond to a GitHub issue"""
        try:
            logger.info(f"🐙 Responding to GitHub issue #{issue.get('number')}")

            # Analyze issue
            analysis = await self.ai_utils.analyze_github_issue(issue)

            if analysis.get('should_respond', False):
                # Generate response
                response = await self.ai_utils.generate_github_response(
                    issue=issue,
                    analysis=analysis
                )

                # Post comment
                await self.ai_utils.post_github_comment(issue.get('number'), response)

                # Add labels if needed
                if analysis.get('labels'):
                    await self.ai_utils.add_github_labels(issue.get('number'), analysis['labels'])

        except Exception as e:
            logger.error(f"Error responding to GitHub issue: {e}")

    async def analyze_community_health(self, community_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall community health"""
        try:
            # Calculate metrics
            total_engagement = 0
            total_sentiment = 0
            platform_count = 0
            issues = []

            for platform, data in community_data.items():
                if platform == 'timestamp':
                    continue

                if data:
                    platform_count += 1

                    # Engagement
                    engagement = data.get('engagement_rate', 0)
                    total_engagement += engagement

                    if engagement < self.engagement_target:
                        issues.append({
                            'type': 'low_engagement',
                            'platform': platform,
                            'value': engagement,
                            'threshold': self.engagement_target
                        })

                    # Sentiment
                    sentiment = data.get('sentiment', {}).get('score', 0.5)
                    total_sentiment += sentiment

                    if sentiment < self.sentiment_threshold:
                        issues.append({
                            'type': 'negative_sentiment',
                            'platform': platform,
                            'value': sentiment,
                            'threshold': self.sentiment_threshold
                        })

            # Calculate averages
            avg_engagement = total_engagement / platform_count if platform_count > 0 else 0
            avg_sentiment = total_sentiment / platform_count if platform_count > 0 else 0.5

            # Calculate health score
            health_score = (avg_engagement + avg_sentiment) / 2

            return {
                'health_score': health_score,
                'avg_engagement': avg_engagement,
                'avg_sentiment': avg_sentiment,
                'issues': issues,
                'platforms_monitored': platform_count,
                'status': self.get_health_status(health_score)
            }

        except Exception as e:
            logger.error(f"Error analyzing community health: {e}")
            return {'health_score': 0, 'status': 'error'}

    def get_health_status(self, health_score: float) -> str:
        """Get health status based on score"""
        if health_score > 0.8:
            return 'excellent'
        elif health_score > 0.6:
            return 'good'
        elif health_score > 0.4:
            return 'fair'
        elif health_score > 0.2:
            return 'poor'
        else:
            return 'critical'

    async def handle_community_issues(self, issues: List[Dict[str, Any]]):
        """Handle community issues"""
        for issue in issues:
            logger.warning(f"Community issue: {issue['type']} on {issue['platform']}")

            if issue['type'] == 'low_engagement':
                await self.boost_engagement(issue['platform'])
            elif issue['type'] == 'negative_sentiment':
                await self.address_negative_sentiment(issue['platform'])

    async def boost_engagement(self, platform: str):
        """Boost engagement on a platform"""
        try:
            logger.info(f"🚀 Boosting engagement on {platform}")

            # Generate engaging content
            content = await self.ai_utils.generate_engaging_content(platform)

            # Post content
            await self.ai_utils.post_content(content, platform)

            # Start community activities
            if platform == 'discord':
                await self.start_discord_activity()
            elif platform == 'twitter':
                await self.start_twitter_campaign()

        except Exception as e:
            logger.error(f"Error boosting engagement: {e}")

    async def address_negative_sentiment(self, platform: str):
        """Address negative sentiment on a platform"""
        try:
            logger.info(f"💬 Addressing negative sentiment on {platform}")

            # Generate positive messaging
            message = await self.ai_utils.generate_positive_message(platform)

            # Post message
            await self.ai_utils.post_content(message, platform)

            # Engage with community
            await self.increase_community_engagement(platform)

        except Exception as e:
            logger.error(f"Error addressing negative sentiment: {e}")

    async def generate_reports(self):
        """Generate community reports"""
        try:
            logger.info("📊 Generating community reports...")

            # Generate daily report
            daily_report = await self.generate_daily_report()

            # Generate weekly summary
            if datetime.now().weekday() == 0:  # Monday
                weekly_report = await self.generate_weekly_report()
                await self.send_weekly_report(weekly_report)

            # Store reports
            await self.store_reports(daily_report)

        except Exception as e:
            logger.error(f"Error generating reports: {e}")

    async def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily community report"""
        return {
            'date': datetime.now().date().isoformat(),
            'metrics': self.community_metrics,
            'active_conversations': len(self.active_conversations),
            'support_requests_handled': await self.count_support_requests_today(),
            'engagement_actions': await self.count_engagement_actions_today(),
            'health_status': self.community_metrics.get('status', 'unknown')
        }

    async def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for community alerts"""
        alerts = []

        # Check response time
        overdue_conversations = await self.check_overdue_conversations()
        if overdue_conversations:
            alerts.append({
                'type': 'overdue_conversations',
                'count': len(overdue_conversations),
                'severity': 'medium'
            })

        # Check sentiment
        if self.community_metrics.get('avg_sentiment', 0.5) < self.sentiment_threshold:
            alerts.append({
                'type': 'negative_sentiment',
                'value': self.community_metrics.get('avg_sentiment'),
                'severity': 'high'
            })

        # Check engagement
        if self.community_metrics.get('avg_engagement', 0) < self.engagement_target:
            alerts.append({
                'type': 'low_engagement',
                'value': self.community_metrics.get('avg_engagement'),
                'severity': 'medium'
            })

        return alerts

    async def handle_alert(self, alert: Dict[str, Any]):
        """Handle a community alert"""
        try:
            alert_type = alert['type']

            if alert_type == 'overdue_conversations':
                await self.handle_overdue_conversations()
            elif alert_type == 'negative_sentiment':
                await self.handle_negative_sentiment_alert()
            elif alert_type == 'low_engagement':
                await self.handle_low_engagement_alert()

        except Exception as e:
            logger.error(f"Error handling alert: {e}")

    async def check_overdue_conversations(self) -> List[str]:
        """Check for overdue conversations"""
        overdue = []
        current_time = datetime.now()

        for user_id, conversation in self.active_conversations.items():
            started = datetime.fromisoformat(conversation['started'])
            if (current_time - started).seconds > self.response_time_target:
                overdue.append(user_id)

        return overdue

    async def get_user_history(self, user_id: str) -> Dict[str, Any]:
        """Get user interaction history"""
        try:
            return await self.blockchain_utils.get_user_history(user_id)
        except Exception as e:
            logger.error(f"Error getting user history: {e}")
            return {}

    async def send_response(self, message: Dict[str, Any], response: str, platform: str):
        """Send response to user"""
        try:
            await self.ai_utils.send_message(
                user_id=message.get('user_id'),
                content=response,
                platform=platform,
                reply_to=message.get('id')
            )
        except Exception as e:
            logger.error(f"Error sending response: {e}")

    async def escalate_to_human(self, request: Dict[str, Any], platform: str):
        """Escalate request to human support"""
        try:
            escalation_data = {
                'type': 'support_escalation',
                'platform': platform,
                'request': request,
                'timestamp': datetime.now().isoformat()
            }

            await self.ai_utils.send_alert(escalation_data)

        except Exception as e:
            logger.error(f"Error escalating to human: {e}")

    async def store_community_data(self, community_data: Dict[str, Any], health_analysis: Dict[str, Any]):
        """Store community monitoring data"""
        try:
            data = {
                'community_data': community_data,
                'health_analysis': health_analysis,
                'timestamp': datetime.now().isoformat(),
                'agent': 'community'
            }

            await self.blockchain_utils.store_community_data(data)

        except Exception as e:
            logger.error(f"Error storing community data: {e}")

    async def execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a manual action"""
        actions = {
            'monitor_community': self.monitor_community,
            'generate_reports': self.generate_reports,
            'boost_engagement': lambda: self.boost_engagement(params.get('platform', 'discord')),
            'handle_support': lambda: self.handle_support_request(params.get('request'), params.get('platform')),
            'check_alerts': self.check_alerts
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        result = await actions[action]()
        return {'success': True, 'result': result}

    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'active': self.active,
            'last_community_check': self.last_community_check.isoformat() if self.last_community_check else None,
            'active_conversations': len(self.active_conversations),
            'community_metrics': self.community_metrics,
            'response_time_target': self.response_time_target,
            'type': 'community'
        }

    def is_active(self) -> bool:
        """Check if agent is active"""
        return self.active
