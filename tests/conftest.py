from pathlib import Path
import pytest
from ep_mapper.schema import DeviceMetadata

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def scenario1_pdf() -> Path:
    return FIXTURES_DIR / "scenario1_class_i.pdf"


@pytest.fixture
def scenario2_pdf() -> Path:
    return FIXTURES_DIR / "scenario2_class_iia.pdf"


@pytest.fixture
def scenario3_pdf() -> Path:
    return FIXTURES_DIR / "scenario3_class_iib.pdf"


@pytest.fixture
def meta_scenario1() -> DeviceMetadata:
    return DeviceMetadata(
        device_name="SimpStrap Pro",
        intended_purpose="Management of minor skin wounds in community settings",
        device_class="I",
        ivd=False,
        active=False,
        implantable=False,
        radiation=False,
        software=False,
    )


@pytest.fixture
def meta_scenario2() -> DeviceMetadata:
    return DeviceMetadata(
        device_name="VenaFlow 3000",
        intended_purpose="Controlled IV medication delivery in hospital settings",
        device_class="IIa",
        ivd=False,
        active=True,
        implantable=False,
        radiation=False,
        software=True,
    )


@pytest.fixture
def meta_scenario3() -> DeviceMetadata:
    return DeviceMetadata(
        device_name="CerebroStim X1",
        intended_purpose="Management of treatment-resistant epilepsy via neural stimulation",
        device_class="IIb",
        ivd=False,
        active=True,
        implantable=True,
        radiation=False,
        software=True,
    )
