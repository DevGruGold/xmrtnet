const { expect } = require("chai");
const { ethers, upgrades } = require("hardhat");

describe("DAO Integration Tests", function () {
    let xmrt, governance, daoGovernance, daoTreasury, vault, aiInterface;
    let owner, user1, user2, aiAgent, treasury;
    let proposalId;

    beforeEach(async function () {
        [owner, user1, user2, aiAgent, treasury] = await ethers.getSigners();

        // Deploy XMRT token
        const XMRT = await ethers.getContractFactory("XMRT");
        xmrt = await upgrades.deployProxy(XMRT, [], { initializer: "initialize" });
        await xmrt.deployed();

        // Deploy DAO Governance
        const DAOGovernance = await ethers.getContractFactory("DAO_Governance");
        daoGovernance = await upgrades.deployProxy(DAOGovernance, [xmrt.address], {
            initializer: "initialize"
        });
        await daoGovernance.deployed();

        // Deploy DAO Treasury
        const DAOTreasury = await ethers.getContractFactory("DAO_Treasury");
        daoTreasury = await upgrades.deployProxy(DAOTreasury, [], {
            initializer: "initialize"
        });
        await daoTreasury.deployed();

        // Deploy main Governance contract
        const Governance = await ethers.getContractFactory("Governance");
        governance = await upgrades.deployProxy(Governance, [daoGovernance.address, daoTreasury.address], {
            initializer: "initialize"
        });
        await governance.deployed();

        // Deploy Vault
        const Vault = await ethers.getContractFactory("Vault");
        vault = await upgrades.deployProxy(Vault, [daoTreasury.address], {
            initializer: "initialize"
        });
        await vault.deployed();

        // Deploy AI Agent Interface
        const AIInterface = await ethers.getContractFactory("AI_Agent_Interface");
        aiInterface = await upgrades.deployProxy(AIInterface, [
            daoGovernance.address,
            daoTreasury.address,
            xmrt.address
        ], {
            initializer: "initialize"
        });
        await aiInterface.deployed();

        // Setup roles
        const AI_AGENT_ROLE = await daoGovernance.AI_AGENT_ROLE();
        const GOVERNANCE_ROLE = await daoTreasury.GOVERNANCE_ROLE();

        await daoGovernance.grantRole(AI_AGENT_ROLE, aiAgent.address);
        await daoTreasury.grantRole(GOVERNANCE_ROLE, daoGovernance.address);
        await aiInterface.grantRole(AI_AGENT_ROLE, aiAgent.address);

        // Setup initial token distribution and staking
        await xmrt.transfer(user1.address, ethers.utils.parseEther("10000"));
        await xmrt.transfer(user2.address, ethers.utils.parseEther("10000"));
        
        await xmrt.connect(user1).stake(ethers.utils.parseEther("5000"));
        await xmrt.connect(user2).stake(ethers.utils.parseEther("3000"));

        // Add ETH to treasury
        await daoTreasury.addAsset(ethers.constants.AddressZero, "Ethereum", "ETH");
        await owner.sendTransaction({
            to: daoTreasury.address,
            value: ethers.utils.parseEther("10")
        });
    });

    describe("XMRT Token Integration", function () {
        it("Should allow staking and track voting power", async function () {
            const stakingAmount = ethers.utils.parseEther("1000");
            await xmrt.connect(user1).stake(stakingAmount);

            const votingPower = await daoGovernance.getVotingPower(user1.address);
            expect(votingPower).to.equal(ethers.utils.parseEther("6000")); // 5000 + 1000
        });

        it("Should apply penalty for early unstaking", async function () {
            const initialBalance = await xmrt.balanceOf(user1.address);
            const stakingAmount = ethers.utils.parseEther("1000");
            
            await xmrt.connect(user1).stake(stakingAmount);
            await xmrt.connect(user1).unstake(stakingAmount);

            const finalBalance = await xmrt.balanceOf(user1.address);
            const penalty = stakingAmount.div(10); // 10% penalty
            expect(finalBalance).to.equal(initialBalance.sub(penalty));
        });
    });

    describe("DAO Governance Integration", function () {
        it("Should create and execute a proposal", async function () {
            const target = daoTreasury.address;
            const value = 0;
            const callData = daoTreasury.interface.encodeFunctionData("createAllocation", [
                ethers.constants.AddressZero,
                ethers.utils.parseEther("1"),
                0, // General allocation
                user2.address,
                "Test allocation"
            ]);
            const description = "Allocate 1 ETH to user2";

            // Create proposal
            const tx = await daoGovernance.connect(user1).createProposal(
                target,
                value,
                callData,
                description
            );
            const receipt = await tx.wait();
            proposalId = receipt.events.find(e => e.event === "ProposalCreated").args.proposalId;

            // Vote on proposal
            await daoGovernance.connect(user1).vote(proposalId, true);
            await daoGovernance.connect(user2).vote(proposalId, true);

            // Fast forward time to end voting period
            await ethers.provider.send("evm_increaseTime", [7 * 24 * 60 * 60]); // 7 days
            await ethers.provider.send("evm_mine");

            // Queue proposal
            await daoGovernance.queueProposal(proposalId);

            // Fast forward timelock period
            await ethers.provider.send("evm_increaseTime", [2 * 24 * 60 * 60]); // 2 days
            await ethers.provider.send("evm_mine");

            // Execute proposal
            await daoGovernance.executeProposal(proposalId);

            const state = await daoGovernance.getProposalState(proposalId);
            expect(state).to.equal(3); // Executed
        });

        it("Should allow AI agent to create proposals", async function () {
            const target = daoTreasury.address;
            const value = 0;
            const callData = "0x";
            const description = "AI-generated proposal";
            const customThreshold = 4000; // 40%

            const tx = await daoGovernance.connect(aiAgent).submitAITriggeredProposal(
                target,
                value,
                callData,
                description,
                customThreshold
            );

            const receipt = await tx.wait();
            const proposalId = receipt.events.find(e => e.event === "ProposalCreated").args.proposalId;

            const proposal = await daoGovernance.getProposal(proposalId);
            expect(proposal.proposer).to.equal(aiAgent.address);
            expect(proposal.description).to.equal(description);
        });
    });

    describe("Treasury Integration", function () {
        it("Should manage multi-asset treasury", async function () {
            // Add XMRT as supported asset
            await daoTreasury.addAsset(xmrt.address, "XMRT Token", "XMRT");

            // Send XMRT to treasury
            await xmrt.transfer(daoTreasury.address, ethers.utils.parseEther("1000"));
            await daoTreasury.receiveTokens(xmrt.address, ethers.utils.parseEther("1000"));

            const balance = await daoTreasury.getAssetBalance(xmrt.address);
            expect(balance).to.equal(ethers.utils.parseEther("1000"));
        });

        it("Should enforce AI spending limits", async function () {
            // Set spending limit for AI agent
            await daoTreasury.setAISpendingLimit(
                ethers.constants.AddressZero,
                ethers.utils.parseEther("1"), // 1 ETH daily
                ethers.utils.parseEther("5")  // 5 ETH total
            );

            // AI agent should be able to spend within limits
            await daoTreasury.connect(aiAgent).executeAISpending(
                ethers.constants.AddressZero,
                ethers.utils.parseEther("0.5"),
                user1.address,
                "Test spending"
            );

            // Should fail if exceeding daily limit
            await expect(
                daoTreasury.connect(aiAgent).executeAISpending(
                    ethers.constants.AddressZero,
                    ethers.utils.parseEther("0.6"),
                    user1.address,
                    "Exceeding limit"
                )
            ).to.be.revertedWith("Daily spending limit exceeded");
        });
    });

    describe("AI Agent Interface Integration", function () {
        it("Should allow AI agents to create proposals through interface", async function () {
            const target = daoTreasury.address;
            const value = 0;
            const callData = "0x";
            const description = "AI interface proposal";
            const customThreshold = 5000;

            const proposalId = await aiInterface.connect(aiAgent).createAIProposal(
                target,
                value,
                callData,
                description,
                customThreshold
            );

            const stats = await aiInterface.getAgentStats(aiAgent.address);
            expect(stats.totalActions).to.equal(1);
        });

        it("Should track AI agent actions", async function () {
            // Execute multiple actions
            await aiInterface.connect(aiAgent).createAIProposal(
                daoTreasury.address,
                0,
                "0x",
                "Proposal 1",
                5000
            );

            await aiInterface.connect(aiAgent).executeAISpending(
                ethers.constants.AddressZero,
                ethers.utils.parseEther("0.1"),
                user1.address,
                "Test spending"
            );

            const stats = await aiInterface.getAgentStats(aiAgent.address);
            expect(stats.totalActions).to.equal(2);

            const recentActions = await aiInterface.getRecentActionsByAgent(aiAgent.address, 5);
            expect(recentActions.length).to.equal(2);
        });

        it("Should enforce action rate limits", async function () {
            // Execute action
            await aiInterface.connect(aiAgent).createAIProposal(
                daoTreasury.address,
                0,
                "0x",
                "Proposal 1",
                5000
            );

            // Should fail if trying to act too quickly
            await expect(
                aiInterface.connect(aiAgent).createAIProposal(
                    daoTreasury.address,
                    0,
                    "0x",
                    "Proposal 2",
                    5000
                )
            ).to.be.revertedWith("Agent action limits exceeded");
        });
    });

    describe("Cross-Contract Integration", function () {
        it("Should maintain consistent state across contracts", async function () {
            // Check that voting power is consistent
            const votingPowerGovernance = await daoGovernance.getVotingPower(user1.address);
            const userStake = await xmrt.userStakes(user1.address);
            
            expect(votingPowerGovernance).to.equal(userStake.amount);
        });

        it("Should handle contract upgrades", async function () {
            // This would test the upgrade mechanism
            // For now, just verify the upgrade authorization works
            const hasAdminRole = await governance.hasRole(
                await governance.ADMIN_ROLE(),
                owner.address
            );
            expect(hasAdminRole).to.be.true;
        });
    });

    describe("Emergency Functions", function () {
        it("Should allow emergency withdrawal from treasury", async function () {
            const GUARDIAN_ROLE = await daoTreasury.GUARDIAN_ROLE();
            await daoTreasury.grantRole(GUARDIAN_ROLE, owner.address);

            const initialBalance = await ethers.provider.getBalance(user2.address);
            
            await daoTreasury.emergencyWithdraw(
                ethers.constants.AddressZero,
                ethers.utils.parseEther("1"),
                user2.address
            );

            const finalBalance = await ethers.provider.getBalance(user2.address);
            expect(finalBalance.sub(initialBalance)).to.equal(ethers.utils.parseEther("1"));
        });

        it("Should allow pausing contracts", async function () {
            await governance.pause();
            
            await expect(
                daoGovernance.connect(user1).createProposal(
                    daoTreasury.address,
                    0,
                    "0x",
                    "Should fail"
                )
            ).to.be.revertedWith("Pausable: paused");
        });
    });
});

