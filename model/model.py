import pandas as pd
# Ajoute en haut du fichier
from sqlalchemy import create_engine

# Crée un engine SQLAlchemy UNE SEULE FOIS (en global)
engine = create_engine("postgresql+psycopg2://yuri:yuri@192.168.0.41:5432/eaufrance")

def fct_condition(filtres: dict):
    conditions = []
    params = []
    for cle, valeur in filtres.items():
        if valeur:
            conditions.append(f"{cle} = %s")
            params.append(valeur)
    return " AND ".join(conditions), tuple(params)



def obtenir_valeurs_distinctes(table, colonne):
    requete = f"""
    SELECT DISTINCT
        {colonne}
    FROM
        {table}
    """
    resultat = pd.read_sql_query(requete, engine)
    return resultat.to_dict(orient='records')


# Fonction générique pour obtenir des données filtrées
def obtenir_donnees_filtrees(table, colonnes, jointures, filtres) -> pd.DataFrame:
    condi_where, params = fct_condition(filtres)
    requete = f"""
    SELECT
        {', '.join(colonnes)}
    FROM
        {table}
    {jointures}
    WHERE
        {condi_where};
    """
    # Correction ici : transformer params en tuple
    info = pd.read_sql_query(requete, engine, params=tuple(params))
    return info

# Fonction générique pour obtenir des données
def obtenir_donnees(table, colonnes, jointures) -> pd.DataFrame:
    requete = f"""
    SELECT
        {', '.join(colonnes)}
    FROM
        {table}
    {jointures}
    """
    # Correction ici : transformer params en tuple
    info = pd.read_sql_query(requete, engine)
    return info

# Exemple d'utilisation pour la table Ouvrage
def obtenir_info_ouvrage(filtres=None):
    table = "ouvrages"
    colonnes = [
        'ouvrages.code_ouvrage', #varchar300 PK
        'ouvrages.nom_ouvrage', #varchar200
        'ouvrages.date_exploitation_debut', #DATE
        'ouvrages.date_exploitation_fin', #DATE
        'ouvrages.code_type_milieu', #varchar100
        'departement.libelle_departement', #VARCHAR(150)
        'ouvrages.longitude', #DECIMAL(9,6)
        'ouvrages.latitude', #DECIMAL(9,6)
        'ouvrages.code_departement'# FK
    ]
    jointures = """
    INNER JOIN departement ON departement.code_departement = ouvrages.code_departement
    """
    if filtres:
        return obtenir_donnees_filtrees(table, colonnes, jointures, filtres)
    else:
        return obtenir_donnees(table, colonnes, jointures)

# Exemple d'utilisation pour la table Point Prelevement
def obtenir_info_prelevement(filtres=None):
    table = "pt_prelevement"
    colonnes = [
        'pt_prelevement.code_point_prelevement', #varchar300 PK
        'pt_prelevement.code_ouvrage', #Varchar200
        'pt_prelevement.nom_point_prelevement', #varchar200
        'pt_prelevement.date_exploitation_debut', #DATE
        'pt_prelevement.code_type_milieu', #varchar100
        'pt_prelevement.libelle_nature', #varchar150
        'pt_prelevement.code_departement', #FK
        'departement.libelle_departement' # pour avoir le nom du département
    ]
    jointures = """
    INNER JOIN departement ON departement.code_departement = pt_prelevement.code_departement
    """
    if filtres:
        return obtenir_donnees_filtrees(table, colonnes, jointures, filtres)
    else:
        return obtenir_donnees(table, colonnes, jointures)

# Exemple d'utilisation pour la table Commune
def obtenir_info_commune(filtres=None):
    table = "commune"
    colonnes = [
        'commune.nom_commune', #varchar500
        'commune.code_commune_insee', #PK
        'commune.code_departement'#FK
    ]
    jointures = """
    INNER JOIN departement ON departement.code_departement = commune.code_departement
    """
    if filtres:
        return obtenir_donnees_filtrees(table, colonnes, jointures, filtres)
    else:
        return obtenir_donnees(table, colonnes, jointures)

# Exemple d'utilisation pour la table Departement
def obtenir_info_departement(filtres=None):
    table = "departement"
    colonnes = [
        "departement.code_departement", #PK
        "departement.libelle_departement", #varchar500
    ]
    jointures = """"""  # Pas de jointure pour cette table
    if filtres:
        return obtenir_donnees_filtrees(table, colonnes, jointures, filtres)
    else:
        return obtenir_donnees(table, colonnes, jointures)

# print(obtenir_info_ouvrage())
# print(obtenir_info_ouvrage({"nom_ouvrage": "AUDELONCOURT"}))
# print(obtenir_info_prelevement())
# print(obtenir_info_prelevement({"nom_point_prelevement": "ELECTRICITE DE FRANCE"}))
# print(obtenir_info_commune())
# print(obtenir_info_commune({"nom_commune": "Craincourt"}))
# print(obtenir_info_departement())
# print(obtenir_info_departement({"code_departement": "12"}))