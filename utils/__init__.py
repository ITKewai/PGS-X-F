"""
DA VERIFICARE:
# TODO: non usare i max_ ma leggere dal file


POSSIBILI
# TODO: rendere questo programma un server web anche cosi si integra nell'hmi ,fare vedere allarmi a lato cliccabili per errori console

A TEMPO PERSO:
# TODO: in base a indirizzo ip scheda rete imposta ip plc e scarica config

DIFFICILE:
# TODO: verifiche (verificare che per i reset pressostati si scende solo con il joystick, se ci sono digitali nel fb_err)


# TODO: controllo pompe, master con slave e left con right
# TODO: feedback dei rulli ratio deve essere 1
# TODO: verificare DEFAULT SPEED e mMAXVELPERC nin control negli assi se è diverso da 100 e 100
# TODO: se sshock abscorver è attivo devo avere anche disable nei param con di che è SW
# TODO: check se file capacita su pulpito ha commessa giusta, se indice azzeramento corrisponde al digitale di azzeramento
# TODO: controllo che feedback val max e min siano coerenti 40T
# TODO: controllare che se presente feedback encoder su espulsore deve rimanere tipo XXX cosi non perde quota una volta spenta e acceso
# TODO: verificare che la numerazione allarmi sia corretta (COD)
# TODO: CONOTROLLARE CHE FINECORSA MAX LEFT E RIGHT SIANO COERENTI
# TODO: se assi SP attivi controllare che siano in function
# TODO: spezzare in piu funzioni ad esempio get axis ecc
# TODO: output valmax1 valmax2 a 100.00 sugli output e gli altri 20 40 60 80
# TODO: controllare versione plc via http (/Portal/Portal.mwsl?PriNav=Online&SecNav=Ident)
# TODO: da fare controllo su control di ogni asse bwslow2
# TODO: vedere che è configurata la luce waitnig for start
# TODO: controllo stessi imput per più input assi (esempio 2 assi con stesso input)
# todo: paraletri supporto a croce di tipo lung
# TODO: se asse 42 attivo allora reset tipo const
# TODO: printare tutti i DI delayed con nome e quanto tempo sono impostati per sapere se i PS laterali hanno un ritardo attivo o no
"""