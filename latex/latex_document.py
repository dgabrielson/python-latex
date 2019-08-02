#!/usr/bin/env python
#######################
from __future__ import print_function, unicode_literals

import os
import re
import shutil
import sys
from glob import glob
from tempfile import NamedTemporaryFile

#######################




class LaTeX_Document:
    """
    LaTeX_Document(body_text,
        title=None,
        author=None,
        date=None,
        packages={},
        extra_preamble=None
        )

    Construct a compilable document.

    Useful methods:
        * compile()
        * render_src()  -- used to cast as str() or "{}".format()
        * preview()
        * pdf_data()
        * set_full_src(text)    -- set source code
    """
    def __init__(self, document_body=None, title=None, author=None, date=None,
                 packages={}, preamble_extras=None):
        self._title = title
        self._author = author
        self._date = date
        self._packages = packages
        self._preamble_extras = preamble_extras
        self._body = document_body

        self._src_file = None
        self._out_file = None
        self._compiled = False
        self._log = None
        self.full_src = None

    def documentclass(self):
        return u'\\documentclass[12pt,letterpaper]{article}\n'

    def packages(self):
        results = ''
        for package, options in self._packages.items():
            if options:
                results += u'\\usepackage[%s]{%s}\n' % (options, package)
            else:
                results += u'\\usepackage{%s}\n' % package
        return results

    def preamble(self):
        results = u''
        results += self.packages()
        if self._preamble_extras:
            results += self._preamble_extras
        return results

    def authortitle(self):
        results = u''
        if self._title:
            results += u'\\title{%s}\n' % self._title
        if self._author:
            results += u'\\author{%s}\n' % self._author
        if self._date:
            results += u'\\date{%s}\n' % self._date
        return results

    def render_src(self):
        if self.full_src is None:
            results = self.documentclass()
            results += self.preamble()
            results += self.authortitle()
            results += u'\\begin{document}\n'
            if self._author or self._title:
                results += u'\\maketitle\n'
            results += "{}".format(self._body)
            results += u'\n\\end{document}\n'
            self.full_src = results
        return self.full_src

    def set_full_src(self, text):
        self.full_src = text

    def __str__(self):
        if self.full_src is None:
            self.render_src()
        return self.full_src


#     def __unicode__(self):
#         if self.full_src is None:
#             self.render_src()
#         return self.full_src



    def compile(self, force=False, extra_assets=[]):
        if not force and self._compiled:
            return True
        self._src_file = NamedTemporaryFile(suffix=u'.tex')
        self._src_file.write(self.source.encode('utf-8', 'replace'))
        self._src_file.flush()
        cmd = u'pdflatex -interaction=nonstopmode "%s"' % self._src_file.name
        working_dir = os.path.split( self._src_file.name )[0]
        current_dir = os.getcwd()
        for filename in extra_assets:
            shutil.copy(filename, working_dir)
        os.chdir( working_dir )
        try:
            result = False
            output_rexp = re.compile(r'^Output written on (.*) \((\d+) pages?, (\d+) bytes\)')
            while True:
                rerun = False
                output_lines = os.popen(cmd, 'r').readlines()

                for line in output_lines:
                    # maybe lowercase? maybe no whitespace
                    if ' Rerun ' in line:
                        rerun = True

                    output = output_rexp.match(line)
                    if output is not None:
                        filename, pages, bytes = output.groups()
                        # note that pages and bytes are strings.
                        result = pages != '0'
                        self._out_file = os.path.join(working_dir, filename)
                self._log = ''.join(output_lines)
                if not rerun:
                    break
            return result
        finally:
            self._compiled = True
            os.chdir( current_dir)  # restore working folder


    def preview(self, application=None, wait=False):
        if not self._compiled:
            self.compile()
        cmd = u'open '
        if application is not None:
            cmd += '-a "%s" ' % application
        if wait:
            cmd += '-W '
        os.popen('%s "%s"' % (cmd, self._out_file))


    def pdf_data(self):
        """
        Returns the PDF datastream.
        """
        if not self._compiled:
            self.compile()
        if self._out_file is None or not os.path.exists(self._out_file):
            #print >> sys.stderr, 'WARNING: Output file %r does not exist' % self._out_file
            return None
        return open(self._out_file, 'rb').read()

    @property
    def filename(self):
        """
        Returns the *output* filename, without path
        """
        if self._out_file is None:
            return None
        return os.path.split(self._out_file)[-1]

    @property
    def source(self):
        """
        Return the current source
        """
        return "{}".format(self)

    @source.setter
    def source(self, value):
        self.full_src = value


    @property
    def output(self):
        return self.pdf_data()


    @property
    def log(self):
        return self._log


    def __del__(self):
        if self._src_file is not None:
            # assume all files with the same base name as the src have been
            # created by this process, and delete them.
            for fn in glob( os.path.splitext(self._src_file.name)[0] + u'.*' ):
                if not fn.endswith('.tex'):
                    os.remove( fn )
