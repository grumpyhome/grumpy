#!/usr/bin/env python3
import sys
import re
import inspect
import pydoc
from pydoc import (getdoc, visiblename, isdata, classname, _is_bound_method,
                   classify_class_attrs, _split_list, builtins, sort_attributes)
from collections import deque


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
    # Extending from code in `pydoc.py` of Python 3.6.5

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

    def docclass(self, object, name=None, mod=None, *ignored):
        """Produce text documentation for a given class object."""
        realname = object.__name__
        name = name or realname
        bases = object.__bases__

        def makename(c, m=object.__module__):
            return classname(c, m)

        if name == realname:
            title = 'class ' + self.bold(realname)
        else:
            title = self.bold(name) + ' = class ' + realname
        if bases:
            parents = map(makename, bases)
            title = title + '(%s)' % ', '.join(parents)

        contents = []
        push = contents.append

        doc = getdoc(object)
        if doc:
            push(f'"""\n{doc}\n"""')

        # List the mro, if non-trivial.
        mro = deque(inspect.getmro(object))
        if len(mro) > 2:
            push("\n## Method resolution order:")
            for i, base in enumerate(mro, 1):
                push(f'# {i}) ' + makename(base))
            push('')

        # Cute little class to pump out a horizontal rule between sections.
        class HorizontalRule:
            def __init__(self):
                self.needone = 0
            def maybe(self):
                if self.needone:
                    push('# ' + '-' * 68)
                self.needone = 1
        hr = HorizontalRule()

        def spill(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            if ok:
                hr.maybe()
                push('# ' + msg)
                for name, kind, homecls, value in ok:
                    try:
                        value = getattr(object, name)
                    except Exception:
                        # Some descriptors may meet a failure in their __get__.
                        # (bug #1785)
                        push(self._docdescriptor(name, value, mod))
                    else:
                        push(self.document(value, name, mod, object))
            return attrs

        def spilldescriptors(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            if ok:
                hr.maybe()
                push('# ' + msg)
                for name, kind, homecls, value in ok:
                    push(self._docdescriptor(name, value, mod))
            return attrs

        def spilldata(msg, attrs, predicate):
            ok, attrs = _split_list(attrs, predicate)
            if ok:
                hr.maybe()
                push('# ' + msg)
                for name, kind, homecls, value in ok:
                    if callable(value) or inspect.isdatadescriptor(value):
                        doc = getdoc(value)
                    else:
                        doc = None
                    try:
                        obj = getattr(object, name)
                    except AttributeError:
                        obj = homecls.__dict__[name]
                    push(self.docother(obj, name, mod, maxlen=70, doc=doc) +
                         '\n')
            return attrs

        attrs = [(name, kind, cls, value)
                 for name, kind, cls, value in inspect.classify_class_attrs(object)
                 if visiblename(name, obj=object)]

        while attrs:
            if mro:
                thisclass = mro.popleft()
            else:
                thisclass = attrs[0][2]
            attrs, inherited = _split_list(attrs, lambda t: t[2] is thisclass)

            if thisclass is builtins.object:
                attrs = inherited
                continue
            elif thisclass is object:
                tag = "defined here"
            else:
                tag = "inherited from %s" % classname(thisclass,
                                                      object.__module__)

            sort_attributes(attrs, object)

            # Pump out the attrs, segregated by kind.
            attrs = spill("Methods %s:\n" % tag, attrs,
                          lambda t: t[1] == 'method')
            attrs = spill("Class methods %s:\n" % tag, attrs,
                          lambda t: t[1] == 'class method')
            attrs = spill("Static methods %s:\n" % tag, attrs,
                          lambda t: t[1] == 'static method')
            attrs = spilldescriptors("Data descriptors %s:\n" % tag, attrs,
                                     lambda t: t[1] == 'data descriptor')
            attrs = spilldata("Data and other attributes %s:\n" % tag, attrs,
                              lambda t: t[1] == 'data')

            assert attrs == []
            attrs = inherited

        contents = '\n'.join(contents) or 'pass'
        return '\n' + title + '\n' + self.indent(contents.rstrip(), '    ') + '\n'

    def docroutine(self, object, name=None, mod=None, cl=None):
        """Produce text documentation for a function or method object."""
        realname = object.__name__
        name = name or realname
        note = ''
        skipdocs = 0
        if _is_bound_method(object):
            imclass = object.__self__.__class__
            if cl:
                if imclass is not cl:
                    note = ' from ' + classname(imclass, mod)
            else:
                if object.__self__ is not None:
                    note = ' method of %s instance' % classname(
                        object.__self__.__class__, mod)
                else:
                    note = ' unbound %s method' % classname(imclass,mod)

        if name == realname:
            title = self.bold(realname)
        else:
            if (cl and realname in cl.__dict__ and
                cl.__dict__[realname] is object):
                skipdocs = 1
            title = self.bold(name) + ' = ' + realname
        argspec = None

        if inspect.isroutine(object):
            try:
                signature = inspect.signature(object)
            except (ValueError, TypeError):
                signature = None
            if signature:
                argspec = str(signature)
                argspec = re.sub(', /\)', ')', argspec)
                argspec = re.sub(', /', '', argspec)
                if realname == '<lambda>':
                    title = self.bold(name) + ' lambda '
                    # XXX lambda's won't usually have func_annotations['return']
                    # since the syntax doesn't support but it is possible.
                    # So removing parentheses isn't truly safe.
                    argspec = argspec[1:-1] # remove parentheses
        if not argspec:
            argspec = '(...)'
        decl = 'def ' + title + argspec + note + ':'

        impl = 'raise NotImplementedError()'
        if skipdocs:
            return decl + '\n' + self.indent(impl) + '\n'
        else:
            doc = getdoc(object) or ''
            if doc:
                doc = f'"""\n{doc}\n"""'
            return decl + '\n' + self.indent(((doc + '\n') if doc else '') + impl).rstrip() + '\n'


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
