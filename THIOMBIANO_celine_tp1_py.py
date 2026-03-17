# %% [markdown]
# # THIOMBIANO_Céline_TP1

# %% [markdown]
# ## Importation des bibliothèques

# %%
import pandas as pd
import plotly as plt
import calendar
import warnings
warnings.filterwarnings("ignore")

# %% [markdown]
# ## Etape 2 : Chargement et préparation des données
# 
# ### Chargement des données

# %%
data = pd.read_csv("datasets/data.csv")  

# %%
data.info()

# %% [markdown]
# ### Colonnes utiles

# %%
df=data[['CustomerID', 'Gender', 'Location', 'Product_Category', 'Quantity', 'Avg_Price', 'Transaction_Date', 'Month', 'Discount_pct']]

# %%
df.describe()

# %% [markdown]
# ### Traitement des valeurs manquantes

# %%
df['CustomerID'] = df['CustomerID'].fillna(0).astype(int)

# %%
df['CustomerID'].count()

# %%
## Remplissage des valeurs manquantes de la colonne "Location" par "Unknown" (utile pour le dropdown)
df["Location"] = df["Location"].fillna("Unknown")
df["Location"].count()

# %% [markdown]
# ### Conversion en date

# %%
df["Transaction_Date"] = pd.to_datetime(df["Transaction_Date"], errors="coerce")


# %% [markdown]
# ### Création de `Total_price` avec remise

# %%
df['Total_price']=df['Quantity']*df['Avg_Price']*(1-df['Discount_pct']/100)

# %%
df.head()

# %%
df.dtypes

# %% [markdown]
# ## Etapes 3: Fonctions metiers
# 
# ### Fonctions à completer

# %% [markdown]
# #### CA

# %%
# Creation de fonction du chiffre d'affaire
def calculer_chiffre_affaire(df):
    df['CA'] = df['Quantity'] * df['Total_price']
    return df['CA'].sum() # somme de la colonne CA pour obtenir le chiffre d'affaire total


# %%
calculer_chiffre_affaire(df)

# %% [markdown]
# #### Frequence meilleur vente

# %%
## frequence_meilleure_vente(data, top=10, ascending=False)
def frequence_meilleure_vente(df, top=10, ascending=False):

    freq = ( # Freq pour calculer la fréquence de vente par catégorie de produit
        df.groupby('Product_Category')['Quantity']# groupby pour regrouper les données par catégorie de produit et Quantity pour compter le nombre de produits vendus
        .sum()
        .reset_index() # reset_index pour réinitialiser l'index du DataFrame résultant
        .sort_values(by='Quantity', ascending=ascending)
        .head(top)
    )
    return freq

# %%
frequence_meilleure_vente(df)

# %% [markdown]
# #### indicateur_du mois

# %%
#indicateur_du_mois(data, current_month=12, freq=True, abbr=False)
def indicateur_du_mois(df, current_month=12, freq=True, abbr=False):
    df['Month'] = df['Transaction_Date'].dt.month # Extraire le mois de la date de transaction
    ventes_mois = df[df['Month'] == current_month] # Filtrer les ventes du mois spécifié
    if freq: # Si freq est True, calculer la fréquence (nombre de ventes)
        indicateur = len(ventes_mois)
    else: # Sinon, calculer le chiffre d'affaires total du mois
        indicateur = ventes_mois['Total_price'].sum()
    if abbr: # Si abbr est True, retourner l'abréviation du mois
        return calendar.month_abbr[current_month], indicateur
    else: # Sinon, retourner le nom complet du mois
        return calendar.month_name[current_month], indicateur

#current_month=12 :le mois que l’on veut analyser.Par défaut c’est 12, donc décembre.
#freq=True :indique le type d’indicateur à calculer.True → nombre de ventes/ False → chiffre d’affaires total

# %% [markdown]
# ## Etapes 4 : Graphiques

# %% [markdown]
# ### barplot_top_10_ventes

# %%
# barplot_top_10_ventes(data) (avec plotly et en fonction de gender)

import plotly.express as px

def barplot_top_10_ventes(df):
    
    # Top 10 catégories les plus vendues
    top_10 = frequence_meilleure_vente(df, top=10, ascending=False)
    
    # filtrer le dataframe sur ces catégories
    df_top = df[df['Product_Category'].isin(top_10['Product_Category'])]# filtrer le dataframe pour ne garder que les lignes dont la catégorie de produit est dans le top 10
    
    # regrouper les ventes par catégorie et genre
    ventes = (
        df_top.groupby(['Product_Category','Gender'])
        .size() # compter le nombre de ventes
        .reset_index(name='Quantity') # convertir la série en DataFrame et nommer la colonne de comptage 'Quantity'
    )  # .reset_index() pour convertir la série en DataFrame et nommer la colonne de comptage 'Quantity'
    
    # graphique
    fig = px.bar(
        ventes,
        x='Quantity',
        y='Product_Category',
        color='Gender',
        orientation='h', # orientation='h' pour un graphique horizontal
        barmode='group', # barmode='group' pour afficher les barres côte à côte
        title='Fréquence des 10 meilleures ventes par catégorie et par sexe',
        labels={
            'Quantity':'Total ventes',
            'Product_Category':'Catégorie du produit',
            'Gender':'Sexe'
        }
    )
    
    # trier les catégories
    fig.update_layout(yaxis={'categoryorder':'total ascending'}) # yaxis={'categoryorder':'total ascending'} pour trier les catégories par ordre croissant de ventes totales
    
    return fig

# %%
barplot_top_10_ventes(df)

# %% [markdown]
# ### plot_evolution_chiffre_affaire(data)

# %%
import pandas as pd
import plotly.express as px

def plot_evolution_chiffre_affaire(df):
    data = df.copy()

    data["Transaction_Date"] = pd.to_datetime(data["Transaction_Date"], errors="coerce")
    data = data.dropna(subset=["Transaction_Date", "Total_price"])

    # dernière vraie date
    last_date = data["Transaction_Date"].max()

    ca_semaine = (
        data
        .set_index("Transaction_Date")
        .resample("W")["Total_price"]
        .sum()
        .reset_index()
    )

    # supprimer les semaines qui dépassent la dernière date réelle
    ca_semaine = ca_semaine[ca_semaine["Transaction_Date"] <= last_date]

    fig = px.line(
        ca_semaine,
        x="Transaction_Date",
        y="Total_price",
        title="Evolution du chiffre d'affaire par semaine",
        labels={
            "Transaction_Date": "Semaine",
            "Total_price": "Chiffre d'affaire"
        },
        template="plotly_white"
    )

    fig.update_traces(
        line=dict(color="#636EFA", width=2),
        mode="lines"
    )

    fig.update_layout(
        plot_bgcolor="#E5ECF6",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=50, b=20),
        height=320,
        xaxis=dict(
            title="Semaine",
            showgrid=True,
            gridcolor="white"
        ),
        yaxis=dict(
            title="Chiffre d'affaire",
            showgrid=True,
            gridcolor="white",
            tickformat="~s"
        )
    )

    return fig

# %%
plot_evolution_chiffre_affaire(df)

# %% [markdown]
# ### plot_chiffre_affaire_mois(data) 
# 

# %%
import pandas as pd
import plotly.express as px
import calendar

def plot_chiffre_affaire_mois(data):
    df = data.copy()

    # Extraire le mois
    df["Month"] = df["Transaction_Date"].dt.month

    # Dernier mois présent dans les données
    current_month = int(df["Month"].max())
    prev_month = 12 if current_month == 1 else current_month - 1

    # Calculs
    ca_mois = df.loc[df["Month"] == current_month, "Total_price"].sum()
    ca_prev = df.loc[df["Month"] == prev_month, "Total_price"].sum()
    variation = ca_mois - ca_prev

    # Libellés
    mois_label = calendar.month_name[current_month]
    ca_text = f"{round(ca_mois / 1000):.0f}k"

    if variation >= 0: 
        var_color = "#3BA272"
        var_text = f"▲ {round(variation / 1000):.0f}k"
    else:
        var_color = "#FF4B3A"
        var_text = f"▼ {round(variation / 1000)}k"

    # Figure vide avec Plotly Express
    fig = px.scatter()
    fig.update_traces(hoverinfo="skip", showlegend=False)

    fig.add_annotation(
        x=0.5, y=0.82,
        xref="paper", yref="paper",
        text=mois_label,
        showarrow=False,
        font=dict(size=24, color="#2a3f5f")
    )

    fig.add_annotation(
        x=0.5, y=0.50,
        xref="paper", yref="paper",
        text=ca_text,
        showarrow=False,
        font=dict(size=56, color="#2a3f5f")
    )

    fig.add_annotation(
        x=0.5, y=0.20,
        xref="paper", yref="paper",
        text=var_text,
        showarrow=False,
        font=dict(size=24, color=var_color)
    )

    fig.update_layout(
        width=260,
        height=180,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=10)
    )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    return fig


# %%
plot_chiffre_affaire_mois(df)

# %% [markdown]
# ### plot_vente_mois(data, abbr=False)

# %%
print((df["Month"] == 12).sum())

# %%
import pandas as pd
import plotly.express as px
import calendar

def plot_vente_mois(data, abbr=False):
    df = data.copy()

    # Utiliser la colonne Month existante (ne pas la recalculer)
    current_month = int(df["Month"].dropna().max())
    prev_month = 12 if current_month == 1 else current_month - 1

    # Calcul du nombre de ventes
    ventes_mois = (df["Month"] == current_month).sum()
    ventes_prev = (df["Month"] == prev_month).sum()
    variation = ventes_mois - ventes_prev

    # Libellé du mois
    mois_label = calendar.month_abbr[current_month] if abbr else calendar.month_name[current_month]

    # Texte de variation
    if variation >= 0:
        var_color = "#3BA272"
        var_text = f"▲ {variation}"
    else:
        var_color = "#FF4B3A"
        var_text = f"▼ {variation}"

    # Figure vide
    fig = px.scatter()
    fig.update_traces(hoverinfo="skip", showlegend=False)

    # Titre (mois)
    fig.add_annotation(
        x=0.5, y=0.82,
        xref="paper", yref="paper",
        text=mois_label,
        showarrow=False,
        font=dict(size=24, color="#2a3f5f")
    )

    # Nombre de ventes
    fig.add_annotation(
        x=0.5, y=0.50,
        xref="paper", yref="paper",
        text=str(ventes_mois),
        showarrow=False,
        font=dict(size=56, color="#2a3f5f")
    )

    # Variation
    fig.add_annotation(
        x=0.5, y=0.20,
        xref="paper", yref="paper",
        text=var_text,
        showarrow=False,
        font=dict(size=24, color=var_color)
    )

    # Style
    fig.update_layout(
        width=260,
        height=180,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=10)
    )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    return fig

# %%
plot_vente_mois(df, abbr=False)

# %% [markdown]
# ### Table des 100 dernières ventes

# %%
# =========================
# Préparation de la table
# =========================
def prepare_last_sales(data):
    table_df = (
        data.sort_values("Transaction_Date", ascending=False)
            .head(100)
            .loc[:, [
                "Transaction_Date",
                "Gender",
                "Location",
                "Product_Category",
                "Quantity",
                "Avg_Price",
                "Discount_pct"
            ]]
            .rename(columns={
                "Transaction_Date": "Date",
                "Product_Category": "Product Category",
                "Avg_Price": "Avg Price",
                "Discount_pct": "Discount Pct"
            })
            .copy()
    )

    table_df["Date"] = pd.to_datetime(table_df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return table_df


# %% [markdown]
# # Création de l'appliaction

# %%
# ==== Importation des librairies ====#
import dash
from dash import html, dcc, dash_table, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

# =========================
# App
# =========================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.H2("ECAP Store", style={"margin": "10px", "fontWeight": "bold"}),
            width=6
        ),

        dbc.Col(
            html.Div(
                dcc.Dropdown(
                    id="zone_dropdown",
                    options=[
                        {"label": loc, "value": loc}
                        for loc in sorted(df["Location"].dropna().unique())
                    ],
                    placeholder="Choisissez des zones",
                    multi=True,
                    clearable=True,
                ),
                style={
                    "width": "80%",
                    "marginLeft": "1%",
                    "marginTop": "8px"
                }
            ),
            width=6
        )
    ], style={"backgroundColor": "#b7d9e6"}),

    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col(
                    dcc.Graph(
                        id="kpi_ca",
                        config={"displayModeBar": False},
                        style={"height": "140px"}
                    ),
                    width=6
                ),
                dbc.Col(
                    dcc.Graph(
                        id="kpi_ventes",
                        config={"displayModeBar": False},
                        style={"height": "140px"}
                    ),
                    width=6
                ),
            ], style={"height": "150px"}),

            dbc.Row([
                dbc.Col(
                    dcc.Graph(
                        id="bar_top10",
                        config={"displayModeBar": False},
                        style={"height": "550px", "width": "100%"}
                    ),
                    width=12
                )
            ])
        ], width=5),

        dbc.Col([
            dbc.Row([
                dbc.Col(
                    dcc.Graph(
                        id="line_ca_week",
                        config={"displayModeBar": False},
                        style={"height": "320px", "width": "100%"}
                    ),
                    width=12,
                )
            ]),

            dbc.Row([
                dbc.Col([
                    html.H3(
                        "Table des 100 dernières ventes",
                        style={"marginBottom": "10px"}
                    ),
                    dash_table.DataTable(
                        id="table_last_sales",
                        page_size=10,
                        filter_action="native",
                        sort_action="native",
                        style_table={"overflowX": "auto"},
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold",
                            "textAlign": "center"
                        },
                        style_cell={
                            "textAlign": "center",
                            "padding": "6px",
                            "fontSize": "12px",
                            "fontFamily": "Arial",
                            "border": "1px solid #cfcfcf"
                        }
                    )
                ], style={"height": "380px"})
            ]),
        ], width=7),
    ])
], fluid=True)

# =========================
# Callback
# =========================
@app.callback(
    Output("kpi_ca", "figure"),
    Output("kpi_ventes", "figure"),
    Output("bar_top10", "figure"),
    Output("line_ca_week", "figure"),
    Output("table_last_sales", "data"),
    Output("table_last_sales", "columns"),
    Input("zone_dropdown", "value")
)
def update_dashboard(selected_zones): # selected_zones : liste des zones sélectionnées dans le dropdown
    dff = df.copy()

    if selected_zones:
        dff = dff[dff["Location"].isin(selected_zones)]

    table_df = prepare_last_sales(dff)

    return (
        plot_chiffre_affaire_mois(dff),
        plot_vente_mois(dff, abbr=False),
        barplot_top_10_ventes(dff),
        plot_evolution_chiffre_affaire(dff),
        table_df.to_dict("records"),
        [{"name": col, "id": col} for col in table_df.columns]
    )

if __name__ == "__main__":
    app.run(debug=True)

