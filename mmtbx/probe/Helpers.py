##################################################################################
#                Copyright 2021  Richardson Lab at Duke University
#
# Licensed under the Apache License, Version 2.0 (the "License"],
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

##################################################################################
# This module exports functions that are helpful to create data structures
# needed by Probe.

from __future__ import print_function, nested_scopes, generators, division
from __future__ import absolute_import
import sys
import iotbx.map_model_manager
import iotbx.data_manager
import cctbx.maptbx.box
import mmtbx
import scitbx.matrix
from scitbx.array_family import flex
from mmtbx.probe import AtomTypes
from iotbx import pdb

import boost_adaptbx.boost.python as bp
bp.import_ext("mmtbx_probe_ext")
import mmtbx_probe_ext as probeExt

def getBondedNeighborLists(atoms, bondProxies):
  """
    Helper function to produce a dictionary of lists that contain all bonded
    neighbors for each atom in a set of atoms.
    :param atoms: Flex array of atoms (could be obtained using model.get_atoms() if there
    are no chains with multiple conformations, must be a subset of the atoms including
    all in the base conformation and in a particular conformation otherwise).
    :param bondProxies: Flex array of bond proxies for the atoms.  This could be obtained
    using model.get_restraints_manager().geometry.get_all_bond_proxies(sites_cart =
    model.get_sites_cart())[0] if the model has only a single conformation.  Otherwise,
    it should be a flex array of atom positions for the atoms that are in the first argument.
    :returns a dictionary with one entry for each atom that contains a list of all of
    the atoms (within the atoms list) that are bonded to it.
  """
  atomDict = {}
  for a in atoms:
    atomDict[a.i_seq] = a
  bondedNeighbors = {}
  for a in atoms:
    bondedNeighbors[a] = []
  for bp in bondProxies:
    try:
      first = atomDict[bp.i_seqs[0]]
      second = atomDict[bp.i_seqs[1]]
      bondedNeighbors[first].append(second)
      bondedNeighbors[second].append(first)
    except Exception:
      # When an atom is bonded to an atom in a different conformer (not in our atom list)
      # we just ignore it.
      pass
  return bondedNeighbors

def compatibleConformations(a1, a2):
  '''
    Returns True if the two atoms are in compatible conformations, False if not.
    :param a1: First atom.
    :param a2: Second atom.
    :return: True if either atom is in the empty conformation or if both are in the
    same conformation.
  '''
  alt1 = a1.parent().altloc
  alt2 = a2.parent().altloc
  if alt1 in ['', ' ']:
    return True
  if alt2 in ['', ' ']:
    return True
  return alt1 == alt2

def getAtomsWithinNBonds(atom, bondedNeighborLists, N, nonHydrogenN = 1e10):
  """
    Helper function to produce a list of all of the atoms that are bonded to the
    specified atoms, or to one of the atoms bonded to the specified atom, recursively
    to a depth of N.  The atom itself will not be included in the list, so an atom that
    has no bonded neighbors will always have an empty result.  This can be used to
    produce a list of excluded atoms for dot scoring.  It checks to ensure that all of
    the bonded atoms are from compatible conformations; note that if the original atom
    is in the empty configuration then this will return atoms from all conformations that
    are in the bonded set.
    :param atom: The atom to be tested.
    :param bondedNeighborLists: Dictionary of lists that contain all bonded neighbors for
    each atom in a set of atoms.  Should be obtained using
    mmtbx.probe.Helpers.getBondedNeighborLists().
    :param N: Depth of recursion.  N=1 will return the atoms bonded to atom.  N=2 will
    also return those bonded to these neighbors (but not the atom itself).
    :param nonHydrogenN: When neither the original atom nor the bonded atom is a Hydrogen,
    limit the depth to this value (if this value is less than N).
    :returns a list of all atoms that are bonded to atom within a depth of N.  The original
    atom is never on the list.
  """
  hFound = atom.element_is_hydrogen()
  # Find all atoms to the specified depth
  atoms = {atom}            # Initialize the set with the atom itself
  for i in range(N):        # Repeat the recursion this many times
    current = list(atoms)   # Make a copy so we're not modifying the list we are traversing
    for a in current:       # Add all neighbors of all atoms in the current level
      for n in bondedNeighborLists[a]:
        # If we find a hydrogen, we no longer use the non-Hydrogen N limit.
        if n.element_is_hydrogen():
          hFound = True
        if i < nonHydrogenN or hFound:
          # Ensure that the new atom is in a compatible conformation with the original atom.
          if compatibleConformations(atom, n):
            atoms.add(n)

  # Remove the original atom from the result and turn the result into a list.
  atoms.discard(atom)
  return list(atoms)

class getExtraAtomInfoReturn(object):
  """
    Return type from getExtraAtomInfo() call.
      extraAtomInfo: ExtraAtomInfoMap with an entry for every atom in the model suitable for
                     passing to the scoring functions.
      warnings: a string that if not empty lists warnings that the person running the program
                might want to know about.  Suitable for printing or logging.
  """
  def __init__(self, extraAtomInfo, warnings):
    self.extraAtomInfo = extraAtomInfo
    self.warnings = warnings

def getExtraAtomInfo(model, useNeutronDistances = False, useImplicitHydrogenDistances = False,
                     useProbeTablesByDefault = False):
  """
    Helper function to provide a mapper for ExtraAtomInfo needed by Probe when scoring
    models.  It first tries to find the information in CCTBX.  If it cannot, it looks
    the information up using the original C-code Probe tables and algorithms.
    :param model: Map Model Manager's Model containing all of the atoms to be described.
    PDB interpretation must have been done on the model, perhaps by calling
    model.process(make_restraints=True), with useNeutronDistances matching
    the parameter to this function.
    :param useNeutronDistances: Default is to use x-ray distances, but setting this to
    True uses neutron distances instead.  This must be set consistently with the
    PDB interpretation parameter used on the model.
    :param useImplicitHydrogenDistances: Default is to use distances consistent with
    explicitly-listed Hydrgoens, but setting this to True implicit-Hydrogen distances instead.
    This must be set consistently with the hydrogens in the model.
    :param useProbeTablesByDefault: Do not attempt to read the data from CCTBX, use the
    original Probe tables.  This is normally the fall-back when it cannot find the data in
    CCTBX.  The Probe tables do not have accurate data on HET atoms, only standard residues.
    The values in the tables may differ from the current CCTBX values, and the Probe tables
    are not being maintained.
    :returns a ExtraAtomInfoMap with an entry for every atom in the model suitable for
    passing to the scoring functions.
  """

  warnings = ""

  # Construct the AtomTypes object we're going to use, telling it whether to use neutron distances.
  at = AtomTypes.AtomTypes(useNeutronDistances, useImplicitHydrogenDistances)

  # Traverse the hierarchy and look up the extra data to be filled in.
  extras = probeExt.ExtraAtomInfoMap([],[])
  mon_lib_srv = model.get_mon_lib_srv()
  ener_lib = mmtbx.monomer_library.server.ener_lib()
  ph = model.get_hierarchy()
  for m in ph.models():
    for chain in m.chains():
      for rg in chain.residue_groups():
        for ag in rg.atom_groups():
          md, ani = mon_lib_srv.get_comp_comp_id_and_atom_name_interpretation(
                residue_name=ag.resname, atom_names=ag.atoms().extract_name())
          atom_dict = md.atom_dict()

          for a in ag.atoms():
            extra = probeExt.ExtraAtomInfo()
            if not useProbeTablesByDefault:
              # See if we can find out about its Hydrogen-bonding status from the
              # model.  If so, we fill it and the vdwRadius information from
              # CCTBX.
              try:
                hb_type = model.get_specific_h_bond_type(a.i_seq)
                if isinstance(hb_type, str):
                  if hb_type == "A" or hb_type == "B":
                    extra.isAcceptor = True
                  if hb_type == "D" or hb_type == "B":
                    extra.isDonor = True

                  # For metallic atoms, the Richardsons determined in discussion with
                  # Michael Prisant that we want to use the ionic radius rather than the
                  # larger radius for all purposes.
                  # @todo Once the CCTBX radius determination discussion and upgrade is
                  # complete (ongoing as of September 2021), this check might be removed
                  # and we'll just use the CCTBX radius.
                  if a.element_is_metallic():
                    warnings += "Using ionic radius for "+a.name.strip()+"\n"
                    extra.vdwRadius = model.get_specific_ion_radius(a.i_seq)
                  else:
                    extra.vdwRadius = model.get_specific_vdw_radius(a.i_seq, useImplicitHydrogenDistances)

                  # Mark aromatic ring N and C atoms as acceptors as a hack to enable the
                  # ring itself to behave as an acceptor.
                  # @todo Remove this once we have a better way to model the ring itself
                  # as an acceptor, perhaps making it a cylinder or a sphere in the center
                  # of the ring.
                  if a.element in ['C','N']:
                    if AtomTypes.IsAromatic(ag.resname, a.name):
                      extra.isAcceptor = True
                      warnings += "Marking "+a.name.strip()+" as an aromatic-ring acceptor\n"

                  # Mark all Carbonyl's with the Probe radius while the Richarsons and
                  # the CCTBX decide how to handle this.
                  # @todo After 2021, see if the CCTBX has the same values (1.65 and 1.80)
                  # for Carbonyls and remove this if so.  It needs to stay with these values
                  # to avoid spurious collisions per experiments run by the Richardsons in
                  # September 2021.
                  if a.name.strip().upper() == 'C':
                    if useImplicitHydrogenDistances:
                      extra.vdwRadius = 1.80
                    else:
                      extra.vdwRadius = 1.65
                    warnings += "Overriding radius for "+a.name.strip()+": "+str(extra.vdwRadius)+"\n"

                  extras.setMappingFor(a, extra)
                  continue

                # Did not find the information from CCTBX, so look it up using
                # the original Probe approach by dropping through to below
                else:
                  warnings += "Could not find "+a.name.strip()+" in CCTBX, using Probe tables\n"
              except Exception as e:
                # Warn and drop through to below.
                warnings += ("Could not look up "+a.name.strip()+" in CCTBX "+
                  "(perhaps interpretation was not run on the model?), using Probe tables"+
                  ": "+str(e)+"\n")

            # Did not find what we were looking for in CCTBX, so drop through to Probe.
            # Probe always returns the result we want as the VdW radius, even for ions.
            extra, warn = at.FindProbeExtraAtomInfo(a)
            if len(warn) > 0:
              warnings += "  Probe says: "+warn+"\n"

            extras.setMappingFor(a, extra)

  return getExtraAtomInfoReturn(extras, warnings)

def getPhantomHydrogensFor(atom, spatialQuery, extraAtomInfo, minOccupancy, acceptorOnly = False,
      placedHydrogenRadius = 1.05):
  """
    Get a list of phantom Hydrogens for the atom specified, which is asserted to be an Oxygen
    atom for a water.
    :param atom: The Oxygen that is to have phantoms added to it.
    :param spatialQuery: mmtbx_probe_ext.SpatialQuery structure to rapidly determine which atoms
    are within a specified distance of a location.
    :param extraAtomInfo: mmtbx_probe_ext.ExtraAtomInfo mapper that provides radius and other
    information about atoms beyond what is in the pdb.hierarchy.  Used here to determine
    which atoms may be acceptors.
    :param minOccupancy: Minimum occupancy for an atom to be considered.
    :param acceptorOnly: Only allow bonds with atoms that are acceptors when this is True.
    This is false by default because Reduce needs to check whether the bonded atom is either
    an acceptor or a possible flipped position of an acceptor, and that is not something that
    can be determined at the time we're placing phantom hydrogens.  In that case, we want to
    include all possible interactions and weed them out during optimization.
    :param placedHydrogenRadius: Radius to use for placed Phantom Hydrogen atoms.
    :return: List of new atoms that make up the phantom Hydrogens, with only their name and
    element type and xyz positions filled in.  They will have i_seq 0 and they should not be
    inserted into a structure.
  """

  ret = []

  # Get the list of nearby atoms.  The center of the search is the water atom
  # and the search radius is 4 (these values are pulled from the Reduce C++ code).
  maxDist = 4.0
  nearby = spatialQuery.neighbors(atom.xyz, 0.001, maxDist)

  # Candidates for nearby atoms.  We use this list to keep track of one ones we
  # have already found so that we can compare against them to only get one for each
  # aromatic ring.
  class Candidate(object):
    def __init__(self, atom, overlap):
      self._atom = atom
      self._overlap = overlap
  candidates = []

  for a in nearby:
    # Only check atoms in compatible conformations.
    if not compatibleConformations(atom, a):
      continue

    # Check to ensure the occupancy of the neighbor is above threshold and that it is
    # close enough to potentially bond to the atom.
    OH_BOND_LENGTH = 1.0
    overlap = ( (rvec3(atom.xyz) - rvec3(a.xyz)).length()  -
                (placedHydrogenRadius + extraAtomInfo.getMappingFor(a).vdwRadius + OH_BOND_LENGTH) )
    if overlap < -0.1 and a.occ > minOccupancy and a.element != "H":
      if not acceptorOnly or extraAtomInfo.getMappingFor(a).isAcceptor:
        # If we have multiple atoms in the same Aromatic ring (part of the same residue)
        # we only point at the closest one.  To ensure this, we check all current candidates
        # and if we find one that is on the same aromatic ring then we either ignore this new
        # atom (if it is further) or replace the existing one (if it is closer).
        skip = False
        if AtomTypes.IsAromatic(a.parent().resname.strip().upper(), a.name.strip().upper()):
          for c in candidates:
            # See if we belong to the same atom group and are both ring acceptors.  If so, we need to replace
            # or else squash this atom.
            if (AtomTypes.IsAromatic(c._atom.parent().resname.strip().upper(), c._atom.name.strip().upper()) and
                a.parent() == c._atom.parent()):
              if overlap < c._overlap:
                # Replace the further atom with this atom.
                c._atom = a
                c._overlap = overlap
                skip = True
                break
              else:
                # This is further away, so we don't insert it.
                skip = True
                break

        # Add the Candidate
        if not skip:
          candidates.append(Candidate(a, overlap))

  # Generate phantoms pointing toward all of the remaining candidates.
  # Make most of their characteristics (including i_seq) copied from the source Oxygen.
  # The element, name, and location are modified.
  for c in candidates:
    h = pdb.hierarchy.atom(atom.parent(), atom)
    h.element = "H"
    h.name = " H?"

    # Place the hydrogen pointing from the Oxygen towards the candidate at a distance
    # of 1 plus an offset that is clamped to the range -1..0 that is the sum of the overlap
    # and the best hydrogen-bonding overlap.
    BEST_HBOND_OVERLAP=0.6
    distance = 1.0 + max(-1.0, min(0.0, c._overlap + BEST_HBOND_OVERLAP))
    try:
      normOffset = (rvec3(c._atom.xyz) - rvec3(atom.xyz)).normalize()
      h.xyz = rvec3(atom.xyz) + distance * normOffset
      ret.append(h)
    except Exception:
      # If we have overlapping atoms, don't add.
      pass

  return ret

def fixupExplicitDonors(atoms, bondedNeighborLists, extraAtomInfo):
  """
    Fix up the donor status for models that have explicit hydrogens.  All Nitrogens, Oxygens
    and Sulphur atoms are stripped of their donor status because they will have explicit Hydrogens
    added or else had some other form of covalent bond added.  All hydrogens that are bonded to
    Nitrogens, Oxygens, or Sulphur atoms are marked as donors.  This does not handle any Phantom
    Hydrogens unless those Hydrogens are marked as bonded to their Water Oxygen.
    :param atoms: The list of atoms to adjust.
    :param bondedNeighborLists: Dictionary of lists that contain all bonded neighbors for
    each atom in a set of atoms.  Should be obtained using
    mmtbx.probe.Helpers.getBondedNeighborLists().
    :param extraAtomInfo: mmtbx_probe_ext.ExtraAtomInfo mapper that provides radius and other
    information about atoms beyond what is in the pdb.hierarchy.  Used here to determine
    which atoms may be acceptors.  This information is modified in place to adjust the donor
    status of atoms.
    :return: None.  As a side effect, the extraAtomInfo is adjusted.
  """

  for a in atoms:
    # If we are a hydrogen that is bonded to a nitrogen, oxygen, or sulfur then we're a donor
    # and our bonded neighbor is not.
    if a.element_is_hydrogen():
      for n in bondedNeighborLists[a]:
        if n.element in ['N','O','S']:
          # Copy the value, set the new values, then copy the new one back in.
          # We are a donor and may have our radius adjusted
          ei = extraAtomInfo.getMappingFor(a)
          ei.isDonor = True
          extraAtomInfo.setMappingFor(a, ei)

          # Set our neigbor to not be a donor, since we are the donor
          ei = extraAtomInfo.getMappingFor(n)
          ei.isDonor = False
          extraAtomInfo.setMappingFor(n, ei)

    # Otherwise, if we're an N, O, or S then remove our donor status because
    # the hydrogens will be the donors.  Because we're not doing implicit
    # hydrogens (and thus are doing explicit hydrogens), if we have a leftover
    # atom that did not have a hydrogen attached we assume that this is because
    # there is some other bonding and we still need to remove the donor status.
    elif a.element in ['N','O','S']:
      ei = extraAtomInfo.getMappingFor(a)
      ei.isDonor = False
      extraAtomInfo.setMappingFor(a, ei)

##################################################################################
# Helper functions to make things that are compatible with vec3_double so
# that we can do math on them.  We need a left-hand and right-hand one so that
# we can make both versions for multiplication.
def rvec3 (xyz) :
  return scitbx.matrix.rec(xyz, (3,1))
def lvec3 (xyz) :
  return scitbx.matrix.rec(xyz, (1,3))

def Test(inFileName = None):
  """
  Run tests on all of our functions.  Throw an assertion failure if one fails.
  """

  from libtbx.test_utils import approx_equal

  #========================================================================
  # Run unit test on getExtraAtomInfo().
  # @todo

  #========================================================================
  # Run unit test on getPhantomHydrogensFor().
  # @todo

  #========================================================================
  # Run unit test on getBondedNeighborLists().  We use a specific PDB snippet
  # for which we know the answer and then we verify that the results are what
  # we expect.
  pdb_1xso_his_61 = (
"""
ATOM    442  N   HIS A  61      26.965  32.911   7.593  1.00  7.19           N
ATOM    443  CA  HIS A  61      27.557  32.385   6.403  1.00  7.24           C
ATOM    444  C   HIS A  61      28.929  31.763   6.641  1.00  7.38           C
ATOM    445  O   HIS A  61      29.744  32.217   7.397  1.00  9.97           O
ATOM    446  CB  HIS A  61      27.707  33.547   5.385  1.00  9.38           C
ATOM    447  CG  HIS A  61      26.382  33.956   4.808  1.00  8.78           C
ATOM    448  ND1 HIS A  61      26.168  34.981   3.980  1.00  9.06           N
ATOM    449  CD2 HIS A  61      25.174  33.397   5.004  1.00 11.08           C
ATOM    450  CE1 HIS A  61      24.867  35.060   3.688  1.00 12.84           C
ATOM    451  NE2 HIS A  61      24.251  34.003   4.297  1.00 11.66           N
END
"""
    )

  dm = iotbx.data_manager.DataManager(['model'])
  dm.process_model_str("1xso_snip.pdb",pdb_1xso_his_61)
  model = dm.get_model()
  model.process(make_restraints=True) # make restraints

  # Get the first model in the hierarchy.
  atoms = model.get_hierarchy().models()[0].atoms()

  # Get the Cartesian positions of all of the atoms we're considering for this alternate
  # conformation.
  carts = flex.vec3_double()
  for a in atoms:
    carts.append(a.xyz)

  # Get the bond proxies for the atoms in the model and conformation we're using and
  # use them to determine the bonded neighbor lists.
  bondProxies = model.get_restraints_manager().geometry.get_all_bond_proxies(sites_cart = carts)[0]
  bondedNeighborLists = getBondedNeighborLists(atoms, bondProxies)

  # Check the counts in the neighbor lists to make sure they match what we expect
  neighborCounts = {"N": 1, "CA": 3, "C": 2, "O": 1, "CB": 2,
                    "CG": 3, "ND1": 2, "CD2": 2, "CE1":2, "NE2": 2}
  for a in atoms:
    assert len(bondedNeighborLists[a]) == neighborCounts[a.name.strip()], (
        "Helpers.Test(): Neighbor count for "+a.name.strip()+" was "+
        str(len(bondedNeighborLists[a]))+", expected "+str(neighborCounts[a.name.strip()]))

  #=====================================================================================
  # Run unit test on compatibleConformations().
  a1 = pdb.hierarchy.atom()
  ag1 = pdb.hierarchy.atom_group()
  ag1.append_atom(a1)
  a2 = pdb.hierarchy.atom()
  ag2 = pdb.hierarchy.atom_group()
  ag2.append_atom(a2)
  ag1.altloc = ""
  ag2.altloc = "A"
  assert compatibleConformations(a1,a2), "Helpers:Test(): altloc expected True for empty first"
  ag1.altloc = "A"
  ag2.altloc = "A"
  assert compatibleConformations(a1,a2), "Helpers:Test(): altloc expected True for compatible"
  ag1.altloc = "A"
  ag2.altloc = "B"
  assert not compatibleConformations(a1,a2), "Helpers:Test(): altloc expected False for incompatible"
  ag1.altloc = "A"
  ag2.altloc = " "
  assert compatibleConformations(a1,a2), "Helpers:Test(): altloc expected True for blank second"
  ag1.altloc = ""
  ag2.altloc = " "
  assert compatibleConformations(a1,a2),  "Helpers:Test(): altloc expected True for empty first and blank second"

  #========================================================================
  # Run unit test on getAtomsWithinNBonds().
  # Get the atoms within N bounds for a range for the "N" atom and verify that the
  # counts match what is expected.  Do this for the case where we clamp the non-
  # hydrogen ones to the 3 and when we use the default of very large to count
  # them all.
  # NOTE: This re-uses the bondedNeighborLists test results from above
  nestedNeighborsForN = [ None, 1, 3, 5, 5, 5, 5]
  for N in range(1,7):
    count = len(getAtomsWithinNBonds(atoms[0], bondedNeighborLists, N, 3))
    assert count == nestedNeighborsForN[N], ("Helpers.Test(): Nested clamped count for "+atoms[0].name.strip()+
        " for N = "+str(N)+" was "+str(count)+", expected "+str(nestedNeighborsForN[N]))
  nestedNeighborsForN = [ None, 1, 3, 5, 7, 9, 9]
  for N in range(1,7):
    count = len(getAtomsWithinNBonds(atoms[0], bondedNeighborLists, N))
    assert count == nestedNeighborsForN[N], ("Helpers.Test(): Nested unclamped count for "+atoms[0].name.strip()+
        " for N = "+str(N)+" was "+str(count)+", expected "+str(nestedNeighborsForN[N]))
  # @todo Test the hydrogen cutoff parameter for getAtomsWithinNBonds

  #========================================================================
  # Generate an example data model with a small molecule in it or else read
  # from the specified file.
  if inFileName is not None and len(inFileName) > 0:
    # Read a model from a file using the DataManager
    dm = iotbx.data_manager.DataManager()
    dm.process_model_file(inFileName)
    model = dm.get_model(inFileName)
  else:
    # Generate a small-molecule model using the map model manager
    # get an initialized instance of the map_model_manager
    mmm=iotbx.map_model_manager.map_model_manager()
    mmm.generate_map()     #   get a model from a generated small library model and calculate a map for it
    model = mmm.model()    #   get the model

  # Fix up bogus unit cell when it occurs by checking crystal symmetry.
  cs = model.crystal_symmetry()
  if (cs is None) or (cs.unit_cell() is None):
    model = cctbx.maptbx.box.shift_and_box_model(model = model)

  # Run PDB interpretation on the model to fill in the required CCTBX information.
  p = mmtbx.model.manager.get_default_pdb_interpretation_params()
  p.pdb_interpretation.use_neutron_distances = False
  model.process(make_restraints=True, pdb_interpretation_params = p) # make restraints

  ret = getExtraAtomInfo(model)
  # User code should check for and print any warnings.
  #if len(ret.warnings) > 0:
  #  print('Warnings returned by getExtraAtomInfo():\n'+ret.warnings)

  #========================================================================
  # Run unit tests on rvec3 and lvec3.
  v1 = rvec3([0, 0, 0])
  v2 = rvec3([1, 0, 0])
  assert approx_equal((v2-v1).length(), 1), "Helpers.Test(): rvec3 test failed"

  v1 = lvec3([0, 0, 0])
  v2 = lvec3([1, 0, 0])
  assert approx_equal((v2-v1).length(), 1), "Helpers.Test(): lvec3 test failed"

if __name__ == '__main__':

  #==============================================================
  # Parse command-line arguments.  The 0th argument is the name
  # of the script. There can be the name of a PDB/CIF file to read.
  realParams = 0
  fileName = ""
  for i in range(1,len(sys.argv)):
    fileName = sys.argv[i]

  # This will raise an assertion failure if there is a problem
  Test(fileName)
  print('OK')