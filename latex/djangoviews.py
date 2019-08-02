"""
Useful with Django>=1.3
"""
import os

import django
from django.conf import settings
from django.contrib.staticfiles.finders import find as staticfiles_finder
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .latex_document import LaTeX_Document
from .utils import latex_fixes


class LaTeXResponseMixin(object):
    """
    For delivering the response -- compiling to PDF etc.
    NOTE: there is currently *no way* to deal with compilation errors.
    """
    as_attachment = True    # send filename and content-disposition headers
    extra_assets = None     # provide a list, if there are any.
    as_source = False
    allow_source_from_get = True
    allow_source_from_post = True
    filename = None         
    
    
    def get_as_attachment(self):
        """Allow for conditional overrides, if required"""
        return self.as_attachment


    def fix_filename_extension(self, filename):
        basename, extension = os.path.splitext(filename)
        if extension.lower() not in ['', '.tex', '.pdf']:
            extension = ''
        if self.get_as_source() and extension.lower() == '.pdf':
            base = os.path.splitext(filename)[0]
            extension = '.tex'
        if not extension:
            if self.get_as_source():
                extension = '.tex'
            else:
                extension = '.pdf'
        return basename + extension
        
        
        
    def get_filename(self, latex_doc=None):
        """Allow for conditional overrides, if required.
        If you define this function, it should pass a base filename
        to the method ``self.fix_filename_extension(filename)``
        to determine the actually file name with extension.
        """
        if not self.filename:
            if latex_doc is None:
                filename = 'file'
            else:
                filename = latex_doc.filename
        else:
            filename = self.filename
        return self.fix_filename_extension(filename)

         

    def _augment_response(self, response, filename):
        """
        Augment the response object with extra headers, e.g., 
        * Filename
        * Content-Disposition
        """
        response['Filename'] = filename  # IE needs this
        if self.get_as_attachment():
            attachment = 'attachment; '
        else:
            attachment = ''
        response['Content-Disposition'] = '{0}filename={1}'.format(attachment, 
                                                                   filename)

        
    def get_as_source(self):
        """
        Returns the flag for whether or not the LaTeX source should be returned.
        This is controllable via the as_source, allow_source_from_{get,post}
        values.
        """
        if self.as_source:
            return True
        if self.allow_source_from_get and self.request.GET.get('src', False):
            return True
        if self.allow_source_from_post and self.request.POST.get('src', False):
            return True
        return False
        
        
    def complete_static_filename(self, filename):
        """
        This hook resolves static assets provided as extra assets
        to absolute filenames.  This will probably break for any
        kind of non-local storage.
        """
        return staticfiles_finder(filename)
        
        
    def get_extra_assets(self):
        """
        Be very careful.  Extra assets must be absolute filenames
        for views.  By default, extra_assets are assumed to be provided
        as static assets.  Make sure you run ./manage.py collectstatic.
        
        This function *must* always return a list (which can be empty).
        """
        asset_list = []
        if self.extra_assets is None:
            return []
        return [ self.complete_static_filename(asset) \
                    for asset in self.extra_assets ]


    def render_to_response(self, context, **response_kwargs):
        response = TemplateResponse(request=self.request,
                                    template=self.get_template_names(),
                                    context=context,
                                    content_type='application/x-latex',
                                    **response_kwargs)

        if not self.get_as_source():
            doc = LaTeX_Document()
            doc.source = latex_fixes(response.rendered_content)
            extra_assets = self.get_extra_assets()
            doc.compile(extra_assets=extra_assets)
            data = doc.output
            if doc.filename is None:
                debug = getattr(settings, 'DEBUG', False)
                content = "<html><head></head><body></body><h1>500 Server Error</h1><h2>Failed to generate PDF</h2>\n\n%s</body></html>"
                if debug:
                    content = content % ('<pre>%s</pre>' % doc.log)
                else:
                    content = content % ''
                return HttpResponseServerError(content)
            response = HttpResponse(data, content_type='application/pdf')
        else:
            doc = None
            
        filename = self.get_filename(doc)            
        self._augment_response(response, filename)
        return response


class LaTeXDetailView(LaTeXResponseMixin, DetailView):
    """
    For rendering a single object via LaTeX template to PDF and
    delivering the PDF.
    """

LaTeX_DetailView = LaTeXDetailView



class LaTeXListView(LaTeXResponseMixin, ListView):
    """
    For rendering a list of objects via LaTeX templates to PDF
    and delivering the PDF.
    """

LaTeX_ListView = LaTeXListView
