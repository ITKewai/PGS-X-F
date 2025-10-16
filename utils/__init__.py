"""
# TODO: comando refresh (a mano se no una volta lanciato sovrascrive config_old)
# TODO: rinominare config > config_old
# TODO: controllo differenze config > config_old
# TODO: verifiche (verificare che per i reset pressostati si scende solo con il joystick, se ci sono digitali nel fb_err)
# TODO: veridicare che la variabile di sistema sia su "SI" il booleano in caso di assi se no non VA (L LL L0 EEC)
# TODO: caricare tutte le informazioni asse per asse
# TODO: controllo per vedere se un uscita DO o AO è usata su piu assi
# TODO: controllo se c è un SYSTEM di usasse usato ma c'è il FLAG su NO
# TODO: controllo safety interlock sgancio chiusura, non deve esserci Droll L (o la system)
# TODO: ricarca Freee daindici sbagliati
# TODO:  ricerca che negli assi non rimangono indici in opt param
# TODO: controllo che la quota H sia maggiore di HH nel pinzaggio se no non apri sgancio in automatico
# TODO: controllare che sui rulli laterali MAN SP UP sia disattivo
# TODO: controllo che tutti i system usati degli assi abbiamo "YES"al flag se no non vanno
# TODO: notificare se le termiche sono state inserite nei motori (no resistanza(
# TODO: nella ricerca dei DI ci sono anche RECICLEVALVIND dei motori
# TODO: tipo lunghezza asse uguale a lunghezza feedback
# TODO: supporti laterali feedback in GRAD anche dentro asse  (e in params '-')
# TODO: verifica che uso variabili system per motori
# TODO: verifica che indirizzi KE1/KE4 non sono scritti
# TODO: va in errore se cerco system si patcha separando la ricerca
# TODO: ricerca nelle expression
# TODO: verificare che la velocità dei rulli sia ugale in control per master e slave
# TODO: verificare che master mult sia 5 e vmin infeiriore  a 3
# TODO: quota di reset maggiore a quota apertura sgancio
#TODO: TEST FINALE RICERCA IN OGNI CAMPO VISIBILE
# TODO: ricerca di con stesso indirizzo
# TODO: warning se expr calc e tipo non calc
"""