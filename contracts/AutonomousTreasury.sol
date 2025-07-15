// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "./XMRT.sol";
import "./AutonomousDAO.sol";
import "./AgentManager.sol";

/**
 * @title AutonomousTreasury
 * @dev Fully autonomous treasury management with AI agent execution authority
 * @notice Enables complete autonomous financial operations and asset management
 */
contract AutonomousTreasury is
    Initializable,
    AccessControlUpgradeable,
    ReentrancyGuardUpgradeable,
    PausableUpgradeable,
    UUPSUpgradeable
{
    using SafeERC20 for IERC20;

    // Roles
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant TREASURY_AGENT_ROLE = keccak256("TREASURY_AGENT_ROLE");
    bytes32 public constant FINANCIAL_CONTROLLER_ROLE = keccak256("FINANCIAL_CONTROLLER_ROLE");
    bytes32 public constant EMERGENCY_ROLE = keccak256("EMERGENCY_ROLE");
    bytes32 public constant AUDITOR_ROLE = keccak256("AUDITOR_ROLE");

    // Treasury Operation Types
    enum OperationType {
        Transfer,
        Investment,
        Withdrawal,
        Swap,
        Stake,
        Unstake,
        Yield,
        Rebalance,
        Emergency
    }

    // Investment Strategies
    enum InvestmentStrategy {
        Conservative,
        Moderate,
        Aggressive,
        Yield,
        Liquidity,
        Diversified
    }

    // Asset Categories
    enum AssetCategory {
        Stable,
        Volatile,
        Yield,
        Liquidity,
        Governance,
        Utility
    }

    // Treasury Operation Structure
    struct TreasuryOperation {
        uint256 operationId;
        OperationType operationType;
        address initiator;
        address targetToken;
        uint256 amount;
        address recipient;
        bytes operationData;
        uint256 timestamp;
        uint256 executionTime;
        bool executed;
        bool approved;
        uint256 approvalCount;
        mapping(address => bool) approvals;
        string description;
        uint256 priority;
    }

    // Asset Management Structure
    struct AssetInfo {
        address tokenAddress;
        string symbol;
        AssetCategory category;
        uint256 balance;
        uint256 targetAllocation; // Percentage in basis points (10000 = 100%)
        uint256 currentAllocation;
        uint256 minBalance;
        uint256 maxBalance;
        bool isActive;
        uint256 lastRebalance;
        uint256 yieldGenerated;
    }

    // Investment Pool Structure
    struct InvestmentPool {
        uint256 poolId;
        string name;
        InvestmentStrategy strategy;
        address[] assets;
        uint256 totalValue;
        uint256 targetReturn; // Annual percentage in basis points
        uint256 riskLevel; // 1-10 scale
        bool isActive;
        address poolManager;
        uint256 createdAt;
        uint256 lastRebalance;
    }

    // Autonomous Budget Structure
    struct AutonomousBudget {
        string category;
        uint256 monthlyLimit;
        uint256 currentSpent;
        uint256 lastReset;
        bool autoApprove;
        address[] authorizedAgents;
        uint256 emergencyLimit;
    }

    // Yield Strategy Structure
    struct YieldStrategy {
        uint256 strategyId;
        string name;
        address targetProtocol;
        address[] inputTokens;
        uint256 expectedAPY;
        uint256 riskScore;
        uint256 minAmount;
        uint256 maxAmount;
        bool isActive;
        uint256 totalDeployed;
        uint256 totalReturns;
    }

    // State Variables
    XMRT public xmrtToken;
    AutonomousDAO public autonomousDAO;
    AgentManager public agentManager;

    uint256 public operationCount;
    uint256 public poolCount;
    uint256 public strategyCount;
    uint256 public totalTreasuryValue;
    uint256 public totalYieldGenerated;

    mapping(uint256 => TreasuryOperation) public operations;
    mapping(address => AssetInfo) public assets;
    mapping(uint256 => InvestmentPool) public investmentPools;
    mapping(string => AutonomousBudget) public budgets;
    mapping(uint256 => YieldStrategy) public yieldStrategies;
    mapping(address => bool) public supportedTokens;
    mapping(address => uint256) public agentSpendingLimits;
    mapping(address => uint256) public agentDailySpent;
    mapping(address => uint256) public lastSpendingReset;

    // Treasury Configuration
    struct TreasuryConfig {
        uint256 minApprovals;
        uint256 maxSingleTransfer;
        uint256 dailyTransferLimit;
        uint256 emergencyWithdrawLimit;
        uint256 rebalanceThreshold; // Percentage deviation to trigger rebalance
        uint256 yieldHarvestThreshold;
        bool autoRebalanceEnabled;
        bool autoYieldHarvestEnabled;
        uint256 riskTolerance;
    }

    TreasuryConfig public treasuryConfig;

    // Asset allocation targets
    address[] public managedAssets;
    uint256 public constant MAX_ASSETS = 50;
    uint256 public constant BASIS_POINTS = 10000;

    // Events
    event OperationCreated(uint256 indexed operationId, OperationType operationType, address indexed initiator);
    event OperationExecuted(uint256 indexed operationId, bool success, address indexed executor);
    event AssetAdded(address indexed token, AssetCategory category);
    event InvestmentPoolCreated(uint256 indexed poolId, InvestmentStrategy strategy);
    event YieldHarvested(address indexed token, uint256 amount);
    event RebalanceExecuted(uint256 totalValue, uint256 timestamp);
    event BudgetUpdated(string category, uint256 newLimit);
    event EmergencyWithdrawal(address indexed token, uint256 amount, address indexed recipient);
    event AgentSpendingLimitUpdated(address indexed agent, uint256 newLimit);

    // Modifiers
    modifier onlyTreasuryAgent() {
        require(hasRole(TREASURY_AGENT_ROLE, msg.sender), "Not a treasury agent");
        _;
    }

    modifier onlyFinancialController() {
        require(hasRole(FINANCIAL_CONTROLLER_ROLE, msg.sender), "Not a financial controller");
        _;
    }

    modifier operationExists(uint256 _operationId) {
        require(_operationId > 0 && _operationId <= operationCount, "Operation does not exist");
        _;
    }

    modifier withinSpendingLimit(address _agent, uint256 _amount) {
        _checkAndUpdateSpendingLimit(_agent, _amount);
        _;
    }

    /**
     * @dev Initialize the AutonomousTreasury
     */
    function initialize(
        address _xmrtToken,
        address _autonomousDAO,
        address _agentManager
    ) public initializer {
        __AccessControl_init();
        __ReentrancyGuard_init();
        __Pausable_init();
        __UUPSUpgradeable_init();

        xmrtToken = XMRT(_xmrtToken);
        autonomousDAO = AutonomousDAO(_autonomousDAO);
        agentManager = AgentManager(_agentManager);

        // Initialize treasury configuration
        treasuryConfig = TreasuryConfig({
            minApprovals: 2,
            maxSingleTransfer: 100000 * 10**18, // 100,000 XMRT
            dailyTransferLimit: 500000 * 10**18, // 500,000 XMRT
            emergencyWithdrawLimit: 50000 * 10**18, // 50,000 XMRT
            rebalanceThreshold: 500, // 5%
            yieldHarvestThreshold: 1000 * 10**18, // 1,000 XMRT
            autoRebalanceEnabled: true,
            autoYieldHarvestEnabled: true,
            riskTolerance: 5 // Medium risk
        });

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(FINANCIAL_CONTROLLER_ROLE, msg.sender);
        _grantRole(EMERGENCY_ROLE, msg.sender);

        // Add XMRT as the primary asset
        _addAsset(_xmrtToken, "XMRT", AssetCategory.Governance, 5000); // 50% target allocation
    }

    /**
     * @dev Create a new treasury operation
     */
    function createOperation(
        OperationType _operationType,
        address _targetToken,
        uint256 _amount,
        address _recipient,
        bytes memory _operationData,
        string memory _description,
        uint256 _priority
    ) external onlyTreasuryAgent returns (uint256) {
        require(supportedTokens[_targetToken] || _targetToken == address(xmrtToken), "Token not supported");
        require(_amount > 0, "Amount must be greater than 0");

        operationCount++;
        uint256 operationId = operationCount;

        TreasuryOperation storage operation = operations[operationId];
        operation.operationId = operationId;
        operation.operationType = _operationType;
        operation.initiator = msg.sender;
        operation.targetToken = _targetToken;
        operation.amount = _amount;
        operation.recipient = _recipient;
        operation.operationData = _operationData;
        operation.timestamp = block.timestamp;
        operation.description = _description;
        operation.priority = _priority;

        // Auto-approve for small amounts within agent limits
        if (_amount <= agentSpendingLimits[msg.sender] && 
            _operationType != OperationType.Emergency) {
            operation.approved = true;
            operation.approvalCount = treasuryConfig.minApprovals;
        }

        emit OperationCreated(operationId, _operationType, msg.sender);
        return operationId;
    }

    /**
     * @dev Approve a treasury operation
     */
    function approveOperation(uint256 _operationId) external onlyFinancialController operationExists(_operationId) {
        TreasuryOperation storage operation = operations[_operationId];
        require(!operation.executed, "Operation already executed");
        require(!operation.approvals[msg.sender], "Already approved");

        operation.approvals[msg.sender] = true;
        operation.approvalCount++;

        if (operation.approvalCount >= treasuryConfig.minApprovals) {
            operation.approved = true;
        }
    }

    /**
     * @dev Execute approved treasury operation
     */
    function executeOperation(uint256 _operationId) external onlyTreasuryAgent operationExists(_operationId) nonReentrant withinSpendingLimit(msg.sender, operations[_operationId].amount) {
        TreasuryOperation storage operation = operations[_operationId];
        require(operation.approved, "Operation not approved");
        require(!operation.executed, "Operation already executed");

        operation.executed = true;
        operation.executionTime = block.timestamp;

        bool success = _executeOperationLogic(operation);

        emit OperationExecuted(_operationId, success, msg.sender);
    }

    /**
     * @dev Internal operation execution logic
     */
    function _executeOperationLogic(TreasuryOperation storage _operation) internal returns (bool) {
        if (_operation.operationType == OperationType.Transfer) {
            return _executeTransfer(_operation);
        } else if (_operation.operationType == OperationType.Investment) {
            return _executeInvestment(_operation);
        } else if (_operation.operationType == OperationType.Withdrawal) {
            return _executeWithdrawal(_operation);
        } else if (_operation.operationType == OperationType.Swap) {
            return _executeSwap(_operation);
        } else if (_operation.operationType == OperationType.Stake) {
            return _executeStake(_operation);
        } else if (_operation.operationType == OperationType.Yield) {
            return _executeYieldHarvest(_operation);
        } else if (_operation.operationType == OperationType.Rebalance) {
            return _executeRebalance(_operation);
        }

        return false;
    }

    /**
     * @dev Execute transfer operation
     */
    function _executeTransfer(TreasuryOperation storage _operation) internal returns (bool) {
        IERC20 token = IERC20(_operation.targetToken);
        require(token.balanceOf(address(this)) >= _operation.amount, "Insufficient balance");

        token.safeTransfer(_operation.recipient, _operation.amount);

        // Update asset balance
        if (assets[_operation.targetToken].isActive) {
            assets[_operation.targetToken].balance -= _operation.amount;
        }

        return true;
    }

    /**
     * @dev Execute investment operation
     */
    function _executeInvestment(TreasuryOperation storage _operation) internal returns (bool) {
        // Decode investment data
        (uint256 poolId, uint256 expectedReturn) = abi.decode(_operation.operationData, (uint256, uint256));

        require(poolId <= poolCount && investmentPools[poolId].isActive, "Invalid investment pool");

        InvestmentPool storage pool = investmentPools[poolId];
        pool.totalValue += _operation.amount;

        // Execute investment logic here (integrate with DeFi protocols)
        IERC20(_operation.targetToken).safeTransfer(pool.poolManager, _operation.amount);

        return true;
    }

    /**
     * @dev Execute withdrawal operation
     */
    function _executeWithdrawal(TreasuryOperation storage _operation) internal returns (bool) {
        // Similar to transfer but with additional withdrawal logic
        return _executeTransfer(_operation);
    }

    /**
     * @dev Execute token swap operation
     */
    function _executeSwap(TreasuryOperation storage _operation) internal returns (bool) {
        // Decode swap data
        (address tokenOut, uint256 minAmountOut, address dexRouter) = abi.decode(
            _operation.operationData, 
            (address, uint256, address)
        );

        // Execute swap logic (integrate with DEX)
        // This would typically involve calling a DEX router

        return true;
    }

    /**
     * @dev Execute staking operation
     */
    function _executeStake(TreasuryOperation storage _operation) internal returns (bool) {
        // Decode staking data
        (address stakingContract, uint256 duration) = abi.decode(
            _operation.operationData, 
            (address, uint256)
        );

        // Execute staking logic
        IERC20(_operation.targetToken).safeApprove(stakingContract, _operation.amount);

        return true;
    }

    /**
     * @dev Execute yield harvest operation
     */
    function _executeYieldHarvest(TreasuryOperation storage _operation) internal returns (bool) {
        // Harvest yield from various protocols
        uint256 harvestedAmount = _operation.amount;

        totalYieldGenerated += harvestedAmount;

        if (assets[_operation.targetToken].isActive) {
            assets[_operation.targetToken].yieldGenerated += harvestedAmount;
        }

        emit YieldHarvested(_operation.targetToken, harvestedAmount);
        return true;
    }

    /**
     * @dev Execute portfolio rebalance
     */
    function _executeRebalance(TreasuryOperation storage _operation) internal returns (bool) {
        _rebalancePortfolio();
        emit RebalanceExecuted(totalTreasuryValue, block.timestamp);
        return true;
    }

    /**
     * @dev Add a new asset to treasury management
     */
    function addAsset(
        address _tokenAddress,
        string memory _symbol,
        AssetCategory _category,
        uint256 _targetAllocation
    ) external onlyFinancialController {
        _addAsset(_tokenAddress, _symbol, _category, _targetAllocation);
    }

    /**
     * @dev Internal function to add asset
     */
    function _addAsset(
        address _tokenAddress,
        string memory _symbol,
        AssetCategory _category,
        uint256 _targetAllocation
    ) internal {
        require(!assets[_tokenAddress].isActive, "Asset already exists");
        require(managedAssets.length < MAX_ASSETS, "Maximum assets reached");
        require(_targetAllocation <= BASIS_POINTS, "Invalid allocation");

        assets[_tokenAddress] = AssetInfo({
            tokenAddress: _tokenAddress,
            symbol: _symbol,
            category: _category,
            balance: IERC20(_tokenAddress).balanceOf(address(this)),
            targetAllocation: _targetAllocation,
            currentAllocation: 0,
            minBalance: 0,
            maxBalance: type(uint256).max,
            isActive: true,
            lastRebalance: block.timestamp,
            yieldGenerated: 0
        });

        managedAssets.push(_tokenAddress);
        supportedTokens[_tokenAddress] = true;

        emit AssetAdded(_tokenAddress, _category);
    }

    /**
     * @dev Create investment pool
     */
    function createInvestmentPool(
        string memory _name,
        InvestmentStrategy _strategy,
        address[] memory _assets,
        uint256 _targetReturn,
        uint256 _riskLevel
    ) external onlyFinancialController returns (uint256) {
        poolCount++;
        uint256 poolId = poolCount;

        investmentPools[poolId] = InvestmentPool({
            poolId: poolId,
            name: _name,
            strategy: _strategy,
            assets: _assets,
            totalValue: 0,
            targetReturn: _targetReturn,
            riskLevel: _riskLevel,
            isActive: true,
            poolManager: msg.sender,
            createdAt: block.timestamp,
            lastRebalance: block.timestamp
        });

        emit InvestmentPoolCreated(poolId, _strategy);
        return poolId;
    }

    /**
     * @dev Set autonomous budget for category
     */
    function setAutonomousBudget(
        string memory _category,
        uint256 _monthlyLimit,
        bool _autoApprove,
        address[] memory _authorizedAgents,
        uint256 _emergencyLimit
    ) external onlyFinancialController {
        budgets[_category] = AutonomousBudget({
            category: _category,
            monthlyLimit: _monthlyLimit,
            currentSpent: 0,
            lastReset: block.timestamp,
            autoApprove: _autoApprove,
            authorizedAgents: _authorizedAgents,
            emergencyLimit: _emergencyLimit
        });

        emit BudgetUpdated(_category, _monthlyLimit);
    }

    /**
     * @dev Set agent spending limit
     */
    function setAgentSpendingLimit(address _agent, uint256 _dailyLimit) external onlyFinancialController {
        agentSpendingLimits[_agent] = _dailyLimit;
        emit AgentSpendingLimitUpdated(_agent, _dailyLimit);
    }

    /**
     * @dev Autonomous portfolio rebalancing
     */
    function _rebalancePortfolio() internal {
        if (!treasuryConfig.autoRebalanceEnabled) return;

        uint256 totalValue = _calculateTotalTreasuryValue();

        for (uint256 i = 0; i < managedAssets.length; i++) {
            address asset = managedAssets[i];
            AssetInfo storage assetInfo = assets[asset];

            if (!assetInfo.isActive) continue;

            uint256 currentBalance = IERC20(asset).balanceOf(address(this));
            uint256 targetValue = (totalValue * assetInfo.targetAllocation) / BASIS_POINTS;
            uint256 currentValue = currentBalance; // Simplified - would need price oracle

            assetInfo.currentAllocation = (currentValue * BASIS_POINTS) / totalValue;

            // Check if rebalancing is needed
            uint256 deviation = assetInfo.currentAllocation > assetInfo.targetAllocation
                ? assetInfo.currentAllocation - assetInfo.targetAllocation
                : assetInfo.targetAllocation - assetInfo.currentAllocation;

            if (deviation > treasuryConfig.rebalanceThreshold) {
                // Execute rebalancing logic
                _executeAssetRebalance(asset, targetValue, currentValue);
            }

            assetInfo.lastRebalance = block.timestamp;
        }
    }

    /**
     * @dev Execute asset rebalancing
     */
    function _executeAssetRebalance(address _asset, uint256 _targetValue, uint256 _currentValue) internal {
        // Implement rebalancing logic
        // This would involve buying/selling assets to reach target allocation
    }

    /**
     * @dev Calculate total treasury value
     */
    function _calculateTotalTreasuryValue() internal view returns (uint256) {
        uint256 total = 0;

        for (uint256 i = 0; i < managedAssets.length; i++) {
            address asset = managedAssets[i];
            if (assets[asset].isActive) {
                uint256 balance = IERC20(asset).balanceOf(address(this));
                // In production, multiply by asset price from oracle
                total += balance;
            }
        }

        return total;
    }

    /**
     * @dev Check and update agent spending limit
     */
    function _checkAndUpdateSpendingLimit(address _agent, uint256 _amount) internal {
        uint256 dailyLimit = agentSpendingLimits[_agent];
        if (dailyLimit == 0) return; // No limit set

        // Reset daily spending if new day
        if (block.timestamp >= lastSpendingReset[_agent] + 1 days) {
            agentDailySpent[_agent] = 0;
            lastSpendingReset[_agent] = block.timestamp;
        }

        require(agentDailySpent[_agent] + _amount <= dailyLimit, "Daily spending limit exceeded");
        agentDailySpent[_agent] += _amount;
    }

    /**
     * @dev Emergency withdrawal function
     */
    function emergencyWithdraw(
        address _token,
        uint256 _amount,
        address _recipient
    ) external onlyRole(EMERGENCY_ROLE) nonReentrant {
        require(_amount <= treasuryConfig.emergencyWithdrawLimit, "Exceeds emergency limit");

        IERC20(_token).safeTransfer(_recipient, _amount);

        emit EmergencyWithdrawal(_token, _amount, _recipient);
    }

    /**
     * @dev Automated yield harvesting
     */
    function harvestYield() external onlyTreasuryAgent {
        if (!treasuryConfig.autoYieldHarvestEnabled) return;

        for (uint256 i = 0; i < managedAssets.length; i++) {
            address asset = managedAssets[i];
            AssetInfo storage assetInfo = assets[asset];

            if (assetInfo.isActive && assetInfo.category == AssetCategory.Yield) {
                // Check if harvest threshold is met
                uint256 pendingYield = _getPendingYield(asset);

                if (pendingYield >= treasuryConfig.yieldHarvestThreshold) {
                    _harvestAssetYield(asset, pendingYield);
                }
            }
        }
    }

    /**
     * @dev Get pending yield for asset
     */
    function _getPendingYield(address _asset) internal view returns (uint256) {
        // Implement yield calculation logic for different protocols
        return 0; // Placeholder
    }

    /**
     * @dev Harvest yield for specific asset
     */
    function _harvestAssetYield(address _asset, uint256 _amount) internal {
        // Implement yield harvesting logic
        assets[_asset].yieldGenerated += _amount;
        totalYieldGenerated += _amount;

        emit YieldHarvested(_asset, _amount);
    }

    // View Functions

    function getTreasuryValue() external view returns (uint256) {
        return _calculateTotalTreasuryValue();
    }

    function getAssetInfo(address _asset) external view returns (AssetInfo memory) {
        return assets[_asset];
    }

    function getOperation(uint256 _operationId) external view returns (
        OperationType operationType,
        address initiator,
        address targetToken,
        uint256 amount,
        address recipient,
        bool executed,
        bool approved,
        uint256 approvalCount
    ) {
        TreasuryOperation storage operation = operations[_operationId];
        return (
            operation.operationType,
            operation.initiator,
            operation.targetToken,
            operation.amount,
            operation.recipient,
            operation.executed,
            operation.approved,
            operation.approvalCount
        );
    }

    function getInvestmentPool(uint256 _poolId) external view returns (InvestmentPool memory) {
        return investmentPools[_poolId];
    }

    function getBudget(string memory _category) external view returns (AutonomousBudget memory) {
        return budgets[_category];
    }

    function getAgentSpendingInfo(address _agent) external view returns (
        uint256 dailyLimit,
        uint256 dailySpent,
        uint256 lastReset
    ) {
        return (
            agentSpendingLimits[_agent],
            agentDailySpent[_agent],
            lastSpendingReset[_agent]
        );
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyRole(ADMIN_ROLE) {}
}