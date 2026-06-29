import pytest
from ep_mapper.schema import DeviceMetadata
from ep_mapper.applicability import ep_applicability_filter, classification_warnings

EP_NUMBERS = ["1","2","3","4","5","6","7","8","9","10","11","12","13","13A","13B","13C","14","15"]

FULL_DEVICE = DeviceMetadata(
    device_name="FullDevice",
    intended_purpose="Test",
    device_class="IIb",
    ivd=True,
    active=True,
    implantable=True,
    radiation=True,
    software=True,
)

PASSIVE_NON_IVD = DeviceMetadata(
    device_name="Passive",
    intended_purpose="Test",
    device_class="I",
    ivd=False,
    active=False,
    implantable=False,
    radiation=False,
    software=False,
)

IVD_DEVICE = DeviceMetadata(
    device_name="IVD",
    intended_purpose="Blood glucose monitoring",
    device_class="IIa",
    ivd=True,
    active=False,
    implantable=False,
    radiation=False,
    software=False,
)


def test_all_eps_applicable_for_full_device():
    result = ep_applicability_filter(FULL_DEVICE, EP_NUMBERS)
    for ep in EP_NUMBERS:
        assert result[ep][0] == "applicable", f"EP {ep} should be applicable for full device"


def test_ep11_not_applicable_when_no_radiation():
    result = ep_applicability_filter(PASSIVE_NON_IVD, EP_NUMBERS)
    assert result["11"][0] == "not_applicable"
    assert "cl 11" in result["11"][1]


def test_ep12_not_applicable_when_passive_no_software():
    result = ep_applicability_filter(PASSIVE_NON_IVD, EP_NUMBERS)
    assert result["12"][0] == "not_applicable"
    assert "cl 12" in result["12"][1]


def test_ep13a_not_applicable_when_not_implantable():
    result = ep_applicability_filter(PASSIVE_NON_IVD, EP_NUMBERS)
    assert result["13A"][0] == "not_applicable"
    assert "cl 13A" in result["13A"][1]


def test_ep13b_not_applicable_when_no_software():
    result = ep_applicability_filter(PASSIVE_NON_IVD, EP_NUMBERS)
    assert result["13B"][0] == "not_applicable"
    assert "cl 13B" in result["13B"][1]


def test_ep13c_always_applicable():
    result = ep_applicability_filter(PASSIVE_NON_IVD, EP_NUMBERS)
    assert result["13C"][0] == "applicable"


def test_ep15_not_applicable_for_non_ivd():
    result = ep_applicability_filter(PASSIVE_NON_IVD, EP_NUMBERS)
    assert result["15"][0] == "not_applicable"
    assert "cl 15" in result["15"][1]


def test_ep15_applicable_for_ivd():
    result = ep_applicability_filter(IVD_DEVICE, EP_NUMBERS)
    assert result["15"][0] == "applicable"


def test_applicability_basis_none_when_applicable():
    result = ep_applicability_filter(FULL_DEVICE, EP_NUMBERS)
    for ep in EP_NUMBERS:
        assert result[ep][1] is None, f"EP {ep}: applicability_basis should be None when applicable"


def test_classification_warning_class_i_software():
    meta = DeviceMetadata("X","Y","I",False,False,False,False,True)
    warns = classification_warnings(meta)
    assert any("Class I" in w and "software" in w.lower() for w in warns)


def test_classification_warning_class_i_implantable():
    meta = DeviceMetadata("X","Y","I",False,False,True,False,False)
    warns = classification_warnings(meta)
    assert any("Class I" in w and "implantable" in w.lower() for w in warns)


def test_no_warnings_for_typical_class_i():
    meta = DeviceMetadata("X","Y","I",False,False,False,False,False)
    assert classification_warnings(meta) == []
