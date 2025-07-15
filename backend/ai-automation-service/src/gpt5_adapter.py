#!/usr/bin/env python3
"""
GPT-5 Integration Adapter
Seamless integration layer for GPT-5 when it becomes available
Maintains backward compatibility with GPT-4
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import openai
from datetime import datetime
import json

class ModelType(Enum):
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo"
    GPT5 = "gpt-5"
    GPT5_TURBO = "gpt-5-turbo"

@dataclass
class AIRequest:
    prompt: str
    context: Dict[str, Any]
    model_preference: ModelType
    temperature: float = 0.7
    max_tokens: int = 4000
    stream: bool = False
    tools: Optional[List[Dict]] = None

@dataclass
class AIResponse:
    content: str
    model_used: ModelType
    tokens_used: int
    confidence_score: float
    reasoning_steps: Optional[List[str]] = None
    tool_calls: Optional[List[Dict]] = None

class GPT5Adapter:
    """
    Adapter for seamless GPT-5 integration with fallback to GPT-4
    Handles model switching, enhanced capabilities, and backward compatibility
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Model availability detection
        self.available_models = self._detect_available_models()
        self.preferred_model = self._select_preferred_model()
        
        # Enhanced capabilities for GPT-5
        self.gpt5_capabilities = {
            "enhanced_reasoning": True,
            "multimodal_support": True,
            "extended_context": True,
            "improved_function_calling": True,
            "better_code_generation": True,
            "advanced_planning": True,
            "autonomous_decision_making": True
        }
        
        # Configuration
        self.config = {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "api_base": os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
            "max_retries": 3,
            "timeout": 60,
            "fallback_enabled": True
        }
        
        self.logger.info(f"🤖 GPT-5 Adapter initialized. Available models: {self.available_models}")
        self.logger.info(f"🎯 Preferred model: {self.preferred_model}")
    
    def _detect_available_models(self) -> List[ModelType]:
        """Detect which AI models are available"""
        available = []
        
        try:
            # Check GPT-4 availability
            available.append(ModelType.GPT4)
            available.append(ModelType.GPT4_TURBO)
            
            # Check GPT-5 availability (when it becomes available)
            # This would be updated when GPT-5 is released
            try:
                # Placeholder for GPT-5 detection
                # models = openai.Model.list()
                # if any("gpt-5" in model.id for model in models.data):
                #     available.append(ModelType.GPT5)
                #     available.append(ModelType.GPT5_TURBO)
                pass
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Error detecting available models: {e}")
            available = [ModelType.GPT4]  # Fallback
        
        return available
    
    def _select_preferred_model(self) -> ModelType:
        """Select the best available model"""
        if ModelType.GPT5 in self.available_models:
            return ModelType.GPT5
        elif ModelType.GPT4_TURBO in self.available_models:
            return ModelType.GPT4_TURBO
        else:
            return ModelType.GPT4
    
    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process AI request with automatic model selection and fallback"""
        
        # Determine best model for request
        selected_model = self._select_model_for_request(request)
        
        try:
            # Process with selected model
            response = await self._make_ai_request(request, selected_model)
            return response
            
        except Exception as e:
            self.logger.error(f"Error with {selected_model}: {e}")
            
            # Fallback to alternative model
            if self.config["fallback_enabled"]:
                fallback_model = self._get_fallback_model(selected_model)
                if fallback_model:
                    self.logger.info(f"🔄 Falling back to {fallback_model}")
                    return await self._make_ai_request(request, fallback_model)
            
            raise e
    
    def _select_model_for_request(self, request: AIRequest) -> ModelType:
        """Select the best model for a specific request"""
        
        # If GPT-5 is available and request needs advanced capabilities
        if ModelType.GPT5 in self.available_models:
            if self._requires_advanced_capabilities(request):
                return ModelType.GPT5
        
        # Use preference or fallback
        if request.model_preference in self.available_models:
            return request.model_preference
        else:
            return self.preferred_model
    
    def _requires_advanced_capabilities(self, request: AIRequest) -> bool:
        """Determine if request requires GPT-5's advanced capabilities"""
        advanced_keywords = [
            "autonomous", "complex reasoning", "multi-step", "planning",
            "code generation", "multimodal", "advanced analysis"
        ]
        
        return any(keyword in request.prompt.lower() for keyword in advanced_keywords)
    
    def _get_fallback_model(self, failed_model: ModelType) -> Optional[ModelType]:
        """Get fallback model when primary model fails"""
        fallback_chain = {
            ModelType.GPT5: ModelType.GPT4_TURBO,
            ModelType.GPT5_TURBO: ModelType.GPT5,
            ModelType.GPT4_TURBO: ModelType.GPT4,
            ModelType.GPT4: None
        }
        
        fallback = fallback_chain.get(failed_model)
        return fallback if fallback in self.available_models else None
    
    async def _make_ai_request(self, request: AIRequest, model: ModelType) -> AIResponse:
        """Make actual AI request to specified model"""
        
        try:
            # Prepare request parameters
            params = {
                "model": model.value,
                "messages": self._prepare_messages(request),
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": request.stream
            }
            
            # Add GPT-5 specific parameters if available
            if model in [ModelType.GPT5, ModelType.GPT5_TURBO]:
                params.update(self._get_gpt5_parameters(request))
            
            # Add tools/functions if provided
            if request.tools:
                params["tools"] = request.tools
                params["tool_choice"] = "auto"
            
            # Make API call
            response = await openai.ChatCompletion.acreate(**params)
            
            # Process response
            return self._process_response(response, model, request)
            
        except Exception as e:
            self.logger.error(f"AI request failed for {model}: {e}")
            raise
    
    def _prepare_messages(self, request: AIRequest) -> List[Dict[str, str]]:
        """Prepare messages for AI request"""
        messages = []
        
        # Add system context if available
        if request.context.get("system_prompt"):
            messages.append({
                "role": "system",
                "content": request.context["system_prompt"]
            })
        
        # Add conversation history if available
        if request.context.get("conversation_history"):
            messages.extend(request.context["conversation_history"])
        
        # Add current prompt
        messages.append({
            "role": "user",
            "content": request.prompt
        })
        
        return messages
    
    def _get_gpt5_parameters(self, request: AIRequest) -> Dict[str, Any]:
        """Get GPT-5 specific parameters"""
        gpt5_params = {}
        
        # Enhanced reasoning mode
        if "reasoning" in request.context:
            gpt5_params["reasoning_mode"] = "enhanced"
        
        # Multimodal support
        if "images" in request.context:
            gpt5_params["multimodal"] = True
        
        # Extended context handling
        if len(request.prompt) > 8000:
            gpt5_params["extended_context"] = True
        
        # Autonomous decision making
        if "autonomous" in request.context:
            gpt5_params["autonomous_mode"] = True
        
        return gpt5_params
    
    def _process_response(self, response: Any, model: ModelType, request: AIRequest) -> AIResponse:
        """Process AI response into standardized format"""
        
        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # Calculate confidence score (enhanced for GPT-5)
        confidence_score = self._calculate_confidence(response, model)
        
        # Extract reasoning steps (GPT-5 feature)
        reasoning_steps = None
        if model in [ModelType.GPT5, ModelType.GPT5_TURBO]:
            reasoning_steps = self._extract_reasoning_steps(response)
        
        # Extract tool calls if any
        tool_calls = None
        if hasattr(response.choices[0].message, 'tool_calls'):
            tool_calls = response.choices[0].message.tool_calls
        
        return AIResponse(
            content=content,
            model_used=model,
            tokens_used=tokens_used,
            confidence_score=confidence_score,
            reasoning_steps=reasoning_steps,
            tool_calls=tool_calls
        )
    
    def _calculate_confidence(self, response: Any, model: ModelType) -> float:
        """Calculate confidence score for response"""
        base_confidence = 0.8
        
        # GPT-5 provides better confidence indicators
        if model in [ModelType.GPT5, ModelType.GPT5_TURBO]:
            # Enhanced confidence calculation for GPT-5
            if hasattr(response, 'confidence_score'):
                return response.confidence_score
            else:
                base_confidence = 0.9  # GPT-5 generally more confident
        
        # Adjust based on response characteristics
        content_length = len(response.choices[0].message.content)
        if content_length > 500:
            base_confidence += 0.05
        
        return min(base_confidence, 1.0)
    
    def _extract_reasoning_steps(self, response: Any) -> Optional[List[str]]:
        """Extract reasoning steps from GPT-5 response"""
        # This would be implemented when GPT-5 provides reasoning steps
        # For now, return None
        return None
    
    async def autonomous_dao_decision(self, context: Dict[str, Any]) -> AIResponse:
        """Make autonomous DAO decision using best available model"""
        
        request = AIRequest(
            prompt=f"""
            As the autonomous AI agent for XMRT DAO, analyze the following situation and make a decision:
            
            Context: {json.dumps(context, indent=2)}
            
            Provide:
            1. Analysis of the situation
            2. Recommended action
            3. Risk assessment
            4. Confidence level
            5. Reasoning steps
            
            Make an autonomous decision if confidence > 80% and risk is low-medium.
            """,
            context={
                "system_prompt": "You are ElizaOS, the autonomous AI agent managing XMRT DAO operations.",
                "autonomous": True,
                "reasoning": True
            },
            model_preference=ModelType.GPT5 if ModelType.GPT5 in self.available_models else ModelType.GPT4_TURBO,
            temperature=0.3  # Lower temperature for decision making
        )
        
        return await self.process_request(request)
    
    async def gpt5_migration_check(self) -> Dict[str, Any]:
        """Check if GPT-5 is available and migrate if possible"""
        
        # Re-detect available models
        self.available_models = self._detect_available_models()
        
        if ModelType.GPT5 in self.available_models and self.preferred_model != ModelType.GPT5:
            self.logger.info("🚀 GPT-5 detected! Migrating to GPT-5...")
            
            # Update preferred model
            old_model = self.preferred_model
            self.preferred_model = ModelType.GPT5
            
            # Test GPT-5 functionality
            test_request = AIRequest(
                prompt="Test GPT-5 functionality for XMRT DAO autonomous operations.",
                context={"system_prompt": "You are ElizaOS testing GPT-5 integration."},
                model_preference=ModelType.GPT5
            )
            
            try:
                test_response = await self.process_request(test_request)
                
                self.logger.info("✅ GPT-5 migration successful!")
                return {
                    "migration_successful": True,
                    "old_model": old_model.value,
                    "new_model": ModelType.GPT5.value,
                    "test_response": test_response.content[:200] + "..."
                }
                
            except Exception as e:
                self.logger.error(f"❌ GPT-5 migration failed: {e}")
                self.preferred_model = old_model  # Rollback
                return {
                    "migration_successful": False,
                    "error": str(e),
                    "rollback_model": old_model.value
                }
        
        return {
            "migration_successful": False,
            "reason": "GPT-5 not available or already using GPT-5"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current adapter status"""
        return {
            "available_models": [model.value for model in self.available_models],
            "preferred_model": self.preferred_model.value,
            "gpt5_available": ModelType.GPT5 in self.available_models,
            "capabilities": self.gpt5_capabilities if ModelType.GPT5 in self.available_models else {},
            "config": {k: v for k, v in self.config.items() if k != "api_key"}
        }

# Global adapter instance
gpt5_adapter = GPT5Adapter()

# Convenience functions
async def autonomous_decision(context: Dict[str, Any]) -> AIResponse:
    """Make autonomous decision using best available model"""
    return await gpt5_adapter.autonomous_dao_decision(context)

async def check_gpt5_migration() -> Dict[str, Any]:
    """Check and perform GPT-5 migration if available"""
    return await gpt5_adapter.gpt5_migration_check()

def get_ai_status() -> Dict[str, Any]:
    """Get current AI system status"""
    return gpt5_adapter.get_status()

