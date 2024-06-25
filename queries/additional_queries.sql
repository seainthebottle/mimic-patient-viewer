CREATE INDEX admission_idxs1 ON mimiciv_hosp.admissions(subject_id)

CREATE INDEX labevents_idxs1 ON mimiciv_hosp.labevents(hadm_id)
CREATE INDEX labevents_idxs2 ON mimiciv_hosp.labevents(subject_id)
CREATE INDEX labevents_idxs3 ON mimiciv_hosp.labevents(charttime)
CREATE INDEX labevents_idxs4 ON mimiciv_hosp.labevents(itemid)

CREATE INDEX emar_idxs1 on mimiciv_hosp.emar(hadm_id)
CREATE INDEX emar_idxs2 on mimiciv_hosp.emar(charttime)
CREATE INDEX emar_idxs3 ON mimiciv_hosp.emar(emar_id, emar_seq)
CREATE INDEX emar_detail_idxs1 ON mimiciv_hosp.emar_detail(emar_id, emar_seq)

CREATE INDEX poe_idxs1 on mimiciv_hosp.poe(hadm_id)

CREATE INDEX chartevents_idxs1 ON mimiciv_icu.chartevents(hadm_id)
CREATE INDEX chartevents_idxs2 on mimiciv_icu.chartevents(subject_id)
CREATE INDEX chartevents_idxs3 on mimiciv_icu.chartevents(stay_id)
CREATE INDEX chartevents_idxs4 on mimiciv_icu.chartevents(charttime)
CREATE INDEX chartevents_idxs5 on mimiciv_icu.chartevents(itemid)

CREATE INDEX outputevents_idxs1 on mimiciv_icu.outputevents(subject_id)
CREATE INDEX outputevents_idxs2 on mimiciv_icu.outputevents(charttime)
CREATE INDEX outputevents_idxs3 on mimiciv_icu.outputevents(stay_id)

CREATE INDEX discharge_idxs1 on mimiciv_note.discharge(hadm_id)