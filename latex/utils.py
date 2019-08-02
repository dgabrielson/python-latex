#######################
from __future__ import print_function, unicode_literals

#######################

def safe_text_specials(s):
    """
    Given a string ``s``, return a new string with any of the latex
    special characters escaped.
    """
    special_map = (
        ('\\',  '\\textbackslash '), 
        ('&', '\\&'),
        ('%', '\\%'),
        ('$', '\\$'),
        ('#', '\\#'),
        ('_', '\\_'),
        ('{', '\\{'),
        ('}', '\\}'),
        ('~', '\\textasciitilde '),
        ('^', '\\textasciicircum '),
        )
    for src, dst in special_map:
        s = s.replace(src, dst)
    return s


def latex_fixes(text):
    result = text
    # this is not really py2 helpful anymore...
    if not isinstance(result, str):
        result = "{}".format(result)
    result = result.replace(u'&#39;', u"'")
    result = result.replace(u'. ', u'.\\ ')
    return result
