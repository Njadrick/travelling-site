Kanisa
======

A project for managing Church websites, built with Django.

Kanisa handles:

* Public pages;
* Sermons;
* A calendar;
* A members' area for documents and service planning;
* Search;
* Banners - for advertising upcoming events etc.

You can see it in action at https://www.centralbaptistchelmsford.org.

Requirements
------------

Kanisa expects to essentially be the only app you're running, and
requires Python 2.7 and Django 1.7.

Installation
------------

Pain points for installation:

1. Set up ``INSTALLED_APPS``;
2. Set up template context processors;
3. Make sure ``SITE_ID`` is set (do we even need the sites
   framework?).
