![](./logo.png)


Hydrus is a reimplementation of the ["SAS Pack"][1] script for calculating the Centers for Medicare
and Medicaid Services' [Overall Hospital Quality Star Ratings][2].

Initial goals for Hydrus were to address the largest usability issues of CMS's SAS Pack:

1.  __Speed:__ CMS's SAS Pack has a run time of [40 to 100 hours][3].  Hydrus runs in less than one minute.

2.  __Price:__ CMS's SAS Pack requires a (very expensive) SAS license.  Hydrus is built on free, open-source software.

3.  __Portability:__ Hydrus runs on Windows, Linux, and Mac.

During development, a number of other issues with CMS's SAS Pack were discovered:

-   CMS's SAS Pack does not correctly implement k-means clustering when assigning star ratings to
    hospitals. This led to incorrect star rating assignments for over 900 hospitals in the October
    2016 release, and over 1000 hospitals in the December 2016 release.

    The default behavior of Hydrus is to fix this error.

    Optionally, Hydrus can instead mimic the SAS Pack's errors to replicate its results.

-   When fitting CMS's Latent Variable Model (LVM) to the hospital data, a large number of
    complicated integrals are calculated.  CMS's SAS Pack uses [Gaussian quadrature][4] to
    approximate these integrals.  These approximations lead to inaccurate estimates of the model
    parameters, which in turn leads to hundreds of hospitals receiving an incorrect star rating.

    The default behavior of Hydrus is to fix this issue by avoiding quadrature altogether, instead
    calculating exact integrals.

    Optionally, Hydrus can instead mimic the SAS Pack's errors to replicate its results.

There are a number of other technical issues in CMS's SAS Pack that cannot be fixed by Hydrus.
The assignment of certain measures to certain measure groups, for example, is a policy decision
that can only be addressed by CMS.

## Quickstart

1.  Make sure you have Python 3 installed, with the `python` executable in your `PATH`.  64-bit
    Python is recommended.

2.  Download this repository:

    ```sh
    $ git clone https://github.com/mark-r-g/hydrus
    $ cd hydrus
    ```

3.  Create a virtual environment and install the required dependencies.

    Via `conda` (recommended, especially on Windows):

    ```sh
    $ conda env create
    $ source activate hydrus  # (or just "activate hydrus" on Windows)
    ```

    A `requirements.txt` is included if you prefer to use `pip` and `venv`. If using this method,
    please note that Hydrus requires Python 3.6 or newer.

4.  Download the "SAS Input File" from [CMS's website][1] and place the unzipped file in the
    `input/` directory.  Hydrus includes a script to do this for you automatically:

    ```sh
    $ python download_cms_data.py
    ```

5.  Run the `__main__` script.  Results are written to a timestamped subfolder in the `output/`
    directory.

    ```sh
    $ python -m hydrus
    ```

## FAQ
### How can I configure Hydrus to reproduce the results released by CMS?
Open the `settings.cfg` file and change both `RAPIDCLUS` and `QUADRATURE` from `False` to `True`.
This tells Hydrus to use the same clustering and quadrature methods used in CMS's SAS Pack.
Run Hydrus with these changes and the resulting star ratings will be identical to those form SAS.

Note that quadrature-based integral approximation is not only less accurate, but also much slower.
Expect a single run to take 5 to 15 minutes instead of less than 1 minute.

### Can I change which measures/groups are included?
Yes, by editing e.g. `input/measure_settings_2016_12.yml`.

We plan to add a guide for this in the future.

### Can I change which hospitals are included, or edit the hospital data before running Hydrus?
Yes, but it requires some work.

We plan to add a guide for this in the future.

## Similar Projects
[@huangrh][5] maintains [a separate repository][6] similar to Hydrus in its goals.

## Authors
Code was written by [@mark-r-g][7] and [@bbayles][8].

Significant non-code contributions were made by [@huangrh][5] and Angelo Bufalino, PhD.

The Hydrus logo was donated by a separate party.

## Contact
If you have questions, please contact [@mark-r-g][7] via the email address listed at the top of
[Hydrus' license header][9].

(TODO: open up the issue tracker and/or wiki?)

## License
Hydrus has been uploaded to GitHub subject to the GNU General Public License (GPL) Version 3.

See the `LICENSE` file for information on the terms and conditions for usage, and a disclaimer of
all warranties.

[1]: https://www.qualitynet.org/dcs/ContentServer?c=Page&pagename=QnetPublic%2FPage%2FQnetTier3&cid=1228775958130
[2]: https://www.cms.gov/Newsroom/MediaReleaseDatabase/Fact-sheets/2016-Fact-sheets-items/2016-07-27.html
[3]: https://www.qualitynet.org/dcs/BlobServer?blobkey=id&blobnocache=true&blobwhere=1228890620609&blobheader=multipart%2Foctet-stream&blobheadername1=Content-Disposition&blobheadervalue1=attachment%3Bfilename%3DStarRtngSASPackInstrns_Oct2016.pdf&blobcol=urldata&blobtable=MungoBlobs
[4]: https://en.wikipedia.org/wiki/Gaussian_quadrature
[5]: https://github.com/huangrh/
[6]: https://github.com/huangrh/rstarating
[7]: https://github.com/mark-r-g/
[8]: https://github.com/bbayles/
[9]: https://github.com/mark-r-g/hydrus/blob/master/hydrus/__main__.py#L1
