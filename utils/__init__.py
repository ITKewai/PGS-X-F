"""
DA VERIFICARE:
# TODO: non usare i max_ ma leggere dal file


POSSIBILI
# TODO: rendere questo programma un server web anche cosi si integra nell'hmi ,fare vedere allarmi a lato cliccabili per errori console

A TEMPO PERSO:
# TODO: in base a indirizzo ip scheda rete imposta ip plc e scarica config
# TODO: spezzare in piu funzioni ad esempio get axis ecc
# TODO: check se file capacita su pulpito ha commessa giusta, se indice azzeramento corrisponde al digitale di azzeramento

DIFFICILE:
# TODO: verifiche (verificare che per i reset pressostati si scende solo con il joystick, se ci sono digitali nel fb_err)
# TODO: printare i safety interlock down up

# TODO: controllare che se presente feedback encoder su espulsore deve rimanere tipo XXX cosi non perde quota una volta spenta e acceso
# TODO: se assi SP attivi controllare che siano in function nel pinzaggio

# TODO: controllare versione plc via http (/Portal/Portal.mwsl?PriNav=Online&SecNav=Ident)
# todo: paraletri supporto a croce di tipo lung
# TODO: se asse 42 attivo allora reset tipo const
# TODO: printare tutti i DI delayed con nome e quanto tempo sono impostati per sapere se i PS laterali hanno un ritardo attivo o no
# TODO: vedere se il bit "STEP" è attivo in params
# TODO: VEDERE TIPO DI RESET se diverso da calc
# todo: IN CONTROLLO INPUT SE VALORE NEGATIVO allora è un JS il vmin non deve essere 0 ma qualcos altro sotto i 500/1000

# TODO: se una delle fotocellule o laser scanner allore parametro FULL AUTO si

# TODO: salvare invece di config old config_cXXXX_vPLC_SAVEMAP

# TODO: v27,28 ECCEZZZIONI

"""