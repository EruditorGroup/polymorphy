ANY  = 'ANY'  # любая граммема


POS  = 'POS'  # часть речи
# ----------
NOUN = 'NOUN' # имя существительное
ADJF = 'ADJF' # имя прилагательное (полное)
ADJS = 'ADJS' # имя прилагательное (краткое)
COMP = 'COMP' # компаратив
VERB = 'VERB' # глагол (личная форма)
INFN = 'INFN' # глагол (инфинитив)
PRTF = 'PRTF' # причастие (полное)
PRTS = 'PRTS' # причастие (краткое)
GRND = 'GRND' # деепричастие
NUMR = 'NUMR' # числительное
ADVB = 'ADVB' # наречие
NPRO = 'NPRO' # местоимение-существительное
PRED = 'PRED' # предикатив
PREP = 'PREP' # предлог
CONJ = 'CONJ' # союз
PRCL = 'PRCL' # частица
INTJ = 'INTJ' # междометие


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


ANim = 'ANim' # одушевленность
# ----------
anim = 'anim' # одушевлённое
inan = 'inan' # неодушевлённое


ABSTRACT_GRAMMEMES = {
    POS:  [NOUN, ADJF, INFN, VERB],
    NMbr: [sing, plur],
    GNdr: [masc, femn, neut],
    CAse: [nomn, gent, datv, accs, ablt, loct, voct],
    ANim: [anim, inan],
}
