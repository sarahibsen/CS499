# Getting Started with Git and GitHub
This guide walks you through the basic steps of working with this repository using Git and GitHub. You’ll learn how to:

1. Clone the repository
2. Create your own branch (if desired)
3. Pull the latest changes
4. Make and commit changes
5. Push changes to your branch
6. Create a Pull Request (PR)

--------------------------------------------------------

## Cloning the Repository 

If you have not yet downloaded the project to your local machine, follow these steps to clone the repository.

1. Navigate to the project’s GitHub page.
2. Click the green "Code" button and copy the URL (either HTTPS or SSH).
3. Open a terminal (or command prompt) on your local machine.
4. Navigate to the directory where you want to clone the repository.
5. Run:
```bash
# Using HTTPS:
git clone https://github.com/<USERNAME>/<REPO_NAME>.git

# OR using SSH:
git clone git@github.com:<USERNAME>/<REPO_NAME>.git

```

6. Navigate into the new folder:
```bash
cd <REPO_NAME>
```

-----------------------------------------------------
## Creating your own branch

Before making changes, it’s best practice to create a new branch so you don’t modify the main (master/main) branch directly.

```bash
# Create and switch to a new branch in one command:
git checkout -b <BRANCH_NAME>
```

Give your branch a meaningful name that reflects the feature or fix you are working on, for example: feature/add-login or fix/typo-in-docs.


--------------------------------------------------------
## Pulling the Latest Changes

Before you start coding  (or at any time you want to sync your work), make sure you have the latest changes from the remote repository:

```bash
# Make sure you are on the branch you want to update
git checkout <BRANCH_NAME>

# Fetch and merge the latest changes from the remote repository into your local branch
git pull origin <BRANCH_NAME>
```

If you are syncing with the main branch, use:
```bash
git checkout main
git pull origin main
```

Then switch back to your own branch, merge in those updates, or rebase as needed.

----------------------------------------------------------
## Making and Committing Changes

1. Open the project in your editor and modify the code as needed.
2. Once you’re satisfied with your changes, save the files.
3. Stage and commit your changes:

```bash
# Stage all changes
git add .

# OR stage specific files (if you don’t want to commit everything)
git add <FILE_PATH> <ANOTHER_FILE_PATH>

# Commit with a message
git commit -m "A brief description of the changes you made"
```

---------------------------------------------------------
## Pushing your Changes
After committing, push your local branch and commits to GitHub:
```bash
git push origin <BRANCH_NAME>
```
This sends your branch (and all its commits) to the remote repository on GitHub under your branch name.

----------------------------------------------------------
## Creatubg a Pull Request (PR)

A Pull Request (PR) lets you propose changes you’ve made in your branch to be merged into another branch (often main) in the remote repository.

1. Go to the repository on GitHub (in your browser).
2. You’ll usually see a prompt that says something like "Compare & pull request" after you push a new branch. If not:
    * Navigate to "Pull requests" tab.
    * Click "New pull request".
3. Select your branch as the "compare" branch, and main (or whichever branch you want to merge into) as the "base" branch.
4. **Review** the changes to ensure everything looks correct.
5. Enter a title and a description (the description helps reviewers understand the changes).
6. Click "Create pull request".

The teammates can now review your code, comment, and once everyone is satisfied, merge your changes into the target branch.