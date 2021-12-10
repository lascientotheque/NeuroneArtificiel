# -*- coding: utf-8 -*-
# """
# Jeu de Nimm (Version 1)
# Auteur : Henri Goffaux
# Date : 12/11/2020
#
# Deux adversaires s'affrontent au jeu de Nimm. Ils peuvent être :
#     - un humain
#     - une IA jouant de manière aléatoire
#     - une IA jouant de manière optimale
#     - une IA jouant parfois de manière aléatoire, parfois de manière optimale
#     - une IA apprenant le jeu par apprentissage par renforcement :
#         2 boules représentent chaque possibilité de jouer : retirer 1, 2, ... allumettes
#         l'IA pioche au hasard parmi les boules existantes. Lorsqu'elle perd, chaque boule jouée est écartée,
#         de manière à diminuer la probabilité de rejouer ces coups à la prochaine partie. Lorsqu'elle gagne, chaque
#         boule tirée au sort par la machine, est remise en jeu. De plus, 1 autre boule de la même couleur est rajoutée.
#         Ainsi, à la partie suivante, ce coup aura une chance plus importante (probabilité plus forte) d’être joué.
#         On dit qu'on le "renforce".
#     - une IA apprenant le jeu en utilisant une fonction de valeur (Bellman)
#         Le programme détermine pour chaque allumette une valeur à partir d’une ‘Fonction de valeur’
#         dérivée de l’équation de Bellman. Ces valeurs sont représentatives de l'espérance d'obtenir la récompense
#         à l’issue de la manche, à savoir remporter celle-ci, si l’on se trouve sur une certaine allumette.
#         Plus l'IA va s’entraîner et plus ces valeurs vont converger vers des valeurs reflétant l’espérance de gagner
#         à partir de ces positions.
#
# En début de jeu, il est possible de modifier les paramètres par défaut du jeu proprement dit ou des joueurs
#
# Résultats:
#     - Les statisques de réussite des joueurs : nombre absolu, moyenne mobile des 10 dernières manches (%) et
#       mamche à partir de laquelle cette moyenne est de 50%
#     - Lorsqu'il y a apprentissage par renforcement : nombre de boules de chaque type par allumette
#     - Lorsqu'il y a apprentissage par fonction de valeur : valeur de chaque état calculé par l'équation de Bellman
# """

from random import random, randint
from math import ceil


def affichage_parametres(parametres):
    """ Fonction permettant d'afficher les paramètres du jeu et des 2 joueurs """

    def affichage_parametres_joueurs(joueur):
        print('joueur ' + str(joueur))
        print('  ' + 'Nom joueur: ' + parametres[joueur][3])
        print('  ' + 'Type: ' + ('Humain', 'IA')[parametres[joueur][0]])
        if (('Humain', 'IA')[parametres[joueur][0]] == 'IA'):
            print('  ' + 'Mode IA: ' + ('Aléatoire', 'Optimal', 'Aléatoire/Optimal', 'Apprentissage')[
                parametres[joueur][1]])
            if not parametres[joueur][2] == None:
                print('  ' + 'Mode apprentissage : ' + ('Renforcement', 'Fonction valeur')[parametres[joueur][2]])
            if parametres[joueur][2] == 1:  # apprentissage fonction valeur
                print('  ' + 'Epsilon-greedy')
                print('    ' + 'Facteur epsilon-greedy: ' + str(parametres[joueur][4][0]))
                print('    ' + 'Epsilon-greedy minimum: ' + str(parametres[joueur][4][1]))
                print('    ' + 'Facteur réduction epsilon-greedy: ' + str(parametres[joueur][4][2]))
                print('    ' + 'Période epsilon-greedy: ' + str(parametres[joueur][4][3]))
                print('    ' + 'Learning rate: ' + str(parametres[joueur][4][4]))

    print('Paramètres du jeu')
    print('  ' + '# allumettes en jeu: ' + str(parametres[0][0]))
    print('  ' + '# max allumettes à retirer: ' + str(parametres[0][1]))
    print('  ' + '# manches: ' + str(parametres[0][2]))

    for j in range(2):
        affichage_parametres_joueurs(j + 1)


def choix(borne_basse, borne_haute, texte):
    """ Fonction  permettant de choisir une réponse valide entre 2 bornes """

    reponse = -1
    while reponse < borne_basse or reponse > borne_haute:
        try:
            reponse = int(input(texte))
        except:
            pass
    return reponse


def initialisation(definir_parametres, parametres):
    """ Fonction  permettant de définir les paramètres initiaux du jeu  et des 2 joueurs """

    def definir_parametres_jeu():
        parametres[0][0] = choix(8, 100, "Nbre d'allumettes en jeu [8 - 100] ? : ")
        parametres[0][1] = choix(2, 5, "Nbre maximal d'allumettes à retirer [2 - 5] ? : ")
        parametres[0][2] = choix(1, 10e6, "Nbre maximal de manches [1 - 10e6] ? : ")

    def definir_parametres_joueur(joueur):
        parametres[joueur][0] = choix(0, 1, "Joueur " + str(joueur) + " [0: Humain] [1: IA] ? : ")
        if parametres[joueur][0] == 1:
            parametres[joueur][1] = choix(0, 3, "Mode IA " + str(
                joueur) + " [0:aléatoire][1:optimal][2:aléatoire/optimal][3:apprentissage] ? : ")
            if parametres[joueur][1] == 3:
                parametres[joueur][2] = choix(0, 1, "Mode apprentissage IA " + str(
                    joueur) + " [0:renforcement][1:fonction valeur] ? : ")
                if parametres[joueur][2] == 1:
                    definir_parametres_fvaleur(joueur)
            else:
                parametres[joueur][2] = None
            parametres[joueur][3] = "IA " + str(joueur)
        else:
            parametres[joueur][1] = None
            parametres[joueur][2] = None
            parametres[joueur][3] = input("Quel est le nom du joueur " + str(joueur) + " ? : ")

    def definir_parametres_fvaleur(joueur):

        if choix(0, 1, "[0: [1.0,0.05,0.996,5,0.001] ] ][1: paramètres spécifiques] ? : ") == 0:
            parametres[joueur][4] = [1.0, 0.05, 0.996, 5, 0.001]
        else:
            succes = False
            while succes == False:
                try:
                    t = list(parametres[joueur][4])
                    parametres[joueur][4][0] = float(input('Facteur e-greedy: '))
                    parametres[joueur][4][1] = float(input('e-greedy minimum: '))
                    parametres[joueur][4][2] = float(input('Facteur réduction e-greedy: '))
                    parametres[joueur][4][3] = int(input('Période e-greedy: '))
                    parametres[joueur][4][4] = float(input('Learning rate: '))
                    succes = True
                except:
                    parametres[joueur][4] = t  # on rétablit la liste des parametres e-greedy aux valeurs de départ

    ch = " "
    if definir_parametres:
        while ch != "f":
            ch = input("[pj:parametres jeu][j1:joueur 1][j2:joueur 2][t:tout][f:fin] ? : ")
            if ch == 'pj':
                definir_parametres_jeu()
            elif ch == 'j1':
                definir_parametres_joueur(1)
            elif ch == 'j2':
                definir_parametres_joueur(2)
            elif ch == 't':
                definir_parametres_jeu()
                definir_parametres_joueur(1)
                definir_parametres_joueur(2)

        affichage_parametres(parametres)


def pile_ou_face(type_joueur, nom_joueur):
    """ Fonction  permettant d'obtenir le résultat du pile ou face permettant de déterminer qui commence
    Si le joueur est humain, il doit entrer son choix, sinon le tirage est aléatoire
    Retourne True si le pari est identique au tirage aléatoire"""

    if type_joueur == 0:  # le joueur est un humain, il doit donner son pari
        pari = choix(1, 2, nom_joueur + " : pile [1] ou face [2] ? : ")
    else:
        pari = randint(1, 2)
    return pari == randint(1, 2)


def joueur_qui_a_la_main(joueur1_commence, nbre_coups):
    """ Détermine le joueur qui a la main """

    if nbre_coups % 2 != 0:
        if joueur1_commence:
            return 1
        else:
            return 2
    else:
        if joueur1_commence:
            return 2
        else:
            return 1


def update_epsilon_greedy(joueur, parametres, manche):
    """ Met à jour le facteur e-greedy en cas d'apprentissage par fonction de valeur """

    if manche % parametres[joueur][4][3] == 0:
        parametres[joueur][4][0] = max(parametres[joueur][4][0] * parametres[joueur][4][2], parametres[joueur][4][1])


def jouer(joueur, allumettes, parametres, boules, etats, historique):
    """ Fonction principale du jeu activée lors de chaque coup d'une manche
    Elle comporte deux sous-fonctions traitant le coup par une IA ou le coup par un humain
    """

    def coup_IA_PC(joueur, allumettes, max_allumettes, parametres, historique):  # Coup par une IA
        mode_IA = parametres[joueur][1]  # [0:aléatoire][1:optimal][2:aléatoire/optimal][3:apprentissage]
        mode_apprentissage_IA = parametres[joueur][2]  # [0:renforcement][1:fonction valeur]
        if mode_IA == 0:  # coup aléatoire
            coup = randint(1, min(max_allumettes, allumettes))
        elif mode_IA == 1:  # coup optimal
            # coup = max(allumettes % (max_allumettes + 1),1) # si multiple de max_allumettes+1 ==> coup = 1
            # pour laisser le plus de choix possible à l'adversaire
            coup = allumettes % (max_allumettes + 1)
            if coup == 0:
                coup = randint(1, min(max_allumettes, allumettes))
        elif mode_IA == 2:  # coup optimal/aléatoire
            coup = randint(1, min(max_allumettes, allumettes))  # aléatoire
            if randint(0, 1) and (
                    allumettes % (max_allumettes + 1) != 0):  # optimal et allumettes est multiple de max_allumettes + 1
                coup = allumettes % (max_allumettes + 1)
        elif mode_IA == 3 and mode_apprentissage_IA == 0:  # Apprentissage par enforcement
            urne = []
            # Remplissage d'une urne avec les boules de couleur: 0 représente boule verte/1
            # représente boule orange/2 représente boule rouge, etc.
            # Total boules =
            t = 0
            for i in range(parametres[0][1]):
                t += i

            for i in range(parametres[0][1]):
                urne += [i] * ceil(boules[joueur - 1][allumettes - 1][i] / t)
                # proportion de boules de chaque couleur arrondie au nbre sup - pour accélérer les calculs !
                # urne += [i] * boules[joueur - 1][allumettes - 1][i]
                # Mélange des boules dans l'urne - Mélange de Fisher-Yates
            for i in range(len(urne) - 1, 1, -1):
                j = randint(0, i)
                urne[j], urne[i] = urne[i], urne[j]
            # Tirage aléatoire d'une boule dans l'urne
            coup = urne[randint(0, len(urne) - 1)]
            # enregistrer le coup
            historique[joueur - 1].append((allumettes - 1, coup))  # coup et allumettes indicés sur 0
            coup += 1  # + 1 car listes indicées sur 0 si urne[..] = 0 => coup = 1 boule à retirer
        elif mode_IA == 3 and mode_apprentissage_IA == 1:  # Fonction de valeur
            # déterminer le type de coup en f() epsilon-greedy
            if random() < (parametres[joueur][4][0]):  # random génère un nombre aléatoire entre 0 et 1
                coup = randint(1, min(max_allumettes, allumettes))
                coup -= 1  # pour indexer sur 0
            else:  # exploitation
                valeur = 0
                # on cherche la plus petite valeur dans etats
                # pour amener l'adversaire sur celle-ci = position la + défavorable

                if allumettes - max_allumettes <= 0:  # l'adversaire obtient la récompense négative - 1
                    coup = allumettes
                else:
                    valeur = etats[joueur - 1][
                        allumettes - 2]  # valeur initiale correspondant à l'allumette suivant la position en cours
                    coup = 1  # initialisation au coup minimum
                    for i in range(allumettes - 1, allumettes - max_allumettes - 1,
                                   -1):  # test des positions pour trouver la plus petite valeur
                        # print('valeur testée: i = ',i,etats[0][i-1])
                        if etats[joueur - 1][i - 1] < valeur:
                            valeur = etats[joueur - 1][i - 1]
                            coup = allumettes - i
                coup -= 1
            historique[joueur - 1].append(allumettes - 1)  # coup et allumettes indicés sur 0
            coup += 1
            # + 1 pour la déduction des allumettes car listes indicées sur 0
        return coup

    def coup_humain(joueur, allumettes, parametres):  # Traitement du coup d'un humain
        return choix(1, min(max_allumettes, allumettes),
                     "Combien d'allumettes retires-tu " + parametres[joueur][3] + " ? : ")

    type_joueur = parametres[joueur][0]  # [0: Humain] [1: IA]
    max_allumettes = parametres[0][1]
    if type_joueur == 0:  # Humain joue
        return coup_humain(joueur, allumettes, parametres)
    else:
        return coup_IA_PC(joueur, allumettes, max_allumettes, parametres, historique)  # PC joue contre l'IA qui apprend


def update_listes_renforcement(joueur, parametres, boules, historique):
    """" Met à jour le nombre de boules de chaque type en cas d'apprentissage par renforcement """

    def test_boules_restantes():
        """" Si le joueur a perdu,, vérifie qu'il reste encore des boules pour une allumette """

        n = 0
        for i in range(len(boules[joueur_perdant - 1][allumette])):
            n += boules[joueur_perdant - 1][allumette][i]

        if n == 0:  # on réinitialise le nombre de boules
            if allumette == 0:
                boules[joueur_perdant - 1][allumette] = [2] + ([0] * (parametres[0][1] - 1))  #
            elif allumette == 1:
                boules[joueur_perdant - 1][allumette] = [2, 2] + ([0] * (parametres[0][1] - 2))  #
            else:
                boules[joueur_perdant - 1][allumette] = [2] * parametres[0][1]  #

    # Le joueur qui a perdu s'obtient par joueur % 2 + 1

    joueur_gagnant = joueur
    joueur_perdant = joueur % 2 + 1

    if parametres[joueur_gagnant][2] == 0:  # joueur qui a gagne joue par renforcement
        for i in range(len(historique[joueur_gagnant - 1])):
            allumette = historique[joueur_gagnant - 1][i][0]
            coup = historique[joueur_gagnant - 1][i][1]
            boules[joueur_gagnant - 1][allumette][coup] += 1
    if parametres[joueur_perdant][2] == 0:  # joueur qui a perdu joue par renforcement
        for i in range(len(historique[joueur_perdant - 1])):
            allumette = historique[joueur_perdant - 1][i][0]
            coup = historique[joueur_perdant - 1][i][1]
            boules[joueur_perdant - 1][allumette][coup] -= 1

            test_boules_restantes()


def update_listes_fvaleur(joueur, parametres, etats, historique):
    """" Met à jour la liste des valeurs calculées par la fonction de valeur """

    def transitions(j):
        for i in range(len(historique[j - 1]), 0, -1):
            if i == len(historique[j - 1]):  # dernier enregistrement de l'historique du joueur j
                etats[j - 1][historique[j - 1][i - 1]] += parametres[j][4][4] * (
                        recompense - etats[j - 1][historique[j - 1][i - 1]])  # r = 1
            else:
                etats[j - 1][historique[j - 1][i - 1]] += parametres[j][4][4] * (
                        etats[j - 1][historique[j - 1][i]] - etats[j - 1][historique[j - 1][i - 1]])

    # joueur qui a perdu s'obtient par joueur % 2 + 1

    joueur_gagnant = joueur
    joueur_perdant = joueur % 2 + 1

    if parametres[joueur_gagnant][2] == 1:  # joueur qui a gagne joue par fvaleur
        recompense = 1
        transitions(joueur_gagnant)

    if parametres[joueur_perdant][2] == 1:  # joueur qui a perdu joue par fvaleur
        recompense = -1
        transitions(joueur_perdant)


def affiche_jeu(allumettes, max_allumettes):
    """" Affiche le jeu sous la forme de # "allumettes" barres verticales - Insère un espace supplémentaire entre
    les groupes de max_allumettes + 1 pour faciliter la compréhension de l'algorithme de réussite"""

    jeu = ''
    for j in range(allumettes):
        jeu = jeu + "| "
        if (j + 1) % (max_allumettes + 1) == 0:
            jeu = jeu + ' '
    print(jeu)


def mmob(liste, moyenne):
    """" Calcule la moyenne mobile des valeurs  contenues dans la liste """

    mm = 0
    for i in liste:
        mm += i
    return mm / moyenne


def initialiser_matrice(type_matrice, j1, j2, alu_en_jeu, max_alu):
    """ retourne une matrice de matrices destinée à contenir, selon le type :
    -   les données d'apprentissage par renforcement pour les 2 joueurs ou 1 seul
        le nombre de boules de chaque type par allumette
        Rem: Le nombre de boules est initialement de 2 par possibilité de retrait sauf pour les premières allumettes
        afin de tenir compte des coups impossibles
    -   Les valeurs des états calculés par la fonction de valeur (Bellman) pour les 2 joueurs ou 1 seul

    type_matrice peut prendre 2 valeurs : "renforcement ou "fonction de valeur"

    j1 et j2 sont des valeurs booléennes qui déterminent si les joueur 1 et/ou 2 sont des IA

    la matrice d'apprentissage par renforcement est initialement de la forme suivante pour 8 allumettes en jeu avec
    un retrait max de 3 allumettes :
    [[[2, 0, 0], [2, 2, 0], [2, 2, 2], [2, 2, 2], [2, 2, 2], [2, 2, 2], [2, 2, 2], [2, 2, 2]],
    [[2, 0, 0], [2, 2, 0], [2, 2, 2], [2, 2, 2], [2, 2, 2], [2, 2, 2], [2, 2, 2], [2, 2, 2]]] pour IA 1 et IA 2

    la matrice d'apprentissage par fonction de valeur est initialement de la forme suivante pour 8 allumettes en jeu :
    [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]
    """

    matrice = []
    if type_matrice == 'renforcement':  # matrice pour apprentissage par renforcement
        matrice = [[[2] * max_alu for _ in range(alu_en_jeu)], [[2] * max_alu for _ in range(alu_en_jeu)]]
        for i in range(max_alu - 1):  # enlever les solutions impossibles
            matrice[0][i] = ([2] * (i + 1)) + ([0] * (max_alu - i - 1))
            matrice[1][i] = ([2] * (i + 1)) + ([0] * (max_alu - i - 1))
    elif type_matrice == 'fonction de valeur':  # matrice des états pour apprentissage par fonction de valeur
        matrice = [[0 for _ in range(alu_en_jeu)], [0 for _ in range(alu_en_jeu)]]

    if j1 and not j2:
        del matrice[1]
        matrice.append([])
    elif j2 and not j1:
        del matrice[0]
        matrice.insert(0, [])
    return matrice


""" ********************************** CODE PRINCIPAL *********************************************** 

*********************************** Paramètres initiaux de jeu **************************************

[0][0] allumettes en jeu 
[0][1] max allumettes a retirer
[0][2] nbre de manches 

[1][0] Type joueur 1 [0: Humain] [1: IA] 
[1][1] Mode IA 1 [None: humain][0:aléatoire][1:optimal][2:aléatoire/optimal][3:apprentissage]
[1][2] Mode apprentissage IA 1 [None: humain] [0:renforcement][1:fonction valeur]
[1][3] Nom Joueur 1 [IA 1] ou [Nom joueur humain]
[1][4][0] epsilon-greedy 
[1][4][1] epsilon-greedy minimum
[1][4][2] Facteur de réduction epsilon-greedy
[1][4][3] Période epsilon_greedy
[1][4][4] learning_rate 

[2][0] Type joueur 2 [0: Humain] [1: IA] 
[2][1] Mode IA 2 [none: humain][0:aléatoire][1:optimal][2:aléatoire/optimal][3:apprentissage]
[2][2] Mode apprentissage IA 2 [None: humain] [0:renforcement][1:fonction valeur]
[2][3] Nom Joueur 2 [IA 2] ou [Nom joueur humain] 
[2][4][0] epsilon-greedy 
[2][4][1] epsilon-greedy minimum
[2][4][2] Facteur de réduction epsilon-greedy
[2][4][3] Période epsilon_greedy
[2][4][4] learning_rate 

"""

# ****************             Quelques configurations 'clé sur porte' *****************************

# joueur 1 = IA jouant de manière optimale / joueur 2 = IA apprenant par renforcement
parametres = [[12, 3, 1000], [1, 1, None, "IA 1", [1.0, 0.05, 0.996, 5, 0.001]],
                         [1, 3, 0, "IA 2", [1.0, 0.05, 0.996, 5, 0.001]]]

# joueur 1 = humain / joueur 2 = IA jouant de manière optimale
# parametres = [[12, 3, 5], [0, None, None, "", [1.0, 0.05, 0.996, 5, 0.001]],
#                           [1, 1, None, "IA 2", [1.0, 0.05, 0.996, 5, 0.001]]]

# joueur 1 = humain / joueur 2 = humain
# parametres = [[12,3,5],[0,None,None,"",[1.0,0.05,0.996,5,0.001]],
#                       [0,None,None,"",[1.0,0.05,0.996,5,0.001]]]

# joueur 1 = optimal / joueur 2 = apprentissage par fonction de valeur
# parametres = [[12, 3, 20000], [1, 1, None, "IA 1", [1.0, 0.05, 0.996, 20, 0.001]],
#                               [1, 3, 1, "IA 2", [1.0, 0.05, 0.996, 20, 0.001]]]

# joueur 1 = apprentissage par fonction de valeur / joueur 2 = apprentisage par renforcement
# parametres = [[12,3,20000],[1,3,1,"IA 1",[1.0, 0.05, 0.996, 20, 0.001]],
#                            [1,3,0,"IA 2",[1.0, 0.05, 0.996, 20, 0.001]]]


initialisation(input("Paramètres par défaut [o][n] ? : ") == "n", parametres)

allumettes_en_jeu = parametres[0][0]  # nbre d'allumettes mises en jeu
max_allumettes = parametres[0][1]  # nbre max d'allumettes pouvant être retirées
nbre_manches = parametres[0][2]  # nbre de manches à jouer
manche = 0  # manche en cours
scores = [0, 0, 0, 0, 0, 0]
# les scores absolus des joueurs + MMob des scores des 10 dernières manches + manches à partir
# desquelles on atteint les 50% de réussite

histo_victoires = [[], []]  # Histo 10 dernières manches

# initialisation apprentissage par renforcement on crée une liste par joueur qui joue selon ce mode pour chaque
# joueur créé, on crée, par allumette, une liste [2,2,2] pour représenter les boules vertes, oranges et rouges
# !!! ne # pas creer les listes de cette manière : boules = [[2,2,2]]*8 - Si on modifie un élément, tous les éléments
# correspondants des autres listes [2,2,2] sont modifiés car en fait il s'agit de la même liste  !!!
# cela donne : boules[[[2,0,0],[2,2,0],[2,2,2],[2,2,2], ... [2,0,0]],[[2,2,0] ... [2,2,2]]]
# boules[0][0][2] ==> joueur 1 (index 0), allumette 1 (index 0), #boules rouges (index 2) ...

boules = initialiser_matrice('renforcement', parametres[1][2] == 0, parametres[2][2] == 0, allumettes_en_jeu, max_allumettes)

# initialisation apprentissage par fonction de valeur
# on crée une liste par joueur qui joue selon ce mode
# pour chaque joueur créé, on crée par allumette, un nombre (0 initialement) pour représenter l'état correspondant 

etats = initialiser_matrice('fonction de valeur', parametres[1][2] == 1, parametres[2][2] == 1, allumettes_en_jeu,
                     max_allumettes)

for j in range(2):
    if parametres[j + 1][0] == 0:  # demander le nom du joueur humain
        parametres[j + 1][3] = input('Quel est ton nom joueur ' + str(j + 1) + ' ? : ')

affichage_parametres(parametres)

joueur1_commence = pile_ou_face(
    parametres[1][0], parametres[1][3])  # déterminer si le joueur 1 commence / parametres[1][0] = type de joueur

affichage_jeu = parametres[1][0] == 0 or parametres[2][0] == 0 or input("Affichage du jeu [o][n] ? : ") == 'o'

while manche < nbre_manches:  # Début du jeu
    manche += 1  # manche en cours
    nbre_allumettes_a_retirer = 0  # nombre d'allumettes à retirer par le joueur ou l'IA
    allumettes = allumettes_en_jeu  # initialiser le nombre d'allumettes en jeu
    nbre_coups = 0

    # listes devant contenir l'historique des coups des joueurs 1 et 2 - utilisées lors d'un apprentissage
    historique = [[], []]

    while allumettes > 0:
        if affichage_jeu:
            affiche_jeu(allumettes, max_allumettes)
        nbre_coups += 1
        joueur = joueur_qui_a_la_main(joueur1_commence, nbre_coups)

        nbre_allumettes_a_retirer = jouer(joueur, allumettes, parametres, boules, etats,
                                          historique)  # on retire le nombre d'allumettes

        allumettes -= nbre_allumettes_a_retirer

        if affichage_jeu:
            print(str(parametres[joueur][3]) + ' retire ' + str(nbre_allumettes_a_retirer) + ' allumette(s)')

        if allumettes == 0:  # la manche est finie
            scores[joueur - 1] += 1

            histo_victoires[joueur - 1].append(1)  # historique victoires/défaites joueur gagant
            histo_victoires[joueur % 2].append(0)  # historique victoires/défaites joueur perdant

            if len(histo_victoires[0]) > 10:
                histo_victoires[0].pop(0)  # supprime le premier élément de la liste des victoires du joueur 1
                histo_victoires[1].pop(0)  # supprime le premier élément de la liste des victoires du joueur 2

            if len(histo_victoires[0]) == 10:  # Calcul de la Mmob sur 10 manches
                scores[2] = 100 * mmob(histo_victoires[0], 10)  # mmob exprimée en %
                scores[3] = 100 * mmob(histo_victoires[1], 10)  # mmob exprimée en %

            for j in range(2, 4):  # détermination de la manche à partir de laquelle les 50% de victoires sont acquis
                if scores[j + 2] == 0:
                    if scores[j] >= 50:
                        scores[j + 2] = manche
                else:
                    if scores[j] < 50:
                        scores[j + 2] = 0

            if parametres[1][2] == 0 or parametres[2][2] == 0:
                update_listes_renforcement(joueur, parametres, boules, historique)

            if parametres[joueur][2] == 1:
                update_epsilon_greedy(joueur, parametres, manche)  # update e-greedy du joueur
            if parametres[joueur % 2 + 1][2] == 1:  # update e-greedy de l'autre joueur
                update_epsilon_greedy(joueur % 2 + 1, parametres, manche)

            if parametres[1][2] == 1 or parametres[2][2] == 1:
                update_listes_fvaleur(joueur, parametres, etats, historique)

            if parametres[1][0] == 0 or parametres[2][0] == 0:  # un humain au moins joue

                print()
                print("Scores :", scores)
                print()

    joueur1_commence = not (joueur1_commence)  # inverser le joueur pour la prochaine manche

# ******************** Fin de la partie ***********************************************

# ******************** Affichage des résultats ****************************************

print()
for j in range(2):
    print("Joueur " + str(j + 1) + " : " + parametres[j + 1][3])
    print('  Type de joueur           : ', ('Humain', 'IA')[parametres[j + 1][0]])
    if parametres[j + 1][0] == 1:
        print('  Mode de jeu              : ',
              ('Aléatoire', 'Optimal', 'Aléatoire/Optimal', 'Apprentissage')[parametres[j + 1][1]])
        if parametres[j + 1][1] == 3:
            print("  Type d'apprentissage     : ", ('Renforcement', 'Fonction valeur')[parametres[j + 1][2]])
            if parametres[j + 1][2] == 1:
                print("  epsilon-greedy           : ", parametres[j + 1][4])
    print("  Victoires                : ", scores[j])
    print("  Moyenne de victoires (%) : ", scores[j + 2])
    if parametres[j + 1][1] == 3:
        print("  Manches d'apprentissage  : ", scores[j + 4])
    print()

# impression du nombre de boules par allumette s'il y a au moins un apprentissage par renforcement

for j in range(2):
    if parametres[j + 1][2] == 0:
        print('*** Joueur ' + str(j + 1) + ' ***')
        print()
        for i in range(allumettes_en_jeu):
            print('allumette', i + 1, boules[j][i])
    print()

print()

# impression de la valeur des états s'il y a au moins un apprentissage par fonction de valeur

for j in range(2):
    if parametres[j + 1][2] == 1:
        print('*** Joueur ' + str(j + 1) + ' ***')
        print()
        for i in range(allumettes_en_jeu):
            print('état', i + 1, etats[j][i])
    print()

print()
