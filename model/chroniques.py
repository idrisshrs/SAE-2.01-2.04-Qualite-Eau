import pandas as pd
import numpy as np
import model.model as db
from model.cache import cache

@cache.cached(key_prefix='donnees_chroniques', timeout=86400)
def cache_chroniques():
    """
    Charge les données des chroniques depuis l'API Hubeau avec mise en cache.
    """
    chroniques_instance = Chroniques()
    data_list = chroniques_instance.donnees()
    data_df = pd.DataFrame(data_list)
    return chroniques_instance, data_df


class Chroniques:
    def __init__(self):
        self.url = "https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques"

    def acces_chroniques(self,):
        df = pd.read_json(self.url)
        info = df["data"]
        arr = np.array(info)
        return arr
    
    def donnees(self):
        """
        (GROS) Probleme : Ya pas une donnée avec true comme prelevement_ecrasant
        """
        L = []
        for c in self.acces_chroniques():
            if c['code_qualification_volume'] == "1" and (c['code_statut_volume'] in ["1", "2"]):
                L.append(c)
        return L
    
    def colonnes(self):
        L = []
        for i in self.acces_chroniques()[0]:
            L.append(i)
        return L
    
    def filtre(self, colonne = None, filtre = None):
        """
        Renvoie un dataframe avec les données de chronique
        On peut filtrer avec des colonnes, mais cela marche sans parametres
        """
        chroniques = self.donnees()
        L = []
        for c in chroniques:
            if colonne and filtre:
                if c[colonne] == filtre:
                    L.append(c)
            else:
                L.append(c)
        return L
    
    def filtre_ulti(self, colonne: list = None, filtre: list = None):
        """
        Renvoie une liste avec les données filtrées
        ATTENTION : les colonnes filtrées doivent etre au meme indice que les filtres
        (genre, le filtre d'indice 0 doit etre de la colonne d'indice 0, etc)
        """
        chroniques = self.donnees()
        L = []
        for c in chroniques:
            if colonne and filtre:
                for i, j in zip(colonne, filtre):
                    if c[i] == j:
                        L.append(c)
            else:
                L.append(c)
        return L
    
    def filtre_ouv(self, nom_ouvrage):
        """
        Retourne une liste de dictionnaires contenant les volumes et années
        pour un nom d'ouvrage donné.
        """
        result = []
        for c in self.donnees():
            if c['nom_ouvrage'] == nom_ouvrage:
                result.append({
                    "annee": c['annee'],
                    "volume": c['volume']
                })
        return result
    
    def annee(self):
        chroniques = self.donnees()
        colonne = 'code_ouvrage'
        filtre = 'OPR0000000102'
        L = []
        for c in chroniques:
            if c[colonne] == filtre:
                L.append(c['annee'])
        return L
    
    def data_evo(self, usage, exp: int, colonne: list = None, filtre: list = None): # FILTARGE FAISABLE
            annees = self.annee()  # c une liste
            L = []
            for annee in annees:
                temp = 0
                if colonne and filtre:
                    for d in self.filtre(colonne, filtre):
                        if d['annee'] == annee and d['libelle_usage'] == usage:
                            temp += d['volume']
                    L.append(temp * exp)
                else:
                    for d in self.filtre():
                        if d['annee'] == annee and d['libelle_usage'] == usage:
                            temp += d['volume']
                    L.append(temp * exp)
            return L 


    def min_annee(self):
        return str(min(self.annee()))
    
    def max_annee(self):
        return str(max(self.annee()))
    
    def nom_ouvrage(self, ouvrage):
        for c in self.donnees():
            if c['code_ouvrage'] == ouvrage:
                return c['nom_ouvrage']

    def ouvrage(self, nom_ouvrage):
        L = []
        for c in self.donnees():
            if c['nom_ouvrage'] == nom_ouvrage:
                L.append(c['volume'])
        return L

    def usage(self):
        return ['EAU POTABLE', 'INDUSTRIE et ACTIVITES ECONOMIQUES (hors irrigation, hors énergie)']
    
    def usage2(self, colonne: list = None, filtre: list = None): # FILTRAGE FAISABLE
            L = []
            for usage in self.usage():
                i = 0
                if colonne and filtre:
                    for elt in self.filtre(colonne, filtre):
                        if elt['libelle_usage'] == usage:
                            i += 1
                    L.append(i)
                else:
                    for elt in self.filtre():
                        if elt['libelle_usage'] == usage:
                            i += 1
                    L.append(i)
            return L
    
    def compte_dep(self, colonne: list = None, filtre: list = None): # FILTRAGE FAISABLE
            dic = {}
            if colonne and filtre:
                for c in self.filtre(colonne, filtre):
                    if c['code_departement'] not in dic:
                        dic[c['code_departement']] = 1
                    else :
                        dic[c['code_departement']] += 1
            else:
                for c in self.filtre():
                    if c['code_departement'] not in dic:
                        dic[c['code_departement']] = 1
                    else :
                        dic[c['code_departement']] += 1

            retour = [{"dep": dep, "value": count} for dep, count in dic.items()]
            return retour
    
    def milieux(self):
        ouvrages = db.obtenir_info_ouvrage()
        L = []
        for i in ouvrages['code_type_milieu']:
            if i not in L:
                L.append(i)
        return L

# ------------- TEST ----------------------#

# chroniques = Chroniques()



# donnees = chroniques.donnees()

def milieu(usage, colonne: list = None, filtre: list = None):
    chroniques, data =  cache_chroniques()
    ouvrages = db.obtenir_info_ouvrage()
    ouvrages_sout = ouvrages[ouvrages['code_type_milieu'] == chroniques.milieux()[0]]['code_ouvrage'].tolist()
    ouvrages_autre = ouvrages[ouvrages['code_type_milieu'] == chroniques.milieux()[1]]['code_ouvrage'].tolist()
    volumes_par_ouvrage = {}
    if colonne and filtre:
        for c in chroniques.filtre_ulti(colonne, filtre):
            if 'volume' in c and c.get('libelle_usage') == usage:
                code = c['code_ouvrage']
                if code not in volumes_par_ouvrage:
                    volumes_par_ouvrage[code] = []
                volumes_par_ouvrage[code].append(c['volume'])
    else:
        for c in chroniques.filtre_ulti():
            if 'volume' in c and c.get('libelle_usage') == usage:
                code = c['code_ouvrage']
                if code not in volumes_par_ouvrage:
                    volumes_par_ouvrage[code] = []
                volumes_par_ouvrage[code].append(c['volume'])

    somme_sout = 0
    for code in ouvrages_sout:
        volumes = volumes_par_ouvrage.get(code, [])
        somme_sout += sum(volumes)

    somme_autre = 0
    for code in ouvrages_autre:
        volumes = volumes_par_ouvrage.get(code, [])
        somme_autre += sum(volumes)

    return [somme_sout, somme_autre]