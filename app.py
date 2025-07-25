
import streamlit as st
import requests

st.set_page_config(page_title="XMRT Onboarding with Eliza", layout="centered")
st.title("🌐 XMRT DAO Onboarding")
st.subheader("The Token That Mines When the Internet Dies")

st.markdown("Welcome to XMRT. This onboarding assistant is powered by **Eliza**, the autonomous AI agent guiding new users through setup, mining, and DAO participation.")

prompt = st.text_input("💬 Ask Eliza a question", placeholder="e.g., How do I start mining on my phone?")

if prompt:
    with st.spinner("Eliza is thinking..."):
        try:
            response = requests.post(
                "https://xmrteliza.vercel.app/api/eliza",
                json={"prompt": prompt},
                timeout=15
            )
            st.markdown(f"🛠️ Raw status: `{response.status_code}`")
            try:
                json_data = response.json()
                st.markdown("📦 Eliza replied:")
                st.success(json_data.get("response", "No message"))
            except Exception as json_err:
                st.error("❌ Failed to parse JSON")
                st.code(response.text)
        except Exception as net_err:
            st.error(f"🔴 Network Error: {net_err}")

st.divider()
st.header("⛏️ Step 1: Get Started Mining")
st.markdown("[Visit MobileMonero.com](https://mobilemonero.com) to install Termux, run signup.py, and generate your rig ID.")

st.divider()
st.header("🧠 Step 2: Tokenize Your IP")
st.caption("Coming soon: Deploy your ideas as NFT + ERC20 tokens.")

st.divider()
st.header("🗳️ Step 3: Join the DAO")
if st.button("💡 Generate DAO Proposal"):
    try:
        proposal = requests.post("https://xmrteliza.vercel.app/api/eliza", json={"prompt": "Help me write a DAO proposal to reward early miners."})
        st.code(proposal.json().get("response", "Proposal failed"))
    except Exception as e:
        st.error(f"❌ Proposal error: {e}")

st.divider()
st.markdown("## 🌐 XMRT Ecosystem")
st.markdown("- [MobileMonero.com](https://mobilemonero.com)")
st.markdown("- [XMRT MESHNET Hub](https://xmrtdao.streamlit.app)")
st.markdown("- [GitHub: XMRT-Ecosystem](https://github.com/DevGruGold/XMRT-Ecosystem)")
