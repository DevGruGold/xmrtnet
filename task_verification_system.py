#!/usr/bin/env python3
"""
TASK VERIFICATION SYSTEM - NO FAKE TASKS ALLOWED
This script enforces real task completion with proof
"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class TaskVerificationSystem:
    def __init__(self):
        self.logger = self.setup_logging()
        self.verification_log = []
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('task_verification.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def verify_prerequisites(self, task_type: str, requirements: List[str]) -> Tuple[bool, List[str]]:
        """Verify all prerequisites exist before attempting task"""
        missing_requirements = []
        
        for requirement in requirements:
            if requirement.startswith('env_'):
                env_var = requirement.replace('env_', '').upper()
                if not os.getenv(env_var):
                    missing_requirements.append(f"Missing environment variable: {env_var}")
            
            elif requirement == 'twitter_api_access':
                if not self.test_twitter_access():
                    missing_requirements.append("Twitter API access failed")
            
            elif requirement == 'github_api_access':
                if not self.test_github_access():
                    missing_requirements.append("GitHub API access failed")
        
        success = len(missing_requirements) == 0
        self.logger.info(f"Prerequisites check for {task_type}: {'PASSED' if success else 'FAILED'}")
        
        if missing_requirements:
            self.logger.error(f"Missing requirements: {missing_requirements}")
        
        return success, missing_requirements
    
    def test_twitter_access(self) -> bool:
        """Test actual Twitter API access"""
        api_key = os.getenv('TWITTER_API_KEY')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        
        if not api_key or not access_token:
            self.logger.error("Twitter credentials not found in environment")
            return False
        
        try:
            # Test actual Twitter API call
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get('https://api.twitter.com/2/users/me', headers=headers)
            
            if response.status_code == 200:
                self.logger.info("Twitter API access verified")
                return True
            else:
                self.logger.error(f"Twitter API test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Twitter API test error: {e}")
            return False
    
    def test_github_access(self) -> bool:
        """Test actual GitHub API access"""
        token = os.getenv('GITHUB_TOKEN')
        
        if not token:
            self.logger.error("GitHub token not found in environment")
            return False
        
        try:
            headers = {'Authorization': f'token {token}'}
            response = requests.get('https://api.github.com/user', headers=headers)
            
            if response.status_code == 200:
                self.logger.info("GitHub API access verified")
                return True
            else:
                self.logger.error(f"GitHub API test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"GitHub API test error: {e}")
            return False
    
    def execute_verified_task(self, task_type: str, task_data: Dict) -> Dict:
        """Execute a task with full verification"""
        
        task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        verification_result = {
            'task_id': task_id,
            'task_type': task_type,
            'start_time': datetime.now().isoformat(),
            'prerequisites_passed': False,
            'execution_successful': False,
            'verification_passed': False,
            'proof_of_completion': None,
            'errors': [],
            'evidence': {}
        }
        
        try:
            # Step 1: Verify prerequisites
            requirements = task_data.get('requirements', [])
            prereq_success, missing_reqs = self.verify_prerequisites(task_type, requirements)
            
            verification_result['prerequisites_passed'] = prereq_success
            
            if not prereq_success:
                verification_result['errors'].extend(missing_reqs)
                self.logger.error(f"Task {task_id} failed prerequisites: {missing_reqs}")
                return verification_result
            
            # Step 2: Execute the actual task
            if task_type == 'twitter_post':
                execution_result = self.execute_twitter_post(task_data)
            elif task_type == 'github_discussion':
                execution_result = self.execute_github_discussion(task_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            verification_result['execution_successful'] = execution_result['success']
            verification_result['evidence'] = execution_result.get('evidence', {})
            
            if execution_result['success']:
                # Step 3: Verify the task actually completed
                verification_success = self.verify_task_completion(task_type, execution_result)
                verification_result['verification_passed'] = verification_success
                verification_result['proof_of_completion'] = execution_result.get('proof')
            
        except Exception as e:
            self.logger.error(f"Task execution error: {e}")
            verification_result['errors'].append(str(e))
        
        verification_result['end_time'] = datetime.now().isoformat()
        
        # Log the complete verification result
        self.log_verification_result(verification_result)
        
        return verification_result
    
    def execute_twitter_post(self, task_data: Dict) -> Dict:
        """Execute actual Twitter post with verification"""
        
        content = task_data.get('content', '')
        if not content:
            return {'success': False, 'error': 'No content provided'}
        
        try:
            # Actual Twitter API call
            api_key = os.getenv('TWITTER_API_KEY')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            
            headers = {'Authorization': f'Bearer {access_token}'}
            data = {'text': content}
            
            response = requests.post(
                'https://api.twitter.com/2/tweets',
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                tweet_data = response.json()
                tweet_id = tweet_data['data']['id']
                tweet_url = f"https://twitter.com/user/status/{tweet_id}"
                
                return {
                    'success': True,
                    'evidence': {
                        'api_response': tweet_data,
                        'response_code': response.status_code
                    },
                    'proof': {
                        'tweet_id': tweet_id,
                        'tweet_url': tweet_url,
                        'timestamp': datetime.now().isoformat()
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'Twitter API error: {response.status_code}',
                    'response': response.text
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_task_completion(self, task_type: str, execution_result: Dict) -> bool:
        """Verify the task actually completed successfully"""
        
        if task_type == 'twitter_post':
            # Verify tweet actually exists
            tweet_id = execution_result.get('proof', {}).get('tweet_id')
            if tweet_id:
                return self.verify_tweet_exists(tweet_id)
        
        return False
    
    def verify_tweet_exists(self, tweet_id: str) -> bool:
        """Verify tweet actually exists by checking Twitter API"""
        try:
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(
                f'https://api.twitter.com/2/tweets/{tweet_id}',
                headers=headers
            )
            
            return response.status_code == 200
        except Exception:
            return False
    
    def log_verification_result(self, result: Dict):
        """Log complete verification result"""
        self.verification_log.append(result)
        
        status = "SUCCESS" if result['verification_passed'] else "FAILED"
        self.logger.info(f"Task {result['task_id']}: {status}")
        
        if result['errors']:
            self.logger.error(f"Errors: {result['errors']}")
        
        if result['proof_of_completion']:
            self.logger.info(f"Proof: {result['proof_of_completion']}")

# Example usage
if __name__ == "__main__":
    verifier = TaskVerificationSystem()
    
    # Example: Verify a Twitter post task
    twitter_task = {
        'requirements': ['env_twitter_api_key', 'env_twitter_access_token'],
        'content': 'Test tweet from verified system'
    }
    
    result = verifier.execute_verified_task('twitter_post', twitter_task)
    print(json.dumps(result, indent=2))
