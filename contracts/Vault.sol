
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "./DAO_Treasury.sol";

/**
 * @title Vault
 * @dev Legacy vault contract that now acts as a proxy to the new DAO_Treasury
 */
contract Vault is
    Initializable,
    AccessControlUpgradeable,
    ReentrancyGuardUpgradeable,
    PausableUpgradeable,
    UUPSUpgradeable
{
    address public constant TREASURY = 0x7099F848b614d0d510BeAB53b3bE409cbd720dF5;
    
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");

    DAO_Treasury public daoTreasury;

    event TreasuryContractSet(address indexed treasury);
    event LegacyWithdrawal(uint256 amount, address indexed to);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address _daoTreasury) public initializer {
        __AccessControl_init();
        __ReentrancyGuard_init();
        __Pausable_init();
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);

        if (_daoTreasury != address(0)) {
            daoTreasury = DAO_Treasury(_daoTreasury);
        }
    }

    /**
     * @dev Legacy withdraw function - now redirects to DAO_Treasury
     */
    function withdraw(uint256 amount) public onlyRole(GOVERNANCE_ROLE) nonReentrant whenNotPaused {
        require(address(daoTreasury) != address(0), "Treasury not set");
        require(amount > 0, "Amount must be greater than 0");
        
        // This would need to be implemented as a governance proposal in the new system
        // For now, we emit an event for tracking
        emit LegacyWithdrawal(amount, msg.sender);
    }

    /**
     * @dev Set the DAO Treasury contract
     */
    function setDAOTreasury(address _daoTreasury) external onlyRole(ADMIN_ROLE) {
        require(_daoTreasury != address(0), "Invalid address");
        daoTreasury = DAO_Treasury(_daoTreasury);
        emit TreasuryContractSet(_daoTreasury);
    }

    /**
     * @dev Get treasury balance (ETH)
     */
    function getBalance() external view returns (uint256) {
        if (address(daoTreasury) != address(0)) {
            return daoTreasury.getAssetBalance(address(0));
        }
        return address(this).balance;
    }

    /**
     * @dev Receive ETH and forward to treasury
     */
    receive() external payable {
        if (address(daoTreasury) != address(0)) {
            (bool success, ) = address(daoTreasury).call{value: msg.value}("");
            require(success, "Forward to treasury failed");
        }
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
