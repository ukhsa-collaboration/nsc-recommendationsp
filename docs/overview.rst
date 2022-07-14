==================
Developer Overview
==================

This site is NOT a content management system for handing all the documents related to
the day-to-day functioning of the National Screening Committee (NSC); it is a publishing
tool to help describe recommendations of the NSC and to engage members of the public and
various interested parties when the policy for a given condition comes up for review.

Apps
====

In typical django fashion the site is divided into apps:

condition
  contains the views for the public-facing pages that describe a given condition, e.g.
  Atrial Fibrillation, what the NSC recommendation for screening is, etc. It also
  contains the views for submitting comments when the condition is being reviewed and
  the consultation period is open.  It does not contain any models, see policy as for
  why.

contact
  contains the views and model for managing the point of contacts at organisations.

document
  the files such as the external review, evidence review etc.  that are used during the
  review of a condition. Documents are available for download by the public and
  stakeholders so they can submit their comments when the consultation period of a
  review is open.

organisation
  contains the views and model for stakeholders - medical institutions, charities, etc.
  that are interested in a given condition and who participate in reviews.

policy
  contains the views and model that PHE staff used to edit the pages viewed by members
  of the public in the condition app.

review
  contains the views and model used by PHE staff to manage the review process, whether
  it is the documents that can be downloaded during the consultation period or notifying
  stakeholders when the consultation period opens.

Contact and organisation are closely coupled. Two separate apps were used to keep the
complexity down and it looked like we would end up modelling individuals as well - these
would be activists and interested members of the public that were not specifically part
of an organisation. So far that has not worked out and likely an individual will just be
an organisation with a single point of contact.

Policy and condition are closely coupled too. They were split purely to keep the views
down to a manageable number. Public-facing views are in the condition app and views used
by PHE staff were put in the policy app. They are both based on the Policy model (in the
policy app). Another reason for the split was that the only pages which are accessible
to the public are the ones in the condition app and document view to download a file.
That makes it easier to secure and shuffle the URLs around according to how the site
will be integrated with the existing PHE/NSC sites.

Documents are only associated with reviews, though they are downloadable by the public.
Again, they were separated out to keep thing simple.


Models and Queries
==================

The code has been reasonably careful when fetching Policy and Organisation objects to
make sure that related reviews are prefetched. However in general the queries have not
been optimised or examined to see if there are better ways of representing the models.

One thing to be aware of is that some of the attributes of a Review are denormalized
onto Policy to simplify presentation (it's also a bit of a legacy cruft from the early
days of the project when it was not abundantly clear that Policy and Review really were
separate and what exactly each represented). For example, the text field, summary, which
holds the plain English summary of the review outcome and background, which contains the
review history are duplicated on Policy and Review. The current intention is that when a
Review is completed (published) the associated Policy will be updated. Note, however
that a Review can be for more than one condition and in theory there can be different
plain English summaries which would describe the review outcome ONLY for a given
condition - there's no point in confusing the public reading the page for a condition by
throwing in a description of the outcome for another condition that was reviewed at the
same time. The content of the review history. background, may vary also with the extra
complication of time since for example, conditions may be grouped for a rapid review but
considered separately for a full review - in which case the histories, at least the
dates, will be different.


URLs
====

The views (and urls) can be organised into two main groups: public-facing and
internal-facing (PHE staff).

The location where the site will be deployed and how it integrates with existing NSC
pages has not been decided, however the structure is sufficiently modular that
re-organising or partitioning the tree will be straightforward.

The URLs are configured as follows:


Public
------

* ``/condition/`` - viewing NSC policy and commenting on conditions


Internal
--------

* ``/admin/`` - dashboard
* ``/policy/`` - managing conditions
* ``/organisation/`` - managing conditions
* ``/contact/`` - managing contacts in organisations
* ``/review/`` - managing reviews of conditions


Shared
------

* ``/document/`` - downloading files


Django Admin
============

The Django admin is defined in the code but not connected to the URL structure. This was
originally used during development, but is no longer required; it remains in the code
for development debugging purposes.


Templates and Accessibility
===========================

The HTML in the templates closely followed the GDS guidelines and should be fully
accessible unless there are mistakes in the examples.


Celery
======

There are some regular tasks managed by Celery - see :doc:`scheduled-tasks`.
