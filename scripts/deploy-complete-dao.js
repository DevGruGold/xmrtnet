const { ethers, upgrades } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("🚀 Starting XMRT DAO Complete Deployment...");

  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  const deploymentResults = {};
  const network = await ethers.provider.getNetwork();
  console.log("Network:", network.name, "Chain ID:", network.chainId);

  try {
    // 1. Deploy XMRT Token (Upgradeable)
    console.log("\n📄 Deploying XMRT Token...");
    const XMRT = await ethers.getContractFactory("XMRT");
    const xmrt = await upgrades.deployProxy(XMRT, [], {
      initializer: "initialize",
      kind: "uups"
    });
    await xmrt.deployed();
    console.log("✅ XMRT Token deployed to:", xmrt.address);
    deploymentResults.xmrt = xmrt.address;

    // 2. Deploy DAO Treasury (Upgradeable)
    console.log("\n💰 Deploying DAO Treasury...");
    const DAOTreasury = await ethers.getContractFactory("DAO_Treasury");
    const daoTreasury = await upgrades.deployProxy(DAOTreasury, [xmrt.address], {
      initializer: "initialize",
      kind: "uups"
    });
    await daoTreasury.deployed();
    console.log("✅ DAO Treasury deployed to:", daoTreasury.address);
    deploymentResults.daoTreasury = daoTreasury.address;

    // 3. Deploy DAO Governance (Upgradeable)
    console.log("\n🏛️ Deploying DAO Governance...");
    const DAOGovernance = await ethers.getContractFactory("DAO_Governance");
    const daoGovernance = await upgrades.deployProxy(DAOGovernance, [
      xmrt.address,
      daoTreasury.address,
      7200, // voting delay (2 hours in blocks)
      50400, // voting period (14 days in blocks)
      ethers.utils.parseEther("1000") // proposal threshold
    ], {
      initializer: "initialize",
      kind: "uups"
    });
    await daoGovernance.deployed();
    console.log("✅ DAO Governance deployed to:", daoGovernance.address);
    deploymentResults.daoGovernance = daoGovernance.address;

    // 4. Deploy AI Agent Interface (Upgradeable)
    console.log("\n🤖 Deploying AI Agent Interface...");
    const AIAgentInterface = await ethers.getContractFactory("AI_Agent_Interface");
    const aiAgentInterface = await upgrades.deployProxy(AIAgentInterface, [
      daoGovernance.address,
      daoTreasury.address,
      xmrt.address
    ], {
      initializer: "initialize",
      kind: "uups"
    });
    await aiAgentInterface.deployed();
    console.log("✅ AI Agent Interface deployed to:", aiAgentInterface.address);
    deploymentResults.aiAgentInterface = aiAgentInterface.address;

    // 5. Deploy Cross-Chain Contract (if not on mainnet)
    if (network.chainId !== 1) {
      console.log("\n🌉 Deploying Cross-Chain Contract...");
      const XMRTCrossChain = await ethers.getContractFactory("XMRTCrossChain");

      // Mock addresses for testnet - replace with actual addresses in production
      const wormholeRelayer = "0x0000000000000000000000000000000000000001";
      const layerZeroEndpoint = "0x0000000000000000000000000000000000000002";

      const xmrtCrossChain = await upgrades.deployProxy(XMRTCrossChain, [
        wormholeRelayer,
        layerZeroEndpoint
      ], {
        initializer: "initialize",
        kind: "uups"
      });
      await xmrtCrossChain.deployed();
      console.log("✅ Cross-Chain Contract deployed to:", xmrtCrossChain.address);
      deploymentResults.xmrtCrossChain = xmrtCrossChain.address;
    }

    // 6. Deploy LayerZero OFT (if supported)
    console.log("\n🔗 Deploying LayerZero OFT...");
    const XMRTLayerZeroOFT = await ethers.getContractFactory("XMRTLayerZeroOFT");

    // Mock LayerZero endpoint for testnet
    const layerZeroEndpoint = "0x0000000000000000000000000000000000000002";

    const xmrtOFT = await XMRTLayerZeroOFT.deploy(
      "XMRT OFT",
      "XMRT",
      layerZeroEndpoint,
      deployer.address
    );
    await xmrtOFT.deployed();
    console.log("✅ LayerZero OFT deployed to:", xmrtOFT.address);
    deploymentResults.xmrtOFT = xmrtOFT.address;

    // 7. Configure Contract Integrations
    console.log("\n⚙️ Configuring contract integrations...");

    // Set treasury in governance
    await daoGovernance.setTreasury(daoTreasury.address);
    console.log("✅ Treasury set in governance");

    // Set governance in treasury
    await daoTreasury.setGovernance(daoGovernance.address);
    console.log("✅ Governance set in treasury");

    // Grant AI agent roles
    const AI_AGENT_ROLE = await daoGovernance.AI_AGENT_ROLE();
    await daoGovernance.grantRole(AI_AGENT_ROLE, aiAgentInterface.address);
    await daoTreasury.grantRole(AI_AGENT_ROLE, aiAgentInterface.address);
    console.log("✅ AI agent roles granted");

    // 8. Initialize AI Agents with test wallets
    console.log("\n🤖 Initializing AI Agents...");

    // Generate test AI agent addresses (in production, use secure key management)
    const governanceAgent = ethers.Wallet.createRandom();
    const treasuryAgent = ethers.Wallet.createRandom();
    const communityAgent = ethers.Wallet.createRandom();

    await aiAgentInterface.registerAgent(
      governanceAgent.address,
      "Governance Agent",
      "Handles proposal processing and voting operations"
    );

    await aiAgentInterface.registerAgent(
      treasuryAgent.address,
      "Treasury Agent", 
      "Manages treasury operations and optimizations"
    );

    await aiAgentInterface.registerAgent(
      communityAgent.address,
      "Community Agent",
      "Provides community support and engagement"
    );

    console.log("✅ AI Agents registered");

    // Store AI agent keys for backend services
    deploymentResults.aiAgents = {
      governance: {
        address: governanceAgent.address,
        privateKey: governanceAgent.privateKey
      },
      treasury: {
        address: treasuryAgent.address,
        privateKey: treasuryAgent.privateKey
      },
      community: {
        address: communityAgent.address,
        privateKey: communityAgent.privateKey
      }
    };

    // 9. Fund AI Agents with initial ETH for gas
    console.log("\n⛽ Funding AI Agents...");
    const fundAmount = ethers.utils.parseEther("0.1");

    await deployer.sendTransaction({
      to: governanceAgent.address,
      value: fundAmount
    });

    await deployer.sendTransaction({
      to: treasuryAgent.address,
      value: fundAmount
    });

    await deployer.sendTransaction({
      to: communityAgent.address,
      value: fundAmount
    });

    console.log("✅ AI Agents funded with ETH for gas");

    // 10. Create initial governance proposal for testing
    console.log("\n📝 Creating initial test proposal...");

    const proposalDescription = "Initial DAO Setup - Enable AI Agent Automation";
    const targets = [aiAgentInterface.address];
    const values = [0];
    const calldatas = [aiAgentInterface.interface.encodeFunctionData("enableAutomation", [true])];

    await daoGovernance.propose(targets, values, calldatas, proposalDescription);
    console.log("✅ Initial proposal created");

    // 11. Save deployment results
    const deploymentData = {
      network: network.name,
      chainId: network.chainId,
      deployer: deployer.address,
      timestamp: new Date().toISOString(),
      contracts: deploymentResults,
      verification: {
        xmrt: `npx hardhat verify --network ${network.name} ${deploymentResults.xmrt}`,
        daoTreasury: `npx hardhat verify --network ${network.name} ${deploymentResults.daoTreasury}`,
        daoGovernance: `npx hardhat verify --network ${network.name} ${deploymentResults.daoGovernance}`,
        aiAgentInterface: `npx hardhat verify --network ${network.name} ${deploymentResults.aiAgentInterface}`
      }
    };

    // Save to deployments directory
    const deploymentsDir = path.join(__dirname, "..", "deployments");
    if (!fs.existsSync(deploymentsDir)) {
      fs.mkdirSync(deploymentsDir, { recursive: true });
    }

    const deploymentFile = path.join(deploymentsDir, `${network.name}-${network.chainId}.json`);
    fs.writeFileSync(deploymentFile, JSON.stringify(deploymentData, null, 2));

    console.log(`\n💾 Deployment data saved to: ${deploymentFile}`);

    // 12. Create environment file for backend services
    const envContent = `# XMRT DAO Deployment Configuration - ${network.name}
NETWORK_NAME=${network.name}
CHAIN_ID=${network.chainId}
DEPLOYER_ADDRESS=${deployer.address}

# Contract Addresses
XMRT_CONTRACT_ADDRESS=${deploymentResults.xmrt}
DAO_GOVERNANCE_ADDRESS=${deploymentResults.daoGovernance}
DAO_TREASURY_ADDRESS=${deploymentResults.daoTreasury}
AI_AGENT_INTERFACE_ADDRESS=${deploymentResults.aiAgentInterface}
${deploymentResults.xmrtCrossChain ? `XMRT_CROSS_CHAIN_ADDRESS=${deploymentResults.xmrtCrossChain}` : ''}
${deploymentResults.xmrtOFT ? `XMRT_OFT_ADDRESS=${deploymentResults.xmrtOFT}` : ''}

# AI Agent Configuration (TEST KEYS - REPLACE IN PRODUCTION)
GOVERNANCE_AGENT_ADDRESS=${deploymentResults.aiAgents.governance.address}
GOVERNANCE_AGENT_PRIVATE_KEY=${deploymentResults.aiAgents.governance.privateKey}
TREASURY_AGENT_ADDRESS=${deploymentResults.aiAgents.treasury.address}
TREASURY_AGENT_PRIVATE_KEY=${deploymentResults.aiAgents.treasury.privateKey}
COMMUNITY_AGENT_ADDRESS=${deploymentResults.aiAgents.community.address}
COMMUNITY_AGENT_PRIVATE_KEY=${deploymentResults.aiAgents.community.privateKey}

# RPC Configuration
${network.name.toUpperCase()}_RPC_URL=${network.name === 'sepolia' ? 'https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID' : 'https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'}
`;

    const envFile = path.join(__dirname, "..", "backend", "xmrt-dao-backend", `.env.${network.name}`);
    fs.writeFileSync(envFile, envContent);
    console.log(`✅ Environment file created: ${envFile}`);

    console.log("\n🎉 XMRT DAO Deployment Complete!");
    console.log("\n📋 Deployment Summary:");
    console.log("========================");
    Object.entries(deploymentResults).forEach(([name, address]) => {
      if (typeof address === 'string') {
        console.log(`${name}: ${address}`);
      }
    });

    console.log("\n🔧 Next Steps:");
    console.log("1. Update backend service environment variables");
    console.log("2. Start backend services with new contract addresses");
    console.log("3. Update frontend configuration");
    console.log("4. Verify contracts on block explorer");
    console.log("5. Test AI agent automation");

    return deploymentResults;

  } catch (error) {
    console.error("❌ Deployment failed:", error);
    throw error;
  }
}

// Execute deployment
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
