The "Handover" teams
####################

:slug: handover-teams
:category: Articles
:tags: software development, teams, good practices, programming, handover, mob programming
:date: 2025-11-08 18:15
:status: published
:summary:
   Are you about to adopt a product via a "handover session"?
   Perhaps you want to delay that moment and reconsider your options.

   .. figure:: {static}img/handover-session.webp
      :align: center
      :width: 100%
      :alt: A short handover session between teams
      :target: {filename}handover-teams.rst

      Good luck to the Blue team!


Do you know what my favourite corporate sin is when it comes to code bases?
It's a **handover** from one team to another.
"But wait, Zaur, there are legitimate reasons for handovers!"
Of course there are.
Organisations are evolving structures, and sooner or later quite a few parts
attached to one of the limbs will be cut off and stitched to the other.
The code bases follow.

We can't avoid handovers, and it's our job - as the source team,
and more importantly, as the receiving team to make a code handover
as smooth as possible.
But the process is so often compressed into a half-day "handover session",
after which the source team wishes all the luck in the world to the new
owners and blasts off to their new adventures.

.. figure:: {static}img/handover-session.svg
   :align: center
   :width: 100%
   :alt: A short handover session between teams
   :target: {static}img/handover-session.svg

   Good luck to the Blue team!

Do you truly own the code at this point?
You can own the code on paper, but you truly own the code only when you know
it inside out, can picture data flows with your eyes closed, understand
the architecture, and have lived the decisions made along the way.
Your code is part of you - your experience, your knowledge, your skills,
your vision.
Simply put, you have to get intimate with the code to own it.

You see where I'm going with this - no amount of "handover" will make you
the true owner of the code, at least not immediately.
You'll get there eventually, with time and
the hundreds and thousands of lines added and removed by you.
To smoothen the transition period, you'll need help from the source team.

Working together
----------------

What if, instead of having a handover session, you had a handover period
in which both teams form a single virtual team and work together?
And by working together I mean **mob/ensemble programming** sessions, in which
knowledge gets shared and slowly transferred from one team to another.
You write new code, fix bugs, do maintenance and refactoring, release and monitor
- all with the specialists from the source team.
If the teams are not physically co-located, try to get together
and work together for a few days - this will create a strong bond between you.

.. figure:: {static}img/handover-period.svg
   :align: center
   :width: 100%
   :alt: A short handover session between teams
   :target: {static}img/handover-period.svg

   Blue team truly owns the product
   after working together with the orange team.

I was there, Gandalf
--------------------

I've been through different handovers, some lasted hours, others months.
The first left me with a feeling of emptiness, dissatisfaction and anger:
"How anyone in their right mind expect me to maintain and work on this code?".
The latter were quite the opposite - after weeks of hands-on experience with
the product and its code base,
our team had a solid "know-how" foundation under our feet,
and we were eager to take over and drive it further.

Why did I accept the first one? Because I was young and green.
I accepted business needs as challenges, and threw myself into the fire with
no hesitation (Am I not a professional?).
I never considered the long-term consequences.
Then they hit. Business demanded new features,
but I couldn't deliver because I didn't truly own the code.

Lessons learned.Today I thoroughly explain to the business all the risks
associated with rushed handovers. Instead, we design a migration plan -
together with the business, the old team, and the new teams.
Then we work together: fix bugs, deliver new features, make experiments and
monitor them in production.
When migration period is over, we are the true new owners of the code base.
