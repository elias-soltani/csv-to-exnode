"""
 A script to read a csv with data points and outputs exf.
"""

# from meshrefine.src.meshrefine import refine_and_export
from opencmiss.zinc.context import Context as ZincContext
from opencmiss.utils.zinc.field import findOrCreateFieldCoordinates, findOrCreateFieldGroup
from opencmiss.zinc.field import Field
from opencmiss.zinc.node import Node
from opencmiss.zinc.element import Element, Elementbasis
import csv
import os

class CsvToExf:
    def __init__(self, file, nodeOffset, elementOffset):
        element_required = False
        fileName = os.path.basename(file)
        dirname = os.path.dirname(file)
        self._inputFile = file
        self._context = ZincContext("CsvToEx")
        self._region = self._context.getDefaultRegion()
        self._fieldmodule = self._region.getFieldmodule()
        self._onlyCoordinates = True

        coordinates = findOrCreateFieldCoordinates(self._fieldmodule, components_count=3)
        cache = self._fieldmodule.createFieldcache()
        #################
        # Create nodes
        #################

        nodes = self._fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        nodetemplate = nodes.createNodetemplate()
        nodetemplate.defineField(coordinates)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_VALUE, 1)
        if not self._onlyCoordinates:
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS1, 1)

        mesh = self._fieldmodule.findMeshByDimension(1)
        if element_required:
            if self._onlyCoordinates:
                basis = self._fieldmodule.createElementbasis(1, Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE)
            else:
                basis = self._fieldmodule.createElementbasis(1, Elementbasis.FUNCTION_TYPE_CUBIC_HERMITE)
            eft = mesh.createElementfieldtemplate(basis)
            elementtemplate = mesh.createElementtemplate()
            elementtemplate.setElementShapeType(Element.SHAPE_TYPE_LINE)
            result = elementtemplate.defineField(coordinates, -1, eft)

            elementIdentifier = elementOffset
        nodeIdentifier = nodeOffset
        with open(self._inputFile, 'r') as csvf:
            reader = csv.reader(csvf)
            next(reader, None)
            for point in reader:
                if nodeIdentifier == nodeOffset:
                    x0 = [float(p) for p in point]
                    nodeIdentifier += 1
                elif nodeIdentifier == nodeOffset + 1:
                    x1 = [float(p) for p in point]
                    node = nodes.createNode(nodeIdentifier - 1, nodetemplate)
                    cache.setNode(node)
                    coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_VALUE, 1, x0)
                    if not self._onlyCoordinates:
                        dx_ds1 = [x1[c] - x0[c] for c in range(3)]
                        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS1, 1, dx_ds1)
                    node = nodes.createNode(nodeIdentifier, nodetemplate)
                    cache.setNode(node)
                    coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_VALUE, 1, x1)
                    if not self._onlyCoordinates:
                        dx_ds1 = [x1[c] - x0[c] for c in range(3)]
                        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS1, 1, dx_ds1)
                    x0 = [d for d in x1]
                    nodeIdentifier = nodeIdentifier + 1
                    if element_required:
                        element = mesh.createElement(elementIdentifier, elementtemplate)
                        element.setNodesByIdentifier(eft, [nodeIdentifier - 1, nodeIdentifier])
                        elementIdentifier = elementIdentifier + 1
                else:
                    x1 = [float(p) for p in point]
                    node = nodes.createNode(nodeIdentifier, nodetemplate)
                    cache.setNode(node)
                    coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_VALUE, 1, x1)
                    if not self._onlyCoordinates:
                        dx_ds1 = [x1[c] - x0[c] for c in range(3)]
                        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS1, 1, dx_ds1)
                    x0 = [d for d in x1]
                    nodeIdentifier = nodeIdentifier + 1
                    if element_required:
                        element = mesh.createElement(elementIdentifier, elementtemplate)
                        element.setNodesByIdentifier(eft, [nodeIdentifier - 1, nodeIdentifier])
                        elementIdentifier = elementIdentifier + 1

        outputFile = os.path.join(dirname, fileName.split('.')[0]+'.exf')
        self._region.writeFile(outputFile)


