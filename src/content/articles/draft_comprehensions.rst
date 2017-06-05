Approaching Python comprehensions with an open mind
###################################################

:status: draft
:date: 2017-04-27 21:00
:tags: comprehensions, programming, python,
:category: Articles
:slug: python-comprehensions-with-open-mind
:summary:

This article emerged from a talk with my new colleague, who came
to the world of Python from Java, Kotlin and Scala background.
He was trying to perform a ``map`` and ``filter`` operations on
a list in a data-pipeline manner, something like:

.. code-block:: python

  new_lst = lst.filter(lambda i: i > 10).map(lambda i: i * 10)


"Sorry mate, you can't do that in Python" - was my answer.
"There are map and filter *functions* in Python and you can use them like:"

.. code-block:: python

  new_lst = map(lambda i: i * 10, filter(lambda i: i > 10, lst))


"However, that's not how things are done nowadays. Nowadays, we use
*comprehensions*, for example:"

.. code-block:: python

  new_lst = [i * 2 for i in lst if i > 10]

"But that looks awful!" - was the answer. "How can you read this?
You have to read it from inside out! Doesn't chained ``.filter().map()``
look more natural to you?" I did not have a ready answer.
Working with Python made reading comprehensions a natural process.
However we returned to the same conversation in a couple of weeks.

Data pipeline at first glance
-----------------------------

There is a function, which takes a Point and a Line geometry objects
and returns the closest point of the line to the given place.
The proposed solution written in Kotlin looked like:

.. code-block:: kotlin

  fun get_closest_point(place: Point, line: Line, tolerance: Int): Point? =
      get_line_coordinates(line)
          .map { Point(it) }
          .filter { place.distance(it) < tolerance }
          .minBy { place.distance(it) }

* First, a ``get_line_coordinates(line)`` is called, which returns
  as list of ``(x, y)`` coordinates.
* Then, each tuple is mapped to a Point object, i.e. the result would be a list
  (an iterator to be exact) of Points.
* Then, place's distance to each point is filtered against a given tolerance
  (i.e. no need to pick up points, which are too far away).
* Finally a point with minimal distance to place is returned.

How would you do a similar thing in Python?

A straight transformation may look like:

.. code-block:: python

  def get_closest_point(place, line, tolerance):
      points = (p for p in
                if place.distance(p) < tolerance)
      return min(points, lambda p: place.distance(p))

Which of these two would you prefer? Frankly speaking, I vote
for Kotlin code. Python code in its current form is rather hard to read.
Let's discuss its weak points and try to improve it.


Splitting comprehensions
------------------------

Reading nested comprehensions is hard because you have to do that inside-out.
So, the first thing in simplifying such comprehension, would be getting
rid of nesting:

.. code-block:: python

  def get_closest_point(place, line, tolerance):
      all_ponts = (Point(c) for c in get_line_coordinates(line))
      points = (p for p in all_points if place.distance(p) < tolerance)
      return min(points, lambda p: place.distance(p))

This time the code looks better, however there is still room to improve. 






i_gt_10 = (i for i in lst if i > 10)
new_lst = [i * 2 for i in i_gt_10]


.. code-block:: text

   '\n'.join(obj.name
       for obj in (
           repository.retrieve(id)
           for id in ids)
       if obj)

   Python vs. Ruby: A Battle to The Death
   https://vimeo.com/9471538

   Python is an experiment in how much freedom programmers need. Too much freedom and nobody can read another's code; too little and expressiveness is endangered.
   Guido van Rossum, 13 Aug 1996

   And what happens in more complex cases? Say, there are several filters?
   Or more mappings?". I . "We have to go deeper."

   http://stackoverflow.com/questions/890128/why-are-python-lambdas-useful
   https://softwareengineering.stackexchange.com/questions/99243/why-doesnt-python-allow-multi-line-lambdas

   U()

   l = [
       i
       for j in range(0, 10)
       if j == 3

       for i in range(j, 5)
       if i < 4
   ]

   print(l)


   all_points = Point(c) for c in self._get_line_coordinates(line)
   points = (p for p in all_points
             if geom.distance(p) < tolerance)
   closest = min(points, lambda p: geom.distance(p))

    fun _default_snap_to_vertices(geom: Geom, line: Line): Point? =
        _get_line_coordinates(line)
            .map { Point(it) }
            .filter { geom.distance(it) < opts.get("tolerance") }
            .minBy { geom.distance(it) }
