"""
DA VERIFICARE:
# TODO: non usare i max_ ma leggere dal file


POSSIBILI
# TODO: notificare se le termiche sono state inserite nei motori (no resistanza)

# TODO: cerifica bug RI vedere se tutti i campi o la maggiorpare di Enabled è diverso da -1

# TODO: warning se expr calc e tipo non calc
# TODO: verificare che input non ha seq imposto
# TODO: rendere questo programma un server web anche cosi si integra nell'hmi ,fare vedere allarmi a lato cliccabili per errori console

A TEMPO PERSO:
# TODO: in base a indirizzo ip scheda rete imposta ip plc e scarica config
# TODO: verifiche (verificare che per i reset pressostati si scende solo con il joystick, se ci sono digitali nel fb_err)
# TODO: creazione file json con flag per attivare o disattivare parti dei controlli

# TODO: controllo pompe, master con slave e left con right
# TODO: feedback dei rulli ratio deve essere 1
# TODO: sistemar ricerca duplicati perchp non va
# TODO: ricerca free mi trova qualcosa in ANA1 - output: [1,2,-1,57,56,-1,-1,-1,-1,-1,-1,-1,-1,-1,300,900,300,900,0,0,0,0,0,100,0,100,0,0,20,20,40,40,60,60,80,80,100,100,0,0,20,20,40,40,60,60,80,80,100,100]
# TODO: verificare DEFAULT SPEED e mMAXVELPERC nin control negli assi se è diverso da 100 e 100

ASTER MULT impostato a 1.7 diverso da 5.0
⚠️ [4]AXIS_4 ha il parametro MASTER DELTAMIN impostato a 2.0 inveriore a 2.0
⚠️ [5]VS ha il parametro MAX SPEED (BW) impostato a 108.33299 maggiore di
# TODO: se sshock abscorver è attivo devo avere anche disable nei param con di che è SW
# TODO: check se file capacita su pulpito ha commessa giusta, se indice azzeramento corrisponde al digitale di azzeramento
"""