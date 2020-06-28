This is the source for https://electioncal.us which provides election
timeline information and makes it available through the website and
icalendar files.

# Building the site

The site is statically hosted by GitHub. To test it locally, first install the
python requirements with:

    pip install -r requirements.txt

Once those are installed, build the site with:

    python scripts/build_site.py

This generates all of files served statically under the `site` folder. To serve
them locally do:

    python -m http.server --directory site/ 8080
