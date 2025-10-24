# 🚀 XMRT DAO Quick Start Guide

## Welcome to the Enhanced Autonomous System!

This guide will help you get started with the newly restored and enhanced XMRT DAO autonomous system.

## 🎯 What's New?

### ✅ Fully Restored Automation
The autonomous analytics cycle system is back online and running automatically every 6 hours!

### ✅ Enhanced Frontend
A completely redesigned, dynamic dashboard with real-time monitoring and multi-tab navigation.

### ✅ GitHub Actions Integration
Automatic cycle execution and report generation via GitHub Actions workflows.

## 🌐 Quick Links

- **Live Dashboard:** https://xmrtnet-test.streamlit.app/
- **Repository:** https://github.com/DevGruGold/xmrtnet
- **Latest Cycle:** Check `ANALYTICS_CYCLE_*.md` files in root

## 📊 Using the Dashboard

### 1. Access the Dashboard
Visit: https://xmrtnet-test.streamlit.app/

### 2. Explore the Tabs

#### 📊 Dashboard Tab
- View real-time system metrics
- See latest analytics cycle information
- Read key insights and recommendations
- Monitor system health

#### 💬 Chat Tab
- Chat with AI agents (Eliza, DAO, Mining, Treasury, Governance)
- Ask questions about the DAO
- Get real-time responses
- Use quick action buttons for common queries

#### 📈 Analytics Tab
- View detailed metrics across all categories
- Track historical performance
- Download cycle reports
- Monitor trends

#### ⚙️ System Tab
- View system configuration
- Check active autonomous operations
- Read system logs
- Trigger manual actions (demo mode)

## 🔄 Analytics Cycles

### What Are They?
Automated processes that run every 6 hours to:
- Collect system metrics
- Analyze performance
- Generate insights
- Provide recommendations

### How to View Cycles
1. **On Dashboard:** Latest cycle info shown on main dashboard
2. **In Repository:** Look for `ANALYTICS_CYCLE_750.md` (or higher)
3. **GitHub Actions:** View execution history in Actions tab

### Cycle Contents
Each cycle report includes:
- 📊 System metrics (Repository, DAO, Mining, Treasury)
- 💡 Key insights (8+ actionable items)
- 🎯 Strategic recommendations (6+ items)
- 🤖 Autonomous operations status
- 📈 Cycle performance data

## 🤖 AI Agents

### Available Agents

1. **Eliza (Core)** 🧠
   - General DAO questions
   - Educational content
   - System overview

2. **DAO Agent** 🏛️
   - Governance information
   - Proposal details
   - Voting processes

3. **Mining Agent** ⛏️
   - Mining operations
   - Network status
   - Mobile mining

4. **Treasury Agent** 💰
   - Financial data
   - Treasury management
   - Revenue streams

5. **Governance Agent** 🗳️
   - Voting processes
   - Proposal creation
   - Participation metrics

### How to Chat
1. Go to 💬 Chat tab
2. Select an agent from dropdown
3. Type your question
4. Click "Send 🚀"
5. Get instant responses

### Quick Actions
Use the quick action buttons for:
- 🗳️ Governance Demo
- 💰 Treasury Analysis
- ⛏️ Mining Insights
- 📚 DAO Education
- 🔗 Cross-Chain Features
- 🛡️ Security Info
- 📈 Tokenomics
- 🌐 Roadmap

## 🛠️ Technical Setup (For Developers)

### Local Development

```bash
# Clone the repository
git clone https://github.com/DevGruGold/xmrtnet.git
cd xmrtnet

# Install dependencies
pip install streamlit requests pathlib

# Run the dashboard
streamlit run src/app.py

# Run analytics cycle
cd src
python autonomous_analytics_cycle.py
```

### Manual Cycle Execution

```bash
cd src
python autonomous_analytics_cycle.py
```

This will:
- Generate a new cycle report
- Save it as `ANALYTICS_CYCLE_{NUMBER}.md`
- Update cycle state
- Display results in terminal

### GitHub Actions

The automation runs via `.github/workflows/autonomous-cycles.yml`

**Schedule:** Every 6 hours  
**Manual Trigger:** Available in Actions tab

## 📊 Understanding Metrics

### Repository Health
- **Code Quality:** Overall code quality score (target: 80%+)
- **Documentation:** Documentation coverage (target: 80%+)
- **Test Coverage:** Automated test coverage (target: 70%+)
- **Security:** Security audit score (target: 90%+)
- **Performance:** System performance index (target: 85%+)

### DAO Operations
- **Active Proposals:** Current governance proposals
- **Treasury Health:** Overall treasury status (target: 80%+)
- **Community Engagement:** Community activity level (target: 70%+)
- **Governance Participation:** Voting participation (target: 60%+)
- **Voting Activity:** Active voting rate (target: 65%+)

### Mining Network
- **Active Miners:** Number of active mining nodes
- **Network Hashrate:** Total network mining power (TH/s)
- **Uptime:** Network availability (target: 99%+)
- **Mobile Nodes:** Mobile mining devices
- **Resilience Score:** Network resilience rating (target: 95%+)

### Treasury & Financials
- **Total Value:** Total treasury value in USD
- **Monthly Revenue:** Income per month
- **Burn Rate:** Monthly expenses
- **Runway:** Months of operation at current rate
- **Yield APR:** Annual percentage rate for treasury yields

## 🎯 Common Use Cases

### 1. Check System Health
1. Visit dashboard
2. Look at main metrics on Dashboard tab
3. Check agent status in sidebar

### 2. View Latest Analytics
1. Go to Dashboard tab
2. Scroll to "Latest Analytics Cycle" section
3. Review insights and recommendations

### 3. Ask Questions
1. Go to Chat tab
2. Select appropriate agent
3. Ask your question
4. Get detailed response

### 4. Download Reports
1. Go to Analytics tab
2. Scroll to bottom
3. Click "📥 Download Latest Cycle Report"

### 5. Monitor Trends
1. Check Analytics tab
2. View metrics across categories
3. Compare with previous cycles

## 🔔 Notifications

### GitHub Actions
- Check Actions tab for cycle execution history
- View summaries for each run
- Get notified of any failures

### Dashboard
- Real-time agent status in sidebar
- Live metrics on dashboard
- System logs in System tab

## 🆘 Troubleshooting

### Dashboard Not Loading
- Check https://xmrtnet-test.streamlit.app/ is accessible
- Refresh the page
- Clear browser cache

### Agents Offline
- Check sidebar for agent status
- Backend may be starting up (wait 2-3 minutes)
- Try again later

### Cycle Not Running
- Check GitHub Actions tab
- Verify workflow is enabled
- Run manual trigger if needed

### Chat Not Responding
- Verify agent is online (sidebar)
- Check internet connection
- Try different agent

## 📚 Additional Resources

- **Full Documentation:** `AUTONOMOUS_SYSTEM_README.md`
- **GitHub Issues:** Report problems or suggest features
- **Discussions:** Join community conversations

## 🎉 Success Indicators

You'll know the system is working when:
- ✅ Dashboard loads and shows data
- ✅ Latest cycle number is visible
- ✅ Agents show as online
- ✅ Chat responds to questions
- ✅ New cycle files appear every 6 hours
- ✅ GitHub Actions run successfully

## 🚀 Next Steps

1. ✅ Explore the dashboard
2. ✅ Chat with different agents
3. ✅ Review latest cycle report
4. ✅ Check back in 6 hours for new cycle
5. ✅ Join discussions on GitHub

---

**Need Help?**
- Open an issue on GitHub
- Start a discussion
- Check the documentation

**Status:** 🟢 All Systems Operational  
**Last Updated:** 2025-10-24  
**Version:** 3.0.0
