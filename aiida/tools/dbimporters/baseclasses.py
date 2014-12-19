# -*- coding: utf-8 -*-

__copyright__ = u"Copyright (c), 2014, École Polytechnique Fédérale de Lausanne (EPFL), Switzerland, Laboratory of Theory and Simulation of Materials (THEOS). All rights reserved."
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file"
__version__ = "0.3.0"

class DbImporter(object):
    """
    Base class for database importers.
    """

    def query(self, **kwargs):
        """
        Method to query the database.

        :param id: database-specific entry identificator
        :param element: element name from periodic table of elements
        :param number_of_elements: number of different elements
        :param mineral_name: name of mineral
        :param chemical_name: chemical name of substance
        :param formula: chemical formula
        :param volume: volume of the unit cell in cubic angstroms
        :param spacegroup: symmetry space group symbol in Hermann-Mauguin
            notation
        :param spacegroup_hall: symmetry space group symbol in Hall
            notation
        :param a, b, c: length of lattice vectors in angstroms
        :param alpha, beta, gamma: angles between lattice vectors in
            degrees
        :param z: number of the formula units in the unit cell
        :param measurement_temp: temperature in kelvins at which the
            unit-cell parameters were measured
        :param measurement_pressure: pressure in kPa at which the
            unit-cell parameters were measured
        :param diffraction_temp: mean temperature in kelvins at which
            the intensities were measured
        :param diffraction_pressure: mean pressure in kPa at which the
            intensities were measured
        :param authors: authors of the publication
        :param journal: name of the journal
        :param title: title of the publication
        :param year: year of the publication
        :param journal_volume: journal volume of the publication
        :param journal_issue: journal issue of the publication
        :param first_page: first page of the publication
        :param last_page: last page of the publication
        :param doi: digital object identifyer (DOI), refering to the
            pulication

        :raises NotImplementedError: if search using given keyword is not
            implemented.
        """
        raise NotImplementedError("not implemented in base class")

    def setup_db(self, **kwargs):
        """
        Sets the database parameters. The method should reconnect to the
        database using updated parameters, if already connected.
        """
        raise NotImplementedError("not implemented in base class")

    def get_supported_keywords(self):
        """
        Returns the list of all supported query keywords.

        :return: list of strings
        """
        raise NotImplementedError("not implemented in base class")

class DbSearchResults(object):
    """
    Base class for database results.
    """

    def __iter__(self):
        """
        Instances of
        :py:class:`aiida.tools.dbimporters.baseclasses.DbSearchResults` can
        be used as iterators.
        """
        return self

    def fetch_all(self):
        """
        Returns all query results as an array of
        :py:class:`aiida.tools.dbimporters.baseclasses.DbEntry`.
        """
        results = []
        for entry in self:
            results.append(entry)
        return results

    def next(self):
        """
        Returns next result as
        :py:class:`aiida.tools.dbimporters.baseclasses.DbEntry`.

        :raise StopIteration: when the end of result array is reached.
        """
        if len( self.results ) > self.position:
            self.position = self.position + 1
            return self.at( self.position - 1 )
        else:
            raise StopIteration()

    def at(self, position):
        """
        Returns ``position``-th result as
        :py:class:`aiida.tools.dbimporters.baseclasses.DbEntry`.

        :param position: zero-based index of a result.

        :raise IndexError: if ``position`` is out of bounds.
        """
        raise NotImplementedError("not implemented in base class")

class DbEntry(object):
    """
    Represents an entry from the structure database (COD, ICSD, ...).
    """

    def __init__(self, **kwargs):
        """
        Sets the basic parameters for the database entry:

        :param source: identifying the location and version of the source
          for the entry, containing:
          * db_source: name of the source database
          * db_url: URL of the source database
          * db_id: structure identifyer in the database
          * db_version: version of the database
          * extras: a dictionary with some extra parameters (e.g. database ID number)
          * url: URL of the structure (should be permanent)
        """
        self.source = {
            'db_source' : None,
            'db_url'    : None,
            'db_id'     : None,
            'db_version': None,
            'extras'    : {},
            'url'       : None,
            'source_md5': None,
        }
        self._cif = None

    @property
    def cif(self):
        """
        Returns raw contents of a CIF file as string.
        """
        if self._cif is None:
            import urllib2
            self._cif = urllib2.urlopen( self.source['url'] ).read()
        return self._cif

    def get_raw_cif(self):
        """
        Returns raw contents of a CIF file as string.

        :return: contents of a file as string
        """
        return self.cif

    def get_ase_structure(self):
        """
        Returns ASE representation of the CIF.
        """
        raise NotImplementedError("not implemented in base class")

    def get_cif_node(self):
        """
        Creates a CIF node, that can be used in AiiDA workflow.

        :return: :py:class:`aiida.orm.data.cif.CifData` object
        """
        from aiida.common.utils import md5_file
        from aiida.orm.data.cif import CifData
        import tempfile
        with tempfile.NamedTemporaryFile() as f:
            f.write(self.cif)
            f.flush()
            self.source['source_md5'] = md5_file(f.name)
            return CifData(file=f.name, source=self.source)

    def get_aiida_structure(self):
        """
        Returns AiiDA-compatible structure, representing the crystal
        structure from the CIF file.
        """
        raise NotImplementedError("not implemented in base class")

    def get_parsed_cif(self):
        """
        Returns data structure, representing the CIF file. Can be created
        using PyCIFRW or any other open-source parser.

        :return: list of lists
        """
        raise NotImplementedError("not implemented in base class")
