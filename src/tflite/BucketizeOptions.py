# automatically generated by the FlatBuffers compiler, do not modify

# namespace: tflite

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class BucketizeOptions(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = BucketizeOptions()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsBucketizeOptions(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    @classmethod
    def BucketizeOptionsBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(buf, offset, b"\x54\x46\x4C\x33", size_prefixed=size_prefixed)

    # BucketizeOptions
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # BucketizeOptions
    def Boundaries(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            a = self._tab.Vector(o)
            return self._tab.Get(flatbuffers.number_types.Float32Flags, a + flatbuffers.number_types.UOffsetTFlags.py_type(j * 4))
        return 0

    # BucketizeOptions
    def BoundariesAsNumpy(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.GetVectorAsNumpy(flatbuffers.number_types.Float32Flags, o)
        return 0

    # BucketizeOptions
    def BoundariesLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # BucketizeOptions
    def BoundariesIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        return o == 0

def BucketizeOptionsStart(builder):
    builder.StartObject(1)

def Start(builder):
    BucketizeOptionsStart(builder)

def BucketizeOptionsAddBoundaries(builder, boundaries):
    builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(boundaries), 0)

def AddBoundaries(builder, boundaries):
    BucketizeOptionsAddBoundaries(builder, boundaries)

def BucketizeOptionsStartBoundariesVector(builder, numElems):
    return builder.StartVector(4, numElems, 4)

def StartBoundariesVector(builder, numElems):
    return BucketizeOptionsStartBoundariesVector(builder, numElems)

def BucketizeOptionsEnd(builder):
    return builder.EndObject()

def End(builder):
    return BucketizeOptionsEnd(builder)
