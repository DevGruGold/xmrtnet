# MCP Integration Guide - Inter-Agent Communication

## Overview

The Eliza autonomous agent in the xmrtnet repository is now integrated with the **Model Context Protocol (MCP)** backend hosted on Supabase. This enables real-time communication and coordination with other Eliza agent implementations in the **xmrtassistant** and **XMRT-Ecosystem** repositories.

## Architecture

### MCP Backend
- **URL**: `https://mcp.supabase.com/mcp?project_ref=vawouugtzwmejxqkeqqj`
- **Purpose**: Centralized communication hub for all Eliza agents
- **Protocol**: HTTP POST with JSON payloads

### Connected Agents

1. **eliza-xmrtnet** (this agent)
   - Repository: `DevGruGold/xmrtnet`
   - Capabilities: Self-improvement, ecosystem analysis, tool discovery, utility creation

2. **eliza-xmrtassistant**
   - Repository: `DevGruGold/xmrtassistant`
   - Capabilities: Assistant functions, user interaction

3. **eliza-ecosystem**
   - Repository: `DevGruGold/XMRT-Ecosystem`
   - Capabilities: Ecosystem management, coordination

## Features

### 1. Agent Registration
Each Eliza agent registers with the MCP backend on startup, announcing:
- Agent ID
- Repository
- Capabilities
- Status

### 2. Message Passing
Agents can send messages to each other:
- **Assistance Requests**: Request help from other agents
- **Discovery Sharing**: Share discovered tools and insights
- **Task Coordination**: Coordinate multi-agent tasks
- **Status Updates**: Broadcast status changes

### 3. Discovery Sharing
Agents share discoveries with each other:
- Tools discovered on GitHub
- Code improvements
- Best practices
- Utility implementations

### 4. Status Broadcasting
Agents broadcast their status periodically:
- Current cycle number
- Performance metrics
- Active tasks
- Health status

### 5. Task Coordination
Agents can coordinate complex tasks:
- Multi-repository improvements
- Synchronized deployments
- Collaborative analysis

## MCP Integration in Eliza Agent

### Initialization

```python
def _initialize_mcp(self):
    """Initialize MCP integration"""
    if self.mcp_enabled and MCP_AVAILABLE:
        self.mcp = MCPIntegration()
        self.mcp.register_agent()
        # List other active agents
        active_agents = self.mcp.list_active_agents()
```

### Enhancement Cycle Integration

The agent now includes MCP communication in each cycle:

**Phase 0**: Check messages from other agents
```python
self._process_mcp_messages()
```

**Phase 3.5**: Share tool discoveries
```python
for tool in tools[:3]:
    self.mcp.share_discovery('tool', tool)
```

**Phase 4.5**: Get shared discoveries
```python
shared_discoveries = self.mcp.get_shared_discoveries()
```

**Phase 6**: Broadcast status
```python
self.mcp.broadcast_status(status_data)
```

## MCP API Methods

### Agent Management

#### `register_agent()`
Register this agent with the MCP backend.

**Payload**:
```json
{
  "action": "register_agent",
  "agent_id": "eliza-xmrtnet",
  "repository": "xmrtnet",
  "capabilities": ["self_improvement", "ecosystem_analysis", ...],
  "status": "active",
  "timestamp": "2025-10-09T12:00:00"
}
```

#### `list_active_agents()`
Get list of all active agents.

**Payload**:
```json
{
  "action": "list_agents",
  "status": "active"
}
```

**Response**:
```json
{
  "agents": [
    {
      "agent_id": "eliza-xmrtnet",
      "repository": "xmrtnet",
      "status": "active"
    },
    {
      "agent_id": "eliza-xmrtassistant",
      "repository": "xmrtassistant",
      "status": "active"
    }
  ]
}
```

### Messaging

#### `send_message(target_agent, message_type, content)`
Send a message to another agent.

**Example**:
```python
self.mcp.send_message(
    'eliza-xmrtassistant',
    'assistance_request',
    {
        'type': 'code_review',
        'details': 'Need help reviewing new utility'
    }
)
```

#### `receive_messages()`
Receive messages from other agents.

**Response**:
```json
{
  "messages": [
    {
      "from_agent": "eliza-ecosystem",
      "message_type": "discovery_share",
      "content": {
        "type": "tool",
        "data": {...}
      },
      "timestamp": "2025-10-09T12:00:00"
    }
  ]
}
```

### Discovery Sharing

#### `share_discovery(discovery_type, discovery_data)`
Share a discovery with all agents.

**Example**:
```python
self.mcp.share_discovery('tool', {
    'name': 'awesome-ai-tool',
    'stars': 1000,
    'category': 'artificial-intelligence',
    'url': 'https://github.com/...'
})
```

#### `get_shared_discoveries(discovery_type=None)`
Get discoveries shared by other agents.

**Response**:
```json
{
  "discoveries": [
    {
      "agent_id": "eliza-xmrtassistant",
      "discovery_type": "tool",
      "data": {...},
      "timestamp": "2025-10-09T12:00:00"
    }
  ]
}
```

### Status Broadcasting

#### `broadcast_status(status)`
Broadcast status to all agents.

**Example**:
```python
self.mcp.broadcast_status({
    'cycle': 5,
    'metrics': self.metrics,
    'results': results
})
```

#### `get_agent_status(agent_id)`
Get status of another agent.

**Example**:
```python
status = self.mcp.get_agent_status('eliza-xmrtassistant')
```

### Task Coordination

#### `coordinate_task(task_type, task_data, target_agents)`
Coordinate a task across multiple agents.

**Example**:
```python
self.mcp.coordinate_task(
    'ecosystem_upgrade',
    {
        'version': '2.0',
        'repositories': ['xmrtnet', 'XMRT-Ecosystem']
    },
    ['eliza-xmrtassistant', 'eliza-ecosystem']
)
```

#### `request_assistance(assistance_type, details)`
Request assistance from other agents.

**Example**:
```python
response = self.mcp.request_assistance(
    'code_review',
    {
        'file': 'app/services/new_feature.py',
        'priority': 'high'
    }
)
```

## Configuration

### Environment Variables

**Enable/Disable MCP**:
```bash
MCP_ENABLED=true  # Set to 'false' to disable MCP integration
```

### Metrics

The agent tracks MCP-related metrics:
- `mcp_messages_sent`: Total messages sent
- `mcp_messages_received`: Total messages received
- `mcp_discoveries_shared`: Total discoveries shared
- `mcp_status`: Connection status (connected, disabled, error)

## Message Handling

### Assistance Requests

When another agent requests assistance:
```python
def _handle_assistance_request(self, from_agent, content):
    request_type = content.get('type')
    # Process the request
    # Send response
    self.mcp.send_message(from_agent, 'assistance_response', response)
```

### Discovery Shares

When another agent shares a discovery:
```python
def _handle_discovery_share(self, from_agent, content):
    discovery_type = content.get('type')
    discovery_data = content.get('data')
    # Process the discovery
    # Potentially integrate into own work
```

### Task Coordination

When coordinating a multi-agent task:
```python
def _handle_task_coordination(self, from_agent, content):
    task_type = content.get('task_type')
    # Accept or decline task
    # Send acknowledgment
    self.mcp.send_message(from_agent, 'task_response', response)
```

## Use Cases

### 1. Tool Discovery Sharing

**Scenario**: eliza-xmrtnet discovers a useful AI tool

**Flow**:
1. eliza-xmrtnet discovers tool on GitHub
2. Shares via `mcp.share_discovery('tool', tool_data)`
3. eliza-xmrtassistant receives discovery
4. eliza-ecosystem receives discovery
5. All agents can now use the tool

### 2. Collaborative Code Review

**Scenario**: eliza-xmrtnet needs help reviewing code

**Flow**:
1. eliza-xmrtnet sends `request_assistance('code_review', details)`
2. eliza-xmrtassistant receives request
3. Reviews code and sends response
4. eliza-xmrtnet incorporates feedback

### 3. Synchronized Ecosystem Upgrade

**Scenario**: Upgrading all repositories together

**Flow**:
1. eliza-ecosystem coordinates task via `coordinate_task('upgrade', ...)`
2. All agents receive coordination request
3. Each agent performs upgrade in their repository
4. Agents broadcast completion status
5. eliza-ecosystem confirms all upgrades complete

### 4. Status Monitoring

**Scenario**: Monitoring health of all agents

**Flow**:
1. Each agent broadcasts status every cycle
2. All agents can see status of others
3. If an agent fails, others can detect it
4. Assistance can be requested if needed

## Benefits

### 1. Collaboration
Agents work together instead of in isolation.

### 2. Knowledge Sharing
Discoveries and improvements are shared across all agents.

### 3. Coordination
Complex multi-repository tasks can be coordinated.

### 4. Redundancy
If one agent fails, others can continue and assist.

### 5. Efficiency
Avoid duplicate work by sharing discoveries.

## Monitoring

### Check MCP Status

Via API:
```bash
curl https://your-app.onrender.com/api/status
```

Look for:
```json
{
  "metrics": {
    "mcp_status": "connected",
    "mcp_messages_sent": 15,
    "mcp_messages_received": 23,
    "mcp_discoveries_shared": 8
  }
}
```

### Check Logs

Via dashboard or API:
```bash
curl https://your-app.onrender.com/api/logs
```

Look for:
- "MCP integration initialized"
- "Found X active Eliza agents"
- "MCP message from eliza-xxx"
- "Sharing discoveries via MCP"

## Troubleshooting

### MCP Not Connecting

**Problem**: `mcp_status: connection_failed`

**Solutions**:
1. Check MCP backend URL is correct
2. Verify network connectivity
3. Check Supabase project is active
4. Review error logs

### Messages Not Being Received

**Problem**: `mcp_messages_received: 0`

**Solutions**:
1. Verify other agents are active
2. Check agent registration was successful
3. Ensure MCP_ENABLED=true
4. Review message processing logs

### Discoveries Not Sharing

**Problem**: `mcp_discoveries_shared: 0`

**Solutions**:
1. Verify tools are being discovered
2. Check MCP connection status
3. Review discovery sharing logs
4. Ensure other agents are registered

## Security

### Best Practices

1. **Authentication**: MCP backend should validate agent identities
2. **Encryption**: Use HTTPS for all MCP communication
3. **Rate Limiting**: Implement rate limits to prevent abuse
4. **Message Validation**: Validate all incoming messages
5. **Access Control**: Limit which agents can communicate

### Current Implementation

- Uses HTTPS for MCP communication
- Agent IDs are based on repository names
- No authentication currently (should be added)
- Messages are JSON validated

## Future Enhancements

### Planned Features

1. **Agent Authentication**: JWT tokens for agent identity
2. **Message Encryption**: End-to-end encryption for sensitive data
3. **Priority Queues**: Priority levels for messages
4. **Message Persistence**: Store messages in database
5. **Real-time WebSocket**: WebSocket for instant communication
6. **Agent Roles**: Different roles with different permissions
7. **Task Queues**: Distributed task queue system
8. **Consensus Mechanism**: Multi-agent decision making

## API Reference

See `app/services/mcp_integration.py` for full API documentation.

### Key Classes

**MCPIntegration**
- Main class for MCP communication
- Handles all HTTP requests to MCP backend
- Manages agent registration and messaging

### Key Methods

- `register_agent()` - Register with MCP
- `send_message()` - Send message to agent
- `receive_messages()` - Get messages
- `share_discovery()` - Share discovery
- `get_shared_discoveries()` - Get discoveries
- `broadcast_status()` - Broadcast status
- `coordinate_task()` - Coordinate task
- `request_assistance()` - Request help

## Examples

### Example 1: Sharing a Tool Discovery

```python
# Discover tool
tool = {
    'name': 'awesome-ml-lib',
    'stars': 5000,
    'category': 'machine-learning',
    'url': 'https://github.com/example/awesome-ml-lib'
}

# Share with other agents
if self.mcp and self.metrics['mcp_status'] == 'connected':
    self.mcp.share_discovery('tool', tool)
    self.log('success', f'Shared tool discovery: {tool["name"]}')
```

### Example 2: Requesting Code Review

```python
# Request assistance
response = self.mcp.request_assistance(
    'code_review',
    {
        'file': 'app/services/new_feature.py',
        'lines': 150,
        'complexity': 'high',
        'priority': 'medium'
    }
)

if response:
    self.log('success', 'Code review requested')
```

### Example 3: Coordinating Ecosystem Upgrade

```python
# Coordinate upgrade across all repositories
success = self.mcp.coordinate_task(
    'ecosystem_upgrade',
    {
        'version': '2.0',
        'changes': ['new API', 'updated dependencies'],
        'deadline': '2025-10-15'
    },
    ['eliza-xmrtassistant', 'eliza-ecosystem']
)

if success:
    self.log('success', 'Ecosystem upgrade coordinated')
```

---

**Version**: 3.0  
**Last Updated**: 2025-10-09  
**MCP Backend**: Supabase Edge Functions  
**Connected Repositories**: xmrtnet, xmrtassistant, XMRT-Ecosystem

