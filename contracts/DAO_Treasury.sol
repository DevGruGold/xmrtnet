// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title DAO_Treasury
 * @dev Enhanced treasury contract for XMRT DAO with multi-asset support and governance integration
 */
contract DAO_Treasury is
    Initializable,
    AccessControlUpgradeable,
    ReentrancyGuardUpgradeable,
    PausableUpgradeable,
    UUPSUpgradeable
{
    using SafeERC20 for IERC20;

    // Roles
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");
    bytes32 public constant AI_AGENT_ROLE = keccak256("AI_AGENT_ROLE");
    bytes32 public constant GUARDIAN_ROLE = keccak256("GUARDIAN_ROLE");

    // Treasury allocation types
    enum AllocationType {
        General,
        Development,
        Marketing,
        Operations,
        Investment,
        Emergency
    }

    // Asset information
    struct AssetInfo {
        address tokenAddress;
        uint256 balance;
        uint256 allocated;
        bool isActive;
        string name;
        string symbol;
    }

    // Allocation tracking
    struct Allocation {
        uint256 id;
        address tokenAddress;
        uint256 amount;
        AllocationType allocationType;
        address recipient;
        string description;
        uint256 timestamp;
        bool executed;
        address approvedBy;
    }

    // Spending limits for AI agents
    struct SpendingLimit {
        address tokenAddress;
        uint256 dailyLimit;
        uint256 totalLimit;
        uint256 dailySpent;
        uint256 totalSpent;
        uint256 lastResetTime;
        bool isActive;
    }

    // State variables
    mapping(address => AssetInfo) public assets;
    address[] public assetList;
    mapping(uint256 => Allocation) public allocations;
    uint256 public allocationCount;
    mapping(address => SpendingLimit) public aiSpendingLimits;
    mapping(AllocationType => uint256) public allocationLimits;

    // Revenue tracking
    mapping(address => uint256) public totalRevenue;
    mapping(address => mapping(uint256 => uint256)) public monthlyRevenue; // token => month => amount

    // Events
    event AssetAdded(address indexed tokenAddress, string name, string symbol);
    event AssetRemoved(address indexed tokenAddress);
    event FundsReceived(address indexed tokenAddress, uint256 amount, address indexed from);
    event AllocationCreated(
        uint256 indexed allocationId,
        address indexed tokenAddress,
        uint256 amount,
        AllocationType allocationType,
        address indexed recipient,
        string description
    );
    event AllocationExecuted(uint256 indexed allocationId, address indexed executor);
    event SpendingLimitSet(address indexed tokenAddress, uint256 dailyLimit, uint256 totalLimit);
    event AISpendingExecuted(address indexed agent, address indexed tokenAddress, uint256 amount, string purpose);
    event EmergencyWithdrawal(address indexed tokenAddress, uint256 amount, address indexed to);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize() public initializer {
        __AccessControl_init();
        __ReentrancyGuard_init();
        __Pausable_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(GUARDIAN_ROLE, msg.sender);

        // Set default allocation limits (in basis points, 10000 = 100%)
        allocationLimits[AllocationType.Development] = 3000; // 30%
        allocationLimits[AllocationType.Marketing] = 2000; // 20%
        allocationLimits[AllocationType.Operations] = 2000; // 20%
        allocationLimits[AllocationType.Investment] = 2000; // 20%
        allocationLimits[AllocationType.Emergency] = 1000; // 10%
    }

    /**
     * @dev Add a new asset to the treasury
     */
    function addAsset(
        address tokenAddress,
        string memory name,
        string memory symbol
    ) external onlyRole(ADMIN_ROLE) {
        require(tokenAddress != address(0), "Invalid token address");
        require(!assets[tokenAddress].isActive, "Asset already exists");

        assets[tokenAddress] = AssetInfo({
            tokenAddress: tokenAddress,
            balance: 0,
            allocated: 0,
            isActive: true,
            name: name,
            symbol: symbol
        });

        assetList.push(tokenAddress);
        emit AssetAdded(tokenAddress, name, symbol);
    }

    /**
     * @dev Remove an asset from the treasury
     */
    function removeAsset(address tokenAddress) external onlyRole(ADMIN_ROLE) {
        require(assets[tokenAddress].isActive, "Asset not found");
        require(assets[tokenAddress].balance == 0, "Asset has balance");

        assets[tokenAddress].isActive = false;
        emit AssetRemoved(tokenAddress);
    }

    /**
     * @dev Receive ETH
     */
    receive() external payable {
        _updateBalance(address(0), msg.value);
        emit FundsReceived(address(0), msg.value, msg.sender);
    }

    /**
     * @dev Receive ERC20 tokens
     */
    function receiveTokens(address tokenAddress, uint256 amount) external nonReentrant {
        require(assets[tokenAddress].isActive, "Asset not supported");
        require(amount > 0, "Amount must be greater than 0");

        IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
        _updateBalance(tokenAddress, amount);
        
        emit FundsReceived(tokenAddress, amount, msg.sender);
    }

    /**
     * @dev Create an allocation proposal (called by governance)
     */
    function createAllocation(
        address tokenAddress,
        uint256 amount,
        AllocationType allocationType,
        address recipient,
        string memory description
    ) external onlyRole(GOVERNANCE_ROLE) returns (uint256) {
        require(assets[tokenAddress].isActive || tokenAddress == address(0), "Asset not supported");
        require(amount > 0, "Amount must be greater than 0");
        require(recipient != address(0), "Invalid recipient");

        uint256 availableBalance = _getAvailableBalance(tokenAddress);
        require(amount <= availableBalance, "Insufficient available balance");

        uint256 allocationId = allocationCount++;
        allocations[allocationId] = Allocation({
            id: allocationId,
            tokenAddress: tokenAddress,
            amount: amount,
            allocationType: allocationType,
            recipient: recipient,
            description: description,
            timestamp: block.timestamp,
            executed: false,
            approvedBy: msg.sender
        });

        // Update allocated amount
        if (tokenAddress == address(0)) {
            // ETH handling would need special case
        } else {
            assets[tokenAddress].allocated += amount;
        }

        emit AllocationCreated(allocationId, tokenAddress, amount, allocationType, recipient, description);
        return allocationId;
    }

    /**
     * @dev Execute an allocation
     */
    function executeAllocation(uint256 allocationId) external nonReentrant whenNotPaused {
        Allocation storage allocation = allocations[allocationId];
        require(!allocation.executed, "Already executed");
        require(allocation.amount > 0, "Invalid allocation");

        allocation.executed = true;

        if (allocation.tokenAddress == address(0)) {
            // ETH transfer
            (bool success, ) = allocation.recipient.call{value: allocation.amount}("");
            require(success, "ETH transfer failed");
        } else {
            // ERC20 transfer
            IERC20(allocation.tokenAddress).safeTransfer(allocation.recipient, allocation.amount);
            assets[allocation.tokenAddress].balance -= allocation.amount;
            assets[allocation.tokenAddress].allocated -= allocation.amount;
        }

        emit AllocationExecuted(allocationId, msg.sender);
    }

    /**
     * @dev Set spending limits for AI agents
     */
    function setAISpendingLimit(
        address tokenAddress,
        uint256 dailyLimit,
        uint256 totalLimit
    ) external onlyRole(ADMIN_ROLE) {
        require(assets[tokenAddress].isActive || tokenAddress == address(0), "Asset not supported");

        aiSpendingLimits[tokenAddress] = SpendingLimit({
            tokenAddress: tokenAddress,
            dailyLimit: dailyLimit,
            totalLimit: totalLimit,
            dailySpent: 0,
            totalSpent: 0,
            lastResetTime: block.timestamp,
            isActive: true
        });

        emit SpendingLimitSet(tokenAddress, dailyLimit, totalLimit);
    }

    /**
     * @dev AI agent spending function with automatic limits
     */
    function executeAISpending(
        address tokenAddress,
        uint256 amount,
        address recipient,
        string memory purpose
    ) external onlyRole(AI_AGENT_ROLE) nonReentrant whenNotPaused {
        require(assets[tokenAddress].isActive || tokenAddress == address(0), "Asset not supported");
        require(amount > 0, "Amount must be greater than 0");
        require(recipient != address(0), "Invalid recipient");

        SpendingLimit storage limit = aiSpendingLimits[tokenAddress];
        require(limit.isActive, "Spending limit not set");

        // Reset daily spending if a day has passed
        if (block.timestamp >= limit.lastResetTime + 1 days) {
            limit.dailySpent = 0;
            limit.lastResetTime = block.timestamp;
        }

        // Check limits
        require(limit.dailySpent + amount <= limit.dailyLimit, "Daily spending limit exceeded");
        require(limit.totalSpent + amount <= limit.totalLimit, "Total spending limit exceeded");

        uint256 availableBalance = _getAvailableBalance(tokenAddress);
        require(amount <= availableBalance, "Insufficient available balance");

        // Update spending tracking
        limit.dailySpent += amount;
        limit.totalSpent += amount;

        // Execute transfer
        if (tokenAddress == address(0)) {
            (bool success, ) = recipient.call{value: amount}("");
            require(success, "ETH transfer failed");
        } else {
            IERC20(tokenAddress).safeTransfer(recipient, amount);
            assets[tokenAddress].balance -= amount;
        }

        emit AISpendingExecuted(msg.sender, tokenAddress, amount, purpose);
    }

    /**
     * @dev Emergency withdrawal function
     */
    function emergencyWithdraw(
        address tokenAddress,
        uint256 amount,
        address to
    ) external onlyRole(GUARDIAN_ROLE) nonReentrant {
        require(to != address(0), "Invalid recipient");

        if (tokenAddress == address(0)) {
            require(amount <= address(this).balance, "Insufficient ETH balance");
            (bool success, ) = to.call{value: amount}("");
            require(success, "ETH transfer failed");
        } else {
            require(amount <= IERC20(tokenAddress).balanceOf(address(this)), "Insufficient token balance");
            IERC20(tokenAddress).safeTransfer(to, amount);
            if (assets[tokenAddress].isActive) {
                assets[tokenAddress].balance -= amount;
            }
        }

        emit EmergencyWithdrawal(tokenAddress, amount, to);
    }

    /**
     * @dev Update asset balance (internal)
     */
    function _updateBalance(address tokenAddress, uint256 amount) internal {
        if (tokenAddress == address(0)) {
            // ETH - balance is automatically updated
            return;
        }

        if (assets[tokenAddress].isActive) {
            assets[tokenAddress].balance += amount;
        }

        // Track revenue
        totalRevenue[tokenAddress] += amount;
        uint256 currentMonth = block.timestamp / 30 days;
        monthlyRevenue[tokenAddress][currentMonth] += amount;
    }

    /**
     * @dev Get available balance (total - allocated)
     */
    function _getAvailableBalance(address tokenAddress) internal view returns (uint256) {
        if (tokenAddress == address(0)) {
            return address(this).balance;
        }

        if (!assets[tokenAddress].isActive) {
            return 0;
        }

        return assets[tokenAddress].balance - assets[tokenAddress].allocated;
    }

    /**
     * @dev Get asset balance
     */
    function getAssetBalance(address tokenAddress) external view returns (uint256) {
        if (tokenAddress == address(0)) {
            return address(this).balance;
        }
        return assets[tokenAddress].balance;
    }

    /**
     * @dev Get available balance for spending
     */
    function getAvailableBalance(address tokenAddress) external view returns (uint256) {
        return _getAvailableBalance(tokenAddress);
    }

    /**
     * @dev Get all supported assets
     */
    function getSupportedAssets() external view returns (address[] memory) {
        return assetList;
    }

    /**
     * @dev Get allocation details
     */
    function getAllocation(uint256 allocationId) external view returns (
        uint256 id,
        address tokenAddress,
        uint256 amount,
        AllocationType allocationType,
        address recipient,
        string memory description,
        uint256 timestamp,
        bool executed,
        address approvedBy
    ) {
        Allocation storage allocation = allocations[allocationId];
        return (
            allocation.id,
            allocation.tokenAddress,
            allocation.amount,
            allocation.allocationType,
            allocation.recipient,
            allocation.description,
            allocation.timestamp,
            allocation.executed,
            allocation.approvedBy
        );
    }

    /**
     * @dev Get AI spending limit
     */
    function getAISpendingLimit(address tokenAddress) external view returns (
        uint256 dailyLimit,
        uint256 totalLimit,
        uint256 dailySpent,
        uint256 totalSpent,
        uint256 dailyRemaining,
        uint256 totalRemaining
    ) {
        SpendingLimit storage limit = aiSpendingLimits[tokenAddress];
        
        uint256 currentDailySpent = limit.dailySpent;
        if (block.timestamp >= limit.lastResetTime + 1 days) {
            currentDailySpent = 0;
        }

        return (
            limit.dailyLimit,
            limit.totalLimit,
            currentDailySpent,
            limit.totalSpent,
            limit.dailyLimit - currentDailySpent,
            limit.totalLimit - limit.totalSpent
        );
    }

    /**
     * @dev Pause contract
     */
    function pause() external onlyRole(GUARDIAN_ROLE) {
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

