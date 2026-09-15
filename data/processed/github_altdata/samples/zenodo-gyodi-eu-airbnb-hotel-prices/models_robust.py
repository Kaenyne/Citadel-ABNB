from itertools import product
import pandas as pd
import numpy as np
import pysal as ps
from datetime import datetime
from pyproj import Proj
import pyproj


def reg_results(r, characteristics, r_stat='t', r_name='OLS'):
    return {**characteristics, **{
                    'type': r_name,
                    'diag_aic': r.aic,
                    'diag_loglik': r.logll
                },
                **dict(zip(['coef_' + x for x in r.name_x], [x[0] for x in r.betas])),
                **dict(zip(['std_err_' + x for x in r.name_x], r.std_err)),
                **dict(zip(['p_value_' + x for x in r.name_x], [x[1] for x in
                                                                (r.t_stat if r_stat == 't' else r.z_stat)]))
                }

def create_weights(kd, robust):
    if not robust:
        wnns = {str(x): ps.lib.weights.KNN(kd, x, p=2) for x in [10]}
    else:
        wnns = {**{str(x): ps.lib.weights.KNN(kd, x, p=2) for x in [5, 10, 25, 50]}, **{
            'distance_{}'.format(x): ps.lib.weights.DistanceBand(kd, threshold=x, p=2) for x in [500, 1000]}}
    for k in wnns.keys():
        wnns[k].transform = 'r'  # equal weights, sum to 1
    return wnns

def write_stats(df, w_matrix, dep_var, f):
    morans = ps.explore.esda.Moran(df[dep_var], w_matrix)
    gearys = ps.explore.esda.Geary(df[dep_var], w_matrix, permutations=100) # incredibly slow with more permutations
    f.write('Moran\'s I: {}, p-value norm: {}, p-value randomized: {}\n'.format(
        morans.I, morans.p_norm, morans.p_rand))
    f.write('Geary\'s C: {}, p-value norm: {}, p-value randomized: {}, p-value permutations: {}\n'.format(
        gearys.C, gearys.p_norm, gearys.p_rand, gearys.p_sim))

    print('Moran\'s I: {}, p-value norm: {}, p-value randomized: {}\n'.format(
        morans.I, morans.p_norm, morans.p_rand),
          'Geary\'s C: {}, p-value norm: {}, p-value randomized: {}, p-value permutations: {}\n'.format(
              gearys.C, gearys.p_norm, gearys.p_rand, gearys.p_sim)
         )
    return None

def safe_ll(r):
    try:
        return r.logll
    except AttributeError:
        return None


def coef_matrix(beta, theta, w, n):
    return np.eye(n) * beta + w.full()[0] * theta


def direct(row, variable_name, n, full_invs, wnns):
    print('direct', row['type'], row['_nearest'], variable_name)
    variable = 'coef_' + variable_name
    lagged_variable = 'coef_lag_' + variable_name
    if lagged_variable not in row.index:
        row_lag = 0
    else:
        row_lag = row[lagged_variable]
    if row['type'] in ['OLS', 'lagged_e', 'lagged_x', 'lagged_e_x']:
        return row[variable]
    elif row['type'] == 'lagged_y':
        return np.trace(np.dot(full_invs[row['_nearest']][row['type']], coef_matrix(
            row[variable], 0, wnns[row['_nearest']], n))) / n
    elif row['type'] == 'lagged_x_y':
        return np.trace(np.dot(full_invs[row['_nearest']][row['type']], coef_matrix(row[variable],
                                                      row_lag, wnns[row['_nearest']], n))) / n
    
    
def indirect(row, variable_name, n, full_invs, wnns):
    print('indirect', row['type'], row['_nearest'], variable_name)
    variable = 'coef_' + variable_name
    lagged_variable = 'coef_lag_' + variable_name
    if lagged_variable not in row.index:
        row_lag = 0
    else:
        row_lag = row[lagged_variable]
    if row['type'] in ['OLS', 'lagged_e']:
        return 0
    elif row['type'] in ['lagged_x', 'lagged_e_x']:
        return row_lag
    elif row['type'] == 'lagged_y':
        mt = np.dot(full_invs[row['_nearest']][row['type']], coef_matrix(
            row[variable], 0, wnns[row['_nearest']], n))
        return np.mean((mt - np.eye(n)*mt).sum(axis=1))
    elif row['type'] == 'lagged_x_y':
        mt = np.dot(full_invs[row['_nearest']][row['type']], coef_matrix(
            row[variable], row_lag, wnns[row['_nearest']], n))
        return np.mean((mt - np.eye(n)*mt).sum(axis=1))
    
    
def coord(city, df):
    if city=='lisbon':
        out_proj = Proj(init='epsg:23029')
    else:
        out_proj = Proj(init='epsg:2303' + str(int(1 + df['lng'].median() // 6)))
    
    return out_proj
    


def total_results(cities,
                  days_list=['weekdays'], robust=False, direct_indirect=False,
                  dep_vars=['log_realSum'], indep_vars=[
                      'room_shared','room_private','person_capacity', 'host_is_superhost','multi','biz', 
                      'cleanliness_rating','guest_satisfaction_overall','bedrooms', 'dist', 'metro_dist'],
                  indep_vars_to_lag=['room_shared','room_private','person_capacity','host_is_superhost','multi','biz',
                                     'cleanliness_rating','guest_satisfaction_overall','bedrooms'],
                  location_vars=['attr_index_norm', 'rest_index_norm']):
    all_res_shs = []
    for city in cities:
        for days in days_list:
            all_results = []
            
            ##define here your path for the folder with datasets
            #e.g. df = pd.read_csv('../zenodo/' + city +'_'+ days + '.csv')
            df = pd.read_csv('path' + city +'_'+ days + '.csv')
          
          
            #print(df)
            
            in_proj = Proj(init='epsg:4326')
            out_proj=coord(city, df)
    
            to_proj = lambda x, y: pyproj.transform(in_proj, out_proj, x, y)
        
            new_coords = df.apply(lambda row: to_proj(row['lng'], row['lat']), axis=1)
    
            df['km_lon'] = new_coords.apply(lambda x: x[0]).apply(lambda x: x + np.random.normal(0,0.01))
            df['km_lat'] = new_coords.apply(lambda x: x[1]).apply(lambda x: x + np.random.normal(0,0.01))
            
            df['host_is_superhost']=df['host_is_superhost'].astype('bool')
            df['log_realSum'] = df['realSum'].apply(np.log)
            
            name = city + '_' + days 
            print(name)
            
            ## creat a folder called "out" in your path for saving the results
            
            city_log = './out/{}log_'.format('robust' if robust else '') + name + '.txt'
            with open(city_log, 'w') as f:
                f.write('')

            print('full', city, df.shape)
            df.reset_index(inplace=True)
            points = df[['km_lon', 'km_lat']].values.tolist()
            kd = ps.lib.cg.kdtree.KDTree(np.array(points))
            wnns = create_weights(kd, robust)

            for col in indep_vars:
                if df[col].dtype == bool:
                    df[col] = df[col].apply(int)

            with open(city_log, 'a') as f:
                for k, dep_var, loc_var in product(wnns.keys(), dep_vars, location_vars):
                    w = wnns[k]
                    if not robust and loc_var == location_vars[0]:
                        write_stats(df, w, [dep_var], f)
                    print(k, dep_var, loc_var, w.full()[0].sum(axis=1))

                    characteristics = {
                        'city': city,
                        'days': days,
                        'location': loc_var,
                        'nearest': k,
                        'dependent_variable': dep_var,
                    }
                    characteristics = {'_' + k: v for k, v in characteristics.items()}

                    indep_vars += [loc_var]

                    f.write('\n=== ' + k + ' neighbors, {} dep_var ===\n'.format(dep_var))
                    indep_vars_lag = ['lag_' + x for x in indep_vars_to_lag]
                    for col, lag_col in zip(indep_vars_to_lag, indep_vars_lag):
                        df[lag_col] = ps.model.spreg.lag_spatial(w, df[col])
                    df['rho'] = ps.model.spreg.lag_spatial(w, df[dep_var])


                    ols = ps.model.spreg.OLS(
                        np.array(df[[dep_var]]),
                        np.array(df[indep_vars]),
                        w, name_y = dep_var, name_x = indep_vars, name_w = k, name_ds=city
                    )
                    f.write('OLS\n' + ols.summary)
                    all_results.append(reg_results(ols, characteristics, 't', 'OLS'))

                    if robust:
                        gme = ps.model.spreg.ML_Error(
                            np.array(df[[dep_var]]),
                            np.array(df[indep_vars]),
                            w, name_y = dep_var, name_x = indep_vars, name_w = k, name_ds=city, method='LU'
                        )
                        f.write('\n---\nLAGGED ERROR\n' + gme.summary)
                        all_results.append(reg_results(gme, characteristics, 'z', 'lagged_e'))

                    lagged_x = ps.model.spreg.OLS(
                        np.array(df[[dep_var]]),
                        np.array(df[indep_vars + indep_vars_lag]),
                        w, name_y = dep_var, name_x = indep_vars + indep_vars_lag,
                        name_w = k, spat_diag=True, name_ds=city
                    )
                    f.write('\n---\nLAGGED X\n' + lagged_x.summary)
                    all_results.append(reg_results(lagged_x, characteristics, 't', 'lagged_x'))

                    lagged_y_lm = ps.model.spreg.ML_Lag(
                        np.array(df[[dep_var]]),
                        np.array(df[indep_vars]),
                        w=w, name_y = dep_var, name_x = indep_vars, name_w = k, name_ds=city, method='LU'
                    )
                    f.write('\n---\nLAGGED Y LM\n' + lagged_y_lm.summary)
                    all_results.append(reg_results(lagged_y_lm, characteristics, 'z', 'lagged_y'))
                        
                    if robust:
                        gme_lagged_x = ps.model.spreg.ML_Error(
                            np.array(df[[dep_var]]),
                        np.array(df[indep_vars + indep_vars_lag]),
                        w, name_y = dep_var, name_x = indep_vars + indep_vars_lag, name_w = k, name_ds=city,
                        method='LU'
                        )
                        f.write('\n---\nLAGGED ERROR, X\n' + gme_lagged_x.summary)
                        all_results.append(reg_results(gme_lagged_x, characteristics, 'z', 'lagged_e_x'))

                    lagged_x_y_lm = ps.model.spreg.ML_Lag(
                            np.array(df[[dep_var]]),
                        np.array(df[indep_vars+indep_vars_lag]),
                        w=w,
                        name_y = dep_var, name_x = indep_vars + indep_vars_lag, name_w = k, name_ds=city,
                        method='LU'
                    )
                    f.write('\n---\nLAGGED Y, X LM\n' + lagged_x_y_lm.summary)
                    all_results.append(reg_results(lagged_x_y_lm, characteristics, 'z', 'lagged_x_y'))

                    indep_vars.remove(loc_var)
                    
            res_sh = pd.DataFrame(all_results)
            if direct_indirect:
                print(res_sh, res_sh.columns)
                full_invs = {}
                for k, w in wnns.items():
                    print(k, datetime.now())
                    full_invs[k] = {}
                    for model_type in ['lagged_y', 'lagged_x_y']:
                        print(model_type, datetime.now())
                        row = res_sh.loc[(res_sh['_nearest'] == k) & (res_sh['type'] == model_type)]
                        w.transform = 'r'
                        full_invs[k][model_type] = np.linalg.inv(np.eye(df.shape[0]) - row[
                    'coef_W_log_realSum'].values[0] * w.full()[0])

                for col in location_vars + indep_vars:
                    res_sh['direct_' + col] = res_sh.apply(direct, axis=1, args=(
                        col, df.shape[0], full_invs, wnns))
                    res_sh['indirect_' + col] = res_sh.apply(indirect, axis=1, args=(
                        col, df.shape[0], full_invs, wnns))

            all_res_shs.append(res_sh)
    return pd.concat(all_res_shs)


### example use of the code

##calculate the main regressions (OLS, lagged_y, lagged_x, lagged_y_x) with direct/indirect effects for Lisbon and save all results in a csv file
cities = ['lisbon']
all_results = total_results(cities, robust=False, direct_indirect=True)
all_results.to_csv('all_results.csv')

 
### calculate all regressions with different weights for Lisbon
res_robust = total_results(cities, robust=True, direct_indirect=False)
res_robust.to_csv('res_robust.csv')

