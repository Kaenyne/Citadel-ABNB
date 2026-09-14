# **D**eparture, **A**rrival, **I**nternal and **O**verflight data

This repository provides daily counts for flights in EUROCONTROL Member States.

The columns are as follows:

* `entry_date`: the UTC date the counts refer to, for example `2019-01-01`
* `country_name`: the country name, for example `Albania`
* `flt_daio`: the sum of departure, arrival, internal and overflight flights
* `flt_o`: the number of overflights
* `flt_i`: the number of internal flights
* `flt_c`: the number of circular flights, i.e. where airport of departure and
           airport of destination are the same
* `flt_dai`: the sum of departure, arrival and internal flights
* `flt_d`: the number of departures
* `flt_a`: the number of arrivals
* `flt_da`: the sume of arrivals and departures
* `flt_i_excl_c`: the sum of internal flights exluding the circular ones


**NOTE**: Canary Islands are included in the count for Spain. For a map using
this data see https://observablehq.com/@espinielli/overflight-variation
