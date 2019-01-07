/* rconvert.h
   ==========
   Author: R.J.Barnes
*/


/*
 (c) 2011 JHU/APL & Others - Please Consult LICENSE.datamap.txt for more information.
*/


#ifndef _RCONVERT_H
#define _RCONVERT_H

int ConvertBitOrder(void);
void ConvertToLong(unsigned char *cnv,int64 *val);
void ConvertToInt(unsigned char *cnv,int32 *val);
void ConvertToShort(unsigned char *cnv,int16 *val);
void ConvertToULong(unsigned char *cnv,uint64 *val);
void ConvertToUInt(unsigned char *cnv,uint32 *val);
void ConvertToUShort(unsigned char *cnv,uint16 *val);
void ConvertToDouble(unsigned char *cnv,double *val);
void ConvertToFloat(unsigned char *cnv,float *val);
void ConvertFromFloat(float val,unsigned char *cnv);
void ConvertFromDouble(double val,unsigned char *cnv);
void ConvertFromLong(int64 val,unsigned char *cnv);
void ConvertFromInt(int32 val,unsigned char *cnv);
void ConvertFromShort(int16 val,unsigned char *cnv);
void ConvertFromULong(uint64 val,unsigned char *cnv);
void ConvertFromUInt(uint32 val,unsigned char *cnv);
void ConvertFromUShort(uint16 val,unsigned char *cnv);
void ConvertBlock(unsigned char *cnv,int *pattern);


int ConvertReadLong(int fp,int64 *val);
int ConvertReadInt(int fp,int32 *val);
int ConvertReadShort(int fp,int16 *val);
int ConvertReadULong(int fp,uint64 *val);
int ConvertReadUInt(int fp,uint32 *val);
int ConvertReadUShort(int fp,uint16 *val);
int ConvertReadDouble(int fp,double *val);
int ConvertReadFloat(int fp,float *val);




#endif



