========
Overview
========

This document is a serious of notes and "inside information" on how and why
the code is the way it is. It was written at the end or March 2020, when the
project was put on pause due to the coronavirus outbreak. Once the project
is up and running again this document will have outlived it's usefulness and
should be deleted.

Objective
=========
This site is NOT a content management system for handing all the documents
related to the day-to-day functioning of the National Screening Committee (NSC).
It does perform something related to that but it is better to think of this as
a publishing tool to help describe recommendations of the NSC and to engage
members of the public and various interested parties when the policy for a
given condition comes up for review.

Apps
====
In typical django fashion the site is divided into apps:

   condition - contains the views for the public-facing pages that describe
   a given condition, e.g. Atrial Fibrillation, what the NSC recommendation
   for screening is, etc. It also contains the views for submitting comments
   when the condition is being reviewed and the consultation period is open.
   It does not contain any models, see policy as for why.

   contact - contains the views and model for managing the point of contacts
   at organisations.

   document - are the files such as the external review, evidence review etc.
   that are used during the review of a condition. Documents are available
   for download by the public and stakeholders so they can submit their
   comments when the consultation period of a review is open.

   organisation - contains the views and model for stakeholders - medical
   institutions, charities, etc. that are interested in a given condition and
   who participate in reviews.

   policy - contains the views and model that PHE staff used to edit the
   pages viewed by members of the public in the condition app.

   review - contains the views and model used by PHE staff to manage the
   review process, whether it is the documents that can be downloaded during
   the consultation period or notifying stakeholders when the consultation
   period opens.

Contact and organisation are closely coupled. Two separate apps were used
to keep the complexity down and it looked like we would end up modelling
individuals as well - these would be activists and interested members of
the public that were not specifically part of an organisation. So far that
has not worked out and likely an individual will just be an organisation
with a single point of contact.

Policy and condition are closely coupled too. They were split purely to keep
the views down to a manageable number. Public-facing views are in the condition
app and views used by PHE staff were put in the policy app. They are both
based on the Policy model (in the policy app). Another reason for the split
was that the only pages which are accessible to the public are the ones in
the condition app and document view to download a file. That makes it easier
to secure and shuffle the URLs around according to how the site will be
integrated with the existing PHE/NSC sites.

Documents are only associated with reviews, though they are downloadable
by the public. Again, they were separated out to keep thing simple,
particularly during the early stages of the project when the full scope was
somewhat ill-defined and certainly poorly understood by the development team.

Models & Queries
================
The code has been reasonably careful when fetching Policy and Organistion
objects to make sure that related reviews are prefetched. However in general
the queries have not been optimised or examined to see if there are better
ways of representing the models.

One thing to be aware of is that some of the attributes of a Review are
denormalized onto Policy to simplify presentation (it's also a bit of a
legacy cruft from the early days of the project when it was not abundantly
clear that Policy and Review really were separate and what exactly each
represented). For example, the text field, summary, which holds the plain
English summary of the review outcome and background, which contains the
review history are duplicated on Policy and Review. The current intention
is that when a Review is completed (published) the associated Policy will
be updated. Note, however that a Review can be for more than one condition
and in theory there can be different plain English summaries which would
describe the review outcome ONLY for a given condition - there's no point
in confusing the public reading the page for a condition by throwing in
a description of the outcome for another condition that was reviewed at
the same time. The content of the review history. background, may vary
also with the extra complication of time since for example, conditions
may be grouped for a rapid review but considered separately for a full
review - in which case the histories, at least the dates, will be
different. IMPORTANT: At time of writing, 27th March 2020, that a Review
can have muleiple conditions is NOT represented in the current design.


URLS
====
The views (and urls) can be organised into two main groups: public-facing
and internal-facing (PHE staff). The URLs are configured as follows:

public:
  /condition/ - viewing NSC policy and commenting on conditions

internal:
  /admin/ - dashboard
  /policy/ - managing conditions
  /organisation/ - managing conditions
  /contact/ - managing contacts in organisations
  /review/ - managing reviews of conditions

shared:
  /document/ - downloading files

The location where the site will be deployed and how it integrates with
existing NSC pages has not been decides however the above structure is
sufficiently modular that re-organising or partitioning the tree will be
straightforward.

Django Admin
============
The Django admin is currently accessible, at /djang-admin/. Originally
this was done to make editing the database a lot easier. It was not really
considered suitable for integrating into the site. However since the work
to integrate with PHE's single sign-on service has not progressed, Django
Authentication provides a good short-term solution for securing the app.
The Django Admin can then be used, probably by the product owner, for
adding user accounts.

Templates & Accessibility
=========================
The HTML in the templates closely followed the GDS guidelines and should be
fully accessible unless there are mistakes in the examples. Currently only
approved components are used. On the task list used on the "home" page when
managing a review is on the "experimental" list. Nothing was used from the
community backlog but will have to change as a review may be for more than
one condition. Choosing from a list of 200 entries is going to be problematic
so some form of drop-down menu with autocomplete is going to be needed to
keep things easy for the user. As a result some accessibility issues are
likely to be introduced.

Celery
======
Currently there is some support for celery added to the site. There are no
tasks defined at time or writing. The design does call for the ability for
PHE staff to schedule opening the consultation period at some date in the
future in which case celery would be needed. However managing the errors
that might result becomes "problematic". Most consultation periods open
with a few days notice so currently the development team are advocating that
the opening of the consultation period and the sending of notifications
is done manually. That gives PHE staff a lot more control over the process
and makes it much easier for them to see and respond to any delivery errors.
