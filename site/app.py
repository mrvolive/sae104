#! /usr/bin/python
# -*- coding:utf-8 -*-

# == Importations == #
from flask import Flask, request, render_template, redirect, session, g, flash
import pymysql.cursors

# == Configuration == #
app = Flask(__name__)
app.secret_key = "azerty"


# == Connexion à la base de données == #
def get_db():
    if "db" not in g:
        g.db = pymysql.connect(
            host="localhost",
            user="omaraval",
            password="3112",
            database="BDD_omaraval",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
    return g.db


# == Déconnexion de la base de données == #
@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


################
# == Routes == #
################


@app.route("/")
def show_index():
    return render_template("index.html")


# == Routes appartements == #


# == Routes consommations == #
@app.route("/consommations/show")
def show_consommations():
    mycursor = get_db().cursor()
    sql ='''SELECT id_consomme AS id, date_conso AS date, quantite_consomme AS quantite, libelle_consommable AS type, num_appartement AS appartement
    FROM consomme
    INNER JOIN consommable ON consomme.id_consommable = consommable.id_consommable
    ORDER BY date_conso DESC;'''
    mycursor.execute(sql)
    liste_consommations = mycursor.fetchall()
    return render_template("consommations/show_consommations.html", conso=liste_consommations)

@app.route('/consommations/delete')
def delete_consommations():
    print('''suppression d'une consommation''')
    id=request.args.get('id',0)
    print(id)
    mycursor = get_db().cursor()
    tuple_param=(id)
    sql="DELETE FROM consomme WHERE id_consomme=%s;"
    mycursor.execute(sql,tuple_param)

    get_db().commit()
    print(request.args)
    print(request.args.get('id'))
    id=request.args.get('id',0)
    return redirect('/consommations/show')

@app.route('/consommations/edit', methods=['GET'])
def edit_consommation():
    print('''affichage du formulaire pour modifier une consommation''')
    print(request.args)
    print(request.args.get('id'))
    
    id=request.args.get('id')
    mycursor = get_db().cursor()
    sql = '''SELECT id_consomme AS id, date_conso AS date, quantite_consomme AS quantite, id_consommable AS idc, num_appartement AS appartement
    FROM consomme
    WHERE id_consomme=%s;'''
    tuple_param=(id)
    mycursor.execute(sql,tuple_param)
    consommation = mycursor.fetchone()
    
    sql = '''SELECT id_consommable AS id, libelle_consommable AS type
    FROM consommable'''
    mycursor.execute(sql)
    consommable = mycursor.fetchall()
    
    sql = '''SELECT num_appartement AS num_app
    FROM appartement'''
    mycursor.execute(sql)
    appart = mycursor.fetchall()
    return render_template('consommations/edit_consommation.html', consommation=consommation, consommable=consommable, appart=appart)

@app.route('/consommations/edit', methods=['POST'])
def valid_edit_consommation():
    print('''modification de la consommation dans le tableau''')
    id = request.form.get('id')
    date = request.form.get('date')
    quantite = request.form.get('quantite')
    type = request.form.get('type')
    appartement = request.form.get('appartement')
    message = 'date:' + date + ' - quantite:' + quantite + ' - type:' + type + ' - appartement:' + appartement + ' - pour la consommation d identifiant:' + id
    print(message)
    mycursor = get_db().cursor()
    tuple_param=(date,quantite,type,appartement,id)
    sql="UPDATE consomme SET date_conso = %s, quantite_consomme= %s, id_consommable= %s, num_appartement= %s WHERE id_consomme=%s;"
    mycursor.execute(sql,tuple_param)
    get_db().commit()
    return redirect('/consommations/show')

@app.route('/consommations/add', methods=['GET'])
def add_consommation():
    print('''affichage du formulaire pour saisir un consommable''')

    mycursor = get_db().cursor()
    sql = '''SELECT id_consomme AS id, date_conso AS date, quantite_consomme AS quantite, id_consommable AS idc, num_appartement AS appartement
    FROM consomme'''
    mycursor.execute(sql)
    consommation = mycursor.fetchall()
    
    sql = '''SELECT id_consommable AS id, libelle_consommable AS type
    FROM consommable'''
    mycursor.execute(sql)
    consommable = mycursor.fetchall()
    
    sql = '''SELECT num_appartement AS num_app
    FROM appartement'''
    mycursor.execute(sql)
    appart = mycursor.fetchall()
    return render_template('consommations/add_consommation.html', consommation=consommation, consommable=consommable, appart=appart)

@app.route('/consommations/add', methods=['POST'])
def valid_add_consommation():
    print('''ajout du consommable dans le tableau''')
    date=request.form.get('date')
    quantite=request.form.get('quantite')
    type=request.form.get('type')
    appartement=request.form.get('appartement')
    message = 'date:' + date + ' - quantite:' + quantite + ' - type:' + type + ' - appartement:' + appartement
    print(message)
    mycursor = get_db().cursor()
    tuple_param=(date,quantite, type, appartement)
    sql="INSERT INTO consomme(id_consomme, date_conso, quantite_consomme, id_consommable, num_appartement) VALUES (NULL, %s, %s, %s, %s);"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/consommations/show')


# == Etat consommations == #

@app.route('/consommations/etat')
def show_etat_consommation():
    mycursor = get_db().cursor()
    sql = '''SELECT id_consomme AS id, date_conso AS date, quantite_consomme AS quantite, libelle_consommable AS type, num_appartement AS appartement
    FROM consomme
    INNER JOIN consommable ON consomme.id_consommable = consommable.id_consommable
    ORDER BY date_conso DESC;'''
    mycursor.execute(sql)
    liste_consommations = mycursor.fetchall()

    sql = ''' SELECT ROUND(AVG(quantite_consomme),2) as conso_moyenne_eau, appartement.num_appartement as appartement
    FROM consomme
    INNER JOIN appartement on consomme.num_appartement = appartement.num_appartement
    WHERE consomme.id_consommable = 1 AND year(consomme.date_conso) = 2023
    GROUP BY appartement.num_appartement;'''
    mycursor.execute(sql)
    conso_moy_eau = mycursor.fetchall()

    sql = '''SELECT COUNT(appartement.num_appartement) as 'over_elec' , appartement.num_appartement as 'appartement'
    FROM consomme
    INNER JOIN appartement on consomme.num_appartement = appartement.num_appartement
    WHERE consomme.id_consommable = 2 AND consomme.quantite_consomme > 300 AND year(consomme.date_conso) = 2023
    GROUP BY appartement.num_appartement;'''
    mycursor.execute(sql)
    over_conso_elec = mycursor.fetchall()

    sql = '''SELECT locataire.nom_locataire, locataire.prenom_locataire,appartement.num_appartement AS 'appartement',MIN(consomme.quantite_consomme) AS conso_elec_mois_min
    FROM appartement
    INNER JOIN locataire on appartement.num_appartement = locataire.num_appartement
    INNER JOIN consomme on appartement.num_appartement = consomme.num_appartement
    WHERE consomme.quantite_consomme = (SELECT MIN(quantite_consomme) FROM consomme WHERE id_consommable = 2) AND consomme.id_consommable = 2
    GROUP BY locataire.nom_locataire, locataire.prenom_locataire;'''
    mycursor.execute(sql)
    min_conso_elec = mycursor.fetchall()

    return render_template('consommations/etat_consommation.html', conso=liste_consommations,conso_moy_eau=conso_moy_eau, over_conso_elec=over_conso_elec, min_conso_elec=min_conso_elec)


# == Routes contrats == #
@app.route("/contrats/show")
def show_contrats():
    mycursor = get_db().cursor()
    sql = '''SELECT id_contrat AS id, montant_loyer AS montant, date_signature AS datesignature, date_debut_contrat AS datedebut, date_fin_contrat AS datefin, nb_locataires AS nombrelocataire, contrat.num_appartement AS appartement
    FROM contrat
    INNER JOIN appartement ON contrat.num_appartement = appartement.num_appartement
    ORDER BY date_signature ASC;'''
    mycursor.execute(sql)
    liste_contrats = mycursor.fetchall()
    return render_template("contrats/show_contrats.html", contra=liste_contrats)

@app.route('/contrats/delete')
def delete_contrats():
    print('''suppression d'un contrat''')
    id = request.args.get('id', 0)
    print(id)
    mycursor = get_db().cursor()
    tuple_param = id
    query = "SELECT COUNT(*) AS signe FROM signatures WHERE id_contrat = %s " #compter AS SIGN
    mycursor.execute(query,tuple_param)
    sign = mycursor.fetchone().get("signe")
    print(sign)
    if sign != 0:
        message = u'Suppression impossible ! (car contrainte clé étrangère)'
        print(message)
        flash(message, 'warning-success')
    else :
        sql = "DELETE FROM contrat WHERE id_contrat=%s;"
        mycursor.execute(sql, tuple_param)
        get_db().commit()
    print(request.args)
    print(request.args.get('id'))
    id = request.args.get('id', 0)
    return redirect('/contrats/show')


@app.route('/contrats/edit', methods=['GET'])
def edit_contrat():
    print('''affichage du formulaire pour modifier un contrat''')
    print(request.args)
    print(request.args.get('id'))
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = '''SELECT id_contrat AS id, montant_loyer AS montant, date_signature AS datesignature, date_debut_contrat AS datedebut, date_fin_contrat AS datefin, nb_locataires AS nombrelocataire, num_appartement AS appartement
    FROM contrat
    WHERE id_contrat=%s;'''
    tuple_param = (id)
    mycursor.execute(sql, tuple_param)
    contrat = mycursor.fetchone()
    sql = '''SELECT num_appartement AS appartement, superficie_appartement AS taille
    FROM appartement'''
    mycursor.execute(sql)
    appart = mycursor.fetchall()
    return render_template('contrats/edit_contrat.html', contrat=contrat, appart=appart)


@app.route('/contrats/edit', methods=['POST'])
def valid_edit_contrat():
    print('''modification d'un contrat dans le tableau''')
    id = request.form.get('id')
    montant = request.form.get('montant')
    datesignature= request.form.get('datesignature')
    datedebut = request.form.get('datedebut')
    datefin = request.form.get('datefin')
    nombrelocataire = request.form.get('nombrelocataire')
    appartement = request.form.get('appartement')
    message = 'montant:' + montant + ' - date de signature:' + datesignature + ' - date de debut:' + datedebut + '- date de fin:' + datefin + 'nombre de locataire' + nombrelocataire +'Numero d appartement' + str(appartement) +' - pour le contrat d identifiant:' + id
    print(message)
    mycursor = get_db().cursor()
    tuple_param = (montant, datesignature, datedebut, datefin, nombrelocataire, appartement, id)
    sql = "UPDATE contrat SET montant_loyer = %s, date_signature= %s, date_debut_contrat = %s, date_fin_contrat = %s,nb_locataires =%s, num_appartement= %s WHERE id_contrat=%s;"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/contrats/show')


@app.route('/contrats/add', methods=['GET'])
def add_contrat():
    print('''affichage du formulaire pour saisir un contrat''')
    mycursor = get_db().cursor()
    sql = '''SELECT id_contrat AS id, montant_loyer AS montant, date_signature AS datesignature, date_debut_contrat AS datedebut, date_fin_contrat AS datefin, nb_locataires AS nombrelocataire, num_appartement AS appartement
    FROM contrat'''
    mycursor.execute(sql)
    contrat = mycursor.fetchall()
    sql = '''SELECT num_appartement AS num_app
    FROM appartement'''
    mycursor.execute(sql)
    appart = mycursor.fetchall()
    return render_template('contrats/add_contrat.html', contrat=contrat,appart=appart)

@app.route('/contrats/add', methods=['POST'])
def valid_add_contrat():
    print('''ajout du contratdans le tableau''')
    montant = request.form.get('montant')
    datesignature = request.form.get('datesignature')
    datedebut = request.form.get('datedebut')
    datefin = request.form.get('datefin')
    nombrelocataire = request.form.get('nombrelocataire')
    appartement = request.form.get('appartement')
    message = 'montant:' + montant + ' - date de signature:' + datesignature + ' - date de debut:' + datedebut + '- date de fin:' + datefin + 'nombre de locataire' + nombrelocataire + 'Numero d appartement' + appartement
    print(message)
    mycursor = get_db().cursor()
    tuple_param=(montant,datesignature,datedebut, datefin, nombrelocataire,appartement)
    sql="INSERT INTO contrat(id_contrat, montant_loyer,date_signature, date_debut_contrat, date_fin_contrat, nb_locataires, num_appartement) VALUES (NULL, %s, %s, %s, %s, %s,%s);"
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    return redirect('/contrats/show')

# == Etat contrat == #
@app.route('/contrats/etat')
def show_etat_contrat():
    mycursor = get_db().cursor()
    sql = '''SELECT ROUND(AVG(montant_loyer),2) as Loyer_Moyen  FROM contrat;'''
    mycursor.execute(sql)
    loy_moyen = mycursor.fetchall()
    sql = '''SELECT appartement.num_appartement, contrat.id_contrat, contrat.montant_loyer, contrat.date_debut_contrat, contrat.date_fin_contrat
FROM contrat 
JOIN appartement  ON contrat.num_appartement = appartement.num_appartement;
'''
    mycursor.execute(sql)
    recup_num_app = mycursor.fetchall()
    mycursor = get_db().cursor()
    sql = '''SELECT locataire.nom_locataire, locataire.prenom_locataire, contrat.date_debut_contrat, contrat.date_fin_contrat
FROM contrat
         INNER JOIN signatures ON signatures.id_contrat = contrat.id_contrat
         INNER JOIN locataire ON locataire.id_locataire = signatures.id_locataire
ORDER BY DATEDIFF(contrat.date_fin_contrat, contrat.date_debut_contrat) DESC
LIMIT 1;'''
    mycursor.execute(sql)
    long_contrat = mycursor.fetchall()
    return render_template('contrats/etat_contrat.html', loy_moyen=loy_moyen,recup_num_app=recup_num_app, long_contrat= long_contrat)

# Contrat qui englobe le plus de locataire
# Le contrat qui dure le plus longtemps ? Si possible
# Le loyer le plus bas

# == Routes locataires == #


#########################
# == Routes Exemples == #
#########################

# @app.route('/')
# @app.route('/etudiant/show')
# def show_etudiants():
#     mycursor = get_db().cursor()
#     sql=''' SELECT id_etudiant AS id, nom_etudiant AS nom, groupe_etudiant AS groupe
#     FROM etudiant
#     ORDER BY nom_etudiant;'''
#     mycursor.execute(sql)
#     liste_etudiants = mycursor.fetchall()
#     return render_template('etudiant/show_contrats.html', etudiants=liste_etudiants )


# @app.route('/etudiant/add', methods=['GET'])
# def add_etudiant():
#     print('''affichage du formulaire pour saisir un étudiant''')
#     return render_template('etudiant/add_contrat.html')

# @app.route('/etudiant/delete')
# def delete_etudiant():
#     print('''suppression d'un étudiant''')
#     id=request.args.get('id',0)
#     print(id)
#     mycursor = get_db().cursor()
#     tuple_param=(id)
#     sql="DELETE FROM etudiant WHERE id_etudiant=%s;"
#     mycursor.execute(sql,tuple_param)

#     get_db().commit()
#     print(request.args)
#     print(request.args.get('id'))
#     id=request.args.get('id',0)
#     return redirect('/etudiant/show')

# @app.route('/etudiant/edit', methods=['GET'])
# def edit_etudiant():
#     print('''affichage du formulaire pour modifier un étudiant''')
#     print(request.args)
#     print(request.args.get('id'))
#     id=request.args.get('id')
#     mycursor = get_db().cursor()
#     sql=''' SELECT id_etudiant AS id, nom_etudiant AS nom, groupe_etudiant AS groupe
#     FROM etudiant
#     WHERE id_etudiant=%s;'''
#     tuple_param=(id)
#     mycursor.execute(sql,tuple_param)
#     etudiant = mycursor.fetchone()
#     return render_template('etudiant/edit_contrat.html', etudiant=etudiant)


# @app.route('/etudiant/add', methods=['POST'])
# def valid_add_etudiant():
#     print('''ajout de l'étudiant dans le tableau''')
#     nom = request.form.get('nom')
#     groupe = request.form.get('groupe')
#     message = 'nom :' + nom + ' - groupe :' + groupe
#     print(message)
#     mycursor = get_db().cursor()
#     tuple_param=(nom,groupe)
#     sql="INSERT INTO etudiant(id_etudiant, nom_etudiant, groupe_etudiant) VALUES (NULL, %s, %s);"
#     mycursor.execute(sql,tuple_param)
#     get_db().commit()
#     return redirect('/etudiant/show')

# @app.route('/etudiant/edit', methods=['POST'])
# def valid_edit_etudiant():
#     print('''modification de l'étudiant dans le tableau''')
#     id = request.form.get('id')
#     nom = request.form.get('nom')
#     groupe = request.form.get('groupe')
#     message = 'nom :' + nom + ' - groupe :' + groupe + ' pour l etudiant d identifiant :' + id
#     print(message)
#     mycursor = get_db().cursor()
#     tuple_param=(nom,groupe,id)
#     sql="UPDATE etudiant SET nom_etudiant = %s, groupe_etudiant= %s WHERE id_etudiant=%s;"
#     mycursor.execute(sql,tuple_param)
#     get_db().commit()
#     return redirect('/etudiant/show')


####################################
# == Lancement de l'application == #
####################################
if __name__ == "__main__":
    app.run(debug=True, port=5000)
