import streamlit as st

st.set_page_config(
    page_title="Teste Visual",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: white !important;
        font-family: 'Segoe UI', Arial, sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔧 Teste de Interface")
st.success("✅ Se você está vendo esta mensagem com fundo verde, o CSS está funcionando!")
st.error("❌ Se você está vendo esta mensagem com fundo vermelho, o CSS está funcionando!")
st.warning("⚠️ Se você está vendo esta mensagem com fundo amarelo, o CSS está funcionando!")
st.info("ℹ️ Se você está vendo esta mensagem com fundo azul, o CSS está funcionando!")

with st.sidebar:
    st.header("Menu de Teste")
    st.selectbox("Teste", ["Opção 1", "Opção 2", "Opção 3"])
    st.button("Botão de Teste")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Teste 1", "123", "10")

with col2:
    st.metric("Teste 2", "456", "-5")
    
with col3:
    st.metric("Teste 3", "789", "15")

st.write("Se todos os elementos acima estão visíveis e bem formatados, a interface está funcionando corretamente.")