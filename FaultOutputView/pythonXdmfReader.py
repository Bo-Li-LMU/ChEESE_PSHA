##
# @file
# This file is part of SeisSol.
#
# @author Thomas Ulrich  
#
# @section LICENSE
# Copyright (c) 2016, SeisSol Group
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# @section DESCRIPTION
#

#Author: Thomas Ulrich
#Date: 09.11.18
#aim: 
# python reader for SeisSol xdmf output (posix or hdf5) and hdf5 mesh


import numpy as np
import h5py
import os
import lxml.etree as ET

def ReadGeometry(xdmfFilename):
   #Read coordinates array of vertices
   tree = ET.parse(xdmfFilename)
   root = tree.getroot()
   path = os.path.dirname(xdmfFilename) 
   if path != '':
      path = path + '/'
   for Property in root.findall('.//Geometry'):
      nPoints = int(Property.get("NumberOfElements"))
      break
   for Property in root.findall('.//Geometry/DataItem'):
      dataLocation = Property.text
      geom_prec = int(Property.get("Precision"))
      break
   splitArgs = dataLocation.split(':')
   if len(splitArgs)==2:
      filename, hdf5var = splitArgs
      h5f = h5py.File(path + filename,'r')
      xyz = h5f[hdf5var][:,:]
      h5f.close()
   else:
      filename = dataLocation
      fid = open(path + filename,'r')
      if geom_prec==4:
         xyz = np.fromfile(fid, dtype=np.dtype('<f'),count=nPoints*3)
      else:
         xyz = np.fromfile(fid, dtype=np.dtype('d'),count=nPoints*3)
      fid.close()
      xyz = xyz.reshape((nPoints,3))
   return xyz

def ReadConnect(xdmfFilename):
   #Read the connectivity matrice defining the cells
   tree = ET.parse(xdmfFilename)
   root = tree.getroot()
   path = os.path.dirname(xdmfFilename) 
   if path != '':
      path = path + '/'
   for Property in root.findall('.//Topology'):
      nElements = int(Property.get("NumberOfElements"))
      break
   for Property in root.findall('.//Topology/DataItem'):
      dataLocation = Property.text
      connect_prec = int(Property.get("Precision"))
      #3 for surface, 4 for volume
      dim2 = int(Property.get("Dimensions").split()[1])
      break
   splitArgs = dataLocation.split(':')
   if len(splitArgs)==2:
      filename, hdf5var = splitArgs
      h5f = h5py.File(path + filename,'r')
      connect = h5f[hdf5var][:,:]
      h5f.close()
   else:
      filename = dataLocation
      fid = open(path + filename,'r')
      if connect_prec==4:
         connect = np.fromfile(fid, dtype=np.dtype('i4'),count=nElements*dim2)
      else:
         connect = np.fromfile(fid, dtype=np.dtype('i8'),count=nElements*dim2)
      fid.close()
      connect = connect.reshape((nElements,dim2))
   return connect

def GetDataLocationAndPrecision(xdmfFilename, dataName):
   def get(prop):
      dataLocation = prop.text
      data_prec = int(prop.get("Precision"))
      dims = prop.get("Dimensions").split()
      if len(dims)==1:
         MemDimension = int(prop.get("Dimensions").split()[0])
      else:
         MemDimension = int(prop.get("Dimensions").split()[1])
      return [dataLocation,data_prec,MemDimension]
   
   tree = ET.parse(xdmfFilename)
   root = tree.getroot()
   for Property in root.findall('.//Attribute'):
      if Property.get("Name")==dataName:
         for prop in Property.findall('.//DataItem'):
            if prop.get("Format") in ['HDF','Binary']:
               return get(prop)
            path = prop.get("Reference")
            if path is not None:
               ref = tree.xpath(path)[0]
               return get(ref)
   raise NameError('%s not found in dataset' %(dataName))

def ReadNdt(xdmfFilename):
   #read number of time steps in the file
   tree = ET.parse(xdmfFilename)
   root = tree.getroot()
   ndt = 0
   for Property in root.findall('.//Grid'):
      if Property.get("GridType")=="Uniform":
         ndt=ndt+1
   if ndt==0:
      raise NameError('ndt=0,( not GridType=Uniform found in xdmf)')
   else:
      return ndt

def ReadNElements(xdmfFilename):
   #read number of cell elements of the mesh
   tree = ET.parse(xdmfFilename)
   root = tree.getroot()
   for Property in root.findall('Domain/Grid/Grid/Topology'):
      return int(Property.get("NumberOfElements"))
   raise NameError('nElements could not be determined')

def ReadTimeStep(xdmfFilename):
   #reading the time step (dt) in the xdmf file
   tree = ET.parse(xdmfFilename)
   root = tree.getroot()
   i=0
   for Property in root.findall('Domain/Grid/Grid/Time'):
      if i==0:
         dt=float(Property.get("Value"))
         i=1
      else:
         dt=float(Property.get("Value"))-dt
         return dt
   raise NameError('time step could not be determined')



def Read1dData(xdmfFilename, dataName, nElements, isInt=False):
   #Read 1 dimension array (used by ReadPartition)
   path = os.path.dirname(xdmfFilename) 
   if path != '':
      path = path + '/'
   dataLocation,data_prec,MemDimension = GetDataLocationAndPrecision(xdmfFilename, dataName)
   splitArgs = dataLocation.split(':')
   if len(splitArgs)==2:
      filename, hdf5var = splitArgs
      h5f = h5py.File(path + filename,'r')
      myData = h5f[hdf5var][:]
      h5f.close()
   else:
      filename = dataLocation
      if data_prec == 4:
          if isInt:
             data_type = np.dtype('i4')
          else:
             data_type = np.dtype('<f')
      else:
          if isInt:
             data_type = np.dtype('i8')
          else:
             data_type = np.dtype('d')
      fid = open(path + filename,'r')
      myData = np.fromfile(fid, dtype=data_type, count=nElements)
      fid.close()
   return [myData,data_prec]

def ReadPartition(xdmfFilename, nElements):
   # Read partition array
   partition, partition_prec = Read1dData(xdmfFilename, 'partition', nElements, isInt=True)
   return partition

def LoadData(xdmfFilename, dataName, nElements, idt=0, oneDtMem=False, firstElement=-1):
   # Load a data array named 'dataName' (e.g. SRs)
   # if oneDtMem=True, only the time step idt is loaded
   # else all time steps are loaded
   # a partial load of the data array can be done using custom firstElement and nElements variables
   if firstElement==-1:
      firstElement=0
      partialLoading=False
   else:
      #read only a slice of the array (memory consumption)
      partialLoading=True

   lastElement=firstElement+nElements
   path = os.path.dirname(xdmfFilename) 
   if path != '':
      path = path + '/'
   dataLocation,data_prec,MemDimension = GetDataLocationAndPrecision(xdmfFilename, dataName)
   splitArgs = dataLocation.split(':')
   if len(splitArgs)==2:
      filename, hdf5var = splitArgs
      h5f = h5py.File(path + filename,'r')
      if not oneDtMem:
         myData = h5f[hdf5var][:,firstElement:lastElement]
      else:
         if h5f[hdf5var].ndim==2:
            myData = h5f[hdf5var][idt,firstElement:lastElement]
         else:
            myData = h5f[hdf5var][firstElement:lastElement]
      h5f.close()
   else:
      filename = dataLocation
      if data_prec == 4:
          data_type = np.dtype('<f')
      else:
          data_type = np.dtype('d')

      fid = open(path + filename,'r')
      if not oneDtMem:
         if not partialLoading:
           myData = np.fromfile(fid, dtype=data_type)
           ndt = np.shape(myData)[0]//MemDimension
           myData = myData.reshape((ndt, MemDimension))
           myData = myData[:,firstElement:lastElement]
         else:
           #read time step by time step to not stress the memory consumption
           ndt = ReadNdt(xdmfFilename)
           myData=np.zeros((ndt,nElements))
           for idt in range(0,ndt):
              fid.seek(idt*MemDimension*data_prec + firstElement*data_prec, os.SEEK_SET)
              myData[idt,:] = np.fromfile(fid, dtype=data_type, count=nElements)
      else:
         fid.seek(idt*MemDimension*data_prec + firstElement*data_prec, os.SEEK_SET)
         myData = np.fromfile(fid, dtype=data_type, count=nElements)
      fid.close()
   return [myData,data_prec]
