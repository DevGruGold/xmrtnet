// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "./XMRT.sol";

/**
 * @title DAO_Governance
 * @dev Comprehensive governance contract for XMRT DAO with AI agent integration
 */
contract DAO_Governance is
    Initializable,
    AccessControlUpgradeable,
    ReentrancyGuardUpgradeable,
    PausableUpgradeable,
    UUPSUpgradeable
{
    using ECDSA for bytes32;

    // Roles
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant AI_AGENT_ROLE = keccak256("AI_AGENT_ROLE");
    bytes32 public constant GUARDIAN_ROLE = keccak256("GUARDIAN_ROLE");

    // Proposal states
    enum ProposalState {
        Pending,
        Active,
        Queued,
        Executed,
        Canceled,
        Defeated
    }

    // Proposal structure
    struct Proposal {
        uint256 id;
        address proposer;
        address target;
        uint256 value;
        bytes callData;
        string description;
        uint256 startTime;
        uint256 endTime;
        uint256 votesFor;
        uint256 votesAgainst;
        uint256 quorumRequired;
        uint256 thresholdRequired; // Percentage (e.g., 5000 = 50%)
        bool executed;
        bool canceled;
        mapping(address => bool) hasVoted;
        mapping(address => uint256) votingPower;
    }

    // Configuration
    uint256 public constant VOTING_PERIOD = 7 days;
    uint256 public constant TIMELOCK_PERIOD = 2 days;
    uint256 public constant MIN_PROPOSAL_THRESHOLD = 1000 * 10**18; // 1000 XMRT staked
    uint256 public constant QUORUM_PERCENTAGE = 1000; // 10% (basis points)
    uint256 public constant MAJORITY_THRESHOLD = 5000; // 50% (basis points)

    // State variables
    XMRT public xmrtToken;
    uint256 public proposalCount;
    mapping(uint256 => Proposal) public proposals;
    mapping(address => address) public delegates;
    mapping(address => uint256) public delegatedVotes;

    // Events
    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        address target,
        uint256 value,
        string description,
        uint256 startTime,
        uint256 endTime
    );
    
    event VoteCast(
        uint256 indexed proposalId,
        address indexed voter,
        bool support,
        uint256 votingPower
    );
    
    event ProposalQueued(uint256 indexed proposalId, uint256 executionTime);
    event ProposalExecuted(uint256 indexed proposalId);
    event ProposalCanceled(uint256 indexed proposalId);
    event DelegateChanged(address indexed delegator, address indexed fromDelegate, address indexed toDelegate);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address _xmrtToken) public initializer {
        __AccessControl_init();
        __ReentrancyGuard_init();
        __Pausable_init();
        __UUPSUpgradeable_init();

        xmrtToken = XMRT(_xmrtToken);
        
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(GUARDIAN_ROLE, msg.sender);
    }

    /**
     * @dev Create a new proposal
     */
    function createProposal(
        address target,
        uint256 value,
        bytes memory callData,
        string memory description
    ) external whenNotPaused returns (uint256) {
        require(getVotingPower(msg.sender) >= MIN_PROPOSAL_THRESHOLD, "Insufficient voting power");
        require(target != address(0), "Invalid target address");
        require(bytes(description).length > 0, "Description required");

        uint256 proposalId = proposalCount++;
        Proposal storage proposal = proposals[proposalId];
        
        proposal.id = proposalId;
        proposal.proposer = msg.sender;
        proposal.target = target;
        proposal.value = value;
        proposal.callData = callData;
        proposal.description = description;
        proposal.startTime = block.timestamp;
        proposal.endTime = block.timestamp + VOTING_PERIOD;
        proposal.quorumRequired = (xmrtToken.totalStaked() * QUORUM_PERCENTAGE) / 10000;
        proposal.thresholdRequired = MAJORITY_THRESHOLD;

        emit ProposalCreated(
            proposalId,
            msg.sender,
            target,
            value,
            description,
            proposal.startTime,
            proposal.endTime
        );

        return proposalId;
    }

    /**
     * @dev AI agent proposal creation with structured data
     */
    function submitAITriggeredProposal(
        address target,
        uint256 value,
        bytes memory callData,
        string memory description,
        uint256 customThreshold
    ) external onlyRole(AI_AGENT_ROLE) whenNotPaused returns (uint256) {
        require(target != address(0), "Invalid target address");
        require(bytes(description).length > 0, "Description required");
        require(customThreshold <= 10000, "Invalid threshold");

        uint256 proposalId = proposalCount++;
        Proposal storage proposal = proposals[proposalId];
        
        proposal.id = proposalId;
        proposal.proposer = msg.sender;
        proposal.target = target;
        proposal.value = value;
        proposal.callData = callData;
        proposal.description = description;
        proposal.startTime = block.timestamp;
        proposal.endTime = block.timestamp + VOTING_PERIOD;
        proposal.quorumRequired = (xmrtToken.totalStaked() * QUORUM_PERCENTAGE) / 10000;
        proposal.thresholdRequired = customThreshold > 0 ? customThreshold : MAJORITY_THRESHOLD;

        emit ProposalCreated(
            proposalId,
            msg.sender,
            target,
            value,
            description,
            proposal.startTime,
            proposal.endTime
        );

        return proposalId;
    }

    /**
     * @dev Cast a vote on a proposal
     */
    function vote(uint256 proposalId, bool support) external whenNotPaused {
        Proposal storage proposal = proposals[proposalId];
        require(getProposalState(proposalId) == ProposalState.Active, "Proposal not active");
        require(!proposal.hasVoted[msg.sender], "Already voted");

        uint256 votingPower = getVotingPower(msg.sender);
        require(votingPower > 0, "No voting power");

        proposal.hasVoted[msg.sender] = true;
        proposal.votingPower[msg.sender] = votingPower;

        if (support) {
            proposal.votesFor += votingPower;
        } else {
            proposal.votesAgainst += votingPower;
        }

        emit VoteCast(proposalId, msg.sender, support, votingPower);
    }

    /**
     * @dev Queue a proposal for execution after timelock
     */
    function queueProposal(uint256 proposalId) external whenNotPaused {
        require(getProposalState(proposalId) == ProposalState.Active, "Proposal not ready for queue");
        require(block.timestamp >= proposals[proposalId].endTime, "Voting period not ended");
        require(_hasPassedVoting(proposalId), "Proposal did not pass");

        emit ProposalQueued(proposalId, block.timestamp + TIMELOCK_PERIOD);
    }

    /**
     * @dev Execute a queued proposal
     */
    function executeProposal(uint256 proposalId) external payable nonReentrant whenNotPaused {
        Proposal storage proposal = proposals[proposalId];
        require(getProposalState(proposalId) == ProposalState.Queued, "Proposal not queued");
        require(block.timestamp >= proposal.endTime + TIMELOCK_PERIOD, "Timelock not expired");
        require(!proposal.executed, "Already executed");

        proposal.executed = true;

        (bool success, bytes memory returnData) = proposal.target.call{value: proposal.value}(proposal.callData);
        require(success, string(returnData));

        emit ProposalExecuted(proposalId);
    }

    /**
     * @dev Cancel a proposal (only by guardian or proposer)
     */
    function cancelProposal(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        require(
            msg.sender == proposal.proposer || hasRole(GUARDIAN_ROLE, msg.sender),
            "Unauthorized to cancel"
        );
        require(!proposal.executed, "Cannot cancel executed proposal");

        proposal.canceled = true;
        emit ProposalCanceled(proposalId);
    }

    /**
     * @dev Delegate voting power to another address
     */
    function delegate(address delegatee) external {
        address currentDelegate = delegates[msg.sender];
        delegates[msg.sender] = delegatee;

        uint256 votingPower = _getDirectVotingPower(msg.sender);
        
        if (currentDelegate != address(0)) {
            delegatedVotes[currentDelegate] -= votingPower;
        }
        
        if (delegatee != address(0)) {
            delegatedVotes[delegatee] += votingPower;
        }

        emit DelegateChanged(msg.sender, currentDelegate, delegatee);
    }

    /**
     * @dev Get the current state of a proposal
     */
    function getProposalState(uint256 proposalId) public view returns (ProposalState) {
        Proposal storage proposal = proposals[proposalId];
        
        if (proposal.canceled) {
            return ProposalState.Canceled;
        }
        
        if (proposal.executed) {
            return ProposalState.Executed;
        }
        
        if (block.timestamp < proposal.startTime) {
            return ProposalState.Pending;
        }
        
        if (block.timestamp <= proposal.endTime) {
            return ProposalState.Active;
        }
        
        if (_hasPassedVoting(proposalId)) {
            if (block.timestamp >= proposal.endTime + TIMELOCK_PERIOD) {
                return ProposalState.Queued;
            }
            return ProposalState.Queued;
        }
        
        return ProposalState.Defeated;
    }

    /**
     * @dev Get voting power for an address (including delegated votes)
     */
    function getVotingPower(address account) public view returns (uint256) {
        return _getDirectVotingPower(account) + delegatedVotes[account];
    }

    /**
     * @dev Get direct voting power (staked tokens only)
     */
    function _getDirectVotingPower(address account) internal view returns (uint256) {
        (uint128 amount,) = xmrtToken.userStakes(account);
        return uint256(amount);
    }

    /**
     * @dev Check if a proposal has passed voting requirements
     */
    function _hasPassedVoting(uint256 proposalId) internal view returns (bool) {
        Proposal storage proposal = proposals[proposalId];
        uint256 totalVotes = proposal.votesFor + proposal.votesAgainst;
        
        // Check quorum
        if (totalVotes < proposal.quorumRequired) {
            return false;
        }
        
        // Check threshold
        uint256 forPercentage = (proposal.votesFor * 10000) / totalVotes;
        return forPercentage >= proposal.thresholdRequired;
    }

    /**
     * @dev Emergency pause function
     */
    function pause() external onlyRole(GUARDIAN_ROLE) {
        _pause();
    }

    /**
     * @dev Unpause function
     */
    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }

    /**
     * @dev Authorize contract upgrades
     */
    function _authorizeUpgrade(address newImplementation) internal override onlyRole(ADMIN_ROLE) {}

    /**
     * @dev Get proposal details
     */
    function getProposal(uint256 proposalId) external view returns (
        uint256 id,
        address proposer,
        address target,
        uint256 value,
        bytes memory callData,
        string memory description,
        uint256 startTime,
        uint256 endTime,
        uint256 votesFor,
        uint256 votesAgainst,
        ProposalState state
    ) {
        Proposal storage proposal = proposals[proposalId];
        return (
            proposal.id,
            proposal.proposer,
            proposal.target,
            proposal.value,
            proposal.callData,
            proposal.description,
            proposal.startTime,
            proposal.endTime,
            proposal.votesFor,
            proposal.votesAgainst,
            getProposalState(proposalId)
        );
    }

    /**
     * @dev Check if an address has voted on a proposal
     */
    function hasVoted(uint256 proposalId, address voter) external view returns (bool) {
        return proposals[proposalId].hasVoted[voter];
    }

    /**
     * @dev Get voting power used by an address on a specific proposal
     */
    function getVotingPowerUsed(uint256 proposalId, address voter) external view returns (uint256) {
        return proposals[proposalId].votingPower[voter];
    }
}

