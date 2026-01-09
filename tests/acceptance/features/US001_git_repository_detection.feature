@US-001 @git-detection @integration-mode
Feature: Smart Git Repository Detection
  As a 5D-Wave AI agent or platform engineer
  I want the cookiecutter hook to detect existing git repositories
  So that I can scaffold Python code without repository creation conflicts

  Background:
    Given the cookiecutter template is available

  # Happy Path Scenarios

  @happy-path @agent-workflow
  Scenario: Agent detects existing repository and skips repo creation
    Given Alex is the 5D-Wave agent working in a project directory
    And the project has an existing git repository from DISCUSS phase
    When Alex generates a Python scaffold with directory name "source"
    Then the hook detects the existing git repository
    And the hook skips GitHub repository creation
    And the hook skips git initialization
    And the hook skips adding git remote origin
    And the hook skips pushing to remote
    And the hook skips pre-commit installation in integration mode
    And the hook skips validation commit in integration mode
    But the hook installs development dependencies
    And Alex continues workflow without manual intervention

  @happy-path @monorepo
  Scenario: Nested monorepo detection traverses multiple parent levels
    Given Maria is working in a services subdirectory
    And a git repository exists two levels up in the directory tree
    When Maria generates a Python scaffold with directory name "trading-engine"
    Then the hook traverses parent directories
    And the hook finds the git repository in the parent tree
    And the hook skips repository creation operations
    And the scaffold is generated in the services subdirectory

  @happy-path @standalone @backwards-compatible
  Scenario: Clean directory triggers full git initialization
    Given Sam is in a kata directory with no git repository in parent tree
    When Sam runs the cookiecutter with kata name "fizzbuzz"
    Then the hook finds no git repository in parent tree
    And the hook creates a private GitHub repository named with the kata
    And the hook initializes a new git repository
    And the hook adds a remote origin pointing to GitHub
    And the hook pushes the initial commit to the main branch
    And a dated project directory is created

  # Edge Case Scenarios

  @edge-case @git-worktree
  Scenario: Git worktree detection works with .git file
    Given a developer is working in a git worktree directory
    And the worktree has a .git file instead of a directory
    When the developer generates a Python scaffold
    Then the hook detects the git worktree as a valid repository
    And the hook skips repository creation operations

  @edge-case @filesystem-root
  Scenario: Detection stops safely at filesystem root
    Given a developer is in a directory near the filesystem root
    And no git repository exists in any parent directory
    When the developer runs the cookiecutter
    Then the hook traverses all parent directories to the root
    And the hook correctly determines no repository exists
    And the hook proceeds with full git initialization

  @edge-case @symlinks
  Scenario: Detection works correctly with symlinked directories
    Given a developer is working in a symlinked project directory
    And the symlink target has a git repository
    When the developer generates a Python scaffold
    Then the hook resolves the symlink and detects the git repository
    And the hook skips repository creation operations

  @edge-case @branch-preservation
  Scenario: Existing repository branch is preserved during scaffold
    Given Alex is working on a feature branch named "feature/trading-api"
    And the project has an existing git repository
    When Alex generates a Python scaffold with directory name "source"
    Then the hook does not change the current branch
    And the hook skips validation commit in integration mode
    And the branch remains "feature/trading-api" after scaffold completion

  # Error Scenarios

  @error-path @permission-denied
  Scenario: Detection continues despite permission-denied directories
    Given a developer is in a project directory
    And some parent directories have restricted read permissions
    When the developer generates a Python scaffold with directory name "service"
    Then the hook handles permission errors gracefully
    And the hook continues with available directory information
    And the scaffold generation completes successfully

  @error-path @gh-cli-failure
  Scenario: GitHub CLI failure in standalone mode provides clear error
    Given Sam is in a kata directory with no git repository
    And the GitHub CLI is not authenticated
    When Sam runs the cookiecutter with kata name "tdd-kata"
    Then the hook fails with a clear error message about GitHub authentication
    And the failure occurs before any files are modified
    And the error message includes remediation steps

  @error-path @git-not-installed
  Scenario: Missing git command in standalone mode provides guidance
    Given a developer is in a clean directory
    And git is not installed on the system
    When the developer runs the cookiecutter
    Then the hook fails with a clear error about missing git
    And the error message includes installation instructions
