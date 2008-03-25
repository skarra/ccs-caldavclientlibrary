##
# Copyright (c) 2007-2008 Apple Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

from protocol.webdav.multiresponseparser import MultiResponseParser
from protocol.webdav.definitions import davxml
from protocol.http.util import parseStatusLine
from xml.etree.ElementTree import QName
from protocol.url import URL

class PropFindParser(MultiResponseParser):

    textProperties = set()
    hrefProperties = set()
    hrefListProperties = set()

    class PropFindResult(object):
        
        def __init__(self):
            self.textProperties = {}
            self.hrefProperties = {}
            self.nodeProperties = {}
            self.badProperties = {}

        def setResource(self, resource):
            self.resource = resource
        def getResource(self):
            return self.resource
        
        def addTextProperty(self, name, value):
            self.textProperties[name] = value
        def getTextProperties(self):
            return self.textProperties

        def addHrefProperty(self, name, value):
            self.hrefProperties[name] = value
        def getHrefProperties(self):
            return self.hrefProperties

        def addNodeProperty(self, name, node):
            self.nodeProperties[name] = node
        def getNodeProperties(self):
            return self.nodeProperties

        def addBadProperty(self, name, status):
            self.badProperties[name] = status
        def getBadProperties(self):
            return self.badProperties

    def __init__(self):
        self.results = {}
    
    def getResults(self):
        return self.results

    # Parse the response element down to the properties
    def parseResponse(self, response):
        # Verify that the node is the correct element <DAV:response>
        if response.tag != davxml.response:
            return
        
        # Node is the right type, so iterate over all child response nodes and process each one
        result = PropFindParser.PropFindResult()
        for child in response.getchildren():

            # Is it the href
            if child.tag == davxml.href:
                result.setResource(child.text)
            
            # Is it propstat
            elif child.tag == davxml.propstat:
                self.parsePropStat(child, result)
        
        # Add the resource only if we got one
        if result.getResource():
            self.results[result.getResource()] = result

    def parsePropStat(self, propstat, result):
        # Scan the propstat node the status - we only process OK status
    
        # Now look for a <DAV:status> element in its children
        status = propstat.find(str(davxml.status))
        
        # Now parse the response and dispatch accordingly
        if status is not None:

            status_result = parseStatusLine(status.text)
            badstatus = status_result if status_result / 100 != 2 else None

            # Now look for a <DAV:prop> element in its children
            for item in propstat.findall(str(davxml.prop)):
                self.parseProp(item, result, badstatus)                

    def parseProp(self, property, result, badstatus):
        # Scan the prop node - each child is processed
        for item in property.getchildren():
            self.parsePropElement(item, result, badstatus)
    
    # Parsing of property elements
    def parsePropElement(self, prop, result, badstatus):
        # Here we need to detect the type of element and dispatch accordingly
        if badstatus:
            result.addBadProperty(QName(prop.tag), badstatus)

        elif prop.tag in PropFindParser.textProperties:
            self.parsePropElementText(prop, result)

        elif prop.tag in PropFindParser.hrefProperties:
            self.parsePropElementHref(prop, result, False)

        elif prop.tag in PropFindParser.hrefListProperties:
            self.parsePropElementHref(prop, result, True)

        else:
            self.parsePropElementUnknown(prop, result)

    def parsePropElementText(self, prop, result):
        # Grab the element data
        result.addTextProperty(QName(prop.tag), prop.text if prop.text else "")
        result.addNodeProperty(QName(prop.tag), prop)

    def parsePropElementHref(self, prop, result, is_list):
        # Grab the element data
        hrefs = tuple([URL(url=href.text, decode=True) for href in prop.findall(str(davxml.href))])
        if not is_list:
            if len(hrefs) == 1:
                hrefs = hrefs[0]
            else:
                hrefs = ""
        result.addHrefProperty(QName(prop.tag), hrefs)
        result.addNodeProperty(QName(prop.tag), prop)

    def parsePropElementUnknown(self, prop, result):
        # Just add the node
        result.addNodeProperty(QName(prop.tag), prop)
