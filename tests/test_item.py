from pyflow.item import Item


class TestModifiers:
    def test_alt_mod(self):
        item = Item(title="test")
        item.set_alt_mod(arg="foo", subtitle="bar")
        assert item._mods["alt"]["arg"] == "foo"
        assert item._mods["alt"]["subtitle"] == "bar"
        assert item._mods["alt"]["valid"] is True
        assert "variables" not in item._mods["alt"]

    def test_cmd_mod(self):
        item = Item(title="test")
        item.set_cmd_mod(arg="foo", subtitle="bar")
        assert item._mods["cmd"]["arg"] == "foo"
        assert item._mods["cmd"]["subtitle"] == "bar"

    def test_ctrl_mod(self):
        item = Item(title="test")
        item.set_ctrl_mod(arg="foo", subtitle="bar")
        assert item._mods["ctrl"]["arg"] == "foo"
        assert item._mods["ctrl"]["subtitle"] == "bar"
        assert item._mods["ctrl"]["valid"] is True

    def test_shift_mod(self):
        item = Item(title="test")
        item.set_shift_mod(arg="foo", subtitle="bar")
        assert item._mods["shift"]["arg"] == "foo"
        assert item._mods["shift"]["subtitle"] == "bar"
        assert item._mods["shift"]["valid"] is True

    def test_mod_with_variables(self):
        item = Item(title="test")
        item.set_cmd_mod(arg="meeting", variables={"calendar": "default"})
        assert item._mods["cmd"]["variables"] == {"calendar": "default"}

    def test_mod_without_variables_omits_key(self):
        item = Item(title="test")
        item.set_cmd_mod(arg="foo")
        assert "variables" not in item._mods["cmd"]

    def test_chaining(self):
        item = Item(title="test")
        result = (
            item.set_cmd_mod(arg="a", variables={"calendar": "default"})
            .set_alt_mod(arg="b", variables={"calendar": "other"})
            .set_ctrl_mod(arg="c")
            .set_shift_mod(arg="d")
        )
        assert result is item
        assert len(item._mods) == 4

    def test_serialized_includes_mods(self):
        item = Item(title="test")
        item.set_cmd_mod(arg="meeting", subtitle="Create meeting", variables={"calendar": "default"})
        serialized = item.serialized
        assert serialized["mods"]["cmd"]["arg"] == "meeting"
        assert serialized["mods"]["cmd"]["variables"] == {"calendar": "default"}

    def test_valid_false(self):
        item = Item(title="test")
        item.set_ctrl_mod(arg="foo", valid=False)
        assert item._mods["ctrl"]["valid"] is False
