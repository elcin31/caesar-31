"""Localize Pandoc's generated EPUB labels without touching book prose.

Pandoc 3.1.11.1 leaves English landmarks even with lang=ru-RU. Work on XML
nodes in generated navigation documents only; cited titles remain untouched.
"""
from pathlib import Path
import os
import zipfile
from xml.dom import minidom

XHTML = 'http://www.w3.org/1999/xhtml'
EPUB = 'http://www.idpf.org/2007/ops'
OPF = 'http://www.idpf.org/2007/opf'
NCX = 'http://www.daisy.org/z3986/2005/ncx/'
XML = 'http://www.w3.org/XML/1998/namespace'
LABELS = {'titlepage': 'Титульный лист', 'cover': 'Обложка', 'toc': 'Содержание'}
PAGE_LABELS = {'nav.xhtml': LABELS['toc'], 'cover.xhtml': LABELS['cover'],
               'title_page.xhtml': LABELS['titlepage']}


def set_text(node, value):
    while node.firstChild:
        node.removeChild(node.firstChild)
    node.appendChild(node.ownerDocument.createTextNode(value))


def localize_epub(path: Path):
    changes = []
    temporary = path.with_suffix('.epub.localized')
    with zipfile.ZipFile(path) as original, zipfile.ZipFile(temporary, 'w') as localized:
        for info in original.infolist():
            data = original.read(info.filename)
            if info.filename.endswith(('.xhtml', '.opf', '.ncx')):
                doc = minidom.parseString(data)
                modified = False
                if info.filename.endswith('.xhtml'):
                    html = doc.documentElement
                    html.setAttribute('lang', 'ru-RU')
                    html.setAttributeNS(XML, 'xml:lang', 'ru-RU')
                    modified = True
                    generated_name = info.filename.rsplit('/', 1)[-1]
                    title = PAGE_LABELS.get(generated_name)
                    if title:
                        for node in doc.getElementsByTagNameNS(XHTML, 'title'):
                            set_text(node, title)
                    if generated_name == 'nav.xhtml':
                        for node in doc.getElementsByTagNameNS(XHTML, 'nav'):
                            kind = node.getAttributeNS(EPUB, 'type')
                            # EPUBCheck's navigation schema rejects aria-label here.
                            # The standard title attribute supplies the Russian label.
                            node.setAttribute('title', 'Содержание' if kind == 'toc' else 'Навигация')
                        for node in doc.getElementsByTagNameNS(XHTML, 'a'):
                            label = LABELS.get(node.getAttributeNS(EPUB, 'type'))
                            if label:
                                set_text(node, label)
                                changes.append({'file': info.filename, 'label': label})
                        for node in doc.getElementsByTagNameNS(XHTML, 'h1'):
                            if node.getAttribute('id') == 'toc-title':
                                set_text(node, 'Содержание')
                elif info.filename.endswith('.opf'):
                    for node in doc.getElementsByTagNameNS(OPF, 'reference'):
                        label = LABELS.get(node.getAttribute('type'))
                        if label:
                            node.setAttribute('title', label)
                            changes.append({'file': info.filename, 'label': label})
                            modified = True
                elif info.filename.endswith('.ncx'):
                    for node in doc.getElementsByTagNameNS(NCX, 'navPoint'):
                        contents = node.getElementsByTagNameNS(NCX, 'content')
                        target = contents[0].getAttribute('src').split('#')[0].rsplit('/', 1)[-1] if contents else ''
                        title = PAGE_LABELS.get(target)
                        if title:
                            labels = node.getElementsByTagNameNS(NCX, 'navLabel')
                            for label in labels[:1]:
                                for text_node in label.getElementsByTagNameNS(NCX, 'text'):
                                    set_text(text_node, title)
                                    modified = True
                if modified:
                    data = doc.toxml(encoding='utf-8') + b'\n'
            # Preserve the first, uncompressed mimetype and every resource byte.
            localized.writestr(info, data)
    os.replace(temporary, path)
    return changes
