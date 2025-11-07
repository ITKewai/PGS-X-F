"""



POSSIBILI
# TODO: notificare se le termiche sono state inserite nei motori (no resistanza)

# TODO: controllare che allarmi siano safetystop
# TODO: verificare che master mult sia 5 e vmin infeiriore  a 3

# TODO: verifica che indirizzi KE1/KE4 non sono scritti

# TODO: warning se expr calc e tipo non calc
# TODO: verificare che input non ha seq imposto

# TODO: rendere questo programma un server web anche cosi si integra nell'hmi ,fare vedere allarmi a lato cliccabili per errori console
INCERTI:
# TODO: va in errore se cerco system si patcha separando la ricerca
# TODO: TEST FINALE RICERCA IN OGNI CAMPO VISIBILE

A TEMPO PERSO:
# TODO: in base a indirizzo ip scheda rete imposta ip plc e scarica config
# TODO: verifiche (verificare che per i reset pressostati si scende solo con il joystick, se ci sono digitali nel fb_err)

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
"""