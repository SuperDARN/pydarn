/* dmap.c
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
 but WITHOUT ANY WARRANTY; without even  the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.
 
 You should have received a copy of the GN U Lesser General Public License
 along with RST.  If not, see <http://www.gnu.org/licenses/>.
   
   
  
*/ 

#include <Python.h>
#include <stdio.h> 
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include "rtypes.h"
#include "rconvert.h"
#include "dmap.h"

struct DataMap *DataMapMake() {
  struct DataMap *ptr;
  ptr=malloc(sizeof(struct DataMap));
  if (ptr==NULL) return ptr;
  ptr->scl=NULL;
  ptr->snum=0;
  ptr->arr=NULL;
  ptr->anum=0;
  return ptr;
}

struct DataMapScalar* DataMapMakeScalar(char *name,int mode,int type,
                                        void *data) {
  struct DataMapScalar *ptr;

  if (name==NULL) return NULL;
  ptr=malloc(sizeof(struct DataMap));
  if (ptr==NULL) return ptr;
  ptr->name=malloc(strlen(name)+1);
  if (ptr->name==NULL) {
    free(ptr);
    return NULL;
  }
  strcpy(ptr->name,name);
  ptr->mode=mode;
  ptr->type=type;
  ptr->data.vptr=data;
  return ptr;
}

int DataMapTestScalar(struct DataMapScalar *ptr,char *name,int type) {
  if (ptr->type !=type) return 0;
  if (strcmp(ptr->name,name) !=0) return 0;
  return 1;
}

void DataMapFreeScalar(struct DataMapScalar *ptr) {
  if (ptr==NULL) return; 
  if (ptr->name !=NULL) free(ptr->name);
  if ((ptr->mode & 0x04) && (ptr->data.vptr !=NULL) && 
      (ptr->type==DATASTRING) && (*((char **) ptr->data.vptr) !=NULL)) 
    free(* (char **) ptr->data.vptr);

  if ((ptr->mode & 0x04) && (ptr->data.mptr !=NULL) && 
      (ptr->type==DATAMAP) && (*ptr->data.mptr !=NULL)) 
    DataMapFree(*ptr->data.mptr);


  if ((ptr->mode !=0) && (ptr->data.vptr !=NULL)) free(ptr->data.vptr);
  free(ptr);
  return;
}

int DataMapAddScalar(struct DataMap *ptr,
		     char *name,int type,void *data) {
  struct DataMapScalar *s;
  if (ptr==NULL) return -1;
  s=DataMapMakeScalar(name,0,type,data);
  if (s==NULL) return -1;

  if (ptr->scl==NULL) ptr->scl=malloc(sizeof(struct DataMapScalar *));
  else {
    struct DataMapScalar **tmp;
    tmp=realloc(ptr->scl,(ptr->snum+1)*sizeof(struct DataMapScalar *));
    if (tmp==NULL) {
      DataMapFreeScalar(s);
      return -1;
    }
    ptr->scl=tmp;
  }
  ptr->scl[ptr->snum]=s;
  ptr->snum++;
  return 0;
}




void *DataMapStoreScalar(struct DataMap *ptr,
                         char *name,int type,void *data) {

  struct DataMapScalar *s;
  void *tmp=NULL;
 
  if (ptr==NULL) return NULL;
  switch (type) {
  case DATACHAR:
    tmp=malloc(sizeof(char));
    if (tmp==NULL) break;
    if (data !=NULL) *((char *) tmp)=*((char *) data);
    break;
  case DATASHORT:
    tmp=malloc(sizeof(int16));
    if (tmp==NULL) break;
     if (data !=NULL) *((int16 *) tmp)=*((int16 *) data);
    break;
  case DATAINT:
    tmp=malloc(sizeof(int32));
    if (tmp==NULL) break;
     if (data !=NULL) *((int32 *) tmp)=*((int32 *) data);
    break;
  case DATALONG:
    tmp=malloc(sizeof(int64));
    if (tmp==NULL) break;
     if (data !=NULL) *((int64 *) tmp)=*((int64 *) data);
    break;
  case DATAUCHAR:
    tmp=malloc(sizeof(unsigned char));
    if (tmp==NULL) break;
     if (data !=NULL) *((unsigned char *) tmp)=*((unsigned char *) data);
    break;
  case DATAUSHORT:
    tmp=malloc(sizeof(uint16));
    if (tmp==NULL) break;
     if (data !=NULL) *((uint16 *) tmp)=*((uint16 *) data);
    break;
  case DATAUINT:
    tmp=malloc(sizeof(uint32));
    if (tmp==NULL) break;
     if (data !=NULL) *((uint32 *) tmp)=*((uint32 *) data);
    break;
  case DATAULONG:
    tmp=malloc(sizeof(uint64));
    if (tmp==NULL) break;
     if (data !=NULL) *((uint64 *) tmp)=*((uint64 *) data);
    break;
  case DATAFLOAT:
    tmp=malloc(sizeof(float));
    if (tmp==NULL) break;
     if (data !=NULL) *((float *) tmp)=*((float *) data);
    break;
  case DATADOUBLE:
    tmp=malloc(+sizeof(double));
    if (tmp==NULL) break;
     if (data !=NULL) *((double *) tmp)=*((double *) data);
    break;
  case DATASTRING:
    tmp=malloc(sizeof(char *));
    if (tmp==NULL) break;
     if (data !=NULL) *((char **) tmp)=*((char **) data);
    break;
  default:
    tmp=malloc(sizeof(struct DataMap *));
    if (tmp==NULL) break;
    if (data !=NULL) *((struct DataMap **) tmp)=*((struct DataMap **) data); 
    break;
  }
  if (tmp==NULL) return NULL;

  s=DataMapMakeScalar(name,1,type,tmp);
  if (s==NULL) return NULL;

  if (ptr->scl==NULL) tmp=malloc(sizeof(struct DataMapScalar *));
  else tmp=realloc(ptr->scl,(ptr->snum+1)*sizeof(struct DataMapScalar *));
  if (tmp==NULL) {
    DataMapFreeScalar(s);
    return NULL;
  }
  ptr->scl=tmp;
  ptr->scl[ptr->snum]=s;
  ptr->snum++;
  return s->data.vptr;
}


int DataMapScalarSetFree(struct DataMap *ptr,char *name,int type) {

  int c;
  struct DataMapScalar *s=NULL;

  for (c=0;c<ptr->snum;c++) {
    s=ptr->scl[c];
    if ((strcmp(s->name,name)==0) && (s->type==type)) break;
  }
  if (c==ptr->snum) return -1;
  s->mode=s->mode | 0x04;
  return 0;
}


int DataMapRemoveScalar(struct DataMap *ptr,
		        char *name,int type) {
  int c;
  struct DataMapScalar *s=NULL;

  for (c=0;c<ptr->snum;c++) {
    s=ptr->scl[c];
    if ((strcmp(s->name,name)==0) && (s->type==type)) break;
  }
  if (c==ptr->snum) return -1;
  DataMapFreeScalar(s);

  if (c != (ptr->snum-1)) 
    memmove(&ptr->scl[c],&ptr->scl[c+1],
	    sizeof(struct DataMapScalar *)*(ptr->snum-c));

  if (ptr->snum>1) {
    struct DataMapScalar **tmp; 
    tmp=realloc(ptr->scl,(ptr->snum-1)*sizeof(struct DataMapScalar *));
    if (tmp==NULL) return -1;
    ptr->scl=tmp;
  } else { 
    free(ptr->scl);
    ptr->scl=NULL;
  }
  ptr->snum--;
  return 0;
}

void *DataMapFindScalar(struct DataMap *ptr,char *name,int type) {
  int c;
  struct DataMapScalar *s=NULL;

  for (c=0;c<ptr->snum;c++) {
    s=ptr->scl[c];
    if ((strcmp(s->name,name)==0) && (s->type==type)) break;
  }
  if (c==ptr->snum) return NULL;
  return s->data.vptr;
}


struct DataMapArray* DataMapMakeArray(char *name,int mode,
                                      int type,int dim,
                                      int32 *rng,void *data) {
  
  struct DataMapArray *ptr;

  if (name==NULL) return NULL;
  if (dim==0) return NULL;

  ptr=malloc(sizeof(struct DataMapArray));
  if (ptr==NULL) return ptr;
  ptr->name=malloc(strlen(name)+1);
  if (ptr->name==NULL) {
    free(ptr);
    return NULL;
  }
  strcpy(ptr->name,name);
  ptr->mode=mode;
  ptr->type=type;
  ptr->dim=dim;
  ptr->rng=rng;
  ptr->data.vptr=data;
  return ptr;
}

int DataMapTestArray(struct DataMapArray *ptr,char *name,int type,int dim) {
  if (ptr->type !=type) return 0;
  if (ptr->dim !=dim) return 0;
  if (strcmp(ptr->name,name) !=0) return 0;
  return 1;
}

void DataMapFreeArray(struct DataMapArray *ptr) {
  if (ptr==NULL) return; 
  if ((ptr->mode & 0x04) && (ptr->data.vptr !=NULL) && 
      (ptr->type==DATASTRING)) {
    int s=1,n;
    char **v=NULL;
    for (n=0;n<ptr->dim;n++) s=s*ptr->rng[n];
    v=((char **) ptr->data.vptr);
    for (n=0;n<s;n++) if (v[n] !=NULL) free(v[n]);    
  }

  if ((ptr->mode & 0x04) && (ptr->data.mptr !=NULL) && 
      (ptr->type==DATAMAP)) {
    int s=1,n;
    for (n=0;n<ptr->dim;n++) s=s*ptr->rng[n];
    for (n=0;n<s;n++) if (ptr->data.mptr[n] !=NULL) 
      DataMapFree(ptr->data.mptr[n]);    
  }


  if ((ptr->mode & 0x01) && (ptr->rng !=NULL)) free(ptr->rng);
  if (ptr->name !=NULL) free(ptr->name);
  if ((ptr->mode & 0x02) && (ptr->data.vptr !=NULL)) free(ptr->data.vptr);
  free(ptr);
  return;
}


int DataMapAddArray(struct DataMap *ptr,
                        char *name,int type,int dim,
                        int32 *rng,void *data) {
  struct DataMapArray *a;
  if (ptr==NULL) return -1;
  a=DataMapMakeArray(name,0,type,dim,rng,data);
  if (a==NULL) return -1;

  if (ptr->arr==NULL) ptr->arr=malloc(sizeof(struct DataMapArray *));
  else {
    struct DataMapArray **tmp;
    tmp=realloc(ptr->arr,(ptr->anum+1)*sizeof(struct DataMapArray *));
    if (tmp==NULL) {
      DataMapFreeArray(a);
      return -1;
    }
    ptr->arr=tmp;
  }
  ptr->arr[ptr->anum]=a;
  ptr->anum++;
  return 0;
}

void *DataMapStoreArray(struct DataMap *ptr,
                     char *name,int type,int dim,
		      int32 *rng,void *data) {

  struct DataMapArray *a;
  int n=1,x=0;
  void *tmp=NULL;
  int32 *rngbuf=NULL;
  if (ptr==NULL) return NULL;
  if (dim==0) return NULL;
  if (rng==NULL) return NULL;

  
  rngbuf=malloc(dim*sizeof(int32));
  if (rngbuf==NULL) return NULL;
 
  n=1;
  for (x=0;x<dim;x++) {
    n=rng[x]*n;
    rngbuf[x]=rng[x];
  }

  switch (type) {
  case DATACHAR:
    tmp=malloc(sizeof(char)*n);
    if (tmp==NULL) break;
    if (data !=NULL) memcpy(tmp,data,sizeof(char)*n);
    else memset(tmp,0,sizeof(char)*n);
    break;
  case DATASHORT:
    tmp=malloc(sizeof(int16)*n);
    if (tmp==NULL) break;
    if (data !=NULL) memcpy(tmp,data,sizeof(int16)*n);
    else memset(tmp,0,sizeof(int16)*n);
    break;
  case DATAINT:
    tmp=malloc(sizeof(int32)*n);
    if (tmp==NULL) break;
    if (data !=NULL) memcpy(tmp,data,sizeof(int32)*n);
    else memset(tmp,0,sizeof(int32)*n);
    break;
  case DATALONG:
    tmp=malloc(sizeof(int64)*n);
    if (tmp==NULL) break;
    if (data !=NULL) memcpy(tmp,data,sizeof(int64)*n);
    else memset(tmp,0,sizeof(int64)*n);
    break;
  case DATAUCHAR:
    tmp=malloc(sizeof(unsigned char)*n);
    if (tmp==NULL) break;
    if (data !=NULL) memcpy(tmp,data,sizeof(unsigned char)*n);
    else memset(tmp,0,sizeof(unsigned char)*n);
    break;
  case DATAUSHORT:
    tmp=malloc(sizeof(uint16)*n);
    if (tmp==NULL) break;
    if (data !=NULL) memcpy(tmp,data,sizeof(uint16)*n);
    else memset(tmp,0,sizeof(uint16)*n);
    break;
  case DATAUINT:
    tmp=malloc(sizeof(uint32)*n);
    if (tmp==NULL) break;
    if (data !=NULL) memcpy(tmp,data,sizeof(uint32)*n);
    else memset(tmp,0,sizeof(uint32)*n);
    break;
  case DATAULONG:
    tmp=malloc(sizeof(uint64)*n);
    if (tmp==NULL) break;
    if (data !=NULL) memcpy(tmp,data,sizeof(uint64)*n);
    else memset(tmp,0,sizeof(uint64)*n);
    break;
  case DATAFLOAT:
    tmp=malloc(sizeof(float)*n);
    if (tmp==NULL) break;
    if (data !=NULL) memcpy(tmp,data,sizeof(float)*n);
    else memset(tmp,0,sizeof(float)*n);
    break;
  case DATADOUBLE:
    tmp=malloc(sizeof(double)*n);
    if (tmp==NULL) break;
    if (data !=NULL) memcpy(tmp,data,sizeof(double)*n);
    else memset(tmp,0,sizeof(double)*n);
    break;
  case DATASTRING:
    tmp=malloc(sizeof(char *)*n);
    if (tmp==NULL) break;
    if (data !=NULL) memcpy(tmp,data,sizeof(char *)*n);
    else memset(tmp,0,sizeof(char *)*n);
    break;
  default:
    tmp=malloc(sizeof(struct DataMap *)*n);
    if (tmp==NULL) break;
    if (data !=NULL) memcpy(tmp,data,sizeof(struct DataMap *)*n);
    else memset(tmp,0,sizeof(struct DataMap *)*n);
    break;
  }
  if (tmp==NULL) {
    if (rngbuf !=NULL) free(rngbuf);
    return NULL;
  }
 
  a=DataMapMakeArray(name,3,type,dim,rngbuf,tmp);
  if (a==NULL) {
    free(rngbuf);
    if (tmp !=NULL) free(tmp);
    return NULL;
  }
  if (ptr->arr==NULL) ptr->arr=malloc(sizeof(struct DataMapArray *));
  else {
    tmp=realloc(ptr->arr,(ptr->anum+1)*sizeof(struct DataMapArray *));
    if (tmp==NULL) {
      DataMapFreeArray(a);
      return NULL;
    }
    ptr->arr=tmp;
  }
  ptr->arr[ptr->anum]=a;
  ptr->anum++;
  return a->data.vptr;
}


int DataMapSetFreeArray(struct DataMap *ptr,
			char *name,int type,int dim) {
  int c;
  struct DataMapArray *a=NULL;

  for (c=0;c<ptr->anum;c++) {
    a=ptr->arr[c];
    if ((strcmp(a->name,name)==0) && (a->type==type) && (a->dim==dim)) break;
  }
  if (c==ptr->anum) return -1;
  a->mode=a->mode | 0x04;
  return 0;
}


int DataMapRemoveArray(struct DataMap *ptr,
		       char *name,int type,int dim) {
  int c;
  struct DataMapArray *a=NULL;
  for (c=0;c<ptr->anum;c++) {
    a=ptr->arr[c];
    if ((strcmp(a->name,name)==0) && (a->type==type) && (a->dim==dim)) break;
  }
  if (c==ptr->anum) return -1;
  DataMapFreeArray(a);

  if (c != (ptr->anum-1)) memmove(&ptr->arr[c],&ptr->arr[c+1],
				  sizeof(struct DataMapArray *)*
                                  (ptr->anum-c));

  if (ptr->anum>1) {
    struct DataMapArray **tmp; 
    tmp=realloc(ptr->arr,(ptr->anum-1)*sizeof(struct DataMapArray *));
    if (tmp==NULL) return -1;
    ptr->arr=tmp;
  } else { 
    free(ptr->arr);
    ptr->arr=NULL;
  }
  ptr->anum--;
  return 0;
}

int DataMapSize(struct DataMap *ptr) {
  int c,x,m,n;
  char **tmp;
  struct DataMapScalar *s=NULL;
  struct DataMapArray *a=NULL;
  int sze=0;

  sze+=sizeof(int32)*4;
  for (c=0;c<ptr->snum;c++) {
    s=ptr->scl[c];
    n=0;
    while (s->name[n] !=0) n++;
    sze+=n+1+1;
    switch (s->type) {
    case DATACHAR:
      sze++;
      break;
    case DATASHORT:
      sze+=sizeof(int16);
      break;
    case DATAINT:
      sze+=sizeof(int32);
      break;
    case DATALONG:
      sze+=sizeof(int64);
      break;
    case DATAUCHAR:
      sze++;
      break;
    case DATAUSHORT:
      sze+=sizeof(uint16);
      break;
    case DATAUINT:
      sze+=sizeof(uint32);
      break;
    case DATAULONG:
      sze+=sizeof(uint64);
      break;

    case DATAFLOAT:
      sze+=sizeof(float);
      break;
    case DATADOUBLE:
      sze+=sizeof(double);;
      break;
    case DATASTRING:
      tmp=(char **) s->data.vptr;
      if (*tmp !=NULL) {
        n=0;
        while((*tmp)[n] !=0) n++;
        sze+=n+1;  
      } else sze++;
      break;
    case DATAMAP:
      if (*s->data.mptr !=NULL)
        sze+=sizeof(int32)+DataMapSize(*s->data.mptr);
      else sze+=sizeof(int32);
      break;
    }
  }

  for (c=0;c<ptr->anum;c++) {
    a=ptr->arr[c];
    n=0;
    while (a->name[n] !=0) n++;
    sze+=n+1+1+4+4*a->dim;
    n=1;
    for (x=0;x<a->dim;x++) n=a->rng[x]*n;
    switch (a->type) {
    case DATACHAR:
      sze+=n;
      break;
    case DATASHORT:
      sze+=sizeof(int16)*n;
      break;
    case DATAINT:
      sze+=sizeof(int32)*n;
      break;
    case DATALONG:
      sze+=sizeof(int64)*n;
      break;

    case DATAUCHAR:
      sze+=n;
      break;
    case DATAUSHORT:
      sze+=sizeof(uint16)*n;
      break;
    case DATAUINT:
      sze+=sizeof(uint32)*n;
      break;
    case DATAULONG:
      sze+=sizeof(uint64)*n;
      break;

    case DATAFLOAT:
      sze+=sizeof(float)*n;
      break;
    case DATADOUBLE:
      sze+=sizeof(double)*n;
      break;
    case DATASTRING:
      tmp=(char **) a->data.vptr;
      for (x=0;x<n;x++) {
        if (tmp[x] !=NULL) {
          m=0;
          while( (tmp[x])[m] !=0) m++;
          sze+=m+1;       
	} else sze++;
      }
      break;
    default:
      for (x=0;x<n;x++) {
        if (a->data.mptr[x] !=NULL) 
          sze+=sizeof(int32)+DataMapSize(a->data.mptr[x]); 
        else sze+=sizeof(int32);
      }
      break;
    }

  }
  return sze;
}


void *DataMapFindArray(struct DataMap *ptr,
		       char *name,int type,int dim,int32 **rng) {
  int c;
  struct DataMapArray *a=NULL;
  for (c=0;c<ptr->anum;c++) {
    a=ptr->arr[c];
    if ((strcmp(a->name,name)==0) && (a->type==type) && (a->dim==dim)) break;
  }
  if (c==ptr->anum) return NULL;
  if (rng !=NULL) *rng=a->rng;
  return a->data.vptr;

}

unsigned char *DataMapEncodeBuffer(struct DataMap *ptr,int *size) {
  int c,x,m,n;
  char **tmp;
  void *tbuf;
  int tsze;
  struct DataMapScalar *s=NULL;
  struct DataMapArray *a=NULL;
  unsigned char *buf=NULL;
  int off=0;
  int sze=0;

  sze=DataMapSize(ptr);

  if (size !=NULL) *size=sze;
  buf=malloc(sze);
  if (buf==NULL) return NULL;

  ConvertFromInt(DATACODE,buf+off);
  off+=sizeof(int32);
  ConvertFromInt(sze,buf+off);
  off+=sizeof(int32);
  ConvertFromInt(ptr->snum,buf+off);
  off+=sizeof(int32);
  ConvertFromInt(ptr->anum,buf+off);
  off+=sizeof(int32);
  
  for (c=0;c<ptr->snum;c++) {
    s=ptr->scl[c];
    n=0;
    while (s->name[n] !=0) n++;
    memcpy(buf+off,s->name,n+1);
    off+=n+1;
    buf[off]=s->type;
    off++;
    switch (s->type) {
    case DATACHAR:
      buf[off]=s->data.cptr[0];
      off++;
      break;
    case DATASHORT:
      ConvertFromShort(*(s->data.sptr),buf+off);
      off+=sizeof(int16);
      break;
    case DATAINT:
      ConvertFromInt(*(s->data.iptr),buf+off);
      off+=sizeof(int32);
      break;
    case DATALONG:
      ConvertFromLong(*(s->data.lptr),buf+off);
      off+=sizeof(int64);
      break;

    case DATAUCHAR:
      buf[off]=s->data.ucptr[0];
      off++;
      break;
    case DATAUSHORT:
      ConvertFromUShort(*(s->data.usptr),buf+off);
      off+=sizeof(uint16);
      break;
    case DATAUINT:
      ConvertFromUInt(*(s->data.uiptr),buf+off);
      off+=sizeof(uint32);
      break;
    case DATAULONG:
      ConvertFromULong(*(s->data.ulptr),buf+off);
      off+=sizeof(uint64);
      break;

    case DATAFLOAT:
      ConvertFromFloat(*(s->data.fptr),buf+off);
      off+=sizeof(float);
      break;
    case DATADOUBLE:
      ConvertFromDouble(*(s->data.dptr),buf+off);
      off+=sizeof(double);
      break;
    case DATASTRING:
      tmp=(char **) s->data.vptr;
      if (*tmp !=NULL) {
        n=0;
        while((*tmp)[n] !=0) n++;
        memcpy(buf+off,*tmp,n+1);
        off+=n+1;
      } else {
        buf[off]=0;
        off+=1;
      }
      break;
    default:
      if (*s->data.mptr !=NULL) {
        tbuf=DataMapEncodeBuffer(*s->data.mptr,&tsze);
        ConvertFromInt(tsze,buf+off);
        off+=sizeof(int32);
        memcpy(buf+off,tbuf,tsze);
        off+=tsze;
        free(tbuf);
      } else {
        tsze=0;
        ConvertFromInt(tsze,buf+off);
        off+=sizeof(int32);
      }
      break;
    }
  }
 
  for (c=0;c<ptr->anum;c++) {
    a=ptr->arr[c];
    n=0;
    while (a->name[n] !=0) n++;
    memcpy(buf+off,a->name,n+1);
    off+=n+1;
    buf[off]=a->type;
    off++;
    ConvertFromInt(a->dim,buf+off);
    off+=sizeof(int32);
    for (x=0;x<a->dim;x++)  {
      ConvertFromInt(a->rng[x],buf+off);
      off+=sizeof(int32);
    }
    n=1;
    for (x=0;x<a->dim;x++) n=a->rng[x]*n;
    switch (a->type) {
    case DATACHAR:
      memcpy(buf+off,a->data.cptr,n);
      off+=n;
      break;
    case DATASHORT:
      for (x=0;x<n;x++) {
        ConvertFromShort(a->data.sptr[x],buf+off);
        off+=sizeof(int16);
      }
      break;
    case DATAINT:
      for (x=0;x<n;x++) {
        ConvertFromInt(a->data.iptr[x],buf+off);
        off+=sizeof(int32);
      }
      break;
    case DATALONG:
      for (x=0;x<n;x++) {
        ConvertFromLong(a->data.lptr[x],buf+off);
        off+=sizeof(int64);
      }
      break;

    case DATAUCHAR:
      memcpy(buf+off,a->data.cptr,n);
      off+=n;
      break;
    case DATAUSHORT:
      for (x=0;x<n;x++) {
        ConvertFromUShort(a->data.usptr[x],buf+off);
        off+=sizeof(uint16);
      }
      break;
    case DATAUINT:
      for (x=0;x<n;x++) {
        ConvertFromUInt(a->data.uiptr[x],buf+off);
        off+=sizeof(uint32);
      }
      break;
    case DATAULONG:
      for (x=0;x<n;x++) {
        ConvertFromULong(a->data.ulptr[x],buf+off);
        off+=sizeof(uint64);
      }
      break;

    case DATAFLOAT:
      for (x=0;x<n;x++) {
        ConvertFromFloat(a->data.fptr[x],buf+off);
        off+=sizeof(float);
      }
      break;
    case DATADOUBLE:
      for (x=0;x<n;x++) {
        ConvertFromDouble(a->data.dptr[x],buf+off);
        off+=sizeof(double);;
      }
      break;
    case DATASTRING:
      tmp=(char **) a->data.vptr;
      for (x=0;x<n;x++) {
        if (tmp[x] !=NULL) {
          m=0;
          while( (tmp[x])[m] !=0) m++;
          memcpy(buf+off,tmp[x],m+1);
          off+=m+1;
	} else {
          buf[off]=0;
          off++;
	}
      }
      break;
    default:
      for (x=0;x<n;x++) {
        if (a->data.mptr[x] !=0) {
          tbuf=DataMapEncodeBuffer(a->data.mptr[x],&tsze);
          ConvertFromInt(tsze,buf+off);
          off+=sizeof(int32);
          memcpy(buf+off,tbuf,tsze);
          off+=tsze;
          free(tbuf);
	} else {
          tsze=0;
          ConvertFromInt(tsze,buf+off);
          off+=sizeof(int32);
	}
      }
    }    
  }
  return buf;
}


int DataMapWrite(int fid,struct DataMap *ptr) {
  unsigned char *buf=NULL;
  int sze=0,st=0,cnt=0;
  buf=DataMapEncodeBuffer(ptr,&sze);
  if (buf==NULL) return -1;
  
  while (cnt<sze) {
    st=write(fid,buf+cnt,sze-cnt);
    if (st<=0) break;
    cnt+=st;
  } 
  if (cnt<sze) return st;
  free(buf);
  return sze;
}

int DataMapFwrite(FILE *fp,struct DataMap *ptr) {
  return DataMapWrite(fileno(fp),ptr);
}

void DataMapFree(struct DataMap *ptr) {
  int s,a;

  if (ptr==NULL) return;
  if (ptr->scl !=NULL) {  
    for (s=0;s<ptr->snum;s++) {
      DataMapFreeScalar(ptr->scl[s]);
    }
    free(ptr->scl);
  }
  if (ptr->arr !=NULL) {
    for (a=0;a<ptr->anum;a++) {
      DataMapFreeArray(ptr->arr[a]);
    }
    free(ptr->arr);
  }
  free(ptr);
}

char *DataMapReadName(int fid) {
  char *ptr,*tmp;
  char t;
  int st=0;
  int blk=256;
  int stp=256;
  int sze=0;

  ptr=malloc(sizeof(char)*blk);
  while (((st=read(fid,&t,1))==1) && (t !=0)) {
    ptr[sze]=t;
    sze++;
    if (sze>=blk) {
      blk+=stp;
      tmp=realloc(ptr,blk);
      if (tmp==NULL) free(ptr);
      ptr=tmp;
    }
    if (ptr==NULL) return NULL;
  }
  if (st != 1) {
    free(ptr);
    return NULL;
  } 
  ptr[sze]=0;
  
  sze++;
  tmp=realloc(ptr,sze);
  if (tmp==NULL) free(ptr);
  ptr=tmp;
  return ptr;
}

char *DataMapReadString(int fid) {
  char *ptr,*tmp;
  char t;
  int st=0;
  int blk=256;
  int stp=256;
  int sze=0;

  ptr=malloc(sizeof(char)*blk);
  while (((st=read(fid,&t,1))==1) && (t !=0)) {
    ptr[sze]=t;
    sze++;
    if (sze>=blk) {
      blk+=stp;
      tmp=realloc(ptr,blk);
      if (tmp==NULL) free(ptr);
      ptr=tmp;
    }
    if (ptr==NULL) return NULL;
  }
  if (st != 1) {
    free(ptr);
    return NULL;
  } 
  ptr[sze]=0;
  
  sze++;
  tmp=realloc(ptr,sze);
  if (tmp==NULL) free(ptr);
  ptr=tmp;
  return ptr;
}

struct DataMap *DataMapDecodeBuffer(unsigned char *buf,int size) {
  int c,x,n,i,e;
  int32 sn,an;
  int32 code,sze;
  char *name;
  char *tmp;
  char type;
  unsigned int off=0;  
  int32 tsze;

  struct DataMap *ptr;
  struct DataMapScalar *s;
  struct DataMapArray *a;
  
  ptr=DataMapMake();
  if (ptr==NULL) return NULL;
  ConvertToInt(buf+off,&code);
  off+=sizeof(int32);
  ConvertToInt(buf+off,&sze);
  off+=sizeof(int32);
  ConvertToInt(buf+off,&sn);
  off+=sizeof(int32);
  ConvertToInt(buf+off,&an);
  off+=sizeof(int32);
  if (sn>0) {
    ptr->snum=sn;
    ptr->scl=malloc(sizeof(struct DataMapScalar *)*sn); 
    if (ptr->scl==NULL) {
      DataMapFree(ptr);
      return NULL;
    }
    for (c=0;c<sn;c++) ptr->scl[c]=NULL;
  }

  if (an>0) {
    ptr->anum=an;
    ptr->arr=malloc(sizeof(struct DataMapArray *)*an);
    if (ptr->arr==NULL) {
      DataMapFree(ptr);
      return NULL;
    }
    for (c=0;c<an;c++) ptr->arr[c]=NULL;
  }

  for (c=0;c<sn;c++) {
    e=0;
    n=0; 
    while ((buf[off+n] !=0) && (off+n<size)) n++;
    if (off+n>=size) break;
    name=malloc(n+1);
    if (name==NULL) break;
    memcpy(name,buf+off,n+1);
    off+=n+1;
    type=buf[off];
    off++;
    s=malloc(sizeof(struct DataMapScalar));
    if (s==NULL) {
      free(name);
      break;
    }

    s->name=name;
    s->mode=6;
    s->type=type;
    ptr->scl[c]=s;   

    switch (s->type) {
    case DATACHAR:
      s->data.vptr=malloc(sizeof(char));
      if (s->data.vptr==NULL) {
        e=1;
        break;
      }
      s->data.cptr[0]=buf[off];
      off++;
      break;
    case DATASHORT:
      s->data.vptr=malloc(sizeof(int16));
      if (s->data.vptr==NULL) {
        e=1;
        break;
      }
      ConvertToShort(buf+off,s->data.sptr);
      off+=sizeof(int16);
      break;
    case DATAINT:
      s->data.vptr=malloc(sizeof(int32));
      if (s->data.vptr==NULL) {
        e=1;
        break;
      }
      ConvertToInt(buf+off,s->data.iptr);
      off+=sizeof(int32); 
      break;
    case DATALONG:
      s->data.vptr=malloc(sizeof(int64));
      if (s->data.vptr==NULL) {
        e=1;
        break;
      }
      ConvertToLong(buf+off,s->data.lptr);
      off+=sizeof(int64);
      break;
    case DATAUCHAR:
      s->data.vptr=malloc(sizeof(unsigned char));
      if (s->data.vptr==NULL) {
        e=1;
        break;
      }
      s->data.ucptr[0]=buf[off];
      off++;
      break;
    case DATAUSHORT:
      s->data.vptr=malloc(sizeof(uint16));
      if (s->data.vptr==NULL) {
        e=1;
        break;
      }
      ConvertToUShort(buf+off,s->data.usptr);
      off+=sizeof(uint16);
      break;
    case DATAUINT:
      s->data.vptr=malloc(sizeof(uint32));
      if (s->data.vptr==NULL) {
        e=1;
        break;
      }
      ConvertToUInt(buf+off,s->data.uiptr);
      off+=sizeof(uint32);
      break;
    case DATAULONG:
      s->data.vptr=malloc(sizeof(uint64));
      if (s->data.vptr==NULL) {
        e=1;
        break;
      }
      ConvertToULong(buf+off,s->data.ulptr);
      off+=sizeof(uint64);
      break;
    case DATAFLOAT:
      s->data.vptr=malloc(sizeof(float));
      if (s->data.vptr==NULL) {
        e=1;
        break;
      }
      ConvertToFloat(buf+off,s->data.fptr);
      off+=sizeof(float);
      break;
    case DATADOUBLE:
      s->data.vptr=malloc(sizeof(double));
      if (s->data.vptr==NULL) {
  	e=1;
        break;
      }
      ConvertToDouble(buf+off,s->data.dptr);
      off+=sizeof(double);
      break;
    case DATASTRING:
      n=0;
      while ((buf[off+n] !=0) && (off+n<size)) n++;
      if (off+n>=size) {
        e=1;
        break;
      }
 
      s->data.vptr=malloc(sizeof(char *));
      if (s->data.vptr==NULL) {
        e=1;
        break;
      }
      if (n !=0) {
        tmp=malloc(n+1);
        if (tmp==NULL) {
          e=1;
          break;
	}
        memcpy(tmp,buf+off,n+1);
        off+=n+1;
        *( (char **) s->data.vptr)=tmp;
      } else {
        *( (char **) s->data.vptr)=NULL;
        off++;
      }
      break;
    default:

      s->data.vptr=malloc(sizeof(struct DataMap *));
      if (s->data.vptr==NULL) {
  	e=1;
        break;
      }
      ConvertToInt(buf+off,&tsze);
      off+=sizeof(int32); 
      if (tsze !=0) { 
        *s->data.mptr=DataMapDecodeBuffer(buf+off,tsze);
        off+=tsze;
      } else *s->data.mptr=NULL;
    }
    if (e==1) break;
  }

  if (c !=sn) {
    DataMapFree(ptr);
    return NULL;
  }
  for (c=0;c<an;c++) {
    e=0;
    n=0;
    while ((buf[off+n] !=0) && (off+n<size)) n++;
    if (off+n>=size) break;
    name=malloc(n+1);
    if (name==NULL) break;
    memcpy(name,buf+off,n+1);
    off+=n+1;
    type=buf[off];
    off++;
    a=malloc(sizeof(struct DataMapArray));
    if (a==NULL) {
      free(name);
      break;
    }
    a->name=name;
    a->mode=7;
    a->type=type;
    ptr->arr[c]=a;   
    ConvertToInt(buf+off,(int32 *) &(a->dim));
    off+=sizeof(int32);
    a->rng=malloc(a->dim*sizeof(int32));
    if (a->rng==NULL) break;
    for (x=0;x<a->dim;x++)  {
       ConvertToInt(buf+off,&a->rng[x]);
       off+=sizeof(int32);
    }
    if (x!=a->dim) break;
    n=1;
    for (x=0;x<a->dim;x++) n=a->rng[x]*n;
    switch (a->type) {
    case DATACHAR:
      a->data.vptr=malloc(sizeof(char)*n);
      if (a->data.vptr==NULL) {
        e=1;
        break;
      }
      memcpy(a->data.cptr,buf+off,sizeof(char)*n);
      off+=sizeof(char)*n;
      break;
    case DATASHORT:
      a->data.vptr=malloc(sizeof(int16)*n);
      if (a->data.vptr==NULL) {
        e=1;
        break;
      }
      for (x=0;x<n;x++) {
        ConvertToShort(buf+off,&a->data.sptr[x]);
        off+=sizeof(int16);
      }
      break;
    case DATAINT:
      a->data.vptr=malloc(sizeof(int32)*n);
      if (a->data.vptr==NULL) {
        break;
        e=1;
      }
      for (x=0;x<n;x++) {
        ConvertToInt(buf+off,&a->data.iptr[x]);
        off+=sizeof(int32);
      }
      break;
    case DATALONG:
      a->data.vptr=malloc(sizeof(int64)*n);
      if (a->data.vptr==NULL) {
        e=1;
        break;
      }
      for (x=0;x<n;x++) {
        ConvertToLong(buf+off,&a->data.lptr[x]);
        off+=sizeof(int64);
      }
      break;

    case DATAUCHAR:
      a->data.vptr=malloc(sizeof(unsigned char)*n);
      if (a->data.vptr==NULL) {
        e=1;
        break;
      }
      memcpy(a->data.cptr,buf+off,sizeof(unsigned char)*n);
      off+=sizeof(unsigned char)*n;
      break;
    case DATAUSHORT:
      a->data.vptr=malloc(sizeof(uint16)*n);
      if (a->data.vptr==NULL) {
        e=1;
        break;
      }
      for (x=0;x<n;x++) {
        ConvertToUShort(buf+off,&a->data.usptr[x]);
        off+=sizeof(uint16);
      }
      break;
    case DATAUINT:
      a->data.vptr=malloc(sizeof(uint32)*n);
      if (a->data.vptr==NULL) {
        e=1;
        break;
      }
      for (x=0;x<n;x++) {
        ConvertToUInt(buf+off,&a->data.uiptr[x]);
        off+=sizeof(uint32);
      }
      break;
    case DATAULONG:
      a->data.vptr=malloc(sizeof(uint64)*n);
      if (a->data.vptr==NULL) {
        e=1;
        break;
      }
      for (x=0;x<n;x++) {
        ConvertToULong(buf+off,&a->data.ulptr[x]);
        off+=sizeof(uint64);
      }
      break;
    case DATAFLOAT:
      a->data.vptr=malloc(sizeof(float)*n);
      if (a->data.vptr==NULL) {
        e=1;
        break;
      }
      for (x=0;x<n;x++) {
        ConvertToFloat(buf+off,&a->data.fptr[x]);
        off+=sizeof(float);
      }
      break;
    case DATADOUBLE:
      a->data.vptr=malloc(sizeof(double)*n);
      if (a->data.vptr==NULL) {
        e=1;
        break;
      }
      for (x=0;x<n;x++) {
	ConvertToDouble(buf+off,&a->data.dptr[x]);
	off+=sizeof(double);
      }
      break;
    case DATASTRING:
      a->data.vptr=malloc(sizeof(char *)*n);
      if (a->data.vptr==NULL) {
        e=1;
        break;
      }  
      for (x=0;x<n;x++) {
         i=0;          
         while ((buf[off+i] !=0) && (off+i<size)) i++;
         if (off+i>=size) break;
         if (i !=0) {
           tmp=malloc(i+1);
           if (tmp==NULL) break;
           memcpy(tmp,buf+off,i+1); 
           ((char **) a->data.vptr)[x]=tmp;
	 } else ((char **) a->data.vptr)[x]=NULL;
         off+=i+1;
      }
      if (x !=n) e=1;
      break;
    default:
      a->data.mptr=malloc(sizeof(struct DataMap *)*n);
      if (a->data.vptr==NULL) {
	e=1;
        break;
      }
      for (x=0;x<n;x++) {
        ConvertToInt(buf+off,&tsze);
        off+=sizeof(int32);
        if (tsze !=0) {
          a->data.mptr[x]=DataMapDecodeBuffer(buf+off,tsze);
          off+=tsze;
	} else a->data.mptr[x]=0;      
      }
    }
    if (e==1) break;
  }

  if (c !=an) {
    DataMapFree(ptr);
    return NULL;
  }
 
  return ptr;
}


struct DataMap *DataMapReadBlock(int fid,int *s) {
  unsigned char *buf=NULL;
  struct DataMap *ptr;
  int32 code,sze,*iptr;
  int size=0,cnt=0,num=0,st=0;   
  st=ConvertReadInt(fid,&code);
  if (st==-1) return NULL;
  st=ConvertReadInt(fid,&sze);
  if (st==-1) return NULL;
  if (sze==0) return NULL;
  size=sze;
  buf=malloc(size);
  if (buf==NULL) return NULL;
  iptr=(int32 *) buf;
  iptr[0]=code;
  iptr[1]=sze;
    
  cnt=0;
  num=size-2*sizeof(int32);
  while (cnt<num) {
    st=read(fid,buf+2*sizeof(int32)+cnt,num-cnt);
    if (st<=0) break;
    cnt+=st;
  }
  if (cnt<num) {
    free(buf);
    return NULL;
  }
  ptr=DataMapDecodeBuffer(buf,size);
  free(buf);
  if (s !=NULL) *s=size+2*sizeof(int32);
  return ptr;
}

struct DataMap *DataMapFreadBlock(FILE *fp,int *s) {
  return DataMapReadBlock(fileno(fp),s);
}

struct DataMap *DataMapRead(int fid) {
  return DataMapReadBlock(fid,NULL);
}

struct DataMap *DataMapFread(FILE *fp) {
  return DataMapRead(fileno(fp));
}


