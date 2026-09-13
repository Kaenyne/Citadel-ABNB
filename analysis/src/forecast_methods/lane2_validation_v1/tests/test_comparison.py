import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location('lane2_validation', Path(__file__).resolve().parents[1]/'run.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def frame():
    return pd.DataFrame([dict(method='toy',object='x',target='r',window='W1',prior_basis='PIT',
                              n=14,rmse=50.0,beats_naive=True, optional=np.nan)])


def test_float_noise_accepted():
    a,b=frame(),frame(); b.loc[0,'rmse'] += 1e-12
    assert module.compare_frames(a,b)['max_abs_difference'] < 1e-9


@pytest.mark.parametrize('column,value', [('rmse',50.000001),('n',13),('beats_naive',False),('optional',1.0)])
def test_material_or_discrete_change_rejected(column,value):
    a,b=frame(),frame(); b.loc[0,column]=value
    with pytest.raises(AssertionError): module.compare_frames(a,b)


def test_missing_key_rejected():
    with pytest.raises(AssertionError): module.compare_frames(frame(),frame().iloc[0:0])


def test_duplicate_key_rejected():
    with pytest.raises(AssertionError): module.compare_frames(frame(),pd.concat([frame(),frame()]))


def test_new_method_only_allowed_explicitly():
    new=frame(); new.loc[0,'method']='new'
    b=pd.concat([frame(),new])
    with pytest.raises(AssertionError): module.compare_frames(frame(),b)
    assert module.compare_frames(frame(),b,allow_extra=True)['added_rows']==1


def test_numeric_infinity_rejected():
    b=frame(); b.loc[0,'rmse']=np.inf
    with pytest.raises(AssertionError): module.compare_frames(frame(),b)
