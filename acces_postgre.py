"""
Module pour accéder à la base de données locale PostgreSQL
"""

#####################################################################
# IMPORTATION DES MODULES
#####################################################################

import psycopg2

#####################################################################
# CONFIGURATION
#####################################################################
# Connexion à la base de données PostgreSQL

connection = psycopg2.connect(database="eaufrance", user="yuri", password="yuri",host='192.168.1.60' , port=5432)

cursor = connection.cursor()

cursor.execute("SELECT * from commune;")

record = cursor.fetchall()

print("Data from Database:- ", record)