Teams Topologies - Book Review
##############################

:slug: teams-topologies-book-review
:category: Books
:tags: book, review, architecture, teams, software development,
:date: 2024-03-23 21:42
:summary: .. image:: {static}teams-topologies-cover.webp
             :width: 30%
             :align: center
             :alt: "Teams Topologies book cover"
             :target: {filename}teams-topologies.rst

          Conway’s Law states that systems are designed to mirror the communication
          structures of the organizations that create them. How, then, can we
          shape an organization to produce the desired system design? Let's
          find out "Team Topologies: Organizing Business and Technology Teams
          for Fast Flow" by Matthew Skelton and Manuel Pais.

Are you familiar with the exiting feeling of making a discovery?
Butterflies in your stomach, intermittent breathing, galvanized palms?
Every chapter draws a "*WOW!*", every page turns into a vivid picture
in your imagination.
That is "Team Topologies" -  a book about systems architecture.
This may come as a surprise, since the title clearly states otherwise.
It's also a book about teams interactions and organizational design.

.. image:: {static}teams-topologies-cover.webp
   :width: 50%
   :align: center
   :alt: "Teams Topologies book cover"

Part I - *Teams As the Means of Delivery*.
Matthew Skelton and Manuel Pais dedicate the early
chapters of the book to show how organizational structure affects
the system design. This effect is nowadays known as "Conway's law",
which originates from Mel Conway's 1968 paper "How Do Committees Invent":

..

  Organizations which design systems ... are constrained to produce designs
  which are copies of the communication structures of these organizations.

It is a scary discovery. It means that organizational structure prevails
over system architecture, unless the structure is made to support the
desired architecture. If the former and the latter are in conflict, one
of them has to change. Which one? If the desired architecture is the target,
there isn't much to change about it. This leaves us with the organizational
structure.

But before diving into the structure, the organization needs to have team-first
mindset. In the book, a team is a stable group of five to nine people who
work toward a shared goal as a unit. The team is the smallest entity of delivery
within the organization. An organization should never assign work to individuals;
only to teams.

How can an organization improve team performance?
The team should be long-lived and stable, of relatively small size (as stated above).
The team should own the software while being able to limit its cognitive load.
The organization should reward the team, not individuals.
Last but not the least: the team members should develop a team-first mindset,
prioritizing team goals and all required activities that help achieve these goals.

----

..

  Organizations must design teams intentionally by asking these questions:
  Given our skills, constraints, cultural and engineering maturity, desired
  software architecture, and business goals, which team topology will help
  us deliver results faster and safer? How can we reduce or avoid handovers
  between teams in the main flow of change? Where should the boundaries be
  in the software system in order to preserve system viability and encourage
  rapid flow? How can our teams align to that?

The answers to these questions are found in
Part II - *Team Topologies that Work for Flow*.

The authors start by examining team anti-patterns, such as
frequently shuffling team members and ad-hoc or reactive
team design. A team that has grown too large may be split without clear
boundaries. A dedicated DBA team might be created after a software crash
in production due to poor database handling. These situation certainly
require action, but "the most natural solution" might slow down delivery and
weaken the autonomy of teams.

..

  In order to be as effective as possible, we need to consciously design
  our teams rather than merely allow them to form accidentally or haphazardly.
  We call these consciously designed team structures **team topologies**,
  a term that acknowledges that teams should be deliberately “placed”
  into organizations while also referring to the boundary of responsibility
  of each team.

A high-performing team takes responsibility and the ownership of the features
they develop - from design all the way to production. Here, *production* means
monitoring feature usage and performance, rather than handing it over to an Ops team.
Such a team is cross-functional and equipped with all necessary skills
to design, develop, test, deploy and monitor application usage and performance.
To maintain a rapid flow, the team remains autonomous, ideally utilizing non-blocking
external dependencies in the form of self-services developed and maintained
by other teams.

.. image:: {static}feedback-from-production.png
   :width: 100%
   :align: center
   :alt: "Feedback from production to different development stages maintained by the same team"
   :target: {static}feedback-from-production.svg

----

..

  Perfection is achieved, not when there is nothing more to add, but
  when there is nothing left to take away.

  -- Antoine de Saint-Exupéry, Airman's Odyssey


Skelton and Pais reduce the number of team variations to four fundamental
team topologies:

* *Stream-aligned team*
* *Enabling team*
* *Complicated-subsystem team*
* *Platform team*

The authors argue that these are the only topologies
necessary to build and run modern software systems. Limiting to these
four team types acts as a powerful template for effective organization design,
especially when combined with well-defined software boundaries and efficient
team interactions.

The **strteam-aligned** team is the primary team type in an organization, and
the purpose of the other fundamental team topologies. A *stream* represents the
continuous flow of work aligned to a business domain or organizational
capability. The team is empowered to build and deliver customer or user
value as quickly, safely, and independently as possible.

The **enabling team** assists stream-aligned teams in acquiring necessary skills
and knowledge, setting up pipelines, adopting tools and solving engineering problems
in unfamiliar environments. Enabling teams have a strongly collaborative nature;
they thrive to understand the problems and shortcomings of stream-aligned
teams in order to provide effective guidance.

A **complicated-subsystem** team is responsible for building and maintaining
a part of the system that relies heavily on specialized knowledge.
This is to such an extent that most team members must be specialists in that particular
area to understand and maintain the subsystem effectively.
Examples of complicated subsystems might include a mathematical model,
a mainframe module, a voice recognition algorithm, and so on.

The purpose of the **platform team** is to enable stream-aligned team to deliver
their work autonomously. It provides internal services to reduce the cognitive
load that would otherwise be required from stream-aligned teams to develop these underlying
services. Examples of these services include: continuous integration (CI),
code registries, repository hosting, databases, deployment, monitoring,
logging aggregation and so on.

Based on reports from successful organizations, the ratio of stream-aligned teams
to other types of teams should be between approximately 6:1 and 9:1.

How should stream-aligned teams divide responsibilities?
The authors advice breaking down the system, so that the resulting parts
can evolve as independently as possible. Consequently, teams assigned to these
parts will experience greater autonomy and ownership over them.

It is also essential to consider the teams dynamics when splitting a monolith.
Splitting a monolithic application into autonomous services that need
to be released and deployed together is merely creating a
"distributed monolith" with tightly coupled pieces.
Microservices sharing a database, monolithic world models with similar domain
language and representation across different formats, or even a single office
layout for all the teams, can all contribute to a distributed monolith.

----

Now that the reader is familiar with the four fundamental team topologies,
Skelton and Pais discuss how teams interact and when to change the teams
and their interactions. Well-defined interactions are key to effective
teams, and the authors outline three essential ways teams can and should interact:

* **Collaboration: working closely together with another team**.
  Imagine two or more teams coming together to solve a problem that requires
  competences from all of them. Their collaboration is rapid; they quickly
  make discoveries and share knowledge, experiment and prototype solutions.
* **X-as-a-Service: consuming or providing something with minimal collaboration**.
  This interaction is ideal when a team needs to focus on its tasks and
  consume the necessary services - from CI/CD infrastructure to upstream
  production API services - without being involved in their development and
  maintenance.
* **Facilitating: helping (or being helped by) another team to clear impediments**.
  When a team lacks certain competences, a facilitating team can save the
  day by coaching and providing help. This is the main interaction mode for
  Enabling teams.

The last chapter of the book - **Evolve Team Structures with Organizational Sensing**.

As Frederic Brooks mentioned in "Mythical Man-Months":

..

  Conway goes on to point out that the organization chart
  will initially reflect the first system design, which is almost surely
  not the right one. If the system design is to be free to change, the
  organization must be prepared to change.

The software design must align with the way in which teams communicate;
otherwise, it is doomed to fail. The methods of communication evolve as
the system and the organization matures. What begins as collaboration eventually
becomes part of platform services with strict boundaries. Stream-aligned teams
seek help from Enabling teams when necessary or provide assistance to other teams
upon request.

----

I tried very hard to distill the essential ideas of the book into this small review
to get you interested in reading it. As you can imagine, there is so much more!
If you are ever involved in designing systems architecture that requires
the interaction of many teams, this book is a must-read.
