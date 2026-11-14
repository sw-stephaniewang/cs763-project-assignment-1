# Conceptual Journal

## AI Usage Log

- I used ChatGPT to help me understand the PA2 requirements, plan the order of the work, draft prompts, and organize this journal.
- I used GitHub Copilot Agent mode in VS Code to build and test the discussion board in stages.
- I compared the results with the Domain 4 master spec and reran several of the PostgreSQL tests myself.
- Estimated conceptual AI contribution to this journal — 70%

## Project Assignment 2

### 1. Set up my PA2 branch

- I started PA2 from the version I submitted for A1 so I could build on my FastAPI setup and GitHub Actions workflow.
- I used the professor’s Domain 4 master spec for the features. One difference I noticed was that my A1 design had comments on posts, while PA2 also needs comments that can reply to other comments.

### 2. Create and retrieve a project update

- I started with one feature so I could follow the whole process. The test creates a post, takes the UUID from the response, and uses it to get the saved post back. I ran the test myself with PostgreSQL running.
- I learned that putting PA2 in a separate folder still allowed the root pytest command to find its test. The A1 environment did not have the PA2 dependencies, so Copilot renamed the test file. That meant I would need to tell GitHub Actions exactly which PA2 test file to run.

### 3. Finish the post lifecycle

- The first version only used `project_id`. Adding `scope_type` and `scope_id` let the same post model work for a project, course, or lab.
- I reran the expanded test, which checks that an edit is saved and that a deleted post can no longer be retrieved. Copilot separately reported checking that a post saved before the schema change could still be read afterward.

### 4. Add post search and timelines

- I reran the tests after Copilot added the filters and timelines. The course timeline test passed with a post attached directly to the course.
- The phrase “multi-project feed” in the master spec made me wonder whether the timeline should also include posts from the projects in that course. I kept that question open for a closer review.

### 5. Add nested comments

- The comment list comes back in chronological order. I can use the parent comment ID to see which comment each reply belongs to.
- Copilot chose to block deletion when a comment still has replies. This keeps the replies connected to their parent, but it means the replies have to be removed first. I treated this as a design choice because the master spec leaves that behavior open.

### 6. Add comment search and text export

- A keyword or author filter helps someone find specific comments. A text export is supposed to be a copy of the full thread. I thought it made sense to keep the download separate from the filters because someone could mistake a filtered file for the full record.
- Copilot indented replies in the text file so readers can follow the conversation without looking up parent comment IDs.

### 7. Add moderation

- I chose the mock faculty header so I could test the moderation workflow in PA2. The role comes from the request, so the app trusts what the caller says about their role. I plan to include that assumption in my security analysis.
- I noticed that a reply can still have an `active` status and be hidden because its parent is hidden. The comment list and text download both need to follow that rule so the download shows the same visible thread.

### 8. Review timelines against the master spec

- I asked Copilot to compare the timeline code and tests with the PDF. The review showed that the course and lab queries only looked for posts attached directly to the requested scope.
- The earlier test passed because it expected that exact behavior. It never linked two projects to the same course and checked whether both projects’ posts appeared. That helped me see why I need to compare what a test checks with what the assignment actually asks for.

### 9. Fix course and lab timelines

- I asked Copilot to include posts from the course or lab itself and from its associated projects. The new test checks which posts appear, whether they appear in order, and whether unrelated or hidden posts stay out.
- The first run failed because `DISTINCT` tried to compare the PostgreSQL JSON tags column. Copilot removed it because the query already selects each matching post once. That helped me see why it was worth checking how the query matched rows before adding a step to remove duplicates.

### 10. Update GitHub Actions for PA2

- I wanted GitHub Actions to run the PostgreSQL integration tests I had been using locally. The A1 health test only checks the A1 endpoint, so I asked Copilot to add an explicit PA2 test step.
- I also asked Copilot to pin the actions to full commit SHAs based on Steve’s feedback and keep the step that waits for SonarQube to finish processing.
- Copilot reported that the local checks passed. My next check is to open the hosted run and verify that it actually runs the PA2 tests and scans the PA2 source. Trivy still uses the A1 image, so I’ll keep that scope clear when I write up the results.