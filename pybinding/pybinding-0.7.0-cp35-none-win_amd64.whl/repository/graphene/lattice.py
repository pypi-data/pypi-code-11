import pybinding as pb

__all__ = ['monolayer', 'monolayer_alt', 'monolayer_4atom', 'bilayer']


def monolayer(nearest_neighbors=1, onsite=(0, 0), **kwargs):
    """Monolayer graphene lattice up to `nearest_neighbors` hoppings

    Parameters
    ----------
    nearest_neighbors : int
        Number of nearest neighbors to consider.
    onsite : Tuple[float, float]
        Onsite energy for sublattices A and B.
    **kwargs
        Specify the hopping parameters `t`, `t_nn` and `t_nnn`.
        If not given, the default values from :mod:`.graphene.constants` will be used.
    """
    from math import sqrt
    from .constants import a_cc, a, t, t_nn

    lat = pb.Lattice(a1=[a, 0], a2=[a/2, a/2 * sqrt(3)])

    # The next-nearest hoppings shift the Dirac point away from zero energy.
    # This will push it back to zero for consistency with the first-nearest model.
    onsite_offset = 0 if nearest_neighbors < 2 else 3 * kwargs.get('t_nn', t_nn)

    lat.add_sublattices(
        ('A', [0, -a_cc/2], onsite[0] + onsite_offset),
        ('B', [0,  a_cc/2], onsite[1] + onsite_offset)
    )

    lat.register_hopping_energies({
        't': kwargs.get('t', t),
        't_nn': kwargs.get('t_nn', t_nn),
        't_nnn': kwargs.get('t_nnn', 0.05),
    })

    lat.add_hoppings(
        ([0,  0], 'A', 'B', 't'),
        ([1, -1], 'A', 'B', 't'),
        ([0, -1], 'A', 'B', 't')
    )

    if nearest_neighbors >= 2:
        lat.add_hoppings(
            ([0, -1], 'A', 'A', 't_nn'),
            ([0, -1], 'B', 'B', 't_nn'),
            ([1, -1], 'A', 'A', 't_nn'),
            ([1, -1], 'B', 'B', 't_nn'),
            ([1,  0], 'A', 'A', 't_nn'),
            ([1,  0], 'B', 'B', 't_nn'),
        )

    if nearest_neighbors >= 3:
        lat.add_hoppings(
            [( 1, -2), 'A', 'B', 't_nnn'],
            [( 1,  0), 'A', 'B', 't_nnn'],
            [(-1,  0), 'A', 'B', 't_nnn'],
        )

    if nearest_neighbors >= 4:
        raise RuntimeError("No more")

    lat.min_neighbors = 2
    return lat


def monolayer_alt(onsite=(0, 0)):
    """Nearest-neighbor lattice with alternative lattice vectors

    This lattice is mainly here to demonstrate specifying hoppings in matrix form.

    Parameters
    ----------
    onsite : Tuple[float, float]
        Onsite energy for sublattices A and B.
    """
    from math import sqrt
    from .constants import a_cc, a, t

    lat = pb.Lattice(
        a1=[ a/2, a/2 * sqrt(3)],
        a2=[-a/2, a/2 * sqrt(3)],
    )

    lat.add_sublattices(
        ('A', [0,    0], onsite[0]),
        ('B', [0, a_cc], onsite[1])
    )

    # matrix hopping specification
    r0 = [ 0,  0]
    r1 = [ 0, -1]
    r2 = [-1,  0]

    tr0 = [[0, t],
           [t, 0]]
    tr1 = [[0, t],
           [0, 0]]
    tr2 = [[0, t],
           [0, 0]]

    lat.add_hopping_matrices([r0, tr0], [r1, tr1], [r2, tr2])
    lat.min_neighbors = 2
    return lat


def monolayer_4atom(onsite=(0, 0)):
    """Nearest-neighbor with 4 atoms per unit cell: square lattice instead of oblique

    Parameters
    ----------
    onsite : Tuple[float, float]
        Onsite energy for sublattices A and B.
    """
    from .constants import a_cc, a, t

    lat = pb.Lattice(a1=[a, 0], a2=[0, 3*a_cc])

    lat.add_sublattices(
        ('A',  [  0, -a_cc/2], onsite[0]),
        ('B',  [  0,  a_cc/2], onsite[1]),
        ('A2', [a/2,    a_cc], onsite[0], 'A'),
        ('B2', [a/2,  2*a_cc], onsite[1], 'B')
    )

    lat.add_hoppings(
        # inside the unit sell
        ([0, 0], 'A',  'B',  t),
        ([0, 0], 'B',  'A2', t),
        ([0, 0], 'A2', 'B2', t),
        # between neighbouring unit cells
        ([-1, -1], 'A', 'B2', t),
        ([ 0, -1], 'A', 'B2', t),
        ([-1,  0], 'B', 'A2', t),
    )

    lat.min_neighbors = 2
    return lat


def bilayer(gammas=(), onsite=(0, 0, 0, 0)):
    """Bilayer lattice with optional :math:`\gamma_3` and :math:`\gamma_4` hoppings

    Parameters
    ----------
    gammas : tuple
        By default, only the :math:`\gamma_1` interlayer hopping is used. One or both
        :math:`\gamma_3` and :math:`\gamma_4` can be added with `gammas=(3,)`,
        `gammas=(4,)` or `gammas=(3, 4)`.
    onsite : Tuple[float, float, float, float]
        Onsite energy for A1, B1, A2, B2
    """
    from math import sqrt
    from .constants import a_cc, a, t

    lat = pb.Lattice(
        a1=[ a/2, a/2 * sqrt(3)],
        a2=[-a/2, a/2 * sqrt(3)]
    )

    c0 = 0.335  # [nm] interlayer spacing
    lat.add_sublattices(
        ('A1', [0,  -a_cc/2,   0], onsite[0]),
        ('B1', [0,   a_cc/2,   0], onsite[1]),
        ('A2', [0,   a_cc/2, -c0], onsite[2]),
        ('B2', [0, 3*a_cc/2, -c0], onsite[3])
    )

    lat.register_hopping_energies({
        'gamma0': t,
        'gamma1': -0.4,
        'gamma3': -0.3,
        'gamma4': -0.04
    })

    lat.add_hoppings(
        # layer 1
        ([ 0,  0], 'A1', 'B1', 'gamma0'),
        ([ 0, -1], 'A1', 'B1', 'gamma0'),
        ([-1,  0], 'A1', 'B1', 'gamma0'),
        # layer 2
        ([ 0,  0], 'A2', 'B2', 'gamma0'),
        ([ 0, -1], 'A2', 'B2', 'gamma0'),
        ([-1,  0], 'A2', 'B2', 'gamma0'),
        # interlayer
        ([ 0,  0], 'B1', 'A2', 'gamma1')
    )

    if 3 in gammas:
        lat.add_hoppings(
            ([0, 1], 'B2', 'A1', 'gamma3'),
            ([1, 0], 'B2', 'A1', 'gamma3'),
            ([1, 1], 'B2', 'A1', 'gamma3')
        )

    if 4 in gammas:
        lat.add_hoppings(
            ([0, 0], 'A2', 'A1', 'gamma4'),
            ([0, 1], 'A2', 'A1', 'gamma4'),
            ([1, 0], 'A2', 'A1', 'gamma4')
        )

    lat.min_neighbors = 2
    return lat
