"""javascript code to be embedded in the html output

TODO: use importlib https://importlib-resources.readthedocs.io/en/latest/using.html
"""
import os

pkg_dir = os.path.dirname(__file__)

common_js_filepath = os.path.join(pkg_dir, "js", "common.js")
submit_js_filepath = os.path.join(pkg_dir, "js", "submission.js")
append_js_filepath = os.path.join(pkg_dir, "js", "append.js")
collapse_js_filepath = os.path.join(pkg_dir, "js", "collapsible.js")

common_funcs="""
<script type="text/javascript">
{file_contents}
</script>
""".format(file_contents=open(common_js_filepath, mode="r").read())

form_submission_script="""
<script type="text/javascript">
{file_contents}
</script>
""".format(file_contents=open(submit_js_filepath, mode="r").read())


form_appendable_script="""
<script type="text/javascript">
{file_contents}
</script>
""".format(file_contents=open(append_js_filepath, mode="r").read())


collapsible_elements_script="""
<script type="text/javascript">
{file_contents}
</script>
""".format(file_contents=open(collapse_js_filepath, mode="r").read())
