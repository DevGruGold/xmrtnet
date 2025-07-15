// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "./DAO_Governance.sol";
import "./DAO_Treasury.sol";

/**
 * @title Governance
 * @dev Main governance contract that orchestrates DAO operations and AI agent interactions
 */
contract Governance is
    Initializable,
    AccessControlUpgradeable,
    ReentrancyGuardUpgradeable,
    PausableUpgradeable,
    UUPSUpgradeable
{
    // Constants
    address public constant DOMAIN_WALLET = 0x7099F848b614d0d510BeAB53b3bE409cbd720dF5;
    address public constant AI_LEADER = 0x77307DFbc436224d5e6f2048d2b6bDfA66998a15;

    // Roles
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant AI_AGENT_ROLE = keccak256("AI_AGENT_ROLE");
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");

    // Contract references
    DAO_Governance public daoGovernance;
    DAO_Treasury public daoTreasury;

    // AI agent configuration
    struct AIAgent {
        address agentAddress;
        string name;
        string role;
        bool isActive;
        uint256 actionsExecuted;
        uint256 lastActionTime;
    }

    mapping(address => AIAgent) public aiAgents;
    address[] public aiAgentList;

    // Events
    event AIAgentRegistered(address indexed agent, string name, string role);
    event AIAgentDeactivated(address indexed agent);
    event AIActionExecuted(address indexed agent, string actionType, bytes data);
    event GovernanceContractSet(address indexed governance);
    event TreasuryContractSet(address indexed treasury);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(
        address _daoGovernance,
        address _daoTreasury
    ) public initializer {
        __AccessControl_init();
        __ReentrancyGuard_init();
        __Pausable_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(ORACLE_ROLE, msg.sender);

        // Set contract references
        if (_daoGovernance != address(0)) {
            daoGovernance = DAO_Governance(_daoGovernance);
        }
        if (_daoTreasury != address(0)) {
            daoTreasury = DAO_Treasury(_daoTreasury);
        }

        // Register AI_LEADER as default AI agent
        _registerAIAgent(AI_LEADER, "Eliza", "Primary AI Agent");
    }

    /**
     * @dev Register a new AI agent
     */
    function registerAIAgent(
        address agentAddress,
        string memory name,
        string memory role
    ) external onlyRole(ADMIN_ROLE) {
        _registerAIAgent(agentAddress, name, role);
    }

    /**
     * @dev Internal function to register AI agent
     */
    function _registerAIAgent(
        address agentAddress,
        string memory name,
        string memory role
    ) internal {
        require(agentAddress != address(0), "Invalid agent address");
        require(!aiAgents[agentAddress].isActive, "Agent already registered");

        aiAgents[agentAddress] = AIAgent({
            agentAddress: agentAddress,
            name: name,
            role: role,
            isActive: true,
            actionsExecuted: 0,
            lastActionTime: 0
        });

        aiAgentList.push(agentAddress);
        _grantRole(AI_AGENT_ROLE, agentAddress);

        emit AIAgentRegistered(agentAddress, name, role);
    }

    /**
     * @dev Deactivate an AI agent
     */
    function deactivateAIAgent(address agentAddress) external onlyRole(ADMIN_ROLE) {
        require(aiAgents[agentAddress].isActive, "Agent not active");
        
        aiAgents[agentAddress].isActive = false;
        _revokeRole(AI_AGENT_ROLE, agentAddress);

        emit AIAgentDeactivated(agentAddress);
    }

    /**
     * @dev Execute AI-triggered action with logging
     */
    function executeAIAction(
        string memory actionType,
        bytes memory actionData
    ) external onlyRole(AI_AGENT_ROLE) whenNotPaused {
        require(aiAgents[msg.sender].isActive, "Agent not active");

        // Update agent statistics
        aiAgents[msg.sender].actionsExecuted++;
        aiAgents[msg.sender].lastActionTime = block.timestamp;

        emit AIActionExecuted(msg.sender, actionType, actionData);
    }

    /**
     * @dev Set DAO Governance contract
     */
    function setDAOGovernance(address _daoGovernance) external onlyRole(ADMIN_ROLE) {
        require(_daoGovernance != address(0), "Invalid address");
        daoGovernance = DAO_Governance(_daoGovernance);
        emit GovernanceContractSet(_daoGovernance);
    }

    /**
     * @dev Set DAO Treasury contract
     */
    function setDAOTreasury(address _daoTreasury) external onlyRole(ADMIN_ROLE) {
        require(_daoTreasury != address(0), "Invalid address");
        daoTreasury = DAO_Treasury(_daoTreasury);
        emit TreasuryContractSet(_daoTreasury);
    }

    /**
     * @dev Get AI agent information
     */
    function getAIAgent(address agentAddress) external view returns (
        string memory name,
        string memory role,
        bool isActive,
        uint256 actionsExecuted,
        uint256 lastActionTime
    ) {
        AIAgent storage agent = aiAgents[agentAddress];
        return (
            agent.name,
            agent.role,
            agent.isActive,
            agent.actionsExecuted,
            agent.lastActionTime
        );
    }

    /**
     * @dev Get all AI agents
     */
    function getAllAIAgents() external view returns (address[] memory) {
        return aiAgentList;
    }

    /**
     * @dev Pause contract
     */
    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }

    /**
     * @dev Unpause contract
     */
    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }

    /**
     * @dev Authorize contract upgrades
     */
    function _authorizeUpgrade(address newImplementation) internal override onlyRole(ADMIN_ROLE) {}
}
