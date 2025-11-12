"""



POSSIBILI
# TODO: notificare se le termiche sono state inserite nei motori (no resistanza)
# TODO: non usare i max_ ma leggere dal file
# TODO: controllare che allarmi siano safetystop
# TODO: verificare che master mult sia 5 e vmin infeiriore  a 3
# TODO: cerifica bug RI vedere se tutti i campi o la maggiorpare di Enabled è diverso da -1
# TODO: verifica che indirizzi KE1/KE4 non sono scritti
# TODO: verificare che i parametri archimetro config>check mesurment non siano LUNG
# TODO: warning se expr calc e tipo non calc
# TODO: verificare che input non ha seq imposto

# TODO: rendere questo programma un server web anche cosi si integra nell'hmi ,fare vedere allarmi a lato cliccabili per errori console
INCERTI:
# TODO: va in errore se cerco system si patcha separando la ricerca
# TODO: TEST FINALE RICERCA IN OGNI CAMPO VISIBILE

A TEMPO PERSO:
# TODO: in base a indirizzo ip scheda rete imposta ip plc e scarica config
# TODO: verifiche (verificare che per i reset pressostati si scende solo con il joystick, se ci sono digitali nel fb_err)
# TODO: creazione file json con flag per attivare o disattivare parti dei controlli
# TODO: [ASSE 10] TILT
#   ⚠️  Flag HH disattivo ma HH=SYS è impostato/usato
#     ↳ Axes	→	[10]TILT	→	HH
#         ↳ IO	→	DI	→	[99] TopRollRotation RI Enable Count	→	Expr	→	N0
#         ↳ IO	→	DI	→	[100] TopRollRotation RI Reset	→	Expr	→	N0
#         ↳ IO	→	DI	→	[307] None	→	Expr	→	N0
#         ↳ IO	→	DI	→	[308] None	→	Expr	→	N0 fuori indice???

⚠️  Duplicati trovati in DI:
   → PNET 0.3   → [64] EMERGENCY RESET PB, [272] EMERGENCY RESET PB
   272 NON ESISTE

# TODO: controllo pompe, master con slave e left con right
# TODO: feedback dei rulli ratio deve essere 1
# TODO: controllo bypass attivi negli assi ma non configurati
# TODO: sistemar ricerca duplicati perchp non va
# TODO: ricerca free mi trova qualcosa in ANA1 - output: [1,2,-1,57,56,-1,-1,-1,-1,-1,-1,-1,-1,-1,300,900,300,900,0,0,0,0,0,100,0,100,0,0,20,20,40,40,60,60,80,80,100,100,0,0,20,20,40,40,60,60,80,80,100,100]
# TODO: verificare DEFAULT SPEED e mMAXVELPERC nin control negli assi se è diverso da 100 e 100
# TODO: verificare se c è settato GOLDTORUNTYPE nell asse
# TODO: controllo che LATSUPQ4 è 1 e LATSUPQ0 è minore o uguale al SUP dei supporti laterali, controllare che i lavlori poi siano LATSUPQ0 > LATSUPQ1 > LATSUPQ2 > LATSUPQ3 > LATSUPQ4

"""