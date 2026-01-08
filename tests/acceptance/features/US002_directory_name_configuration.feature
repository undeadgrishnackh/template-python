@US-002 @directory-name @integration-signal
Feature: Configurable Source Directory Name
  As a platform engineer or 5D-Wave agent
  I want to specify a custom directory name for the generated scaffold
  So that I can integrate Python code into existing project structures

  Background:
    Given the cookiecutter template is available

  # Happy Path Scenarios

  @happy-path @explicit-name
  Scenario: Explicit directory name skips kata name prompt
    Given Maria is in a platform services directory
    When Maria runs the cookiecutter with directory name "trading-engine"
    Then Maria is not prompted for a kata name
    And the hook creates a directory named exactly "trading-engine"
    And the directory structure matches project conventions
    And no date prefix is added to the directory name

  @happy-path @5dwave-convention
  Scenario: 5D-Wave source directory follows agent conventions
    Given Alex is the 5D-Wave agent in a project root
    And the project already has a git repository
    When Alex runs the cookiecutter with directory name "source"
    Then the hook creates a directory named "source"
    And the directory contains the standard Python scaffold structure
    And the structure is ready for 5D-Wave DEVELOP phase

  @happy-path @default-preserved @backwards-compatible
  Scenario: Default behavior preserved for standalone katas
    Given Sam is starting a fresh coding kata
    When Sam runs the cookiecutter without specifying directory name
    Then Sam is prompted for a kata name
    And Sam enters "fizzbuzz" as the kata name
    And the hook creates a dated directory with the kata name
    And full git initialization runs as before

  # Integration Signal Scenarios

  @integration-signal @parameter-override
  Scenario: Explicit directory name signals integration mode
    Given a developer provides directory name "my-service"
    And the developer is in a clean directory without git
    When the developer generates the scaffold
    Then the hook treats this as integration mode
    And the hook skips GitHub repository creation
    And the hook skips remote origin setup
    But the hook still creates a local git repository

  @integration-signal @combined-detection
  Scenario: Directory name combined with git detection
    Given Alex provides directory name "source"
    And Alex is inside an existing git repository
    When Alex generates the scaffold
    Then both signals indicate integration mode
    And the hook confidently skips all repository creation
    And only environment setup and validation commit run

  # Edge Case Scenarios

  @edge-case @special-characters
  Scenario: Directory name with valid special characters
    Given Maria provides directory name "trading_engine_v2"
    When Maria generates the scaffold
    Then the hook creates directory "trading_engine_v2" successfully
    And all generated files use the correct directory name

  @edge-case @unicode-name
  Scenario: Directory name with unicode characters
    Given a developer provides directory name "service-test"
    When the developer generates the scaffold
    Then the hook handles the hyphenated name correctly
    And the scaffold is generated without errors

  # Error Scenarios

  @error-path @invalid-directory-name
  Scenario: Invalid directory name characters rejected
    Given a developer provides directory name "my/service"
    When the developer attempts to generate the scaffold
    Then the hook fails with a clear error about invalid directory name
    And the error explains which characters are not allowed
    And no partial files are created

  @error-path @directory-exists
  Scenario: Target directory already exists
    Given Maria is in a services directory
    And a directory named "trading-engine" already exists
    When Maria runs the cookiecutter with directory name "trading-engine"
    Then the hook fails before overwriting existing content
    And the error message clearly states the directory exists
    And Maria is advised to remove or rename the existing directory

  @error-path @empty-directory-name
  Scenario: Empty directory name handled gracefully
    Given a developer provides an empty directory name
    When the developer attempts to generate the scaffold
    Then the hook falls back to prompting for kata name
    Or the hook fails with a clear error message
