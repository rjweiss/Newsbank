library(readr)
library(lubridate)
library(plyr)

data = read.csv('C:/Users/rjweiss/Documents/GitHub/Newsbank/scr/output.csv',
                header=F)

names(data) = c('dir','title','program','station','market','hms','ymd','path')

data$hms = hms(data$hms)
data$ymd = ymd(data$ymd)

table(data$market)
table(data$station)

ggplot(data, aes(x=hms@hour)) + geom_histogram() + facet_wrap(~market)