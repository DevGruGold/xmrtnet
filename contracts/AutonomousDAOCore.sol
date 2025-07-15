// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./XMRT.sol";
import "./AI_Agent_Interface.sol";

/**
 * @title AutonomousDAOCore
 * @dev Enhanced fully autonomous DAO with advanced AI agent execution authority
 * @notice This contract enables complete autonomous operation with multi-agent coordination
 */
contract AutonomousDAOCore is
    Initializable,
    AccessControlUpgradeable,
    ReentrancyGuardUpgradeable,
    PausableUpgradeable,
    UUPSUpgradeable
{
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;

    // Enhanced Role System for Complete Autonomy
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant MASTER_AGENT_ROLE = keccak256("MASTER_AGENT_ROLE");
    bytes32 public constant EXECUTION_AGENT_ROLE = keccak256("EXECUTION_AGENT_ROLE");
    bytes32 public constant TREASURY_AGENT_ROLE = keccak256("TREASURY_AGENT_ROLE");
    bytes32 public constant GOVERNANCE_AGENT_ROLE = keccak256("GOVERNANCE_AGENT_ROLE");
    bytes32 public constant SECURITY_AGENT_ROLE = keccak256("SECURITY_AGENT_ROLE");
    bytes32 public constant ORACLE_AGENT_ROLE = keccak256("ORACLE_AGENT_ROLE");
    bytes32 public constant EMERGENCY_AGENT_ROLE = keccak256("EMERGENCY_AGENT_ROLE");

    // Autonomous Execution Modes
    enum AutonomyLevel {
        Disabled,           // No autonomous execution
        Basic,              // Basic routine operations
        Advanced,           // Complex multi-step operations
        Full,               // Complete autonomous authority
        Emergency           // Emergency response mode
    }

    // Agent Consensus Requirements
    enum ConsensusType {
        Single,             // Single agent can execute
        Majority,           // Majority of agents required
        Unanimous,          // All agents must agree
        Weighted,           // Weighted voting based on agent reputation
        Adaptive            // Dynamic consensus based on operation risk
    }

    // Enhanced Proposal Structure for Autonomous Execution
    struct AutonomousProposal {
        uint256 id;
        address proposer;
        address[] targets;
        uint256[] values;
        bytes[] calldatas;
        string description;
        uint256 startTime;
        uint256 endTime;
        uint256 executionDelay;
        uint256 votesFor;
        uint256 votesAgainst;
        uint256 abstainVotes;
        uint256 quorumRequired;
        uint256 thresholdRequired;
        bool executed;
        bool canceled;
        bool autoExecutable;
        AutonomyLevel requiredAutonomy;
        ConsensusType consensusType;
        uint256 riskLevel;
        mapping(address => bool) agentApprovals;
        mapping(address => uint256) agentWeights;
        uint256 totalAgentWeight;
        uint256 approvalWeight;
    }

    // Agent Performance and Reputation System
    struct AgentProfile {
        address agentAddress;
        string agentId;
        uint256 reputation;
        uint256 successfulExecutions;
        uint256 failedExecutions;
        uint256 totalValueManaged;
        uint256 lastActiveTime;
        bool isActive;
        AutonomyLevel maxAuthorityLevel;
        uint256[] specializations; // Array of operation type IDs
        mapping(uint256 => uint256) operationHistory;
    }

    // Autonomous Treasury Management
    struct TreasuryOperation {
        uint256 id;
        address token;
        uint256 amount;
        address recipient;
        string purpose;
        uint256 timestamp;
        address executingAgent;
        bool executed;
        uint256 approvalCount;
        mapping(address => bool) agentApprovals;
    }

    // Multi-Signature Automation for Agents
    struct MultiSigOperation {
        uint256 id;
        bytes32 operationHash;
        address[] requiredAgents;
        mapping(address => bool) signatures;
        uint256 signatureCount;
        uint256 requiredSignatures;
        bool executed;
        uint256 deadline;
        bytes operationData;
    }

    // State Variables
    mapping(uint256 => AutonomousProposal) public proposals;
    mapping(address => AgentProfile) public agents;
    mapping(uint256 => TreasuryOperation) public treasuryOperations;
    mapping(uint256 => MultiSigOperation) public multiSigOperations;

    address[] public activeAgents;
    uint256 public proposalCount;
    uint256 public treasuryOperationCount;
    uint256 public multiSigOperationCount;

    AutonomyLevel public currentAutonomyLevel;
    uint256 public emergencyThreshold;
    uint256 public maxTreasuryOperationValue;
    uint256 public agentReputationThreshold;

    IERC20 public xmrtToken;
    address public treasuryAddress;

    // Autonomous Decision Parameters
    uint256 public autoExecutionDelay;
    uint256 public consensusTimeout;
    uint256 public emergencyResponseTime;
    bool public emergencyMode;

    // Events for Autonomous Operations
    event AutonomousProposalCreated(uint256 indexed proposalId, address indexed proposer, AutonomyLevel autonomyLevel);
    event AutonomousProposalExecuted(uint256 indexed proposalId, address indexed executor, bool success);
    event AgentRegistered(address indexed agent, string agentId, AutonomyLevel maxAuthority);
    event AgentAuthorityUpdated(address indexed agent, AutonomyLevel newAuthority);
    event AgentReputationUpdated(address indexed agent, uint256 newReputation);
    event TreasuryOperationExecuted(uint256 indexed operationId, address indexed agent, uint256 amount);
    event MultiSigOperationCreated(uint256 indexed operationId, bytes32 operationHash);
    event MultiSigOperationExecuted(uint256 indexed operationId, bool success);
    event AutonomyLevelChanged(AutonomyLevel oldLevel, AutonomyLevel newLevel);
    event EmergencyModeActivated(address indexed activator, string reason);
    event EmergencyModeDeactivated(address indexed deactivator);

    // Modifiers
    modifier onlyActiveAgent() {
        require(agents[msg.sender].isActive, "Agent not active");
        _;
    }

    modifier onlyAuthorizedAgent(AutonomyLevel requiredLevel) {
        require(agents[msg.sender].maxAuthorityLevel >= requiredLevel, "Insufficient agent authority");
        _;
    }

    modifier onlyInAutonomyLevel(AutonomyLevel requiredLevel) {
        require(currentAutonomyLevel >= requiredLevel, "Insufficient autonomy level");
        _;
    }

    modifier notInEmergencyMode() {
        require(!emergencyMode, "Emergency mode active");
        _;
    }

    /**
     * @dev Initialize the Autonomous DAO Core
     */
    function initialize(
        address _xmrtToken,
        address _treasuryAddress,
        uint256 _emergencyThreshold,
        uint256 _maxTreasuryOperationValue
    ) public initializer {
        __AccessControl_init();
        __ReentrancyGuard_init();
        __Pausable_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);

        xmrtToken = IERC20(_xmrtToken);
        treasuryAddress = _treasuryAddress;
        emergencyThreshold = _emergencyThreshold;
        maxTreasuryOperationValue = _maxTreasuryOperationValue;

        currentAutonomyLevel = AutonomyLevel.Basic;
        autoExecutionDelay = 24 hours;
        consensusTimeout = 6 hours;
        emergencyResponseTime = 1 hours;
        agentReputationThreshold = 100;
    }

    /**
     * @dev Register a new AI agent with specific authority level
     */
    function registerAgent(
        address _agentAddress,
        string memory _agentId,
        AutonomyLevel _maxAuthority,
        uint256[] memory _specializations
    ) external onlyRole(ADMIN_ROLE) {
        require(_agentAddress != address(0), "Invalid agent address");
        require(!agents[_agentAddress].isActive, "Agent already registered");

        AgentProfile storage agent = agents[_agentAddress];
        agent.agentAddress = _agentAddress;
        agent.agentId = _agentId;
        agent.reputation = agentReputationThreshold;
        agent.maxAuthorityLevel = _maxAuthority;
        agent.isActive = true;
        agent.lastActiveTime = block.timestamp;
        agent.specializations = _specializations;

        activeAgents.push(_agentAddress);

        // Grant appropriate roles based on authority level
        if (_maxAuthority >= AutonomyLevel.Basic) {
            _grantRole(EXECUTION_AGENT_ROLE, _agentAddress);
        }
        if (_maxAuthority >= AutonomyLevel.Advanced) {
            _grantRole(TREASURY_AGENT_ROLE, _agentAddress);
            _grantRole(GOVERNANCE_AGENT_ROLE, _agentAddress);
        }
        if (_maxAuthority >= AutonomyLevel.Full) {
            _grantRole(MASTER_AGENT_ROLE, _agentAddress);
            _grantRole(SECURITY_AGENT_ROLE, _agentAddress);
        }
        if (_maxAuthority == AutonomyLevel.Emergency) {
            _grantRole(EMERGENCY_AGENT_ROLE, _agentAddress);
        }

        emit AgentRegistered(_agentAddress, _agentId, _maxAuthority);
    }

    /**
     * @dev Create autonomous proposal that can be executed by agents
     */
    function createAutonomousProposal(
        address[] memory _targets,
        uint256[] memory _values,
        bytes[] memory _calldatas,
        string memory _description,
        uint256 _executionDelay,
        AutonomyLevel _requiredAutonomy,
        ConsensusType _consensusType,
        uint256 _riskLevel
    ) external onlyActiveAgent returns (uint256) {
        require(_targets.length == _values.length && _targets.length == _calldatas.length, "Array length mismatch");
        require(_targets.length > 0, "Empty proposal");
        require(_riskLevel <= 100, "Invalid risk level");

        uint256 proposalId = ++proposalCount;
        AutonomousProposal storage proposal = proposals[proposalId];

        proposal.id = proposalId;
        proposal.proposer = msg.sender;
        proposal.targets = _targets;
        proposal.values = _values;
        proposal.calldatas = _calldatas;
        proposal.description = _description;
        proposal.startTime = block.timestamp;
        proposal.endTime = block.timestamp + 7 days; // Default voting period
        proposal.executionDelay = _executionDelay;
        proposal.requiredAutonomy = _requiredAutonomy;
        proposal.consensusType = _consensusType;
        proposal.riskLevel = _riskLevel;
        proposal.autoExecutable = true;

        // Set quorum and threshold based on risk level
        proposal.quorumRequired = _calculateQuorum(_riskLevel);
        proposal.thresholdRequired = _calculateThreshold(_riskLevel);

        emit AutonomousProposalCreated(proposalId, msg.sender, _requiredAutonomy);
        return proposalId;
    }

    /**
     * @dev Execute autonomous proposal by authorized agent
     */
    function executeAutonomousProposal(uint256 _proposalId) 
        external 
        onlyActiveAgent 
        onlyAuthorizedAgent(proposals[_proposalId].requiredAutonomy)
        onlyInAutonomyLevel(proposals[_proposalId].requiredAutonomy)
        nonReentrant 
    {
        AutonomousProposal storage proposal = proposals[_proposalId];
        require(!proposal.executed && !proposal.canceled, "Proposal not executable");
        require(block.timestamp >= proposal.endTime + proposal.executionDelay, "Execution delay not met");

        // Check consensus requirements
        require(_checkConsensus(_proposalId), "Consensus not reached");

        // Update agent activity
        agents[msg.sender].lastActiveTime = block.timestamp;

        bool success = true;

        // Execute all operations in the proposal
        for (uint256 i = 0; i < proposal.targets.length; i++) {
            (bool callSuccess,) = proposal.targets[i].call{value: proposal.values[i]}(proposal.calldatas[i]);
            if (!callSuccess) {
                success = false;
                break;
            }
        }

        proposal.executed = true;

        // Update agent reputation based on execution success
        if (success) {
            agents[msg.sender].successfulExecutions++;
            _updateAgentReputation(msg.sender, 10); // Increase reputation
        } else {
            agents[msg.sender].failedExecutions++;
            _updateAgentReputation(msg.sender, -5); // Decrease reputation
        }

        emit AutonomousProposalExecuted(_proposalId, msg.sender, success);
    }

    /**
     * @dev Agent approval for proposal consensus
     */
    function approveProposal(uint256 _proposalId) external onlyActiveAgent {
        AutonomousProposal storage proposal = proposals[_proposalId];
        require(!proposal.executed && !proposal.canceled, "Proposal not active");
        require(!proposal.agentApprovals[msg.sender], "Already approved");

        proposal.agentApprovals[msg.sender] = true;
        proposal.agentWeights[msg.sender] = agents[msg.sender].reputation;
        proposal.approvalWeight += agents[msg.sender].reputation;

        agents[msg.sender].lastActiveTime = block.timestamp;
    }

    /**
     * @dev Execute treasury operation autonomously
     */
    function executeAutonomousTreasuryOperation(
        address _token,
        uint256 _amount,
        address _recipient,
        string memory _purpose
    ) external onlyRole(TREASURY_AGENT_ROLE) onlyActiveAgent nonReentrant {
        require(_amount <= maxTreasuryOperationValue, "Amount exceeds limit");
        require(_recipient != address(0), "Invalid recipient");

        uint256 operationId = ++treasuryOperationCount;
        TreasuryOperation storage operation = treasuryOperations[operationId];

        operation.id = operationId;
        operation.token = _token;
        operation.amount = _amount;
        operation.recipient = _recipient;
        operation.purpose = _purpose;
        operation.timestamp = block.timestamp;
        operation.executingAgent = msg.sender;

        // For high-value operations, require multi-agent approval
        if (_amount > maxTreasuryOperationValue / 2) {
            operation.approvalCount = 1;
            operation.agentApprovals[msg.sender] = true;
            // Require additional approvals...
        } else {
            // Execute immediately for low-value operations
            _executeTreasuryOperation(operationId);
        }

        agents[msg.sender].totalValueManaged += _amount;
        agents[msg.sender].lastActiveTime = block.timestamp;
    }

    /**
     * @dev Create multi-signature operation for critical functions
     */
    function createMultiSigOperation(
        bytes memory _operationData,
        address[] memory _requiredAgents,
        uint256 _requiredSignatures,
        uint256 _deadline
    ) external onlyRole(SECURITY_AGENT_ROLE) returns (uint256) {
        require(_requiredAgents.length >= _requiredSignatures, "Invalid signature requirements");
        require(_deadline > block.timestamp, "Invalid deadline");

        uint256 operationId = ++multiSigOperationCount;
        MultiSigOperation storage operation = multiSigOperations[operationId];

        operation.id = operationId;
        operation.operationHash = keccak256(_operationData);
        operation.requiredAgents = _requiredAgents;
        operation.requiredSignatures = _requiredSignatures;
        operation.deadline = _deadline;
        operation.operationData = _operationData;

        emit MultiSigOperationCreated(operationId, operation.operationHash);
        return operationId;
    }

    /**
     * @dev Sign multi-signature operation
     */
    function signMultiSigOperation(uint256 _operationId) external onlyActiveAgent {
        MultiSigOperation storage operation = multiSigOperations[_operationId];
        require(!operation.executed, "Operation already executed");
        require(block.timestamp <= operation.deadline, "Operation expired");
        require(!operation.signatures[msg.sender], "Already signed");

        // Check if agent is required for this operation
        bool isRequired = false;
        for (uint256 i = 0; i < operation.requiredAgents.length; i++) {
            if (operation.requiredAgents[i] == msg.sender) {
                isRequired = true;
                break;
            }
        }
        require(isRequired, "Agent not required for this operation");

        operation.signatures[msg.sender] = true;
        operation.signatureCount++;

        // Auto-execute if enough signatures
        if (operation.signatureCount >= operation.requiredSignatures) {
            _executeMultiSigOperation(_operationId);
        }

        agents[msg.sender].lastActiveTime = block.timestamp;
    }

    /**
     * @dev Activate emergency mode
     */
    function activateEmergencyMode(string memory _reason) 
        external 
        onlyRole(EMERGENCY_AGENT_ROLE) 
    {
        emergencyMode = true;
        currentAutonomyLevel = AutonomyLevel.Emergency;

        emit EmergencyModeActivated(msg.sender, _reason);
    }

    /**
     * @dev Deactivate emergency mode
     */
    function deactivateEmergencyMode() 
        external 
        onlyRole(EMERGENCY_AGENT_ROLE) 
    {
        emergencyMode = false;
        currentAutonomyLevel = AutonomyLevel.Full; // Return to full autonomy

        emit EmergencyModeDeactivated(msg.sender);
    }

    /**
     * @dev Update autonomy level
     */
    function updateAutonomyLevel(AutonomyLevel _newLevel) 
        external 
        onlyRole(MASTER_AGENT_ROLE) 
    {
        AutonomyLevel oldLevel = currentAutonomyLevel;
        currentAutonomyLevel = _newLevel;

        emit AutonomyLevelChanged(oldLevel, _newLevel);
    }

    // Internal Functions

    function _calculateQuorum(uint256 _riskLevel) internal view returns (uint256) {
        // Higher risk requires higher quorum
        return (activeAgents.length * (50 + _riskLevel / 2)) / 100;
    }

    function _calculateThreshold(uint256 _riskLevel) internal pure returns (uint256) {
        // Higher risk requires higher threshold
        return 50 + _riskLevel / 2; // 50-100% threshold based on risk
    }

    function _checkConsensus(uint256 _proposalId) internal view returns (bool) {
        AutonomousProposal storage proposal = proposals[_proposalId];

        if (proposal.consensusType == ConsensusType.Single) {
            return proposal.approvalWeight > 0;
        } else if (proposal.consensusType == ConsensusType.Majority) {
            uint256 totalWeight = _getTotalAgentWeight();
            return proposal.approvalWeight > totalWeight / 2;
        } else if (proposal.consensusType == ConsensusType.Weighted) {
            uint256 totalWeight = _getTotalAgentWeight();
            return (proposal.approvalWeight * 100) / totalWeight >= proposal.thresholdRequired;
        }

        return false;
    }

    function _getTotalAgentWeight() internal view returns (uint256) {
        uint256 totalWeight = 0;
        for (uint256 i = 0; i < activeAgents.length; i++) {
            if (agents[activeAgents[i]].isActive) {
                totalWeight += agents[activeAgents[i]].reputation;
            }
        }
        return totalWeight;
    }

    function _updateAgentReputation(address _agent, int256 _change) internal {
        AgentProfile storage agent = agents[_agent];
        if (_change > 0) {
            agent.reputation += uint256(_change);
        } else {
            uint256 decrease = uint256(-_change);
            if (agent.reputation > decrease) {
                agent.reputation -= decrease;
            } else {
                agent.reputation = 0;
            }
        }

        emit AgentReputationUpdated(_agent, agent.reputation);
    }

    function _executeTreasuryOperation(uint256 _operationId) internal {
        TreasuryOperation storage operation = treasuryOperations[_operationId];
        require(!operation.executed, "Operation already executed");

        if (operation.token == address(0)) {
            // ETH transfer
            payable(operation.recipient).transfer(operation.amount);
        } else {
            // ERC20 transfer
            IERC20(operation.token).transfer(operation.recipient, operation.amount);
        }

        operation.executed = true;

        emit TreasuryOperationExecuted(_operationId, operation.executingAgent, operation.amount);
    }

    function _executeMultiSigOperation(uint256 _operationId) internal {
        MultiSigOperation storage operation = multiSigOperations[_operationId];
        require(!operation.executed, "Operation already executed");

        // Decode and execute the operation data
        (bool success,) = address(this).call(operation.operationData);

        operation.executed = true;

        emit MultiSigOperationExecuted(_operationId, success);
    }

    function _authorizeUpgrade(address newImplementation) 
        internal 
        override 
        onlyRole(ADMIN_ROLE) 
    {}

    // View Functions

    function getProposal(uint256 _proposalId) external view returns (
        uint256 id,
        address proposer,
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        string memory description,
        uint256 startTime,
        uint256 endTime,
        bool executed,
        bool canceled,
        AutonomyLevel requiredAutonomy,
        ConsensusType consensusType,
        uint256 riskLevel
    ) {
        AutonomousProposal storage proposal = proposals[_proposalId];
        return (
            proposal.id,
            proposal.proposer,
            proposal.targets,
            proposal.values,
            proposal.calldatas,
            proposal.description,
            proposal.startTime,
            proposal.endTime,
            proposal.executed,
            proposal.canceled,
            proposal.requiredAutonomy,
            proposal.consensusType,
            proposal.riskLevel
        );
    }

    function getAgentProfile(address _agent) external view returns (
        string memory agentId,
        uint256 reputation,
        uint256 successfulExecutions,
        uint256 failedExecutions,
        uint256 totalValueManaged,
        bool isActive,
        AutonomyLevel maxAuthorityLevel
    ) {
        AgentProfile storage agent = agents[_agent];
        return (
            agent.agentId,
            agent.reputation,
            agent.successfulExecutions,
            agent.failedExecutions,
            agent.totalValueManaged,
            agent.isActive,
            agent.maxAuthorityLevel
        );
    }

    function getActiveAgents() external view returns (address[] memory) {
        return activeAgents;
    }

    function isProposalApprovedByAgent(uint256 _proposalId, address _agent) 
        external 
        view 
        returns (bool) 
    {
        return proposals[_proposalId].agentApprovals[_agent];
    }

    receive() external payable {}
}