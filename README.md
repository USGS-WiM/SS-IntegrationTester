![WiM](wim.png)


# StreamStats Integration Tester

The StreamStats Integration Tester is used to compare StreamStats results to known values to ensure accuracy. There are two primary functions:
1. Testing: Generate and save StreamStats results for basin delineation, computation of basin characteristics, and computation of flow statistics for test sites across TestWeb, ProdWebA, and ProbWebB servers. Computed values are compared to known values. Results are compared between the servers.
2. Comparison: Compare two testing sessions. If a testing session is completed before and after a migration, compare the results of these two testing sessions and discover if any differences exist. 
### Prerequisites

- Python 3

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Installing

Run the following in the Windows command prompt:

```bash
pip install -r requirements.txt
```

Alternate instructions for the Windows Anaconda3 prompt with a Conda environment:

```bash
# create a new Conda environment
conda create --name ss-integrationtester
# active the Conda environment
conda activate ss-integrationtester
# install the project's dependencies
conda install pip
pip install -r requirements.txt
```

### How To Use the Integration Tester
1. Testing: use this function when you want to generate current results for StreamStats
   
```bash
python testing.py
```

Results will be available in this file structure:
```
SS-IntegrationTester
│
└───Output
    │   
    └───Testing-YYYY-MM-DD-HH-SS
        │   ConsoleOutput.txt
        │   
        └───TEST
        │   │   
        │   └───BasinDelineations
        │   │      AK.txt
        │   │      AL.txt
        │   │      ...
        │   │   
        │   └───BasinCharacteristics
        │   │      BasinCharacteristicsOutput.csv
        │   │      BasinCharacteristicsDifferences.csv
        │   │      BasinCharacteristicsUncompared.csv
        │   │      AK.txt
        │   │      AL.txt
        │   │      ...
        │   │   
        │   └───FlowStatistics
        │          AK.txt
        │          AL.txt
        │          ...
        │   
        └───PRODWEBA
        │   │   
        │   └───BasinDelineations
        │   │      AK.txt
        │   │      AL.txt
        │   │      ...
        │   │   
        │   └───BasinCharacteristics
        │   │      BasinCharacteristicsOutput.csv
        │   │      BasinCharacteristicsDifferences.csv
        │   │      BasinCharacteristicsUncompared.csv
        │   │      AK.txt
        │   │      AL.txt
        │   │      ...
        │   │   
        │   └───FlowStatistics
        │          AK.txt
        │          AL.txt
        │          ...
        │   
        └───PRODWEBB
        │   │   
        │   └───BasinDelineations
        │   │      AK.txt
        │   │      AL.txt
        │   │      ...
        │   │   
        │   └───BasinCharacteristics
        │   │      BasinCharacteristicsOutput.csv
        │   │      BasinCharacteristicsDifferences.csv
        │   │      BasinCharacteristicsUncompared.csv
        │   │      AK.txt
        │   │      AL.txt
        │   │      ...
        │   │   
        │   └───FlowStatistics
        │          AK.txt
        │          AL.txt
        │          ...
        └───Comparison
            │   DifferencesSummary.csv
            │   
            └───Comparison-TEST-PRODWEBA
            │       Comparison-TEST-PRODWEBA.csv
            │       Comparison-TEST-PRODWEBA-Differences.csv
            │       Comparison-TEST-PRODWEBA-Uncompared.csv
            │   
            └───Comparison-TEST-PRODWEBB
                    Comparison-TEST-PRODWEBA.csv
                    Comparison-TEST-PRODWEBA-Differences.csv
                    Comparison-TEST-PRODWEBA-Uncompared.csv
```

Explanation of files in Testing-YYYY-MM-DD-HH-MM-SS folder:
- ConsoleOutput.txt: copy of the console output
- [server]/BasinDelineations/[region].txt: contains the full service response for basin delineation for that test site
- [server]/BasinCharacteristics/[region].txt: contains the full service response for basin characteristics for that test site
- [server]/FlowStatistics/[region].txt: contains the full service response for flow statistics for that test site
- [server]/BasinCharacteristics/BasinCharacteristicsOutput.csv: contains basin characteristics (computed and known values) for all test sites
- [server]/BasinCharacteristics/BasinCharacteristicsDifferences.csv: contains computed basin characteristics that were not equal to known values
- [server]/BasinCharacteristics/BasinCharacteristicsUncompared.csv: contains computed basin characteristics that were not compared to known values because a known value was not available
- Comparison/DifferencesSummary.csv: contains the differences discovered when comparing TestWeb to ProdWebA and Test to ProdWebB
- Comparison/Comparison-TEST-[server]/Comparison-TEST-[server].csv: contains all compared values for basin delineation, basin characteristics, and flow statistics between TestWeb and ProdWebA or ProdWebB
- Comparison/Comparison-TEST-[server]/Comparison-TEST-[server]-Differences.csv: contains all values for basin delineation, basin characteristics, and flow statistics that were different between TestWeb and ProdWebA or ProdWebB
- Comparison/Comparison-TEST-[server]/Comparison-TEST-[server]-Uncompared.csv: contains all values for basin delineation, basin characteristics, and flow statistics that were not able to be compared between TestWeb and ProdWebA or ProdWebB due to lack of data in one server

## Development Workflow

Explain the desired workflow. Workflow may deviate from the instructions below depending on the projects needs.

**Instructions below are for developers actively working on the repo.**

An issue will be assigned to you via Github. Your workflow begins after assignment:

1. Create a branch with your initials and the issue number as the branch name (e.g. `JD-134`)
2. Do the work. 
3. Once all checks have passed and you are ready to submit a Pull Request, update the changelog with a brief description of what your work added, changed, or removed. There is an Unreleased section at top with subheadings for each category. Edit the file CHANGELOG.md found at project root.
4. Add the changed files `git add .` and commit `git commit -m '[your commit message here]'` you commit message should reference the issue number and include a very brief description of the work.
5.  **Pull from `dev`**
    - Run `git pull origin dev`. This is a critical step. It ensures your Pull Request is synced with the latest work in the main `dev` branch. If you are lucky, it will auto-merge. Otherwise, you may have to resolve conflicts between your commit and what currently exists in dev. Please be careful with this step so no code is lost - ask for help if you are unsure what to do.
    - If manually merging, you will have changed files so you will need to add and commit once more.
6.  Push your committed and synced branch to the remote repo (Github): `git push origin [your branch name]`
7.  Submit Pull Request (PR) to merge your issue branch into `dev`

Move on to next assigned issue and start back at step 1.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on the process for submitting pull requests to us. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details on adhering by the [USGS Code of Scientific Conduct](https://www2.usgs.gov/fsp/fsp_code_of_scientific_conduct.asp).

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](../../tags).

Advance the version when adding features, fixing bugs or making minor enhancement. Follow semver principles. To add tag in git, type git tag v{major}.{minor}.{patch}. Example: git tag v2.0.5

To push tags to remote origin: `git push origin --tags`

*Note that your alias for the remote origin may differ.

## Authors

* **[Andrea Medenblik]([PROFILE_PAGE_URL_HERE](https://www.usgs.gov/staff-profiles/andrea-s-medenblik))**  - *Developer* - [USGS Web Informatics & Mapping](https://wim.usgs.gov/)

See also the list of [contributors](../../graphs/contributors) who participated in this project.

## License

This project is licensed under the Creative Commons CC0 1.0 Universal License - see the [LICENSE.md](LICENSE.md) file for details

## Suggested Citation
In the spirit of open source, please cite any re-use of the source code stored in this repository. Below is the suggested citation:

`This project contains code produced by the Web Informatics and Mapping (WIM) team at the United States Geological Survey (USGS). As a work of the United States Government, this project is in the public domain within the United States. https://wim.usgs.gov`


## Acknowledgments

This updated StreamStats integration tester was inspired by:

* [StreamStats BatchTester](https://github.com/USGS-WiM/StreamStats-Setup/tree/master/batchTester)
* [StreamStats Integration Test](https://github.com/USGS-WiM/StreamStatsIntegrationTest)

## About WIM
* This project authored by the [USGS WIM team](https://wim.usgs.gov)
* WIM is a team of developers and technologists who build and manage tools, software, web services, and databases to support USGS science and other federal government cooperators.
* WIM is a part of the [Upper Midwest Water Science Center](https://www.usgs.gov/centers/upper-midwest-water-science-center).
