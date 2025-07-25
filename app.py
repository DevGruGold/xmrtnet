import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="XMRT Onboarding", layout="centered")
st.title("🚀 XMRT DAO Onboarding")
st.subheader("The Token That Mines When the Internet Dies")

# Configure Gemini Eliza agent
genai.configure(api_key="AIzaSyAS9tG4JzVnCfaoiYJzSOIhacB0lB3dVsg")
eliza = genai.GenerativeModel("models/gemini-pro").start_chat()

# Collect alias
alias = st.text_input("What’s your alias, miner?")

# Eliza interaction
if alias:
    st.markdown("### 🤖 Eliza says:")
    welcome = eliza.send_message(f"My name is {alias}. Help me get started with XMRT.")
    st.info(welcome.text)

st.markdown("---")
st.markdown("## ⛏️ Step 1: Get Started Mining")
st.markdown("""
Use [MobileMonero.com](https://mobilemonero.com) to install Termux, run `signup.py`, and generate your unique rig ID.

Check your stats at the [📊 MESHNET Leaderboard](https://xmrtdao.streamlit.app)
""")

st.markdown("---")
st.markdown("## 🧠 Step 2: Tokenize Your IP")
if st.button("Deploy NFT + ERC20 Token"):
    st.warning("This feature will launch from a backend script or connected wallet. (Coming Soon!)")
    tx_response = eliza.send_message("What does deploying my IP token actually do?")
    st.success(tx_response.text)

st.markdown("---")
st.markdown("## 🗳️ Step 3: Propose to the DAO")
if st.button("Help me write a proposal"):
    proposal = eliza.send_message("Help me write a DAO proposal to reward early miners.")
    st.markdown("### ✍️ Proposal Draft")
    st.code(proposal.text)

st.markdown("---")
st.markdown("## 🌐 XMRT Tools")
st.markdown("""
- [📱 MobileMonero.com](https://mobilemonero.com)
- [📊 XMRT DAO Hub](https://xmrtdao.streamlit.app)
- [🤖 Eliza Web Agent](https://xmrteliza.vercel.app)
- [📁 GitHub Starter Kit](https://github.com/DevGruGold/xmrtnet/tree/main)
""")