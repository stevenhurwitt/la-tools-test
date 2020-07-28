import logging

from dateutil.parser import parse
from energyworx_public.enums import str_to_enum
from energyworx_public import domain

logger = logging.getLogger()


class Property(object):

    def __init__(self, name=None, required=False, validator=None, repeated=False, default=None):
        self.name = name
        self.required = required
        self.validator = validator
        self.repeated = repeated
        self.default = default

    def __get__(self, inst, objtype):
        if hasattr(inst, self._get_attr_name()):
            value = getattr(inst, self._get_attr_name())
        else:
            value = self._get_default()
            self.__set__(inst, value)
        return value

    def __set__(self, inst, value):
        if value is None or isinstance(value, str) and value == '':
            value = self._get_default()
        setattr(inst, self._get_attr_name(), value)

    def _get_attr_name(self):
        return '_' + self.name

    def _get_default(self):
        return self.default if self.default is not None else ([] if self.repeated else None)


class DateTimeProperty(Property):

    def __init__(self, name=None, required=False, validator=None):
        super(DateTimeProperty, self).__init__(name=name, required=required, validator=validator, repeated=False)


class EnumProperty(Property):

    def __init__(self, enum_type, name=None, required=False, validator=None, repeated=False):
        super(EnumProperty, self).__init__(name=name, required=required, validator=validator, repeated=repeated)
        self.enum_type = enum_type


class StructuredProperty(Property):

    def __init__(self, domain_class, name=None, required=False, validator=None, repeated=False):
        super(StructuredProperty, self).__init__(name=name, required=required, validator=validator, repeated=repeated)
        self.domain_class = domain_class


class MappingProperty(Property):

    def __init__(self, name=None, domain_property=None, required=False, validator=None, repeated=False, default=None):
        super(MappingProperty, self).__init__(name, required, validator, repeated, default)
        self.domain_property = domain_property


class MappingEnumProperty(EnumProperty):

    def __init__(self, enum_type, name=None, domain_property=None, required=False, validator=None, repeated=False):
        super(MappingEnumProperty, self).__init__(enum_type=enum_type, name=name, required=required, validator=validator, repeated=repeated)
        self.domain_property = domain_property


class MappingStructuredProperty(StructuredProperty):

    def __init__(self, domain_class, name=None, domain_property=None, required=False, validator=None, repeated=False):
        super(MappingStructuredProperty, self).__init__(domain_class, name=name, required=required, validator=validator, repeated=repeated)
        self.domain_property = domain_property


class EnergyworxDomainMeta(type):
    """
    A metaclass which is used to add extra attributes 'attr_by_prop_name' and 'prop_by_attr' to every domain class
    """
    def __new__(mcs, name, bases, dct):
        new_class = super(EnergyworxDomainMeta, mcs).__new__(mcs, name, bases, dct)
        attr_by_prop_name = {}
        prop_by_attr = {}
        for attr, value in dct.items():
            """if isinstance(value, Property):
                setattr(value, 'attr_name', attr)
                attr_by_prop_name.update({value.name: attr})
                prop_by_attr.update({attr: value})"""
            #do normal attr/prop stuff
            if type(value) != list:
                value_obj = Property(value)
                if isinstance(value_obj, Property):
                    setattr(value_obj, 'attr_name', attr)
                    attr_by_prop_name.update({value_obj.name: attr})
                    prop_by_attr.update({attr: value_obj})
            
            #make structured props for tags/channels
            elif type(value) == list:
                struct_prop = []
                if attr == 'tags':
                    for v in value:
                        struct_prop.append(domain.Tag.from_dict(v))
                    struct_prop = StructuredProperty(struct_prop)
        
                if isinstance(struct_prop, StructuredProperty):
                    setattr(struct_prop, 'attr_name', attr)
                    setattr(struct_prop, 'repeated', True)
                    attr_by_prop_name.update({'tags': attr})
                    prop_by_attr.update({attr: struct_prop})
            
                elif attr == 'channels':

                    for v in value:
                        new_ch = domain.Channel()
                        try:
                            new_ch.description = v['description']
                        except:
                            new_ch.description = ''
                        new_ch.is_source = v['isSource']
                        new_ch.classifier = v['classifier']
                        new_ch.unit_type = v['unitType']
                        new_ch.datapoint_type = v['datapointType']
                        new_ch.id = v['id']
                        new_ch.name = v['name']
                        struct_prop.append(new_ch)
                    struct_prop = StructuredProperty(struct_prop)
            
                    if isinstance(struct_prop, StructuredProperty):
                        setattr(struct_prop, 'attr_name', attr)
                        setattr(struct_prop, 'repeated', True)
                        attr_by_prop_name.update({'channels': attr})
                        prop_by_attr.update({attr: struct_prop})

        if attr_by_prop_name:
            new_class.attr_by_prop_name = attr_by_prop_name

        if prop_by_attr:
            new_class.prop_by_attr = prop_by_attr

        return new_class


class EnergyworxDomain(object):

    """ Base class for every domain class """

    __metaclass__ = EnergyworxDomainMeta

    id = Property(name="id", required=True)
    read_only = Property(name="readOnly", default=False)

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    @classmethod
    def from_message(cls, message):
        """
        Create domain object from a protojson message
        Args:
            message(dict(str, str)): proto json

        Returns:
            (EnergyworxDomain): a domain object
        """
        cls = EnergyworxDomainMeta('EnergyworxDomain', (EnergyworxDomain, ), message)
        kwargs = {}
        for prop_name, value in message.items():
           
            #print('property {prop_name}, value: {value}'.format(prop_name=prop_name, value=value))
            #attr = cls.attr_by_prop_name.get(prop_name) or (super(cls, cls).attr_by_prop_name.get(prop_name))
            attr = cls.attr_by_prop_name.get(prop_name)
            if not attr:
                print('Property name {prop_name} can not be mapped to a domain attribute on domain class {class_name}'.format(prop_name=prop_name, class_name=cls.__name__))
            #prop = cls.prop_by_attr.get(attr) or (super(cls, cls).prop_by_attr.get(attr))
            prop = cls.prop_by_attr.get(attr)
            if not prop:
                print('Attribute {attr_name} can not be mapped to a property instance on domain class {class_name}'.format(attr_name=attr, class_name=cls.__name__))

            if isinstance(prop, StructuredProperty):
                if prop.repeated:
                    try:
                        kwargs.update({attr: [prop.domain_class.from_message(v) for v in value]})
                    except:
                        print(value)
                else:
                    kwargs.update({attr: prop.domain_class.from_message(value)})
            elif isinstance(prop, EnumProperty):
                kwargs.update({attr: str_to_enum(prop.enum_type, value)})
            elif isinstance(prop, DateTimeProperty):
                kwargs.update({attr: parse(value)})
            else:
                kwargs.update({attr: value})
        #return cls(kwargs)
        return(kwargs)

    def to_message(self):
        """
        Create a dict based on property name and attribute
        Returns:
            (dict): a dict based on property name and attribute value
        """
        prop_by_attr = {}
        prop_by_attr.update(self.prop_by_attr.items())
        if not prop_by_attr.get('id') and EnergyworxDomain in self.__class__.__bases__:
            prop_by_attr['id'] = super(self.__class__, self).prop_by_attr.get('id')

        message = {}
        for attr, prop in prop_by_attr.items():
            if isinstance(prop, StructuredProperty):
                if prop.repeated:
                    message.update({prop.name: [item.to_message() for item in getattr(self, attr)]})
                else:
                    message.update({prop.name: getattr(self, attr).to_message()})
            elif isinstance(prop, EnumProperty):
                message.update({prop.name: getattr(self, attr).name if getattr(self, attr) else None})
            elif isinstance(prop, DateTimeProperty):
                message.update({prop.name: getattr(self, attr).replace(tzinfo=None).strftime('%Y-%m-%dT%H:%M:%S.%f') if getattr(self, attr) else None})
            elif getattr(self, attr):
                message.update({prop.name: getattr(self, attr)})
        return message
