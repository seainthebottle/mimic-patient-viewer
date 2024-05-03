CREATE INDEX chartevents_idxs1 ON mimiciv_icu.chartevents(hadm_id)
CREATE INDEX chartevents_idxs2 on mimiciv_icu.chartevents(subject_id)
CREATE INDEX labevents_idxs1 ON mimiciv_hosp.labevents(hadm_id)
CREATE INDEX outputevents_idxs1 on mimiciv_icu.outputevents(subject_id)