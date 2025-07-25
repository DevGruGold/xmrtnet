import streamlit as st
import requests

st.set_page_config(page_title="XMRT Onboarding", layout="centered")
st.title("XMRT DAO Onboarding")
st.subheader("The Token That Mines When the Internet Dies")

st.markdown("Welcome! Let Eliza guide you through setting up your XMRT miner rig.")

alias = st.text_input("What's your alias, miner?")

if alias:
    st.markdown("### Eliza says:")
    try:
        response = requests.post("https://xmrteliza.vercel.app/api/eliza", json={"prompt": f"My name is {alias}. Help me get started."})
        if response.status_code == 200:
            st.success(response.json()["output"])
        else:
            st.error("Eliza couldn't respond. Server error.")
    except Exception as e:
        st.error(f"Failed to reach Eliza: {e}")

st.markdown("---")
st.header("Step 1: Get Mining")
st.markdown("[Visit MobileMonero.com](https://mobilemonero.com) to set up Termux miner and generate your rig ID.")

st.markdown("---")
st.header("Step 2: Tokenize Your IP")
st.caption("Coming soon: Deploy NFT + ERC20 from your uploaded idea.")

st.markdown("---")
st.header("Step 3: Join the DAO")
if st.button("Generate Proposal"):
    try:
        prop = requests.post("https://xmrteliza.vercel.app/api/eliza", json={"prompt": "Help me write a proposal to reward early miners."})
        st.code(prop.json()["output"])
    except:
        st.error("Eliza failed to generate the proposal.")
        
st.markdown("---")
st.markdown("### Ecosystem Links")
st.markdown("""
- [MobileMonero.com](https://mobilemonero.com)
- [XMRT MESHNET Hub](https://xmrtdao.streamlit.app)
- [XMRT-Ecosystem GitHub](https://github.com/DevGruGold/XMRT-Ecosystem)
""")