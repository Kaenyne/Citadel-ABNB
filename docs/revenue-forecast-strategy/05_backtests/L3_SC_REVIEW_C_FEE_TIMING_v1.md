# SC-C — monthly fee-triplet requirement clarification

Reviewer cohort_fx · author nclh · 2026-09-14. Narrow follow-up after the broader v2 independent closure; no current data, numerical result or status defect.

The FEE_CAPTURE gap says the panel must exist on all six scheduled dates. That overstates the requirement for each individual monthly theta row. The frozen `L3_FEE_PREREG_v1.md` separates September 14/16/18 from October 12/14/16 and disallows automatic monthly pooling. The original fee runner estimates each named wave independently with its appropriate treatment/comparator definition.

Required clarification: each monthly theta needs its own complete three-date triplet and monthly design gates; both triplets are necessary only to estimate both monthly outputs. September need not await October. Both estimates remain unavailable in the currently reviewed source, and the inventory date remains unchanged. No collector should be started or awaited, and no missing value should become zero.

Author was asked to update gap wording in a new metadata-only output, preserve earlier versions and bind a focused regression/receipt. This correction does not reopen the source/preservation/FX/hedge audit or change the accepted original 1,187 classifications. Final review should bind the corrected output manifest after verifying the two fee-row requirements and unchanged source cells.

## RESUME

Author supplies the corrected canonical version; reviewer checks the monthly wording and source/value preservation, then supplies an addendum for lead's final acceptance manifest.
