# -*- coding: utf-8 -*-
"""
This module provides material and material package classes that can do size distribution and slurry calculations.\n

@name: psd slurrymaterial
@author: Ex Mente Technologies (Pty) Ltd
"""

import os
import sys
import numpy
import copy
from auxi.core.object import Object
from auxi.core.namedobject import NamedObject

__version__ = "0.2.0"


# =============================================================================
# Types.
# =============================================================================

class Material(NamedObject):
    """Represents a particulate material consisting of multiple particle size classes.\n
    Properties defined here:\n
    name               : The material's name.
    size_classes       : The material's list of particle size classes.
    size_classes_count : The number of particle size classes in the material.
    assays             : A dictionary containing assays (size distributions) for this material.
    """

    # -------------------------------------------------------------------------
    # Standard methods.
    # -------------------------------------------------------------------------
    def __init__(self, name, file_path):
        """Initialise the object from a text file containing particle size classes and assays.
        The format of the text file is as follows:
        * The lines are space separated. The values in a line are separated by one or more spaces.
        * The first line is a heading line.
		* The second line contains the density of the solid material.
		* The third line contains the water fraction of the slurry (wet basis).
        * All subsequent lines contain a particle size, followed by mass fractions (dry basis).
        * Particle sizes are indicated in [meter].
        * The first column lists the particle sizes in the material. Each class
          must be interpreted as "mass fraction retained". In other words if the
          size class is indicated as 307.2E-3, it means that it is the class of
          material retained on a 307.2mm screen, and can also be though of as
          +307.2mm material. The first size class represents the largest particles.
          The final size class should be zero, as it represents
          all material that passed through the smallest aperture screen.
        * All subsequent columns describe assays of the material.
        The following is an example of a material text file:
        SizeClass       DryFeedA  DryMillCharge  WetFeedA  WetMillCharge  Water
        solid_density   3.00      3.00           3.00      3.00           1.0.
        H2O             0.00      0.00           0.80      0.60           1.00
        307.2E-3        0.20      0.02           0.20      0.02           0.00
        108.6E-3        0.18      0.06           0.18      0.06           0.00
        38.4E-3         0.17      0.04           0.17      0.04           0.00
        13.6E-3         0.07      0.03           0.07      0.03           0.00
        4.8E-3          0.13      0.03           0.13      0.03           0.00
        1.7E-3          0.07      0.04           0.07      0.04           0.00
        600.0E-6        0.06      0.18           0.06      0.18           0.00
        210.0E-6        0.02      0.50           0.02      0.50           0.00
        75.0E-6         0.10      0.09           0.10      0.09           0.00
        0.0E0           0.00      0.00           0.00      0.00           0.00
        """

        # Initialise the material's properties.
        self.name = name
        self.size_classes = list()

        # Read the material's data from the file and prepare it for use.
        f = open(file_path, "r")
        lines = f.readlines()
        f.close()
        lines = self._prepare_lines(lines)

        # Determine the assay names, and create a dictionary entry for each assay.
        assay_names = lines[0].split(" ")
        del(assay_names[0:1])
        self.psds = dict()
        self.solid_densities = dict()
        self.H2O_fractions = dict()
        for assay_name in assay_names:
            self.psds[assay_name] = numpy.array([])
            self.solid_densities[assay_name] = 1.0
            self.H2O_fractions[assay_name] = 0.0

        # Read the solid densities of the assays.
        strings = lines[1].split(" ")
        if not strings[0] == "solid_density":
            raise Exception("Invalid data file. The second line of the data file must start with 'solid_density'.")
        for j in range(0, len(self.solid_densities)): # Add the solid densities.
            assay_name = assay_names[j]
            self.solid_densities[assay_name] = float(strings[j+1])

        # Read the water fractions of the assays.
        strings = lines[2].split(" ")
        if not strings[0] == "H2O":
            raise Exception("Invalid data file. The third line of the data file must start with 'H2O'.")
        for j in range(0, len(self.H2O_fractions)): # Add the water fractions.
            assay_name = assay_names[j]
            self.H2O_fractions[assay_name] = float(strings[j+1])

        # Read the size classes and mass fractions.
        for i in range(3, len(lines)):
            strings = lines[i].split(" ")
            if len(strings) < len(assay_names) + 1: # Not a full line.
                continue
            self.size_classes.append(float(strings[0])) # Add the new size class.
            for j in range(0, len(self.psds)):    # Add the mass fractions to the assays.
                assay_name = assay_names[j]
                self.psds[assay_name] = numpy.append(self.psds[assay_name], float(strings[j+1]))

        # Initialise the remaining properties.
        self.size_class_count = len(self.size_classes)


    def __str__(self):
        """Create a string representation of self."""
        result = "Material: name='" + self.name + "'\n"

        # Create the header line of the table.
        result = result + "Compound".ljust(20)
        assay_names = sorted(self.psds.keys())
        for assay_name in assay_names:
            result = result + assay_name.ljust(20)
        result = result + "\n"

        # Create the solid density line.
        result = result + "Solid density".ljust(20)
        assay_names = sorted(self.psds.keys())
        for assay_name in assay_names:
            result = result + str(self.solid_densities[assay_name]).ljust(20)
        result = result + "\n"

        # Create the H2O fraction line.
        result = result + "H2O fraction".ljust(20)
        assay_names = sorted(self.psds.keys())
        for assay_name in assay_names:
            result = result + str(self.H2O_fractions[assay_name]).ljust(20)
        result = result + "\n"

        # Create the content lines of the table.
        for size_class in self.size_classes:
            result = result + str(size_class).ljust(20)
            compound_index = self.get_size_class_index(size_class)
            for assay_name in assay_names:
                result = result + str(self.psds[assay_name][compound_index]).ljust(20)
            result = result + "\n"
        return result


    # -------------------------------------------------------------------------
    # Private methods.
    # -------------------------------------------------------------------------
    def _prepare_lines(self, lines):
        """Prepare the lines read from the text file before starting to process it."""

        result = list()
        for line in lines:
            line = line.strip()                 # Remove all whitespace characters (e.g. spaces, line breaks, etc.) from the start and end of the line.
            line = line.replace("\t", " ")      # Replace all tabs with spaces.
            while line.find("  ") > -1:         # Replace all repeating spaces with a single space.
                line = line.replace("  ", " ")
            result.append(line)
        return result


    # -------------------------------------------------------------------------
    # Public methods.
    # -------------------------------------------------------------------------
    def get_size_class_index(self, size_class):
        """Determine the index of the specified size class.\n
        size class : The formula and phase of the specified size class, e.g. Fe2O3[S1].\n
        return   : The index of the specified size class.
        """

        return self.size_classes.index(size_class)


    def create_empty_psd(self):
        """Create an empty array to store a psd. The array's length will be equal to the number of size classes in the material.\n
        return : A floating point array.
        """

        return numpy.zeros(self.size_class_count)


    def add_assay(self, name, solid_density, H2O_fraction, psd):
        """Add an assay to the material.\n
        name  : The name of the new assay.
        psd   : A numpy array containing the size class mass fractions for the assay. The sequence of the assay's elements must correspond to the sequence of the material's size classes.
        """

        if not type(solid_density) is float:
            raise Exception("Invalid solid density. It must be a float.")
        self.solid_densities[name] = solid_density

        if not type(H2O_fraction) is float:
            raise Exception("Invalid H2O fraction. It must be a float.")
        self.H2O_fractions[name] = H2O_fraction

        if not type(psd) is numpy.ndarray:
            raise Exception("Invalid psd. It must be a numpy array.")
        elif not psd.shape == (self.size_class_count,):
            raise Exception("Invalid psd: It must have the same number of elements as the material has size classes.")
        elif name in self.psds.keys():
            raise Exception("Invalid psd: An assay with that name already exists.")
        self.psds[name] = psd


    def get_psd_total(self, name):
        """Calculate the total of the specified assay's psd.\n
        name   : The name of the assay.\n
        return : The total mass fraction of the specified assay.
        """

        return sum(self.psds[name])


    def create_package(self, assay = None, mass = 0.0, normalise=True):
        """Create a MaterialPackage based on the specified parameters.\n
        assay     :       The name of the assay based on which the package must be created.
        mass      : [kg]  The mass of the package.
        normalise :       Indicates whether the assay must be normalised before creating the package.\n
        return    :       The created MaterialPackage.
        """

        if assay == None:
            return MaterialPackage(self, 1.0, 0.0, self.create_empty_assay())

        if normalise:
            psd_total = self.get_psd_total(assay)
            if psd_total == 0.0:
                psd_total = 1.0
        else:
            psd_total = 1.0
        H2O_mass = mass * self.H2O_fractions[assay]
        solid_mass = mass - H2O_mass
        return MaterialPackage(self,
                               self.solid_densities[assay],
                               H2O_mass,
                               solid_mass * self.psds[assay] / psd_total)



class MaterialPackage(Object):

    # -------------------------------------------------------------------------
    # Standard methods.
    # -------------------------------------------------------------------------
    def __init__(self, material, solid_density, H2O_mass, size_class_masses):
        """Initialise the object.\n
        material        :       A reference to the Material to which self belongs.
        size_class_masses : [kg]  The masses of the size classes in the package.
        """

        # Confirm that the parameters are OK.
        if not type(material) is Material:
            raise TypeError("Invalid material type. Must be psdslurrymaterial.Material")
        if not type(size_class_masses) is numpy.ndarray:
            raise TypeError("Invalid size_class_masses type. Must be numpy.ndarray.")

        # Initialise the object's properties.
        self.material = material
        self.solid_density = solid_density
        self.H2O_mass = H2O_mass
        self.size_class_masses = size_class_masses


    def __str__(self):
        """Create a string representation of the object."""
        result = "MaterialPackage\n"
        result = result + "material".ljust(24) + self.material.name + "\n"
        result = result + "mass fraction solids".ljust(24) + str(self.get_mass_fraction_solids()) + "\n"
        result = result + "volume fraction solids".ljust(24) + str(self.get_volume_fraction_solids()) + "\n"
        result = result + "solid density".ljust(24) + str(self.solid_density) + "\n"
        result = result + "slurry density".ljust(24) + str(self.get_density()) + "\n"
        result = result + "mass".ljust(24) + str(self.get_mass()) + "\n"
        result = result + "H2O mass".ljust(24) + str(self.H2O_mass) + "\n"
        result = result + "volume".ljust(24) + str(self.get_volume()) + "\n"
        result = result + "Component masses:\n"
        for size_class in self.material.size_classes:
            index = self.material.get_size_class_index(size_class)
            result = result + str(size_class).ljust(24) + str(self.size_class_masses[index]) + "\n"
        return result


    # -------------------------------------------------------------------------
    # Operators.
    # -------------------------------------------------------------------------
    def __add__(self, other):
        """Addition operator (+).
        Add self and 'other' together, return the result as a new package, and leave self unchanged.\n
        other  : Can can be one of the following:
                 1. MaterialPackage
                    'other' is added to self to create a new package.
                 2. tuple: (size class, mass)
                    The specified mass of the specified size class is added to self.
        return : A new Material package that is the sum of self and 'other'.
        """

        # Add another package.
        if type(other) is MaterialPackage:
            solid_density = (self.get_solid_mass() + other.get_solid_mass()) / (self.get_solid_mass() / self.solid_density + other.get_solid_mass() / other.solid_density)
            H2O_mass = self.H2O_mass + other.H2O_mass
            if self.material == other.material: # Packages of the same material.
                result =  MaterialPackage(self.material, solid_density, H2O_mass, self.size_class_masses + other.size_class_masses)
                return result
            else: # Packages of different materials.
                result = self.clone()
                result.solid_density = solid_density
                result.H2O_mass = H2O_mass
                for size_class in other.material.size_classes:
                    if size_class not in self.material.size_classes:
                        raise Exception("Packages of '" + other.material.name + "' cannot be added to packages of '" + self.material.name + "'. The size class '" + size_class + "' was not found in '" + self.material.name + "'.")
                    result = result + (size_class, other.get_size_class_mass(size_class))
                return result

        # Add the specified mass of water.
        elif self._is_H2O_mass_tuple(other):
            # Added material variables.
            mass = other[1]

            # Create the result package.
            result = self.clone()
            result.H2O_mass += mass
            return result

        # Add the specified mass of the specified size class.
        elif self._is_size_class_mass_tuple(other):
            # Added material variables.
            size_class = other[0]
            compound_index = self.material.get_size_class_index(size_class)
            mass = other[1]

            # Create the result package.
            result = self.clone()
            result.size_class_masses[compound_index] = result.size_class_masses[compound_index] + mass
            return result

        # If not one of the above, it must be an invalid argument.
        else:
            raise TypeError("Invalid addition argument.")


    def __mul__(self, scalar):
        """The multiplication operator (*).
        Create a new package by multiplying self with other.\n
        scalar : The result is a new package with its content equal to self multiplied by a scalar, leaving self unchanged.\n
        result : A new MaterialPackage equal to self package multiplied by other.
        """

        # Multiply with a scalar floating point number.
        if type(scalar) is float or type(scalar) is numpy.float64 or type(scalar) is numpy.float32:
            if scalar < 0.0:
                raise Exception("Invalid multiplication operation. Cannot multiply package with negative number.")
            result = MaterialPackage(self.material, self.solid_density, self.H2O_mass * scalar, self.size_class_masses * scalar)
            return result

        # If not one of the above, it must be an invalid argument.
        else:
            raise TypeError("Invalid multiplication argument.")


    # -------------------------------------------------------------------------
    # Private methods.
    # -------------------------------------------------------------------------
    def _is_size_class_mass_tuple(self, value):
        """Determines whether value is a tuple of the format (size class(float), mass(float))."""

        if not type(value) is tuple:
            return False
        elif not len(value) == 2:
            return False
        elif not type(value[0]) is float:
            return False
        elif not type(value[1]) is float and not type(value[1]) is numpy.float64 and not type(value[1]) is numpy.float32:
            return False
        else:
            return True


    def _is_H2O_mass_tuple(self, value):
        """Determines whether value is a tuple of the format (size class(float), mass(float))."""

        if not type(value) is tuple:
            return False
        elif not len(value) == 2:
            return False
        elif not type(value[0]) is str and not value[0] == "H2O":
            return False
        elif not type(value[1]) is float and not type(value[1]) is numpy.float64 and not type(value[1]) is numpy.float32:
            return False
        else:
            return True


    # -------------------------------------------------------------------------
    # Public methods.
    # -------------------------------------------------------------------------
    def clone(self):
        """Create a complete copy of self.\n
        return : A MaterialPackage that is identical to self."""

        result = copy.copy(self)
        result.size_class_masses = copy.deepcopy(self.size_class_masses)
        return result


    # TODO: document
    # TODO: test
    def clear(self):
        self.solid_density = 1.0
        self.H2O_mass = 0.0
        self.size_class_masses = self.size_class_masses * 0.0


    def get_psd(self):
        """Determine the assay of self.\n
        return : [mass fractions] An array containing the psd of self.
        """

        return self.size_class_masses / self.size_class_masses.sum()


    def get_mass(self):
        """Determine the mass of self.\n
        return : [kg] The mass of self.
        """

        return self.size_class_masses.sum() + self.H2O_mass


    def get_solid_mass(self):
        """Determine the solid mass of self.\n
        return : [kg] The solid mass of self.
        """

        return self.size_class_masses.sum()


    def get_size_class_mass(self, size_class):
        """Determine the mass of the specified size class in self.\n
        size class :      The formula and phase of the size class, e.g. Fe2O3[S1]\n
        return   : [kg] The mass of the size class in self.
        """

        return self.size_class_masses[self.material.get_size_class_index(size_class)]


    # TODO: Test
    def get_size_class_mass_fraction(self, size_class):
        """Determine the mass fraction of the specified size class in self.\n
        size class : The formula and phase of the size class, e.g. Fe2O3[S1]\n
        return   : The mass fraction of the size class in self.
        """

        return self.get_size_class_mass(size_class) / self.get_solid_mass()


    def get_density(self):
        return self.get_mass() / self.get_volume()


    def get_mass_fraction_solids(self):
        return self.get_solid_mass() / self.get_mass()


    def get_volume(self):
        return self.H2O_mass / 1.0 + self.get_solid_mass() / self.solid_density


    def get_volume_fraction_solids(self):
        return 1.0 - (self.H2O_mass / 1.0) / self.get_volume()


    def extract(self, other):
        """Extract some material from self.
        Extract 'other' from self, modifying self and returning the extracted material as a new package.\n
        other  : Can be one of the following:
                 1. float
                    A mass equal to other is extracted from self. Self is reduced by other and the extracted package is returned as a new package.
                 2. tuple: (size class, mass)
                    The other tuple specifies the mass of a size class to be extracted. It is extracted from self and the extracted mass is returned as a new package.
                 3. string
                    The 'other' string specifies the size class to be extracted. All of the mass of that size class will be removed from self and a new package created with it.\n
        return : A new material package containing the material that was extracted from self.
        """

        # Extract the specified mass.
        if type(other) is float or type(other) is numpy.float64 or type(other) is numpy.float32:
            if other > self.get_mass():
                raise Exception("Invalid extraction operation. Cannot extract a mass larger than the package's mass.")
            fraction_to_subtract = other / self.get_mass()
            result = MaterialPackage(self.material, self.solid_density, self.H2O_mass * fraction_to_subtract, self.size_class_masses * fraction_to_subtract)
            self.H2O_mass = self.H2O_mass * (1.0 - fraction_to_subtract)
            self.size_class_masses = self.size_class_masses * (1.0 - fraction_to_subtract)
            return result

        # Extract the specified mass of water.
        elif self._is_H2O_mass_tuple(other):
            if other[1] > self.H2O_mass:
                raise Exception("Invalid extraction operation. Cannot extract a water mass larger than what the package contains.")
            self.H2O_mass = self.H2O_mass - other[1]
            resultarray = self.size_class_masses * 0.0
            result = MaterialPackage(self.material, self.solid_density, other[1], resultarray)
            return result

        # Extract the specified mass of the specified size class.
        elif self._is_size_class_mass_tuple(other):
            index = self.material.get_size_class_index(other[0])
            if other[1] > self.size_class_masses[index]:
                raise Exception("Invalid extraction operation. Cannot extract a size class mass larger than what the package contains.")
            self.size_class_masses[index] = self.size_class_masses[index] - other[1]
            resultarray = self.size_class_masses*0.0
            resultarray[index] = other[1]
            result = MaterialPackage(self.material, self.solid_density, 0.0, resultarray)
            return result

        # Extract all of the specified size class.
        elif type(other) is str:
            index = self.material.get_size_class_index(float(other))
            result = self * 0.0
            result.size_class_masses[index] = self.size_class_masses[index]
            self.size_class_masses[index] = 0.0
            return result

        # If not one of the above, it must be an invalid argument.
        else:
            raise TypeError("Invalid extraction argument.")


    # TODO: Test
    # TODO: Document
#    def add_to(self, other):
#        # Add another package.
#        if type(other) is MaterialPackage:
#            if self.material == other.material: # Packages of the same material.
#                self.size_class_masses = self.size_class_masses + other.size_class_masses
#            else: # Packages of different materials.
#                for size_class in other.material.size_classes:
#                    if size_class not in self.material.size_classes:
#                        raise Exception("Packages of '" + other.material.name + "' cannot be added to packages of '" + self.material.name + "'. The size class '" + size_class + "' was not found in '" + self.material.name + "'.")
#                    self.add_to((size_class, other.get_size_class_mass(size_class)))
#
#        # Add the specified mass of the specified size class.
#        elif self._is_size_class_mass_tuple(other):
#            # Added material variables.
#            size_class = other[0]
#            compound_index = self.material.get_size_class_index(size_class)
#            mass = other[1]
#
#            # Create the result package.
#            self.size_class_masses[compound_index] = self.size_class_masses[compound_index] + mass
#
#        # If not one of the above, it must be an invalid argument.
#        else:
#            raise TypeError("Invalid addition argument.")


def _get_default_data_path():
    module_path = os.path.dirname(sys.modules[__name__].__file__)
    data_path = os.path.join(module_path, r"data")
    data_path = os.path.abspath(data_path)
    return data_path

DEFAULT_DATA_PATH = _get_default_data_path()
