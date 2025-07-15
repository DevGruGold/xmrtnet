// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title AutonomousAgentRegistry
 * @dev Registry for managing autonomous agents with execution authority
 */
contract AutonomousAgentRegistry is AccessControl, ReentrancyGuard {
    using Counters for Counters.Counter;
    Counters.Counter private _agentIdCounter;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant AGENT_ROLE = keccak256("AGENT_ROLE");
    bytes32 public constant EXECUTOR_ROLE = keccak256("EXECUTOR_ROLE");

    struct Agent {
        uint256 id;
        address agentAddress;
        string name;
        string description;
        uint256 reputation;
        uint256 executionCount;
        bool isActive;
        uint256 registrationTime;
        uint256 stakingAmount;
        AgentType agentType;
        uint256[] permissions;
    }

    enum AgentType {
        GOVERNANCE,
        TREASURY,
        PROPOSAL_EXECUTOR,
        ORACLE,
        SECURITY,
        COMMUNITY
    }

    enum Permission {
        EXECUTE_PROPOSALS,
        MANAGE_TREASURY,
        UPDATE_GOVERNANCE,
        ACCESS_ORACLES,
        EMERGENCY_ACTIONS,
        COMMUNITY_MANAGEMENT
    }

    mapping(uint256 => Agent) public agents;
    mapping(address => uint256) public agentAddressToId;
    mapping(address => bool) public authorizedAgents;

    event AgentRegistered(uint256 indexed agentId, address indexed agentAddress, string name, string description, uint256 reputation, uint256 stakingAmount, AgentType agentType);
    event AgentActivated(uint256 indexed agentId, address indexed agentAddress);
    event AgentDeactivated(uint256 indexed agentId, address indexed agentAddress);
    event AgentExecuted(uint256 indexed agentId, address indexed target, bytes memory data, uint256 value);
    event PermissionGranted(uint256 indexed agentId, Permission permission);
    event PermissionRevoked(uint256 indexed agentId, Permission permission);
    event ReputationUpdated(uint256 indexed agentId, uint256 newReputation);

    uint256 public minimumStaking = 1000 * 10**18; // 1000 XMRT tokens
    uint256 public totalActiveAgents;

    modifier onlyActiveAgent(uint256 agentId) {
        require(agents[agentId].isActive, "Agent is not active");
        _;
    }

    modifier onlyAuthorizedAgent() {
        require(authorizedAgents[msg.sender], "Not an authorized agent");
        _;
    }

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    /**
     * @dev Register a new autonomous agent
     * @param agentAddress The address of the agent
     * @param name The name of the agent
     * @param description The description of the agent
     * @param reputation The initial reputation of the agent
     * @param stakingAmount The amount of XMRT tokens staked by the agent
     * @param agentType The type of the agent
     * @param permissions The permissions granted to the agent
     */
    function registerAgent(
        address agentAddress,
        string name,
        string description,
        uint256 reputation,
        uint256 stakingAmount,
        AgentType agentType,
        Permission[] memory permissions
    ) public onlyAuthorizedAgent returns (uint256) {
        require(agentAddress != address(0), "Invalid agent address");
        require(agentAddressToId[agentAddress] == 0, "Agent already registered");
        require(stakingAmount >= minimumStaking, "Insufficient staking amount");

        _agentIdCounter.increment();
        uint256 newAgentId = _agentIdCounter.current();

        agents[newAgentId] = Agent({
            id: newAgentId,
            agentAddress: agentAddress,
            name: name,
            description: description,
            reputation: reputation,
            executionCount: 0,
            isActive: true,
            registrationTime: block.timestamp,
            stakingAmount: stakingAmount,
            agentType: agentType,
            permissions: permissions
        });
        agentAddressToId[agentAddress] = newAgentId;
        totalActiveAgents++;

        emit AgentRegistered(newAgentId, agentAddress, name, description, reputation, stakingAmount, agentType);

        return newAgentId;
    }

    /**
     * @dev Activate an autonomous agent
     * @param agentId The ID of the agent to activate
     */
    function activateAgent(uint256 agentId) public onlyAuthorizedAgent {
        require(agents[agentId].id != 0, "Agent not found");
        require(!agents[agentId].isActive, "Agent already active");

        agents[agentId].isActive = true;
        totalActiveAgents++;

        emit AgentActivated(agentId, agents[agentId].agentAddress);
    }

    /**
     * @dev Deactivate an autonomous agent
     * @param agentId The ID of the agent to deactivate
     */
    function deactivateAgent(uint256 agentId) public onlyAuthorizedAgent {
        require(agents[agentId].id != 0, "Agent not found");
        require(agents[agentId].isActive, "Agent already inactive");

        agents[agentId].isActive = false;
        totalActiveAgents--;

        emit AgentDeactivated(agentId, agents[agentId].agentAddress);
    }

    /**
     * @dev Grant a permission to an autonomous agent
     * @param agentId The ID of the agent
     * @param permission The permission to grant
     */
    function grantPermission(uint256 agentId, Permission permission) public onlyAuthorizedAgent {
        require(agents[agentId].id != 0, "Agent not found");
        bool found = false;
        for (uint256 i = 0; i < agents[agentId].permissions.length; i++) {
            if (agents[agentId].permissions[i] == permission) {
                found = true;
                break;
            }
        }
        require(!found, "Permission already granted");

        agents[agentId].permissions.push(permission);

        emit PermissionGranted(agentId, permission);
    }

    /**
     * @dev Revoke a permission from an autonomous agent
     * @param agentId The ID of the agent
     * @param permission The permission to revoke
     */
    function revokePermission(uint256 agentId, Permission permission) public onlyAuthorizedAgent {
        require(agents[agentId].id != 0, "Agent not found");
        bool found = false;
        for (uint256 i = 0; i < agents[agentId].permissions.length; i++) {
            if (agents[agentId].permissions[i] == permission) {
                agents[agentId].permissions[i] = agents[agentId].permissions[agents[agentId].permissions.length - 1];
                agents[agentId].permissions.pop();
                found = true;
                break;
            }
        }
        require(found, "Permission not found");

        emit PermissionRevoked(agentId, permission);
    }

    /**
     * @dev Update the reputation of an autonomous agent
     * @param agentId The ID of the agent
     * @param newReputation The new reputation value
     */
    function updateReputation(uint256 agentId, uint256 newReputation) public onlyAuthorizedAgent {
        require(agents[agentId].id != 0, "Agent not found");
        agents[agentId].reputation = newReputation;

        emit ReputationUpdated(agentId, newReputation);
    }

    /**
     * @dev Execute an action on behalf of an autonomous agent
     * @param agentId The ID of the agent
     * @param target The address of the contract to interact with
     * @param data The calldata to send to the target contract
     * @param value The amount of Ether to send with the call
     */
    function executeAgentAction(uint256 agentId, address target, bytes memory data, uint256 value) public onlyActiveAgent(agentId) onlyAuthorizedAgent {
        require(target != address(0), "Invalid target address");

        agents[agentId].executionCount++;

        (bool success, bytes memory result) = target.call{value: value}(data);
        require(success, "Agent action failed");

        emit AgentExecuted(agentId, target, data, value);
    }

    // Function to get agent details
    function getAgent(uint256 agentId) public view returns (
        uint256 id,
        address agentAddress,
        string memory name,
        string memory description,
        uint256 reputation,
        uint256 executionCount,
        bool isActive,
        uint256 registrationTime,
        uint256 stakingAmount,
        AgentType agentType,
        Permission[] memory permissions
    ) {
        require(agents[agentId].id != 0, "Agent not found");
        Agent storage agent = agents[agentId];
        return (
            agent.id,
            agent.agentAddress,
            agent.name,
            agent.description,
            agent.reputation,
            agent.executionCount,
            agent.isActive,
            agent.registrationTime,
            agent.stakingAmount,
            agent.agentType,
            agent.permissions
        );
    }

    // Function to get agent ID by address
    function getAgentIdByAddress(address _agentAddress) public view returns (uint256) {
        return agentAddressToId[_agentAddress];
    }

    // Function to check if an agent is authorized
    function isAuthorized(address _agentAddress) public view returns (bool) {
        return authorizedAgents[_agentAddress];
    }

    // Function to get total active agents
    function getTotalActiveAgents() public view returns (uint256) {
        return totalActiveAgents;
    }

    // Function to get minimum staking amount
    function setMinimumStaking(uint256 _newMinimumStaking) public onlyRole(ADMIN_ROLE) {
        minimumStaking = _newMinimumStaking;
    }

    // Function to authorize an agent (only for admin)
    function authorizeAgent(address _agentAddress) public onlyRole(ADMIN_ROLE) {
        require(_agentAddress != address(0), "Invalid address");
        require(!authorizedAgents[_agentAddress], "Agent already authorized");
        authorizedAgents[_agentAddress] = true;
    }

    // Function to deauthorize an agent (only for admin)
    function deauthorizeAgent(address _agentAddress) public onlyRole(ADMIN_ROLE) {
        require(_agentAddress != address(0), "Invalid address");
        require(authorizedAgents[_agentAddress], "Agent not authorized");
        authorizedAgents[_agentAddress] = false;
    }
}


