#!/usr/bin/env python3
import sys
import inspect
import pydoc
from pydoc import getdoc, visiblename, isdata


def _get_classes(object, all_=None):
    for key, value in inspect.getmembers(object, inspect.isclass):
        # if __all__ exists, believe it.  Otherwise use old heuristic.
        if (all_ is not None or (inspect.getmodule(value) or object) is object):
            if visiblename(key, all_, object):
                yield (key, value)

def _get_funcs(object, all_=None):
    for key, value in inspect.getmembers(object, inspect.isroutine):
        # if __all__ exists, believe it.  Otherwise use old heuristic.
        if (all_ is not None or inspect.isbuiltin(value) or inspect.getmodule(value) is object):
            if visiblename(key, all_, object):
                yield (key, value)

def _get_data(object, all_=None):
    for key, value in inspect.getmembers(object, isdata):
        if visiblename(key, all_, object):
            yield (key, value)



class StubDoc(pydoc._PlainTextDoc):
    def section(self, title, contents):
        """Format a section with a given heading."""
        clean_contents = contents.rstrip()
        return title + '\n' + clean_contents + '\n\n'

    def docmodule(self, object, name=None, mod=None):
        result = ''
        docstring = pydoc.getdoc(object)
        all_ = getattr(object, '__all__', None)

        if docstring:
            result += f'"""\n{docstring}\n"""\n\n'

        #######

        classes = list(_get_classes(object, all_=all_))
        funcs = list(_get_funcs(object, all_=all_))
        data = list(_get_data(object, all_=all_))

        if data:
            contents = []
            for key, value in data:
                contents.append(self.docother(value, key, name, maxlen=70))
            result = result + self.section('\n## DATA ##\n', '\n'.join(contents))

        if classes:
            # classlist = [value for key, value in classes]
            contents = [] #self.formattree(inspect.getclasstree(classlist, 1), name)]
            for key, value in classes:
                contents.append(self.document(value, key, name))
            result = result + self.section('\n## CLASSES ##\n', '\n'.join(contents))

        if funcs:
            contents = []
            for key, value in funcs:
                contents.append(self.document(value, key, name))
            result = result + self.section('\n## FUNCTIONS ##\n', '\n'.join(contents))

        if hasattr(object, '__version__'):
            version = str(object.__version__)
            if version[:11] == '$' + 'Revision: ' and version[-1:] == '$':
                version = version[11:-1].strip()
            result = result + self.section('## VERSION ## ', version)
        if hasattr(object, '__date__'):
            result = result + self.section('## DATE ## ', str(object.__date__))
        if hasattr(object, '__author__'):
            result = result + self.section('## AUTHOR ##', str(object.__author__))
        if hasattr(object, '__credits__'):
            result = result + self.section('## CREDITS ##', str(object.__credits__))
        return result

    # def docmodule(self, *args, **kwargs):
    #     import ipdb; ipdb.set_trace()
    #     return super(__class__, self).docmodule(*args, **kwargs)


def get_stubfile(target) -> str:
    return pydoc.render_doc(
        target,
        title='#!/usr/bin/env python  # [%s]',
        renderer=StubDoc(),
    )


if __name__ == '__main__':
    # import ipdb; ipdb.set_trace()
    target = sys.argv[1]
    print(get_stubfile(target))
