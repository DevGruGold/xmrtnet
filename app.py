
import streamlit as st
import requests

st.set_page_config(page_title="XMRT Onboarding with Eliza", layout="centered")
st.title("🌐 XMRT DAO Onboarding")
st.subheader("The Token That Mines When the Internet Dies")

st.markdown("""
Welcome to XMRT. This onboarding assistant is powered by **Eliza**, the autonomous AI agent guiding new users through setup, mining, and DAO participation.
""")

prompt = st.text_input("💬 Ask Eliza a question", placeholder="e.g., How do I start mining on my phone?")

if prompt:
    with st.spinner("Eliza is thinking..."):
        try:
            response = requests.post("https://xmrteliza.vercel.app/eliza", json={"prompt": prompt})
            eliza_reply = response.json().get("response", "No response received.")
            st.success("Eliza says:")
            st.markdown(f"> {eliza_reply}")
        except Exception as e:
            st.error(f"Failed to reach Eliza: {e}")

st.divider()
st.header("⛏️ Get Started Mining")
st.markdown("[Visit MobileMonero.com](https://mobilemonero.com) to install Termux, run signup.py, and generate your rig ID.")

st.divider()
st.header("🧠 Tokenize Your IP")
st.caption("Coming soon: Deploy your ideas as NFT + ERC20 tokens.")

st.divider()
st.header("🗳️ Join the DAO")
if st.button("Generate DAO Proposal"):
    try:
        proposal = requests.post("https://xmrteliza.vercel.app/eliza", json={"prompt": "Help me write a DAO proposal to reward early miners."})
        st.code(proposal.json()["response"])
    except:
        st.error("Proposal generation failed. Try again later.")

st.divider()
st.markdown("## 🌐 XMRT Ecosystem")
st.markdown("""
- [MobileMonero.com](https://mobilemonero.com)
- [XMRT MESHNET Hub](https://xmrtdao.streamlit.app)
- [XMRT-Ecosystem GitHub](https://github.com/DevGruGold/XMRT-Ecosystem)
""")
