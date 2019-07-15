from abc import ABC, abstractmethod


class Copyable(ABC):
    @abstractmethod
    def copy(self):
        pass


class Properties:
    serialVersionUID = 4112578634029874840

    def __init__(self, defaults=None):
        self.defaults = defaults
        self.propertiesTable = {}

    def setProperty(self, key, value):
        self.propertiesTable[key] = value

    def getProperty(self, key, defaultValue=None):
        if key in self.propertiesTable:
            return self.propertiesTable[key]
        return defaultValue

    def propertyNames(self):
        return self.propertiesTable.keys()

    def stringPropertyNames(self):
        keys = [k for k in self.propertiesTable.keys() if isinstance(k, str)]
        return keys

    def list(self):
        print('-- listing properties --')
        for k, v in self.propertiesTable.items():
            print('{}={}\n'.format(k, v))


class Attribute(Copyable):
    serialVersionUID = -742180568732916383
    NUMERIC = 0
    NOMINAL = 1
    STRING = 2
    DATE = 3
    RELATIONAL = 4
    ORDERING_SYMBOLIC = 0
    ORDERING_ORDERED = 1
    ORDERING_MODULO = 2
    ARFF_ATTRIBUTE = '@attribute'
    ARFF_ATTRIBUTE_INTEGER = 'integer'
    ARFF_ATTRIBUTE_REAL = 'real'
    ARFF_ATTRIBUTE_NUMERIC = 'numeric'
    ARFF_ATTRIBUTE_STRING = 'string'
    ARFF_ATTRIBUTE_DATE = 'date'
    ARFF_ATTRIBUTE_RELATIONAL = 'relational'
    ARFF_END_SUBRELATION = '@end'
    STRING_COMPRESS_THRESHOLD = 200

    def __init__(self, attributeName, createStringAttribute=False, attributeValues=None, metadata=None):
        self.m_Name = attributeName
        self.m_Type = Attribute.NUMERIC
        self.m_AttributeInfo = None
        self.m_Index = -1
        self.m_Weight = 1.0
        if createStringAttribute:
            self.m_AttributeInfo = NominalAttributeInfo(None, attributeName)
            self.m_Type = Attribute.STRING
        elif attributeValues is not None:
            self.m_AttributeInfo = NominalAttributeInfo(attributeValues, attributeName)
            if attributeValues is None:
                self.m_type = Attribute.STRING
            else:
                self.m_Type = Attribute.NOMINAL
        if metadata is not None:
            self.m_AttributeMetaInfo = AttributeMetaInfo(metadata, self)
        else:
            self.m_AttributeMetaInfo = metadata


class AttributeMetaInfo:
    def __init__(self, metadata, att):
        self.m_Metadata = metadata
        self.m_Ordering = Attribute.ORDERING_SYMBOLIC
        self.m_IsRegular = False
        self.m_IsAverageable = False
        self.m_HasZeropoint = False
        self.m_LowerBound = -9999999999999999
        self.m_LowerBoundIsOpen = False
        self.m_UpperBound = 9999999999999999
        self.m_UpperBoundIsOpen = False
        self.setMetadata(att)

    def setMetadata(self, att):
        if att.m_Type == Attribute.DATE:
            self.m_Ordering = Attribute.ORDERING_ORDERED
            self.m_IsRegular = True
        else:
            orderString = self.m_Metadata.getProperty("ordering")
            default = False
            if att.m_Type == Attribute.NUMERIC and orderString is not "modulo" and orderString is not "symbolic":
                default = True
            self.m_IsAverageable = self.m_Metadata.getProperty("averageable", default)
            self.m_HasZeropoint = self.m_Metadata.getProperty("zeropoint", default)
            if self.m_IsAverageable or self.m_HasZeropoint:
                default = True
            self.m_IsRegular = self.m_Metadata.getProperty("regular", default)
            if orderString is "symbolic":
                self.m_Ordering = Attribute.ORDERING_SYMBOLIC
            elif orderString is "ordered":
                self.m_Ordering = Attribute.ORDERING_ORDERED
            elif orderString is "modulo":
                self.m_Ordering = Attribute.ORDERING_MODULO
            else:
                if att.m_Type == Attribute.NUMERIC or self.m_IsAverageable or self.m_HasZeropoint:
                    self.m_Ordering = Attribute.ORDERING_ORDERED
                else:
                    self.m_Ordering = Attribute.ORDERING_SYMBOLIC
        if self.m_IsAverageable and not self.m_IsRegular:
            raise Exception("Error, an averageable attribute must be regular.")
        if self.m_HasZeropoint and not self.m_IsRegular:
            raise Exception("Error, a zeropoint attribute must be regular.")
        if self.m_IsRegular and self.m_Ordering == Attribute.ORDERING_SYMBOLIC:
            raise Exception("Error, a symbolic attribute cannot be regular.")
        if self.m_IsAverageable and self.m_Ordering != Attribute.ORDERING_ORDERED:
            raise Exception("Error, an averageable attribute must be ordered.")
        if self.m_HasZeropoint and self.m_Ordering != Attribute.ORDERING_ORDERED:
            raise Exception("Error, a zeropoint attribute must be ordered.")
        weight = self.m_Metadata.getProperty("weight")
        if weight is not None:
            att.m_Weight = weight
        if att.m_Type == Attribute.NUMERIC:
            self.setNumericRange(self.m_Metadata.getProperty("range"))

    def setNumericRange(self, rangeString):
        pass


class NominalAttributeInfo:
    def __init__(self, attributeValues, attributeName):
        self.m_Values = []
        self.m_Hashtable = {}
        if attributeValues is not None:
            for i in range(len(attributeValues)):
                store = attributeValues[i]
                if store in self.m_Hashtable:
                    raise Exception(
                        "Error, a nominal attribute ({}) cannot have duplicate labels ({}).".format(attributeName,
                                                                                                    store))
                self.m_Values.append(store)
                self.m_Hashtable[store] = i
