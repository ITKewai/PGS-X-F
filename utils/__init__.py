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
@ TODO:  ricerca che negli assi non rimangono indici in opt param
# TODO: controllo che la quota H sia maggiore di HH nel pinzaggio se no non apri sgancio in automatico
@# TODO: controllare che sui rulli laterali MAN SP UP sia disattivo
TODO: controllo che tutti i system usati degli assi abbiamo "YES"al flag se no non vanno
TODO: notificare se le termiche sono state inserite nei motori (no resistanza(
TODO: nella ricerca dei DI ci sono anche RECICLEVALVIND dei motori
TODO: tipo lunghezza asse uguale a lunghezza feedback
TODO: supporti laterali GRAD

"""