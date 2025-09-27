import streamlit as st
import pandas as pd
import plotly.express as px
from mtg_utils import load_data, create_rarity_chart, create_value_by_color_chart, create_set_chart

# Configuração da página
st.set_page_config(
    page_title="Catálogo MTG - Minha Coleção",
    page_icon="🎴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🎴 Catálogo Interativo - Coleção MTG")
st.markdown("---")

# Carregar dados com cache
@st.cache_data
def load_cached_data():
    return load_data()

df = load_cached_data()

# Sidebar com filtros
st.sidebar.header("🔍 Filtros e Configurações")

# Filtros
selected_set = st.sidebar.selectbox('Set:', ['Todos'] + sorted(df['Set name'].unique().tolist()))
selected_rarity = st.sidebar.selectbox('Raridade:', ['Todas'] + sorted(df['Rarity'].unique().tolist()))
selected_color = st.sidebar.selectbox('Cor:', ['Todas'] + sorted(df['Color'].dropna().unique().tolist()))
selected_type = st.sidebar.selectbox('Tipo Principal:', ['Todos'] + sorted(df['Main Type'].dropna().unique().tolist()))

# Filtro de preço
min_price, max_price = st.sidebar.slider(
    'Faixa de Preço (USD):',
    min_value=0.0,
    max_value=float(df['USD Price'].max()),
    value=(0.0, float(df['USD Price'].max()))
)

# Aplicar filtros
filtered_df = df.copy()
if selected_set != 'Todos':
    filtered_df = filtered_df[filtered_df['Set name'] == selected_set]
if selected_rarity != 'Todas':
    filtered_df = filtered_df[filtered_df['Rarity'] == selected_rarity]
if selected_color != 'Todas':
    filtered_df = filtered_df[filtered_df['Color'] == selected_color]
if selected_type != 'Todos':
    filtered_df = filtered_df[filtered_df['Main Type'] == selected_type]

filtered_df = filtered_df[(filtered_df['USD Price'] >= min_price) & (filtered_df['USD Price'] <= max_price)]

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_cards = len(filtered_df)
    st.metric("Cartas Únicas", f"{total_cards:,}")

with col2:
    total_value = filtered_df['USD Price'].sum()
    st.metric("Valor Total", f"${total_value:,.2f}")

with col3:
    avg_value = filtered_df['USD Price'].mean()
    st.metric("Valor Médio", f"${avg_value:.2f}")

with col4:
    unique_sets = filtered_df['Set name'].nunique()
    st.metric("Sets Diferentes", unique_sets)

# Abas principais
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🎴 Visualizar Cartas", "📈 Análises", "🔍 Busca"])

with tab1:
    st.subheader("Visão Geral da Coleção")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_rarity_chart(filtered_df), use_container_width=True)
        st.plotly_chart(create_set_chart(filtered_df), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_value_by_color_chart(filtered_df), use_container_width=True)
        
        # Top 10 cartas mais valiosas
        st.subheader("🏆 Top 10 Cartas Mais Valiosas")
        top_cards = filtered_df.nlargest(10, 'USD Price')[['Name', 'Set name', 'Rarity', 'USD Price']]
        st.dataframe(top_cards, use_container_width=True)

with tab2:
    st.subheader("🎴 Visualização de Cartas")
    
    # Configurações de exibição
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        cols_per_row = st.selectbox("Cartas por linha:", [2, 3, 4, 5, 6, 7, 8, 9, 10], index=1)
    with col2:
        sort_by = st.selectbox("Ordenar por:", 
                              ['Nome', 'Preço (Maior)', 'Preço (Menor)', 'Set', 'Raridade'])
    with col3:
        items_per_page = st.selectbox("Cartas por página:", [20, 50, 100, 300], index=0)
    
    # Opção para mostrar imagens
    show_images = st.checkbox("📸 Mostrar imagens das cartas", value=True)
    
    # Ordenação
    if sort_by == 'Nome':
        display_df = filtered_df.sort_values('Name')
    elif sort_by == 'Preço (Maior)':
        display_df = filtered_df.sort_values('USD Price', ascending=False)
    elif sort_by == 'Preço (Menor)':
        display_df = filtered_df.sort_values('USD Price', ascending=True)
    elif sort_by == 'Set':
        display_df = filtered_df.sort_values('Set name')
    elif sort_by == 'Raridade':
        rarity_order = {'mythic': 0, 'rare': 1, 'uncommon': 2, 'common': 3, 'special': 4}
        display_df = filtered_df.copy()
        display_df['Rarity_Order'] = display_df['Rarity'].map(rarity_order)
        display_df = display_df.sort_values('Rarity_Order')
    
    # Paginação
    total_pages = max(1, len(display_df) // items_per_page + (1 if len(display_df) % items_per_page else 0))
    page = st.number_input("Página:", min_value=1, max_value=total_pages, value=1)
    
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(display_df))
    page_df = display_df.iloc[start_idx:end_idx]
    
    st.write(f"**Mostrando {start_idx + 1}-{end_idx} de {len(display_df)} cartas**")
    
    # Função para extrair URL da imagem
    def extract_image_url(image_cell):
        if pd.isna(image_cell):
            return None
        text = str(image_cell)
        if '=IMAGE(' in text:
            try:
                return text.split('"')[1]
            except:
                return None
        elif text.startswith('http'):
            return text
        return None
    
    # Exibir cartas
    if show_images:
        # Modo com imagens
        for i, (idx, row) in enumerate(page_df.iterrows()):
            if i % cols_per_row == 0:
                cols = st.columns(cols_per_row)
            
            with cols[i % cols_per_row]:
                with st.container():
                    # Extrair URL da imagem
                    image_url = extract_image_url(row.get('Image URL'))
                    
                    if image_url:
                        st.image(image_url, use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/244x340/2c3e50/ffffff?text=No+Image", 
                                use_container_width=True)
                    
                    st.write(f"**{row['Name']}**")
                    st.write(f"*{row['Set name']}*")
                    
                    # Cores para raridade
                    rarity_colors = {
                        'mythic': '🟡',
                        'rare': '🟠', 
                        'uncommon': '🔵',
                        'common': '⚪',
                        'special': '🟣'
                    }
                    
                    rarity_icon = rarity_colors.get(row['Rarity'], '⚫')
                    st.write(f"{rarity_icon} **{row['Rarity'].title()}**")
                    st.write(f"🎨 **Cor:** {row.get('Color', 'N/A')}")
                    st.write(f"💲 **Preço:** ${row['USD Price']:.2f}")
                    
                    with st.expander("Ver detalhes"):
                        st.write(f"**Tipo:** {row.get('Type Line', 'N/A')}")
                        st.write(f"**CMC:** {row.get('CMC', 'N/A')}")
                        if pd.notna(row.get('Mana Cost')):
                            st.write(f"**Custo de Mana:** {row['Mana Cost']}")
                        if pd.notna(row.get('Oracle Text')):
                            st.write(f"**Texto:**")
                            st.text(row['Oracle Text'])
                    
                    st.markdown("---")
    else:
        # Modo tabela (rápido)
        for idx, row in page_df.iterrows():
            with st.expander(f"{row['Name']} - {row['Set name']} (${row['USD Price']:.2f})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Raridade:** {row['Rarity']}")
                    st.write(f"**Cor:** {row.get('Color', 'N/A')}")
                    st.write(f"**Tipo:** {row.get('Type Line', 'N/A')}")
                with col2:
                    st.write(f"**CMC:** {row.get('CMC', 'N/A')}")
                    if pd.notna(row.get('Oracle Text')):
                        st.write("**Texto:**")
                        st.text(row['Oracle Text'][:300] + "..." if len(str(row['Oracle Text'])) > 300 else row['Oracle Text'])
    
    # Controles de paginação
    if total_pages > 1:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.write(f"**Página {page} de {total_pages}**")
            prev_col, next_col = st.columns(2)
            with prev_col:
                if page > 1:
                    if st.button("⏪ Página Anterior"):
                        st.rerun()
            with next_col:
                if page < total_pages:
                    if st.button("Próxima Página ⏩"):
                        st.rerun()

with tab3:
    st.subheader("📈 Análises Detalhadas")
    
    # Análise de criaturas
    creatures = filtered_df[filtered_df['Main Type'].str.contains('Creature', na=False)]
    if len(creatures) > 0:
        st.write(f"**🐉 Análise de Criaturas:** {len(creatures)} cartas")
        
        col1, col2 = st.columns(2)
        with col1:
            # Distribuição de poder
            creatures['Power_num'] = pd.to_numeric(creatures['Power'], errors='coerce')
            fig_power = px.histogram(creatures.dropna(subset=['Power_num']), 
                                   x='Power_num', 
                                   title='Distribuição de Poder das Criaturas',
                                   labels={'Power_num': 'Poder'})
            st.plotly_chart(fig_power, use_container_width=True)
        
        with col2:
            # Distribuição de resistência
            creatures['Toughness_num'] = pd.to_numeric(creatures['Toughness'], errors='coerce')
            fig_toughness = px.histogram(creatures.dropna(subset=['Toughness_num']), 
                                       x='Toughness_num',
                                       title='Distribuição de Resistência das Criaturas',
                                       labels={'Toughness_num': 'Resistência'})
            st.plotly_chart(fig_toughness, use_container_width=True)
    
    # Análise de CMC
    st.write("**📊 Análise de Custo de Mana (CMC)**")
    cmc_df = filtered_df.dropna(subset=['CMC'])
    if len(cmc_df) > 0:
        col1, col2 = st.columns(2)
        with col1:
            fig_cmc_dist = px.histogram(cmc_df, x='CMC', 
                                      title='Distribuição de CMC',
                                      labels={'CMC': 'Custo de Mana Convertido'})
            st.plotly_chart(fig_cmc_dist, use_container_width=True)
        
        with col2:
            fig_cmc_price = px.scatter(cmc_df, x='CMC', y='USD Price', color='Rarity',
                                     title='Relação: CMC vs Preço',
                                     hover_data=['Name'],
                                     labels={'CMC': 'Custo de Mana', 'USD Price': 'Preço (USD)'})
            st.plotly_chart(fig_cmc_price, use_container_width=True)
    
    # Análise de valor por tipo
    st.write("**💎 Análise por Tipo de Carta**")
    value_by_type = filtered_df.groupby('Main Type')['USD Price'].sum().sort_values(ascending=False)
    if len(value_by_type) > 0:
        fig_type = px.bar(x=value_by_type.index, y=value_by_type.values,
                        title='Valor Total por Tipo de Carta',
                        labels={'x': 'Tipo', 'y': 'Valor Total (USD)'})
        st.plotly_chart(fig_type, use_container_width=True)

with tab4:
    st.subheader("🔍 Busca Avançada de Cartas")
    
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Buscar por nome da carta:")
    with col2:
        search_in_text = st.checkbox("Buscar também no texto da carta")
    
    if search_term:
        if search_in_text:
            # Buscar no nome e no texto
            results = filtered_df[
                filtered_df['Name'].str.contains(search_term, case=False, na=False) |
                filtered_df['Oracle Text'].str.contains(search_term, case=False, na=False)
            ]
        else:
            # Buscar apenas no nome
            results = filtered_df[filtered_df['Name'].str.contains(search_term, case=False, na=False)]
        
        st.write(f"**Resultados:** {len(results)} cartas encontradas")
        
        for idx, row in results.iterrows():
            with st.expander(f"{row['Name']} - {row['Set name']} (${row['USD Price']:.2f})"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    # Tentar mostrar imagem
                    image_url = extract_image_url(row.get('Image URL'))
                    if image_url:
                        st.image(image_url, width=200)
                    else:
                        st.image("https://via.placeholder.com/200x280/2c3e50/ffffff?text=No+Image", 
                                width=200)
                
                with col2:
                    st.write(f"**Nome:** {row['Name']}")
                    st.write(f"**Set:** {row['Set name']}")
                    st.write(f"**Raridade:** {row['Rarity']}")
                    st.write(f"**Cor:** {row.get('Color', 'N/A')}")
                    st.write(f"**Tipo:** {row.get('Type Line', 'N/A')}")
                    st.write(f"**CMC:** {row.get('CMC', 'N/A')}")
                    st.write(f"**Preço:** ${row['USD Price']:.2f}")
                    if pd.notna(row.get('Mana Cost')):
                        st.write(f"**Custo de Mana:** {row['Mana Cost']}")
                    if pd.notna(row.get('Oracle Text')):
                        st.write(f"**Texto:**")
                        st.text(row['Oracle Text'])

# Footer
st.markdown("---")
st.markdown("**Catálogo MTG** - Desenvolvido com Streamlit | Coleção: 1.258 cartas")

# Adicionar função extract_image_url se não estiver definida
def extract_image_url(image_cell):
    if pd.isna(image_cell):
        return None
    text = str(image_cell)
    if '=IMAGE(' in text:
        try:
            return text.split('"')[1]
        except:
            return None
    elif text.startswith('http'):
        return text
    return None
