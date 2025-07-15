// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "./DAO_Governance.sol";
import "./DAO_Treasury.sol";
import "./XMRT.sol";

/**
 * @title AI_Agent_Interface
 * @dev Interface contract for AI agents to interact with the DAO ecosystem
 */
contract AI_Agent_Interface is
    Initializable,
    AccessControlUpgradeable,
    ReentrancyGuardUpgradeable,
    PausableUpgradeable,
    UUPSUpgradeable
{
    // Roles
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant AI_AGENT_ROLE = keccak256("AI_AGENT_ROLE");
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");

    // Contract references
    DAO_Governance public daoGovernance;
    DAO_Treasury public daoTreasury;
    XMRT public xmrtToken;

    // AI action types
    enum AIActionType {
        CreateProposal,
        ExecuteSpending,
        StakeTokens,
        UnstakeTokens,
        UpdateParameters,
        EmergencyAction
    }

    // AI action structure
    struct AIAction {
        uint256 id;
        address agent;
        AIActionType actionType;
        bytes actionData;
        uint256 timestamp;
        bool executed;
        string description;
        uint256 gasUsed;
    }

    // State variables
    mapping(uint256 => AIAction) public aiActions;
    uint256 public actionCount;
    mapping(address => uint256) public agentActionCounts;
    mapping(address => uint256) public agentLastActionTime;

    // Configuration
    uint256 public constant MIN_ACTION_INTERVAL = 1 minutes;
    uint256 public constant MAX_DAILY_ACTIONS = 100;
    mapping(address => uint256) public dailyActionCounts;
    mapping(address => uint256) public lastDayReset;

    // Events
    event AIActionRequested(
        uint256 indexed actionId,
        address indexed agent,
        AIActionType actionType,
        string description
    );
    event AIActionExecuted(
        uint256 indexed actionId,
        address indexed agent,
        bool success,
        uint256 gasUsed
    );
    event AIProposalCreated(
        uint256 indexed actionId,
        uint256 indexed proposalId,
        address indexed agent
    );
    event AISpendingExecuted(
        uint256 indexed actionId,
        address indexed agent,
        address token,
        uint256 amount,
        address recipient
    );

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(
        address _daoGovernance,
        address _daoTreasury,
        address _xmrtToken
    ) public initializer {
        __AccessControl_init();
        __ReentrancyGuard_init();
        __Pausable_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);

        daoGovernance = DAO_Governance(_daoGovernance);
        daoTreasury = DAO_Treasury(_daoTreasury);
        xmrtToken = XMRT(_xmrtToken);
    }

    /**
     * @dev Create a governance proposal via AI agent
     */
    function createAIProposal(
        address target,
        uint256 value,
        bytes memory callData,
        string memory description,
        uint256 customThreshold
    ) external onlyRole(AI_AGENT_ROLE) whenNotPaused returns (uint256) {
        _checkActionLimits(msg.sender);

        uint256 actionId = _recordAction(
            msg.sender,
            AIActionType.CreateProposal,
            abi.encode(target, value, callData, description, customThreshold),
            description
        );

        uint256 proposalId = daoGovernance.submitAITriggeredProposal(
            target,
            value,
            callData,
            description,
            customThreshold
        );

        aiActions[actionId].executed = true;
        emit AIProposalCreated(actionId, proposalId, msg.sender);

        return proposalId;
    }

    /**
     * @dev Execute AI-controlled spending
     */
    function executeAISpending(
        address tokenAddress,
        uint256 amount,
        address recipient,
        string memory purpose
    ) external onlyRole(AI_AGENT_ROLE) whenNotPaused returns (uint256) {
        _checkActionLimits(msg.sender);

        uint256 actionId = _recordAction(
            msg.sender,
            AIActionType.ExecuteSpending,
            abi.encode(tokenAddress, amount, recipient, purpose),
            purpose
        );

        daoTreasury.executeAISpending(tokenAddress, amount, recipient, purpose);

        aiActions[actionId].executed = true;
        emit AISpendingExecuted(actionId, msg.sender, tokenAddress, amount, recipient);

        return actionId;
    }

    /**
     * @dev Stake tokens on behalf of the DAO
     */
    function stakeTokensForDAO(uint256 amount) external onlyRole(AI_AGENT_ROLE) whenNotPaused returns (uint256) {
        _checkActionLimits(msg.sender);

        uint256 actionId = _recordAction(
            msg.sender,
            AIActionType.StakeTokens,
            abi.encode(amount),
            string(abi.encodePacked("Stake ", _uint2str(amount), " XMRT tokens"))
        );

        // This would require the AI agent to have XMRT tokens or the treasury to approve
        // For now, we record the action for tracking
        aiActions[actionId].executed = true;

        return actionId;
    }

    /**
     * @dev Batch execute multiple AI actions
     */
    function batchExecuteActions(
        AIActionType[] memory actionTypes,
        bytes[] memory actionDataArray,
        string[] memory descriptions
    ) external onlyRole(AI_AGENT_ROLE) whenNotPaused returns (uint256[] memory) {
        require(actionTypes.length == actionDataArray.length, "Array length mismatch");
        require(actionTypes.length == descriptions.length, "Array length mismatch");
        require(actionTypes.length <= 10, "Too many actions in batch");

        _checkActionLimits(msg.sender);

        uint256[] memory actionIds = new uint256[](actionTypes.length);

        for (uint256 i = 0; i < actionTypes.length; i++) {
            actionIds[i] = _recordAction(
                msg.sender,
                actionTypes[i],
                actionDataArray[i],
                descriptions[i]
            );
        }

        return actionIds;
    }

    /**
     * @dev Get AI agent statistics
     */
    function getAgentStats(address agent) external view returns (
        uint256 totalActions,
        uint256 dailyActions,
        uint256 lastActionTime,
        bool canAct
    ) {
        return (
            agentActionCounts[agent],
            _getCurrentDailyActions(agent),
            agentLastActionTime[agent],
            _canAgentAct(agent)
        );
    }

    /**
     * @dev Get action details
     */
    function getAction(uint256 actionId) external view returns (
        address agent,
        AIActionType actionType,
        bytes memory actionData,
        uint256 timestamp,
        bool executed,
        string memory description,
        uint256 gasUsed
    ) {
        AIAction storage action = aiActions[actionId];
        return (
            action.agent,
            action.actionType,
            action.actionData,
            action.timestamp,
            action.executed,
            action.description,
            action.gasUsed
        );
    }

    /**
     * @dev Get recent actions by agent
     */
    function getRecentActionsByAgent(address agent, uint256 limit) external view returns (uint256[] memory) {
        uint256[] memory recentActions = new uint256[](limit);
        uint256 count = 0;
        
        for (uint256 i = actionCount; i > 0 && count < limit; i--) {
            if (aiActions[i - 1].agent == agent) {
                recentActions[count] = i - 1;
                count++;
            }
        }

        // Resize array to actual count
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = recentActions[i];
        }

        return result;
    }

    /**
     * @dev Internal function to record an action
     */
    function _recordAction(
        address agent,
        AIActionType actionType,
        bytes memory actionData,
        string memory description
    ) internal returns (uint256) {
        uint256 actionId = actionCount++;
        
        aiActions[actionId] = AIAction({
            id: actionId,
            agent: agent,
            actionType: actionType,
            actionData: actionData,
            timestamp: block.timestamp,
            executed: false,
            description: description,
            gasUsed: 0
        });

        agentActionCounts[agent]++;
        agentLastActionTime[agent] = block.timestamp;
        
        // Update daily action count
        if (block.timestamp >= lastDayReset[agent] + 1 days) {
            dailyActionCounts[agent] = 0;
            lastDayReset[agent] = block.timestamp;
        }
        dailyActionCounts[agent]++;

        emit AIActionRequested(actionId, agent, actionType, description);
        return actionId;
    }

    /**
     * @dev Check if agent can perform actions
     */
    function _checkActionLimits(address agent) internal view {
        require(_canAgentAct(agent), "Agent action limits exceeded");
    }

    /**
     * @dev Check if agent can act
     */
    function _canAgentAct(address agent) internal view returns (bool) {
        // Check time interval
        if (block.timestamp < agentLastActionTime[agent] + MIN_ACTION_INTERVAL) {
            return false;
        }

        // Check daily limit
        if (_getCurrentDailyActions(agent) >= MAX_DAILY_ACTIONS) {
            return false;
        }

        return true;
    }

    /**
     * @dev Get current daily actions for agent
     */
    function _getCurrentDailyActions(address agent) internal view returns (uint256) {
        if (block.timestamp >= lastDayReset[agent] + 1 days) {
            return 0;
        }
        return dailyActionCounts[agent];
    }

    /**
     * @dev Convert uint to string
     */
    function _uint2str(uint256 _i) internal pure returns (string memory) {
        if (_i == 0) {
            return "0";
        }
        uint256 j = _i;
        uint256 len;
        while (j != 0) {
            len++;
            j /= 10;
        }
        bytes memory bstr = new bytes(len);
        uint256 k = len;
        while (_i != 0) {
            k = k - 1;
            uint8 temp = (48 + uint8(_i - _i / 10 * 10));
            bytes1 b1 = bytes1(temp);
            bstr[k] = b1;
            _i /= 10;
        }
        return string(bstr);
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

