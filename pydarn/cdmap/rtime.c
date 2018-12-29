/* time.c
   ======
   Author: R.J.Barnes
*/

/*
 LICENSE AND DISCLAIMER
 
 Copyright (c) 2012 The Johns Hopkins University/Applied Physics Laboratory
 
 This file is part of the Radar Software Toolkit (RST).
 
 RST is free software: you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 any later version.
 
 RST is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.
 
 You should have received a copy of the GNU Lesser General Public License
 along with RST.  If not, see <http://www.gnu.org/licenses/>.
 
 
 
*/

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "rtime.h"


#define DAY_SEC 86400

void TimeYrsecToYMDHMS(int yrsec,int yr,int *mo,int *dy,int *hr,int *mn,
                  int *sc) {


  time_t clock;
  struct tm tmyr;
  struct tm *tm;
  char *tz;

  memset(&tmyr,0,sizeof(struct tm));
  tmyr.tm_year=yr-1900;
  tmyr.tm_mon=0;
  tmyr.tm_mday=1;
  tmyr.tm_hour=0;
  tmyr.tm_min=0;
  tmyr.tm_sec=0;

  tz = getenv("TZ");
  setenv("TZ", "", 1);
  tzset();
 
  clock=mktime(&tmyr);
  if (tz) setenv("TZ", tz, 1);
  else unsetenv("TZ");
  tzset();

  clock=clock+yrsec;
  tm=gmtime(&clock);
  
  *mo=tm->tm_mon+1;
  *dy=tm->tm_mday;
  *hr=tm->tm_hour; 
  *mn=tm->tm_min;
  *sc=tm->tm_sec;
}


void TimeEpochToYMDHMS(double tme,int *yr,int *mo,int *dy,int *hr,int *mn,
	       double *sc) {
  time_t clock;
  struct tm *tm;

  clock=floor(tme);
  tm=gmtime(&clock);
  
  *yr=tm->tm_year+1900;
  *mo=tm->tm_mon+1;
  *dy=tm->tm_mday;
  *hr=tm->tm_hour; 
  *mn=tm->tm_min;
  *sc=tm->tm_sec+(tme-floor(tme));
}

double TimeYMDHMSToEpoch(int yr,int mo,int dy,int hr,int mn,double sec) {
 
  time_t clock;
  struct tm tm;
  char *tz;

  memset(&tm,0,sizeof(struct tm));
  tm.tm_year=yr-1900;
  tm.tm_mon=mo-1;
  tm.tm_mday=dy;
  tm.tm_hour=hr;
  tm.tm_min=mn;
  tm.tm_sec=floor(sec);

  tz = getenv("TZ");
  setenv("TZ", "", 1);
  tzset();
  clock=mktime(&tm);
  if (tz) setenv("TZ", tz, 1);
  else unsetenv("TZ");
  tzset();
               
  return clock+(sec-floor(sec));
}