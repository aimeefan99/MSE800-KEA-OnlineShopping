# Sprint 1 Jira Setup Tasks

This file translates `Sprint 1` into Jira-ready setup and planning tasks.
`Sprint 1` is not a feature-development sprint, so the work items below should be created as `Task` items rather than `Story` items.

## Sprint Goal

Confirm project scope and establish the technical foundation for the remaining sprints.

## Suggested Jira Structure

- Issue type: `Task`
- Sprint: `MSE800 Sprint 1`
- Priority: use `Highest` for foundation items, `High` for important setup items, and `Medium` for supporting planning items.

## Task 1: Confirm Project Scope and MVP Boundary

Priority: `Highest`

Description:
Finalize the agreed project scope, confirm the MVP boundary, and record the features that are included and excluded from the six-week delivery plan.

Acceptance Criteria:
- The core marketplace workflow is clearly listed.
- The two highlighted features are clearly listed.
- Out-of-scope features are clearly listed.
- The document set uses the same scope definition consistently.
- Team members can identify what will and will not be built in this project.

## Task 2: Confirm Role Model and Core Workflow

Priority: `Highest`

Description:
Confirm that the system uses the `user` and `administrator` role model, and confirm that buyer and seller are user behaviours rather than fixed account roles.

Acceptance Criteria:
- The role model is written clearly in the project documentation.
- User actions and administrator actions are separated clearly.
- Buyer and seller are described as transaction behaviours, not account types.
- The core trading flow is defined from listing creation to request completion.

## Task 3: Review Reference Platform and Confirm Project Differentiation

Priority: `High`

Description:
Review Trade Me and confirm the practical gaps that justify the project's point of difference.

Acceptance Criteria:
- Trade Me is identified as the main reference platform.
- The reviewed limitations are described clearly and realistically.
- The selected differentiation points are recorded.
- The selected differentiation points match the highlighted features in the plan.

## Task 4: Confirm AI One-Click Listing and Homepage Recommendation Concepts

Priority: `Highest`

Description:
Define the two highlighted features at the concept level so they can be implemented consistently in later sprints.

Acceptance Criteria:
- The AI one-click listing feature is described clearly.
- The homepage recommendation feature is described clearly.
- Inputs, outputs, and limitations are recorded for both features.
- Both features are realistic for the project timeline.

## Task 5: Create Core Diagrams

Priority: `High`

Description:
Create the key diagrams required to support system understanding and later implementation.

Acceptance Criteria:
- A use case diagram is created.
- An ER diagram is created.
- An activity diagram is created.
- The diagrams reflect the current agreed workflow and scope.
- The diagrams are ready for team discussion and later refinement.

## Task 6: Sketch Main Page Structure and Wireframes

Priority: `High`

Description:
Define the main page structure, navigation flow, and early wireframes for the main interfaces.

Acceptance Criteria:
- Main pages are identified.
- Navigation between the main pages is defined.
- Core user flow is visible in the wireframes.
- Core administrator flow is visible in the wireframes.
- The wireframes are sufficient to guide implementation in Sprint 2.

## Task 7: Prepare Initial Database Schema Draft

Priority: `Highest`

Description:
Prepare the first database structure draft based on the agreed platform workflow.

Acceptance Criteria:
- Core tables are identified.
- Main table relationships are identified.
- Key attributes for each core table are listed.
- Status fields and key constraints are considered in the draft.
- The draft supports the planned MVP workflow.

## Task 8: Initialize Repository, Board, and Project Skeleton

Priority: `Highest`

Description:
Set up the shared development environment so implementation can begin cleanly in Sprint 2.

Acceptance Criteria:
- The GitHub repository is available and accessible to both team members.
- The Jira board is created and the Sprint 1 structure is usable.
- The basic Flask project structure is initialized.
- The initial folder structure supports frontend, backend, and documentation work.
- Both team members can start work from the same project baseline.

## Task 9: Confirm Deployment Direction

Priority: `Medium`

Description:
Confirm the planned containerised deployment direction using Docker and Kubernetes.

Acceptance Criteria:
- Docker is identified as the containerisation approach.
- Kubernetes is identified as the deployment orchestration approach.
- The deployment target is recorded in the project documentation.
- The team agrees to implement deployment progressively rather than leaving it entirely to the final week.

## Task 10: Prepare the Initial Backlog for Sprint 2 and Beyond

Priority: `High`

Description:
Translate the agreed scope into an actionable backlog for the upcoming implementation sprints.

Acceptance Criteria:
- Sprint 2 candidate items are created in Jira.
- Sprint 3 to Sprint 5 candidate items are drafted in Jira.
- Core implementation items are prioritised.
- The backlog reflects the current project scope and sprint plan.
- The team can begin Sprint 2 without additional scope clarification.
