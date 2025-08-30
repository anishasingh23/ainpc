import streamlit as st, os, asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

st.set_page_config(page_title="AI NPC Battle Arena", layout="wide")
st.title("AI NPC Battle Arena")

MCP_URL = st.text_input("MCP URL", value=os.getenv("MCP_URL","http://127.0.0.1:8000/mcp"))
npc_options = ["EmberMage","IronKnight","WindBlade","MistCaller"]
col1, col2 = st.columns(2)
with col1:
    npc_a = st.selectbox("NPC A", npc_options, index=0)
    level = st.slider("Level", 10, 100, 50)
with col2:
    npc_b = st.selectbox("NPC B", npc_options, index=1)
    seed = st.number_input("Seed (for deterministic runs)", value=42, step=1)

if st.button("Simulate Battle"):
    st.info("Running simulation... make sure the MCP server is running (python server/mcp_server.py http)")
    async def call_simulate():
        async with streamablehttp_client(MCP_URL) as (r,w,_):
            async with ClientSession(r,w) as sess:
                await sess.initialize()
                res = await sess.call_tool("simulate_battle_tool", arguments={"npc_a":npc_a,"npc_b":npc_b,"level":level,"seed":int(seed)})
                return res.structuredContent
    try:
        result = asyncio.run(call_simulate())
        st.subheader("Winner: " + result["winner"])
        st.text_area("Battle Log", value="\\n".join(result["log"]), height=400)
        if st.button("Generate Narration (Groq)"):
            async def call_narrate():
                async with streamablehttp_client(MCP_URL) as (r,w,_):
                    async with ClientSession(r,w) as sess:
                        await sess.initialize()
                        narr = await sess.call_tool("narrate_battle_with_groq", arguments={"battle_log": result["log"], "style":"sportscaster"})
                        return narr.structuredContent.get("narration","")
            try:
                narration = asyncio.run(call_narrate())
                st.markdown("**Narration:**")
                st.write(narration)
            except Exception as e:
                st.error("Narration failed. Ensure GROQ_API_KEY is set and groq installed. " + str(e))
    except Exception as e:
        st.error("Simulation failed: " + str(e))

st.markdown("---")
st.markdown("**Quick start**: Run `python server/mcp_server.py http` in one terminal; open this Streamlit app (`streamlit run dashboard/app.py`) in another.")
