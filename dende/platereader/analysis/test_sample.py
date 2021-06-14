from .sample import Sample, Treatment, Material, create_sample_from_string


def test_sample():

    actual = create_sample_from_string("p.patens$")

    expected = Sample(
        Material("p.patens"),
    )

    assert(actual == expected)

    actual = create_sample_from_string("p.patens$H202")

    expected = Sample(
        Material("p.patens"),
        Treatment("H202")
    )

    assert(actual == expected)

    actual = create_sample_from_string("*WT*$MCLA")

    expected = Sample(
        Material("WT", True),
        Treatment("MCLA")
    )

    assert(actual == expected)

    actual = create_sample_from_string("*WT*$MCLA")

    expected = Sample(
        Material("WT", False),
        Treatment("MCLA")
    )

    assert(actual != expected)