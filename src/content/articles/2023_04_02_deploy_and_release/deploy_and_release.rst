Good software practices: Software deployment and feature releases
########################################################################

:slug: good-software-practices-software-deployment-and-feature-releases
:category: Articles
:tags: good practices, software, deployment, release
:date: 2023-04-03 21:52
:status: published
:summary: "Big Bang" software releases are hard on end users and developers.
          What can we do about it?


*Software release* is the process of making a new version of software available to users. Think of an application or a library uploaded to a registry, where it can be downloaded by end-users.

Once software is released, it can be deployed to the target device or platform. Installing a mobile app from the App Store is a deployment. Publishing a front-end application package on a CDN is also a deployment.

A *feature release* is the process of making new functionality of software available to users.

The problem
===========

Companies are notorious for delivering new features through "Big Bang" releases, which often means users are not involved in the development process and do not see the new functionality until it is fully completed. This approach can result in half-baked or even unnecessary features being released.

The process of Big Bang feature development is also problematic. A developer spends weeks or months working on a feature, writes the code in a separate version control branch, and does not merge it back into the mainline until it is finished. When the developer finally attempts to integrate the feature into the mainline, they often face numerous issues. Since no one else on the team is familiar with the feature's internals, the developer must be responsible for fixing all the related bugs.

A good practice
===============

Develop the feature in short-lived version control system branches and continuously merge them into the mainline. By doing so, the feature code becomes a part of every software release. To prevent issues, guard the feature code using a feature flag and keep it in a "dormant" state.

Once the feature is viable enough, it can be enabled for a small set of users who are eager to test the latest and greatest of your software, even if some functionalities are still under development. This way, you can receive feedback and iron out any issues before releasing the feature to a wider audience. Once the feature is ready, it can be delivered to all users simply by flipping the feature flag.

.. image:: {static}feature-deployments.svg
   :width: 100%
   :alt: Avoiding "Big Bangs" with gradual feature release.
   :align: left


This approach helps to avoid the risks associated with a Big Bang release. By testing the code on a smaller audience beforehand, you can release with more confidence and face fewer surprises, bugs, and defects when the feature goes live.
