# Copyright (C) 2014 Ashton Reimer
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
.. module:: DataTypes
   :synopsis: the parent class needed for reading data (dmap, hdf5 (soon?))
.. moduleauthor:: Ashton Reimer, 20140822, generalized from radDataTypes.py by
Jef Spaleta

*********************
**Module**: pydarn.sdio.DataTypes
*********************

Classes
---------
  * :class:`pydarn.sdio.DataTypes.DataPtr`

"""

# Method to read data using python dmap (pydmap)
def read_file(filename):
    from dmap import parse_dmap_format_from_file

    return parse_dmap_format_from_file(filename)


import logging

class DataFileIO(object):
    """A generalized data pointer class which contains general methods for
    reading various data file (dmap, hdf5, etc.) types into SuperDARN data types
    (fit, raw, iqdat, map, etc.).
    
    Public Attributes
    ------------------
    sTime : (datetime)
        start time of the request
    eTime : (datetime)
        end time of the request
    fType : (str)
        the file type, 'fitacf', 'rawacf', 'iqdat', 'fitex', 'lmfit'
    dType : (str)
        the file data type, 'dmap','hdf5'
    recordIndex : (dict)
        look up dictionary for file offsets for all records 
    scanStartIndex : (dict)
        look up dictionary for file offsets for scan start records

    Private Attributes
    -------------------
    ptr : (file)
        the data pointer (different depending dmap or hdf5)
    fd : (int)
        the file descriptor 
    filename : (str)
        the name of the currently open file

    Methods
    ---------
    open
    close
    createIndex
        Index the offsets for all records and scan boundaries
    offsetSeek
        Seek file to requested byte offset, checking to make sure it in the
        record index
    offsetTell
        Current byte offset
    rewind
        rewind file back to the beginning 
    read
        read record at current file offset in to a dictionary
 
    Written by ASR 20140822
    """

    #### NOTE TO DEVS ####
    # Dictionaries are used to select which data type specific methods to use
    # Props to Adam Knox (github @aknox-va) for the idea. 
    #
    # First of all, different data containers, like dmap, hdf5, txt, etc. 
    # are what is meant by data types
    #
    # The point here is to support various data types using this class
    # without the child classes (radDataPtr, sdDataPtr) having to switch
    # to employ logic to utilize the appropriate method ie) radDataPtr 
    # doesn't need to have conditional logic to decide with "read" 
    # method to use.
    #
    # To add support for another data type, one needs to do 2 things:
    #     1) There are 5 methods that are data type specific:
    #        read, createIndex, offsetSeek, offsetTell, and rewind
    #        One must create a method for each one of these (see examples
    #        at the end of this class).
    #     2) Each method needs to be registered in the method dictionaries 
    #        in the __init__ of this class. The keys in each dictionary 
    #        are the data types and the values are the method names for 
    #        those dictionary types, ie) __read is the read methods 
    #        dictionary, where __read = {'dmap':self.__readDmap} points
    #        to the __readDmap method for the dmap data type.
    #####################

    def __init__(self, stime, datatype, eTime=None, fileName=None):

        import davitpy.pydarn
        import datetime as dt

        # Data type method dictionaries to select the data type 
        # specific methods to use credit to Adam Knox (github 
        # @aknox-va) for the idea.          

        __read = {'dmap':self.__readDmap}
        __createIndex = {'dmap':self.__createIndexDmap}
        __offsetSeek = {'dmap':self.__offsetSeekDmap}
        __offsetTell = {'dmap':self.__offsetTellDmap}
        __rewind = {'dmap':self.__rewindDmap}
        datatypelist = __read.keys()

        # Check input variables
        estr = "datatype: {:} not supported.  ".format(str(datatype))
        estr = "{:s}Supported data types: {:}".format(estr, str(datatypelist))
        assert isinstance(stime, dt.datetime), \
            logging.error('stime must be datetime object')
        assert datatype in datatypelist, logging.error(estr)
        assert eTime == None or isinstance(eTime, dt.datetime), \
            logging.error('eTime must be datetime object or None')

        # Set up the general attributes
        self.sTime = stime
        self.eTime = eTime
        self.dType = datatype
        self.recordIndex = None
        self.scanStartIndex = None
        self._filename = fileName 
        self._fd = None
        self._ptr =  None

        # Set the data Type specific methods
        self.read = __read[datatype]
        self.createIndex = __createIndex[datatype]
        self.offsetSeek = __offsetSeek[datatype]
        self.offsetTell = __offsetTell[datatype]
        self.rewind = __rewind[datatype]


    # FIRST, THE GENERAL COMMON METHODS

    def __del__(self):
        self.close() 

    def __iter__(self):
        return self
     
    def open(self):
        """open the associated filename."""
        import os
        self._fd = os.open(self._filename, os.O_RDONLY)
        self._ptr = os.fdopen(self._fd)
 
    def close(self):
        """ Close the associated file.
        """
        import os
        if self._ptr is not None:
            self._ptr.close()
            self._fd = None


    # BEGIN DATA TYPE SPECIFIC HIDDEN METHODS

    ########################################
    #                 DMAP
    ########################################

    # NOW ALL OF THE DMAP SPECIFIC METHODS
    def __createIndexDmap(self):
        """ Create dictionary of offsets as a function of timestamp.
        """
        # This method will have to do different things depending 
        # on self.dType (for future other data file support ie. hdf5)

        import datetime as dt
        from davitpy.pydarn.dmapio import getDmapOffset, readDmapRec
        from davitpy.pydarn.dmapio import setDmapOffset

        recordDict = {}
        scanStartDict = {}
        starting_offset = self.__offsetTellDmap()
        # rewind back to start of file
        self.__rewindDmap()
        while(1):
            # read the next record from the dmap file
            offset = getDmapOffset(self._fd)
            dfile = readDmapRec(self._fd)
            if dfile is None:
                # if we dont have valid data, clean up, get out
                print '\nreached end of data'
                break
            else:
                if(dt.datetime.utcfromtimestamp(dfile['time']) >= self.sTime and
                   dt.datetime.utcfromtimestamp(dfile['time']) <= self.eTime): 
                    rectime = dt.datetime.utcfromtimestamp(dfile['time'])
                    recordDict[rectime] = offset
                    if dfile['scan'] == 1:
                        scanStartDict[rectime] = offset
        # reset back to before building the index
        self.recordIndex = recordDict
        self.__offsetSeekDmap(starting_offset)
        self.scanStartIndex = scanStartDict
        return recordDict, scanStartDict

    def __offsetSeekDmap(self, offset, force=False):
        """ Jump to dmap record at supplied byte offset.
        Require offset to be in record index list unless forced. 
        """
        # This method will have to do different things depending 
        # on self.dType (for future other data file support ie. hdf5)

        from davitpy.pydarn.dmapio import setDmapOffset, getDmapOffset

        if force:
            return setDmapOffset(self._fd, offset)
        else:
            if self.recordIndex is None:        
                self.__createIndexDmap()

            if offset in self.recordIndex.values():
                return setDmapOffset(self._fd, offset)
            else:
                return getDmapOffset(self._fd)

    def __offsetTellDmap(self):
        """ Jump to dmap record at supplied byte offset.
        """

        # This method will have to do different things depending 
        # on self.dType (for future other data file support ie. hdf5)

        from davitpy.pydarn.dmapio import getDmapOffset
        return getDmapOffset(self._fd)

    def __rewindDmap(self):
        """ Jump to beginning of dmap file.
        """

        # This method will have to do different things depending 
        # on self.dType (for future other data file support ie. hdf5)
        from davitpy.pydarn.dmapio import setDmapOffset 
        return setDmapOffset(self._fd, 0)

    def __readDmap(self):
       """ A function to read a single record of data from a dmap file.

       Returns
       --------
       dfile : (dict/NoneType)
           A dictionary with the data in the dmap record.  Will return None
           when finished reading
       """
       # This method will have to do different things depending 
       # on self.dType (for future other data file support ie. hdf5)

       from davitpy import pydarn
       import datetime as dt

       # check input
       if self._ptr == None:
           logging.error('your pointer does not point to any data')
           return None

       if self._ptr.closed:
           logging.error('your file pointer is closed')
           return None

       # do this until we reach the requested start time
       # and have a parameter match
       while(1):
           offset = pydarn.dmapio.getDmapOffset(self._fd)
           dfile = pydarn.dmapio.readDmapRec(self._fd)
           # check for valid data
           if(dfile == None or
              dt.datetime.utcfromtimestamp(dfile['time']) > self.eTime):
               # if we dont have valid data, clean up, get out
               print '\nreached end of data'
               return None

           # check that we're in the time window
           if(dt.datetime.utcfromtimestamp(dfile['time']) >= self.sTime and
              dt.datetime.utcfromtimestamp(dfile['time']) <= self.eTime):
               return dfile

    ########################################
    #    NEW DATATYPE TEMPLATE METHODS
    ########################################

    # NOW ALL OF THE NEW DATATYPE SPECIFIC METHODS

    def __readNewDatatype(self):
        pass
    def __createIndexNewDatatype(self):
        pass
    def __offsetSeekNewDatatype(self):
        pass
    def __offsetTellDatatype(self):
        pass
    def __rewindDatatype(self):
        pass


# Class used for testing
class testing(DataPtr):
    def __init__(self, stime, datatype, etime, filename):
        import datetime as dt
        super(testing, self).__init__(stime, datatype, eTime=etime,
                                      fileName=filename)


if __name__=="__main__":

    import datetime
    from davitpy import pydarn
    from davitpy.pydarn.sdio.fetchUtils import fetch_remote_files

    print "##############################"
    print " TESTING THE DataPtr class..."
    print "##############################"

    stime = datetime.datetime(2012, 11, 24, 4)
    eTime = datetime.datetime(2012, 11, 24, 5)

    print " TRYING TO WORK WITH THE DMAP DATATYPE"
    print " FETCHING A SUPERDARN FITEX FILE......"
    files = fetch_remote_files(stime, eTime, \
                'sftp','sd-data.ece.vt.edu', 'data/{year}/{ftype}/{radar}/', \
                {'radar':'mcm', 'ftype':'fitex', 'channel':'a'}, '/tmp/sd/', \
                ['{date}.{hour}......{radar}.{ftype}', \
                 '{date}.{hour}......{radar}.{channel}.{ftype}'], \
                username='sd_dbread', password='5d', \
                time_inc=datetime.timedelta(hours=2))
    print "   Fetched the file: " + files[0] + "\n"

    print " INITIALIZING A CLASS THAT INHERITS FROM DataPtr"
    t = pydarn.sdio.DataTypes.testing(stime, 'dmap', eTime, files[0])
    print "   ...it worked! (Success!)"


    print " Opening the file..."
    t.open()
    print "   ...it worked! (Success!)"


    print "Reading a line of the file..."
    dfile = t.read()
    if isinstance(dfile, dict):
        print "   SUCCESS!"
    else:
        print "   FAILED!"


    print " Getting file offsets as a function of timestamp..."
    index, _ = t.createIndex()
    if isinstance(index, dict):
        print "   SUCCESS!"
    else:
        print "   FAILED!"


    print " Seeking to file offset at datetime(2012,11,24,4,4,39,141000)"
    t.offsetSeek(index[datetime.datetime(2012, 11, 24, 4, 4, 39, 141000)])
    offset = t.offsetTell()
    dfile = t.read()
    print " Seeked to time: {:}".format( \
                        str(datetime.datetime.utcfromtimestamp(dfile['time'])))
    print " Telling the file offset..."
    print " Should get: {:} and we got: {:}".format( \
                str(index[datetime.datetime(2012, 11, 24, 4, 4, 39, 141000)]),
                                                     str(offset))

    print " Rewinding the file..."
    t.rewind()
    print "    ...rewound! (Success!)"

    print " Closing the file..."
    t.close()
    print "    ...closed! (Success!)"
    print "\n ALL DONE TESTING"

  

