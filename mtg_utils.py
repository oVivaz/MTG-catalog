import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

def load_data():
    """Carrega os dados da coleção MTG"""
    file_path = Path(r"C:\Users\Vito\MTG_Project\MTG_SCRY_PYTHON.xlsx")
    df = pd.read_excel(file_path, sheet_name='MTG_SCRY_PYTHON')
    
    # Processamentos que fizemos
    df['USD Price'] = pd.to_numeric(df['USD Price'], errors='coerce')
    df['Main Type'] = df['Type Line'].str.split(' — ').str[0]
    df['CMC'] = pd.to_numeric(df['CMC'], errors='coerce')
    
    # Análise de tipo de cor
    df['Tipo_Cor'] = 'Multicolor'
    df.loc[df['Color'].isin(['W', 'U', 'B', 'R', 'G']), 'Tipo_Cor'] = 'Monocolor'
    df.loc[df['Color'].isna(), 'Tipo_Cor'] = 'Incolor'
    
    return df

def create_rarity_chart(df):
    """Cria gráfico de distribuição de raridade"""
    rarity_counts = df['Rarity'].value_counts()
    fig = px.pie(values=rarity_counts.values, names=rarity_counts.index,
                 title='Distribuição de Raridade')
    return fig

def create_value_by_color_chart(df):
    """Cria gráfico de valor por cor"""
    value_by_color = df.groupby('Color')['USD Price'].sum().sort_values(ascending=False)
    fig = px.bar(x=value_by_color.index, y=value_by_color.values,
                 title='Valor Total por Cor',
                 labels={'x': 'Cor', 'y': 'Valor Total (USD)'})
    return fig

def create_set_chart(df, top_n=15):
    """Cria gráfico de top sets"""
    set_counts = df['Set name'].value_counts().head(top_n)
    fig = px.bar(y=set_counts.index, x=set_counts.values,
                 title=f'Top {top_n} Sets por Quantidade',
                 labels={'x': 'Quantidade', 'y': 'Set'})
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig