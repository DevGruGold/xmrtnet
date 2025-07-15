// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "./XMRT.sol";
import "./AutonomousDAO.sol";

/**
 * @title AgentManager
 * @dev Comprehensive agent management system for autonomous DAO operations
 * @notice Handles agent registration, performance tracking, task assignment, and coordination
 */
contract AgentManager is
    Initializable,
    AccessControlUpgradeable,
    ReentrancyGuardUpgradeable,
    PausableUpgradeable,
    UUPSUpgradeable
{
    using ECDSA for bytes32;

    // Roles
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant AGENT_COORDINATOR_ROLE = keccak256("AGENT_COORDINATOR_ROLE");
    bytes32 public constant PERFORMANCE_AUDITOR_ROLE = keccak256("PERFORMANCE_AUDITOR_ROLE");

    // Agent Specializations
    enum AgentSpecialization {
        General,
        Treasury,
        Governance,
        Security,
        Analytics,
        CrossChain,
        Community,
        Development
    }

    // Agent Status
    enum AgentStatus {
        Pending,
        Active,
        Suspended,
        Retired,
        Slashed
    }

    // Task Priority Levels
    enum TaskPriority {
        Low,
        Medium,
        High,
        Critical,
        Emergency
    }

    // Task Status
    enum TaskStatus {
        Pending,
        Assigned,
        InProgress,
        Completed,
        Failed,
        Cancelled
    }

    // Comprehensive Agent Profile
    struct AgentProfile {
        address agentAddress;
        string name;
        string description;
        string metadataURI;
        AgentSpecialization[] specializations;
        AgentStatus status;
        uint256 registrationTime;
        uint256 lastActiveTime;
        uint256 stakingAmount;
        uint256 reputationScore;
        uint256 totalTasksCompleted;
        uint256 totalTasksFailed;
        uint256 totalRewardsEarned;
        uint256 slashingCount;
        address[] endorsers;
        mapping(AgentSpecialization => uint256) specializationScores;
        mapping(address => bool) hasEndorsed;
    }

    // Task Structure
    struct Task {
        uint256 taskId;
        string description;
        bytes taskData;
        AgentSpecialization requiredSpecialization;
        TaskPriority priority;
        TaskStatus status;
        address assignedAgent;
        address creator;
        uint256 reward;
        uint256 deadline;
        uint256 createdAt;
        uint256 assignedAt;
        uint256 completedAt;
        bool requiresMultiSig;
        uint256 requiredEndorsements;
        mapping(address => bool) endorsements;
        uint256 endorsementCount;
    }

    // Performance Metrics
    struct PerformanceMetrics {
        uint256 successRate;
        uint256 averageCompletionTime;
        uint256 qualityScore;
        uint256 reliabilityScore;
        uint256 responseTime;
        uint256 lastUpdated;
    }

    // Agent Coordination Pool
    struct CoordinationPool {
        AgentSpecialization specialization;
        address[] activeAgents;
        uint256 totalCapacity;
        uint256 currentLoad;
        uint256 averageResponseTime;
        bool emergencyMode;
    }

    // State Variables
    XMRT public xmrtToken;
    AutonomousDAO public autonomousDAO;

    uint256 public agentCount;
    uint256 public taskCount;
    uint256 public totalStakedAmount;

    mapping(address => AgentProfile) public agentProfiles;
    mapping(address => bool) public isRegisteredAgent;
    mapping(uint256 => Task) public tasks;
    mapping(address => PerformanceMetrics) public performanceMetrics;
    mapping(AgentSpecialization => CoordinationPool) public coordinationPools;
    mapping(address => uint256[]) public agentTaskHistory;
    mapping(AgentSpecialization => address[]) public specializationAgents;

    // Task queues by priority
    mapping(TaskPriority => uint256[]) public taskQueues;
    mapping(uint256 => bool) public taskInQueue;

    // Reputation and scoring
    mapping(address => mapping(address => uint256)) public peerRatings;
    mapping(address => uint256) public lastRatingTime;

    // Emergency response
    address[] public emergencyAgents;
    bool public emergencyMode;
    uint256 public emergencyThreshold;

    // Configuration
    uint256 public constant MIN_STAKING_AMOUNT = 1000 * 10**18; // 1000 XMRT
    uint256 public constant REPUTATION_DECAY_RATE = 5; // 5% per month
    uint256 public constant MAX_CONCURRENT_TASKS = 5;
    uint256 public constant TASK_TIMEOUT_PERIOD = 24 hours;

    // Events
    event AgentRegistered(address indexed agent, AgentSpecialization[] specializations);
    event AgentStatusChanged(address indexed agent, AgentStatus oldStatus, AgentStatus newStatus);
    event TaskCreated(uint256 indexed taskId, AgentSpecialization specialization, TaskPriority priority);
    event TaskAssigned(uint256 indexed taskId, address indexed agent);
    event TaskCompleted(uint256 indexed taskId, address indexed agent, bool success);
    event PerformanceUpdated(address indexed agent, uint256 newReputationScore);
    event EmergencyModeActivated(string reason);
    event AgentSlashed(address indexed agent, uint256 amount, string reason);
    event RewardDistributed(address indexed agent, uint256 amount);

    // Modifiers
    modifier onlyRegisteredAgent() {
        require(isRegisteredAgent[msg.sender], "Not a registered agent");
        require(agentProfiles[msg.sender].status == AgentStatus.Active, "Agent not active");
        _;
    }

    modifier onlyActiveAgent(address _agent) {
        require(isRegisteredAgent[_agent], "Not a registered agent");
        require(agentProfiles[_agent].status == AgentStatus.Active, "Agent not active");
        _;
    }

    modifier taskExists(uint256 _taskId) {
        require(_taskId > 0 && _taskId <= taskCount, "Task does not exist");
        _;
    }

    /**
     * @dev Initialize the AgentManager
     */
    function initialize(
        address _xmrtToken,
        address _autonomousDAO
    ) public initializer {
        __AccessControl_init();
        __ReentrancyGuard_init();
        __Pausable_init();
        __UUPSUpgradeable_init();

        xmrtToken = XMRT(_xmrtToken);
        autonomousDAO = AutonomousDAO(_autonomousDAO);

        emergencyThreshold = 3; // Minimum 3 agents for emergency response

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(AGENT_COORDINATOR_ROLE, msg.sender);
        _grantRole(PERFORMANCE_AUDITOR_ROLE, msg.sender);

        // Initialize coordination pools
        _initializeCoordinationPools();
    }

    /**
     * @dev Register a new agent with comprehensive profile
     */
    function registerAgent(
        string memory _name,
        string memory _description,
        string memory _metadataURI,
        AgentSpecialization[] memory _specializations,
        uint256 _stakingAmount
    ) external nonReentrant {
        require(!isRegisteredAgent[msg.sender], "Agent already registered");
        require(_stakingAmount >= MIN_STAKING_AMOUNT, "Insufficient staking amount");
        require(_specializations.length > 0, "Must have at least one specialization");
        require(xmrtToken.balanceOf(msg.sender) >= _stakingAmount, "Insufficient XMRT balance");

        // Transfer staking amount
        xmrtToken.transferFrom(msg.sender, address(this), _stakingAmount);
        totalStakedAmount += _stakingAmount;

        // Create agent profile
        AgentProfile storage profile = agentProfiles[msg.sender];
        profile.agentAddress = msg.sender;
        profile.name = _name;
        profile.description = _description;
        profile.metadataURI = _metadataURI;
        profile.specializations = _specializations;
        profile.status = AgentStatus.Pending;
        profile.registrationTime = block.timestamp;
        profile.lastActiveTime = block.timestamp;
        profile.stakingAmount = _stakingAmount;
        profile.reputationScore = 1000; // Starting reputation score

        // Initialize performance metrics
        performanceMetrics[msg.sender] = PerformanceMetrics({
            successRate: 100,
            averageCompletionTime: 0,
            qualityScore: 100,
            reliabilityScore: 100,
            responseTime: 0,
            lastUpdated: block.timestamp
        });

        // Add to specialization pools
        for (uint256 i = 0; i < _specializations.length; i++) {
            specializationAgents[_specializations[i]].push(msg.sender);
            coordinationPools[_specializations[i]].activeAgents.push(msg.sender);
            coordinationPools[_specializations[i]].totalCapacity++;
        }

        isRegisteredAgent[msg.sender] = true;
        agentCount++;

        emit AgentRegistered(msg.sender, _specializations);
    }

    /**
     * @dev Activate a pending agent (admin approval)
     */
    function activateAgent(address _agent) external onlyRole(ADMIN_ROLE) {
        require(isRegisteredAgent[_agent], "Agent not registered");
        require(agentProfiles[_agent].status == AgentStatus.Pending, "Agent not pending");

        agentProfiles[_agent].status = AgentStatus.Active;
        agentProfiles[_agent].lastActiveTime = block.timestamp;

        emit AgentStatusChanged(_agent, AgentStatus.Pending, AgentStatus.Active);
    }

    /**
     * @dev Create a new task for agents
     */
    function createTask(
        string memory _description,
        bytes memory _taskData,
        AgentSpecialization _requiredSpecialization,
        TaskPriority _priority,
        uint256 _reward,
        uint256 _deadline,
        bool _requiresMultiSig,
        uint256 _requiredEndorsements
    ) external returns (uint256) {
        require(_deadline > block.timestamp, "Invalid deadline");
        require(_reward > 0, "Reward must be greater than 0");

        taskCount++;
        uint256 taskId = taskCount;

        Task storage task = tasks[taskId];
        task.taskId = taskId;
        task.description = _description;
        task.taskData = _taskData;
        task.requiredSpecialization = _requiredSpecialization;
        task.priority = _priority;
        task.status = TaskStatus.Pending;
        task.creator = msg.sender;
        task.reward = _reward;
        task.deadline = _deadline;
        task.createdAt = block.timestamp;
        task.requiresMultiSig = _requiresMultiSig;
        task.requiredEndorsements = _requiredEndorsements;

        // Add to appropriate priority queue
        taskQueues[_priority].push(taskId);
        taskInQueue[taskId] = true;

        // Transfer reward to contract
        xmrtToken.transferFrom(msg.sender, address(this), _reward);

        emit TaskCreated(taskId, _requiredSpecialization, _priority);

        // Auto-assign if possible
        _autoAssignTask(taskId);

        return taskId;
    }

    /**
     * @dev Auto-assign task to best available agent
     */
    function _autoAssignTask(uint256 _taskId) internal {
        Task storage task = tasks[_taskId];
        address bestAgent = _findBestAgent(task.requiredSpecialization, task.priority);

        if (bestAgent != address(0)) {
            _assignTask(_taskId, bestAgent);
        }
    }

    /**
     * @dev Manually assign task to specific agent
     */
    function assignTask(uint256 _taskId, address _agent) external onlyRole(AGENT_COORDINATOR_ROLE) taskExists(_taskId) {
        _assignTask(_taskId, _agent);
    }

    /**
     * @dev Internal task assignment logic
     */
    function _assignTask(uint256 _taskId, address _agent) internal onlyActiveAgent(_agent) {
        Task storage task = tasks[_taskId];
        require(task.status == TaskStatus.Pending, "Task not pending");
        require(_hasSpecialization(_agent, task.requiredSpecialization), "Agent lacks required specialization");
        require(_getAgentCurrentTasks(_agent) < MAX_CONCURRENT_TASKS, "Agent at task capacity");

        task.assignedAgent = _agent;
        task.status = TaskStatus.Assigned;
        task.assignedAt = block.timestamp;

        agentTaskHistory[_agent].push(_taskId);
        coordinationPools[task.requiredSpecialization].currentLoad++;

        // Remove from queue
        _removeFromQueue(_taskId, task.priority);

        emit TaskAssigned(_taskId, _agent);
    }

    /**
     * @dev Agent accepts and starts working on assigned task
     */
    function startTask(uint256 _taskId) external onlyRegisteredAgent taskExists(_taskId) {
        Task storage task = tasks[_taskId];
        require(task.assignedAgent == msg.sender, "Not assigned to this agent");
        require(task.status == TaskStatus.Assigned, "Task not assigned");
        require(block.timestamp <= task.deadline, "Task deadline passed");

        task.status = TaskStatus.InProgress;
        agentProfiles[msg.sender].lastActiveTime = block.timestamp;
    }

    /**
     * @dev Complete a task and submit results
     */
    function completeTask(uint256 _taskId, bytes memory _result) external onlyRegisteredAgent taskExists(_taskId) {
        Task storage task = tasks[_taskId];
        require(task.assignedAgent == msg.sender, "Not assigned to this agent");
        require(task.status == TaskStatus.InProgress, "Task not in progress");

        task.status = TaskStatus.Completed;
        task.completedAt = block.timestamp;

        // Update agent performance
        _updateAgentPerformance(msg.sender, _taskId, true);

        // Distribute reward
        _distributeReward(msg.sender, task.reward);

        // Update coordination pool
        coordinationPools[task.requiredSpecialization].currentLoad--;

        emit TaskCompleted(_taskId, msg.sender, true);
    }

    /**
     * @dev Report task failure
     */
    function reportTaskFailure(uint256 _taskId, string memory _reason) external onlyRegisteredAgent taskExists(_taskId) {
        Task storage task = tasks[_taskId];
        require(task.assignedAgent == msg.sender, "Not assigned to this agent");
        require(task.status == TaskStatus.InProgress, "Task not in progress");

        task.status = TaskStatus.Failed;

        // Update agent performance (negative impact)
        _updateAgentPerformance(msg.sender, _taskId, false);

        // Return reward to creator
        xmrtToken.transfer(task.creator, task.reward);

        // Update coordination pool
        coordinationPools[task.requiredSpecialization].currentLoad--;

        emit TaskCompleted(_taskId, msg.sender, false);
    }

    /**
     * @dev Emergency task assignment for critical situations
     */
    function emergencyAssignTask(uint256 _taskId) external onlyRole(ADMIN_ROLE) taskExists(_taskId) {
        Task storage task = tasks[_taskId];
        require(task.priority == TaskPriority.Emergency || task.priority == TaskPriority.Critical, "Not emergency task");

        // Find emergency-capable agent
        address emergencyAgent = _findEmergencyAgent(task.requiredSpecialization);
        require(emergencyAgent != address(0), "No emergency agent available");

        _assignTask(_taskId, emergencyAgent);
    }

    /**
     * @dev Update agent performance metrics
     */
    function _updateAgentPerformance(address _agent, uint256 _taskId, bool _success) internal {
        AgentProfile storage profile = agentProfiles[_agent];
        PerformanceMetrics storage metrics = performanceMetrics[_agent];
        Task storage task = tasks[_taskId];

        if (_success) {
            profile.totalTasksCompleted++;

            // Calculate completion time
            uint256 completionTime = task.completedAt - task.assignedAt;
            metrics.averageCompletionTime = (metrics.averageCompletionTime + completionTime) / 2;

            // Update specialization score
            profile.specializationScores[task.requiredSpecialization] += 10;

            // Increase reputation
            profile.reputationScore += 5;
        } else {
            profile.totalTasksFailed++;

            // Decrease reputation
            if (profile.reputationScore > 10) {
                profile.reputationScore -= 10;
            }
        }

        // Recalculate success rate
        uint256 totalTasks = profile.totalTasksCompleted + profile.totalTasksFailed;
        if (totalTasks > 0) {
            metrics.successRate = (profile.totalTasksCompleted * 100) / totalTasks;
        }

        metrics.lastUpdated = block.timestamp;

        emit PerformanceUpdated(_agent, profile.reputationScore);
    }

    /**
     * @dev Find best agent for a task based on specialization and performance
     */
    function _findBestAgent(AgentSpecialization _specialization, TaskPriority _priority) internal view returns (address) {
        address[] memory candidates = specializationAgents[_specialization];
        address bestAgent = address(0);
        uint256 bestScore = 0;

        for (uint256 i = 0; i < candidates.length; i++) {
            address candidate = candidates[i];

            if (agentProfiles[candidate].status != AgentStatus.Active) continue;
            if (_getAgentCurrentTasks(candidate) >= MAX_CONCURRENT_TASKS) continue;

            uint256 score = _calculateAgentScore(candidate, _specialization, _priority);

            if (score > bestScore) {
                bestScore = score;
                bestAgent = candidate;
            }
        }

        return bestAgent;
    }

    /**
     * @dev Calculate agent score for task assignment
     */
    function _calculateAgentScore(address _agent, AgentSpecialization _specialization, TaskPriority _priority) internal view returns (uint256) {
        AgentProfile storage profile = agentProfiles[_agent];
        PerformanceMetrics storage metrics = performanceMetrics[_agent];

        uint256 score = 0;

        // Base reputation score (40% weight)
        score += (profile.reputationScore * 40) / 100;

        // Success rate (30% weight)
        score += (metrics.successRate * 30) / 100;

        // Specialization score (20% weight)
        score += (profile.specializationScores[_specialization] * 20) / 100;

        // Availability bonus (10% weight)
        uint256 currentTasks = _getAgentCurrentTasks(_agent);
        uint256 availabilityBonus = ((MAX_CONCURRENT_TASKS - currentTasks) * 10) / MAX_CONCURRENT_TASKS;
        score += availabilityBonus;

        // Priority bonus for high-priority tasks
        if (_priority == TaskPriority.Critical || _priority == TaskPriority.Emergency) {
            score += 50;
        }

        return score;
    }

    /**
     * @dev Get current number of active tasks for an agent
     */
    function _getAgentCurrentTasks(address _agent) internal view returns (uint256) {
        uint256[] memory taskHistory = agentTaskHistory[_agent];
        uint256 activeTasks = 0;

        for (uint256 i = 0; i < taskHistory.length; i++) {
            TaskStatus status = tasks[taskHistory[i]].status;
            if (status == TaskStatus.Assigned || status == TaskStatus.InProgress) {
                activeTasks++;
            }
        }

        return activeTasks;
    }

    /**
     * @dev Check if agent has required specialization
     */
    function _hasSpecialization(address _agent, AgentSpecialization _specialization) internal view returns (bool) {
        AgentSpecialization[] memory specializations = agentProfiles[_agent].specializations;

        for (uint256 i = 0; i < specializations.length; i++) {
            if (specializations[i] == _specialization) {
                return true;
            }
        }

        return false;
    }

    /**
     * @dev Find emergency-capable agent
     */
    function _findEmergencyAgent(AgentSpecialization _specialization) internal view returns (address) {
        for (uint256 i = 0; i < emergencyAgents.length; i++) {
            address agent = emergencyAgents[i];
            if (agentProfiles[agent].status == AgentStatus.Active && 
                _hasSpecialization(agent, _specialization) &&
                _getAgentCurrentTasks(agent) < MAX_CONCURRENT_TASKS) {
                return agent;
            }
        }
        return address(0);
    }

    /**
     * @dev Remove task from priority queue
     */
    function _removeFromQueue(uint256 _taskId, TaskPriority _priority) internal {
        uint256[] storage queue = taskQueues[_priority];

        for (uint256 i = 0; i < queue.length; i++) {
            if (queue[i] == _taskId) {
                queue[i] = queue[queue.length - 1];
                queue.pop();
                taskInQueue[_taskId] = false;
                break;
            }
        }
    }

    /**
     * @dev Distribute reward to agent
     */
    function _distributeReward(address _agent, uint256 _amount) internal {
        agentProfiles[_agent].totalRewardsEarned += _amount;
        xmrtToken.transfer(_agent, _amount);

        emit RewardDistributed(_agent, _amount);
    }

    /**
     * @dev Initialize coordination pools for all specializations
     */
    function _initializeCoordinationPools() internal {
        for (uint256 i = 0; i <= uint256(AgentSpecialization.Development); i++) {
            AgentSpecialization spec = AgentSpecialization(i);
            coordinationPools[spec] = CoordinationPool({
                specialization: spec,
                activeAgents: new address[](0),
                totalCapacity: 0,
                currentLoad: 0,
                averageResponseTime: 0,
                emergencyMode: false
            });
        }
    }

    /**
     * @dev Slash agent for misconduct
     */
    function slashAgent(address _agent, uint256 _amount, string memory _reason) external onlyRole(ADMIN_ROLE) {
        require(isRegisteredAgent[_agent], "Agent not registered");
        require(_amount <= agentProfiles[_agent].stakingAmount, "Slash amount exceeds stake");

        agentProfiles[_agent].stakingAmount -= _amount;
        agentProfiles[_agent].slashingCount++;
        agentProfiles[_agent].reputationScore = agentProfiles[_agent].reputationScore / 2; // Halve reputation

        // Transfer slashed amount to treasury
        totalStakedAmount -= _amount;
        // Could transfer to DAO treasury here

        emit AgentSlashed(_agent, _amount, _reason);
    }

    /**
     * @dev Activate emergency mode
     */
    function activateEmergencyMode(string memory _reason) external onlyRole(ADMIN_ROLE) {
        emergencyMode = true;

        // Pause non-critical operations
        _pause();

        emit EmergencyModeActivated(_reason);
    }

    // View Functions

    function getAgentProfile(address _agent) external view returns (
        string memory name,
        string memory description,
        AgentSpecialization[] memory specializations,
        AgentStatus status,
        uint256 reputationScore,
        uint256 totalTasksCompleted,
        uint256 stakingAmount
    ) {
        AgentProfile storage profile = agentProfiles[_agent];
        return (
            profile.name,
            profile.description,
            profile.specializations,
            profile.status,
            profile.reputationScore,
            profile.totalTasksCompleted,
            profile.stakingAmount
        );
    }

    function getTask(uint256 _taskId) external view returns (
        string memory description,
        AgentSpecialization requiredSpecialization,
        TaskPriority priority,
        TaskStatus status,
        address assignedAgent,
        uint256 reward,
        uint256 deadline
    ) {
        Task storage task = tasks[_taskId];
        return (
            task.description,
            task.requiredSpecialization,
            task.priority,
            task.status,
            task.assignedAgent,
            task.reward,
            task.deadline
        );
    }

    function getPerformanceMetrics(address _agent) external view returns (PerformanceMetrics memory) {
        return performanceMetrics[_agent];
    }

    function getQueueLength(TaskPriority _priority) external view returns (uint256) {
        return taskQueues[_priority].length;
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyRole(ADMIN_ROLE) {}
}