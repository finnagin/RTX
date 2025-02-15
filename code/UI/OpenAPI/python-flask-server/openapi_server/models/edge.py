# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.attribute import Attribute
from openapi_server import util

from openapi_server.models.attribute import Attribute  # noqa: E501

class Edge(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, predicate=None, relation=None, subject=None, object=None, attributes=None):  # noqa: E501
        """Edge - a model defined in OpenAPI

        :param predicate: The predicate of this Edge.  # noqa: E501
        :type predicate: str
        :param relation: The relation of this Edge.  # noqa: E501
        :type relation: str
        :param subject: The subject of this Edge.  # noqa: E501
        :type subject: str
        :param object: The object of this Edge.  # noqa: E501
        :type object: str
        :param attributes: The attributes of this Edge.  # noqa: E501
        :type attributes: List[Attribute]
        """
        self.openapi_types = {
            'predicate': str,
            'relation': str,
            'subject': str,
            'object': str,
            'attributes': List[Attribute]
        }

        self.attribute_map = {
            'predicate': 'predicate',
            'relation': 'relation',
            'subject': 'subject',
            'object': 'object',
            'attributes': 'attributes'
        }

        self._predicate = predicate
        self._relation = relation
        self._subject = subject
        self._object = object
        self._attributes = attributes

    @classmethod
    def from_dict(cls, dikt) -> 'Edge':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Edge of this Edge.  # noqa: E501
        :rtype: Edge
        """
        return util.deserialize_model(dikt, cls)

    @property
    def predicate(self):
        """Gets the predicate of this Edge.


        :return: The predicate of this Edge.
        :rtype: str
        """
        return self._predicate

    @predicate.setter
    def predicate(self, predicate):
        """Sets the predicate of this Edge.


        :param predicate: The predicate of this Edge.
        :type predicate: str
        """

        self._predicate = predicate

    @property
    def relation(self):
        """Gets the relation of this Edge.

        The relationship type term of this edge, originally specified by, or curated by inference from, the original source of knowledge. This should generally be specified as predicate ontology CURIE.  # noqa: E501

        :return: The relation of this Edge.
        :rtype: str
        """
        return self._relation

    @relation.setter
    def relation(self, relation):
        """Sets the relation of this Edge.

        The relationship type term of this edge, originally specified by, or curated by inference from, the original source of knowledge. This should generally be specified as predicate ontology CURIE.  # noqa: E501

        :param relation: The relation of this Edge.
        :type relation: str
        """

        self._relation = relation

    @property
    def subject(self):
        """Gets the subject of this Edge.

        Corresponds to the map key CURIE of the subject concept node of this relationship edge.  # noqa: E501

        :return: The subject of this Edge.
        :rtype: str
        """
        return self._subject

    @subject.setter
    def subject(self, subject):
        """Sets the subject of this Edge.

        Corresponds to the map key CURIE of the subject concept node of this relationship edge.  # noqa: E501

        :param subject: The subject of this Edge.
        :type subject: str
        """
        if subject is None:
            raise ValueError("Invalid value for `subject`, must not be `None`")  # noqa: E501

        self._subject = subject

    @property
    def object(self):
        """Gets the object of this Edge.

        Corresponds to the map key CURIE of the object concept node of this relationship edge.  # noqa: E501

        :return: The object of this Edge.
        :rtype: str
        """
        return self._object

    @object.setter
    def object(self, object):
        """Sets the object of this Edge.

        Corresponds to the map key CURIE of the object concept node of this relationship edge.  # noqa: E501

        :param object: The object of this Edge.
        :type object: str
        """
        if object is None:
            raise ValueError("Invalid value for `object`, must not be `None`")  # noqa: E501

        self._object = object

    @property
    def attributes(self):
        """Gets the attributes of this Edge.

        A list of additional attributes for this edge  # noqa: E501

        :return: The attributes of this Edge.
        :rtype: List[Attribute]
        """
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        """Sets the attributes of this Edge.

        A list of additional attributes for this edge  # noqa: E501

        :param attributes: The attributes of this Edge.
        :type attributes: List[Attribute]
        """

        self._attributes = attributes
