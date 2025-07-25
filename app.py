import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="XMRT Onboarding", layout="centered")
st.title("ðŸš€ XMRT DAO Onboarding")
st.subheader("The Token That Mines When the Internet Dies")

# Configure Gemini
genai.configure(api_key="AIzaSyAS9tG4JzVnCfaoiYJzSOIhacB0lB3dVsg")
eliza = genai.GenerativeModel("gemini-pro").start_chat()

# Input: user alias
alias = st.text_input("Whatâ€™s your alias, miner?")

if alias:
    st.markdown("### ðŸ¤– Eliza says:")
    welcome = eliza.send_message(f"My name is {alias}. Help me get started with XMRT.")
    st.info(welcome.text)

    # Embed that alias into vector space
    try:
        embedding = genai.embed_content(
            model="models/embedding-001",
            content=f"{alias} joined XMRT onboarding and created a rig.",
            task_type="RETRIEVAL_DOCUMENT"
        )
        st.success("âœ… Identity embedded successfully!")
        st.caption(f"Vector preview: {embedding['embedding'][:5]}...")
    except Exception as e:
        st.error(f"Embedding error: {e}")

st.divider()
st.markdown("## â›ï¸ Get Started Mining")
st.markdown("""
Install Termux â†’ run `signup.py` â†’ generate your rig ID  
Then visit [ðŸ“Š MESHNET Dashboard](https://xmrtdao.streamlit.app)
""")

st.divider()
st.markdown("## ðŸ§  Tokenize Your IP")
if st.button("Deploy NFT + ERC20 Token"):
    eliza_response = eliza.send_message("What does deploying my IP token actually do?")
    st.success(eliza_response.text)

st.divider()
st.markdown("## ðŸ—³ï¸ Propose to the DAO")
if st.button("Write my proposal"):
    proposal = eliza.send_message("Help me write a DAO proposal to reward early miners.")
    st.code(proposal.text)

st.divider()
st.markdown("## ðŸŒ XMRT Ecosystem")
st.markdown("""
- [ðŸ“± MobileMonero.com](https://mobilemonero.com)
- [ðŸ“Š MESHNET DAO Hub](https://xmrtdao.streamlit.app)
- [ðŸ¤– Eliza Web Agent](https://xmrteliza.vercel.app)
- [ðŸ“ GitHub Starter Kit](https://github.com/DevGruGold/xmrtnet/tree/main)
""")