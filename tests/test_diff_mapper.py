from backend.utils.diff_mapper import diff_mapper


def test_extract_changed_lines():

    patch = """
@@ -10,2 +10,4 @@
 line1
+new line
+another new line
 line2
"""

    lines = diff_mapper.extract_changed_lines(
        patch
    )

    assert lines == [11, 12]


def test_empty_patch():

    assert (
        diff_mapper.extract_changed_lines("")
        == []
    )