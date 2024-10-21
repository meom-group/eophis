# How to contribute

Contributions and feedbacks are welcome. We appreciate the time and effort you are ready to invest for collaborating to this project.


## Code of Conduct

Everyone participating in the Eophis project is expected to treat other people with respect and, more generally, to follow guidelines articulated in the [Python Community Code of Conduct](https://policies.python.org/python.org/code-of-conduct/).


## Bug reports and feature requests

For bug reports, feature requests, and suggestions, please [open an issue](https://github.com/meom-group/eophis/issues).

For bugs, please also provide:

- your operating system name and version
- Eophis version
- Self-contained code snippet to reproduce the bug


## Developer's guide

If you have built something upon Eophis (or wish to):

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a branch for local development and make changes locally
4. Commit your changes and push your branch to GitHub
5. Submit a pull request through the GitHub website

When creating a pull request, discussion will be open to decide in which branch your contributions should be merged. If your contribution implies new features, please provide testing procedures.

### Branching strategy

- **develop** is dedicated to code sources evolution and integration of new features
- **doc** is dedicated to evolution and fixes of documentation, and repo markdown files (README, CONTRIBUTING…)
- **hotfix** is dedicated for correction of minor bugs, it is kept close to *main* branch
- **release** gathers modifications of other branches. It is dedicated to stabilization and beta testing
- **main** freezes stable states of *release* branch for official package deployment

### Coding convention

Eophis follows [PEP 8 coding convention](https://peps.python.org/pep-0008/). Here are some additional guidelines:

- Avoid obscure or too long variable names
- Use 4-space indentation
- Document every function, class...with [Numpy doscstring style](https://numpydoc.readthedocs.io/en/latest/format.html)
- Coding is art, aesthetics matters =D

Module structure:

- Add module header with short description of the module, License and copyright
- When importing packages, distinguish Eophis module and external packages
- Define exactly what should be imported from the module with ``__all__``, even to import everything or nothing
