
import lxml.etree

class JabberXDataForm:

    def __init__(self, x_data_element):

        if not type(x_data_element) == lxml.etree._Element:
            raise TypeError("`element' must be lxml.etree.Element")

        self._build(x_data_element)

    def _build(self, x_data_element):
        return
