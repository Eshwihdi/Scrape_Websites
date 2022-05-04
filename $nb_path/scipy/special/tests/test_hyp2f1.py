"""Tests for hyp2f1 for complex values.

Author: Albert Steppi, with credit to Adam Kullberg (FormerPhycisist) for
the implementation of mp_hyp2f1 below, which modifies mpmath's hyp2f1 to
return the same branch as scipy's on the standard branch cut.
"""

import sys
import pytest
import numpy as np
from typing import NamedTuple
from numpy.testing import assert_allclose

from scipy.special import hyp2f1
from scipy.special._testutils import check_version, MissingModule


try:
    import mpmath
except ImportError:
    mpmath = MissingModule("mpmath")


def mp_hyp2f1(a, b, c, z):
    """Return mpmath hyp2f1 calculated on same branch as scipy hyp2f1.

    For most values of a,b,c mpmath returns the x - 0j branch of hyp2f1 on the
    branch cut x=(1,inf) whereas scipy's hyp2f1 calculates the x + 0j branch.
    Thus, to generate the right comparison values on the branch cut, we
    evaluate mpmath.hyp2f1 at x + 1e-15*j.

    The exception to this occurs when c-a=-m in which case both mpmath and
    scipy calculate the x + 0j branch on the branch cut. When this happens
    mpmath.hyp2f1 will be evaluated at the original z point.
    """
    on_branch_cut = z.real > 1.0 and abs(z.imag) < 1.0e-15
    cond1 = abs(c - a - round(c - a)) < 1.0e-15 and round(c - a) <= 0
    cond2 = abs(c - b - round(c - b)) < 1.0e-15 and round(c - b) <= 0
    # Make sure imaginary part is *exactly* zero
    if on_branch_cut:
        z = z.real + 0.0j
    if on_branch_cut and not (cond1 or cond2):
        z_mpmath = z.real + 1.0e-15j
    else:
        z_mpmath = z
    return complex(mpmath.hyp2f1(a, b, c, z_mpmath))


class Hyp2f1TestCase(NamedTuple):
    a: float
    b: float
    c: float
    z: complex
    expected: complex
    rtol: float


class TestHyp2f1:
    """Tests for hyp2f1 for complex values.

    Expected values for test cases were computed using mpmath. See
    `scipy.special._precompute.hyp2f1_data`. The verbose style of specifying
    test cases is used for readability and to make it easier to mark individual
    cases as expected to fail. Expected failures are used to highlight cases
    where improvements are needed. See
    `scipy.special._precompute.hyp2f1_data.make_hyp2f1_test_cases` for a
    function to generate the boilerplate for the test cases.

    Assertions have been added to each test to ensure that the test cases match
    the situations that are intended. A final test `test_test_hyp2f1` checks
    that the expected values in the test cases actually match what is computed
    by mpmath. This test is marked slow even though it isn't particularly slow
    so that it won't run by default on continuous integration builds.
    """
    @pytest.mark.parametrize(
        "hyp2f1_test_case",
        [
            pytest.param(
                Hyp2f1TestCase(
                    a=0.5,
                    b=0.2,
                    c=-10,
                    z=0.2 + 0.2j,
                    expected=np.inf + 0j,
                    rtol=0
                )
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=0.5,
                    b=0.2,
                    c=-10,
                    z=0 + 0j,
                    expected=1 + 0j,
                    rtol=0
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=0.5,
                    b=0,
                    c=-10,
                    z=0.2 + 0.2j,
                    expected=1 + 0j,
                    rtol=0
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=0.5,
                    b=0,
                    c=0,
                    z=0.2 + 0.2j,
                    expected=1 + 0j,
                    rtol=0,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=0.5,
                    b=0.2,
                    c=0,
                    z=0.2 + 0.2j,
                    expected=np.inf + 0j,
                    rtol=0,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=0.5,
                    b=0.2,
                    c=0,
                    z=0 + 0j,
                    expected=np.nan + 0j,
                    rtol=0,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=0.5,
                    b=-5,
                    c=-10,
                    z=0.2 + 0.2j,
                    expected=(1.0495404166666666+0.05708208333333334j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=0.5,
                    b=-10,
                    c=-10,
                    z=0.2 + 0.2j,
                    expected=(1.092966013125+0.13455014673750001j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-10,
                    b=-20,
                    c=-10,
                    z=0.2 + 0.2j,
                    expected=(-0.07712512000000005+0.12752814080000005j),
                    rtol=1e-13,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-1,
                    b=3.2,
                    c=-1,
                    z=0.2 + 0.2j,
                    expected=(1.6400000000000001+0.6400000000000001j),
                    rtol=1e-13,
                ),
            ),
        ]
    )
    def test_c_non_positive_int(self, hyp2f1_test_case):
        a, b, c, z, expected, rtol = hyp2f1_test_case
        assert_allclose(hyp2f1(a, b, c, z), expected, rtol=rtol)

    @pytest.mark.parametrize(
        "hyp2f1_test_case",
        [
            pytest.param(
                Hyp2f1TestCase(
                    a=0.5,
                    b=0.2,
                    c=1.5,
                    z=1 + 0j,
                    expected=1.1496439092239847 + 0j,
                    rtol=1e-15
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=12.3,
                    b=8.0,
                    c=20.31,
                    z=1 + 0j,
                    expected=69280986.75273195 + 0j,
                    rtol=1e-15
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=290.2,
                    b=321.5,
                    c=700.1,
                    z=1 + 0j,
                    expected=1.3396562400934e117 + 0j,
                    rtol=1e-12,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-102.1,
                    b=-20.3,
                    c=1.3,
                    z=1 + 0j,
                    expected=2.7899070752746906e22 + 0j,
                    rtol=1e-15
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-202.6,
                    b=60.3,
                    c=1.5,
                    z=1 + 0j,
                    expected=-1.3113641413099326e-56 + 0j,
                    rtol=1e-12,
                ),
            ),
        ],
    )
    def test_unital_argument(self, hyp2f1_test_case):
        """Tests for case z = 1, c - a - b > 0.

        Expected answers computed using mpmath.
        """
        a, b, c, z, expected, rtol = hyp2f1_test_case
        assert z == 1 and c - a - b > 0  # Tests the test
        assert_allclose(hyp2f1(a, b, c, z), expected, rtol=rtol)

    @pytest.mark.parametrize(
        "hyp2f1_test_case",
        [
            pytest.param(
                Hyp2f1TestCase(
                    a=0.5,
                    b=0.2,
                    c=1.3,
                    z=-1 + 0j,
                    expected=0.9428846409614143 + 0j,
                    rtol=1e-15),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=12.3,
                    b=8.0,
                    c=5.300000000000001,
                    z=-1 + 0j,
                    expected=-4.845809986595704e-06 + 0j,
                    rtol=1e-15
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=221.5,
                    b=90.2,
                    c=132.3,
                    z=-1 + 0j,
                    expected=2.0490488728377282e-42 + 0j,
                    rtol=1e-7,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-102.1,
                    b=-20.3,
                    c=-80.8,
                    z=-1 + 0j,
                    expected=45143784.46783885 + 0j,
                    rtol=1e-7,
                ),
                marks=pytest.mark.xfail(
                    condition=sys.maxsize < 2**32,
                    reason="Fails on 32 bit.",
                )
            ),
        ],
    )
    def test_special_case_z_near_minus_1(self, hyp2f1_test_case):
        """Tests for case z ~ -1, c ~ 1 + a - b

        Expected answers computed using mpmath.
        """
        a, b, c, z, expected, rtol = hyp2f1_test_case
        assert abs(1 + a - b - c) < 1e-15 and abs(z + 1) < 1e-15
        assert_allclose(hyp2f1(a, b, c, z), expected, rtol=rtol)

    @pytest.mark.parametrize(
        "hyp2f1_test_case",
        [
            pytest.param(
                Hyp2f1TestCase(
                    a=-4,
                    b=2.02764642551431,
                    c=1.0561196186065624,
                    z=(0.9473684210526314-0.10526315789473695j),
                    expected=(0.0031961077109535375-0.0011313924606557173j),
                    rtol=1e-12,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-8,
                    b=-7.937789122896016,
                    c=-15.964218273004214,
                    z=(2-0.10526315789473695j),
                    expected=(0.005543763196412503-0.0025948879065698306j),
                    rtol=5e-13,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-8,
                    b=8.095813935368371,
                    c=4.0013768449590685,
                    z=(0.9473684210526314-0.10526315789473695j),
                    expected=(-0.0003054674127221263-9.261359291755414e-05j),
                    rtol=1e-10,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-4,
                    b=-3.956227226099288,
                    c=-3.9316537064827854,
                    z=(1.1578947368421053-0.3157894736842106j),
                    expected=(-0.0020809502580892937-0.0041877333232365095j),
                    rtol=5e-12,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.02764642551431,
                    b=-4,
                    c=2.050308316530781,
                    z=(0.9473684210526314-0.10526315789473695j),
                    expected=(0.0011282435590058734+0.0002027062303465851j),
                    rtol=5e-13,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.937789122896016,
                    b=-8,
                    c=-15.964218273004214,
                    z=(1.3684210526315788+0.10526315789473673j),
                    expected=(-9.134907719238265e-05-0.00040219233987390723j),
                    rtol=5e-12,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=4.080187217753502,
                    b=-4,
                    c=4.0013768449590685,
                    z=(0.9473684210526314-0.10526315789473695j),
                    expected=(-0.000519013062087489-0.0005855883076830948j),
                    rtol=5e-12,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-10000,
                    b=2.2,
                    c=93459345.3,
                    z=(2+2j),
                    expected=(0.9995292071559088-0.00047047067522659253j),
                    rtol=1e-12,
                ),
            ),
        ]
    )
    def test_a_b_negative_int(self, hyp2f1_test_case):
        a, b, c, z, expected, rtol = hyp2f1_test_case
        assert a == int(a) and a < 0 or b == int(b) and b < 0  # Tests the test
        assert_allclose(hyp2f1(a, b, c, z), expected, rtol=rtol)

    @pytest.mark.parametrize(
        "hyp2f1_test_case",
        [
            pytest.param(
                Hyp2f1TestCase(
                    a=-0.5,
                    b=-0.9629749245209605,
                    c=-15.5,
                    z=(1.1578947368421053-1.1578947368421053j),
                    expected=(0.9778506962676361+0.044083801141231616j),
                    rtol=1e-12,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=8.5,
                    b=-3.9316537064827854,
                    c=1.5,
                    z=(0.9473684210526314-0.10526315789473695j),
                    expected=(4.0793167523167675-10.11694246310966j),
                    rtol=6e-12,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=8.5,
                    b=-0.9629749245209605,
                    c=2.5,
                    z=(1.1578947368421053-0.10526315789473695j),
                    expected=(-2.9692999501916915+0.6394599899845594j),
                    rtol=1e-11,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-0.5,
                    b=-0.9629749245209605,
                    c=-15.5,
                    z=(1.5789473684210522-1.1578947368421053j),
                    expected=(0.9493076367106102-0.04316852977183447j),
                    rtol=1e-11,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-0.9220024191881196,
                    b=-0.5,
                    c=-15.5,
                    z=(0.5263157894736841+0.10526315789473673j),
                    expected=(0.9844377175631795-0.003120587561483841j),
                    rtol=1e-10,
                ),
            ),
        ],
    )
    def test_a_b_neg_int_after_euler_hypergeometric_transformation(
        self, hyp2f1_test_case
    ):
        a, b, c, z, expected, rtol = hyp2f1_test_case
        assert (  # Tests the test
            (abs(c - a - int(c - a)) < 1e-15 and c - a < 0) or
            (abs(c - b - int(c - b)) < 1e-15 and c - b < 0)
        )
        assert_allclose(hyp2f1(a, b, c, z), expected, rtol=rtol)

    @pytest.mark.parametrize(
        "hyp2f1_test_case",
        [
            pytest.param(
                Hyp2f1TestCase(
                    a=-0.9220024191881196,
                    b=-0.9629749245209605,
                    c=-15.963511401609862,
                    z=(0.10526315789473673-0.3157894736842106j),
                    expected=(0.9941449585778349+0.01756335047931358j),
                    rtol=1e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=1.0272592605282642,
                    b=-0.9629749245209605,
                    c=-15.963511401609862,
                    z=(0.5263157894736841+0.5263157894736841j),
                    expected=(1.0388722293372104-0.09549450380041416j),
                    rtol=5e-11,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.02764642551431,
                    b=1.0561196186065624,
                    c=-7.93846038215665,
                    z=(0.10526315789473673+0.7368421052631575j),
                    expected=(2.1948378809826434+24.934157235172222j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.02764642551431,
                    b=16.088264119063613,
                    c=8.031683612216888,
                    z=(0.3157894736842106-0.736842105263158j),
                    expected=(-0.4075277891264672-0.06819344579666956j),
                    rtol=2e-12,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=4.080187217753502,
                    b=2.050308316530781,
                    c=8.031683612216888,
                    z=(0.7368421052631575-0.10526315789473695j),
                    expected=(2.833535530740603-0.6925373701408158j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.02764642551431,
                    b=2.050308316530781,
                    c=4.078873014294075,
                    z=(0.10526315789473673-0.3157894736842106j),
                    expected=(1.005347176329683-0.3580736009337313j),
                    rtol=5e-16,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-0.9220024191881196,
                    b=-0.9629749245209605,
                    c=-15.963511401609862,
                    z=(0.3157894736842106-0.5263157894736843j),
                    expected=(0.9824353641135369+0.029271018868990268j),
                    rtol=5e-13,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-0.9220024191881196,
                    b=-0.9629749245209605,
                    c=-159.63511401609862,
                    z=(0.3157894736842106-0.5263157894736843j),
                    expected=(0.9982436200365834+0.002927268199671111j),
                    rtol=1e-7,
                ),
                marks=pytest.mark.xfail(reason="Poor convergence.")
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.02764642551431,
                    b=16.088264119063613,
                    c=8.031683612216888,
                    z=(0.5263157894736841-0.5263157894736843j),
                    expected=(-0.6906825165778091+0.8176575137504892j),
                    rtol=5e-13,
                ),
            ),
        ]
    )
    def test_region1(self, hyp2f1_test_case):
        """|z| < 0.9 and real(z) >= 0."""
        a, b, c, z, expected, rtol = hyp2f1_test_case
        assert abs(z) < 0.9 and z.real >= 0  # Tests the test
        assert_allclose(hyp2f1(a, b, c, z), expected, rtol=rtol)

    @pytest.mark.parametrize(
        "hyp2f1_test_case",
        [
            pytest.param(
                Hyp2f1TestCase(
                    a=2.02764642551431,
                    b=1.0561196186065624,
                    c=4.078873014294075,
                    z=(-0.3157894736842106+0.7368421052631575j),
                    expected=(0.7751915029081136+0.24068493258607315j),
                    rtol=5e-15,
                ),
            ),
        ]
    )
    def test_region2(self, hyp2f1_test_case):
        """|z| < 1 and real(z) < 0."""
        a, b, c, z, expected, rtol = hyp2f1_test_case
        assert abs(z) < 1 and z.real < 0  # Tests the test
        assert_allclose(hyp2f1(a, b, c, z), expected, rtol=rtol)

    @pytest.mark.parametrize(
        "hyp2f1_test_case",
        [
            pytest.param(
                Hyp2f1TestCase(
                    a=16.25,
                    b=4.25,
                    c=2.5,
                    z=(0.4931034482758623-0.7965517241379311j),
                    expected=(38.41207903409937-30.510151276075792j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.0,
                    b=16.087593263474208,
                    c=16.088264119063613,
                    z=(0.5689655172413794-0.7965517241379311j),
                    expected=(-0.6667857912761286-1.0206224321443573j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=8.0,
                    b=1.0272592605282642,
                    c=-7.949900487447654,
                    z=(0.4931034482758623-0.7965517241379311j),
                    expected=(1679024.1647997478-2748129.775857212j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=4.080187217753502,
                    b=16.0,
                    c=-7.949900487447654,
                    z=(0.4931034482758623-0.7965517241379311j),
                    expected=(424747226301.16986-1245539049327.2856j),
                    rtol=1e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.02764642551431,
                    b=-15.964218273004214,
                    c=4.0,
                    z=(0.4931034482758623-0.7965517241379311j),
                    expected=(-0.0057826199201757595+0.026359861999025885j),
                    rtol=5e-06,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.02764642551431,
                    b=-0.9629749245209605,
                    c=2.0397202577726152,
                    z=(0.5689655172413794-0.7965517241379311j),
                    expected=(0.4671901063492606+0.7769632229834897j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.0,
                    b=-3.956227226099288,
                    c=-7.949900487447654,
                    z=(0.4931034482758623+0.7965517241379312j),
                    expected=(0.9422283708145973+1.3476905754773343j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=1.0,
                    b=-15.980848054962111,
                    c=-15.964218273004214,
                    z=(0.4931034482758623-0.7965517241379311j),
                    expected=(0.4168719497319604-0.9770953555235625j),
                    rtol=5e-10,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-0.5,
                    b=16.088264119063613,
                    c=2.5,
                    z=(0.5689655172413794+0.7965517241379312j),
                    expected=(1.279096377550619-2.173827694297929j),
                    rtol=5e-12,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-1.9214641416286231,
                    b=4.0013768449590685,
                    c=2.0397202577726152,
                    z=(0.4931034482758623+0.7965517241379312j),
                    expected=(-2.071520656161738-0.7846098268395909j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-0.9220024191881196,
                    b=8.0,
                    c=-0.9629749245209605,
                    z=(0.5689655172413794-0.7965517241379311j),
                    expected=(-7.740015495862889+3.386766435696699j),
                    rtol=5e-12,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-1.9214641416286231,
                    b=16.088264119063613,
                    c=-7.93846038215665,
                    z=(0.4931034482758623+0.7965517241379312j),
                    expected=(-6318.553685853241-7133.416085202879j),
                    rtol=1e-10,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-15.980848054962111,
                    b=-3.9316537064827854,
                    c=16.056809865262608,
                    z=(0.5689655172413794+0.7965517241379312j),
                    expected=(-0.8854577905547399+8.135089099967278j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-1.9214641416286231,
                    b=-0.9629749245209605,
                    c=4.078873014294075,
                    z=(0.4931034482758623+0.7965517241379312j),
                    expected=(1.224291301521487+0.36014711766402485j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-15.75,
                    b=-0.75,
                    c=-1.5,
                    z=(0.4931034482758623+0.7965517241379312j),
                    expected=(-1.5765685855028473-3.9399766961046323j),
                    rtol=1e-3,
                ),
                marks=pytest.mark.xfail(
                    reason="Unhandled parameters."
                )
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-15.980848054962111,
                    b=-1.92872979730171,
                    c=-7.93846038215665,
                    z=(0.5689655172413794-0.7965517241379311j),
                    expected=(56.794588688231194+4.556286783533971j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=4.5,
                    b=4.5,
                    c=2.050308316530781,
                    z=(0.5689655172413794+0.7965517241379312j),
                    expected=(-4.251456563455306+6.737837111569671j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=4.5,
                    b=8.5,
                    c=-1.92872979730171,
                    z=(0.4931034482758623-0.7965517241379311j),
                    expected=(2177143.9156599627-3313617.2748088865j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.5,
                    b=-1.5,
                    c=4.0013768449590685,
                    z=(0.4931034482758623-0.7965517241379311j),
                    expected=(0.45563554481603946+0.6212000158060831j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=8.5,
                    b=-7.5,
                    c=-15.964218273004214,
                    z=(0.4931034482758623+0.7965517241379312j),
                    expected=(61.03201617828073-37.185626416756214j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-15.5,
                    b=16.5,
                    c=4.0013768449590685,
                    z=(0.4931034482758623+0.7965517241379312j),
                    expected=(-33143.425963520735+20790.608514722644j),
                    rtol=1e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-0.5,
                    b=4.5,
                    c=-0.9629749245209605,
                    z=(0.5689655172413794+0.7965517241379312j),
                    expected=(30.778600270824423-26.65160354466787j),
                    rtol=5e-13,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-0.5,
                    b=-3.5,
                    c=16.088264119063613,
                    z=(0.5689655172413794-0.7965517241379311j),
                    expected=(1.0629792615560487-0.08308454486044772j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-3.5,
                    b=-7.5,
                    c=-0.9629749245209605,
                    z=(0.4931034482758623-0.7965517241379311j),
                    expected=(17431.571802591767+3553.7129767034507j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.25,
                    b=8.25,
                    c=16.5,
                    z=(0.11379310344827598+0.9482758620689657j),
                    expected=(0.4468600750211926+0.7313214934036885j),
                    rtol=1e-3,
                ),
                marks=pytest.mark.xfail(
                    reason="Unhandled parameters."
                )
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=8.25,
                    b=16.25,
                    c=4.5,
                    z=(0.3413793103448277+0.8724137931034486j),
                    expected=(-3.905704438293991+3.693347860329299j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=4.25,
                    b=4.25,
                    c=-0.5,
                    z=(0.11379310344827598-0.9482758620689655j),
                    expected=(-40.31777941834244-89.89852492432011j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=1.0272592605282642,
                    b=8.0,
                    c=-15.964218273004214,
                    z=(0.11379310344827598-0.9482758620689655j),
                    expected=(52584.347773055284-109197.86244309516j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=8.095813935368371,
                    b=-15.964218273004214,
                    c=16.056809865262608,
                    z=(0.03793103448275881+0.9482758620689657j),
                    expected=(-1.187733570412592-1.5147865053584582j),
                    rtol=5e-10,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=4.080187217753502,
                    b=-3.9316537064827854,
                    c=1.0651378143226575,
                    z=(0.26551724137931054+0.9482758620689657j),
                    expected=(13.077494677898947+35.071599628224966j),
                    rtol=5e-13,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=4.080187217753502,
                    b=-3.5,
                    c=-3.5,
                    z=(0.26551724137931054+0.8724137931034486j),
                    expected=(-0.5359656237994614-0.2344483936591811j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=4.25,
                    b=-3.75,
                    c=-1.5,
                    z=(0.26551724137931054+0.9482758620689657j),
                    expected=(1204.8114871663133+64.41022826840198j),
                    rtol=5e-13,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-1.9214641416286231,
                    b=16.0,
                    c=4.0013768449590685,
                    z=(0.03793103448275881-0.9482758620689655j),
                    expected=(-9.85268872413994+7.011107558429154j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.937789122896016,
                    b=16.0,
                    c=4.0013768449590685,
                    z=(0.3413793103448277-0.8724137931034484j),
                    expected=(528.5522951158454-1412.21630264791j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-15.5,
                    b=1.0561196186065624,
                    c=-7.5,
                    z=(0.4172413793103451+0.8724137931034486j),
                    expected=(133306.45260685298+256510.7045225382j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.937789122896016,
                    b=8.077282662161238,
                    c=-15.963511401609862,
                    z=(0.3413793103448277-0.8724137931034484j),
                    expected=(-0.998555715276967+2.774198742229889j),
                    rtol=5e-11,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.75,
                    b=-0.75,
                    c=1.5,
                    z=(0.11379310344827598-0.9482758620689655j),
                    expected=(2.072445019723025-2.9793504811373515j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-15.5,
                    b=-1.92872979730171,
                    c=1.5,
                    z=(0.11379310344827598-0.9482758620689655j),
                    expected=(-41.87581944176649-32.52980303527139j),
                    rtol=5e-13,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-3.75,
                    b=-15.75,
                    c=-0.5,
                    z=(0.11379310344827598-0.9482758620689655j),
                    expected=(-3729.6214864209774-30627.510509112635j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-3.956227226099288,
                    b=-15.964218273004214,
                    c=-0.906685989801748,
                    z=(0.03793103448275881+0.9482758620689657j),
                    expected=(-131615.07820609974+145596.13384245415j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=1.5,
                    b=16.5,
                    c=16.088264119063613,
                    z=(0.26551724137931054+0.8724137931034486j),
                    expected=(0.18981844071070744+0.7855036242583742j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=16.5,
                    b=8.5,
                    c=-3.9316537064827854,
                    z=(0.11379310344827598-0.9482758620689655j),
                    expected=(110224529.2376068+128287212.04290268j),
                    rtol=5e-13,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.5,
                    b=-7.5,
                    c=4.0013768449590685,
                    z=(0.3413793103448277-0.8724137931034484j),
                    expected=(0.2722302180888523-0.21790187837266162j),
                    rtol=1e-12,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=8.5,
                    b=-7.5,
                    c=-15.964218273004214,
                    z=(0.11379310344827598-0.9482758620689655j),
                    expected=(-2.8252338010989035+2.430661949756161j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-3.5,
                    b=16.5,
                    c=4.0013768449590685,
                    z=(0.03793103448275881+0.9482758620689657j),
                    expected=(-20.604894257647945+74.5109432558078j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.5,
                    b=8.5,
                    c=-0.9629749245209605,
                    z=(0.3413793103448277+0.8724137931034486j),
                    expected=(-2764422.521269463-3965966.9965808876j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-1.5,
                    b=-0.5,
                    c=1.0561196186065624,
                    z=(0.26551724137931054+0.9482758620689657j),
                    expected=(1.2262338560994905+0.6545051266925549j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-0.5,
                    b=-15.5,
                    c=-7.949900487447654,
                    z=(0.4172413793103451-0.8724137931034484j),
                    expected=(-2258.1590330318213+8860.193389158803j),
                    rtol=1e-10,
                ),
            ),
        ]
    )
    def test_region4(self, hyp2f1_test_case):
        """0.9 <= |z| <= 1 and |1 - z| >= 1.

        This region is unhandled by of the standard transformations and
        needs special care.
        """
        a, b, c, z, expected, rtol = hyp2f1_test_case
        assert 0.9 <= abs(z) <= 1 and abs(1 - z) >= 0.9  # Tests the test
        assert_allclose(hyp2f1(a, b, c, z), expected, rtol=rtol)

    @pytest.mark.parametrize(
        "hyp2f1_test_case",
        [
            pytest.param(
                Hyp2f1TestCase(
                    a=4.5,
                    b=16.088264119063613,
                    c=8.5,
                    z=(0.6448275862068968+0.8724137931034486j),
                    expected=(0.018601324701770394-0.07618420586062377j),
                    rtol=5e-08,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=8.25,
                    b=4.25,
                    c=4.5,
                    z=(0.6448275862068968-0.8724137931034484j),
                    expected=(-1.391549471425551-0.118036604903893j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.02764642551431,
                    b=2.050308316530781,
                    c=-1.9631175993998025,
                    z=(0.6448275862068968+0.8724137931034486j),
                    expected=(-2309.178768155151-1932.7247727595172j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=16.087593263474208,
                    b=1.0,
                    c=-15.964218273004214,
                    z=(0.6448275862068968+0.8724137931034486j),
                    expected=(85592537010.05054-8061416766688.324j),
                    rtol=1e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=8.095813935368371,
                    b=-0.5,
                    c=1.5,
                    z=(0.6448275862068968+0.8724137931034486j),
                    expected=(1.2334498208515172-2.1639498536219732j),
                    rtol=5e-11,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=16.087593263474208,
                    b=-15.964218273004214,
                    c=4.0,
                    z=(0.6448275862068968+0.8724137931034486j),
                    expected=(102266.35398605966-44976.97828737755j),
                    rtol=1e-3,
                ),
                marks=pytest.mark.xfail(
                    reason="Unhandled parameters."
                )
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=4.0,
                    b=-3.956227226099288,
                    c=-15.964218273004214,
                    z=(0.6448275862068968-0.8724137931034484j),
                    expected=(-2.9590030930007236-4.190770764773225j),
                    rtol=5e-13,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=4.080187217753502,
                    b=-15.5,
                    c=-7.5,
                    z=(0.5689655172413794-0.8724137931034484j),
                    expected=(-112554838.92074208+174941462.9202412j),
                    rtol=5e-05,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-15.980848054962111,
                    b=2.050308316530781,
                    c=1.0,
                    z=(0.6448275862068968-0.8724137931034484j),
                    expected=(3.7519882374080145+7.360753798667486j),
                    rtol=5e-13,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.937789122896016,
                    b=2.050308316530781,
                    c=4.0,
                    z=(0.6448275862068968-0.8724137931034484j),
                    expected=(0.000181132943964693+0.07742903103815582j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.937789122896016,
                    b=4.0013768449590685,
                    c=-1.9631175993998025,
                    z=(0.5689655172413794+0.8724137931034486j),
                    expected=(386338.760913596-386166.51762171905j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-15.980848054962111,
                    b=8.0,
                    c=-1.92872979730171,
                    z=(0.6448275862068968+0.8724137931034486j),
                    expected=(1348667126.3444858-2375132427.158893j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-3.5,
                    b=-0.9629749245209605,
                    c=4.5,
                    z=(0.5689655172413794+0.8724137931034486j),
                    expected=(1.428353429538678+0.6472718120804372j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.937789122896016,
                    b=-0.9629749245209605,
                    c=2.0397202577726152,
                    z=(0.5689655172413794-0.8724137931034484j),
                    expected=(3.1439267526119643-3.145305240375117j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-1.9214641416286231,
                    b=-15.964218273004214,
                    c=-7.93846038215665,
                    z=(0.6448275862068968-0.8724137931034484j),
                    expected=(75.27467675681773+144.0946946292215j),
                    rtol=1e-07,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-3.75,
                    b=-7.75,
                    c=-7.5,
                    z=(0.5689655172413794+0.8724137931034486j),
                    expected=(-0.3699450626264222+0.8732812475910993j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=1.5,
                    b=16.5,
                    c=1.0561196186065624,
                    z=(0.5689655172413794-0.8724137931034484j),
                    expected=(5.5361025821300665-2.4709693474656285j),
                    rtol=5e-09,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=1.5,
                    b=8.5,
                    c=-3.9316537064827854,
                    z=(0.6448275862068968-0.8724137931034484j),
                    expected=(-782805.6699207705-537192.581278909j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.5,
                    b=-15.5,
                    c=1.0561196186065624,
                    z=(0.6448275862068968+0.8724137931034486j),
                    expected=(12.345113400639693-14.993248992902007j),
                    rtol=0.0005,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=1.5,
                    b=-0.5,
                    c=-15.964218273004214,
                    z=(0.6448275862068968+0.8724137931034486j),
                    expected=(23.698109392667842+97.15002033534108j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.5,
                    b=16.5,
                    c=4.0013768449590685,
                    z=(0.6448275862068968-0.8724137931034484j),
                    expected=(1115.2978631811834+915.9212658718577j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-15.5,
                    b=16.5,
                    c=-0.9629749245209605,
                    z=(0.6448275862068968+0.8724137931034486j),
                    expected=(642077722221.6489+535274495398.21027j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.5,
                    b=-3.5,
                    c=4.0013768449590685,
                    z=(0.5689655172413794+0.8724137931034486j),
                    expected=(-5.689219222945697+16.877463062787143j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-15.5,
                    b=-1.5,
                    c=-0.9629749245209605,
                    z=(0.5689655172413794-0.8724137931034484j),
                    expected=(-44.32070290703576+1026.9127058617403j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=16.25,
                    b=2.25,
                    c=4.5,
                    z=(0.11379310344827598-1.024137931034483j),
                    expected=(-0.021965227124574663+0.009908300237809064j),
                    rtol=1e-3,
                ),
                marks=pytest.mark.xfail(
                    reason="Unhandled parameters."
                )
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.02764642551431,
                    b=1.5,
                    c=16.5,
                    z=(0.26551724137931054+1.024137931034483j),
                    expected=(1.0046072901244183+0.19945500134119992j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=16.087593263474208,
                    b=1.0,
                    c=-3.9316537064827854,
                    z=(0.3413793103448277+0.9482758620689657j),
                    expected=(21022.30133421465+49175.98317370489j),
                    rtol=5e-13,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=4.080187217753502,
                    b=16.088264119063613,
                    c=-1.9631175993998025,
                    z=(0.4172413793103451-0.9482758620689655j),
                    expected=(-7024239.358547302+2481375.02681063j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=16.25,
                    b=-15.75,
                    c=1.5,
                    z=(0.18965517241379315+1.024137931034483j),
                    expected=(92371704.94848-403546832.548352j),
                    rtol=5e-06,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=8.5,
                    b=-7.949900487447654,
                    c=8.5,
                    z=(0.26551724137931054-1.024137931034483j),
                    expected=(1.9335109845308265+5.986542524829654j),
                    rtol=5e-10,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=8.095813935368371,
                    b=-1.92872979730171,
                    c=-7.93846038215665,
                    z=(0.4931034482758623+0.8724137931034486j),
                    expected=(-122.52639696039328-59.72428067512221j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=16.25,
                    b=-1.75,
                    c=-1.5,
                    z=(0.4931034482758623+0.9482758620689657j),
                    expected=(-90.40642053579428+50.50649180047921j),
                    rtol=5e-08,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-3.5,
                    b=8.077282662161238,
                    c=16.5,
                    z=(0.4931034482758623+0.9482758620689657j),
                    expected=(-0.2155745818150323-0.564628986876639j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-0.9220024191881196,
                    b=1.0561196186065624,
                    c=8.031683612216888,
                    z=(0.4172413793103451-0.9482758620689655j),
                    expected=(0.9503140488280465+0.11574960074292677j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-0.75,
                    b=2.25,
                    c=-15.5,
                    z=(0.4172413793103451+0.9482758620689657j),
                    expected=(0.9285862488442175+0.8203699266719692j),
                    rtol=5e-13,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.75,
                    b=4.25,
                    c=-15.5,
                    z=(0.3413793103448277-0.9482758620689655j),
                    expected=(-1.0509834850116921-1.1145522325486075j),
                    rtol=1e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.937789122896016,
                    b=-0.9629749245209605,
                    c=2.0397202577726152,
                    z=(0.4931034482758623-0.9482758620689655j),
                    expected=(2.88119116536769-3.4249933450696806j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-15.5,
                    b=-15.964218273004214,
                    c=16.5,
                    z=(0.18965517241379315+1.024137931034483j),
                    expected=(199.65868451496038+347.79384207302877j),
                    rtol=1e-13,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-15.75,
                    b=-15.75,
                    c=-3.5,
                    z=(0.4931034482758623-0.8724137931034484j),
                    expected=(-208138312553.07013+58631611809.026955j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.937789122896016,
                    b=-15.5,
                    c=-7.5,
                    z=(0.3413793103448277+0.9482758620689657j),
                    expected=(-23032.90519856288-18256.94050457296j),
                    rtol=5e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=4.5,
                    b=1.5,
                    c=1.0561196186065624,
                    z=(0.4931034482758623-0.8724137931034484j),
                    expected=(1.507342459587056+1.2332023580148403j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=2.5,
                    b=4.5,
                    c=-3.9316537064827854,
                    z=(0.4172413793103451+0.9482758620689657j),
                    expected=(7044.766127108853-40210.365567285575j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=1.5,
                    b=-1.5,
                    c=1.0561196186065624,
                    z=(0.03793103448275881+1.024137931034483j),
                    expected=(0.2725347741628333-2.247314875514784j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=4.5,
                    b=-1.5,
                    c=-7.949900487447654,
                    z=(0.26551724137931054+1.024137931034483j),
                    expected=(-11.250200011017546+12.597393659160472j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.5,
                    b=8.5,
                    c=16.088264119063613,
                    z=(0.26551724137931054+1.024137931034483j),
                    expected=(-0.18515160890991517+0.7959014164484782j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-7.5,
                    b=16.5,
                    c=-3.9316537064827854,
                    z=(0.3413793103448277-1.024137931034483j),
                    expected=(998246378.8556538+1112032928.103645j),
                    rtol=5e-14,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-1.5,
                    b=-3.5,
                    c=2.050308316530781,
                    z=(0.03793103448275881+1.024137931034483j),
                    expected=(0.5527670397711952+2.697662715303637j),
                    rtol=1e-15,
                ),
            ),
            pytest.param(
                Hyp2f1TestCase(
                    a=-15.5,
                    b=-1.5,
                    c=-0.9629749245209605,
                    z=(0.4931034482758623-0.8724137931034484j),
                    expected=(55.396931662136886+968.467463806326j),
                    rtol=5e-14,
                ),
            ),
        ]
    )
    def test_region5(self, hyp2f1_test_case):
        """1 < |z| < 1.1 and |1 - z| >= 0.9 and real(z) >= 0"""
        a, b, c, z, expected, rtol = hyp2f1_test_case
        assert 1 < abs(z) < 1.1 and abs(1 - z) >= 0.9 and z.real >= 0
        assert_allclose(hyp2f1(a, b, c, z), expected, rtol=rtol)

    # Marked as slow so it won't run by default.
    @pytest.mark.slow
    @check_version(mpmath, "1.0.0")
    def test_test_hyp2f1(self):
        """Test that expected values match what is computed by mpmath.

        This gathers the parameters for the test cases out of the pytest marks.
        The parameters are a, b, c, z, expected, rtol, where expected should
        be the value of hyp2f1(a, b, c, z) computed with mpmath. The test
        recomputes hyp2f1(a, b, c, z) using mpmath and verifies that expected
        actually is the correct value. This allows the data for the tests to
        live within the test code instead of an external datafile, while
        avoiding having to compute the results with mpmath during the test,
        except for when slow tests are being run.
        """
        test_methods = [
            test_method for test_method in dir(self)
            if test_method.startswith('test') and
            # Filter properties and attributes (futureproofing).
            callable(getattr(self, test_method)) and
            # Filter out this test
            test_method != 'test_test_hyp2f1'
        ]
        for test_method in test_methods:
            params = self._get_test_parameters(getattr(self, test_method))
            for a, b, c, z, expected, _ in params:
                assert_allclose(mp_hyp2f1(a, b, c, z), expected, rtol=2.25e-16)

    def _get_test_parameters(self, test_method):
        """Get pytest.mark parameters for a test in this class."""
        return [
            case.values[0] for mark in test_method.pytestmark
            if mark.name == 'parametrize'
            for case in mark.args[1]
        ]
