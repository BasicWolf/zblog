Thoughts about XML structure: elements vs. attributes
=====================================================

:slug: thoughts_on_xml_structure
:categories: Articles
:tags: programming, XML
:date: 2013-05-18 12:00

:summary: Exploring XML elements versus attributes.

XML defines no rules about using elements or attributes in paricular case. For example:

.. code-block:: xml

  <user firstname="Alex" lastname="Black"/>

is as valid as

.. code-block:: xml

  <user>
    <firstname>Alex</firstname>
    <lastname>Black</lastname>
 </user>

Are there any general guidelines on when attributes or elements should be used?
Let's explore various cases to find out the best solution of the problem.


Consider the example above. Should one use the attributes or elements
in this case? Unless you care about the size of the data, it doesn't matter
at all!
And that is true for this particular case without a context.
We have no knowledge about how the ``<user>`` data is **processed**.


Processing matters
------------------

XML is meant to be both human and machine readable. Would you agree that
"machine readable" matters more, because every day machines automatically
process tons of XML data?

For example, the first steps of processing XHTML [1]_ may look like:

.. code-block:: none

   |----------|   |------------|   |-----------------|
   | XML data |-->| XML parser |-->| XHTML processor |--> ...
   |----------|   |------------|   |-----------------|


Note, that the *XML parser* knows nothing about the data except that
it is XML. It doesn't care whether the data is described via the
elements or attributes. In fact, the XML parser is able to parse any
data, whether it is an XHTML document, RSS channell, OpenDocument container
and so on.
The XML parser transforms the input data into objects in memory which are
passed to the *XHTML processor* which contains the logic of dealing
with these objects.

XML data
--------

Consider an ordered list which starts with a "100" bullet:

.. code-block:: html

   <ol start="100">
     <li>Coffee</li>
     <li>Milk</li>
   </ol>

The XHTML processor, knows that the ``<ol>`` tag represents an ordered
list, and the nested ``<li>`` tags are the list elements with the data.
The processor also expects that the ``<ol>`` tag data may contain specific
attribute which describe the list, e.g. ``"start"``
Note, that changing the value of the ``start`` attribute does not interfere
with the data (the list items).

Now, let's create an unordered list:

.. code-block:: html

   <ul>
     <li>Tee</li>
     <li>Soda</li>
   </ul>

The XHTML processor will also parse this data as a list, because it is
*aware* of the ``<ul>`` tag and its contents.
The HTML standard has the third ``<dt>`` [2]_ tag which describes a definision
list.

Let's think of an interesting design task: how would you design an XML
format which stores any kind of lists unknown to the processor module?

.. code-block:: none

   |----------|   |------------|   |----------------|
   | XML data |-->| XML parser |-->| Our  processor |--> ...
   |----------|   |------------|   |----------------|


And that is where attributes can be very useful:

.. code-block:: xml

  <users type="list" item="user">
    <user>
      <name>Alex</name>
      <lastname>Black</lastname>
    </user>

    <user>
      <name>John</name>
      <name>Brown</name>
    </user>
  </users>

The processor is not aware of the ``<users>`` tag. But it knows that if
an element contains the ``type="list"`` attribute (and value), then the
``item`` attribute would describe the list items to look for. What if
we wanted to make a list with multiple selected items? The attributes can
handle this situation as well:

.. code-block:: xml

  <users type="list" item="user">
    <user selected="true">
      <name>Alex</name>
      <lastname>Black</lastname>
    </user>

    <user>...</user>
    <user selected="true">...</user>
    <user>...</user>
  </users>


Attributes as metadata
----------------------

Metadata is a data which describes some other data. In all the examples
above, the attributes contained the metadata information. Removing the
``type="list"`` and ``item="user"`` attributes from the ``<users>`` tag
will affect the way how the data is processed, but the original data
is intact.

In my opinion the attributes are perfect for metadata, and a person
designing an XML document format should simply take the discussion of
"Attributes vs. elements" to the "Data and metadata" level.

Eager to hear your comments!

Footnotes
---------

.. [1] HTML is not a subset of XML, while XHTML is.
.. [2] http://www.w3schools.com/html/html_lists.asp
