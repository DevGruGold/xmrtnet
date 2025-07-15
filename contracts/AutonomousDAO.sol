// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";
import "./XMRT.sol";
import "./AI_Agent_Interface.sol";

/**
 * @title AutonomousDAO
 * @dev Fully autonomous DAO with AI agent execution authority and self-governance
 * @notice This contract enables complete autonomous operation with agent-driven decisions
 */
contract AutonomousDAO is
    Initializable,
    AccessControlUpgradeable,
    ReentrancyGuardUpgradeable,
    PausableUpgradeable,
    UUPSUpgradeable
{
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;

    // Enhanced Roles for Autonomous Operation
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant AI_AGENT_ROLE = keccak256("AI_AGENT_ROLE");
    bytes32 public constant AUTONOMOUS_EXECUTOR_ROLE = keccak256("AUTONOMOUS_EXECUTOR_ROLE");
    bytes32 public constant GUARDIAN_ROLE = keccak256("GUARDIAN_ROLE");
    bytes32 public constant TREASURY_MANAGER_ROLE = keccak256("TREASURY_MANAGER_ROLE");
    bytes32 public constant PROPOSAL_CREATOR_ROLE = keccak256("PROPOSAL_CREATOR_ROLE");

    // Autonomous Execution States
    enum ExecutionMode {
        Manual,           // Requires human approval
        SemiAutonomous,   // Agent can execute with constraints
        FullyAutonomous   // Agent has complete execution authority
    }

    // Enhanced Proposal States
    enum ProposalState {
        Pending,
        Active,
        Queued,
        Executed,
        Canceled,
        Defeated,
        AutoExecuting,    // Being executed by agent
        AutoExecuted      // Successfully executed by agent
    }

    // Agent Execution Authority Levels
    enum AgentAuthority {
        None,
        Limited,      // Can execute routine operations
        Moderate,     // Can execute treasury operations up to limit
        Full          // Can execute any approved proposal
    }

    // Autonomous Proposal Structure
    struct AutonomousProposal {
        uint256 id;
        address proposer;
        address target;
        uint256 value;
        bytes callData;
        string description;
        uint256 startTime;
        uint256 endTime;
        uint256 executionTime;
        uint256 votesFor;
        uint256 votesAgainst;
        uint256 quorumRequired;
        uint256 thresholdRequired;
        bool executed;
        bool canceled;
        bool autoExecutable;
        AgentAuthority requiredAuthority;
        ExecutionMode executionMode;
        address assignedAgent;
        uint256 executionDeadline;
        mapping(address => bool) hasVoted;
        mapping(address => uint256) votingPower;
        mapping(address => bool) agentApprovals;
    }

    // Agent Registration Structure
    struct RegisteredAgent {
        address agentAddress;
        string name;
        string description;
        AgentAuthority authority;
        bool active;
        uint256 registrationTime;
        uint256 executionCount;
        uint256 successRate;
        uint256 stakingAmount;
        address[] endorsers;
    }

    // Autonomous Execution Parameters
    struct AutonomousConfig {
        ExecutionMode defaultMode;
        uint256 autoExecutionDelay;
        uint256 maxAutoExecutionValue;
        uint256 agentStakingRequirement;
        uint256 consensusThreshold;
        bool emergencyPause;
    }

    // State Variables
    XMRT public xmrtToken;
    AI_Agent_Interface public agentInterface;

    uint256 public proposalCount;
    uint256 public agentCount;

    AutonomousConfig public autonomousConfig;

    mapping(uint256 => AutonomousProposal) public proposals;
    mapping(address => RegisteredAgent) public registeredAgents;
    mapping(address => bool) public isRegisteredAgent;
    mapping(uint256 => address[]) public proposalAgentVotes;
    mapping(address => uint256[]) public agentExecutionHistory;

    // Multi-signature for critical operations
    mapping(bytes32 => mapping(address => bool)) public multiSigApprovals;
    mapping(bytes32 => uint256) public multiSigApprovalCount;

    // Autonomous execution queue
    uint256[] public executionQueue;
    mapping(uint256 => bool) public inExecutionQueue;

    // Events
    event ProposalCreated(uint256 indexed proposalId, address indexed proposer, address indexed assignedAgent);
    event AgentRegistered(address indexed agent, AgentAuthority authority);
    event AutonomousExecution(uint256 indexed proposalId, address indexed agent, bool success);
    event ExecutionModeChanged(ExecutionMode oldMode, ExecutionMode newMode);
    event AgentAuthorityUpdated(address indexed agent, AgentAuthority oldAuthority, AgentAuthority newAuthority);
    event EmergencyPauseTriggered(address indexed trigger, string reason);
    event MultiSigApproval(bytes32 indexed operationHash, address indexed approver, uint256 approvalCount);

    // Modifiers
    modifier onlyRegisteredAgent() {
        require(isRegisteredAgent[msg.sender], "Not a registered agent");
        require(registeredAgents[msg.sender].active, "Agent not active");
        _;
    }

    modifier onlyAuthorizedAgent(AgentAuthority requiredAuthority) {
        require(isRegisteredAgent[msg.sender], "Not a registered agent");
        require(registeredAgents[msg.sender].authority >= requiredAuthority, "Insufficient agent authority");
        _;
    }

    modifier whenNotEmergencyPaused() {
        require(!autonomousConfig.emergencyPause, "Emergency pause active");
        _;
    }

    /**
     * @dev Initialize the autonomous DAO
     */
    function initialize(
        address _xmrtToken,
        address _agentInterface,
        ExecutionMode _defaultMode
    ) public initializer {
        __AccessControl_init();
        __ReentrancyGuard_init();
        __Pausable_init();
        __UUPSUpgradeable_init();

        xmrtToken = XMRT(_xmrtToken);
        agentInterface = AI_Agent_Interface(_agentInterface);

        autonomousConfig = AutonomousConfig({
            defaultMode: _defaultMode,
            autoExecutionDelay: 1 hours,
            maxAutoExecutionValue: 10000 * 10**18, // 10,000 XMRT
            agentStakingRequirement: 1000 * 10**18, // 1,000 XMRT
            consensusThreshold: 3, // Minimum 3 agent approvals
            emergencyPause: false
        });

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(GUARDIAN_ROLE, msg.sender);
    }

    /**
     * @dev Register a new AI agent with execution authority
     */
    function registerAgent(
        address _agentAddress,
        string memory _name,
        string memory _description,
        AgentAuthority _authority
    ) external onlyRole(ADMIN_ROLE) {
        require(_agentAddress != address(0), "Invalid agent address");
        require(!isRegisteredAgent[_agentAddress], "Agent already registered");
        require(xmrtToken.balanceOf(_agentAddress) >= autonomousConfig.agentStakingRequirement, "Insufficient staking");

        registeredAgents[_agentAddress] = RegisteredAgent({
            agentAddress: _agentAddress,
            name: _name,
            description: _description,
            authority: _authority,
            active: true,
            registrationTime: block.timestamp,
            executionCount: 0,
            successRate: 100, // Start with 100% success rate
            stakingAmount: autonomousConfig.agentStakingRequirement,
            endorsers: new address[](0)
        });

        isRegisteredAgent[_agentAddress] = true;
        agentCount++;

        _grantRole(AI_AGENT_ROLE, _agentAddress);
        if (_authority >= AgentAuthority.Moderate) {
            _grantRole(AUTONOMOUS_EXECUTOR_ROLE, _agentAddress);
        }

        // Stake tokens for agent registration
        xmrtToken.transferFrom(_agentAddress, address(this), autonomousConfig.agentStakingRequirement);

        emit AgentRegistered(_agentAddress, _authority);
    }

    /**
     * @dev Create autonomous proposal with agent assignment
     */
    function createAutonomousProposal(
        address _target,
        uint256 _value,
        bytes memory _callData,
        string memory _description,
        AgentAuthority _requiredAuthority,
        ExecutionMode _executionMode
    ) external returns (uint256) {
        require(hasRole(PROPOSAL_CREATOR_ROLE, msg.sender) || hasRole(AI_AGENT_ROLE, msg.sender), "Unauthorized");
        require(_target != address(0), "Invalid target");

        proposalCount++;
        uint256 proposalId = proposalCount;

        AutonomousProposal storage proposal = proposals[proposalId];
        proposal.id = proposalId;
        proposal.proposer = msg.sender;
        proposal.target = _target;
        proposal.value = _value;
        proposal.callData = _callData;
        proposal.description = _description;
        proposal.startTime = block.timestamp;
        proposal.endTime = block.timestamp + 7 days;
        proposal.executionTime = 0;
        proposal.quorumRequired = (xmrtToken.totalSupply() * 1000) / 10000; // 10%
        proposal.thresholdRequired = 5000; // 50%
        proposal.executed = false;
        proposal.canceled = false;
        proposal.autoExecutable = (_executionMode != ExecutionMode.Manual);
        proposal.requiredAuthority = _requiredAuthority;
        proposal.executionMode = _executionMode;
        proposal.executionDeadline = block.timestamp + 30 days;

        // Auto-assign agent based on authority level
        address assignedAgent = _findBestAgent(_requiredAuthority);
        proposal.assignedAgent = assignedAgent;

        // Add to execution queue if fully autonomous
        if (_executionMode == ExecutionMode.FullyAutonomous && assignedAgent != address(0)) {
            executionQueue.push(proposalId);
            inExecutionQueue[proposalId] = true;
        }

        emit ProposalCreated(proposalId, msg.sender, assignedAgent);
        return proposalId;
    }

    /**
     * @dev Autonomous execution by registered agents
     */
    function executeAutonomously(uint256 _proposalId) external onlyRegisteredAgent whenNotEmergencyPaused nonReentrant {
        AutonomousProposal storage proposal = proposals[_proposalId];
        require(proposal.id != 0, "Proposal does not exist");
        require(!proposal.executed && !proposal.canceled, "Proposal already finalized");
        require(proposal.autoExecutable, "Proposal not auto-executable");
        require(proposal.assignedAgent == msg.sender || proposal.executionMode == ExecutionMode.FullyAutonomous, "Not assigned agent");
        require(registeredAgents[msg.sender].authority >= proposal.requiredAuthority, "Insufficient authority");
        require(block.timestamp >= proposal.endTime + autonomousConfig.autoExecutionDelay, "Execution delay not met");

        // Check if proposal passed
        bool passed = _checkProposalPassed(proposal);
        require(passed, "Proposal did not pass");

        // Execute the proposal
        proposal.executed = true;
        proposal.executionTime = block.timestamp;

        bool success = _executeProposal(proposal);

        // Update agent statistics
        RegisteredAgent storage agent = registeredAgents[msg.sender];
        agent.executionCount++;
        if (success) {
            agent.successRate = ((agent.successRate * (agent.executionCount - 1)) + 100) / agent.executionCount;
        } else {
            agent.successRate = (agent.successRate * (agent.executionCount - 1)) / agent.executionCount;
        }

        // Remove from execution queue
        if (inExecutionQueue[_proposalId]) {
            _removeFromExecutionQueue(_proposalId);
        }

        agentExecutionHistory[msg.sender].push(_proposalId);

        emit AutonomousExecution(_proposalId, msg.sender, success);
    }

    /**
     * @dev Multi-signature approval for critical operations
     */
    function multiSigApprove(bytes32 _operationHash) external onlyRole(GUARDIAN_ROLE) {
        require(!multiSigApprovals[_operationHash][msg.sender], "Already approved");

        multiSigApprovals[_operationHash][msg.sender] = true;
        multiSigApprovalCount[_operationHash]++;

        emit MultiSigApproval(_operationHash, msg.sender, multiSigApprovalCount[_operationHash]);
    }

    /**
     * @dev Emergency pause triggered by agents or guardians
     */
    function triggerEmergencyPause(string memory _reason) external {
        require(hasRole(GUARDIAN_ROLE, msg.sender) || hasRole(AI_AGENT_ROLE, msg.sender), "Unauthorized");

        autonomousConfig.emergencyPause = true;
        _pause();

        emit EmergencyPauseTriggered(msg.sender, _reason);
    }

    /**
     * @dev Process execution queue automatically
     */
    function processExecutionQueue() external onlyRegisteredAgent {
        require(executionQueue.length > 0, "Execution queue empty");

        uint256 processed = 0;
        uint256 maxProcessing = 10; // Process max 10 proposals per call

        for (uint256 i = 0; i < executionQueue.length && processed < maxProcessing; i++) {
            uint256 proposalId = executionQueue[i];
            AutonomousProposal storage proposal = proposals[proposalId];

            if (!proposal.executed && !proposal.canceled && 
                block.timestamp >= proposal.endTime + autonomousConfig.autoExecutionDelay) {

                if (_checkProposalPassed(proposal) && 
                    registeredAgents[msg.sender].authority >= proposal.requiredAuthority) {

                    try this.executeAutonomously(proposalId) {
                        processed++;
                    } catch {
                        // Log failed execution but continue processing
                    }
                }
            }
        }
    }

    /**
     * @dev Update agent authority level
     */
    function updateAgentAuthority(address _agent, AgentAuthority _newAuthority) external onlyRole(ADMIN_ROLE) {
        require(isRegisteredAgent[_agent], "Agent not registered");

        AgentAuthority oldAuthority = registeredAgents[_agent].authority;
        registeredAgents[_agent].authority = _newAuthority;

        // Update roles based on new authority
        if (_newAuthority >= AgentAuthority.Moderate && !hasRole(AUTONOMOUS_EXECUTOR_ROLE, _agent)) {
            _grantRole(AUTONOMOUS_EXECUTOR_ROLE, _agent);
        } else if (_newAuthority < AgentAuthority.Moderate && hasRole(AUTONOMOUS_EXECUTOR_ROLE, _agent)) {
            _revokeRole(AUTONOMOUS_EXECUTOR_ROLE, _agent);
        }

        emit AgentAuthorityUpdated(_agent, oldAuthority, _newAuthority);
    }

    /**
     * @dev Change execution mode
     */
    function changeExecutionMode(ExecutionMode _newMode) external onlyRole(ADMIN_ROLE) {
        ExecutionMode oldMode = autonomousConfig.defaultMode;
        autonomousConfig.defaultMode = _newMode;

        emit ExecutionModeChanged(oldMode, _newMode);
    }

    // Internal Functions

    function _findBestAgent(AgentAuthority _requiredAuthority) internal view returns (address) {
        address bestAgent = address(0);
        uint256 bestScore = 0;

        // Simple scoring: success rate + execution count
        for (uint256 i = 0; i < agentCount; i++) {
            // This is a simplified approach - in practice, you'd iterate through registered agents
            // For now, return the first suitable agent found
        }

        return bestAgent;
    }

    function _checkProposalPassed(AutonomousProposal storage _proposal) internal view returns (bool) {
        uint256 totalVotes = _proposal.votesFor + _proposal.votesAgainst;

        // Check quorum
        if (totalVotes < _proposal.quorumRequired) {
            return false;
        }

        // Check threshold
        uint256 forPercentage = (_proposal.votesFor * 10000) / totalVotes;
        return forPercentage >= _proposal.thresholdRequired;
    }

    function _executeProposal(AutonomousProposal storage _proposal) internal returns (bool) {
        (bool success, ) = _proposal.target.call{value: _proposal.value}(_proposal.callData);
        return success;
    }

    function _removeFromExecutionQueue(uint256 _proposalId) internal {
        for (uint256 i = 0; i < executionQueue.length; i++) {
            if (executionQueue[i] == _proposalId) {
                executionQueue[i] = executionQueue[executionQueue.length - 1];
                executionQueue.pop();
                inExecutionQueue[_proposalId] = false;
                break;
            }
        }
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyRole(ADMIN_ROLE) {}

    // View Functions

    function getProposal(uint256 _proposalId) external view returns (
        uint256 id,
        address proposer,
        address target,
        uint256 value,
        string memory description,
        uint256 startTime,
        uint256 endTime,
        uint256 votesFor,
        uint256 votesAgainst,
        bool executed,
        bool canceled,
        address assignedAgent
    ) {
        AutonomousProposal storage proposal = proposals[_proposalId];
        return (
            proposal.id,
            proposal.proposer,
            proposal.target,
            proposal.value,
            proposal.description,
            proposal.startTime,
            proposal.endTime,
            proposal.votesFor,
            proposal.votesAgainst,
            proposal.executed,
            proposal.canceled,
            proposal.assignedAgent
        );
    }

    function getRegisteredAgent(address _agent) external view returns (RegisteredAgent memory) {
        return registeredAgents[_agent];
    }

    function getExecutionQueueLength() external view returns (uint256) {
        return executionQueue.length;
    }

    function getAgentExecutionHistory(address _agent) external view returns (uint256[] memory) {
        return agentExecutionHistory[_agent];
    }
}