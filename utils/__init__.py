"""
NON POSSIBILI
# TODO: verifiche (verificare che per i reset pressostati si scende solo con il joystick, se ci sono digitali nel fb_err)


POSSIBILI
# TODO: controllo safety interlock sgancio chiusura, non deve esserci Droll L (o la system)
# TODO: ricerca che negli assi non rimangono indici in opt param
# TODO: controllo che la quota H sia maggiore di HH nel pinzaggio se no non apri sgancio in automatico
# TODO: controllare che sui rulli laterali MAN SP UP sia disattivo
# TODO: notificare se le termiche sono state inserite nei motori (no resistanza(
# TODO: tipo lunghezza asse uguale a lunghezza feedback
# TODO: supporti laterali feedback in GRAD anche dentro asse  (e in params '-')
# TODO: verifica che uso variabili system per motori
# TODO: verifica che indirizzi KE1/KE4 non sono scritti
# TODO: verificare che la velocità dei rulli sia ugale in control per master e slave
# TODO: verificare che master mult sia 5 e vmin infeiriore  a 3
# TODO: quota di reset maggiore a quota apertura sgancio
# TODO: ricerca di con stesso indirizzo
# TODO: warning se expr calc e tipo non calc
# TODO: verificare che input non ha seq imposto

# TODO: verificare che un input non sia usato in piu assi
# TODO: verificare che un uput non sia in piu assi
# TODO: verificare che un funaxis non siano indici su piu assi
# TODO: ricerca input o output o feedback
# TODO: rendere questo programma un server web anche cosi si integra nell'hmi ,fare vedere allarmi a lato cliccabili per errori console

# TODO: dailytotauto possono essere anche AI AO ?
INCERTI:
# TODO: va in errore se cerco system si patcha separando la ricerca
#TODO: TEST FINALE RICERCA IN OGNI CAMPO VISIBILE

"""