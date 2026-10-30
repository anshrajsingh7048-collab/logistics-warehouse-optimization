# GitHub + Streamlit Community Cloud deployment guide

This project has been prepared for deployment, but it has **not** been published to your personal GitHub account or deployed to Streamlit Cloud. Those steps require you to sign in and authorize the relevant services.

## A. Publish to GitHub using the website

1. Sign in to GitHub and create a **new public repository**, for example `logistics-warehouse-optimization`.
2. Do not initialize the repository with a README if you plan to upload this project's README as well.
3. In the new repository, choose **Add file → Upload files**.
4. Upload the project files and folders from this package: `app.py`, `generate_data.py`, `requirements.txt`, `.gitignore`, `README.md`, and the `data`, `sql`, and `docs` folders.
5. Commit the upload to the default branch (usually `main`).
6. Open the repository and confirm that `app.py`, `requirements.txt`, and `data/` are visible at the repository root.

## B. Deploy to Streamlit Community Cloud

1. Sign in to Streamlit Community Cloud using the account connected to your GitHub.
2. Select **Create app** / **Deploy an app**.
3. Choose the repository you just uploaded, branch `main`, and main file path `app.py`.
4. Deploy the app and wait for the build to complete.
5. Open the app URL and test every dashboard page and filter.
6. If deployment fails, open the app's logs and check for dependency or file-path errors. Keep `requirements.txt` at the repository root and preserve the `data/` directory structure.

## C. Final validation checklist

- [ ] Repository contains all files and CSV datasets.
- [ ] `app.py` and `requirements.txt` are at the root.
- [ ] Streamlit app loads without errors.
- [ ] Every page renders after changing filters.
- [ ] Tables and charts contain data.
- [ ] Synthetic-data disclaimer is visible in the app and README.
- [ ] No secrets, credentials, or personal information are committed.
- [ ] You can explain each KPI formula and at least two limitations.

## D. Suggested GitHub repository description

`Independent portfolio project: simulated FMCG logistics and warehouse analytics dashboard using Python, Pandas, SQL concepts, and Streamlit.`
