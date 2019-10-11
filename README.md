
# misc

![Lifecycle
](https://img.shields.io/badge/lifecycle-experimental-orange.svg?style=flat)

Miscellaneous command line scripts and utilities


## Summary

* [github_repos.sh](https://raw.githubusercontent.com/makeyourownmaker/misc/master/github_repos.sh):
Check number of github repositories and update beeminder if increased
Requires [bmndr](https://github.com/lydgate/bmndr)

* [so_rep.sh](https://raw.githubusercontent.com/makeyourownmaker/misc/master/so_rep.sh):
Check stackoverflow reputation and update beeminder if increased
Requires [bmndr](https://github.com/lydgate/bmndr)

* [goodReads.py](https://raw.githubusercontent.com/makeyourownmaker/misc/master/goodReads.py):
Lookup book details including rating statistics using ISBN and calculate further statistics
Requires [goodreads python module plus API key and API secret](https://github.com/sefakilic/goodreads)

* [omdb](https://raw.githubusercontent.com/makeyourownmaker/misc/master/omdb):
Lookup IMDB, rotten tomatoes ratings, runtime etc
Requires [jq](https://stedolan.github.io/jq/)
Broken - requires free API key now


## Warning

Some of these tools contain obvious problems and should be considered as
"proof of concept" code.  I'm putting it here with the hope that it is useful
to someone.  No judging me.  Look at my other repositories for that.


## Installation

Recent versions of bash, perl, python etc are probably required.

Check each script for additional dependencies.

The following should work on any unix-ish environment:
```sh
wget https://raw.githubusercontent.com/makeyourownmaker/misc/master/<scriptname>
chmod u+x <scriptname>
./<scriptname>
```


## Usage

Read the source code to see what parameters are required or which variables
need to be edited.


## Roadmap

Probably going to make few to no changes.  Some of these scripts may already be
broken.

Most of these utilities are not used on a regular basis but if one starts
to become really useful I'll move it to a separate repository.


## Contributing

Pull requests are welcome.


## License
[GPL-2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
