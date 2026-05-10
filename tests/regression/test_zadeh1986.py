"""Zadeh's two-doctors paradox (Zadeh 1986).

Two physicians independently diagnose a patient. The frame is
``Theta = {meningitis, contusion, brain-tumor}``.

Doctor 1 says::

    m1({meningitis})    = 0.99
    m1({brain-tumor})   = 0.01

Doctor 2 says::

    m2({contusion})     = 0.99
    m2({brain-tumor})   = 0.01

Dempster's rule normalises the only non-conflicting product (on
``brain-tumor``, mass ``0.01 * 0.01 = 0.0001``) to **certainty** that the
patient has a brain tumour — a counter-intuitive conclusion since both
doctors only assigned 1% to that hypothesis. Yager and Dubois-Prade keep the
mass mostly on the ignorance set; PCR5 redistributes the conflict back onto
the actual diagnoses.

This regression locks the canonical numerical outputs in.

References:
    Zadeh, L. A. (1986). A simple view of the Dempster-Shafer theory of
    evidence and its implication for the rule of combination. *AI Magazine*,
    7(2), 85–90.
"""

from __future__ import annotations

import pytest

from carla_evidence import Frame, MassFunction
from carla_evidence.combination import dempster, dubois_prade, pcr5, yager


@pytest.fixture
def theta() -> Frame:
    return Frame.of("meningitis", "contusion", "brain_tumor")


@pytest.fixture
def doctor_1(theta: Frame) -> MassFunction:
    return MassFunction(theta, {("meningitis",): 0.99, ("brain_tumor",): 0.01})


@pytest.fixture
def doctor_2(theta: Frame) -> MassFunction:
    return MassFunction(theta, {("contusion",): 0.99, ("brain_tumor",): 0.01})


class TestDempsterParadox:
    """Dempster collapses everything onto brain_tumor — the paradoxical result."""

    def test_dempster_certifies_brain_tumor(
        self, doctor_1: MassFunction, doctor_2: MassFunction
    ) -> None:
        out = dempster(doctor_1, doctor_2)
        assert out.mass(("brain_tumor",)) == pytest.approx(1.0)

    def test_dempster_zero_for_other_hypotheses(
        self, doctor_1: MassFunction, doctor_2: MassFunction
    ) -> None:
        out = dempster(doctor_1, doctor_2)
        assert out.mass(("meningitis",)) == 0.0
        assert out.mass(("contusion",)) == 0.0


class TestYagerHandlesParadox:
    """Yager keeps almost all mass on Theta (acknowledging the conflict)."""

    def test_yager_mass_on_brain_tumor_stays_tiny(
        self, doctor_1: MassFunction, doctor_2: MassFunction, theta: Frame
    ) -> None:
        out = yager(doctor_1, doctor_2)
        # Only intersection: brain_tumor ∩ brain_tumor = brain_tumor with prob 0.01*0.01.
        assert out.mass(("brain_tumor",)) == pytest.approx(0.0001)
        # Everything else (the conflict mass 0.9999) lands on Theta.
        assert out.mass(theta.omega) == pytest.approx(0.9999)


class TestDuboisPradeHandlesParadox:
    """Dubois-Prade keeps mass on the union of conflicting focals."""

    def test_dubois_prade_concentrates_on_pairs(
        self, doctor_1: MassFunction, doctor_2: MassFunction
    ) -> None:
        out = dubois_prade(doctor_1, doctor_2)
        # The big conflict pair {meningitis} × {contusion} = ∅ → union = {meningitis, contusion}.
        # Product = 0.99 * 0.99 = 0.9801.
        assert out.mass(("meningitis", "contusion")) == pytest.approx(0.9801)
        # brain_tumor ∩ brain_tumor preserves the small intersection.
        assert out.mass(("brain_tumor",)) == pytest.approx(0.0001)


class TestPCR5HandlesParadox:
    """PCR5 redistributes conflict proportionally back to the diagnoses."""

    def test_pcr5_splits_conflict_evenly(
        self, doctor_1: MassFunction, doctor_2: MassFunction
    ) -> None:
        out = pcr5(doctor_1, doctor_2)
        # Conflict pairs and their PCR5 redistribution:
        # (meningitis, contusion):    0.99 * 0.99 = 0.9801, denom = 1.98
        #   → meningitis: 0.99² · 0.99 / 1.98 = 0.49005
        #   → contusion:  0.99 · 0.99² / 1.98 = 0.49005
        # (meningitis, brain_tumor): 0.99 * 0.01 = 0.0099, denom = 1.0
        #   → meningitis: 0.99² · 0.01 / 1.0 = 0.009801
        #   → brain_tumor: 0.99 · 0.01² / 1.0 = 0.000099
        # (brain_tumor, contusion): 0.01 * 0.99 = 0.0099, denom = 1.0
        #   → brain_tumor: 0.01² · 0.99 / 1.0 = 0.000099
        #   → contusion: 0.01 · 0.99² / 1.0 = 0.009801
        # Non-conflict pair: (brain_tumor, brain_tumor) → brain_tumor: 0.0001
        expected_meningitis = 0.49005 + 0.009801
        expected_contusion = 0.49005 + 0.009801
        expected_brain = 0.0001 + 0.000099 + 0.000099
        assert out.mass(("meningitis",)) == pytest.approx(expected_meningitis)
        assert out.mass(("contusion",)) == pytest.approx(expected_contusion)
        assert out.mass(("brain_tumor",)) == pytest.approx(expected_brain)

    def test_pcr5_brain_tumor_stays_minor(
        self, doctor_1: MassFunction, doctor_2: MassFunction
    ) -> None:
        """The decision-maker's takeaway: PCR5 keeps brain_tumor at a few permille,
        not at certainty as Dempster would have it."""
        out = pcr5(doctor_1, doctor_2)
        assert out.mass(("brain_tumor",)) < 0.001
        # And meningitis/contusion remain the leading hypotheses.
        assert out.mass(("meningitis",)) > 0.4
        assert out.mass(("contusion",)) > 0.4
