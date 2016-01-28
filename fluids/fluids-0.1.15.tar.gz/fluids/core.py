# -*- coding: utf-8 -*-
'''Chemical Engineering Design Library (ChEDL). Utilities for process modeling.
Copyright (C) 2016, Caleb Bell <Caleb.Andrew.Bell@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.'''

from __future__ import division
from math import sin, cos, exp, pi, log
from scipy.constants import g, R





### Not quite dimensionless groups
def thermal_diffusivity(k, rho, Cp):
    r'''Calculates thermal diffusivity or `alpha` for a fluid with the given
    parameters.

    .. math::
        \alpha = \frac{k}{\rho Cp}

    Parameters
    ----------
    k : float
        Thermal conductivity, [W/m/K]
    Cp : float
        Heat capacity, [J/kg/K]
    rho : float
        Density, [kg/m^3]

    Returns
    -------
    alpha : float
        Thermal diffusivity, [m^2/s]

    Notes
    -----

    Examples
    --------
    >>> thermal_diffusivity(0.02, 1., 1000.)
    2e-05

    References
    ----------
    .. [1] Blevins, Robert D. Applied Fluid Dynamics Handbook. New York, N.Y.:
       Van Nostrand Reinhold Co., 1984.
    '''
    alpha = k/(rho*Cp)
    return alpha


### Ideal gas fluid properties


def c_ideal_gas(T, k, MW):
    r'''Calculates speed of sound `c` in an ideal gas at tempereture T.

    .. math::
        c = \sqrt{kR_{specific}T}

    Parameters
    ----------
    T : float
        Temperature of fluid, [K]
    k : float
        Isentropic exponent of fluid, [-]
    MW : float
        Molecular weight of fluid, [g/mol]

    Returns
    -------
    c : float
        Speed of sound in fluid, [m/s]

    Notes
    -----
    Used in compressible flow calculations.
    Note that the gas constant used is the specific gas constant:

    .. math::
        R_{specific} = R\frac{1000}{MW}

    Examples
    --------
    >>> c_ideal_gas(1.4, 303., 28.96)
    348.9820844443473

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    '''
    Rspecific = R*1000./MW
    c = (k*Rspecific*T)**0.5
    return c

#print [c_ideal_gas(1.4, 303., 28.96)]


### Dimensionless groups with documentation

def Reynolds(V, D, rho=None, mu=None, nu=None):
    r'''Calculates Reynolds number or `Re` for a fluid with the given
    properties for the specified velocity and diameter.

    .. math::
        Re = {D \cdot V}{\nu} = \frac{\rho V D}{\mu}

    Inputs either of any of the following sets:

    * V, D, density `rho` and kinematic viscosity `mu`
    * V, D, and dynamic viscosity `nu`

    Parameters
    ----------
    D : float
        Diameter [m]
    V : float
        Velocity [m/s]
    rho : float, optional
        Density, [kg/m^3]
    mu : float, optional
        Dynamic viscosity, [Pa*s]
    nu : float, optional
        Kinematic viscosity, [m^2/s]

    Returns
    -------
    Re : float
        Reynolds number []

    Notes
    -----
    .. math::
        Re = \frac{\text{Momentum}}{\text{Viscosity}}

    An error is raised if none of the required input sets are provided.

    Examples
    --------
    >>> Reynolds(2.5, 0.25, 1.1613, 1.9E-5)
    38200.65789473684
    >>> Reynolds(2.5, 0.25, nu=1.636e-05)
    38202.93398533008

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    '''
    if rho and mu:
        nu = mu/rho
    elif not nu:
        raise Exception('Either density and viscosity, or dynamic viscosity, \
        is needed')
    Re = V*D/nu
    return Re


def Peclet_heat(V, L, rho=None, Cp=None, k=None, alpha=None):
    r'''Calculates heat transfer Peclet number or `Pe` for a specified velocity
    `V`, characteristic length `L`, and specified properties for the given
    fluid.

    .. math::
        Pe = \frac{VL\rho C_p}{k} = \frac{LV}{\alpha}

    Inputs either of any of the following sets:

    * V, L, density `rho`, heat capcity `Cp`, and thermal conductivity `k`
    * V, L, and thermal diffusivity `alpha`

    Parameters
    ----------
    V : float
        Velocity [m/s]
    L : float
        Characteristic length [m]
    rho : float, optional
        Density, [kg/m^3]
    Cp : float, optional
        Heat capacity, [J/kg/K]
    k : float, optional
        Thermal conductivity, [W/m/K]
    alpha : float, optional
        Thermal diffusivity, [m^2/s]

    Returns
    -------
    Pe : float
        Peclet number (heat) []

    Notes
    -----
    .. math::
        Pe = \frac{\text{Bulk heat transfer}}{\text{Conduction heat transfer}}

    An error is raised if none of the required input sets are provided.

    Examples
    --------
    >>> Peclet_heat(1.5, 2, 1000., 4000., 0.6)
    20000000.0
    >>> Peclet_heat(1.5, 2, alpha=1E-7)
    30000000.0

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    '''
    if rho and Cp and k:
        alpha =  k/(rho*Cp)
    elif not alpha:
        raise Exception('Either heat capacity and thermal conductivity and\
        density, or thermal diffusivity is needed')
    Pe = V*L/alpha
    return Pe


def Weber(V, L, rho, sigma):
    r'''Calculates Weber number, `We`, for a fluid with the given density,
    surface tension, velocity, and geometric parameter (usually diameter
    of bubble).

    .. math::
        We = \frac{V^2 L\rho}{\sigma}

    Parameters
    ----------
    V : float
        Velocity of fluid, [m/s]
    L : float
        Characteristic length, typically bubble diameter [m]
    rho : float
        Density of fluid, [kg/m^3]
    sigma : float
        Surface tension, [N/m]

    Returns
    -------
    We : float
        Weber number []

    Notes
    -----
    Used in bubble calculations.

    .. math::
        We = \frac{\text{inertial force}}{\text{surface tension force}}

    Examples
    --------
    >>> Weber(V=0.18, L=0.001, rho=900., sigma=0.01)
    2.916

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    .. [3] Gesellschaft, V. D. I., ed. VDI Heat Atlas. 2nd edition.
       Berlin; New York:: Springer, 2010.
    '''
    We = V**2*L*rho/sigma
    return We


def Mach(V, c):
    r'''Calculates Mach number or `Ma` for a fluid of velocity `V` with speed
    of sound `c`.

    .. math::
        Ma = \frac{V}{c}

    Parameters
    ----------
    V : float
        Velocity of fluid, [m/s]
    c : float
        Speed of sound in fluid, [m/s]

    Returns
    -------
    Ma : float
        Mach number []

    Notes
    -----
    Used in compressible flow calculations.

    .. math::
        Ma = \frac{\text{fluid velocity}}{\text{sonic velocity}}

    Examples
    --------
    >>> Mach(33., 330)
    0.1

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    '''
    return V/c


def Prandtl(Cp=None, k=None, mu=None, nu=None, rho=None, alpha=None):
    r'''Calculates Prandtl number or `Pr` for a fluid with the given
    parameters.

    .. math::
        Pr = \frac{C_p \mu}{k} = \frac{\nu}{\alpha} = \frac{C_p \rho \nu}{k}

    Inputs can be any of the following sets:

    * Heat capacity, dynamic viscosity, and thermal conductivity
    * Thermal diffusivity and kinematic viscosity
    * Heat capacity, kinematic viscosity, thermal conductivity, and density

    Parameters
    ----------
    Cp : float
        Heat capacity, [J/kg/K]
    k : float
        Thermal conductivity, [W/m/K]
    mu : float, optional
        Dynamic viscosity, [Pa*s]
    nu : float, optional
        Kinematic viscosity, [m^2/s]
    rho : float
        Density, [kg/m^3]
    alpha : float
        Thermal diffusivity, [m^2/s]

    Returns
    -------
    Pr : float
        Prandtl number []

    Notes
    -----
    .. math::
        Pr=\frac{\text{kinematic viscosity}}{\text{thermal diffusivity}} = \frac{\text{momendum diffusivity}}{\text{thermal diffusivity}}

    An error is raised if none of the required input sets are provided.

    Examples
    --------
    >>> Prandtl(Cp=1637., k=0.010, mu=4.61E-6)
    0.754657
    >>> Prandtl(Cp=1637., k=0.010, nu=6.4E-7, rho=7.1)
    0.7438528
    >>> Prandtl(nu=6.3E-7, alpha=9E-7)
    0.7000000000000001

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    .. [3] Gesellschaft, V. D. I., ed. VDI Heat Atlas. 2nd edition.
       Berlin; New York:: Springer, 2010.
    '''
    if k and Cp and mu:
        Pr = Cp*mu/k
    elif nu and rho and Cp and k:
        Pr = nu*rho*Cp/k
    elif nu and alpha:
        Pr = nu/alpha
    else:
        raise Exception('Insufficient information provided for Pr calculation')
    return Pr


def Grashof(L, beta, T1, T2=0, rho=None, mu=None, nu=None, g=g):
    r'''Calculates Grashof number or `Gr` for a fluid with the given
    properties, temperature difference, and characteristic length.

    .. math::
        Gr = = \frac{g\beta (T_s-T_\infty)L^3}{\nu^2}
        = \frac{g\beta (T_s-T_\infty)L^3\rho^2}{\mu^2}

    Inputs either of any of the following sets:

    * L, beta, T1 and T2, and density `rho` and kinematic viscosity `mu`
    * L, beta, T1 and T2, and dynamic viscosity `nu`

    Parameters
    ----------
    L : float
        Characteristic length [m]
    beta : float
        Volumetric thermal expansion coefficient [1/K]
    T1 : float
        Temperature 1, usually a film temperature [K]
    T2 : float, optional
        Temperature 2, usually a bulk temperature (or 0 if only a difference
        is provided to the function) [K]
    rho : float, optional
        Density, [kg/m^3]
    mu : float, optional
        Dynamic viscosity, [Pa*s]
    nu : float, optional
        Kinematic viscosity, [m^2/s]
    g : float, optional
        Acceleration due to gravity, [m/s^2]

    Returns
    -------
    Gr : float
        Grashof number []

    Notes
    -----
    .. math::
        Gr = \frac{\text{Buoyancy forces}}{\text{Viscous forces}}

    An error is raised if none of the required input sets are provided.
    Used in free convection problems only.

    Examples
    --------
    Example 4 of [1]_, p. 1-21 (matches):

    >>> Grashof(L=0.9144, beta=0.000933, T1=178.2, rho=1.1613, mu=1.9E-5)
    4656936556.178915
    >>> Grashof(L=0.9144, beta=0.000933, T1=378.2, T2=200, nu=1.636e-05)
    4657491516.530312

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    '''
    if rho and mu:
        nu = mu/rho
    elif not nu:
        raise Exception('Either density and viscosity, or dynamic viscosity, \
        is needed')
    Gr = g*beta*abs(T2-T1)*L**3/nu**2
    return Gr


def Bond(rhol, rhog, sigma, L):
    r'''Calculates Bond number, `Bo` also known as Eotvos number,
    for a fluid with the given liquid and gas densities, surface tension,
    and geometric parameter (usually length).

    .. math::
        Bo = \frac{g(\rho_l-\rho_g)L^2}{\sigma}

    Parameters
    ----------
    rhol : float
        Density of liquid, [kg/m^3]
    rhog : float
        Density of gas, [kg/m^3]
    sigma : float
        Surface tension, [N/m]
    L : float
        Characteristic length, [m]

    Returns
    -------
    Bo : float
        Bond number []

    Examples
    --------
    >>> Bond(1000., 1.2, .0589, 2)
    665187.2339558573

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    '''
    return (g*(rhol-rhog)*L**2/sigma)

def Rayleigh(Pr, Gr):
    r'''Calculates Rayleigh number or `Ra` using Prandtl number `Pr` and
    Grashof number `Gr` for a fluid with the given
    properties, temperature difference, and characteristic length used
    to calculate `Gr` and `Pr`.

    .. math::
        Ra = PrGr

    Parameters
    ----------
    Pr : float
        Prandtl number []
    Gr : float
        Grashof number []

    Returns
    -------
    Ra : float
        Rayleigh number []

    Notes
    -----
    Used in free convection problems only.

    Examples
    --------
    >>> Rayleigh(1.2, 4.6E9)
    5520000000.0

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    '''
    Ra = Pr*Gr
    return Ra


def Froude(V, L, g=g, squared=False):
    r'''Calculates Froude number `Fr` for velocity `V` and geometric length
    `L`. If desired, gravity can be specified as well. Normally the function
    returns the result of the equation below; Froude number is also often
    said to be defined as the square of the equation below.

    .. math::
        Fr = \frac{V}{\sqrt{gL}}

    Parameters
    ----------
    V : float
        Velocity of the particle or fluid, [m/s]
    L : float
        Characteristic length, no typical definition [m]
    g : float, optional
        Acceleration due to gravity, [m/s^2]
    squared : bool, optional
        Whether to return the squared form of Frounde number

    Returns
    -------
    Fr : float
        Froude number, [-]

    Notes
    -----
    Many alternate definitions including density ratios have been used.

    .. math::
        Fr = \frac{\text{Inertial Force}}{\text{Gravity Force}}

    Examples
    --------
    >>> Froude(1.83, L=2., g=1.63)
    1.0135432593877318
    >>> Froude(1.83, L=2., squared=True)
    0.17074638128208924

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    '''
    Fr = V/(L*g)**0.5
    if squared:
        Fr *= Fr
    return Fr


def Nusselt(h, L, k):
    r'''Calculates Nusselt number `Nu` for a heat transfer coefficient `h`,
    characteristic length `L`, and thermal conductivity `k`.

    .. math::
        Nu = \frac{hL}{k}

    Parameters
    ----------
    h : float
        Heat transfer coefficient, [W/m^2/K]
    L : float
        Characteristic length, no typical definition [m]
    k : float
        Thermal conductivity of fluid [W/m/K]

    Returns
    -------
    Nu : float
        Nusselt number, [-]

    Notes
    -----
    Do not confuse k, the thermal conductivity of the fluid, with that
    of within a solid object associated with!

    .. math::
        Nu = \frac{\text{Convective heat transfer}}
        {\text{Conductive heat transfer}}

    Examples
    --------
    >>> Nusselt(1000., 1.2, 300.)
    4.0
    >>> Nusselt(10000., .01, 4000.)
    0.025

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Bergman, Theodore L., Adrienne S. Lavine, Frank P. Incropera, and
       David P. DeWitt. Introduction to Heat Transfer. 6E. Hoboken, NJ:
       Wiley, 2011.
    '''
    Nu = h*L/k
    return Nu


def Biot(h, L, k):
    r'''Calculates Biot number `Br` for heat transfer coefficient `h`,
    geometric length `L`, and thermal conductivity `k`.

    .. math::
        Bi=\frac{hL}{k}

    Parameters
    ----------
    h : float
        Heat transfer coefficient, [W/m^2/K]
    L : float
        Characteristic length, no typical definition [m]
    k : float
        Thermal conductivity, within the object [W/m/K]

    Returns
    -------
    Bi : float
        Biot number, [-]

    Notes
    -----
    Do not confuse k, the thermal conductivity within the object, with that
    of the medium h is calculated with!

    .. math::
        Bi = \frac{\text{Surface thermal resistance}}
        {\text{Internal thermal resistance}}

    Examples
    --------
    >>> Biot(1000., 1.2, 300.)
    4.0
    >>> Biot(10000., .01, 4000.)
    0.025

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    '''
    Bi = h*L/k
    return Bi


def Stanton(h, V, rho, Cp):
    r'''Calculates Stanton number or `St` for a specified heat transfer
    coefficient `h`, velocity `V`, density `rho`, and heat capacity `Cp`.

    .. math::
        St = \frac{h}{V\rho Cp}

    Parameters
    ----------
    h : float
        Heat transfer coefficient, [W/m^2/K]
    V : float
        Velocity, [m/s]
    rho : float
        Density, [kg/m^3]
    Cp : float
        Heat capacity, [J/kg/K]

    Returns
    -------
    St : float
        Stanton number []

    Notes
    -----
    .. math::
        St = \frac{\text{Heat transfer coefficient}}{\text{Thermal capacity}}

    Examples
    --------
    >>> Stanton(5000, 5, 800, 2000.)
    0.000625

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [1] Bergman, Theodore L., Adrienne S. Lavine, Frank P. Incropera, and
       David P. DeWitt. Introduction to Heat Transfer. 6E. Hoboken, NJ:
       Wiley, 2011.
    '''
    St = h/(V*rho*Cp)
    return St


def Euler(dP, rho, V):
    r'''Calculates Euler number or `Eu` for a fluid of velocity `V` and
    density `rho` experiencing a pressure drop `dP`.

    .. math::
        Eu = \frac{\Delta P}{\rho V^2}

    Parameters
    ----------
    dP : float
        Pressure drop experience by the fluid, [Pa]
    rho : float
        Density of the fluid, [kg/m^3]
    V : float
        Velocity of fluid, [m/s]

    Returns
    -------
    Eu : float
        Euler number []

    Notes
    -----
    Used in pressure drop calculations.
    Rarely, this number is divided by two.
    Named after Leonhard Euler applied calculus to fluid dynamics.

    .. math::
        Eu = \frac{\text{Pressure drop}}{2\cdot \text{velocity head}}

    Examples
    --------
    >>> Euler(1E5, 1000., 4)
    6.25

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    '''
    Eu = dP/(rho*V**2)
    return Eu


def Cavitation(P, Psat, rho, V):
    r'''Calculates Cavitation number or `Ca` for a fluid of velocity `V` with
    a pressure `P`, vapor pressure `Psat`, and density `rho`.

    .. math::
        Ca = \sigma_c = \sigma = \frac{P-P_{sat}}{\frac{1}{2}\rho V^2}

    Parameters
    ----------
    P : float
        Internal pressure of the fluid, [Pa]
    Psat : float
        Vapor pressure of the fluid, [Pa]
    rho : float
        Density of the fluid, [kg/m^3]
    V : float
        Velocity of fluid, [m/s]

    Returns
    -------
    Ca : float
        Cavitation number []

    Notes
    -----
    Used in determining if a flow through a restriction will cavitate.
    Sometimes, the multiplication by 2 will be omitted;

    .. math::
        Ca = \frac{\text{Pressure - Vapor pressure}}
        {\text{Inertial pressure}}

    Examples
    --------
    >>> Cavitation(2E5, 1E4, 1000, 10)
    3.8

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    '''
    Ca = (P-Psat)/(0.5*rho*V**2)
    return Ca


def Eckert(V, Cp, dT):
    r'''Calculates Eckert number or `Ec` for a fluid of velocity `V` with
    a heat capacity `Cp`, between two temperature given as `dT`.

    .. math::
        Ec = \frac{V^2}{C_p \Delta T}

    Parameters
    ----------
    V : float
        Velocity of fluid, [m/s]
    Cp : float
        Heat capacity of the fluid, [J/kg/K]
    dT : float
        Temperature difference, [K]

    Returns
    -------
    Ec : float
        Eckert number []

    Notes
    -----
    Used in certain heat transfer calculations. Fairly rare.

    .. math::
        Ec = \frac{\text{Kinetic energy} }{ \text{Enthalpy difference}}

    Examples
    --------
    >>> Eckert(10, 2000., 25.)
    0.002

    References
    ----------
    .. [1] Goldstein, Richard J. ECKERT NUMBER. Thermopedia. Hemisphere, 2011.
       10.1615/AtoZ.e.eckert_number
    '''
    Ec = V**2/(Cp*dT)
    return Ec


def Jakob(Cp, Hvap, Te):
    r'''Calculates Jakob number or `Ja` for a boiling fluid with sensible heat
    capacity `Cp`, enthalpy of vaporization `Hvap`, and boiling at `Te` degrees
    above its saturation boiling point.

    .. math::
        Ja = \frac{C_{P}\Delta T_e}{\Delta H_{vap}}

    Parameters
    ----------
    Cp : float
        Heat capacity of the fluid, [J/kg/K]
    Hvap : float
        Enthalpy of vaporization of the fluid at its saturation temperature [J/kg]
    Te : float
        Temperature difference above the fluid's saturation boiling temperature, [K]

    Returns
    -------
    Ja : float
        Jakob number []

    Notes
    -----
    Used in boiling heat transfer analysis. Fairly rare.

    .. math::
        Ja = \frac{\Delta \text{Sensible heat}}{\Delta \text{Latent heat}}

    Examples
    --------
    >>> Jakob(4000., 2E6, 10.)
    0.02

    References
    ----------
    .. [1] Bergman, Theodore L., Adrienne S. Lavine, Frank P. Incropera, and
       David P. DeWitt. Introduction to Heat Transfer. 6E. Hoboken, NJ:
       Wiley, 2011.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    '''
    Ja = Cp*Te/Hvap
    return Ja


def Drag(F, A, V, rho):
    r'''Calculates drag coefficient `Cd` for a given drag force `F`,
    projected area `A`, characteristic velocity `V`, and density `rho`.

    .. math::
        C_D = \frac{F_d}{A\cdot\frac{1}{2}\rho V^2}

    Parameters
    ----------
    F : float
        Drag force, [N]
    A : float
        Projected area, [m^2]
    V : float
        Characteristic velocity, [m/s]
    rho : float
        Density, [kg/m^3]

    Returns
    -------
    Cd : float
        Drag coefficient, [-]

    Notes
    -----
    Used in flow around objects, or objects flowing within a fluid.

    .. math::
        C_D = \frac{\text{Drag forces}}{\text{Projected area}\cdot
        \text{Velocity head}}

    Examples
    --------
    >>> Drag(1000, 0.0001, 5, 2000)
    400.0

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    '''
    Cd = F/(A*rho*V**2/2.)
    return Cd


def Capillary(V, mu, sigma):
    r'''Calculates Capillary number `Ca` for a characteristic velocity `V`,
    viscosity `mu`, and surface tension `sigma`.

    .. math::
        Ca = \frac{V \mu}{\sigma}

    Parameters
    ----------
    V : float
        Characteristic velocity, [m/s]
    mu : float
        Dynamic viscosity, [Pa*s]
    sigma : float
        Surface tension, [N/m]

    Returns
    -------
    Ca : float
        Capillary number, [-]

    Notes
    -----
    Used in porous media calculations and film flow calculations.
    Surface tension may gas-liquid, or liquid-liquid.

    .. math::
        Ca = \frac{\text{Viscous forces}}
        {\text{Surface forces}}

    Examples
    --------
    >>> Capillary(1.2, 0.01, .1)
    0.12

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Kundu, Pijush K., Ira M. Cohen, and David R. Dowling. Fluid
       Mechanics. Academic Press, 2012.
    '''
    Ca = V*mu/sigma
    return Ca


def relative_roughness(D, roughness=1.52e-06):
    r'''Calculates relative roughness `eD` using a diameter and the roughness
    of the material of the wall. Default roughness is that of steel.

    .. math::
        eD=\frac{\epsilon}{D}

    Parameters
    ----------
    D : float
        Diameter of pipe, [m]
    roughness : float, optional
        Roughness of pipe wall [m]

    Returns
    -------
    eD : float
        Relative Roughness, [-]

    Examples
    --------
    >>> relative_roughness(0.0254)
    5.9842519685039374e-05
    >>> relative_roughness(0.5, 1E-4)
    0.0002

    References
    ----------
    .. [1] Green, Don, and Robert Perry. Perry's Chemical Engineers' Handbook,
       Eighth Edition. McGraw-Hill Professional, 2007.
    .. [2] Cengel, Yunus, and John Cimbala. Fluid Mechanics: Fundamentals and
       Applications. Boston: McGraw Hill Higher Education, 2006.
    '''
    eD = roughness/D
    return eD


### Misc utilities

def nu_mu_converter(rho, nu=0, mu=0):
    """Specify density and either Kinematic viscosity or Dynamic Viscosity
    by name for the result to be converted to the other.

    >>> nu_mu_converter(998.1,nu=1.01E-6)
    0.001008081
    """
    if nu and mu:
        return Exception('Error: Both parameters given')
    if mu:
        return mu/rho
    elif nu:
        return nu*rho
    else:
        return Exception('Something went wrong.')


def gravity(latitude, height):
    r'''Calculates local acceleration due to gravity `g` according to [1]_.
    Uses latitude and height to calculate `g`.

    .. math::
        g = 9.780356(1 + 0.0052885\sin^2\phi - 0.0000059^22\phi)
        - 3.086\times 10^{-6} H

    Parameters
    ----------
    latitude : float
        Degrees, [degrees]
    height : float
        Height above earth's surface [m]

    Returns
    -------
    g : float
        Acceleration due to gravity, [m/s^2]

    Notes
    -----
    Better models, such as EGM2008 exist.

    Examples
    --------
    >>> gravity(55, 1E4)
    9.784151976863571

    References
    ----------
    .. [1] Haynes, W.M., Thomas J. Bruno, and David R. Lide. CRC Handbook of
       Chemistry and Physics. [Boca Raton, FL]: CRC press, 2014.
    '''
    latitude=latitude*pi/180
    return 9.780356*(1+0.0052885*sin(latitude)**2\
    -0.0000059*sin(2*latitude)**2) -3.086E-6*height

### Friction loss conversion functions

def K_from_f(f, L, D):
    r'''Calculates loss coefficient, K, for a given section of pipe
    at a specified friction factor.

    .. math::
        K = fL/D

    Parameters
    ----------
    f : float
        friction factor of pipe, []
    L : float
        Length of pipe, [m]
    D : float
        Inner diameter of pipe, [m]

    Returns
    -------
    K : float
        Loss coefficient, []

    Notes
    -----
    For fittings with a specified L/D ratio, use D = 1 and set L to
    specified L/D ratio.

    Examples
    --------
    >>> K_from_f(f=0.018, L=100., D=.3)
    6.0
    '''
    K = f*L/D
    return K


def K_from_L_equiv(L_D, f=0.015):
    r'''Calculates loss coefficient, for a given equivalent length (L/D).

    .. math::
        K = f \frac{L}{D}

    Parameters
    ----------
    L_D : float
        Length over diameter, []
    f : float, optional
        Darcy friction factor, [-]

    Returns
    -------
    K : float
        Loss coefficient, []

    Notes
    -----
    Almost identical to `K_from_f`, but with a default friction factor for
    fully turbulent flow in steel pipes.

    Examples
    --------
    >>> K_from_L_equiv(240.)
    3.5999999999999996
    '''
    K = f*L_D
    return K


def dP_from_K(K, rho, V):
    r'''Calculates pressure drop, for a given loss coefficient,
    at a specified density and velocity.

    .. math::
        dP = 0.5K\rho V^2

    Parameters
    ----------
    K : float
        Loss coefficient, []
    rho : float
        Density of fluid, [kg/m^3]
    V : float
        Velocity of fluid in pipe, [m/s]

    Returns
    -------
    dP : float
        Pressure drop, [Pa]

    Notes
    -----
    Loss ciefficient `K` is usually the sum of several factors, including
    the friction factor.

    Examples
    --------
    >>> dP_from_K(K=10, rho=1000, V=3)
    45000.0
    '''
    dP = K*0.5*rho*V**2
    return dP


def head_from_K(K, V):
    r'''Calculates head loss, for a given loss coefficient,
    at a specified velocity.

    .. math::
        \text{head} = \frac{K V^2}{2g}

    Parameters
    ----------
    K : float
        Loss coefficient, []
    V : float
        Velocity of fluid in pipe, [m/s]

    Returns
    -------
    head : float
        Head loss, [m]

    Notes
    -----
    Loss ciefficient `K` is usually the sum of several factors, including
    the friction factor.

    Examples
    --------
    >>> head_from_K(K=10, V=1.5)
    1.1471807396001694
    '''
    head = K*0.5*V**2/g
    return head



### Misc conversion functions
def head_from_P(P, rho):
    r'''Calculates head for a fluid of specified density at specified
    pressure.

    .. math::
        \text{head} = {P\over{\rho g}}

    Parameters
    ----------
    P : float
        Pressure fluid in pipe, [Pa]
    rho : float
        Density of fluid, [kg/m^3]

    Returns
    -------
    head : float
        Head, [m]

    Notes
    -----
    By definition. Head varies with location, inversely propertional to the
    increase in gravitational constant.

    Examples
    --------
    >>> head_from_P(P=1E5, rho=1000.)
    10.197162129779283
    '''
    head = P/rho/g
    return head


def P_from_head(head, rho):
    r'''Calculates head for a fluid of specified density at specified
    pressure.

    .. math::
        P = \rho g \cdot \text{head}

    Parameters
    ----------
    head : float
        Head, [m]
    rho : float
        Density of fluid, [kg/m^3]

    Returns
    -------
    P : float
        Pressure fluid in pipe, [Pa]

    Notes
    -----

    Examples
    --------
    >>> P_from_head(head=5., rho=800.)
    39226.6
    '''
    P = head*rho*g
    return P



### Synonyms
alpha = thermal_diffusivity # synonym for thermal diffusivity
Pr = Prandtl # Synonym
