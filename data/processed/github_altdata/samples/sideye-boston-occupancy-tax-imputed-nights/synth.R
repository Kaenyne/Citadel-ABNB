devtools::load_all('~/repos/augsynth')

by_month = read.csv('~/repos/airbnb/long_reservation_date_by_month.csv')
nights_by_month_nr = augsynth(nights ~ trt, unit, month, by_month, progfunc="None", scm = T)
print(summary(nights_by_month_nr))
plot(nights_by_month_nr)
by_month$log_nights = log_nights
log_nights_by_month_nr = augsynth( ~ trt, unit, month, by_month, progfunc="None", scm = T)
print(summary(log_nights_by_month_nr))
plot(log_nights_by_month_nr)

