POS  = 'POS'  # часть речи
# ----------
NOUN = 'NOUN' # существительное
ADJF = 'ADJF' # прилагательное
INFN = 'INFN' # глагол-инфинитив
VERB = 'VERB' # глагол в личной форме

NMbr = 'NMbr' # число
# ----------
sing = 'sing' # единственное
plur = 'plur' # множественное

GNdr = 'GNdr' # пол
# ----------
masc = 'masc' # мужской
femn = 'femn' # женский
neut = 'neut' # средний

CAse = 'CAse' # падеж
# ----------
nomn = 'nomn' # именительный
gent = 'gent' # родительный
datv = 'datv' # дательный
accs = 'accs' # винительный
ablt = 'ablt' # творительный
loct = 'loct' # предложный
voct = 'voct' # звательный

ANY  = 'ANY'  # любая граммема

ABSTRACT_GRAMMEMES = {
    POS:  [NOUN, ADJF, INFN, VERB],
    NMbr: [sing, plur],
    GNdr: [masc, femn, neut],
    CAse: [nomn, gent, datv, accs, ablt, loct, voct]
}